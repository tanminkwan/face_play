import uuid
import random
import logging
import cv2
from datetime import datetime, timezone
from config import S3_IMAGE_BUCKET, RESERVED_FACES, IS_FACE_RESTORATION_ENABLED, MIN_FACE_DETECTION_SCORE
from app import F_BASE, M_BASE, db, storage, face_detector
from app.common import update_images_by_face
from library.gadget import load_and_resize_image
from database.models import FaceEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

f_color = (255, 0, 255)
m_color = (0, 255, 0)
fail_color = (0, 0, 255)
text_color = (235, 145, 45)

def process_image(image, photo_title, photo_id):
    img = load_and_resize_image(image, max_width=1024, max_height=1024)
    faces = face_detector.get(img)

    if not faces:
        logger.error(f"No faces detected in the image. Please upload a valid image with faces. file_name : {image}.")
        return None
    
    faces = sorted(faces, key=lambda face: face.bbox[0])
    file_name = f"{str(uuid.uuid4())}.jpg"

    face_data_list = []
    for i, face in enumerate(faces): # 얼굴 영역 표시

        bbox = face.bbox.astype(int)

        if face.det_score < MIN_FACE_DETECTION_SCORE:
            cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), fail_color, 2)
            cv2.putText(img, "Fail", (bbox[0] + 5, bbox[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, fail_color, 2)
            continue

        color = m_color if face.gender else f_color
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.putText(img, f" {i}", (bbox[0] + 5, bbox[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        base_image, base_face = random.choice(M_BASE if face.gender else F_BASE)

        id = str(uuid.uuid4())

        update_images_by_face(
            S3_IMAGE_BUCKET, 
            f"{id}.jpg", 
            base_image, 
            face, 
            target_face=base_face,
            restore=IS_FACE_RESTORATION_ENABLED
        )

        face_data_list.append(
            FaceEmbeddings(
                id=id,
                photo_title=photo_title,
                photo_id=photo_id,
                face_index=i,
                age=float(face.age),
                gender=int(face.gender),
                file_name=file_name,
                embedding=face.embedding.tolist()
            )
        )
        
    if face_data_list:
        storage.upload_image(S3_IMAGE_BUCKET, file_name, image=img)
        db.save_data_batch(face_data_list)
    else:
        logger.error(f"No faces detected in the image.")
        return None

    return file_name

def get_image_list(photo_id=None, photo_title=None):
    results = db.get_data(filters=dict(photo_id=photo_id, photo_title=photo_title))
    images = [
        {
            "face_id": item.id,
            "photo_id": item.photo_id,
            "photo_title": item.photo_title,
            "age": item.age,
            "gender": item.gender,
            "face_index": item.face_index,
            "file_name": item.file_name,
        }
        for item in results
    ]
    return images

def get_image_url(file_name):
    return storage.get_file_url(S3_IMAGE_BUCKET, file_name)

def get_average_faces():

    m_v = db.get_data_by_id(id=RESERVED_FACES[1])
    f_v = db.get_data_by_id(id=RESERVED_FACES[0])

    f_age = f_v.age if f_v else 0.0
    m_age = m_v.age if m_v else 0.0

    f_num_people = f_v.num_people if f_v else 0.0
    m_num_people = m_v.num_people if m_v else 0.0

    f_l = f_v.last_processed_at if f_v else 0.0
    m_l = m_v.last_processed_at if m_v else 0.0

    last_processed_at = max(f_l, m_l)

    timestamp = datetime.fromtimestamp(last_processed_at, tz=timezone.utc)\
        .strftime('%Y%m%d%H%M%S')

    file_name = f"mean_face.{timestamp}.jpg"

    average_faces_info = {
        "file_name": file_name, 
        "f_age":f_age, 
        "m_age":m_age, 
        "f_num_people":f_num_people,
        "m_num_people":m_num_people
    }

    return average_faces_info

def view_network_graph(id):

    data = db.search_vectors_by_min_score(id, min_score=0.2, include_self=True, batch_size=50)

    if not data:
        return [], "<p style='color:red;'>No data found for the given ID.</p>"
    
    for item in data:
        if item.face_index is not None:
            item.photo_id = f"{item.photo_id}__{item.face_index}"
        if item.id == id:
            main_node_id = item.id

    return data, main_node_id