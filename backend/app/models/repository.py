from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    github_id = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(500), nullable=False)
    url = Column(String(500), nullable=False)
    default_branch = Column(String(100), default="main")
    is_private = Column(Boolean, default=False)
    last_scanned = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="repositories")
    scans = relationship("Scan", back_populates="repository")
