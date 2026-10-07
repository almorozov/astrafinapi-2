import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import create_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=10)).decode()

def _verify(pw: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), h.encode())
    except ValueError:
        return False

@router.post("/register")
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(username=data.username).first():
        raise HTTPException(status_code=400, detail="Username is taken")
    company = db.query(models.Company).filter_by(name=data.company_name).first()
    if company is None:
        company = models.Company(name=data.company_name)
        db.add(company)
        db.flush()
    user = models.User(
        username=data.username,
        password_hash=_hash(data.password),
        full_name=data.full_name,
        role="accountant",
        company_id=company.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "company_id": user.company_id, "role": user.role}

@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=data.username).first()
    if user is None or not _verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Bad credentials")
    return {"access_token": create_token(user.id)}