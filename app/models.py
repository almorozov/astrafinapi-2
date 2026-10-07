from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    inn = Column(String(16), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="company")
    payments = relationship("Payment", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(128), default="")
    role = Column(String(32), default="accountant", nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="users")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String(8), default="RUB")
    description = Column(Text, default="")
    recipient = Column(String(128), default="")
    status = Column(String(16), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    company = relationship("Company", back_populates="payments")