from insightface.app.common import Face
import numpy as np
import numpy.typing as npt
from typing import Union, Optional, List
import cv2
from io import BytesIO
from functools import wraps

def update_mean_vector(
        mean_vector: Optional[Union[float, List[float], npt.NDArray[np.float32]]], 
        mean_weight: Union[int, float], 
        new_vectors: Union[List[List[float]], npt.NDArray[np.float32]],
        )->npt.NDArray[np.float32]:
    """
    기존 평균 벡터와 새 벡터들의 평균을 가중치로 업데이트합니다.

    Parameters:
        mean_vector (array-like): 기존 평균 벡터.
        mean_weight (int): 평균의 샘플값.
        new_vectors (array-like): 새 벡터 목록.

    Returns:
        numpy.ndarray: 업데이트된 평균 벡터.
    """
    if not new_vectors:
        return mean_vector

    new_vectors = np.asarray(new_vectors, dtype=np.float32)
    new_mean_vector = np.mean(new_vectors, axis=0)
    new_weight = len(new_vectors)

    if not mean_vector:
        return new_mean_vector

    mean_vector = np.asarray(mean_vector, dtype=np.float32)

    if mean_vector.size == 0:
        return new_mean_vector

    norm_mean_weight = mean_weight / (mean_weight + new_weight)
    norm_new_weight = new_weight / (mean_weight + new_weight)

    new_mean_vector = (mean_vector * norm_mean_weight) + (new_mean_vector * norm_new_weight)

    return new_mean_vector

def create_face_from_vector(vector):
    # Face 객체 생성
    face = Face()
    # 벡터를 float32로 변환 후 Face 객체의 embedding 속성에 할당
    face.embedding = np.asarray(vector, dtype=np.float32)
    return face

def to_np_image(func):
    """
    Decorator that takes a function returning an S3/MinIO get_object response (or bytes),
    reads and decodes it, and returns a numpy array suitable for OpenCV processing.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function, which should return an object with .read() or raw bytes
        data = func(*args, **kwargs)

        # If data is an S3/MinIO response object, read from it:
        # Adjust this logic if your client returns raw bytes directly (e.g., data is already bytes).
        image_data = BytesIO(data.read())

        # Decode buffer as an image using OpenCV
        np_array = cv2.imdecode(np.frombuffer(image_data.getbuffer(), np.uint8), cv2.IMREAD_COLOR)
        return np_array

    return wrapper

def to_image_bytes(func):
    """
    Decorator that:
    1) Expects an argument named 'image' (an OpenCV np.ndarray).
    2) Encodes it as .jpg bytes.
    3) Injects 'image_bytes' and 'length' arguments into the wrapped function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # If an 'image' argument is found, transform it
        if 'image' in kwargs and kwargs['image'] is not None:
            np_image = kwargs.pop('image')  # remove 'image' from kwargs
            success, buffer = cv2.imencode('.jpg', np_image)
            if not success:
                raise ValueError("Failed to encode image as JPG.")

            image_bytes = BytesIO(buffer)
            length = image_bytes.getbuffer().nbytes
            
            # Inject the new arguments
            kwargs['image_bytes'] = image_bytes
            kwargs['length'] = length

        # Call the original function with updated kwargs
        return func(*args, **kwargs)
    return wrapper

def load_and_resize_image(image_path: str, max_width: int = None, max_height: int = None) -> np.ndarray:
    """
    Reads an image from a file path and optionally resizes it if it exceeds 
    the given max_width or max_height while preserving aspect ratio.

    :param image_path: File path to the image.
    :param max_width:  Maximum allowed width. If the image is wider, it will be resized down.
    :param max_height: Maximum allowed height. If the image is taller, it will be resized down.
    :return:           The loaded (and possibly resized) image as a NumPy array.
    """
    # 1) Read the raw bytes
    with open(image_path, "rb") as f:
        file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
    
    # 2) Decode to an OpenCV image (BGR format)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not decode image from {image_path}")

    # 3) Determine current size
    height, width = img.shape[:2]

    # 4) Calculate scale factors for width and height based on the constraints
    scale_w = 1.0
    scale_h = 1.0

    if max_width is not None and width > max_width:
        scale_w = max_width / float(width)

    if max_height is not None and height > max_height:
        scale_h = max_height / float(height)

    # Choose the smaller of the two scale factors (so we don't exceed either dimension).
    scale = min(scale_w, scale_h)

    # 5) Resize only if we actually need to scale down
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    return img

def singleton(cls):
    """
    A decorator that transforms a class into a singleton:
    Only one instance of the class will ever be created.
    """
    _instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance
