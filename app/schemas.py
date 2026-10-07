from typing import Optional
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = ""
    company_name: str = Field(min_length=1, max_length=128)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    company_id: int
    class Config:
        from_attributes = True

class EmployeeCreate(BaseModel):
    username: str
    password: str
    full_name: str = ""
    role: str = "accountant"

class PaymentCreate(BaseModel):
    amount: int
    currency: str = "RUB"
    description: str = ""
    recipient: str = ""