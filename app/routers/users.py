from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user

@router.patch("/me")
def update_me(
    data: schemas.UserUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "company_id": user.company_id,
    }