from pydantic import BaseModel,ConfigDict
from typing import Optional
from database.models.user import Gender

class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[Gender] = None
    is_verified: bool = False
    currency: str = "INR"
    location: Optional[str] = None
    