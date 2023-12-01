import hashlib
from http import HTTPStatus
import uuid
from app.DTO.dog_dto import DogDTO, DogImageDTO, DogType, PossibleDogMatchDTO
from app.helpers.image_helper import create_pil_images, get_base64
from app.services.auth import VerifyToken
from typing import Any, List, Optional
from app.MyLogger import logger
from app.services.dog_service import DogWithImagesService
from app.services.vectordb_indexer import VectorDBIndexer
from app.viewmodels.api_response import APIResponse
from app.viewmodels.dog_viewmodel import RETURN_PROPERTIES, DogFullDetailsResponse, DogImageResponse, DogAddRequest, DogResolvedRequest, DogResponse, DogSearchRequest, PossibleDogMatchRequest, PossibleDogMatchResponse
from fastapi import APIRouter, File, Form, Query, Security, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from app.helpers.model_helper import create_embedding_model, embed_query
from app.helpers.helper import detect_image_mimetype, generate_dog_id, hash_image, resize_image_and_convert_to_format, timeit
from app.helpers.weaviate_helper import FilterValueTypes
from weaviate.util import generate_uuid5
from app.models.predicates import Predicate, Filter, and_, or_
# from sentence_transformers import SentenceTransformer
import os
from datetime import date, datetime, timedelta
from PIL import Image
from io import BytesIO
import base64
from app.services.ivectordb_client import IVectorDBClient
from app.services.weaviate_vectordb_client import WeaviateVectorDBClient
from automapper import mapper
from app.DAL.database import Database, get_connection_string
from app.DAL.repositories import DogWithImagesRepository

logger.info("Starting up the dogfinder router")

router = APIRouter(prefix="/dogfinder")
vecotrDBClient: IVectorDBClient
dogWithImagesRepository: DogWithImagesRepository = None
dogWithImagesService: DogWithImagesService = None
embedding_model: Any = None
db: Database = None

# CHANGE THIS TO FALSE ON PRODUCTION
IS_VERIFIED_FIELD_DEFAULT_VALUE = False

dog_class_definition = {
        "class": "Dog",
        "invertedIndexConfig": {
            "indexNullState": True,
            "indexTimestamps": True
        },
        "properties": [
            {
                "name": "breed",
                "dataType": ["text"],
                "description": "Name of dog breed"
            },
            {
                "name": "size",
                "dataType": ["text"],
                "description": "The dog's size"
            },
            {
                "name": "color",
                "dataType": ["text"],
                "description": "The dog's color"
            },
            {
                "name": "sex",
                "dataType": ["text"],
                "description": "The dog's sex"
            },
            {
                "name": "ageGroup",
                "dataType": ["text"],
                "description": "The dog's age group"
            },
            {
                "name": "extraDetails",
                "dataType": ["text"],
                "description": "Any extra detail that can be returned to the user to identify the dog"
            },
            {
                "name": "location",
                "dataType": ["text"],
                "description": "The location where the dog was lost or found"
            },
            {
                "name": "type",
                "dataType": ["text"],
                "description": "Found Or Lost"
            },
            {
                "name": "imageBase64",
                "dataType": ["blob"],
                "description": "Image in base64 format"
            },
            {
                "name": "isResolved",
                "dataType": ["boolean"],
                "description": "was the dog found?"
            },
            {
                "name": "dogId",
                "dataType": ["number"],
                "description": "Id of the dog"
            },
            {
                "name": "dogImageId",
                "dataType": ["number"],
                "description": "Id of the dog image"
            },
            {
                "name": "contactName",
                "dataType": ["text"],
                "description": "Contact name"
            },
            {
                "name": "contactPhone",
                "dataType": ["text"],
                "description": "Contact phone"
            },
            {
                "name": "contactEmail",
                "dataType": ["text"],
                "description": "Contact email"
            },
            {
                "name": "contactAddress",
                "dataType": ["text"],
                "description": "Contact address"
            },
            {
                "name": "isVerified",
                "dataType": ["boolean"],
                "description": "Is the dog entry verified?"
            },
            {
                "name": "imageContentType",
                "dataType": ["text"],
                "description": "The image content type"
            },
            {
                "name": "chipNumber",
                "dataType": ["text"],
                "description": "The chip number of the dog if exists"
            },
            {
                "name": "name",
                "dataType": ["text"],
                "description": "The name of the dog if exists"
            },
            {
                "name": "dogFoundOn",
                "dataType": ["text"],
                "description": "The date the dog was found"
            }
        ]
    }


