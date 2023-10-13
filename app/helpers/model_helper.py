from cachetools import LRUCache, cached
from app.MyLogger import logger
from app.helpers.helper import timeit
from cachetools import cached, LRUCache
from sentence_transformers import SentenceTransformer
import os

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