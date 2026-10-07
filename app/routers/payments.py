from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

@router.post("")
def create_payment(
    data: schemas.PaymentCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = models.Payment(
        company_id=user.company_id,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        recipient=data.recipient,
        status="pending",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return {"id": payment.id, "status": payment.status}

@router.get("")
def list_payments(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payments = db.query(models.Payment).filter_by(company_id=user.company_id).all()
    return [
        {
            "id": p.id,
            "amount": p.amount,
            "currency": p.currency,
            "status": p.status,
            "recipient": p.recipient,
        }
        for p in payments
    ]

@router.get("/{payment_id}")
def get_payment(
    payment_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = db.get(models.Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "id": payment.id,
        "company_id": payment.company_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "description": payment.description,
        "recipient": payment.recipient,
        "status": payment.status,
    }