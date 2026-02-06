import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import io


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.get = AsyncMock()
    return db


@pytest.fixture
def sample_scan_data():
    return {
        "id": 1,
        "user_id": None,
        "status": "pending",
        "source_type": "upload",
        "source_path": "test.zip",
        "total_findings": 0,
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
    }


@pytest.fixture
def sample_findings():
    return [
        {
            "id": 1,
            "scan_id": 1,
            "rule_id": "python.lang.security.audit.eval-injection",
            "rule_name": "Eval Injection",
            "severity": "critical",
            "file_path": "app.py",
            "start_line": 10,
            "end_line": 10,
            "message": "Avoid using eval() with user input",
        },
        {
            "id": 2,
            "scan_id": 1,
            "rule_id": "python.lang.security.audit.hardcoded-password",
            "rule_name": "Hardcoded Password",
            "severity": "high",
            "file_path": "config.py",
            "start_line": 5,
            "end_line": 5,
            "message": "Hardcoded password detected",
        },
    ]


def test_scan_response_model():
    from app.schemas.scan import ScanResponse
    
    data = {
        "id": 1,
        "status": "completed",
        "source_type": "github",
        "source_path": "https://github.com/test/repo",
        "branch": "main",
        "commit_sha": "abc123",
        "languages_detected": ["python", "javascript"],
        "total_files": 10,
        "files_scanned": 10,
        "total_findings": 5,
        "critical_count": 1,
        "high_count": 2,
        "medium_count": 1,
        "low_count": 1,
        "error_message": None,
        "started_at": "2024-01-01T00:00:00",
        "completed_at": "2024-01-01T00:01:00",
        "created_at": "2024-01-01T00:00:00",
        "findings": [],
    }
    
    response = ScanResponse(**data)
    assert response.id == 1
    assert response.status == "completed"
    assert response.total_findings == 5


def test_finding_response_model():
    from app.schemas.scan import FindingResponse
    
    data = {
        "id": 1,
        "scan_id": 1,
        "rule_id": "test-rule",
        "rule_name": "Test Rule",
        "severity": "high",
        "file_path": "test.py",
        "start_line": 10,
        "end_line": 15,
        "start_col": 0,
        "end_col": 0,
        "code_snippet": "vulnerable_code()",
        "message": "Test message",
        "ai_explanation": None,
        "ai_remediation": None,
        "cwe_ids": ["CWE-79"],
        "owasp_ids": ["A03:2021"],
        "references": [],
        "is_false_positive": False,
        "created_at": "2024-01-01T00:00:00",
    }
    
    response = FindingResponse(**data)
    assert response.severity == "high"
    assert "CWE-79" in response.cwe_ids


def test_severity_validation():
    valid_severities = ["critical", "high", "medium", "low", "info"]
    
    for sev in valid_severities:
        assert sev in valid_severities


@pytest.mark.asyncio
async def test_scan_stats_calculation():
    from app.services.scanner import ScannerService
    
    scanner = ScannerService()
    findings = [
        {"severity": "critical"},
        {"severity": "critical"},
        {"severity": "high"},
        {"severity": "high"},
        {"severity": "high"},
        {"severity": "medium"},
        {"severity": "low"},
        {"severity": "low"},
    ]
    
    stats = scanner._calculate_stats(findings)
    
    assert stats["critical"] == 2
    assert stats["high"] == 3
    assert stats["medium"] == 1
    assert stats["low"] == 2


@pytest.mark.asyncio
async def test_finding_deduplication():
    from app.services.scanner import ScannerService
    
    scanner = ScannerService()
    findings = [
        {"file_path": "a.py", "start_line": 10, "rule_id": "r1"},
        {"file_path": "a.py", "start_line": 10, "rule_id": "r1"},
        {"file_path": "a.py", "start_line": 20, "rule_id": "r1"},
        {"file_path": "b.py", "start_line": 10, "rule_id": "r1"},
    ]
    
    unique = scanner._deduplicate_findings(findings)
    
    assert len(unique) == 3
