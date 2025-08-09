"""
Transaction-related request models (Pydantic models for API input validation)
"""
from pydantic import BaseModel, Field,field_validator
from typing import Optional, Annotated
from datetime import datetime
from database.models.transaction import TransactionType


class TransactionCreateRequest(BaseModel):
    """Request model for creating a new transaction"""
    transaction_name: str
    amount: Annotated[float, Field(gt=0.0)]
    transaction_type: TransactionType
    account_id: int # this will use as both from or to depend on transaction type
    category_id: int
    description: Optional[str] = None
    to_account_id: Optional[int] = None  # For transfers
    date: Optional[datetime] = None  # Use current date if not provided

    @field_validator('to_account_id')
    def clean_to_account_id(cls, v):
        if v == 0 or v == "" or v is None:
            return None
        return v
    
    @field_validator('description') 
    def clean_description(cls, v):
        if v in ["", "string", None]:
            return None
        return v
    @field_validator('date')
    def validate_date_not_future(cls, v):
        if v and v > datetime.now():
            raise ValueError('Transaction date cannot be in future')
        return v
    
    # Add category ownership validation
    @field_validator('category_id')
    def validate_category_ownership(cls, v):
        if v <= 0:
            raise ValueError("Category ID must be a positive integer")
        return v
    # Add enhanced account validation
    @field_validator('account_id')
    def validate_account_ownership(cls, v):
        if v <= 0:
            raise ValueError("Account ID must be a positive integer")
        return v
   


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
