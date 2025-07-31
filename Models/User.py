from datetime import datetime
from pydantic import BaseModel

class User (BaseModel): 
    def __init__(self):
        id : int | None = None
        name : str | None = None
        email : str | None = None
        age : int | None = None
        gender : str | None = None
        password : str | None = None
        is_verified : bool = False
        date_created : str = datetime.now().isoformat()
        date_updated : str = datetime.now().isoformat()

