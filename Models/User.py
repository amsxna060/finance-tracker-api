from datetime import datetime
from pydantic import BaseModel,Field
from typing import Annotated

class User (BaseModel): 
    id : Annotated[int,Field(gt=0)]
    name : str 
    email : str 
    age : Annotated[int,Field(gt=0)]
    gender : str
    password : str | None = None
    is_verified : bool = False
    currency : str
    location : str
    date_created : str = datetime.now().isoformat()
    date_updated : str = datetime.now().isoformat()