@router.on_event("startup")
async def startup_event():
    """
    Load all the necessary models and data once the server starts.
    """
    global vecotrDBClient
    global dogWithImagesRepository
    global dogWithImagesService
    global embedding_model
    global db

    # Create the vector db client, connecting to the weaviate instance
    vecotrDBClient = WeaviateVectorDBClient(url=f"{os.getenv('WEAVIATE_HOST', 'http://localhost:8080')}")
    # Create the schema
    vecotrDBClient.create_schema(class_name="Dog", class_obj=dog_class_definition)

    # DB variables
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME", 'dogfinder')
    DB_PROTOCOL = os.environ.get("DB_PROTOCOL", "sqlite")

    db_connection_string = get_connection_string(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, db=DB_NAME, protocol=DB_PROTOCOL)
    db = Database(db_url=db_connection_string)
    db.create_tables()
    
    # Create the embedding model
    logger.info(f"Creating embedding model")
    embedding_model, cache_info = create_embedding_model()
    
    # Create vectordb indexer
    vectorDBIndexer = VectorDBIndexer(vecotrDBClient, embedding_model)

    # Create the dogWithImagesRepository with the session_factory
    dogWithImagesRepository = DogWithImagesRepository(session_factory=db.session)
    dogWithImagesService = DogWithImagesService(dogWithImagesRepository, vectorDBIndexer)

    


auth = VerifyToken()

# @router.post("/query/", response_model=APIResponse)
# async def query(type: DogType = Form(...), breed: Optional[str] = Form(None), img: UploadFile = File(...), top: int = Form(10), isVerified: Optional[bool] = Form(True)):
#     try:
#         # Handle the image, resize it and convert it to base64 with webp format and get the content type
#         base64Images, imageContentTypes = zip(*handle_uploaded_images([img]))

#         # Create QueryRequest
#         queryRequest = QueryRequest(type=type, breed=breed, imageBase64=base64Images[0], top=top, isVerified=isVerified)

#         # Query the database
#         results = query_vector_db(queryRequest, query)

