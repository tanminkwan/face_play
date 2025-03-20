from insightface.app.common import Face
import numpy as np
import cv2
from io import BytesIO
from functools import wraps

def to_ndarray(vector):
    # 벡터를 numpy 배열로 변환
    return np.array(vector, dtype=np.float32)

def create_face_from_vector(vector):
    # Face 객체 생성
    face = Face()
    # 벡터를 float32로 변환 후 Face 객체의 embedding 속성에 할당
    face.embedding = to_ndarray(vector)
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
