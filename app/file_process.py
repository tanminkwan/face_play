from minio import Minio
import io
from minio.error import S3Error
from config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_SECURE
import cv2
from datetime import timedelta
from app.db_process import get_photo_metadata

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

def get_image_list():
    return get_photo_metadata()
