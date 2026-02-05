import asyncio
import hashlib
import json
import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import redis.asyncio as redis
from ..core.config import settings

LANGUAGE_EXTENSIONS = {
    "python": [".py", ".pyw", ".pyi"],
    "javascript": [".js", ".jsx", ".mjs", ".cjs"],
    "typescript": [".ts", ".tsx", ".mts", ".cts"],
    "go": [".go"],
    "java": [".java"],
    "ruby": [".rb", ".erb", ".rake"],
    "php": [".php", ".phtml", ".php3", ".php4", ".php5"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".c++", ".h++"],
    "csharp": [".cs"],
    "rust": [".rs"],
    "kotlin": [".kt", ".kts"],
    "swift": [".swift"],
    "scala": [".scala", ".sc"],
    "shell": [".sh", ".bash", ".zsh"],
    "yaml": [".yml", ".yaml"],
    "json": [".json"],
    "xml": [".xml"],
    "sql": [".sql"],
}

LANGUAGE_SCANNERS = {
    "python": ["semgrep", "bandit"],
    "javascript": ["semgrep"],
    "typescript": ["semgrep"],
    "go": ["semgrep"],
    "java": ["semgrep"],
    "ruby": ["semgrep"],
    "php": ["semgrep"],
    "default": ["semgrep"],
}

SEVERITY_MAP = {
    "ERROR": "high",
    "WARNING": "medium",
    "INFO": "low",
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low",
}


