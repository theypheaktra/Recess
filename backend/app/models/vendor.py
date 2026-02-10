"""
Vendor model - Subcontractors and freelancers
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class VendorType(str, enum.Enum):
    """Vendor type"""
    studio = "studio"       # Subcontractor studio
    freelancer = "freelancer"  # Individual freelancer


class TaxType(str, enum.Enum):
    """Tax classification"""
    corporate = "corporate"     # Corporate tax
    individual = "individual"   # Individual withholding tax


class Vendor(Base):
    """
    Vendor model - Subcontractors and freelancers who receive orders
    """
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String(200), nullable=False)
    name_jp = Column(String(200), nullable=True)
    type = Column(SQLEnum(VendorType), nullable=False)
    tier = Column(Integer, nullable=False)  # Usually tier 2
    
    # Organization link (if studio)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Contact
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Business Info
    business_no = Column(String(50), nullable=True)
    tax_type = Column(SQLEnum(TaxType), nullable=False)
    
    # Banking
    bank_name = Column(String(100), nullable=True)
    bank_account = Column(String(100), nullable=True)
    account_holder = Column(String(100), nullable=True)
    
    # Pricing
    default_rate = Column(Numeric(10, 2), nullable=True)  # Default unit price
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="vendors")
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")
    settlements = relationship("Settlement", back_populates="vendor")
    
    def __repr__(self):
        return f"<Vendor(id={self.id}, name='{self.name}', type={self.type})>"
