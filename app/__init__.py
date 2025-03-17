import insightface
from config import VECTOR_DB, BUFFALO_L_PATH, INSWAPPER_PATH
from app.file_process import load_base_image

if VECTOR_DB == "QDRANT":
    from app.database.qdrant import QdrantDatabase
    db = QdrantDatabase()  # Initialize the database interface
else:
    raise ValueError("Invalid VECTOR_DB value. Please set VECTOR_DB to 'QDRANT'.")

f_base = load_base_image("f_base.jpg")
m_base = load_base_image("m_base.jpg")

# Initialize InsightFace models
face_detector = insightface.app.FaceAnalysis(name='buffalo_l', root=BUFFALO_L_PATH)
face_detector.prepare(ctx_id=-1)

face_swapper = insightface.model_zoo.get_model(INSWAPPER_PATH)

BASE_IMAGE = [f_base, m_base]
BASE_FACE = [face_detector.get(f_base)[0],  face_detector.get(m_base)[0]]