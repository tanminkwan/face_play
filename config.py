from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# S3 configuration
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_SECURE = os.getenv("S3_SECURE", "false").lower() == "true"
S3_PROCESSED_IMAGE_BUCKET = os.getenv("S3_PROCESSED_IMAGE_BUCKET", "processed-images")

# Qdrant configuration
VECTOR_DB = os.getenv("VECTOR_DB", "QDRANT")
VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST", "localhost")
VECTOR_DB_PORT = int(os.getenv("VECTOR_DB_PORT", 6333))

# InsightFace configuration
BUFFALO_L_PATH = "C:\\"
INSWAPPER_PATH = "C:\\models\\inswapper_128.onnx"
CODEFORMER_MODEL = "C:/GitHub/v-face_play/CodeFormer/weights/CodeFormer/codeformer.pth"

