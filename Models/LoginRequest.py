from pydantic import BaseModel, field_validator, ValidationInfo
from pydantic_core import ValidationError
import re

class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator('email')
    def email_validation(cls, email):
        if '@' not in email:
            raise ValueError("Wrong Email, '@' is missing")
        elif '.com' not in email:
            raise ValueError("Wrong Email, '.com' is missing.")
        else:
            return email
        
    @field_validator('password')
    def password_strength_check(cls, password):
        # For login, we don't need strict password validation
        # Just ensure it's not empty
        if not password or len(password.strip()) == 0:
            raise ValueError("Password cannot be empty")
        return password


        

    