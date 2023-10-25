from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_serializer

class DogType(str, Enum):
    FOUND: str = "found"
    LOST: str = "lost"

class DogSex(str, Enum):
    MALE: str = "male"
    FEMALE: str = "female"

class DogRequest(BaseModel):
    base64Images: List[str]
    type: DogType
    isMatched: bool = False
    isVerified: bool = False
    # Contact details like name, phone, email, address
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    contactAddress: Optional[str] = None
    # I'm putting all of these as optional for now
    name: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    sex: Optional[DogSex] = None
    extraDetails: Optional[str] = None
    chipNumber: Optional[str] = None
    location: Optional[str] = None

    dogFoundOn: Optional[date] = None
    
    class Config:
        use_enum_values = True

class DogImageResponse(BaseModel):
    id: int
    base64Image: str
    imageContentType: Optional[str] = "webp"

class DogResponse(BaseModel):
    id: int
    images: List[DogImageResponse]
    type: DogType
    isMatched: bool = False
    isVerified: bool = False
    # I'm putting all of these as optional for now
    name: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    sex: Optional[DogSex] = None
    extraDetails: Optional[str] = None
    chipNumber: Optional[str] = None
    location: Optional[str] = None
    
    dogFoundOn: Optional[date] = None

    # add field_serializer to convert dogFoundOn to string
    @field_serializer("dogFoundOn")
    def dogFoundOn_serializer(self, v: date, _info):
        return v.isoformat() if v else None
    


    class Config:
        use_enum_values = True

