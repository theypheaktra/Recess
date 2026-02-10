"""
Purchase Order schemas - Pydantic models for order management
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.models.purchase_order import OrderStatus


class PurchaseOrderBase(BaseModel):
    project_id: int
    vendor_id: int
    process_type: str = Field(..., pattern="^(layout|genga|douga|color|bg|composite)$")
    quantity: int = Field(..., gt=0)
    unit: str = Field(default="cut", pattern="^(cut|sheet)$")
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    difficulty_rate: Decimal = Field(default=Decimal("1.0"), ge=Decimal("1.0"), le=Decimal("2.0"))
    urgency_rate: Decimal = Field(default=Decimal("1.0"), ge=Decimal("1.0"), le=Decimal("1.5"))
    withholding_tax_rate: Decimal = Field(default=Decimal("0.0"), ge=Decimal("0"), le=Decimal("0.1"))
    deadline: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a new purchase order"""
    pass


class PurchaseOrderUpdate(BaseModel):
    """Schema for updating a purchase order"""
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    difficulty_rate: Optional[Decimal] = Field(None, ge=Decimal("1.0"), le=Decimal("2.0"))
    urgency_rate: Optional[Decimal] = Field(None, ge=Decimal("1.0"), le=Decimal("1.5"))
    deadline: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None


class PurchaseOrder(PurchaseOrderBase):
    """Schema for purchase order response"""
    id: int
    order_no: str
    base_amount: Decimal
    adjusted_amount: Decimal
    vat_rate: Decimal
    vat_amount: Decimal
    withholding_tax: Decimal
    net_amount: Decimal
    status: OrderStatus
    ordered_by: int
    approved_by: Optional[int]
    ordered_at: Optional[datetime]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseOrderCalculation(BaseModel):
    """Schema for order calculation preview"""
    quantity: int
    unit_price: Decimal
    base_amount: Decimal
    difficulty_rate: Decimal
    urgency_rate: Decimal
    adjusted_amount: Decimal
    vat_rate: Decimal
    vat_amount: Decimal
    withholding_tax_rate: Decimal
    withholding_tax: Decimal
    net_amount: Decimal
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 50,
                "unit_price": "15000.00",
                "base_amount": "750000.00",
                "difficulty_rate": "1.2",
                "urgency_rate": "1.0",
                "adjusted_amount": "900000.00",
                "vat_rate": "0.10",
                "vat_amount": "90000.00",
                "withholding_tax_rate": "0.033",
                "withholding_tax": "29700.00",
                "net_amount": "960300.00"
            }
        }
