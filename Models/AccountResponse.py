from pydantic import BaseModel,Field,ConfigDict
from typing import Optional,Annotated
from datetime import datetime

from database.models import AccountType

class AccountResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id : int
    account_name : Annotated[str,Field(min_length=5,max_length=25)]
    description : Optional[str]
    account_type : AccountType = AccountType.SAVINGS
    balance : Annotated[float,Field(gt=0.0)]
    currency : str = 'INR'
    created_at : datetime
    updated_at : datetime