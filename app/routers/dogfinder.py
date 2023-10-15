import hashlib
import uuid
from typing import Any, List, Optional
from app.MyLogger import logger
from app.models.api_response import APIResponse
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.helpers.model_helper import create_embedding_model
from app.helpers.helper import timeit
from app.helpers.weaviate_helper import FilterValueTypes
from app.models import DogDocument
from weaviate.util import generate_uuid5
from app.models.predicates import Predicate, Filter, and_, or_
# from sentence_transformers import SentenceTransformer
import os
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO
import base64
from app.services.ivectordb_client import IVectorDBClient
from app.services.weaviate_vectordb_client import WeaviateVectorDBClient

logger.info("Starting up the dogfinder router")

router = APIRouter(prefix="/dogfinder")
vecotrDBClient: IVectorDBClient

IS_FOUND_FIELD = "isFound"
UUID_FIELD = "uuid5"
DOG_ID_FIELD = "dogId"

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
                "name": "type",
                "dataType": ["text"],
                "description": "Found Or Lost"
            },
            {
                "name": "filename",
                "dataType": ["text"],
                "description": "Uploaded filename"
            },
            {
                "name": "image",
                "dataType": ["blob"],
                "description": "Image"
            },
            {
                "name": IS_FOUND_FIELD,
                "dataType": ["boolean"],
                "description": "was the dog found?"
            },
            {
                "name": DOG_ID_FIELD,
                "dataType": ["text"],
                "description": "id of the dog"
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
            }
        ]
    }

def hash_image(image):
    return hashlib.md5(image.encode()).hexdigest()

def generate_dog_id():
    return str(uuid.uuid4())


# This is the request model for the add_documents endpoint
class DocumentRequest(BaseModel):
    documents: List[DogDocument]

# This is the request model for the query endpoint
class QueryRequest(BaseModel):
    type: str
    image: str
    breed: Optional[str] = None
    top: int = 10
    return_properties: Optional[List[str]] = ["type", "breed", "filename", "image", IS_FOUND_FIELD, DOG_ID_FIELD, "contactName", "contactPhone", "contactEmail", "contactAddress"]

class DogFoundRequest(BaseModel):
    dogId: str



@router.on_event("startup")
async def startup_event():
    """
    Load all the necessary models and data once the server starts.
    """
    global vecotrDBClient

    # Create the vector db client, connecting to the weaviate instance
    vecotrDBClient = WeaviateVectorDBClient(url=f"http://{os.getenv('WEAVIATE_HOST', 'localhost')}:{os.getenv('WEAVIATE_PORT', '8080')}")

    # Create the schema
    vecotrDBClient.create_schema(class_name="Dog", class_obj=dog_class_definition)


@router.post("/query/", response_model=APIResponse)
async def query(query: Optional[str] = Form(None), type: str = Form(...), breed: Optional[str] = Form(None), img: UploadFile = File(...), top: int = Form(10)):
    try:
        # Get file from UploadFile and convert it to Base64Str
        img_content = img.file.read()
        img_base64 = get_base64(img_content)
        query_image = create_pil_image(img_base64)

        # Create QueryRequest
        queryRequest = QueryRequest(type=type, breed=breed, image=img_base64, top=top)

        # Create the embedding model
        logger.info(f"Creating embedding model")
        embedding_model, cache_info = create_embedding_model()

        # Embed the query image
        query_embedding = embed_query(query_image, embedding_model)

        # Build the filter with conditions to query the vector db
        filter = build_filter(queryRequest)

        # Query the database
        logger.info(f"Querying the database")
        results = vecotrDBClient.query(class_name="Dog", query=query, query_embedding=query_embedding, limit=queryRequest.top, offset=None, filter=filter.to_dict(), properties=queryRequest.return_properties)

        api_response = APIResponse(status_code=200, message=f"Queried {len(results)} results from the vecotrdb", data={ "total": len(results), "results": results })
    except Exception as e:
        logger.error(f"Error while querying the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while querying the vecotrdb: {e}", data={ "total": 0, "results": [] })
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.post("/add_document", response_model=APIResponse)
async def add_document(type: str = Form(...), breed: Optional[str] = Form(None), img: UploadFile = File(...), contactName: Optional[str] = Form(None), contactPhone: Optional[str] = Form(None), contactEmail: Optional[str] = Form(None), contactAddress: Optional[str] = Form(None)):
    # logger.info(f"Document Request: {documentRequest}")

    try:
        # Add the document to the database
        documents = []

        # Get file from UploadFile and convert it to Base64Str
        img_content = img.file.read()
        img_base64 = get_base64(img_content)
        document_image = create_pil_image(img_base64)

        # Create DogDocument
        dogDocument = DogDocument(type=type, breed=breed, image=img_base64, filename=img.filename, contactName=contactName, contactPhone=contactPhone, contactEmail=contactEmail, contactAddress=contactAddress)

        # Create the embedding model
        logger.info(f"Creating embedding model")
        embedding_model, cache_info = create_embedding_model()

        # Embed the document image
        dog_embedding = embed_query(document_image, embedding_model)

        try:
            # Create the data object
            data_properties = create_data_properties(dogDocument, generate_dog_id())
            # Create a uuid based on the filename
            data_properties[UUID_FIELD] = generate_uuid5({"breed": dogDocument.breed, "type": dogDocument.type,"imageHash":hash_image(dogDocument.image)})
            data_properties["document_embedding"] = dog_embedding

            documents.append(data_properties)
        except Exception as e:
            logger.error(f"Error while creating data_properties for document: {e}")

        # Add the documents to the database
        logger.info(f"Add documents batch")
        result = vecotrDBClient.add_documents_batch("Dog", documents)

        api_response = APIResponse(status_code=200, message=f"Added documents to the vecotrdb", data=result)
    except Exception as e:
        logger.error(f"Error while adding documents to the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while adding documents to the vecotrdb: {e}")
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.post("/add_documents", response_model=APIResponse)
async def add_documents(documentRequest: DocumentRequest):
    logger.info(f"Document Request: {documentRequest}")

    try:
        # Add the documents to the database
        documents_length = len(documentRequest.documents)
        logger.info(f"Adding {documents_length} documents")
        documents = []

        # Create the embedding model
        logger.info(f"Creating embedding model")
        embedding_model, cache_info = create_embedding_model()

        # Embed the documents images
        embedding_results = embed_documents([create_pil_image(document.image) for document in documentRequest.documents], embedding_model)
        request_dog_id = generate_dog_id()

        # Iterate over the documents and add them to the database
        for i, document in enumerate(documentRequest.documents):
            try:
                # Create the data object
                data_properties = create_data_properties(document, request_dog_id)

                # Create a uuid based on the filename
                data_properties[UUID_FIELD] = generate_uuid5({"breed": document.breed, "type": document.type, "imageHash": hash_image(document.image)})

                # Embed the document
                logger.info(f"Setting Embedding document [{document.filename}] {i+1} of {documents_length}")
                data_properties["document_embedding"] = embedding_results[i]


                documents.append(data_properties)
            except Exception as e:
                logger.error(f"Error while creating data_properties for document [{document.filename}] {i+1} of {documents_length}: {e}")

        # Add the documents to the database
        logger.info(f"Add documents batch")
        result = vecotrDBClient.add_documents_batch("Dog", documents)

        api_response = APIResponse(status_code=200, message=f"Added documents to the vecotrdb", data=result)
    except Exception as e:
        logger.error(f"Error while adding documents to the vecotrdb: {e}")
        api_response = APIResponse(status_code=500, message=f"Error while adding documents to the vecotrdb: {e}")
    finally:
        # return back a json response and set the status code to api_response.status_code
        return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.get("/get_schema")
