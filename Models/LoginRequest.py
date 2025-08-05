from pydantic import BaseModel, field_validator
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