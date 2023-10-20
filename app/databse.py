import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, Column, String, ForeignKey, DateTime, Enum, Boolean, UUID
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy_utils import database_exists, create_database, drop_database

# DB variables
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_PROTOCOL = os.environ.get("DB_PROTOCOL", "sqlite")


# Set SQLite type adjustments (does not support UUID)
def get_id_creator():
    if DB_PROTOCOL == 'sqlite':
        return lambda: str(uuid.uuid4())
    else:
        return uuid.uuid4


def get_id_column_type():
    if DB_PROTOCOL == 'sqlite':
        return String
    else:
        return UUID(as_uuid=True)


ID_COLUMN_TYPE = get_id_column_type()
ID_CREATOR = get_id_creator()

# DB field enums
DOG_TYPE_ENUMS = Enum('lost', 'found', name='dog_type')
DOG_SEX_ENUMS = Enum('male', 'female', name='dog_sex')

# Create a base class for declarative models
Base = declarative_base()


class Dog(Base):
    __tablename__ = 'dogs'

    # Dog data
    ## Entry data
    id = Column(ID_COLUMN_TYPE, primary_key=True, default=ID_CREATOR)
    dog_type = Column(DOG_TYPE_ENUMS, nullable=False)
    is_matched = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    ## contact details
    contact_name = Column(String)
    contact_phone = Column(String)
    contact_email = Column(String)
    contact_address = Column(String)

    ## dog attributes
    name = Column(String)
    chip_number = Column(String(length=15))
    breed = Column(String)
    color = Column(String)
    size = Column(String)
    extra_details = Column(String)
    sex = Column(DOG_SEX_ENUMS)

    ## change times
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # relationship
    images = relationship('DogImages', back_populates='dog')


class DogImages(Base):
    __tablename__ = 'dog_images'
    id = Column(ID_COLUMN_TYPE, primary_key=True, default=ID_CREATOR)
    dog_id = Column(ID_COLUMN_TYPE, ForeignKey('dogs.id'))
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    dog = relationship('Dog', back_populates='images')


def add_examples(session):
    # Example 1: Insert a dog
    dog1 = Dog(dog_type="lost", name="Rex", chip_number="1234567890", breed="Labrador",
               color="Yellow", size="Large")
    session.add(dog1)

    # Example 2: Insert dog images
    image1 = DogImages(dog=dog1, image_url="https://example.com/rex1.jpg")
    image2 = DogImages(dog=dog1, image_url="https://example.com/rex2.jpg")
    session.add_all([image1, image2])

    # Commit the changes to the database
    session.commit()

    dog2 = Dog(dog_type="found", name="Buddy", chip_number="9876543210", breed="Golden Retriever",
               color="Golden", size="Medium")
    session.add(dog2)

    # Commit the changes to the database
    session.commit()

    # Example 3: Insert more dog images
    image3 = DogImages(dog=dog2, image_url="https://example.com/buddy1.jpg")
    image4 = DogImages(dog=dog2, image_url="https://example.com/buddy2.jpg")
    session.add_all([image3, image4])

    # Commit the changes to the database
    session.commit()


def get_connection_string(user, password, host, port=5432, db='dogfinder', protocol='postgresql'):
    if protocol == 'sqlite':
        return f"sqlite:///localhost/{db}.db"
    else:
        return f'{protocol}://{user}:{password}@{host}:{port}/{db}'


def main():
    # Create DB connection
    db_connection_string = get_connection_string(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT,
                                                 db=DB_NAME, protocol=DB_PROTOCOL)
    engine = create_engine(url=db_connection_string, echo=True)

    # Drop existing db if exists
    if database_exists(engine.url):
        drop_database(engine.url)

    # Create new db if not exists
    if not database_exists(engine.url):
        create_database(engine.url)

    # Open session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the database tables
    Base.metadata.create_all(engine)

    # Insert examples
    add_examples(session)


if __name__ == '__main__':
    main()
