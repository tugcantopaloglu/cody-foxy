from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from datetime import datetime

from ..core.database import get_db
from ..core.security import get_current_user, require_auth
from ..core.rate_limiter import rate_limit
from ..models.project import Team, Project, team_members, project_members

router = APIRouter()


class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    owner_id: int
    member_count: int = 0
    project_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: Optional[int] = None
    repository_id: Optional[int] = None
    default_branch: str = "main"
    scan_on_push: bool = True
    scan_on_pr: bool = True
    fail_threshold: str = "high"


class ProjectResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    team_id: Optional[int]
    owner_id: int
    repository_id: Optional[int]
    default_branch: str
    scan_on_push: bool
    scan_on_pr: bool
    fail_threshold: str
    last_scan_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectStats(BaseModel):
    total_scans: int
    total_findings: int
    critical_count: int
    high_count: int
    trend: str


def slugify(text: str) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


@router.post("/teams", response_model=TeamResponse)
@rate_limit("api_default")
async def create_team(
    request: Request,
    team: TeamCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    slug = slugify(team.name)
    
    existing = await db.execute(select(Team).where(Team.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    new_team = Team(
        name=team.name,
        slug=slug,
        description=team.description,
        owner_id=int(user["sub"]),
    )
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    
    return TeamResponse.model_validate(new_team)


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    user_id = int(user["sub"])
    
    result = await db.execute(
        select(Team).where(
            (Team.owner_id == user_id) |
            (Team.id.in_(
                select(team_members.c.team_id).where(team_members.c.user_id == user_id)
            ))
        )
    )
    teams = result.scalars().all()
    
    return [TeamResponse.model_validate(t) for t in teams]


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return TeamResponse.model_validate(team)


@router.post("/teams/{team_id}/members")
async def add_team_member(
    team_id: int,
    user_email: str,
    role: str = "member",
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.owner_id != int(user["sub"]):
        raise HTTPException(status_code=403, detail="Not team owner")
    
    from ..models.user import User
    result = await db.execute(select(User).where(User.email == user_email))
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.execute(
        team_members.insert().values(
            team_id=team_id,
            user_id=member.id,
            role=role,
        )
    )
    await db.commit()
    
    return {"status": "added", "user_id": member.id}


@router.post("/projects", response_model=ProjectResponse)
@rate_limit("api_default")
async def create_project(
    request: Request,
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    slug = slugify(project.name)
    user_id = int(user["sub"])
    
    new_project = Project(
        name=project.name,
        slug=slug,
        description=project.description,
        team_id=project.team_id,
        owner_id=user_id,
        repository_id=project.repository_id,
        default_branch=project.default_branch,
        scan_on_push=project.scan_on_push,
        scan_on_pr=project.scan_on_pr,
        fail_threshold=project.fail_threshold,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return ProjectResponse.model_validate(new_project)


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    team_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    user_id = int(user["sub"])
    
    query = select(Project).where(
        (Project.owner_id == user_id) |
        (Project.id.in_(
            select(project_members.c.project_id).where(
                project_members.c.user_id == user_id
            )
        ))
    )
    
    if team_id:
        query = query.where(Project.team_id == team_id)
    
    result = await db.execute(query.order_by(Project.updated_at.desc()))
    projects = result.scalars().all()
    
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse.model_validate(project)


@router.get("/projects/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    from ..models.scan import Scan
    from ..models.project import project_scans
    
    result = await db.execute(
        select(Scan).join(project_scans).where(
            project_scans.c.project_id == project_id
        ).order_by(Scan.created_at.desc()).limit(10)
    )
    scans = result.scalars().all()
    
    total_findings = sum(s.total_findings for s in scans)
    critical_count = sum(s.critical_count for s in scans)
    high_count = sum(s.high_count for s in scans)
    
    trend = "stable"
    if len(scans) >= 2:
        recent = scans[0].total_findings
        previous = scans[1].total_findings
        if recent < previous:
            trend = "improving"
        elif recent > previous:
            trend = "worsening"
    
    return ProjectStats(
        total_scans=len(scans),
        total_findings=total_findings,
        critical_count=critical_count,
        high_count=high_count,
        trend=trend,
    )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    updates: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != int(user["sub"]):
        raise HTTPException(status_code=403, detail="Not project owner")
    
    project.name = updates.name
    project.description = updates.description
    project.default_branch = updates.default_branch
    project.scan_on_push = updates.scan_on_push
    project.scan_on_pr = updates.scan_on_pr
    project.fail_threshold = updates.fail_threshold
    
    await db.commit()
    await db.refresh(project)
    
    return ProjectResponse.model_validate(project)


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != int(user["sub"]):
        raise HTTPException(status_code=403, detail="Not project owner")
    
    await db.delete(project)
    await db.commit()
    
    return {"status": "deleted"}
