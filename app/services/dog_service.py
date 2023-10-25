# DogWithImagesService that will be used to get the dog images from the API
# will use DogWithImagesRepository to get the dog images from the DB and into the DB
from app.DAL.models import Dog
from app.DAL.repositories import DogWithImagesRepository
from app.DTO.dog_dto import DogDTO
from app.services.vectordb_indexer import VectorDBIndexer


class DogWithImagesService:
    def __init__(self, repository: DogWithImagesRepository, vectordbIndexer: VectorDBIndexer) -> None:
        self.repository = repository
        self.vectordbIndexer = vectordbIndexer

    def add_dog_with_images(self, dogDTO: DogDTO) -> Dog:
        dog = self.repository.add_dog_with_images(dogDTO)

        # Add the dog to the vector database
        result = self.vectordbIndexer.index_dogs_with_images([dog])

        return dog, result

    def get_dog_with_images_by_id(self, dog_id: int) -> DogDTO:
        return self.repository.get_dog_with_images_by_id(dog_id)

    def get_all_dogs_with_images(self) -> list[DogDTO]:
        return self.repository.get_all_dogs_with_images()
    
    # Update the dog isMatched field to True or False
    def update_dog_is_matched(self, dog_id: int, is_matched: bool) -> DogDTO:
        self.repository.update_dog_is_matched(dog_id, is_matched)

        result = self.vectordbIndexer.delete_dogs_with_images([Dog(id=dog_id)])

        return result
