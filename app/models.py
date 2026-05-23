from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
from datetime import datetime, timezone

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, nullable=False)
    balance = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
