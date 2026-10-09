import os
import json
import shutil
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from datetime import datetime
import zipfile
import tarfile
from pathlib import Path

from ..core.database import get_db
from ..core.security import require_auth
from ..core.config import settings
from ..models.scan import Scan, Finding, ScanStatus
from ..schemas.scan import ScanResponse, ScanCreate, FindingResponse
from ..services.scanner import ScannerService
from ..services.ai_analyzer import AIAnalyzer
from ..services.sarif_generator import SarifGenerator
from ..services.github_service import GitHubService
from .websocket import manager

router = APIRouter()


class GitHubScanRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    enable_ai: bool = True


def _user_id(user: dict) -> int:
    try:
        user_id = int(user["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid user identity") from exc
    if user_id <= 0:
        raise HTTPException(status_code=401, detail="Invalid user identity")
    return user_id


async def _owned_scan(scan_id: int, db: AsyncSession, user: dict) -> Scan:
    result = await db.execute(
        select(Scan).options(selectinload(Scan.findings)).where(
            Scan.id == scan_id, Scan.user_id == _user_id(user)
        )
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


async def run_scan(scan_id: int, directory: str, db_url: str, enable_ai: bool = True):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        scan = await db.get(Scan, scan_id)
        if not scan:
            return
        
        scan.status = ScanStatus.RUNNING.value
        scan.started_at = datetime.utcnow()
        await db.commit()
        await manager.broadcast({"type": "scan_started", "scan_id": scan_id},
                                scan_id=str(scan_id), user_id=scan.user_id)
        
        try:
            scanner = ScannerService()
            results = await scanner.scan_directory(directory)
            
            scan.languages_detected = results["languages"]
            scan.total_files = results["total_files"]
            scan.files_scanned = results["files_scanned"]
            
            findings_data = results["findings"]
            
            if enable_ai and findings_data:
                analyzer = AIAnalyzer()
                findings_data = await analyzer.analyze_findings_batch(findings_data[:50])
            
            for f_data in findings_data:
                finding = Finding(
                    scan_id=scan_id,
                    rule_id=f_data["rule_id"],
                    rule_name=f_data["rule_name"],
                    severity=f_data["severity"],
                    file_path=f_data["file_path"],
                    start_line=f_data["start_line"],
                    end_line=f_data["end_line"],
                    start_col=f_data.get("start_col", 0),
                    end_col=f_data.get("end_col", 0),
                    code_snippet=f_data.get("code_snippet", ""),
                    message=f_data["message"],
                    ai_explanation=f_data.get("ai_explanation", ""),
                    ai_remediation=f_data.get("ai_remediation", ""),
                    cwe_ids=f_data.get("cwe_ids", []),
                    owasp_ids=f_data.get("owasp_ids", []),
                    references=f_data.get("references", []),
                )
                db.add(finding)
            
            stats = results["stats"]
            scan.total_findings = len(findings_data)
            scan.critical_count = stats["critical"]
            scan.high_count = stats["high"]
            scan.medium_count = stats["medium"]
            scan.low_count = stats["low"]
            
            sarif = SarifGenerator()
            scan.sarif_output = sarif.generate(findings_data, scan_id=scan_id)
            
            scan.status = ScanStatus.COMPLETED.value
            scan.completed_at = datetime.utcnow()
            
        except Exception as e:
            scan.status = ScanStatus.FAILED.value
            scan.error_message = str(e)
        
        await db.commit()
        await manager.broadcast({
            "type": "scan_completed",
            "scan_id": scan_id,
            "status": scan.status,
            "total_findings": scan.total_findings,
        }, scan_id=str(scan_id), user_id=scan.user_id)
    
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)


@router.post("/upload", response_model=ScanResponse)
async def upload_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    enable_ai: bool = True,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    user_id = _user_id(user)
    if not file.filename or not file.filename.endswith(('.zip', '.tar.gz', '.tgz')):
        raise HTTPException(status_code=400, detail="Only zip/tar.gz files supported")
    content = await file.read(settings.MAX_FILE_SIZE + 1)
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Archive exceeds the upload size limit")
    
    temp_dir = tempfile.mkdtemp(prefix="cody_upload_")
    file_path = os.path.join(temp_dir, "upload.archive")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    extract_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        if file.filename.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as z:
                if sum(member.file_size for member in z.infolist()) > settings.MAX_FILE_SIZE:
                    raise ValueError("Expanded archive exceeds the size limit")
                destination = Path(extract_dir).resolve()
                for member in z.infolist():
                    if not (destination / member.filename).resolve().is_relative_to(destination):
                        raise ValueError("Unsafe archive path")
                    z.extract(member, extract_dir)
        else:
            with tarfile.open(file_path, 'r:gz') as t:
                if sum(member.size for member in t.getmembers()) > settings.MAX_FILE_SIZE:
                    raise ValueError("Expanded archive exceeds the size limit")
                t.extractall(extract_dir, filter="data")
    except (tarfile.TarError, zipfile.BadZipFile, ValueError) as exc:
        shutil.rmtree(temp_dir)
        raise HTTPException(status_code=400, detail="Invalid or unsafe archive") from exc
    
    scan = Scan(
        user_id=user_id,
        source_type="upload",
        source_path=file.filename,
        status=ScanStatus.PENDING.value,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    await db.refresh(scan, attribute_names=["findings"])
    
    background_tasks.add_task(run_scan, scan.id, extract_dir, settings.DATABASE_URL, enable_ai)
    
    return ScanResponse.model_validate(scan)


@router.post("/github", response_model=ScanResponse)
async def scan_github_repo(
    background_tasks: BackgroundTasks,
    repo_url: str | None = None,
    branch: str = "main",
    enable_ai: bool = True,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
    payload: GitHubScanRequest | None = Body(None),
):
    if payload is not None:
        repo_url, branch, enable_ai = payload.repo_url, payload.branch, payload.enable_ai
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required")
    user_id = _user_id(user)
    github_token = None
    if user:
        from ..models.user import User
        result = await db.execute(select(User).where(User.id == user_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            github_token = db_user.github_token
    
    github = GitHubService(github_token)
    
    try:
        temp_dir = await github.clone_repo(repo_url, branch)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to clone repository") from e
    
    scan = Scan(
        user_id=user_id,
        source_type="github",
        source_path=repo_url,
        branch=branch,
        status=ScanStatus.PENDING.value,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    await db.refresh(scan, attribute_names=["findings"])
    
    background_tasks.add_task(run_scan, scan.id, temp_dir, settings.DATABASE_URL, enable_ai)
    
    return ScanResponse.model_validate(scan)


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    scan = await _owned_scan(scan_id, db, user)
    return ScanResponse.model_validate(scan)


@router.get("/{scan_id}/findings", response_model=List[FindingResponse])
async def get_findings(
    scan_id: int,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    await _owned_scan(scan_id, db, user)
    query = select(Finding).where(Finding.scan_id == scan_id)
    if severity:
        query = query.where(Finding.severity == severity)
    
    result = await db.execute(query)
    findings = result.scalars().all()
    
    return [FindingResponse.model_validate(f) for f in findings]


@router.get("/{scan_id}/sarif")
async def get_sarif(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    scan = await _owned_scan(scan_id, db, user)
    if not scan.sarif_output:
        raise HTTPException(status_code=400, detail="SARIF not available")
    
    return scan.sarif_output


@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    query = select(Scan).options(selectinload(Scan.findings)).where(Scan.user_id == _user_id(user))
    query = query.order_by(Scan.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    scans = result.scalars().all()
    
    return [ScanResponse.model_validate(s) for s in scans]