#         api_response = APIResponse(status_code=200, message=f"Queried {len(results)} results from the vecotrdb", data={ "total": len(results), "results": results })
#     except Exception as e:
#         logger.error(f"Error while querying the vecotrdb: {e}")
#         api_response = APIResponse(status_code=500, message=f"Error while querying the vecotrdb: {e}", data={ "total": 0, "results": [] })
#     finally:
#         # return back a json response and set the status code to api_response.status_code
#         return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.post("/search_in_found_dogs", response_model=APIResponse)
async def search_in_found_dogs(dogSearchRequest: DogSearchRequest):
    try:
        # Handle the image, resize it and convert it to base64 with webp format and get the content type
        base64Images, imageContentTypes = zip(*handle_uploaded_images([dogSearchRequest.base64Image]))

        # Create QueryRequest
        dogSearchRequest.type = DogType.FOUND
        dogSearchRequest.base64Image = base64Images[0]
        dogSearchRequest.isVerified = True

        # Query the database
        results = query_vector_db(dogSearchRequest)

        api_response = APIResponse(status_code=200, message=f"Queried {len(results)} results from the vecotrdb", data={ "total": len(results), "results": results })
    except Exception as e:
        logger.error(f"Error while querying the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying the vecotrdb: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.post("/search_in_lost_dogs", response_model=APIResponse)
async def search_in_lost_dogs(dogSearchRequest: DogSearchRequest):
    try:
        # Handle the image, resize it and convert it to base64 with webp format and get the content type
        base64Images, imageContentTypes = zip(*handle_uploaded_images([dogSearchRequest.base64Image]))

        # Create QueryRequest
        dogSearchRequest.type = DogType.LOST
        dogSearchRequest.base64Image = base64Images[0]
        dogSearchRequest.isVerified = True
        # queryRequest = QueryRequest(type=DogType.LOST, breed=breed, imageBase64=base64Images[0], top=top, isVerified=True)

        # Query the database
        results = query_vector_db(dogSearchRequest)

        api_response = APIResponse(status_code=200, message=f"Queried {len(results)} results from the vecotrdb", data={ "total": len(results), "results": results })
    except Exception as e:
        logger.error(f"Error while querying the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying the vecotrdb: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.get("/get_unverified_documents", response_model=APIResponse)
async def get_unverified_documents(auth_result: dict = Security(auth.verify, scopes=['read:unverified_documents'])):
    try:
        # Query the database
        results = vecotrDBClient.query(class_name="Dog", query=None, query_embedding=None, limit=10000, offset=None, filter=and_(*[Predicate(["isVerified"], "Equal", False, FilterValueTypes.valueBoolean)]).to_dict(), properties=RETURN_PROPERTIES)

        api_response = APIResponse(status_code=200, message=f"Queried {len(results)} results from the vecotrdb", data={ "total": len(results), "results": results })
    except Exception as e:
        logger.error(f"Error while querying the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying the vecotrdb: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)
    
# Endpoint for quering the database without the need for a query image, only DOG_ID_FIELD
@router.get("/get_dog_by_id", response_model=APIResponse)
async def get_dog_by_id(dogId: int):
    try:
        # Query the database
        dog = dogWithImagesRepository.get_dog_with_images_by_id(dogId)
        
        dogResponse = mapper.to(DogResponse).map(dog, fields_mapping={"images": []})
        dogResponse.images = [mapper.to(DogImageResponse).map(image) for image in dog.images]

        api_response = APIResponse(status_code=200, message=f"Queried dog from the database", data={ "results": dogResponse.model_dump() })
    except Exception as e:
        logger.error(f"Error while querying the database: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying the database: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.get("/get_dog_by_id_full_details", response_model=APIResponse)
async def query_by_dog_id(dogId: int, auth_result: dict = Security(auth.verify, scopes=['read:get_dog_by_id_full_details'])):
    try:
        # Query the database
        dog = dogWithImagesRepository.get_dog_with_images_by_id(dogId)
        
        dogFullDetailsResponse = mapper.to(DogFullDetailsResponse).map(dog, fields_mapping={"images": []})
        dogFullDetailsResponse.images = [mapper.to(DogImageResponse).map(image) for image in dog.images]

        api_response = APIResponse(status_code=200, message=f"Queried dog from the database", data={ "results": dogFullDetailsResponse.model_dump() })
    except Exception as e:
        logger.error(f"Error while querying the database: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying the database: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

# Create endpoint for adding possible dog match, using the dogId and possibleMatchId
@router.post("/add_possible_dog_match", response_model=APIResponse)
async def add_possible_dog_match(possibleDogMatchRequest: PossibleDogMatchRequest):
    try:
        # Create PossibleDogMatchDTO
        possibleDogMatchDTO = mapper.to(PossibleDogMatchDTO).map(possibleDogMatchRequest)

        # Add the possible dog match to the database
        dogWithImagesService.add_possible_dog_match(possibleDogMatchDTO)

        api_response = APIResponse(status_code=200, message=f"Added possible dog match to the database")
    except Exception as e:
        logger.error(f"Error while adding possible dog match to the database: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while adding possible dog match to the database: {e}")
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

# add endpoint for getting dogs reported by a specific user, get the reporterId from the auto0 token
@router.get("/get_dogs_by_reporter_id", response_model=APIResponse)
async def get_dogs_by_reporter_id(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), auth_result: dict = Security(auth.verify)):
    try:
        # Query the database
        dogs, total_count = dogWithImagesService.get_all_dogs_with_images_by_reporter_id(auth_result["sub"], page=page, page_size=page_size)
        
        dogFullDetailsResponses = [mapper.to(DogFullDetailsResponse).map(dog, fields_mapping={"images": []}) for dog in dogs]
        for dog, dogResponse in zip(dogs, dogFullDetailsResponses):
            dogResponse.images = [mapper.to(DogImageResponse).map(image) for image in dog.images]

        api_response = APIResponse(status_code=200, message=f"Queried dogs by reporter ID from the database", data={ "results": dogFullDetailsResponses, "pagination": { "total": total_count, "page": page, "page_size": page_size, "returned": len(dogFullDetailsResponses) } })
    except Exception as e:
        logger.error(f"Error while querying dogs by reporter ID from the database: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying dogs by reporter ID from the database: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=jsonable_encoder(api_response), status_code=api_response.status_code)

@router.get("/get_possible_dog_matches", response_model=APIResponse)
async def get_possible_dog_matches(dogId: Optional[int] = None, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), auth_result: dict = Security(auth.verify, scopes=['read:get_possible_dog_matches'])):
    # get from service
    try:
        # Query the database
        possibleDogMatches, total_count = dogWithImagesService.get_possible_dog_matches(dog_id=dogId, page=page, page_size=page_size)

        possibleDogMatchResponses = [mapper.to(PossibleDogMatchResponse).map(possibleDogMatch, fields_mapping={ "dog": None, "possibleMatch": None }) for possibleDogMatch in possibleDogMatches]
        for possibleDogMatch, possibleDogMatchResponse in zip(possibleDogMatches, possibleDogMatchResponses):
            possibleDogMatchResponse.dog = mapper.to(DogResponse).map(possibleDogMatch.dog, fields_mapping={ "images": [] })
            possibleDogMatchResponse.dog.images = [mapper.to(DogImageResponse).map(image) for image in possibleDogMatch.dog.images]
            possibleDogMatchResponse.possibleMatch = mapper.to(DogResponse).map(possibleDogMatch.possibleMatch, fields_mapping={ "images": [] })
            possibleDogMatchResponse.possibleMatch.images = [mapper.to(DogImageResponse).map(image) for image in possibleDogMatch.possibleMatch.images]

        api_response = APIResponse(status_code=200, message=f"Queried possible dog matches from the database", data={ "results": possibleDogMatchResponses, "pagination": { "total": total_count, "page": page, "page_size": page_size, "returned": len(possibleDogMatchResponses) } })
    except Exception as e:
        logger.error(f"Error while querying possible dog matches from the database: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying possible dog matches from the database: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=jsonable_encoder(api_response), status_code=api_response.status_code)

@router.post("/add_document", response_model=APIResponse)
async def add_document(dogRequest: DogAddRequest, auth_result: dict = Security(auth.verify)):
    # logger.info(f"Document Request: {documentRequest}")

    try:
        # Handle the image, resize it and convert it to base64 with webp format and get the content type
        # Unzip the array of tuples coming back from handle_uploaded_images
        base64Images = handle_uploaded_images(dogRequest.base64Images)

        # Create DogDocument
        # Map the DogRequest to DogDTO
        dogDTO = mapper.to(DogDTO).map(dogRequest, fields_mapping={
            "images": [], "reporterId": auth_result["sub"], "isVerified": IS_VERIFIED_FIELD_DEFAULT_VALUE
        })
        dogDTO.images = [DogImageDTO(base64Image=base64Image[0], imageContentType=base64Image[1]) for base64Image in base64Images]

        dogDTO, result = dogWithImagesService.add_dog_with_images(dogDTO)

        api_response = APIResponse(status_code=200, message=f"Added documents to the vecotrdb", data=dogDTO.model_dump(), meta=result)
    except Exception as e:
        logger.exception(f"Error while adding documents to the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while adding documents to the vecotrdb: {e}")
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

# Add an endpoint to set isVerified to True
@router.post("/verify_document", response_model=APIResponse)
async def verify_document(dogId: int, auth_result: str = Security(auth.verify, scopes=['write:verify_document'])):
    logger.info(f"Verify document: {dogId}")

    try:
        # Add the documents to the database
        logger.info(f"Verify document")
        result = vecotrDBClient.update_document("Dog", dogId, {
            "isVerified": True,
        })

        api_response = APIResponse(status_code=200, message=f"Verified document in the vecotrdb", data=result)
    except Exception as e:
        logger.error(f"Error while verifying document in the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while verifying document in the vecotrdb: {e}")
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.get("/get_schema")
async def get_schema(class_name: str):
    return vecotrDBClient.get_schema(class_name)

# reindex all dogs with images
@router.get("/reindex_all_dogs_with_images", response_model=APIResponse)
async def reindex_all_dogs_with_images(auth_result: str = Security(auth.verify, scopes=['write:reindex_all_dogs_with_images'])):
    try:
        # Reindex all dogs with images
        result = dogWithImagesService.index_all_dogs_with_images()

        api_response = APIResponse(status_code=200, message=f"Reindexed all dogs with images in the vecotrdb", meta=result)
    except Exception as e:
        logger.error(f"Error while reindexing all dogs with images in the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while reindexing all dogs with images in the vecotrdb: {e}")
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)


@router.delete("/clean_all", response_model=APIResponse)
async def clean_all(recreate_db: bool = False, auth_result: str = Security(auth.verify, scopes=['delete:clean_all'])):
    try:
        logger.info(f"Deleting all documents from the vectordb. recreate_db: {recreate_db}")

        # Delete all objects from the database
        vecotrDBClient.clean_all("Dog", dog_class_definition)

        # Recreate the database
        if recreate_db:
            db.recreate_database()
            message = "All documents were deleted from the vectordb and the database was recreated"
        else:
            message = "All documents were deleted from the vectordb"

        api_response = APIResponse(status_code=200, message=message)
    except Exception as e:
        message = f"Error deleting all documents from the vectordb"
        if recreate_db:
            message += ". The database was not recreated successfully"
        
        message += f": {e}"

        logger.error(message)

        api_response = APIResponse(status_code=500, message=message)
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

# Add an endpoint to delete dog with images by id
@router.delete("/delete_dog_by_id", response_model=APIResponse)
async def delete_dog_by_id(dogId: int, auth_result: str = Security(auth.verify, scopes=['delete:delete_dog_by_id'])):
    logger.info(f"Deleting dog with id: {dogId}")

    try:
        # Delete the dog from the database
        dogWithImagesService.delete_dog_with_images_by_id(dogId)

        api_response = APIResponse(status_code=200, message=f"Deleted dog with id {dogId} from the database")
    except Exception as e:
        logger.error(f"Error while deleting dog with id {dogId} from the database: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while deleting dog with id {dogId} from the database: {e}")
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)


@router.get("/dogs")
def get_dogs(type: Optional[DogType] = None, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), auth_result: str = Security(auth.verify, scopes=['read:dogs'])):
    results, total_count = dogWithImagesService.get_all_dogs_with_images(type=type, page=page, page_size=page_size)

    parsed_results = [
        mapper.to(DogFullDetailsResponse).map(dog, fields_mapping={
            "images": []
            })
        for dog in results
    ]
    
    for dog, dogResponse in zip(results, parsed_results):
        dogResponse.images = [mapper.to(DogImageResponse).map(image) for image in dog.images]
    
    api_response = APIResponse(status_code=HTTPStatus.OK.value, data={ "results": parsed_results, "pagination": { "total": total_count, "page": page, "page_size": page_size, "returned": len(parsed_results) } })
    
    return JSONResponse(content=jsonable_encoder(api_response), status_code=api_response.status_code)    

@router.post("/doc_resolved", response_model=APIResponse)
async def doc_resolved(foundRequest: DogResolvedRequest, auth_result: str = Security(auth.verify, scopes=['write:dog_resolved'])):
    try:
        dogWithImagesService.update_dog_is_resolved(foundRequest.dogId, True)
        api_response = APIResponse(status_code=200, message=f"Dog id {foundRequest.dogId} marked as resolved")
    except Exception as e:
        logger.error(f"Error while marking dog with id {foundRequest.dogId} as resolved: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while marking dog with id {foundRequest.dogId} as resolved: {e}")
    finally:
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

# build a predicate for the properties, breed, type, if they are not None with and_ between them
@timeit
def build_filter(dogSearchRequest: DogSearchRequest) -> Optional[Filter]:
    logger.info(f"Building the filter for queryRequest: {dogSearchRequest}")

    # create a list of predicates
    predicates = []

    # add type predicate
    if dogSearchRequest.type is not None:
        predicates.append(Predicate(["type"], "Equal", dogSearchRequest.type.value, FilterValueTypes.valueText))

    # add breed predicate
    if dogSearchRequest.breed is not None:
        predicates.append(Predicate(["breed"], "Equal", dogSearchRequest.breed, FilterValueTypes.valueText))

    # add sex predicate
    if dogSearchRequest.sex is not None:
        predicates.append(Predicate(["sex"], "Equal", dogSearchRequest.sex.value, FilterValueTypes.valueText))

    # add ageGroup predicate
    if dogSearchRequest.ageGroup is not None:
        predicates.append(Predicate(["ageGroup"], "Equal", dogSearchRequest.ageGroup.value, FilterValueTypes.valueText))

    # add size predicate
    if dogSearchRequest.size is not None:
        predicates.append(Predicate(["size"], "Equal", dogSearchRequest.size.value, FilterValueTypes.valueText))

    # add color predicate
    if dogSearchRequest.color is not None:
        predicates.append(Predicate(["color"], "Equal", dogSearchRequest.color.value, FilterValueTypes.valueText))

    # add chipNumber predicate
    if dogSearchRequest.chipNumber is not None:
        predicates.append(Predicate(["chipNumber"], "Equal", dogSearchRequest.chipNumber, FilterValueTypes.valueText))

    # add name predicate
    if dogSearchRequest.name is not None:
        predicates.append(Predicate(["name"], "Equal", dogSearchRequest.name, FilterValueTypes.valueText))

    # add location predicate
    if dogSearchRequest.location is not None:
        predicates.append(Predicate(["location"], "Equal", dogSearchRequest.location, FilterValueTypes.valueText))

    # add isVerified predicate
    # Commented out because we want to return verified and unverified dogs for now until we have a way to verify them
    # if queryRequest.isVerified is not None:
    #     predicates.append(Predicate(["isVerified"], "Equal", queryRequest.isVerified, FilterValueTypes.valueBoolean))

    # add isResolved predicate, we only want to return dogs that are not resolved
    predicates.append(Predicate(["isResolved"], "Equal", False, FilterValueTypes.valueBoolean))

    # if there are predicates return and_ between them
    if (len(predicates) > 0):
        return and_(*predicates)

    # if there are no predicates return None
    return None



def query_vector_db(dogSearchRequest: DogSearchRequest):
    # Open the image from the base64 string to PIL Image
    query_image = create_pil_images([dogSearchRequest.base64Image])[0]

    # Embed the query image
    query_embedding = embed_query(query_image, embedding_model)

    # Build the filter with conditions to query the vector db
    filter = build_filter(dogSearchRequest)

    # Query the database
    logger.info(f"Querying the database")
    results = vecotrDBClient.query(class_name="Dog", query_embedding=query_embedding, limit=dogSearchRequest.top, offset=None, filter=filter.to_dict(), properties=dogSearchRequest.return_properties)

    return results

def handle_uploaded_images(imgs):
    """
    This function takes a list of uploaded images and returns a list of resized and converted images in base64 format and their content types.

    Args:
        imgs: A list of uploaded images.

    Returns:
        A list of tuples containing the resized and converted images in base64 format and their content types.
    """
    images = []
    for img in imgs:
        # Check if file is an UploadFile image or base64 image
        if isinstance(img, UploadFile):
            # Read the image content from the uploaded file
            img_content = img.file.read()

            # Convert the image content to base64 format
            img_base64 = get_base64(img_content)
        else:
            img_base64 = img

        # Resize the image and convert it to the desired format
        img_base64, img_content_type = resize_image_and_convert_to_format(img_base64, (1024, 1024))

        # Append the resized and converted image and its content type to the list
        images.append((img_base64, img_content_type))

    # Return the list of resized and converted images and their content types
    return images
