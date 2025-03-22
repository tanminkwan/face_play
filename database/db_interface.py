from abc import ABC, abstractmethod
from typing import List, Dict
from pydantic import BaseModel

# Abstract base class for database operations
class DatabaseInterface(ABC):
    @abstractmethod
    def save_data(self, face_data: BaseModel):
        """
        Save a single face data record into the database.
        """
        pass

    @abstractmethod
    def save_data_batch(self, data_list: List[BaseModel]):
        """
        Save multiple face data records into the database in one batch.
        """
        pass

    @abstractmethod
    def get_data(self, filters:Dict = None, with_vectors: bool = False) -> List[BaseModel]:
        """
        Retrieve data from the database based on filters.
        """
        pass

    @abstractmethod
    def get_data_by_id(self, id: str, with_vectors: bool = False) -> BaseModel:
        """
        Retrieve a single data record by ID.
        """
        pass

    @abstractmethod
    def get_data_after_date(self, date_ts: float, with_vectors: bool = False) -> List[BaseModel]:
        """
        Retrieve data created after a specific timestamp.
        """
        pass

    @abstractmethod
    def search_similar_vectors_by_id(self, id: str, top_n: int = 10) -> List[BaseModel]:
        """
        Search for similar vectors in the database by vector ID.
        """
        pass

    @abstractmethod
    def search_vectors_by_min_score(self, id: str, min_score: float, batch_size: int = 50) -> List[BaseModel]:
        """
        Search for vectors with a minimum score threshold.
        """
        pass