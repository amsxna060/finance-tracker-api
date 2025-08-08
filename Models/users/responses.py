"""
User-related response models (Pydantic models for API output)
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from database.models.user import Gender, Role


class UserResponse(BaseModel):
    """Response model for user data"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[Gender] = None
    role: Role = Role.USER
    is_verified: bool = False
    currency: str = "INR"
    location: Optional[str] = None


class LoginResponse(BaseModel):
    """Response model for successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
