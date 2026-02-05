from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', String(20), default='member'),
    Column('joined_at', DateTime, default=datetime.utcnow),
)


project_members = Table(
    'project_members',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', String(20), default='viewer'),
    Column('added_at', DateTime, default=datetime.utcnow),
)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("User", secondary=team_members, backref="teams")
    projects = relationship("Project", back_populates="team", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
    default_branch = Column(String(100), default="main")
    scan_on_push = Column(Boolean, default=True)
    scan_on_pr = Column(Boolean, default=True)
    fail_threshold = Column(String(20), default="high")
    notify_on_critical = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    last_scan_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="projects")
    owner = relationship("User", foreign_keys=[owner_id])
    repository = relationship("Repository")
    members = relationship("User", secondary=project_members, backref="projects")
    scans = relationship("Scan", secondary="project_scans", backref="project")


project_scans = Table(
    'project_scans',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('scan_id', Integer, ForeignKey('scans.id'), primary_key=True),
)


class ScanSchedule(Base):
    __tablename__ = "scan_schedules"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    branch = Column(String(100), default="main")
    enable_ai = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project")
