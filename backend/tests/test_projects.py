import pytest
from datetime import datetime


def test_team_model_creation():
    from app.models.project import Team
    
    team = Team(
        name="Test Team",
        slug="test-team",
        description="A test team",
        owner_id=1,
    )
    
    assert team.name == "Test Team"
    assert team.slug == "test-team"
    assert team.owner_id == 1


def test_project_model_creation():
    from app.models.project import Project
    
    project = Project(
        name="Test Project",
        slug="test-project",
        description="A test project",
        owner_id=1,
        default_branch="main",
        scan_on_push=True,
        scan_on_pr=True,
        fail_threshold="high",
    )
    
    assert project.name == "Test Project"
    assert project.default_branch == "main"
    assert project.scan_on_push is True
    assert project.fail_threshold == "high"


def test_slugify():
    from app.api.projects import slugify
    
    assert slugify("Test Project") == "test-project"
    assert slugify("My Awesome App!") == "my-awesome-app"
    assert slugify("hello   world") == "hello-world"
    assert slugify("Test--Project") == "test-project"


def test_scan_schedule_model():
    from app.models.project import ScanSchedule
    
    schedule = ScanSchedule(
        project_id=1,
        cron_expression="0 0 * * *",
        branch="main",
        enable_ai=True,
        is_active=True,
    )
    
    assert schedule.cron_expression == "0 0 * * *"
    assert schedule.enable_ai is True


def test_project_response_schema():
    from app.api.projects import ProjectResponse
    
    data = {
        "id": 1,
        "name": "Test",
        "slug": "test",
        "description": None,
        "team_id": None,
        "owner_id": 1,
        "repository_id": None,
        "default_branch": "main",
        "scan_on_push": True,
        "scan_on_pr": True,
        "fail_threshold": "high",
        "last_scan_at": None,
        "created_at": datetime.utcnow(),
    }
    
    response = ProjectResponse(**data)
    assert response.name == "Test"
    assert response.fail_threshold == "high"


def test_team_response_schema():
    from app.api.projects import TeamResponse
    
    data = {
        "id": 1,
        "name": "Team A",
        "slug": "team-a",
        "description": "Test team",
        "owner_id": 1,
        "member_count": 5,
        "project_count": 3,
        "created_at": datetime.utcnow(),
    }
    
    response = TeamResponse(**data)
    assert response.name == "Team A"
    assert response.member_count == 5


def test_project_stats_schema():
    from app.api.projects import ProjectStats
    
    stats = ProjectStats(
        total_scans=10,
        total_findings=50,
        critical_count=2,
        high_count=8,
        trend="improving",
    )
    
    assert stats.total_scans == 10
    assert stats.trend == "improving"
