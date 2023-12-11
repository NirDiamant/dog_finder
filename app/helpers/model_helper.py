from cachetools import LRUCache, cached
from app.MyLogger import logger
from app.helpers.helper import timeit
from cachetools import cached, LRUCache
from sentence_transformers import SentenceTransformer
import os

from app.model_optimization.remove_background import process_pil_image

@timeit
def create_embedding_model():
    embedding_model = create_sentence_transformer_embedding_model(), create_sentence_transformer_embedding_model.cache_info()
    logger.info("Returning SentenceTransformer embedding model")

    return embedding_model

@cached(cache=LRUCache(maxsize=8), info=True)
def create_sentence_transformer_embedding_model():
    embedding_model_name = os.environ.get('SENTENCE_TRANSFORMER_EMBEDDING_MODEL_NAME', "clip-ViT-B-32")
        
    logger.info(f"Creating SentenceTransformer embedding model with model name: {embedding_model_name}")
        
    embedding = SentenceTransformer(model_name_or_path=embedding_model_name)

    return embedding

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
def embed_query(query_image, embedding_model, image_model):
    logger.info(f"Embedding query: '{query_image}'")

    masked_query_image = process_pil_image(image_pil=query_image, image_model=image_model)

    if (embedding_model is not None):
        query_embedding = embedding_model.encode(masked_query_image)
    else:
        # create a random embedding
        query_embedding = [0.1] * 512

    return query_embedding