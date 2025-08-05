from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Optional

class User(BaseModel): 
    """
    Pydantic User model for API serialization/deserialization.
    This model aligns with the SQLAlchemy User model fields.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: Annotated[int, Field(gt=0)]
    name: str 
    email: str 
    age: Annotated[int, Field(gt=0)]
    gender: str
    password: Optional[str] = None
    is_verified: bool = False
    currency: str
    location: str
    created_at: datetime
    updated_at: datetime

