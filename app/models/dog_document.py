
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel
# import json

# class DogTypeEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Enum):
#             return obj.value
#         return json.JSONEncoder.default(self, obj)
    
class DogType(str, Enum):
    FOUND: str = "found"
    LOST: str = "lost"

    
class DogDocument(BaseModel):
    filename: str
    imageBase64: str
    type: DogType
    isMatched: bool = False
    isVerified: bool = False
    # Contact details like name, phone, email, address
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    contactAddress: Optional[str] = None
    imageContentType: Optional[str] = None
    # I'm putting all of these as optional for now
    breed: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    extraDetails: Optional[str] = None

    class Config:
        use_enum_values = True