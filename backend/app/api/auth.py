from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_db
from ..core.security import create_access_token, hash_password, verify_password, get_current_user
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse, GitHubCallback
from ..services.github_service import GitHubService

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/github/callback", response_model=TokenResponse)
async def github_callback(callback: GitHubCallback, db: AsyncSession = Depends(get_db)):
    github = GitHubService()
    token_data = await github.exchange_code(callback.code)
    
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data.get("error_description", "GitHub auth failed"))
    
    access_token = token_data["access_token"]
    github = GitHubService(access_token)
    gh_user = await github.get_user()
    
    result = await db.execute(select(User).where(User.github_id == str(gh_user["id"])))
    user = result.scalar_one_or_none()
    
    if not user:
        result = await db.execute(select(User).where(User.email == gh_user.get("email")))
        user = result.scalar_one_or_none()
    
    if user:
        user.github_id = str(gh_user["id"])
        user.github_token = access_token
        user.avatar_url = gh_user.get("avatar_url")
    else:
        user = User(
            email=gh_user.get("email") or f"{gh_user['login']}@github.local",
            username=gh_user["login"],
            github_id=str(gh_user["id"]),
            github_token=access_token,
            avatar_url=gh_user.get("avatar_url"),
        )
        db.add(user)
    
    await db.commit()
    await db.refresh(user)
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def get_me(token: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.execute(select(User).where(User.id == int(token["sub"])))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.model_validate(user)
