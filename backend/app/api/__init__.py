from fastapi import APIRouter
from .auth import router as auth_router
from .scans import router as scans_router
from .repos import router as repos_router
from .websocket import router as ws_router
from .projects import router as projects_router
from .github_app import router as github_app_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(scans_router, prefix="/scans", tags=["scans"])
api_router.include_router(repos_router, prefix="/repos", tags=["repositories"])
api_router.include_router(ws_router, prefix="/ws", tags=["websocket"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(github_app_router, prefix="/github", tags=["github"])
