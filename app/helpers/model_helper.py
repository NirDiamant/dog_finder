from cachetools import LRUCache, cached
from app.MyLogger import logger
from app.helpers.helper import timeit
from cachetools import cached, LRUCache
from sentence_transformers import SentenceTransformer
import os
from app.model_optimization.features_extractor import FeatureExtractor
from app.model_optimization.remove_background import process_pil_image, process_pil_image_YOLO

@timeit
def create_embedding_model():
    logger.info("Creating embedding model")

    embedding_model_name = os.environ.get('EMBEDDING_MODEL_NAME', "dino")

    if embedding_model_name == "sentence-transformers":
        embedding_model = create_sentence_transformer_embedding_model(), create_sentence_transformer_embedding_model.cache_info()
    elif embedding_model_name == "dino":
        embedding_model = create_dino_embedding_model(), create_dino_embedding_model.cache_info()
    
    logger.info("Returning SentenceTransformer embedding model")

    return embedding_model

@cached(cache=LRUCache(maxsize=8), info=True)
def create_sentence_transformer_embedding_model():
    embedding_model_name = os.environ.get('SENTENCE_TRANSFORMER_EMBEDDING_MODEL_NAME', "clip-ViT-B-32")
        
    logger.info(f"Creating SentenceTransformer embedding model with model name: {embedding_model_name}")
        
    embedding_model = SentenceTransformer(model_name_or_path=embedding_model_name)

    return embedding_model

@cached(cache=LRUCache(maxsize=8), info=True)
def create_dino_embedding_model():
    logger.info("Creating DINO embedding model")

    embedding_model = FeatureExtractor()

    return embedding_model


@timeit
def embed_documents(documents, embedding_model, image_segmentation_model):
    logger.info(f"Embedding documents {len(documents)} documents: '{documents}'")

    # Remove background from images
    # masked_documents = [process_pil_image(pil_image=document, image_segmentation_model=image_segmentation_model) for document in documents]
    masked_documents = [process_pil_image_YOLO(pil_image=document, image_segmentation_model=image_segmentation_model) for document in documents]
    
    # Embed the documents
    documents_embedding = embedding_model.encode(masked_documents)
    logger.info(f"Documents embedding: {documents_embedding} Dimensions: [{len(documents_embedding)},{len(documents_embedding[0])}]")

    return documents_embedding

@timeit
def embed_query(query_image, embedding_model, image_segmentation_model):
    logger.info(f"Embedding query: '{query_image}'")

    # masked_query_image = process_pil_image(pil_image=query_image, image_segmentation_model=image_segmentation_model)
    masked_query_image = process_pil_image_YOLO(pil_image=query_image, image_segmentation_model=image_segmentation_model)

    # Embed the query
    query_embedding = embedding_model.encode(masked_query_image)
    logger.info(f"Query embedding: {query_embedding} Dimensions: [{len(query_embedding)}]")

    return query_embedding