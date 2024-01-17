# DogWithImagesService that will be used to get the dog images from the API
# will use DogWithImagesRepository to get the dog images from the DB and into the DB
from typing import Optional, Tuple
from app.DAL.models import Dog
from app.DAL.repositories import DogWithImagesRepository
from app.DTO.dog_dto import DogDTO, DogType, PossibleDogMatchDTO
from app.services.vectordb_indexer import VectorDBIndexer
from app.MyLogger import logger

class DogWithImagesService:
    def __init__(self, repository: DogWithImagesRepository, vectordbIndexer: VectorDBIndexer) -> None:
        self.repository: DogWithImagesRepository = repository
        self.vectordbIndexer: VectorDBIndexer = vectordbIndexer

    def add_dog_with_images(self, dogDTO: DogDTO) -> Tuple[Dog, dict]:
        try:
            newDogDTO = self.repository.add_dog_with_images(dogDTO)

            # Add the dog to the vector database
            result = self.vectordbIndexer.index_dogs_with_images([newDogDTO])

            return newDogDTO, result
        except Exception as e:
            logger.exception(f"Error while adding dog with images: {e}")
            raise e

    # index all dogs with images
    def index_all_dogs_with_images(self) -> dict:
        try:
            # Get dogs total count
            final_result = None
            _, total_count = self.repository.get_all_dogs_with_images(type=None, is_resolved=False, page=1, page_size=1)

            # Calculate total pages
            total_pages = (total_count + 99) // 100

            # Loop over the total pages and index the dogs with images in the vector database
            for i in range(1, total_pages + 1):
                dogDTOs, _ = self.repository.get_all_dogs_with_images(type=None, is_resolved=False, page=i, page_size=100)

                result = self.vectordbIndexer.index_dogs_with_images(dogDTOs)

                # Aggregate the result and return the final result
                if final_result is None:
                    final_result = result
                else:
                    final_result["successful"] += result["successful"]
                    final_result["failed"] += result["failed"]
                    final_result["failed_objects"].extend(result["failed_objects"])

            return final_result
        except Exception as e:
            logger.exception(f"Error while indexing all dogs with images: {e}")
            raise e

    def get_dog_with_images_by_id(self, dog_id: int) -> DogDTO:
        try:
            return self.repository.get_dog_with_images_by_id(dog_id)
        except Exception as e:
            logger.exception(f"Error while getting dog with images by ID: {e}")
            raise e

    def get_all_dogs_with_images(self, type: Optional[DogType] = None, page: int = 1, page_size: int = 10, sort_order: str = "desc") -> Tuple[list[DogDTO], int]:
        try:
            return self.repository.get_all_dogs_with_images(type=type, page=page, page_size=page_size, sort_order=sort_order)
        except Exception as e:
            logger.exception(f"Error while getting all dogs with images: {e}")
            raise e

    def get_all_dogs_with_images_by_reporter_id(self, reporter_id: str, page: int = 1, page_size: int = 10) -> Tuple[list[DogDTO], int]:
        try:
            return self.repository.get_all_dogs_with_images_by_reporter_id(reporter_id, page=page, page_size=page_size)
        except Exception as e:
            logger.exception(f"Error while getting all dogs with images by reporter ID: {e}")
            raise e
        
    def get_possible_dog_matches(self, dog_id: Optional[int] = None, page: int = 1, page_size: int = 10) -> Tuple[list[PossibleDogMatchDTO], int]:
        try:
            return self.repository.get_possible_dog_matches(dog_id, page=page, page_size=page_size)
        except Exception as e:
            logger.exception(f"Error while getting possible dog matches: {e}")
            raise e

    def delete_possible_dog_match(self, id: int) -> None:
        try:
            self.repository.delete_possible_dog_match(id)
        except Exception as e:
            logger.exception(f"Error while deleting possible dog match: {e}")
            raise e

    # Update the dog isResolved field to True or False
    def update_dog_is_resolved(self, dog_id: int, possibleMatchId: int, is_resolved: bool) -> None:
        try:
            self.repository.update_dog_is_resolved(dog_id, is_resolved)
            self.repository.delete_possible_dog_matches(dog_id)
            self.repository.update_dog_is_resolved(possibleMatchId, is_resolved)
            self.repository.delete_possible_dog_matches(possibleMatchId)

            self.vectordbIndexer.delete_dogs_with_images([Dog(id=dog_id)])
            self.vectordbIndexer.delete_dogs_with_images([Dog(id=possibleMatchId)])
        except Exception as e:
            logger.exception(f"Error while updating dog isResolved field: {e}")
            raise e

    def get_possible_dog_matches_count(self) -> int:
        try:
            return self.repository.get_possible_dog_matches_count()
        except Exception as e:
            logger.exception(f"Error while getting count of possible dog matches: {e}")
            raise e
    
    def add_possible_dog_match(self, possibleDogMatchDTO: PossibleDogMatchDTO) -> None:
        try:
            self.repository.add_possible_dog_match(possibleDogMatchDTO)
        except Exception as e:
            logger.exception(f"Error while adding possible dog match: {e}")
            raise e

    # delete the dog with images from the DB
    def delete_dog_with_images_by_id(self, dog_id: int) -> None:
        try:
            self.repository.delete_dog_with_images_by_id(dog_id)

            self.vectordbIndexer.delete_dogs_with_images([Dog(id=dog_id)])
        except Exception as e:
            logger.exception(f"Error while deleting dog with images: {e}")
            raise e