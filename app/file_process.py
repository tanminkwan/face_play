from minio import Minio
import io
from minio.error import S3Error
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE
import cv2
import numpy as np
from io import BytesIO
from datetime import timedelta

client = Minio(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def upload_to_minio(image, bucket, file_name):
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = io.BytesIO(buffer)
    client.put_object(bucket, file_name, image_bytes, \
                      length=image_bytes.getbuffer().nbytes, content_type='image/jpeg')

def get_presigned_url(bucket, file_name):
    url = client.presigned_get_object(bucket, file_name, 
                                       expires=timedelta(days=1))
    print(url)
    return url

# Load base images from MinIO
def load_base_image(file_name):
    response = client.get_object("base-images", file_name)
    image_data = BytesIO(response.read())
    return cv2.imdecode(np.frombuffer(image_data.getbuffer(), np.uint8), cv2.IMREAD_COLOR)
