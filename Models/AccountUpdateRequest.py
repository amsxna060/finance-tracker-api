from pydantic import BaseModel
from typing import Optional

class AccountUpdateRequest(BaseModel):
    account_name: Optional[str] = None
    description: Optional[str] = None
    balance: Optional[float] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None