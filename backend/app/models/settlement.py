"""
Settlement model - Payment processing (정산)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Numeric, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SettlementStatus(str, enum.Enum):
    """Settlement status"""
    pending = "pending"           # Awaiting processing
    approved = "approved"         # Approved for payment
    paid = "paid"                # Payment completed
    disputed = "disputed"        # Under dispute
    cancelled = "cancelled"      # Cancelled


class Settlement(Base):
    """
    Settlement model - Payment processing and tracking
    
    정산 (Jeongsan) - Final settlement calculation and payment
    Created after QC3 approval, tracks actual payment
    """
    __tablename__ = "settlements"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    settlement_no = Column(String(20), unique=True, nullable=False, index=True)  # ST-2026-0001
    
    # References
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Work Completed
    completed_cuts = Column(Integer, nullable=False)  # Actual cuts completed
    completed_sheets = Column(Integer, default=0)  # For douga/color work
    
    # Amounts (copied from purchase order, may be adjusted)
    base_amount = Column(Numeric(12, 2), nullable=False)
    adjusted_amount = Column(Numeric(12, 2), nullable=False)
    vat_amount = Column(Numeric(12, 2), nullable=False)
    withholding_tax = Column(Numeric(12, 2), default=0)
    net_amount = Column(Numeric(12, 2), nullable=False)
    
    # Deductions (if any)
    penalty_amount = Column(Numeric(12, 2), default=0)  # For late delivery
    adjustment_amount = Column(Numeric(12, 2), default=0)  # Other adjustments
    final_amount = Column(Numeric(12, 2), nullable=False)  # net_amount - penalties + adjustments
    
    # Status & Workflow
    status = Column(SQLEnum(SettlementStatus), default=SettlementStatus.pending, nullable=False)
    
    # People
    settled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Payment Tracking
    payment_method = Column(String(50), nullable=True)  # bank_transfer, cash, etc.
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)  # Transaction ID
    
    # Additional Info
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("PurchaseOrder", back_populates="settlements")
    vendor = relationship("Vendor", back_populates="settlements")
    project = relationship("Project", back_populates="settlements")
    
    def __repr__(self):
        return f"<Settlement(id={self.id}, settlement_no='{self.settlement_no}', vendor_id={self.vendor_id}, final_amount={self.final_amount})>"
    
    def calculate_final_amount(self):
        """
        Calculate final payment amount after deductions and adjustments
        
        Formula:
        final_amount = net_amount - penalty_amount + adjustment_amount
        """
        self.final_amount = self.net_amount - self.penalty_amount + self.adjustment_amount
