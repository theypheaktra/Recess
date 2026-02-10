"""
Organization model - Companies and studios
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class OrgType(str, enum.Enum):
    """Organization type"""
    committee = "committee"  # Production committee
    prime = "prime"         # Prime contractor studio
    sub = "sub"            # Subcontractor studio


class Organization(Base):
    """
    Organization model representing companies and studios
    
    - Tier 0: Production committees (broadcasting, distribution, publishing)
    - Tier 1: Prime contractor studios (MAPPA, WIT Studio, LIKAI)
    - Tier 2: Subcontractor studios and freelancer groups
    """
    __tablename__ = "organizations"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String(200), nullable=False)
    name_jp = Column(String(200), nullable=True)
    type = Column(SQLEnum(OrgType), nullable=False)
    tier = Column(Integer, nullable=False)  # 0, 1, or 2
    
    # Business Info
    business_no = Column(String(50), nullable=True)  # Business registration number
    tax_id = Column(String(50), nullable=True)
    
    # Banking
    bank_name = Column(String(100), nullable=True)
    bank_account = Column(String(100), nullable=True)
    account_holder = Column(String(100), nullable=True)
    
    # Contact
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    projects_as_client = relationship("Project", back_populates="client_org", foreign_keys="Project.client_org_id")
    vendors = relationship("Vendor", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', type={self.type}, tier={self.tier})>"
