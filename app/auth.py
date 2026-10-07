import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import get_db
from . import models

SECRET = os.getenv("JWT_SECRET", "local-dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_TTL_HOURS = 12

bearer = HTTPBearer(auto_error=False)

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> models.User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = jwt.decode(creds.credentials, SECRET, algorithms=[ALGORITHM])
        uid = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(models.User, uid)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user