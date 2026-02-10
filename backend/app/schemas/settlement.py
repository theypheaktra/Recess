"""
Settlement schemas - Pydantic models for settlement processing
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.models.settlement import SettlementStatus


class SettlementBase(BaseModel):
    order_id: int
    vendor_id: int
    project_id: int
    completed_cuts: int = Field(..., gt=0)
    completed_sheets: int = Field(default=0, ge=0)
    penalty_amount: Decimal = Field(default=Decimal("0"), ge=0)
    adjustment_amount: Decimal = Field(default=Decimal("0"))
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class SettlementCreate(SettlementBase):
    """Schema for creating a new settlement"""
    pass


class SettlementUpdate(BaseModel):
    """Schema for updating a settlement"""
    completed_cuts: Optional[int] = Field(None, gt=0)
    completed_sheets: Optional[int] = Field(None, ge=0)
    penalty_amount: Optional[Decimal] = Field(None, ge=0)
    adjustment_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[SettlementStatus] = None


class Settlement(SettlementBase):
    """Schema for settlement response"""
    id: int
    settlement_no: str
    base_amount: Decimal
    adjusted_amount: Decimal
    vat_amount: Decimal
    withholding_tax: Decimal
    net_amount: Decimal
    final_amount: Decimal
    status: SettlementStatus
    settled_by: Optional[int]
    approved_by: Optional[int]
    payment_date: Optional[date]
    payment_reference: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SettlementSummary(BaseModel):
    """Schema for settlement dashboard summary"""
    total_settlements: int
    pending_count: int
    approved_count: int
    paid_count: int
    total_pending_amount: Decimal
    total_approved_amount: Decimal
    total_paid_amount: Decimal
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_settlements": 150,
                "pending_count": 25,
                "approved_count": 10,
                "paid_count": 115,
                "total_pending_amount": "45000000.00",
                "total_approved_amount": "15000000.00",
                "total_paid_amount": "230000000.00"
            }
        }
