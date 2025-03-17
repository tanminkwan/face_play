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
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

# InsightFace configuration
BUFFALO_L_PATH = os.getenv("BUFFALO_L_PATH", "C:\\")
# 모델 경로 설정
CODEFORMER_MODEL = "CodeFormer/weights/CodeFormer/codeformer.pth"

