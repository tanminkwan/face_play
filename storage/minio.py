from minio import Minio
from minio.error import S3Error
from datetime import timedelta
from storage.storage_interface import StorageInterface
from library.gadget import to_np_image, to_image_bytes
from minio.deleteobjects import DeleteObject

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

    def load_base_images_list(self, bucket, prefixes):
        """
        주어진 prefix 리스트에 따라 이미지를 분류하여 로드합니다.

        Args:
            prefixes (list[str]): 파일명 prefix 리스트 예: ["f_", "m_", "mean_f_", "mean_m_"]

        Returns:
            dict[str, list]: prefix별 이미지 리스트 딕셔너리
        """
        files = self.list_files_in_bucket(bucket)

        result = {prefix: [] for prefix in prefixes}

        for file in files:
            img = self.load_image(bucket, file)
            for prefix in prefixes:
                if file.startswith(prefix):
                    result[prefix].append(img)
                    break  # 하나의 prefix에만 해당된다고 가정
        return result

    
    def delete_all_objects_batch(self, bucket, recursive=True):
        """
        해당 버킷의 모든 객체를 배치로 삭제합니다. (빠름)
        """
        delete_list = [DeleteObject(obj.object_name) for obj in self.client.list_objects(bucket, recursive=recursive)]

        if not delete_list:
            print("ℹ️ 버킷이 이미 비어 있습니다.")
            return

        print(f"총 {len(delete_list)} 개 객체 삭제 중...")
        for del_err in self.client.remove_objects(bucket, delete_list):
            print(f"❌ 삭제 실패: {del_err}")
        
        print("✅ 모든 객체 삭제 완료 (배치 모드)")