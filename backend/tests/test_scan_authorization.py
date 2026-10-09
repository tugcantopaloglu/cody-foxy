from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
import io
import tarfile
import zipfile

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api import scans, websocket, projects, auth
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models import Finding, Scan, User, Team, Project


@pytest_asyncio.fixture
async def scan_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with factory() as db:
        db.add_all([User(id=1, email="owner@example.test", username="owner"),
                    User(id=2, email="other@example.test", username="other")])
        await db.flush()
        db.add_all([Team(id=1, name="Owner team", slug="owner-team", owner_id=1),
                    Team(id=2, name="Other team", slug="other-team", owner_id=2),
                    Project(id=1, name="Owner project", slug="owner-project", owner_id=1),
                    Project(id=2, name="Other project", slug="other-project", owner_id=2)])
        db.add_all([Scan(id=1, user_id=1, status="completed", source_path="owner.zip",
                         created_at=datetime(2024, 1, 1), sarif_output={"version": "2.1.0"}),
                    Scan(id=2, user_id=2, source_path="other.zip"),
                    Scan(id=3, user_id=None, source_path="legacy-anonymous.zip")])
        await db.flush()
        db.add(Finding(scan_id=1, rule_id="test-rule", rule_name="Fixture finding",
                       severity="high", file_path="fixture.py", start_line=1, end_line=1,
                       message="Fixture finding"))
        await db.commit()
        app = FastAPI()
        app.include_router(scans.router, prefix="/scans")
        app.include_router(projects.router)
        app.include_router(auth.router, prefix="/auth")

        async def override_db():
            yield db

        app.dependency_overrides[get_db] = override_db
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    await engine.dispose()


def headers(user_id):
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user_id)})}"}


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/scans/", "/scans/1", "/scans/1/findings", "/scans/1/sarif"])
async def test_anonymous_cannot_read_scans(scan_client, path):
    response = await scan_client.get(path)
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("suffix", ["", "/findings", "/sarif"])
@pytest.mark.parametrize("scan_id", [2, 3, 999])
async def test_foreign_legacy_and_missing_scans_are_not_disclosed(scan_client, scan_id, suffix):
    response = await scan_client.get(f"/scans/{scan_id}{suffix}", headers=headers(1))
    assert response.status_code == 404
    assert response.json() == {"detail": "Scan not found"}


@pytest.mark.asyncio
async def test_owner_can_read_scan_findings_and_sarif(scan_client):
    response = await scan_client.get("/scans/1", headers=headers(1))
    assert response.status_code == 200
    assert response.json()["source_path"] == "owner.zip"
    assert len(response.json()["findings"]) == 1
    response = await scan_client.get("/scans/1/findings?severity=high", headers=headers(1))
    assert response.status_code == 200
    assert response.json()[0]["rule_id"] == "test-rule"
    response = await scan_client.get("/scans/1/findings?severity=low", headers=headers(1))
    assert response.json() == []
    response = await scan_client.get("/scans/1/sarif", headers=headers(1))
    assert response.json() == {"version": "2.1.0"}


@pytest.mark.asyncio
@pytest.mark.parametrize("owner,expected", [(1, [1]), (2, [2])])
async def test_lists_are_scoped_to_the_owner(scan_client, owner, expected):
    response = await scan_client.get("/scans/", headers=headers(owner))
    assert response.status_code == 200
    assert [scan["id"] for scan in response.json()] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1"])
async def test_pagination_bounds(scan_client, query):
    response = await scan_client.get(f"/scans/?{query}", headers=headers(1))
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_anonymous_cannot_create_scans(scan_client):
    response = await scan_client.post("/scans/upload", files={"file": ("fixture.zip", b"test")})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_login_and_authenticated_scan_access(scan_client):
    account = {"email": "new@example.com", "username": "new-user", "password": "Fixture-password-123"}
    response = await scan_client.post("/auth/register", json=account)
    assert response.status_code == 200
    token = response.json()["access_token"]
    response = await scan_client.get("/scans/", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == []
    response = await scan_client.post("/auth/login", json={"email": account["email"], "password": account["password"]})
    assert response.status_code == 200
    response = await scan_client.post("/auth/login", json={"email": account["email"], "password": "incorrect"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_archive_upload_returns_owned_scan(scan_client, tmp_path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("fixture.py", "value = 1")
    directory = tmp_path / "upload"
    directory.mkdir()
    with patch.object(scans.tempfile, "mkdtemp", return_value=str(directory)), patch.object(scans, "run_scan", new_callable=AsyncMock):
        response = await scan_client.post("/scans/upload", headers=headers(1),
                                         files={"file": ("fixture.zip", archive.getvalue())})
    assert response.status_code == 200
    scan_id = response.json()["id"]
    response = await scan_client.get(f"/scans/{scan_id}", headers=headers(2))
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unsafe_tar_archive_is_rejected_and_removed(scan_client, tmp_path):
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as bundle:
        member = tarfile.TarInfo("../../outside.txt")
        member.size = 4
        bundle.addfile(member, io.BytesIO(b"test"))
    directory = tmp_path / "upload"
    directory.mkdir()
    with patch.object(scans.tempfile, "mkdtemp", return_value=str(directory)):
        response = await scan_client.post("/scans/upload", headers=headers(1),
                                         files={"file": ("fixture.tar.gz", archive.getvalue())})
    assert response.status_code == 400
    assert not directory.exists()
    assert not (tmp_path / "outside.txt").exists()
    response = await scan_client.post("/scans/github?repo_url=https://github.com/example/fixture")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("subject", ["invalid", "0", "-1"])
async def test_invalid_identity_fails_closed(scan_client, subject):
    response = await scan_client.get("/scans/", headers=headers(subject))
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/teams/2", "/projects/2", "/projects/2/stats"])
async def test_foreign_team_and_project_details_are_not_disclosed(scan_client, path):
    response = await scan_client.get(path, headers=headers(1))
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/teams/1", "/projects/1", "/projects/1/stats"])
async def test_owner_can_read_team_and_project_details(scan_client, path):
    response = await scan_client.get(path, headers=headers(1))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_broadcast_reaches_only_owner_connections():
    manager = websocket.ConnectionManager()
    owner_scan = AsyncMock()
    owner_global = AsyncMock()
    other_global = AsyncMock()
    other_scan = AsyncMock()
    manager.active_connections = {
        "user:1:scan:7": [owner_scan], "user:1": [owner_global],
        "user:2:scan:7": [other_scan], "user:2": [other_global]
    }
    event = {"type": "scan_completed", "scan_id": 7}
    await manager.broadcast(event, scan_id="7", user_id=1)
    owner_scan.send_json.assert_awaited_once_with(event)
    owner_global.send_json.assert_awaited_once_with(event)
    other_global.send_json.assert_not_awaited()
    other_scan.send_json.assert_not_awaited()


@pytest.mark.asyncio
async def test_foreign_scan_websocket_is_rejected_before_accept():
    socket = AsyncMock()
    socket.headers = headers(2)
    socket.query_params = {}
    db = AsyncMock()
    db.get.return_value = Scan(id=7, user_id=1)
    await websocket.websocket_scan(socket, "7", db)
    socket.close.assert_awaited_once_with(code=1008)
    socket.accept.assert_not_awaited()
