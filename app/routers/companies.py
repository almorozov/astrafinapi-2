import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])

def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=10)).decode()

@router.get("")
def list_companies(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    companies = db.query(models.Company).filter_by(id=user.company_id).all()
    return [{"id": c.id, "name": c.name} for c in companies]

@router.get("/{company_id}")
def get_company(
    company_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = db.get(models.Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"id": company.id, "name": company.name, "inn": company.inn}

@router.get("/{company_id}/payments")
def company_payments(
    company_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role not in ("director", "auditor"):
        raise HTTPException(status_code=403, detail="Director or auditor role required")
    payments = db.query(models.Payment).filter_by(company_id=company_id).all()
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

@router.post("/{company_id}/employees")
def add_employee(
    company_id: int,
    data: schemas.EmployeeCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "director" or user.company_id != company_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if data.role not in ("director", "accountant", "auditor"):
        raise HTTPException(status_code=400, detail="Unknown role")
    if db.query(models.User).filter_by(username=data.username).first():
        raise HTTPException(status_code=400, detail="Username is taken")
    emp = models.User(
        username=data.username,
        password_hash=_hash(data.password),
        full_name=data.full_name,
        role=data.role,
        company_id=company_id,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return {"id": emp.id, "username": emp.username, "role": emp.role}