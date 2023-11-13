from enum import Enum

class DogSex(str, Enum):
    MALE: str = "male"
    FEMALE: str = "female"
    
class DogType(str, Enum):
    FOUND: str = "found"
    LOST: str = "lost"
    
class DogAgeGroup(str, Enum):
    PUPPY = "puppy"
    ADULT = "adult"
    SENIOR = "senior"