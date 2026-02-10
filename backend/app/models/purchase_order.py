"""
Purchase Order model - Core order management (발주서)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Numeric, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Purchase order status"""
    draft = "draft"           # Being created
    pending = "pending"       # Awaiting approval
    approved = "approved"     # Approved by authority
    in_progress = "in_progress"  # Work ongoing
    completed = "completed"   # Work finished
    settled = "settled"       # Payment completed
    cancelled = "cancelled"   # Cancelled


class PurchaseOrder(Base):
    """
    Purchase Order model - Core business entity for ordering work
    
    발주서 (Baljuseo) - Official work order from prime to subcontractor
    Contains pricing, quantity, and payment terms
    """
    __tablename__ = "purchase_orders"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(20), unique=True, nullable=False, index=True)  # PO-2026-0001
    
    # References
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    
    # Work Details
    process_type = Column(String(20), nullable=False)  # layout, genga, douga, color, bg, composite
    quantity = Column(Integer, nullable=False)  # Number of cuts/sheets
    unit = Column(String(20), default="cut")  # cut or sheet
    
    # Pricing - Base
    unit_price = Column(Numeric(10, 2), nullable=False)  # Price per unit
    base_amount = Column(Numeric(12, 2), nullable=False)  # quantity × unit_price
    
    # Pricing - Adjustments
    difficulty_rate = Column(Numeric(3, 2), default=1.0)  # 1.0-2.0 multiplier
    urgency_rate = Column(Numeric(3, 2), default=1.0)    # 1.0-1.5 rush multiplier
    adjusted_amount = Column(Numeric(12, 2), nullable=False)  # base × difficulty × urgency
    
    # Pricing - Taxes
    vat_rate = Column(Numeric(5, 4), default=0.10)  # 10% VAT
    vat_amount = Column(Numeric(12, 2), nullable=False)  # adjusted × vat_rate
    
    withholding_tax_rate = Column(Numeric(5, 4), default=0.0)  # 3.3% for freelancers
    withholding_tax = Column(Numeric(12, 2), default=0)  # adjusted × withholding_rate
    
    # Pricing - Final
    net_amount = Column(Numeric(12, 2), nullable=False)  # adjusted + vat - withholding
    
    # Status & Workflow
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.draft, nullable=False)
    
    # People
    ordered_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Dates
    ordered_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(Date, nullable=True)
    
    # Additional Info
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="purchase_orders")
    vendor = relationship("Vendor", back_populates="purchase_orders")
    settlements = relationship("Settlement", back_populates="order")
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, order_no='{self.order_no}', vendor_id={self.vendor_id}, net_amount={self.net_amount})>"
    
    def calculate_amounts(self):
        """
        Calculate all monetary amounts based on business rules
        
        Formula:
        1. base_amount = quantity × unit_price
        2. adjusted_amount = base_amount × difficulty_rate × urgency_rate
        3. vat_amount = adjusted_amount × vat_rate (10%)
        4. withholding_tax = adjusted_amount × withholding_rate (3.3% for freelancers)
        5. net_amount = adjusted_amount + vat_amount - withholding_tax
        """
        # Base calculation
        self.base_amount = self.quantity * self.unit_price
        
        # Apply adjustment multipliers
        self.adjusted_amount = self.base_amount * self.difficulty_rate * self.urgency_rate
        
        # Calculate VAT (always 10%)
        self.vat_amount = self.adjusted_amount * self.vat_rate
        
        # Calculate withholding tax (3.3% for freelancers, 0% for studios)
        self.withholding_tax = self.adjusted_amount * self.withholding_tax_rate
        
        # Final net payment amount
        self.net_amount = self.adjusted_amount + self.vat_amount - self.withholding_tax
