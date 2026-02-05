from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int
    slug: str
    owner_id: int
    member_count: int = 0
    project_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: Optional[int] = None
    repository_id: Optional[int] = None
    default_branch: str = "main"
    scan_on_push: bool = True
    scan_on_pr: bool = True
    fail_threshold: str = "high"


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_branch: Optional[str] = None
    scan_on_push: Optional[bool] = None
    scan_on_pr: Optional[bool] = None
    fail_threshold: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    slug: str
    owner_id: int
    last_scan_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectStats(BaseModel):
    total_scans: int
    total_findings: int
    critical_count: int
    high_count: int
    trend: str


class ScanScheduleBase(BaseModel):
    project_id: int
    cron_expression: str
    branch: str = "main"
    enable_ai: bool = True
    is_active: bool = True


class ScanScheduleCreate(ScanScheduleBase):
    pass


class ScanScheduleResponse(ScanScheduleBase):
    id: int
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
