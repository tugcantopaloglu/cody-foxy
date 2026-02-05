from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from ..core.database import Base


class ScanStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
    status = Column(String(20), default=ScanStatus.PENDING.value)
    source_type = Column(String(20), default="upload")
    source_path = Column(String(500), nullable=True)
    branch = Column(String(100), nullable=True)
    commit_sha = Column(String(40), nullable=True)
    languages_detected = Column(JSON, default=list)
    total_files = Column(Integer, default=0)
    files_scanned = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    sarif_output = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
    repository = relationship("Repository", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    rule_id = Column(String(200), nullable=False)
    rule_name = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    start_col = Column(Integer, default=0)
    end_col = Column(Integer, default=0)
    code_snippet = Column(Text, nullable=True)
    message = Column(Text, nullable=False)
    ai_explanation = Column(Text, nullable=True)
    ai_remediation = Column(Text, nullable=True)
    cwe_ids = Column(JSON, default=list)
    owasp_ids = Column(JSON, default=list)
    references = Column(JSON, default=list)
    is_false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="findings")
