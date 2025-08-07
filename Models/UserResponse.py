from pydantic import BaseModel,ConfigDict
from typing import Optional
from database.models.user import Gender, Role

class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[Gender] = None
    role: Role = Role.USER  # Add role field
    is_verified: bool = False
    currency: str = "INR"
    location: Optional[str] = None
    