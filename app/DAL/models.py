import inspect
import json
import os
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Boolean, Integer, Date
from sqlalchemy.orm import relationship
from .database import Base

# DB field enums
DOG_TYPE_ENUMS = Enum('lost', 'found', name='dog_type')
DOG_SEX_ENUMS = Enum('male', 'female', name='dog_sex')
DOG_AGE_GROUP_ENUMS = Enum('puppy', 'adult', 'senior', name='dog_age_group')

class Dog(Base):
    __tablename__ = 'dogs'

    # Dog data
    ## Entry data
    id = Column(Integer, primary_key=True, autoincrement=True)
    reporterId = Column(String)
    type = Column(DOG_TYPE_ENUMS, nullable=False) # vectordb will use this field DO NOT REMOVE
    isResolved = Column(Boolean, default=False)
    isVerified = Column(Boolean, default=False)

    ## contact details
    contactName = Column(String)
    contactPhone = Column(String)
    contactEmail = Column(String)
    contactAddress = Column(String)

    ## dog attributes
    name = Column(String)
    breed = Column(String)
    color = Column(String)
    size = Column(String)
    sex = Column(DOG_SEX_ENUMS)
    ageGroup = Column(DOG_AGE_GROUP_ENUMS)
    chipNumber = Column(String(length=15))
    location = Column(String)
    extraDetails = Column(String)

    ## change times
    dogFoundOn = Column(Date, default=datetime.utcnow)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, onupdate=datetime.utcnow)

    # relationship
    images = relationship('DogImage', back_populates='dog', cascade='all, delete-orphan')
    possibleMatches = relationship('PossibleDogMatch', foreign_keys='PossibleDogMatch.dogId', back_populates='dog', cascade='all, delete-orphan')
    possibleMatchesOf = relationship('PossibleDogMatch', foreign_keys='PossibleDogMatch.possibleMatchId', back_populates='possibleMatch', cascade='all, delete-orphan')

class DogImage(Base):
    __tablename__ = 'dog_images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dogId = Column(Integer, ForeignKey('dogs.id'))
    base64Image = Column(String)
    imageContentType = Column(String)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, onupdate=datetime.utcnow)

    dog = relationship('Dog', back_populates='images')


class PossibleDogMatch(Base):
    __tablename__ = 'possible_dog_matches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dogId = Column(Integer, ForeignKey('dogs.id'))
    possibleMatchId = Column(Integer, ForeignKey('dogs.id'))
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, onupdate=datetime.utcnow)

    dog = relationship('Dog', foreign_keys=[dogId], back_populates='possibleMatches')
    possibleMatch = relationship('Dog', foreign_keys=[possibleMatchId], back_populates='possibleMatchesOf')