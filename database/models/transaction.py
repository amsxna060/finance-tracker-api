from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
from sqlalchemy.types import Enum 
import enum

class TransactionType(enum.Enum):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    TRANSFER = 'TRANSFER'

class Transaction(Base):
    __tablename__ = "transactions"  # Note: you had "trasactions" (typo) in SQL

    id = Column(Integer, primary_key=True, index=True)
    transaction_name = Column(String, nullable=False)  # "Grocery shopping", "Salary"
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    to_account = Column(Integer, nullable=True)    # For transfers
    description = Column(String, nullable=True)   # Extra details
    
    # Add this line:
    date = Column(DateTime, default=func.now(), nullable=False)  # Transaction date
    
    # Foreign Keys (Many-to-One relationships)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False) # from or to both
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships (Many-to-One)
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")