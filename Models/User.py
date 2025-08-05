from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, Optional

class User(BaseModel): 
    id: Annotated[int, Field(gt=0)]
    name: str 
    email: str 
    age: Annotated[int, Field(gt=0)]
    gender: str
    password: Optional[str] = None  # Don't return in responses
    is_verified: bool = False
    currency: str = "INR"
    location: str = "India"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enables SQLAlchemy model conversion

class UserResponse(BaseModel):
    """User model for API responses (without password)"""
    id: int
    name: str 
    email: str 
    age: int
    gender: str
    is_verified: bool
    currency: str
    location: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
