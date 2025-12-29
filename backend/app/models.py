from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    description = Column(String)
    amount = Column(Float)
    category = Column(String)
    source = Column(String, default="csv")

class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, unique=True)
    item_id = Column(String, unique=True)

