import os

from sqlalchemy import create_engine, orm
from contextlib import contextmanager, AbstractContextManager
from sqlalchemy.orm import declarative_base, Session
from app.MyLogger import logger
from typing import Callable

def get_connection_string(user: str, password: str, host: str, port: int = 5432, db: str = 'dogfinder', protocol: str = 'postgresql') -> str:
    if protocol == 'sqlite':
        return f"sqlite:///{db}.db"
    else:
        return f'{protocol}://{user}:{password}@{host}:{port}/{db}'

# Create a base class for declarative models
Base = declarative_base()

class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.error("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()

#
# def add_examples(session):
#     # Example 1: Insert a dog
#     dog1 = Dog(dog_type="lost", name="Rex", chip_number="1234567890", breed="Labrador",
#                color="Yellow", size="Large")
#     session.add(dog1)
#
#     # Example 2: Insert dog images
#     image1 = DogImages(dog=dog1, image_base64="SOME_IMAGE_BASE64")
#     image2 = DogImages(dog=dog1, image_base64="SOME_IMAGE_BASE64")
#     session.add_all([image1, image2])
#
#     # Commit the changes to the database
#     session.commit()
#
#     dog2 = Dog(dog_type="found", name="Buddy", chip_number="9876543210", breed="Golden Retriever",
#                color="Golden", size="Medium", location="Somewhere over the rainbow")
#     session.add(dog2)
#
#     # Commit the changes to the database
#     session.commit()
#
#     # Example 3: Insert more dog images
#     image3 = DogImages(dog=dog2, image_base64="SOME_IMAGE_BASE64")
#     image4 = DogImages(dog=dog2, image_base64="SOME_IMAGE_BASE64")
#     session.add_all([image3, image4])
#
#     # Commit the changes to the database
#     session.commit()


# def get_connection_string(user: str, password: str, host: str, port: int = 5432, db: str = 'dogfinder',
#                           protocol: str = 'postgresql') -> str:
#     if protocol == 'sqlite':
#         return f"sqlite:///{db}.db"
#     else:
#         return f'{protocol}://{user}:{password}@{host}:{port}/{db}'
#
#
# def main():
#     from sqlalchemy_utils import database_exists, create_database, drop_database
#     from sqlalchemy import create_engine
#     from sqlalchemy.orm import sessionmaker
#
#     # Create DB connection
#     db_connection_string = get_connection_string(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT,
#                                                  db=DB_NAME, protocol=DB_PROTOCOL)
#     engine = create_engine(url=db_connection_string, echo=True)
#
#     # Drop existing db if exists
#     if database_exists(engine.url):
#         drop_database(engine.url)
#
#     # Create new db if not exists
#     if not database_exists(engine.url):
#         create_database(engine.url)
#
#     # Open session
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     # Create the database tables
#     Base.metadata.create_all(engine)
#
#     # Insert examples
#     add_examples(session)
#
#
# if __name__ == '__main__':
#     main()
