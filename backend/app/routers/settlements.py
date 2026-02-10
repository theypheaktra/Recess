"""
Settlements router - Payment processing API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.models import Settlement, PurchaseOrder, User, SettlementStatus, OrderStatus
from app.schemas.settlement import (
    SettlementCreate,
    SettlementUpdate,
    Settlement as SettlementSchema,
    SettlementSummary
)
from app.routers.auth import get_current_user

router = APIRouter()


def generate_settlement_no(db: Session) -> str:
    """Generate unique settlement number: ST-YYYY-NNNN"""
    from datetime import date
    year = date.today().year
    
    # Get latest settlement number for this year
    latest = db.query(Settlement).filter(
        Settlement.settlement_no.like(f"ST-{year}-%")
    ).order_by(desc(Settlement.settlement_no)).first()
    
    if latest:
        last_num = int(latest.settlement_no.split("-")[2])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"ST-{year}-{new_num:04d}"


@router.post("/settlements", response_model=SettlementSchema, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    settlement_data: SettlementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new settlement based on a purchase order
    
    **Requirements:**
    - Purchase order must exist and be approved
    - Copies monetary amounts from purchase order
    - Calculates final amount with penalties/adjustments
    """
    # Get the purchase order
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == settlement_data.order_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase order {settlement_data.order_id} not found"
        )
    
    # Check if order is approved
    if order.status != OrderStatus.approved and order.status != OrderStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Purchase order must be approved before settlement"
        )
    
    # Check if settlement already exists for this order
    existing = db.query(Settlement).filter(
        Settlement.order_id == settlement_data.order_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settlement already exists for this order"
        )
    
    # Generate settlement number
    settlement_no = generate_settlement_no(db)
    
    # Create settlement
    settlement = Settlement(
        settlement_no=settlement_no,
        order_id=settlement_data.order_id,
        vendor_id=settlement_data.vendor_id,
        project_id=settlement_data.project_id,
        completed_cuts=settlement_data.completed_cuts,
        completed_sheets=settlement_data.completed_sheets,
        # Copy amounts from order
        base_amount=order.base_amount,
        adjusted_amount=order.adjusted_amount,
        vat_amount=order.vat_amount,
        withholding_tax=order.withholding_tax,
        net_amount=order.net_amount,
        # Apply penalties/adjustments
        penalty_amount=settlement_data.penalty_amount,
        adjustment_amount=settlement_data.adjustment_amount,
        payment_method=settlement_data.payment_method,
        notes=settlement_data.notes,
        settled_by=current_user.id,
        status=SettlementStatus.pending
    )
    
    # Calculate final amount
    settlement.calculate_final_amount()
    
    # Update order status
    order.status = OrderStatus.completed
    
    # Save to database
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    
    return settlement


@router.get("/settlements", response_model=List[SettlementSchema])
async def list_settlements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[SettlementStatus] = None,
    project_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List settlements with optional filters
    
    **Filters:**
    - status: Filter by settlement status
    - project_id: Filter by project
    - vendor_id: Filter by vendor
    """
    query = db.query(Settlement)
    
    if status:
        query = query.filter(Settlement.status == status)
    if project_id:
        query = query.filter(Settlement.project_id == project_id)
    if vendor_id:
        query = query.filter(Settlement.vendor_id == vendor_id)
    
    settlements = query.order_by(desc(Settlement.created_at)).offset(skip).limit(limit).all()
    return settlements


@router.get("/settlements/{settlement_id}", response_model=SettlementSchema)
async def get_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get settlement by ID"""
    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    return settlement


@router.put("/settlements/{settlement_id}", response_model=SettlementSchema)
async def update_settlement(
    settlement_id: int,
    settlement_update: SettlementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update settlement"""
    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    # Only allow updates if settlement is pending or approved
    if settlement.status not in [SettlementStatus.pending, SettlementStatus.approved]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update settlement in current status"
        )
    
    # Update fields
    update_data = settlement_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settlement, field, value)
    
    # Recalculate final amount if penalties/adjustments changed
    if any(k in update_data for k in ['penalty_amount', 'adjustment_amount']):
        settlement.calculate_final_amount()
    
    db.commit()
    db.refresh(settlement)
    
    return settlement


@router.post("/settlements/{settlement_id}/complete", response_model=SettlementSchema)
async def complete_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark settlement as completed (paid)
    
    Requires role_level <= 5 (L5: PM, L4: Desk, L3: PD, L2: EP, L1: CEO)
    """
    if current_user.role_level > 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to complete settlements"
        )
    
    settlement = db.query(Settlement).filter(Settlement.id == settlement_id).first()
    
    if not settlement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settlement {settlement_id} not found"
        )
    
    if settlement.status != SettlementStatus.approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settlement must be approved before completion"
        )
    
    settlement.status = SettlementStatus.paid
    settlement.completed_at = datetime.utcnow()
    settlement.approved_by = current_user.id
    
    # Update related purchase order status
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == settlement.order_id).first()
    if order:
        order.status = OrderStatus.settled
    
    db.commit()
    db.refresh(settlement)
    
    return settlement


@router.get("/settlements/summary", response_model=SettlementSummary)
async def get_settlements_summary(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get settlement summary statistics for dashboard
    
    Returns counts and totals by status
    """
    query = db.query(Settlement)
    
    if project_id:
        query = query.filter(Settlement.project_id == project_id)
    
    # Count by status
    total_settlements = query.count()
    pending_count = query.filter(Settlement.status == SettlementStatus.pending).count()
    approved_count = query.filter(Settlement.status == SettlementStatus.approved).count()
    paid_count = query.filter(Settlement.status == SettlementStatus.paid).count()
    
    # Sum amounts by status
    pending_sum = db.query(func.sum(Settlement.final_amount)).filter(
        Settlement.status == SettlementStatus.pending
    ).scalar() or Decimal("0")
    
    approved_sum = db.query(func.sum(Settlement.final_amount)).filter(
        Settlement.status == SettlementStatus.approved
    ).scalar() or Decimal("0")
    
    paid_sum = db.query(func.sum(Settlement.final_amount)).filter(
        Settlement.status == SettlementStatus.paid
    ).scalar() or Decimal("0")
    
    return {
        "total_settlements": total_settlements,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "paid_count": paid_count,
        "total_pending_amount": pending_sum,
        "total_approved_amount": approved_sum,
        "total_paid_amount": paid_sum
    }
