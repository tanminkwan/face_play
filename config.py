from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_PROCESSED_IMAGE_BUCKET = os.getenv("MINIO_PROCESSED_IMAGE_BUCKET", "processed-images")

# Qdrant configuration
VECTOR_DB = os.getenv("VECTOR_DB", "QDRANT")
VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST", "localhost")
VECTOR_DB_PORT = int(os.getenv("VECTOR_DB_PORT", 6333))

# InsightFace configuration
BUFFALO_L_PATH = "C:\\"
INSWAPPER_PATH = "C:\\models\\inswapper_128.onnx"
CODEFORMER_MODEL = "CodeFormer/weights/CodeFormer/codeformer.pth"

