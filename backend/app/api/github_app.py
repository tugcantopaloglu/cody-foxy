import hmac
import hashlib
import json
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from ..core.database import get_db
from ..core.config import settings
from ..models.scan import Scan, ScanStatus
from ..models.project import Project
from ..services.parallel_scanner import ParallelScanner
from ..services.github_service import GitHubService

router = APIRouter()


class GitHubWebhookPayload(BaseModel):
    action: Optional[str] = None
    ref: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None
    repository: Optional[dict] = None
    pull_request: Optional[dict] = None
    sender: Optional[dict] = None


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not signature or not secret:
        return False
    
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


async def run_pr_scan(
    project_id: int,
    repo_url: str,
    branch: str,
    pr_number: int,
    commit_sha: str,
    db_url: str,
):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        scan = Scan(
            source_type="github_pr",
            source_path=f"{repo_url}/pull/{pr_number}",
            branch=branch,
            commit_sha=commit_sha,
            status=ScanStatus.PENDING.value,
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        try:
            github = GitHubService()
            temp_dir = await github.clone_repo(repo_url, branch)
            
            scanner = ParallelScanner()
            results = await scanner.scan_directory(temp_dir)
            
            scan.total_findings = len(results["findings"])
            scan.critical_count = results["stats"]["critical"]
            scan.high_count = results["stats"]["high"]
            scan.medium_count = results["stats"]["medium"]
            scan.low_count = results["stats"]["low"]
            scan.status = ScanStatus.COMPLETED.value
            scan.completed_at = datetime.utcnow()
            
            project = await db.get(Project, project_id)
            if project:
                fail_counts = {
                    "critical": scan.critical_count,
                    "high": scan.critical_count + scan.high_count,
                    "medium": scan.critical_count + scan.high_count + scan.medium_count,
                    "low": scan.total_findings,
                }
                
                threshold = project.fail_threshold
                should_fail = fail_counts.get(threshold, 0) > 0
                
                owner, repo = repo_url.rstrip('/').split('/')[-2:]
                await github.create_check_run(
                    owner=owner,
                    repo=repo,
                    sha=commit_sha,
                    name="Cody Foxy Security Scan",
                    conclusion="failure" if should_fail else "success",
                    title=f"Found {scan.total_findings} security issues",
                    summary=f"""
## Security Scan Results

| Severity | Count |
|----------|-------|
| Critical | {scan.critical_count} |
| High | {scan.high_count} |
| Medium | {scan.medium_count} |
| Low | {scan.low_count} |

[View full report](https://codyfoxy.dev/scan/{scan.id})
""",
                )
                
        except Exception as e:
            scan.status = ScanStatus.FAILED.value
            scan.error_message = str(e)
        
        await db.commit()


@router.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    signature = request.headers.get("X-Hub-Signature-256", "")
    event = request.headers.get("X-GitHub-Event", "")
    
    body = await request.body()
    
    webhook_secret = settings.GITHUB_WEBHOOK_SECRET if hasattr(settings, 'GITHUB_WEBHOOK_SECRET') else ""
    if webhook_secret and not verify_github_signature(body, signature, webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = json.loads(body)
    
    if event == "ping":
        return {"status": "pong"}
    
    if event == "push":
        return await handle_push_event(payload, background_tasks, db)
    
    if event == "pull_request":
        return await handle_pr_event(payload, background_tasks, db)
    
    if event == "check_suite":
        return await handle_check_suite(payload, background_tasks, db)
    
    return {"status": "ignored", "event": event}


async def handle_push_event(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession,
):
    repo = payload.get("repository", {})
    repo_url = repo.get("html_url", "")
    ref = payload.get("ref", "")
    commit_sha = payload.get("after", "")
    
    if not ref.startswith("refs/heads/"):
        return {"status": "ignored", "reason": "not a branch push"}
    
    branch = ref.replace("refs/heads/", "")
    
    result = await db.execute(
        select(Project).where(Project.scan_on_push == True)
    )
    projects = result.scalars().all()
    
    for project in projects:
        if project.repository and project.repository.url == repo_url:
            if branch == project.default_branch:
                background_tasks.add_task(
                    run_pr_scan,
                    project.id,
                    repo_url,
                    branch,
                    0,
                    commit_sha,
                    settings.DATABASE_URL,
                )
    
    return {"status": "processing"}


async def handle_pr_event(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession,
):
    action = payload.get("action", "")
    
    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "reason": f"action {action} not handled"}
    
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    
    repo_url = repo.get("html_url", "")
    pr_number = pr.get("number", 0)
    branch = pr.get("head", {}).get("ref", "")
    commit_sha = pr.get("head", {}).get("sha", "")
    
    result = await db.execute(
        select(Project).where(Project.scan_on_pr == True)
    )
    projects = result.scalars().all()
    
    for project in projects:
        if project.repository and project.repository.url == repo_url:
            background_tasks.add_task(
                run_pr_scan,
                project.id,
                repo_url,
                branch,
                pr_number,
                commit_sha,
                settings.DATABASE_URL,
            )
    
    return {"status": "processing", "pr": pr_number}


async def handle_check_suite(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession,
):
    action = payload.get("action", "")
    
    if action != "requested":
        return {"status": "ignored"}
    
    check_suite = payload.get("check_suite", {})
    repo = payload.get("repository", {})
    
    commit_sha = check_suite.get("head_sha", "")
    repo_url = repo.get("html_url", "")
    branch = check_suite.get("head_branch", "main")
    
    return {"status": "acknowledged"}


@router.get("/installation/{installation_id}")
async def get_installation(
    installation_id: int,
):
    return {
        "installation_id": installation_id,
        "status": "active",
    }
