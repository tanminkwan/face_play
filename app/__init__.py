import insightface
from config import VECTOR_DB, BUFFALO_L_PATH, INSWAPPER_PATH, CODEFORMER_MODEL
from app.ai_process.restore_faces import FaceRestorer
from app.file_process import load_base_images, list_files_in_bucket

if VECTOR_DB == "QDRANT":
    from app.database.qdrant import QdrantDatabase
    db = QdrantDatabase()  # Initialize the database interface
else:
    raise ValueError("Invalid VECTOR_DB value. Please set VECTOR_DB to 'QDRANT'.")

# Initialize InsightFace models
face_detector = insightface.app.FaceAnalysis(name='buffalo_l', root=BUFFALO_L_PATH)
face_detector.prepare(ctx_id=-1)

face_swapper = insightface.model_zoo.get_model(INSWAPPER_PATH)

face_restorer = FaceRestorer(model_path=CODEFORMER_MODEL)

f_base_images, m_base_images = load_base_images()
F_BASE = [(f, face_detector.get(f)[0]) for f in f_base_images]
M_BASE = [(m, face_detector.get(m)[0]) for m in m_base_images]