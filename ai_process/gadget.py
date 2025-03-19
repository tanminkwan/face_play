from insightface.app.common import Face
import numpy as np

def to_ndarray(vector):
    # 벡터를 numpy 배열로 변환
    return np.array(vector, dtype=np.float32)

def create_face_from_vector(vector):
    # Face 객체 생성
    face = Face()
    # 벡터를 float32로 변환 후 Face 객체의 embedding 속성에 할당
    face.embedding = to_ndarray(vector)
    return face

