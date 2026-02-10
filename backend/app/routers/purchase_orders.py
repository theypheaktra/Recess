"""
Purchase Orders router - Core order management API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.models import PurchaseOrder, User, OrderStatus
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrder as PurchaseOrderSchema,
    PurchaseOrderCalculation
)
from app.routers.auth import get_current_user

router = APIRouter()


def generate_order_no(db: Session) -> str:
    """Generate unique order number: PO-YYYY-NNNN"""
    from datetime import date
    year = date.today().year
    
    # Get latest order number for this year
    latest = db.query(PurchaseOrder).filter(
        PurchaseOrder.order_no.like(f"PO-{year}-%")
    ).order_by(desc(PurchaseOrder.order_no)).first()
    
    if latest:
        last_num = int(latest.order_no.split("-")[2])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"PO-{year}-{new_num:04d}"


@router.post("/orders", response_model=PurchaseOrderSchema, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    order_data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new purchase order
    
    **Business Logic:**
    1. base_amount = quantity × unit_price
    2. adjusted_amount = base_amount × difficulty_rate × urgency_rate
    3. vat_amount = adjusted_amount × 10%
    4. withholding_tax = adjusted_amount × 3.3% (for freelancers)
    5. net_amount = adjusted_amount + vat - withholding
    """
    # Generate order number
    order_no = generate_order_no(db)
    
    # Create order instance
    order = PurchaseOrder(
        order_no=order_no,
        project_id=order_data.project_id,
        vendor_id=order_data.vendor_id,
        process_type=order_data.process_type,
        quantity=order_data.quantity,
        unit=order_data.unit,
        unit_price=order_data.unit_price,
        difficulty_rate=order_data.difficulty_rate,
        urgency_rate=order_data.urgency_rate,
        withholding_tax_rate=order_data.withholding_tax_rate,
        deadline=order_data.deadline,
        description=order_data.description,
        notes=order_data.notes,
        ordered_by=current_user.id,
        ordered_at=datetime.utcnow(),
        status=OrderStatus.draft
    )
    
    # Calculate amounts
    order.calculate_amounts()
    
    # Save to database
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/orders", response_model=List[PurchaseOrderSchema])
async def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[OrderStatus] = None,
    project_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List purchase orders with optional filters
    
    **Filters:**
    - status: Filter by order status
    - project_id: Filter by project
    - vendor_id: Filter by vendor
    """
    query = db.query(PurchaseOrder)
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if project_id:
        query = query.filter(PurchaseOrder.project_id == project_id)
    if vendor_id:
        query = query.filter(PurchaseOrder.vendor_id == vendor_id)
    
    orders = query.order_by(desc(PurchaseOrder.created_at)).offset(skip).limit(limit).all()
    return orders


@router.get("/orders/{order_id}", response_model=PurchaseOrderSchema)
async def get_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get purchase order by ID"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order {order_id} not found"
        )
    
    return order


@router.put("/orders/{order_id}", response_model=PurchaseOrderSchema)
async def update_purchase_order(
    order_id: int,
    order_update: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update purchase order"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order {order_id} not found"
        )
    
    # Only allow updates if order is in draft or pending status
    if order.status not in [OrderStatus.draft, OrderStatus.pending]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update order in current status"
        )
    
    # Update fields
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    # Recalculate if pricing fields changed
    if any(k in update_data for k in ['quantity', 'unit_price', 'difficulty_rate', 'urgency_rate']):
        order.calculate_amounts()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.post("/orders/{order_id}/approve", response_model=PurchaseOrderSchema)
async def approve_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve purchase order
    
    Requires role_level <= 5 (L5: PM, L4: Desk, L3: PD, L2: EP, L1: CEO)
    """
    if current_user.role_level > 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to approve orders"
        )
    
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order {order_id} not found"
        )
    
    if order.status != OrderStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be in pending status to approve"
        )
    
    order.status = OrderStatus.approved
    order.approved_by = current_user.id
    order.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.post("/orders/{order_id}/cancel", response_model=PurchaseOrderSchema)
async def cancel_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel purchase order"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order {order_id} not found"
        )
    
    if order.status in [OrderStatus.completed, OrderStatus.settled, OrderStatus.cancelled]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order in current status"
        )
    
    order.status = OrderStatus.cancelled
    
    db.commit()
    db.refresh(order)
    
    return order


@router.post("/orders/calculate", response_model=PurchaseOrderCalculation)
async def calculate_order_amount(
    quantity: int = Query(..., gt=0),
    unit_price: Decimal = Query(..., gt=0),
    difficulty_rate: Decimal = Query(Decimal("1.0"), ge=Decimal("1.0"), le=Decimal("2.0")),
    urgency_rate: Decimal = Query(Decimal("1.0"), ge=Decimal("1.0"), le=Decimal("1.5")),
    withholding_tax_rate: Decimal = Query(Decimal("0.033"), ge=0, le=Decimal("0.1")),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate order amounts (preview calculation)
    
    Useful for frontend to show calculated amounts before order creation
    """
    vat_rate = Decimal("0.10")  # Fixed 10% VAT
    
    base_amount = quantity * unit_price
    adjusted_amount = base_amount * difficulty_rate * urgency_rate
    vat_amount = adjusted_amount * vat_rate
    withholding_tax = adjusted_amount * withholding_tax_rate
    net_amount = adjusted_amount + vat_amount - withholding_tax
    
    return {
        "quantity": quantity,
        "unit_price": unit_price,
        "base_amount": base_amount,
        "difficulty_rate": difficulty_rate,
        "urgency_rate": urgency_rate,
        "adjusted_amount": adjusted_amount,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "withholding_tax_rate": withholding_tax_rate,
        "withholding_tax": withholding_tax,
        "net_amount": net_amount
    }
