from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# S3 configuration
OBJECT_STORAGE = os.getenv("OBJECT_STORAGE", "MINIO")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_SECURE = os.getenv("S3_SECURE", "false").lower() == "true"
S3_IMAGE_BUCKET = os.getenv("S3_IMAGE_BUCKET", "processed-images")

# Qdrant configuration
VECTOR_DB = os.getenv("VECTOR_DB", "QDRANT")
VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST", "localhost")
VECTOR_DB_PORT = int(os.getenv("VECTOR_DB_PORT", 6333))

RESERVED_FACES = [
    "00000000-0000-0000-0000-000000000000",
    "11111111-1111-1111-1111-111111111111"
    ]

# AI Option
IS_FACE_RESTORATION_ENABLED = os.getenv("ENABLE_FACE_RESTORATION", "false").lower() == "true"

# AI Model configuration
BUFFALO_L_PATH = "C:\\"
INSWAPPER_PATH = "C:\\models\\inswapper_128.onnx"
CODEFORMER_MODEL = "C:\\models\\codeformer-v0.1.0.pth"