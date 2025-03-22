from pydantic import BaseModel
from typing import List, Optional


class FaceEmbeddings(BaseModel):
    id: str
    photo_id: Optional[str] = None
    photo_title: Optional[str] = None
    age: Optional[float] = None
    gender: Optional[int] = None
    face_index: Optional[int] = None
    file_name: Optional[str] = None
    created_at: Optional[float] = None
    num_people: Optional[int] = None
    last_processed_at: Optional[float] = None
    updated_at: Optional[float] = None
    embedding: Optional[List[float]] = None
    score: Optional[float] = None