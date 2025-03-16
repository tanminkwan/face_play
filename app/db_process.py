import uuid
from config import QDRANT_HOST, QDRANT_PORT
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT
)

def save_face_data(photo_title, photo_id, face_index, age, gender, embedding):
    # UUID를 사용하여 고유 ID 생성
    generated_id = str(uuid.uuid4())

    # Convert numpy types to standard Python types
    metadata = {
        "photo_title": photo_title,
        "photo_id": photo_id,
        "face_index": face_index,
        "age": age,
        "gender": gender
    }

    client.upsert(
        collection_name="face_embeddings",
        points=[
            PointStruct(
                id=generated_id,
                vector=embedding,
                payload=metadata
            )
        ]
    )

def get_photo_metadata():
    results = client.scroll(
        collection_name="face_embeddings",
        scroll_filter=None,
        limit=100
    )
    metadata_list = []
    for point in results[0]:
        metadata = point.payload
        metadata_list.append({
            "photo_id": metadata["photo_id"],
            "photo_title": metadata["photo_title"],
            "age": metadata["age"],
            "gender": metadata["gender"],
            "face_index": metadata["face_index"],
            "bucket_file": f"{metadata['bucket']}/{metadata['file_name']}"
        })
    return metadata_list
