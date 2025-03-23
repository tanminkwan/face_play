import insightface
from config import \
    VECTOR_DB, VECTOR_DB_HOST, VECTOR_DB_PORT, \
    OBJECT_STORAGE, S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_SECURE, \
    BUFFALO_L_PATH, INSWAPPER_PATH, CODEFORMER_MODEL
from library.restore_faces import FaceRestorer
from database import db_connection
from storage import storage_client

db = db_connection(
    VECTOR_DB, 
    host=VECTOR_DB_HOST, 
    port=VECTOR_DB_PORT
    )

storage = storage_client(
    OBJECT_STORAGE,
    endpoint=S3_ENDPOINT,
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_KEY,
    secure=S3_SECURE
    )

face_detector = insightface.app.FaceAnalysis(name='buffalo_l', root=BUFFALO_L_PATH)
face_detector.prepare(ctx_id=-1)

face_swapper = insightface.model_zoo.get_model(INSWAPPER_PATH)

face_restorer = FaceRestorer(model_path=CODEFORMER_MODEL)

images = storage.load_base_images_list("base-images", ["m_", "f_"])
F_BASE = [(f, face_detector.get(f)[0]) for f in images["f_"]]
M_BASE = [(m, face_detector.get(m)[0]) for m in images["m_"]]