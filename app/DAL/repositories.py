
from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy.orm import Session
from app.DAL.models import Dog, DogImage, PossibleDogMatch
from sqlalchemy.exc import SQLAlchemyError
from automapper import mapper
from app.DTO.dog_dto import DogDTO, DogImageDTO, PossibleDogMatchDTO
from sqlalchemy.orm import subqueryload
from app.MyLogger import logger

class DogWithImagesRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    from sqlalchemy.exc import SQLAlchemyError

    def add_dog_with_images(self, dogDTO: DogDTO) -> DogDTO:
        try:
            with self.session_factory() as session:
                # Create dog object                
                dog: Dog = mapper.to(Dog).map(dogDTO, fields_mapping={
                    "images": [DogImage(base64Image=image.base64Image, imageContentType=image.imageContentType) for image in dogDTO.images]
                })

                session.add(dog)
                session.commit()

                session.refresh(dog)

                dogDTO = mapper.to(DogDTO).map(dog, fields_mapping={ "images": [] })
                dogDTO.images = [mapper.to(DogImageDTO).map(image) for image in dog.images]

                return dogDTO
        except SQLAlchemyError as e:
            # Rollback transaction on error
            logger.exception(f"DB Error while adding dog with images: {e}")
            session.rollback()
            raise e
        except Exception as e:
            # Rollback transaction on error
            logger.exception(f"Error while adding dog with images: {e}")
            session.rollback()
            raise e
        finally:
            # Close session
            session.close()

    # Add the rest of the CRUD operations here with images
    def get_dog_with_images_by_id(self, dog_id: int) -> DogDTO:
        try:
            with self.session_factory() as session:
                # Query dog with images by id eager loading images relationship with join
                dog = session.query(Dog).options(subqueryload(Dog.images)).filter(Dog.id == dog_id).first()
                
                dogDTO = mapper.to(DogDTO).map(dog, fields_mapping={ "images": [] })
                dogDTO.images = [mapper.to(DogImageDTO).map(image) for image in dog.images]

                return dogDTO
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def get_all_dogs_with_images(self) -> list[DogDTO]:
        try:
            dogsDTO = []

            with self.session_factory() as session:
                dogs = session.query(Dog).options(subqueryload(Dog.images)).all()
                session.refresh(dogs)

                dogsDTO = [mapper.to(DogDTO).map(dog, fields_mapping={ "images": [] }) for dog in dogs]
                for i, dog in enumerate(dogs):
                    dogsDTO[i].images = [mapper.to(DogImageDTO).map(image) for image in dog.images]

                return dogs
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    # Update the dog isResolved field to True or False    
    def update_dog_is_resolved(self, dog_id: int, is_resolved: bool) -> None:
        try:
            with self.session_factory() as session:
                # Query dog with images by id eager loading images relationship with join
                dog = session.query(Dog).filter(Dog.id == dog_id).first()
                
                dog.isResolved = is_resolved

                session.commit()
        except SQLAlchemyError as e:
            raise e
        finally:
            session.close()

    def add_possible_dog_match(self, possibleDogMatchDTO: PossibleDogMatchDTO) -> None:
        try:
            with self.session_factory() as session:
                # Create dog object                
                possibleDogMatch: PossibleDogMatch = mapper.to(PossibleDogMatch).map(possibleDogMatchDTO)

                # Fetch the Dog instances
                dog = session.query(Dog).get(possibleDogMatch.dogId)
                possibleMatch = session.query(Dog).get(possibleDogMatch.possibleMatchId)

                # Assign the Dog instances
                possibleDogMatch.dog = dog
                possibleDogMatch.possibleMatch = possibleMatch

                session.add(possibleDogMatch)
                session.commit()

                session.refresh(possibleDogMatch)

                # Returning the possibleDogMatchDTO with the dog and possibleMatch instances
                # Remarking for now if it's not really needed
                # possibleDogMatchDTO = mapper.to(PossibleDogMatchDTO).map(possibleDogMatch, fields_mapping={ "dog": None, "possibleMatch": None })
                # possibleDogMatchDTO.dog = mapper.to(DogDTO).map(dog, fields_mapping={ "images": [] })
                # possibleDogMatchDTO.dog.images = [mapper.to(DogImageDTO).map(image) for image in dog.images]
                # possibleDogMatchDTO.possibleMatch = mapper.to(DogDTO).map(possibleMatch, fields_mapping={ "images": [] })
                # possibleDogMatchDTO.possibleMatch.images = [mapper.to(DogImageDTO).map(image) for image in possibleMatch.images]

                # return possibleDogMatchDTO
        except SQLAlchemyError as e:
            # Rollback transaction on error
            logger.exception(f"DB Error while adding possible dog match: {e}")
            session.rollback()
            raise e
        except Exception as e:
            # Rollback transaction on error
            logger.exception(f"Error while adding possible dog match: {e}")
            session.rollback()
            raise e
        finally:
            # Close session
            session.close()