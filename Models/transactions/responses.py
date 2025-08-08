"""
Transaction-related response models (Pydantic models for API output)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from database.models.transaction import TransactionType


class TransactionResponse(BaseModel):
    """Response model for transaction data"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_name: str
    amount: Annotated[float, Field(gt=0.0)]
    transaction_type: TransactionType
    account_id: int
    category_id: int
    user_id: int
    description: Optional[str] = None
    transaction_date: datetime
    to_account_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class TransactionSummaryResponse(BaseModel):
    """Response model for transaction summaries and analytics"""
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int
    period_start: datetime
    period_end: datetime
