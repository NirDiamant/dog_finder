from typing import Any, Dict, List

from fastapi import HTTPException
from app.helpers.helper import timeit
from app.helpers.weaviate_helper import FilterValueTypes
from app.models.predicates import Predicate, or_
from app.services.ivectordb_client import IVectorDBClient
from app.MyLogger import logger
import weaviate

class WeaviateVectorDBClient(IVectorDBClient):
    def __init__(self, client: Any = None, url: str = None):        
        if (isinstance(client, weaviate.Client)):
            self.client = client
        else:
            # Connect to the Weaviate local instance
            self.client: weaviate.Client = weaviate.Client(url)

    @timeit
    def add_documents_batch(self, class_name: str, documents: list[dict]) -> None:
        """
        Adds a batch of documents to the vectordb.
        """
        logger.info(f"Adding {len(documents)} documents of class '{class_name}' to the vectordb")

        # Add the documents to the database

        #region: Catch batch errors and successes
        success = []
        errors = []

        def check_batch_result(results: dict):
            if results is not None:
                for result in results:
                    if "result" in result and "errors" in result["result"]:
                        if "error" in result["result"]["errors"]:
                            logger.error(result["result"])
                            errors.append({"error": result["result"]["errors"]["error"], "properties": result["properties"]})
                    else:
                        # logger.info(f"found result {result}")
                        success.append({ "properties": result["properties"] })
        #endregion

        self.client.batch.configure(
            batch_size=100,  # Specify the batch size
            num_workers=4,   # Parallelize the process
            dynamic=True,  # By default
            callback=check_batch_result
        )
        
        with self.client.batch as batch:
            documents_length = len(documents)
            # Iterate over the documents and add them to the database
            for i, data_properties in enumerate(documents):
                try:
                    uuid5 = data_properties.pop("uuid5")
                    document_embedding = data_properties.pop("document_embedding")

                    # Add the data object to the database
                    batch.add_data_object(
                        data_object=data_properties,
                        class_name=class_name,
                        uuid=uuid5,
                        vector=document_embedding
                    )
                except Exception as e:
                    logger.error(f"Error adding document [{data_properties}] {i+1} of {documents_length} to the database: {e}")
                    errors.append({"error": [{ "message": f"{e}"}], "properties": data_properties})
                    continue

        logger.info(f"Added {len(success)} documents to the database")

        if len(errors) > 0:
            logger.error(f"Errors adding documents to the database: {len(errors)}")
            logger.error(f"Errors: {errors}")

        return { "successful": len(success), "failed": len(errors), "failed_objects": errors }

    @timeit
    def delete_by_ids(self, class_name: str, field_name: str, ids: list[int]) -> None:
        """
        Deletes all documents of specific class name from the vectordb.
        """

        try:
            logger.info(f"Deleting {len(ids)} documents of '{class_name}' class from the vectordb") 

            with self.client.batch(
                num_workers=2,   # Parallelize the process
            ) as batch:
                # From documentRequest.documents, create a list of unique ids
                ids = list(set(ids))
                logger.info(f"Deleting {len(ids)} documents from the database: {ids}")

                # Create Predicate for dogs ids
                filter = or_(*[Predicate([field_name], "Equal", id, FilterValueTypes.valueNumber) for id in ids])
                logger.info(f"Delete filter: {filter.to_dict()}") 

                # Delete all the documents with the ids
                result = batch.delete_objects(
                    class_name=class_name,
                    where=filter.to_dict(),
                )

            # log info by using the result object
            logger.info(f"Results of deleted_by_ids {result['results']}") 

            return { "success": True, "results": result["results"] }
        except Exception as e:
            logger.error(f"Error deleting documents of '{class_name}' class and ids {ids} from the vectordb: {e}")
            return { "success": False, "message": f"Error deleting documents of '{class_name}' class and ids {ids} from the vectordb" }
        
    @timeit
    def clean_all(self, class_name: str, class_obj: dict) -> None:
        """
        Deletes all documents of specific class name from the vectordb.
        """
        try:
            logger.info(f"Deleting all documents of '{class_name}' class from the vectordb")

            # Get the class object
            # class_obj = self.client.schema.get(class_name)

            # Delete all objects from the database and the class
            self.client.schema.delete_class(class_name)
            
            # recreate the class
            self.create_schema(class_name, class_obj)

            logger.info(f"All documents of '{class_name}' class were deleted from the vectordb")
        except Exception as e:
            logger.exception(f"Error deleting all documents of '{class_name}' class from the vectordb: {e}")
            raise
   
    @timeit
    def query(self, class_name: str, query_embedding: List[float], limit: int = None, offset: int = None, filter: Dict[str, Any] = None, properties: List[str] = None):
        """
        Queries the model with a given query and returns best matches.
        """
        logger.info(f"Querying the vector db with query_embedding length: {len(query_embedding) if query_embedding is not None else None}, filter: {filter}, limit: {limit}, offset: {offset}, properties: {properties}")
        
        # Query the database
        logger.info(f"Querying the database")
        if query_embedding is None:
            results = (
                self.client.query
                .get(class_name, properties)
                .with_where(filter)
                .with_limit(limit)
                .with_additional(["id"])
                # .with_offset(offset)
                .do()
            )
        else:
            results = (
                self.client.query
                .get(class_name, properties)
                .with_near_vector({
                    "vector": query_embedding,
                })
                .with_where(filter)
                .with_limit(limit)
                .with_additional(["distance","id"])
                .do()
            )
        
        # Check if there are errors
        if results.get("errors"):
            logger.error(f"Error while querying the database: {results['errors']}")
            # raise exception, not http
            raise Exception(f"Error while querying the database: {results['errors']}")
        
        results = results["data"]["Get"][class_name]

        # Prepare the sources
        # Iterate over the results and add score to each object (not on _additional).
        # The score should be calulated as max(0, min(1, 1-doc._additional["distance"])
        # round the score to 4 decimals in one line
        for doc in results:
            if "_additional" in doc and "distance" in doc["_additional"]:
                doc["score"] = round(max(0, min(1, 1-doc["_additional"]["distance"])), 4)

        logger.info(f"Results: {results}")
        
        return results

    @timeit
    def create_schema(self, class_name: str, class_obj: dict):
        """
        Creates the schema of the vectordb.
        """
        try:                        
            logger.info(f"Entering create_schema")
            # wrap with try catch to avoid error if the class already exists
            try:
                if not self.client.schema.contains(class_obj):            
                    logger.info(f"Creating the schema for class '{class_name}' with schema {class_obj} in the vectordb")
                    self.client.schema.create_class(class_obj)
                    logger.info(f"Schema for class '{class_name}' was created in the vectordb")
                else:
                    logger.info(f"Schema for class '{class_name}' already exists in the vectordb")
            except Exception as e:
                logger.error(f"Error creating class: {e}")
                # Delete all objects and class from the vectordb
                logger.info("Deleting all objects and class from the vectordb")
                self.client.schema.delete_class(class_name)
                logger.info(f"Creating the {class_name} class again")
                self.client.schema.create_class(class_obj)
                logger.info(f"Schema for class '{class_name}' was created in the vectordb")
            
            return { "success": True, "message": f"Schema for class '{class_name}' with schema {class_obj} was created in the vectordb" }
        except Exception as e:
            logger.error(f"Error creating schema for class '{class_name}' with schema {class_obj} in the vectordb: {e}")
            return { "success": False, "message": f"Error creating schema for class '{class_name}' with schema {class_obj} in the vectordb: {e}" }
        
    @timeit
    def get_schema(self, class_name: str):
        return self.client.schema.get(class_name)

    @timeit
    def update_document(self, class_name, dog_id, data:Dict):
        self.client.data_object.update(
            uuid=dog_id,
            class_name=class_name,
            data_object=data,
        )