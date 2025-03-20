import insightface
from config import BUFFALO_L_PATH, INSWAPPER_PATH, CODEFORMER_MODEL
from libraries.restore_faces import FaceRestorer

# Initialize InsightFace models
insightface.app.FaceAnalysis(name='buffalo_l', root=BUFFALO_L_PATH).prepare(ctx_id=-1)
insightface.model_zoo.get_model(INSWAPPER_PATH)
FaceRestorer(model_path=CODEFORMER_MODEL)
