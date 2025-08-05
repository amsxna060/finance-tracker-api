from pydantic import BaseModel, Field, field_validator
from typing import Annotated

class UserCreate(BaseModel):
    name: str 
    email: str
    age: Annotated[int, Field(gt=0)]
    gender: str
    password: str

    @field_validator('email')
    def email_validation(cls, email):
        if '@' not in email:
            raise ValueError("Wrong Email, '@' is missing")
        elif '.com' not in email:
            raise ValueError("Wrong Email, '.com' is missing.")
        else:
            return email
    
