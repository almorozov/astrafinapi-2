from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])

@router.get("/companies")
def debug_companies(db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    return [{"id": c.id, "name": c.name, "inn": c.inn} for c in companies]

@router.get("/stats")
def debug_stats(db: Session = Depends(get_db)):
    return {
        "companies": db.query(models.Company).count(),
        "users": db.query(models.User).count(),
        "payments": db.query(models.Payment).count(),
    }