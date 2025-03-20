from datetime import datetime, timezone
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, Range
from config import VECTOR_DB_HOST, VECTOR_DB_PORT
from database.db_interface import DatabaseInterface

def get_result(point):
    metadata = point.payload
    return {
        "id": point.id,
        "photo_id": metadata.get("photo_id", None),
        "photo_title": metadata.get("photo_title", None),
        "age": metadata.get("age", None),
        "gender": metadata.get("gender", None),
        "face_index": metadata.get("face_index", None),
        "file_name": metadata.get("file_name", None),
        "created_at": metadata.get("created_at", None),
        "num_people": metadata.get("num_people", None),
        "last_processed_at": metadata.get("last_processed_at", None),
        "updated_at": metadata.get("updated_at", None),
        "embedding": point.vector,
    }

# Qdrant implementation of the database interface
class QdrantDatabase(DatabaseInterface):
    def __init__(self):
        self.client = QdrantClient(host=VECTOR_DB_HOST, port=VECTOR_DB_PORT)

    def save_face_data(self, id, photo_title, photo_id, face_index, age, gender, file_name, embedding):
        metadata = {
            "photo_title": photo_title,
            "photo_id": photo_id,
            "face_index": face_index,
            "age": age,
            "gender": gender,
            "file_name": file_name,
            "created_at": datetime.now(timezone.utc).timestamp()
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

    def save_face_data_batch(self, face_data_list):
        """
        Save multiple face data records into Qdrant in one batch.

        :param face_data_list: A list of dicts, each containing the fields:
            {
              "id": unique_id_for_the_face,
              "photo_title": ...,
              "photo_id": ...,
              "face_index": ...,
              "age": ...,
              "gender": ...,
              "file_name": ...,
              "embedding": np.ndarray or list[float]
            }
        """
        points = []
        current_time = datetime.now(timezone.utc).timestamp()

        for data in face_data_list:
            metadata = {
                "photo_title": data.get("photo_title"),
                "photo_id": data.get("photo_id"),
                "face_index": data.get("face_index"),
                "age": data.get("age"),
                "gender": data.get("gender"),
                "file_name": data.get("file_name"),
                "created_at": current_time  # or you can do per-item time
            }

            points.append(
                PointStruct(
                    id=data["id"],
                    vector=data["embedding"],
                    payload=metadata
                )
            )

        if points:
            self.client.upsert(
                collection_name="face_embeddings",
                points=points
            )
            
    def save_special_face_data(self, id, age, gender, num_people, last_processed_at, embedding):
        metadata = {
            "age": age,
            "num_people": num_people,
            "last_processed_at": last_processed_at,
            "updated_at": datetime.now(timezone.utc).timestamp()
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

    def get_data(self, file_name=None, photo_id=None, with_vectors=False):
        filters = []
        if file_name:
            filters.append({"key": "file_name", "match": {"value": file_name}})
        if photo_id:
            filters.append({"key": "photo_id", "match": {"value": photo_id}})

        query_filter = {"must": filters} if filters else None

        results = self.client.scroll(
            collection_name="face_embeddings",
            scroll_filter=query_filter,
            limit=100,
            with_vectors=with_vectors  # 파라미터로 벡터 정보를 포함할지 여부 지정
        )

        data_list = [get_result(point) for point in results[0]]

        return data_list

    def get_data_by_id(self, id, with_vectors=False):
        
        result = self.client.retrieve(
            collection_name="face_embeddings",
            ids=[id],
            with_vectors=with_vectors
        )

        if not result:
            return None
        record = result[0]
        return {
                "id": record.id,
                "age": record.payload.get("age", None),
                "gender": record.payload.get("gender", None),
                "num_people": record.payload.get("num_people", None),
                "last_processed_at": record.payload.get("last_processed_at", None),
                "updated_at": record.payload.get("updated_at", None),
                "embedding": record.vector,
            }

    def get_data_after_date_sorted(self, date_ts: float, with_vectors=False):
    
        # 숫자형 필드 "created_at"를 대상으로 Range 필터 적용
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="created_at",
                    range=Range(gt=date_ts)
                )
            ]
        )

        results = self.client.scroll(
            collection_name="face_embeddings",
            scroll_filter=query_filter,
            limit=100,
            with_vectors=with_vectors  # 파라미터로 벡터 정보를 포함할지 여부 지정
        )

        data_list = [get_result(point) for point in results[0]]
        # 정렬은 기존 ISO 8601 문자열인 "created_at" 기준으로 수행 (문자열 비교도 올바른 순서를 보장함)
        data_list.sort(key=lambda x: x.get("created_at", 0))
        return data_list

