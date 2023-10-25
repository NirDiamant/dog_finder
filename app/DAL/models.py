import inspect
import json
import os
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Boolean, Integer
from sqlalchemy.orm import relationship
from .database import Base

# DB field enums
DOG_TYPE_ENUMS = Enum('lost', 'found', name='dog_type')
DOG_SEX_ENUMS = Enum('male', 'female', name='dog_sex')

class Dog(Base):
    __tablename__ = 'dogs'

    # Dog data
    ## Entry data
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(DOG_TYPE_ENUMS, nullable=False) # vectordb will use this field DO NOT REMOVE
    isMatched = Column(Boolean, default=False)
    isVerified = Column(Boolean, default=False)

    ## contact details
    contactName = Column(String)
    contactPhone = Column(String)
    contactEmail = Column(String)
    contactAddress = Column(String)

    ## dog attributes
    name = Column(String)
    chipNumber = Column(String(length=15))
    breed = Column(String)
    color = Column(String)
    size = Column(String)
    sex = Column(DOG_SEX_ENUMS)
    location = Column(String)
    extraDetails = Column(String)

    ## change times
    dogFoundOn = Column(DateTime, default=datetime.utcnow)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, onupdate=datetime.utcnow)

    # relationship
    images = relationship('DogImage', back_populates='dog')

class DogImage(Base):
    __tablename__ = 'dog_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dogId = Column(Integer, ForeignKey('dogs.id'))
    base64Image = Column(String)
    imageContentType = Column(String)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, onupdate=datetime.utcnow)

    dog = relationship('Dog', back_populates='images')