class ScanCache:
    def __init__(self, redis_url: Optional[str] = None, ttl: int = 3600):
        self.ttl = ttl
        self._memory_cache: Dict[str, tuple] = {}
        self._redis = None
        if redis_url:
            try:
                self._redis = redis.from_url(redis_url)
            except Exception:
                pass

    def _file_hash(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    async def get(self, file_path: str) -> Optional[List[Dict]]:
        try:
            file_hash = self._file_hash(file_path)
            cache_key = f"scan:{file_hash}"
            
            if self._redis:
                cached = await self._redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            if cache_key in self._memory_cache:
                data, expires = self._memory_cache[cache_key]
                if datetime.utcnow() < expires:
                    return data
                del self._memory_cache[cache_key]
            
            return None
        except Exception:
            return None

    async def set(self, file_path: str, findings: List[Dict]) -> None:
        try:
            file_hash = self._file_hash(file_path)
            cache_key = f"scan:{file_hash}"
            
            if self._redis:
                await self._redis.setex(cache_key, self.ttl, json.dumps(findings))
            
            expires = datetime.utcnow() + timedelta(seconds=self.ttl)
            self._memory_cache[cache_key] = (findings, expires)
        except Exception:
            pass


class ParallelScanner:
    def __init__(
        self,
        progress_callback: Optional[Callable] = None,
        max_workers: int = 4,
        use_cache: bool = True,
    ):
        self.progress_callback = progress_callback
        self.max_workers = max_workers
        self.cache = ScanCache(settings.REDIS_URL) if use_cache else None
        self.custom_rules_path = Path(__file__).parent.parent / "rules"
        self._skip_dirs = {
            ".git", "node_modules", "__pycache__", "venv", ".venv",
            "vendor", "dist", "build", ".next", ".nuxt", "target",
            "bin", "obj", ".idea", ".vscode", "coverage", ".tox",
        }

    async def scan_directory(
        self,
        directory: str,
        incremental: bool = False,
        changed_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        path = Path(directory)
        if not path.exists():
            raise ValueError(f"Directory not found: {directory}")

        languages = self._detect_languages(path)
        all_files = self._get_scannable_files(path)
        
        if incremental and changed_files:
            files_to_scan = [f for f in all_files if str(f) in changed_files]
        else:
            files_to_scan = all_files

        findings = []
        cached_findings = []
        files_to_process = []

        if self.cache:
            for file in files_to_scan:
                cached = await self.cache.get(str(file))
                if cached:
                    cached_findings.extend(cached)
                else:
                    files_to_process.append(file)
        else:
            files_to_process = files_to_scan

        if files_to_process:
            scan_results = await self._parallel_scan(directory, files_to_process, languages)
            findings.extend(scan_results)
            
            if self.cache:
                file_findings: Dict[str, List[Dict]] = {}
                for f in scan_results:
                    fp = f.get("file_path", "")
                    if fp not in file_findings:
                        file_findings[fp] = []
                    file_findings[fp].append(f)
                
                for fp, ff in file_findings.items():
                    await self.cache.set(fp, ff)

        all_findings = findings + cached_findings
        all_findings = self._deduplicate_findings(all_findings)

        return {
            "languages": languages,
            "total_files": len(all_files),
            "files_scanned": len(files_to_scan),
            "files_cached": len(files_to_scan) - len(files_to_process),
            "findings": all_findings,
            "stats": self._calculate_stats(all_findings),
        }

    async def _parallel_scan(
        self,
        directory: str,
        files: List[Path],
        languages: List[str],
    ) -> List[Dict]:
        findings = []
        
        scan_tasks = []
        
        scan_tasks.append(self._run_semgrep(directory, languages))
        
        if "python" in languages:
            scan_tasks.append(self._run_bandit(directory))
        
        results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                findings.extend(result)
        
        return findings

    def _detect_languages(self, path: Path) -> List[str]:
        detected = set()
        for file in path.rglob("*"):
            if file.is_file() and not self._should_skip(file):
                suffix = file.suffix.lower()
                for lang, exts in LANGUAGE_EXTENSIONS.items():
                    if suffix in exts:
                        detected.add(lang)
        return list(detected)

    def _get_scannable_files(self, path: Path) -> List[Path]:
        files = []
        for file in path.rglob("*"):
            if file.is_file() and not self._should_skip(file):
                for exts in LANGUAGE_EXTENSIONS.values():
                    if file.suffix.lower() in exts:
                        files.append(file)
                        break
        return files

    def _should_skip(self, file: Path) -> bool:
        return any(d in file.parts for d in self._skip_dirs)

    async def _run_semgrep(self, directory: str, languages: List[str]) -> List[Dict]:
        findings = []
        try:
            configs = [
                "p/security-audit",
                "p/secrets",
                "p/owasp-top-ten",
                "p/ci",
            ]
            
            if "python" in languages:
                configs.append("p/python")
            if "javascript" in languages or "typescript" in languages:
                configs.extend(["p/javascript", "p/typescript"])
            if "go" in languages:
                configs.append("p/golang")
            if "java" in languages:
                configs.append("p/java")
            if "ruby" in languages:
                configs.append("p/ruby")
            if "php" in languages:
                configs.append("p/php")
            
            cmd = [
                "semgrep", "scan",
                "--json",
                "--no-git-ignore",
                "--timeout", "30",
                "--jobs", str(self.max_workers),
            ]
            for config in configs:
                cmd.extend(["--config", config])
            
            if self.custom_rules_path.exists():
                cmd.extend(["--config", str(self.custom_rules_path)])
            
            cmd.append(directory)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=settings.SCAN_TIMEOUT
            )
            
            if stdout:
                result = json.loads(stdout.decode())
                for r in result.get("results", []):
                    finding = self._parse_semgrep_result(r)
                    findings.append(finding)
                    
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            pass
        
        return findings

    async def _run_bandit(self, directory: str) -> List[Dict]:
        findings = []
        try:
            cmd = [
                "bandit", "-r", "-f", "json", "-ll",
                "--exit-zero",
                directory
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=120
            )
            
            if stdout:
                result = json.loads(stdout.decode())
                for r in result.get("results", []):
                    finding = self._parse_bandit_result(r)
                    findings.append(finding)
                    
        except Exception:
            pass
        
        return findings

    def _parse_semgrep_result(self, r: Dict) -> Dict:
        return {
            "rule_id": r.get("check_id", "unknown"),
            "rule_name": r.get("extra", {}).get("message", r.get("check_id", "")),
            "severity": SEVERITY_MAP.get(
                r.get("extra", {}).get("severity", "medium").upper(),
                "medium"
            ),
            "file_path": r.get("path", ""),
            "start_line": r.get("start", {}).get("line", 0),
            "end_line": r.get("end", {}).get("line", 0),
            "start_col": r.get("start", {}).get("col", 0),
            "end_col": r.get("end", {}).get("col", 0),
            "code_snippet": r.get("extra", {}).get("lines", ""),
            "message": r.get("extra", {}).get("message", ""),
            "cwe_ids": self._extract_cwes(r),
            "owasp_ids": self._extract_owasp(r),
            "references": r.get("extra", {}).get("metadata", {}).get("references", []),
            "tool": "semgrep",
            "fingerprint": r.get("extra", {}).get("fingerprint", ""),
        }

    def _parse_bandit_result(self, r: Dict) -> Dict:
        severity = r.get("issue_severity", "medium").lower()
        return {
            "rule_id": f"bandit/{r.get('test_id', 'unknown')}",
            "rule_name": r.get("test_name", ""),
            "severity": severity if severity in ["critical", "high", "medium", "low"] else "medium",
            "file_path": r.get("filename", ""),
            "start_line": r.get("line_number", 0),
            "end_line": r.get("line_range", [0])[-1] if r.get("line_range") else r.get("line_number", 0),
            "start_col": r.get("col_offset", 0),
            "end_col": r.get("end_col_offset", 0),
            "code_snippet": r.get("code", ""),
            "message": r.get("issue_text", ""),
            "cwe_ids": [f"CWE-{r.get('issue_cwe', {}).get('id', '')}"] if r.get("issue_cwe") else [],
            "owasp_ids": [],
            "references": [r.get("more_info", "")] if r.get("more_info") else [],
            "tool": "bandit",
            "confidence": r.get("issue_confidence", "medium"),
        }

    def _extract_cwes(self, r: Dict) -> List[str]:
        metadata = r.get("extra", {}).get("metadata", {})
        cwes = metadata.get("cwe", [])
        if isinstance(cwes, str):
            return [cwes]
        return cwes if cwes else []

    def _extract_owasp(self, r: Dict) -> List[str]:
        metadata = r.get("extra", {}).get("metadata", {})
        owasp = metadata.get("owasp", [])
        if isinstance(owasp, str):
            return [owasp]
        return owasp if owasp else []

    def _deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []
        for f in findings:
            key = (f.get("file_path"), f.get("start_line"), f.get("rule_id"))
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    def _calculate_stats(self, findings: List[Dict]) -> Dict[str, int]:
        stats = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            sev = f.get("severity", "medium").lower()
            if sev in stats:
                stats[sev] += 1
        return stats
