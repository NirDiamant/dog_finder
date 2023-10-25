from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.DTO.dog_dto import DogDTO

class IVectorDBClient(ABC):
    @abstractmethod
    def add_documents_batch(self, class_name: str, documents: list[DogDTO]) -> None:
        pass

    @abstractmethod
    def clean_all(self, class_name: str) -> None:
        pass

    @abstractmethod
    def delete_by_ids(self, class_name: str, field_name: str, ids: list[str]) -> None:
        pass

    @abstractmethod
    def query(self, class_name: str, query: str, query_embedding: List[float], limit: int = None, offset: int = None, filter: Dict[str, Any] = None) -> dict:
        pass

    @abstractmethod
    def create_schema(self, class_name: str, properties: dict) -> None:
        pass

    @abstractmethod
    def get_schema(self, class_name: str) -> None:
        pass

    def update_document(self, class_name, dog_id, data:Dict):
        pass