from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RepositoryCreate(BaseModel):
    github_id: Optional[str] = None
    name: str
    full_name: str
    url: str
    default_branch: str = "main"
    is_private: bool = False


class RepositoryResponse(BaseModel):
    id: int
    github_id: Optional[str]
    name: str
    full_name: str
    url: str
    default_branch: str
    is_private: bool
    last_scanned: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
