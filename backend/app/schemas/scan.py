from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ScanCreate(BaseModel):
    repository_id: Optional[int] = None
    source_type: str = "upload"
    branch: Optional[str] = None


class FindingResponse(BaseModel):
    id: int
    rule_id: str
    rule_name: str
    severity: str
    file_path: str
    start_line: int
    end_line: int
    start_col: int
    end_col: int
    code_snippet: Optional[str]
    message: str
    ai_explanation: Optional[str]
    ai_remediation: Optional[str]
    cwe_ids: List[str]
    owasp_ids: List[str]
    references: List[str]
    is_false_positive: bool

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    id: int
    status: str
    source_type: str
    source_path: Optional[str]
    branch: Optional[str]
    commit_sha: Optional[str]
    languages_detected: List[str]
    total_files: int
    files_scanned: int
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    findings: List[FindingResponse] = []

    class Config:
        from_attributes = True


class ScanStatusUpdate(BaseModel):
    scan_id: int
    status: str
    files_scanned: int
    total_files: int
    current_file: Optional[str] = None
    findings_count: int = 0


class SarifOutput(BaseModel):
    version: str = "2.1.0"
    runs: List[Any]
