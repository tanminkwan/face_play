from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np

class StorageInterface(ABC):

    @abstractmethod
    def upload_image(self, bucket: str, file_name: str, image: np.ndarray) -> None:
        """
        이미지 데이터를 S3에 업로드합니다.
        """
        pass

    @abstractmethod
    def get_file_url(self, bucket: str, file_name: str) -> str:
        """
        S3 객체에 대한 presigned URL을 반환합니다.
        """
        pass

    @abstractmethod
    def load_image(self, bucket: str, file_name: str) -> np.ndarray:
        """
        S3에서 이미지 파일을 읽어 cv2 이미지 객체(NumPy 배열)로 반환합니다.
        """
        pass

    @abstractmethod
    def list_files_in_bucket(self, bucket: str, recursive: bool = True) -> List[str]:
        """
        버킷 내의 파일 목록을 문자열 리스트로 반환합니다.
        """
        pass

    @abstractmethod
    def load_base_images_list(self) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        기본 이미지들을 로드하여, 여성 이미지 리스트와 남성 이미지 리스트의 튜플로 반환합니다.
        """
        pass
