import httpx
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional
import git
from ..core.config import settings


class GitHubService:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.api_base = "https://api.github.com"

    async def exchange_code(self, code: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"},
            )
            return response.json()

    async def get_user(self) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/user",
                headers=self._headers(),
            )
            return response.json()

    async def get_user_repos(self, page: int = 1, per_page: int = 30) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/user/repos",
                params={
                    "page": page,
                    "per_page": per_page,
                    "sort": "updated",
                    "direction": "desc",
                },
                headers=self._headers(),
            )
            return response.json()

    async def get_repo(self, owner: str, repo: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/repos/{owner}/{repo}",
                headers=self._headers(),
            )
            return response.json()

    async def get_repo_contents(self, owner: str, repo: str, path: str = "", ref: str = "main") -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref},
                headers=self._headers(),
            )
            return response.json()

    async def clone_repo(self, repo_url: str, branch: str = "main") -> str:
        temp_dir = tempfile.mkdtemp(prefix="cody_scan_")
        
        clone_url = repo_url
        if self.access_token and "github.com" in repo_url:
            clone_url = repo_url.replace("https://", f"https://x-access-token:{self.access_token}@")
        
        repo = git.Repo.clone_from(
            clone_url,
            temp_dir,
            branch=branch,
            depth=1,
        )
        
        return temp_dir

    async def create_check_run(self, owner: str, repo: str, head_sha: str, findings: List[Dict]) -> Dict:
        annotations = []
        for f in findings[:50]:
            annotations.append({
                "path": f["file_path"],
                "start_line": f["start_line"],
                "end_line": f["end_line"],
                "annotation_level": self._severity_to_level(f["severity"]),
                "message": f["message"],
                "title": f["rule_name"],
            })

        conclusion = "success"
        if any(f["severity"] in ["critical", "high"] for f in findings):
            conclusion = "failure"
        elif any(f["severity"] == "medium" for f in findings):
            conclusion = "neutral"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/repos/{owner}/{repo}/check-runs",
                headers={**self._headers(), "Accept": "application/vnd.github+json"},
                json={
                    "name": "Cody Foxy Security Scan",
                    "head_sha": head_sha,
                    "status": "completed",
                    "conclusion": conclusion,
                    "output": {
                        "title": f"Found {len(findings)} security issues",
                        "summary": self._build_summary(findings),
                        "annotations": annotations,
                    },
                },
            )
            return response.json()

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _severity_to_level(self, severity: str) -> str:
        mapping = {
            "critical": "failure",
            "high": "failure",
            "medium": "warning",
            "low": "notice",
            "info": "notice",
        }
        return mapping.get(severity, "warning")

    def _build_summary(self, findings: List[Dict]) -> str:
        stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            sev = f.get("severity", "medium")
            if sev in stats:
                stats[sev] += 1
        
        return f"""## 🦊 Cody Foxy Security Scan Results

| Severity | Count |
|----------|-------|
| 🔴 Critical | {stats['critical']} |
| 🟠 High | {stats['high']} |
| 🟡 Medium | {stats['medium']} |
| 🟢 Low | {stats['low']} |

**Total Issues:** {len(findings)}
"""
