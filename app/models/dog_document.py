
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DogDocument(BaseModel):
    filename: str
    image: str
    type: str
    breed: Optional[str] = None
    isFound: bool = False
    isVerified: bool = False
    # Contact details like name, phone, email, address
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    contactAddress: Optional[str] = None