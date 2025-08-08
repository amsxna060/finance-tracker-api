"""
User-related request models (Pydantic models for API input validation)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional
from database.models.user import Gender, Role


class UserCreateRequest(BaseModel):
    """Request model for user registration"""
    name: str 
    email: str
    age: Annotated[int, Field(gt=0)]
    gender: Gender
    password: str

    @field_validator('email')
    def email_validation(cls, email):
        if '@' not in email:
            raise ValueError("Wrong Email, '@' is missing")
        elif '.com' not in email:
            raise ValueError("Wrong Email, '.com' is missing.")
        else:
            return email


class LoginRequest(BaseModel):
    """Request model for user login"""
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
        # For login, we just accept any password
        # Password strength is only checked during registration
        return password


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    name: Optional[str] = None
    age: Optional[Annotated[int, Field(gt=0)]] = None
    gender: Optional[Gender] = None
    currency: Optional[str] = None
    location: Optional[str] = None
