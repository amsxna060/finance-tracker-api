from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey,CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
from sqlalchemy.types import Enum as SQLAlchemyEnum
import enum

class AccountType(enum.Enum):
    """
    Represents the different types of financial accounts in a tracking app.
    """
    # Asset Accounts (what you own)
    CHECKING = 'CHECKING'          # For daily transactions
    SAVINGS = 'SAVINGS'            # For saving money
    CASH = 'CASH'                  # Physical cash
    INVESTMENT = 'INVESTMENT'      # Brokerage accounts, 401(k), IRA
    PROPERTY = 'PROPERTY'          # Real estate, vehicles, etc.

    # Liability Accounts (what you owe)
    CREDIT_CARD = 'CREDIT_CARD'    # Revolving credit
    LOAN = 'LOAN'                  # Mortgages, student loans, auto loans
    

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String, nullable=False)  # Added this - every account needs a name!
    description = Column(String, nullable=True)
    account_type = Column(SQLAlchemyEnum(AccountType), default=AccountType.SAVINGS)
    balance = Column(Float,CheckConstraint('balance >= 0'), default=0.0)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"), nullable=False)  # 🔥 FOREIGN KEY!
    currency = Column(String, default='INR')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accounts")  # 🔥 RELATIONSHIP!
    transactions = relationship("Transaction", back_populates="account")