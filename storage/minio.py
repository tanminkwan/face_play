from minio import Minio
import io
from minio.error import S3Error
from config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_SECURE
import cv2
import numpy as np
from io import BytesIO
from datetime import timedelta
from storage.storage_interface import StorageInterface
from library.gadget import to_np_image, to_image_bytes

# Qdrant implementation of the database interface
class MinIO(StorageInterface):

    def __init__(
            self,
            endpoint=None,
            access_key=None,
            secret_key=None,
            secure=False
        ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    # upload_to_s3
    @to_image_bytes
    def upload_image(self, bucket, file_name, image_bytes, length):
        """
        The real 'upload_image' logic expects the image as bytes, plus the length.
        Thanks to the decorator, you can simply call upload_image(..., image=your_np_array)
        and get these two parameters auto-injected.
        """
        self.client.put_object(
            bucket,
            file_name,
            image_bytes,
            length=length,
            content_type='image/jpeg'
        )

    # get_presigned_url
    def get_file_url(self, bucket, file_name):
        url = self.client.presigned_get_object(bucket, file_name, 
                                        expires=timedelta(days=1))
        print(url)
        return url

    # Load base images from MinIO(or S3)
    @to_np_image
    def load_image(self, bucket, file_name):
        return self.client.get_object(bucket, file_name)

    def list_files_in_bucket(self, bucket, recursive=True):
        # bucket 내 파일 목록 조회 (recursive=True 로 모든 객체 검색)
        try:
            objects = self.client.list_objects(bucket, recursive=recursive)
            file_list = [obj.object_name for obj in objects]
            return file_list
        except S3Error as err:
            print(f"Error occurred: {err}")
            return []

    # load_base_images
    def load_base_images_list(self):

        base_bucket = "base-images"

        files = self.list_files_in_bucket(base_bucket)

        female_base_list = []
        male_base_list = []

        for file in files:
            img = self.load_image(base_bucket, file)
            if file.startswith("f_"):
                female_base_list.append(img)
            elif file.startswith("m_"):
                male_base_list.append(img)
        return female_base_list, male_base_list
