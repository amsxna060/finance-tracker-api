"""
Account-related request models (Pydantic models for API input validation)
"""
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from database.models import AccountType


class AccountCreateRequest(BaseModel):
    """Request model for creating a new account"""
    account_name: Annotated[str, Field(min_length=5, max_length=25)]
    description: Optional[str] = None
    account_type: AccountType = AccountType.SAVINGS
    balance: Annotated[float, Field(gt=0.0)]
    currency: str = 'INR'


class AccountUpdateRequest(BaseModel):
    """Request model for updating an existing account (partial updates)"""
    account_name: Optional[str] = None
    description: Optional[str] = None
    balance: Optional[float] = None
    account_type: Optional[AccountType] = None
    currency: Optional[str] = None
