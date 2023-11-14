from enum import Enum

class DogSex(str, Enum):
    MALE: str = "male"
    FEMALE: str = "female"
    
class DogType(str, Enum):
    FOUND: str = "found"
    LOST: str = "lost"
    
class DogAgeGroup(str, Enum):
    PUPPY: str = "puppy"
    ADULT: str = "adult"
    SENIOR: str = "senior"