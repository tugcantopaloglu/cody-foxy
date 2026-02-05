from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.repository import Repository
from ..models.user import User
from ..schemas.repository import RepositoryResponse, RepositoryCreate
from ..services.github_service import GitHubService

router = APIRouter()


@router.get("/github", response_model=List[dict])
async def list_github_repos(
    page: int = 1,
    per_page: int = 30,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = await db.execute(select(User).where(User.id == int(user["sub"])))
    db_user = result.scalar_one_or_none()
    
    if not db_user or not db_user.github_token:
        raise HTTPException(status_code=400, detail="GitHub not connected")
    
    github = GitHubService(db_user.github_token)
    repos = await github.get_user_repos(page, per_page)
    
    return repos


@router.post("/sync", response_model=List[RepositoryResponse])
async def sync_repos(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = int(user["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    
    if not db_user or not db_user.github_token:
        raise HTTPException(status_code=400, detail="GitHub not connected")
    
    github = GitHubService(db_user.github_token)
    gh_repos = await github.get_user_repos(per_page=100)
    
    synced = []
    for gh_repo in gh_repos:
        result = await db.execute(
            select(Repository).where(
                Repository.user_id == user_id,
                Repository.github_id == str(gh_repo["id"])
            )
        )
        repo = result.scalar_one_or_none()
        
        if repo:
            repo.name = gh_repo["name"]
            repo.full_name = gh_repo["full_name"]
            repo.url = gh_repo["html_url"]
            repo.default_branch = gh_repo.get("default_branch", "main")
            repo.is_private = gh_repo.get("private", False)
        else:
            repo = Repository(
                user_id=user_id,
                github_id=str(gh_repo["id"]),
                name=gh_repo["name"],
                full_name=gh_repo["full_name"],
                url=gh_repo["html_url"],
                default_branch=gh_repo.get("default_branch", "main"),
                is_private=gh_repo.get("private", False),
            )
            db.add(repo)
        
        synced.append(repo)
    
    await db.commit()
    
    return [RepositoryResponse.model_validate(r) for r in synced]


@router.get("/", response_model=List[RepositoryResponse])
async def list_repos(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = await db.execute(
        select(Repository).where(Repository.user_id == int(user["sub"]))
    )
    repos = result.scalars().all()
    
    return [RepositoryResponse.model_validate(r) for r in repos]


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repo(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = await db.execute(
        select(Repository).where(
            Repository.id == repo_id,
            Repository.user_id == int(user["sub"])
        )
    )
    repo = result.scalar_one_or_none()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return RepositoryResponse.model_validate(repo)
