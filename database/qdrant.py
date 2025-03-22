from datetime import datetime, timezone
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, Range
from database.db_interface import DatabaseInterface
from typing import List, Dict, Optional
from pydantic import BaseModel
from database.models import FaceEmbeddings

def get_result(point) -> FaceEmbeddings:
    metadata = point.payload
    return FaceEmbeddings(
        id=point.id,
        photo_id=metadata.get("photo_id"),
        photo_title=metadata.get("photo_title"),
        face_index=metadata.get("face_index"),
        age=metadata.get("age"),
        gender=metadata.get("gender"),
        file_name=metadata.get("file_name"),
        created_at=metadata.get("created_at"),
        num_people=metadata.get("num_people"),
        last_processed_at=metadata.get("last_processed_at"),
        updated_at=metadata.get("updated_at"),
        embedding=point.vector,
        score=getattr(point, 'score', None),
    )

def create_metadata(face_data: FaceEmbeddings, created_at: Optional[float] = None) -> dict:
    """
    Create metadata dictionary for a FaceData object.

    :param face_data: A FaceData object.
    :param created_at: Optional timestamp for the created_at field. Defaults to the current time.
    :return: Metadata dictionary.
    """
    return {
        "photo_title": face_data.photo_title,
        "photo_id": face_data.photo_id,
        "face_index": face_data.face_index,
        "age": face_data.age,
        "gender": face_data.gender,
        "file_name": face_data.file_name,
        "last_processed_at": face_data.last_processed_at,
        "num_people": face_data.num_people,
        "updated_at": datetime.now(timezone.utc).timestamp(),
        "created_at": created_at
    }

# Qdrant implementation of the database interface
class QdrantDatabase(DatabaseInterface):

    def __init__(self, host, port, collection_name):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name

    def save_data(self, face_data: BaseModel):
        """
        Save a single face data record into Qdrant.

        :param face_data: A FaceEmbeddings object.
        """
        metadata = create_metadata(face_data)

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=face_data.id,
                    vector=face_data.embedding,
                    payload=metadata
                )
            ]
        )

    def save_data_batch(self, data_list: List[BaseModel]):
        """
        Save multiple face data records into Qdrant in one batch.

        :param data_list: A list of FaceEmbeddings objects.
        """
        points = []
        current_time = datetime.now(timezone.utc).timestamp()

        for data in data_list:
            metadata = create_metadata(data, created_at=current_time)

            print(f"meta : {metadata}")
            points.append(
                PointStruct(
                    id=data.id,
                    vector=data.embedding,
                    payload=metadata
                )
            )

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
    def get_data(self, filters: Dict=None, with_vectors=False) -> List[BaseModel]:
        """
        Retrieve data from Qdrant based on filters.

        :param file_name: Filter by file name.
        :param photo_id: Filter by photo ID.
        :param with_vectors: Whether to include vector data.
        :return: A list of FaceEmbeddings objects.
        """
        filters = [
            {"key": key, "match": {"value": value}} for key, value in filters.items() if value
        ]

        query_filter = {"must": filters} if filters else None

        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=query_filter,
            limit=100,
            with_vectors=with_vectors  # 파라미터로 벡터 정보를 포함할지 여부 지정
        )

        return [get_result(point) for point in results[0]]

    def get_data_by_id(self, id, with_vectors=False) -> BaseModel:
        """
        Retrieve a single data record by ID.

        :param id: The ID of the record.
        :param with_vectors: Whether to include vector data.
        :return: A BaseModel object.
        """
        point = self._get_point_by_id(id, with_vectors=with_vectors)
        if not point:
            return None    
        
        return get_result(point)

    def get_data_after_date(self, date_ts: float, with_vectors=False) -> List[BaseModel]:
        """
        Retrieve data created after a specific timestamp.

        :param date_ts: The timestamp to filter data.
        :param with_vectors: Whether to include vector data.
        :return: A list of BaseModel objects.
        """
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
            collection_name=self.collection_name,
            scroll_filter=query_filter,
            limit=500,
            with_vectors=with_vectors  # 파라미터로 벡터 정보를 포함할지 여부 지정
        )

        data_list = [get_result(point) for point in results[0]]
        data_list.sort(key=lambda x: x.created_at)

        return data_list

    def _get_point_by_id(self, id, with_vectors=False):
        # Retrieve the vector by its ID
        point = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[id],
            with_vectors=with_vectors
            )

        if not point:
            print(f"No data found for ID: {id}")
            return None
        
        return point[0]

    # Function to search similar vectors in Qdrant by vector id
    def search_similar_vectors_by_id(self, id, top_n=10) -> List[BaseModel]:
        """
        Search for similar vectors in Qdrant by vector ID.

        :param id: The ID of the vector to search for.
        :param top_n: The number of similar vectors to retrieve.
        :return: A list of BaseModel objects.
        """
        point = self._get_point_by_id(id, with_vectors=True)

        query_vector = point.vector

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_n
        )

        return [get_result(point) for point in search_result]

    # Function to search vectors by minimum score threshold
    def search_vectors_by_min_score(self, id, min_score, batch_size=50) -> List[BaseModel]:
        """
        Search for vectors with a minimum score threshold.

        :param id: The ID of the vector to search for.
        :param min_score: The minimum score threshold.
        :param batch_size: The number of results to fetch per batch.
        :return: A list of FaceEmbeddings objects.
        """
        point = self._get_point_by_id(id, with_vectors=True)

        query_vector = point.vector

        offset = 0
        fetched_all = False

        data_list = []
        while not fetched_all:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=batch_size,
                offset=offset
            )

            if not search_result:
                break

            for point in search_result:

                if point.id == id:
                    continue

                if point.score < min_score:
                    fetched_all = True
                    break
                data_list.append(get_result(point))

            offset += batch_size

        return data_list