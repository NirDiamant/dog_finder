from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_serializer
from datetime import date

class DogType(str, Enum):
    FOUND: str = "found"
    LOST: str = "lost"

class DogSex(str, Enum):
    MALE: str = "male"
    FEMALE: str = "female"

class DogImageDTO(BaseModel):
    id: Optional[int] = None
    base64Image: str
    imageContentType: Optional[str] = "webp"

class DogDTO(BaseModel):
    id: Optional[int] = None
    reporterId: str 
    images: List[DogImageDTO]
    type: DogType
    isResolved: bool = False
    isVerified: bool = False

    ## Contact details
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    contactAddress: Optional[str] = None
    
    ## dog attributes
    name: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    sex: Optional[DogSex] = None
    chipNumber: Optional[str] = None
    location: Optional[str] = None
    extraDetails: Optional[str] = None

    dogFoundOn: Optional[date] = None

    # add field_serializer to convert dogFoundOn to string
    @field_serializer("dogFoundOn")
    def dogFoundOn_serializer(self, v: date, _info):
        return v.isoformat() if v else None

    class Config:
        use_enum_values = True
    
    def to_vectordb_json(self):
        vectordb_json = {
            "type": self.type,
            "isResolved": self.isResolved,
            "isVerified": self.isVerified,
            "name": self.name,
            "chipNumber": self.chipNumber,
            "breed": self.breed,
            "color": self.color,
            "size": self.size,
            "sex": self.sex,
            "location": self.location,
            "dogFoundOn": self.dogFoundOn.isoformat() if self.dogFoundOn else None,
        }
        
        return vectordb_json

class PossibleDogMatchDTO(BaseModel):
    dogId: int
    possibleMatchId: int

    dog: Optional[DogDTO] = None
    possibleMatch: Optional[DogDTO] = None