async def get_schema(class_name: str):
    return vecotrDBClient.get_schema(class_name)

@router.delete("/clean_all", response_model=APIResponse)
async def clean_all():
    logger.info("Deleting all documents from the vectordb")

    # Delete all objects from the database
    result = vecotrDBClient.clean_all("Dog", dog_class_definition)

    # If result.success is False return 500 with result.message
    if result.get("success") is False:
        api_response = APIResponse(status_code=500, message=f"Error deleting all documents from the vectordb: {result.get('message')}")
    else:
        api_response = APIResponse(status_code=200, message=f"All documents were deleted from the vectordb")

    # return back a json response and set the status code to api_response.status_code
    return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

@router.post("/doc_found", response_model=APIResponse)
async def doc_found(foundRequest: DogFoundRequest):

    vecotrDBClient.update_document("Dog", foundRequest.dogId,{
                "isFound": True,
            })

    api_response = APIResponse(status_code=200, message=f"found dog marked", data={})
    # return back a json response and set the status code to api_response.status_code
    return JSONResponse(content=api_response.to_dict(), status_code=api_response.status_code)

# build a predicate for the properties, breed, type, if they are not None with and_ between them
@timeit
def build_filter(queryRequest: QueryRequest) -> Optional[Filter]:
    logger.info(f"Building the filter for queryRequest: {queryRequest}")

    # create a list of predicates
    predicates = []

    # add breed predicate
    if queryRequest.breed is not None:
        predicates.append(Predicate(["breed"], "Equal", queryRequest.breed, FilterValueTypes.valueText))

    # add type predicate
    if queryRequest.type is not None:
        predicates.append(Predicate(["type"], "Equal", queryRequest.type, FilterValueTypes.valueText))

    predicates.append(Predicate(["isFound"], "Equal", False, FilterValueTypes.valueBoolean))

    # if there are predicates return and_ between them
    if (len(predicates) > 0):
        return and_(*predicates)

    # if there are no predicates return None
    return None

def create_data_properties(document: DogDocument, dog_id:str) -> dict[str, Any]:
    # Transform document to dictionary
    data_properties = document.model_dump()

    # Transform datetime objects to string
    for key, val in data_properties.items():
        if isinstance(val, datetime):
            data_properties[key.lower()] = val.strftime("%Y-%m-%dT%H:%M:%S.%SZ") if val else None

    data_properties[DOG_ID_FIELD] = dog_id

    return data_properties

def get_base64(img_content):
    img_base64 = base64.b64encode(img_content).decode('utf-8')
    logger.debug(f"Image base64: {img_base64}")

    return img_base64

def create_pil_image(img_base64):
    # Open the image from the base64 string to PIL Image
    query_image = Image.open(BytesIO(base64.b64decode(img_base64)))

    return query_image

@timeit
def embed_documents(documents, embedding_model):
    logger.info(f"Embedding documents {len(documents)} documents: '{documents}'")

    if (embedding_model is not None):
        texts_embedding = embedding_model.encode(documents)
        # log texts_embedding 2 dimensions lenght of the first element as well
        logger.info(f"Texts embedding: {texts_embedding} Dimensions: [{len(texts_embedding)},{len(texts_embedding[0])}]")
    else:
        # create a random embedding
        texts_embedding = [[0.1] * 512] * len(documents)

    return texts_embedding

@timeit
def embed_query(query, embedding_model):
    logger.info(f"Embedding query: '{query}'")

    if (embedding_model is not None):
        query_embedding = embedding_model.encode(query)
    else:
        # create a random embedding
        query_embedding = [0.1] * 512

    return query_embedding

def _json_serializable(value: Any) -> Any:
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return value
