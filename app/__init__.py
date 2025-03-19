import insightface
from config import VECTOR_DB, OBJECT_STORAGE, BUFFALO_L_PATH, INSWAPPER_PATH, CODEFORMER_MODEL
from ai_process.restore_faces import FaceRestorer

if VECTOR_DB == "QDRANT":
    from database.qdrant import QdrantDatabase
    db = QdrantDatabase()  # Initialize the database interface
else:
    raise ValueError("Invalid VECTOR_DB value. Please set VECTOR_DB to 'QDRANT'.")

# Initialize InsightFace models
face_detector = insightface.app.FaceAnalysis(name='buffalo_l', root=BUFFALO_L_PATH)
face_detector.prepare(ctx_id=-1)

face_swapper = insightface.model_zoo.get_model(INSWAPPER_PATH)

face_restorer = FaceRestorer(model_path=CODEFORMER_MODEL)

if OBJECT_STORAGE == "MINIO":
    from storage.minio import MinIO
    storage = MinIO()  # Initialize the database interface
else:
    raise ValueError("Invalid Storage value.")

f_base_images, m_base_images = storage.load_base_images_list()
F_BASE = [(f, face_detector.get(f)[0]) for f in f_base_images]
M_BASE = [(m, face_detector.get(m)[0]) for m in m_base_images]