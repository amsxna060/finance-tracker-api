"""
Transaction-related request models (Pydantic models for API input validation)
"""
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime
from database.models.transaction import TransactionType


class TransactionCreateRequest(BaseModel):
    """Request model for creating a new transaction"""
    transaction_name: str
    amount: Annotated[float, Field(gt=0.0)]
    transaction_type: TransactionType
    account_id: int
    category_id: int
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    to_account_id: Optional[int] = None  # For transfers


class TransactionUpdateRequest(BaseModel):
    """Request model for updating an existing transaction (partial updates)"""
    transaction_name: Optional[str] = None
    amount: Optional[Annotated[float, Field(gt=0.0)]] = None
    transaction_type: Optional[TransactionType] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    to_account_id: Optional[int] = None
