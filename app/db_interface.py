from abc import ABC, abstractmethod
from datetime import datetime, timezone
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from config import QDRANT_HOST, QDRANT_PORT

# Abstract base class for database operations
class DatabaseInterface(ABC):
    @abstractmethod
    def save_face_data(self, id, photo_title, photo_id, face_index, age, gender, file_name, embedding):
        pass

    @abstractmethod
    def get_data(self, id=None, file_name=None, photo_id=None):
        pass

# Qdrant implementation of the database interface
class QdrantDatabase(DatabaseInterface):
    def __init__(self):
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    def save_face_data(self, id, photo_title, photo_id, face_index, age, gender, file_name, embedding):
        id = id
        metadata = {
            "photo_title": photo_title,
            "photo_id": photo_id,
            "face_index": face_index,
            "age": age,
            "gender": gender,
            "file_name": file_name,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.client.upsert(
            collection_name="face_embeddings",
            points=[
                PointStruct(
                    id=id,
                    vector=embedding,
                    payload=metadata
                )
            ]
        )

    def get_data(self, id=None, file_name=None, photo_id=None):
        filters = []
        if id:
            filters.append({"key": "id", "match": {"value": id}})
        if file_name:
            filters.append({"key": "file_name", "match": {"value": file_name}})
        if photo_id:
            filters.append({"key": "photo_id", "match": {"value": photo_id}})

        query_filter = {"must": filters} if filters else None

        results = self.client.scroll(
            collection_name="face_embeddings",
            scroll_filter=query_filter,
            limit=100
        )

        data_list = []
        for point in results[0]:
            metadata = point.payload
            data_list.append({
                "id": point.id,
                "photo_id": metadata["photo_id"],
                "photo_title": metadata["photo_title"],
                "age": metadata["age"],
                "gender": metadata["gender"],
                "face_index": metadata["face_index"],
                "file_name": metadata["file_name"],
                "created_at": metadata["created_at"]
            })
        return data_list
