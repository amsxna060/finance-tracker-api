from pydantic import BaseModel,Field,field_validator,ValidationError
from typing import Annotated
from database.models.user import Gender

class UserCreate(BaseModel):
    name : str 
    email : str
    age : Annotated[int,Field(gt=0)]
    gender : Gender
    password : str

    @field_validator('email')
    def email_validation(cls,email):
        if '@' not in email:
            raise ValidationError("Wrong Email, '@' is missing")
        elif '.com' not in email:
            raise ValidationError("Wrong Email, '.com' is missing.")
        else:
            return email
    
