import insightface
from config import VECTOR_DB, OBJECT_STORAGE, BUFFALO_L_PATH, INSWAPPER_PATH, CODEFORMER_MODEL
from library.restore_faces import FaceRestorer
from database import db_connection
from storage import storage_client

db = db_connection(VECTOR_DB)
storage = storage_client(OBJECT_STORAGE)

face_detector = insightface.app.FaceAnalysis(name='buffalo_l', root=BUFFALO_L_PATH)
face_detector.prepare(ctx_id=-1)

face_swapper = insightface.model_zoo.get_model(INSWAPPER_PATH)

face_restorer = FaceRestorer(model_path=CODEFORMER_MODEL)