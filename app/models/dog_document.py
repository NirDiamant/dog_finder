
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DogDocument(BaseModel):
    filename: str
    image: str
    type: str
    breed: Optional[str] = None
    isFound: bool = False