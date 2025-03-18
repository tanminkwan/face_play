from minio import Minio
import io
from minio.error import S3Error
from config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_SECURE
import cv2
import numpy as np
from io import BytesIO
from datetime import timedelta

client = Minio(
    endpoint=S3_ENDPOINT,
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_KEY,
    secure=S3_SECURE
)

def upload_to_s3(image, bucket, file_name):
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = io.BytesIO(buffer)
    client.put_object(bucket, file_name, image_bytes, \
                      length=image_bytes.getbuffer().nbytes, content_type='image/jpeg')

def get_presigned_url(bucket, file_name):
    url = client.presigned_get_object(bucket, file_name, 
                                       expires=timedelta(days=1))
    print(url)
    return url

# Load base images from MinIO(or S3)
def load_image(bucket, file_name):
    response = client.get_object("base-images", file_name)
    image_data = BytesIO(response.read())
    return cv2.imdecode(np.frombuffer(image_data.getbuffer(), np.uint8), cv2.IMREAD_COLOR)

def list_files_in_bucket(bucket, recursive=True):
    # bucket 내 파일 목록 조회 (recursive=True 로 모든 객체 검색)
    try:
        objects = client.list_objects(bucket, recursive=recursive)
        file_list = [obj.object_name for obj in objects]
        return file_list
    except S3Error as err:
        print(f"Error occurred: {err}")
        return []

def load_base_images():

    base_bucket = "base-images"

    files = list_files_in_bucket(base_bucket)

    female_base_list = []
    male_base_list = []
    for file in files:
        img = load_image(base_bucket, file)
        if file.startswith("f_"):
            female_base_list.append(img)
        elif file.startswith("m_"):
            male_base_list.append(img)
    return female_base_list, male_base_list
