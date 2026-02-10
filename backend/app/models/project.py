"""
Project, Episode, and Cut models - Core production tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Numeric, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ProjectType(str, enum.Enum):
    """Project type"""
    TVA = "TVA"      # TV Animation
    Movie = "Movie"
    OVA = "OVA"      # Original Video Animation
    Web = "Web"


class ProjectStatus(str, enum.Enum):
    """Project status"""
    planning = "planning"
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class ProcessType(str, enum.Enum):
    """Production process type"""
    layout = "layout"
    genga = "genga"      # Key animation
    douga = "douga"      # In-between animation
    color = "color"      # Coloring
    bg = "bg"           # Background
    composite = "composite"  # Compositing/shooting


class CutStatus(str, enum.Enum):
    """Cut production status"""
    assigned = "assigned"
    in_progress = "in_progress"
    qc1_pending = "qc1_pending"
    qc1_approved = "qc1_approved"
    qc1_rejected = "qc1_rejected"
    qc2_pending = "qc2_pending"
    qc2_approved = "qc2_approved"
    qc2_rejected = "qc2_rejected"
    qc3_pending = "qc3_pending"
    qc3_approved = "qc3_approved"
    qc3_rejected = "qc3_rejected"
    completed = "completed"
    rework = "rework"


class Project(Base):
    """Project model - Animation production project"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_no = Column(String(20), unique=True, nullable=False, index=True)  # PRJ-2026-001
    
    name = Column(String(200), nullable=False)
    name_jp = Column(String(200), nullable=True)
    
    client_org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    type = Column(SQLEnum(ProjectType), nullable=False)
    
    total_episodes = Column(Integer, nullable=True)
    total_cuts = Column(Integer, default=0)
    completed_cuts = Column(Integer, default=0)
    progress = Column(Numeric(5, 2), default=0)  # Percentage 0-100
    
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.planning, nullable=False)
    budget = Column(Numeric(15, 2), nullable=True)
    deadline = Column(Date, nullable=True)
    
    description = Column(Text, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    client_org = relationship("Organization", back_populates="projects_as_client")
    creator = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    episodes = relationship("Episode", back_populates="project", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="project")
    settlements = relationship("Settlement", back_populates="project")


class Episode(Base):
    """Episode model - Individual episodes within a project"""
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    episode_no = Column(Integer, nullable=False)
    name = Column(String(200), nullable=True)
    name_jp = Column(String(200), nullable=True)
    
    total_cuts = Column(Integer, default=0)
    completed_cuts = Column(Integer, default=0)
    progress = Column(Numeric(5, 2), default=0)
    
    deadline = Column(Date, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.planning, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="episodes")
    cuts = relationship("Cut", back_populates="episode", cascade="all, delete-orphan")


class Cut(Base):
    """Cut model - Individual animation cuts (minimum work unit)"""
    __tablename__ = "cuts"
    
    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    
    cut_no = Column(String(20), nullable=False)
    scene_no = Column(String(20), nullable=True)
    
    process_type = Column(SQLEnum(ProcessType), nullable=False)
    difficulty_level = Column(Numeric(3, 2), default=1.0)  # 1.0-2.0
    
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(CutStatus), default=CutStatus.assigned, nullable=False)
    
    # QC Status
    qc1_status = Column(String(20), nullable=True)
    qc1_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    qc1_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    qc2_status = Column(String(20), nullable=True)
    qc2_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    qc2_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    qc3_status = Column(String(20), nullable=True)
    qc3_approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    qc3_approved_at = Column(DateTime(timezone=True), nullable=True)
    
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    episode = relationship("Episode", back_populates="cuts")
