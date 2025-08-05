from pydantic import BaseModel, field_validator, ValidationError
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
        # This regex uses lookaheads to check for all conditions at once.
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[#?!@$%^&*-]).{8,}$"

        # re.match checks for a match only at the beginning of the string.
        if re.match(pattern, password):
            return password
        else:
            raise ValueError("""
    Checks if a password is strong using a single regular expression.
    A strong password must:
    - Be at least 8 characters long
    - Contain at least one uppercase letter
    - Contain at least one lowercase letter
    - Contain at least one number
    - Contain at least one special character (@$!%*?&#)
    """)