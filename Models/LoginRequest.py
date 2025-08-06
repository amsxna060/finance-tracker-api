from pydantic import BaseModel,field_validator,ValidationError
import re

class LoginRequest(BaseModel):
    email:str
    password:str

    @field_validator('email')
    def email_validation(cls,email):
        if '@' not in email:
            raise ValueError("Wrong Email, '@' is missing")
        elif '.com' not in email:
            raise ValueError("Wrong Email, '.com' is missing.")
        else:
            return email
        
    @field_validator('password')
    def password_strength_check(cls,password):
        # For login, we just accept any password
        # Password strength is only checked during registration
        return password


        

    