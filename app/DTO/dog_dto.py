from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

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
    images: List[DogImageDTO]
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

    class Config:
        use_enum_values = True

    
    def to_vectordb_json(self):
        vectordb_json = {
            "type": self.type,
            "isMatched": self.isMatched,
            "isVerified": self.isVerified,
            "name": self.name,
            "chipNumber": self.chipNumber,
            "breed": self.breed,
            "color": self.color,
            "size": self.size,
            "sex": self.sex,
            "location": self.location
        }
        
        return vectordb_json
