# Add function that will index all dogs with images
from datetime import datetime
from typing import Any, List
from app.DAL.models import Dog, DogImage
from app.DTO.dog_dto import DogDTO, DogImageDTO
# from app.DTO.dog_dto import DogDTO
from app.helpers.image_helper import create_pil_images
from app.services.ivectordb_client import IVectorDBClient
from app.MyLogger import logger
from app.helpers.model_helper import embed_documents, embed_query
from weaviate.util import generate_uuid5

class VectorDBIndexer:
    def __init__(self, vecotrDBClient: IVectorDBClient, embedding_model, image_segmentation_model) -> None:
        self.vecotrDBClient = vecotrDBClient
        self.embedding_model = embedding_model
        self.image_segmentation_model = image_segmentation_model

    def index_dogs_with_images(self, dogDTOs: list[DogDTO]) -> None:
        # Add the document to the database
        documents = []
        failed_objects = []

        # iterate over dogs and each image for each dog and create a list of data_properties, add them to documents. Add the documents to the database
        for dogDTO in dogDTOs:
            try:
                # Create a list of PIL images from the base64 images
                pilImages = create_pil_images([image.base64Image for image in dogDTO.images])

                # Embed the document image
                dog_images_embedding = embed_documents(pilImages, self.embedding_model, image_segmentation_model=self.image_segmentation_model)
            
                for i, dogImage in enumerate(dogDTO.images):
                    logger.info(f"Adding document {dogDTO.id} with image id {dogImage.id} to VectorDB")
                    data_properties = create_data_properties(dogDTO, dogImage)
                    data_properties["uuid5"] = generate_uuid5({"dogId": dogDTO.id, "imageId": dogImage.id })
                    data_properties["document_embedding"] = dog_images_embedding[i]
                    documents.append(data_properties)
            except Exception as e:
                logger.exception(f"Error while creating indexing document for dog with id {dogDTO.id}: {e}")
                failed_objects.append(dogDTO.id)

        result = self.vecotrDBClient.add_documents_batch("Dog", documents)

        result["failed"] += len(failed_objects)
        result["failed_objects"].extend(failed_objects)
        
        return result
    
    def delete_dogs_with_images(self, dogs: List[Dog]) -> None:
        # Delete the documents from the database

        result = self.vecotrDBClient.delete_by_ids(
            class_name='Dog',
            field_name='dogId',
            ids=[dog.id for dog in dogs]
        )

        return result

def create_data_properties(dog: DogDTO, dogImage: DogImageDTO) -> dict[str, Any]:
    # Transform document to dictionary
    data_properties = dog.to_vectordb_json()
    
    # Transform datetime objects to string
    # for key, val in data_properties.items():
    #     if isinstance(val, datetime):
    #         data_properties[key.lower()] = val.strftime("%Y-%m-%dT%H:%M:%S.%SZ") if val else None

    data_properties["dogId"] = dog.id
    data_properties["dogImageId"] = dogImage.id
    data_properties["imageBase64"] = dogImage.base64Image
    data_properties["imageContentType"] = dogImage.imageContentType

    return data_properties