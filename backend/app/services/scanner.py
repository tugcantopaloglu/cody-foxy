import asyncio
import json
import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import yaml

LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "go": [".go"],
    "java": [".java"],
    "ruby": [".rb"],
    "php": [".php"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp"],
    "csharp": [".cs"],
    "rust": [".rs"],
    "kotlin": [".kt", ".kts"],
    "swift": [".swift"],
    "scala": [".scala"],
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


class ScannerService:
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.custom_rules_path = Path(__file__).parent.parent / "rules"

    async def scan_directory(self, directory: str) -> Dict[str, Any]:
        path = Path(directory)
        if not path.exists():
            raise ValueError(f"Directory not found: {directory}")

        languages = self._detect_languages(path)
        files = self._get_scannable_files(path)
        
        findings = []
        scanned = 0
        
        semgrep_results = await self._run_semgrep(directory, languages)
        findings.extend(semgrep_results)
        
        if "python" in languages:
            bandit_results = await self._run_bandit(directory)
            findings.extend(bandit_results)
        
        findings = self._deduplicate_findings(findings)
        
        return {
            "languages": languages,
            "total_files": len(files),
            "files_scanned": len(files),
            "findings": findings,
            "stats": self._calculate_stats(findings),
        }

    def _detect_languages(self, path: Path) -> List[str]:
        detected = set()
        for file in path.rglob("*"):
            if file.is_file():
                suffix = file.suffix.lower()
                for lang, exts in LANGUAGE_EXTENSIONS.items():
                    if suffix in exts:
                        detected.add(lang)
        return list(detected)

    def _get_scannable_files(self, path: Path) -> List[Path]:
        files = []
        skip_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "vendor", "dist", "build"}
        for file in path.rglob("*"):
            if file.is_file() and not any(d in file.parts for d in skip_dirs):
                for exts in LANGUAGE_EXTENSIONS.values():
                    if file.suffix.lower() in exts:
                        files.append(file)
                        break
        return files

    async def _run_semgrep(self, directory: str, languages: List[str]) -> List[Dict]:
        findings = []
        try:
            configs = ["p/security-audit", "p/secrets", "p/owasp-top-ten"]
            
            cmd = [
                "semgrep", "scan",
                "--json",
                "--no-git-ignore",
                "--timeout", "30",
            ]
            for config in configs:
                cmd.extend(["--config", config])
            cmd.append(directory)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if stdout:
                result = json.loads(stdout.decode())
                for r in result.get("results", []):
                    finding = {
                        "rule_id": r.get("check_id", "unknown"),
                        "rule_name": r.get("extra", {}).get("message", r.get("check_id", "")),
                        "severity": SEVERITY_MAP.get(r.get("extra", {}).get("severity", "medium").upper(), "medium"),
                        "file_path": r.get("path", ""),
                        "start_line": r.get("start", {}).get("line", 0),
                        "end_line": r.get("end", {}).get("line", 0),
                        "start_col": r.get("start", {}).get("col", 0),
                        "end_col": r.get("end", {}).get("col", 0),
                        "code_snippet": r.get("extra", {}).get("lines", ""),
                        "message": r.get("extra", {}).get("message", ""),
                        "cwe_ids": r.get("extra", {}).get("metadata", {}).get("cwe", []),
                        "owasp_ids": r.get("extra", {}).get("metadata", {}).get("owasp", []),
                        "references": r.get("extra", {}).get("metadata", {}).get("references", []),
                        "tool": "semgrep",
                    }
                    findings.append(finding)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            pass
        return findings

    async def _run_bandit(self, directory: str) -> List[Dict]:
        findings = []
        try:
            cmd = ["bandit", "-r", "-f", "json", "-ll", directory]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=120)
            
            if stdout:
                result = json.loads(stdout.decode())
                for r in result.get("results", []):
                    severity = r.get("issue_severity", "medium").lower()
                    finding = {
                        "rule_id": f"bandit/{r.get('test_id', 'unknown')}",
                        "rule_name": r.get("test_name", ""),
                        "severity": severity if severity in ["critical", "high", "medium", "low"] else "medium",
                        "file_path": r.get("filename", ""),
                        "start_line": r.get("line_number", 0),
                        "end_line": r.get("line_range", [0])[-1] if r.get("line_range") else r.get("line_number", 0),
                        "start_col": 0,
                        "end_col": 0,
                        "code_snippet": r.get("code", ""),
                        "message": r.get("issue_text", ""),
                        "cwe_ids": [f"CWE-{r.get('issue_cwe', {}).get('id', '')}"] if r.get("issue_cwe") else [],
                        "owasp_ids": [],
                        "references": [r.get("more_info", "")] if r.get("more_info") else [],
                        "tool": "bandit",
                    }
                    findings.append(finding)
        except Exception:
            pass
        return findings

    def _deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []
        for f in findings:
            key = (f["file_path"], f["start_line"], f["rule_id"])
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
