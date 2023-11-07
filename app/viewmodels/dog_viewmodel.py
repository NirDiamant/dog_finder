from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_serializer, validator

RETURN_PROPERTIES = [
    "type",
    "breed",
    "size",
    "color",
    "sex",
    "extraDetails",
    "location",
    "imageBase64",
    "isMatched",
    "dogId",
    "contactName",
    "contactPhone",
    "contactEmail",
    "contactAddress",
    "isVerified",
    "imageContentType",
    "chipNumber",
    "dogFoundOn"
]

class DogType(str, Enum):
    FOUND: str = "found"
    LOST: str = "lost"

class DogSex(str, Enum):
    MALE: str = "male"
    FEMALE: str = "female"

# class QueryRequest(BaseModel):
#     type: DogType
#     imageBase64: str
#     breed: Optional[str] = None
#     top: int = 10
#     return_properties: Optional[List[str]] = RETURN_PROPERTIES
#     isVerified: Optional[bool] = True

class DogMatchedRequest(BaseModel):
    dogId: int

class DogSearchRequest(BaseModel):
    top: Optional[int] = 10
    type: Optional[DogType] = None
    base64Image: str
    isMatched: Optional[bool] = False
    isVerified: Optional[bool] = True

    name: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    sex: Optional[DogSex] = None
    chipNumber: Optional[str] = None
    location: Optional[str] = None

    return_properties: Optional[List[str]] = RETURN_PROPERTIES

class DogAddRequest(BaseModel):
    base64Images: List[str]
    type: DogType
    isMatched: bool = False
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
    
    class Config:
        use_enum_values = True
        
    @validator("*", pre=True)
    def empty_strings_to_none(cls, value):
        if isinstance(value, str) and not value:
            return None
        return value
    

class DogImageResponse(BaseModel):
    id: int
    base64Image: str
    imageContentType: Optional[str] = "webp"

class DogResponse(BaseModel):
    id: int
    reporterId: str
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

class DogFullDetailsResponse(BaseModel):
    id: int
    images: List[DogImageResponse]
    type: DogType
    isMatched: bool = False
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

