"""
User model - Core user authentication and profile
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserStatus(str, enum.Enum):
    """User account status"""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class User(Base):
    """
    User model representing system users across all tiers
    
    Tier 0: Production Committee members
    Tier 1: Prime contractor staff (CEO, EP, PD, Desk, PM)
    Tier 2: Subcontractor staff (PM, Team Lead, Workers)
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    name = Column(String(100), nullable=False)
    name_jp = Column(String(100), nullable=True)  # Japanese name
    phone = Column(String(20), nullable=True)
    
    # Role & Hierarchy
    role_level = Column(Integer, nullable=False)  # L0-L7
    tier = Column(Integer, nullable=False)  # 0, 1, or 2
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Status
    status = Column(SQLEnum(UserStatus), default=UserStatus.active, nullable=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    created_projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}', role_level={self.role_level})>"
