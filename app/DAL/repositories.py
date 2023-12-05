from contextlib import AbstractContextManager
from typing import Callable, Optional, Tuple
from sqlalchemy.orm import Session, subqueryload
from sqlalchemy.exc import SQLAlchemyError
from app.DAL.models import Dog, DogImage, PossibleDogMatch
from automapper import mapper
from app.DTO.dog_dto import DogDTO, DogImageDTO, DogType, PossibleDogMatchDTO
from app.MyLogger import logger

class DogWithImagesRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        """
        Initialize the DogWithImagesRepository with a session factory.

        Args:
            session_factory (Callable[..., AbstractContextManager[Session]]): A callable that returns a session context manager.
        """
        self.session_factory = session_factory

    def add_dog_with_images(self, dogDTO: DogDTO) -> DogDTO:
        """
        Add a dog with images to the database.

        Args:
            dogDTO (DogDTO): The dog data transfer object.

        Returns:
            DogDTO: The dog data transfer object with the added dog and images.
        """
        try:
            with self.session_factory() as session:
                dog: Dog = mapper.map(dogDTO)

                session.add(dog)
                session.commit()

                session.refresh(dog)

                dogDTO = mapper.map(dog)

                return dogDTO
        except SQLAlchemyError as e:
            logger.exception(f"DB Error while adding dog with images: {e}")
            session.rollback()
            raise e
        except Exception as e:
            logger.exception(f"Error while adding dog with images: {e}")
            session.rollback()
            raise e

    def get_dog_with_images_by_id(self, dog_id: int) -> DogDTO:
        """
        Retrieve a dog with images from the database by its ID.

        Args:
            dog_id (int): The ID of the dog.

        Returns:
            DogDTO: The dog data transfer object with the retrieved dog and images.
        """
        try:
            with self.session_factory() as session:
                dog = session.query(Dog).options(subqueryload(Dog.images)).filter(Dog.id == dog_id).first()
                
                dogDTO = mapper.map(dog)

                return dogDTO
        except SQLAlchemyError as e:
            raise e

    def get_all_dogs_with_images(self, type: Optional[DogType] = None, page: int = 1, page_size: int = 10) -> Tuple[list[DogDTO], int]:
        """
        Retrieve all dogs with images from the database.

        Args:
            type (Optional[DogType], optional): The type of dogs to retrieve. Defaults to None.
            page (int, optional): The page number. Defaults to 1.
            page_size (int, optional): The number of dogs per page. Defaults to 10.

        Returns:
            Tuple[list[DogDTO], int]: A tuple containing the list of dog data transfer objects and the total number of dogs.
        """
        try:
            with self.session_factory() as session:
                dogs_query = session.query(Dog).options(subqueryload(Dog.images), subqueryload(Dog.possibleMatches))
                if type:
                    dogs_query = dogs_query.filter(Dog.type == type)
                
                total_dogs = dogs_query.count()

                dogs_query = dogs_query.order_by("id").offset((page - 1) * page_size).limit(page_size)

                dogs = dogs_query.all()

                dogsDTO = [mapper.map(dog) for dog in dogs]

                return dogsDTO, total_dogs
        except SQLAlchemyError as e:
            raise e

    def get_all_dogs_with_images_by_reporter_id(self, reporter_id: str, page: int = 1, page_size: int = 10) -> Tuple[list[DogDTO], int]:
        """
        Retrieve all dogs reported by a user from the database.

        Args:
            reporter_id (str): The ID of the user.
            page (int, optional): The page number. Defaults to 1.
            page_size (int, optional): The number of dogs per page. Defaults to 10.

        Returns:
            Tuple[list[DogDTO], int]: A tuple containing the list of dog data transfer objects and the total number of dogs.
        """
        try:
            with self.session_factory() as session:
                dogs_query = session.query(Dog).options(subqueryload(Dog.images)).filter(Dog.reporterId == reporter_id)
                
                total_dogs = dogs_query.count()

                dogs_query = dogs_query.order_by("id").offset((page - 1) * page_size).limit(page_size)

                dogs = dogs_query.all()

                dogsDTO = [mapper.map(dog, fields_mapping={ "possibleMatch": None, "dog": None }) for dog in dogs]

                return dogsDTO, total_dogs
        except SQLAlchemyError as e:
            raise e

    def update_dog_is_resolved(self, dog_id: int, is_resolved: bool) -> None:
        """
        Update the isResolved property of a dog in the database.

        Args:
            dog_id (int): The ID of the dog.
            is_resolved (bool): The new value of the isResolved property.
        """
        try:
            with self.session_factory() as session:
                dog = session.query(Dog).filter(Dog.id == dog_id).first()
                
                dog.isResolved = is_resolved

                session.commit()
        except SQLAlchemyError as e:
            logger.exception(f"DB Error while updating dog isResolved: {e}")
            session.rollback()
            raise e
        except Exception as e:
            logger.exception(f"Error while updating dog isResolved: {e}")
            session.rollback()
            raise e

    def add_possible_dog_match(self, possibleDogMatchDTO: PossibleDogMatchDTO) -> None:
        """
        Add a possible dog match to the database.

        Args:
            possibleDogMatchDTO (PossibleDogMatchDTO): The possible dog match data transfer object.
        """
        try:
            with self.session_factory() as session:
                possibleDogMatch: PossibleDogMatch = mapper.map(possibleDogMatchDTO)

                dog = session.query(Dog).get(possibleDogMatch.dogId)
                possibleMatch = session.query(Dog).get(possibleDogMatch.possibleMatchId)

                possibleDogMatch.dog = dog
                possibleDogMatch.possibleMatch = possibleMatch

                session.add(possibleDogMatch)
                session.commit()

                session.refresh(possibleDogMatch)
        except SQLAlchemyError as e:
            logger.exception(f"DB Error while adding possible dog match: {e}")
            session.rollback()
            raise e
        except Exception as e:
            logger.exception(f"Error while adding possible dog match: {e}")
            session.rollback()
            raise e
        
    def get_possible_dog_matches(self, dog_id: Optional[int] = None, page: int = 1, page_size: int = 10) -> Tuple[list[PossibleDogMatchDTO], int]:
        """
        Retrieve possible dog matches from the database.

        Args:
            dog_id (int, optional): The ID of the dog. If provided, retrieves possible dog matches for a specific dog. Defaults to None.
            page (int, optional): The page number. Defaults to 1.
            page_size (int, optional): The number of possible dog matches per page. Defaults to 10.

        Returns:
            Tuple[list[PossibleDogMatchDTO], int]: A tuple containing the list of possible dog match data transfer objects and the total number of possible dog matches.
        """
        try:
            with self.session_factory() as session:
                possibleDogMatches_query = session.query(PossibleDogMatch).options(subqueryload(PossibleDogMatch.dog), subqueryload(PossibleDogMatch.possibleMatch))
                
                if dog_id is not None:
                    possibleDogMatches_query = possibleDogMatches_query.filter(PossibleDogMatch.dogId == dog_id)

                total_possibleDogMatches = possibleDogMatches_query.count()

                possibleDogMatches_query = possibleDogMatches_query.order_by("id").offset((page - 1) * page_size).limit(page_size)

                possibleDogMatches = possibleDogMatches_query.all()

                possibleDogMatchesDTO = [mapper.map(possibleDogMatch) for possibleDogMatch in possibleDogMatches]

                return possibleDogMatchesDTO, total_possibleDogMatches
        except SQLAlchemyError as e:
            raise e

    def delete_dog_with_images_by_id(self, dog_id: int) -> None:
        """
        Delete a dog with images from the database by its ID.

        Args:
            dog_id (int): The ID of the dog.
        """
        try:
            with self.session_factory() as session:
                dog = session.query(Dog).options(subqueryload(Dog.images)).filter(Dog.id == dog_id).first()
                
                # Delete the dog
                session.delete(dog)
                session.commit()
        except SQLAlchemyError as e:
            logger.exception(f"DB Error while deleting dog with images: {e}")
            session.rollback()
            raise e
        except Exception as e:
            logger.exception(f"Error while deleting dog with images: {e}")
            session.rollback()
            raise e