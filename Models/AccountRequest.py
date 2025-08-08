
from pydantic import BaseModel,Field
from typing import Optional,Annotated

from database.models import AccountType



class AccountRequest(BaseModel):
    account_name : Annotated[str,Field(min_length=5,max_length=25)]
    description : Optional[str]
    account_type : AccountType = AccountType.SAVINGS
    balance : Annotated[float,Field(gt=0.0)]
    currency : str = 'INR'

