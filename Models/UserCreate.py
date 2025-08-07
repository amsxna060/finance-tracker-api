from pydantic import BaseModel,Field,field_validator,ValidationError
from typing import Annotated, Optional
from database.models.user import Gender, Role

class UserCreate(BaseModel):
    name : str 
    email : str
    age : Annotated[int,Field(gt=0)]
    gender : Gender
    password : str
    # role : Optional[Role] = Role.USER  # Add role field with default 'user'

    @field_validator('email')
    def email_validation(cls,email):
        if '@' not in email:
            raise ValueError("Wrong Email, '@' is missing")
        elif '.com' not in email:
            raise ValueError("Wrong Email, '.com' is missing.")
        else:
            return email
    
