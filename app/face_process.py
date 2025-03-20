import uuid
import random
import cv2
import numpy as np
from config import S3_IMAGE_BUCKET, RESERVED_FACES, IS_FACE_RESTORATION_ENABLED
from app import F_BASE, M_BASE, db, storage, face_detector, face_swapper, face_restorer
from library.gadget import load_and_resize_image

def process_image(image, photo_title, photo_id):

    img = load_and_resize_image(image, max_width=1024, max_height=1024)
    
    faces = face_detector.get(img)
    
    # If no faces are detected, return an error message
    if not faces:
        return {"error": "No faces detected in the image. Please upload a valid image with faces."}

    faces = sorted(faces, key=lambda face: face.bbox[0])
    file_name = f"{str(uuid.uuid4())}.jpg"

    face_data_list = []
    for i, face in enumerate(faces):
        # 얼굴 영역 표시
        bbox = face.bbox.astype(int)
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        # Draw labels
        text_color = (235, 45, 45)
        cv2.putText(img, f"IDX : {i}", (bbox[0] + 5, bbox[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        cv2.putText(img, f"Age: {face.age}", (bbox[0] + 5, bbox[1] + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        cv2.putText(img, f"Gender: {'M' if face.gender else 'F'}", (bbox[0] + 5, bbox[1] + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        # Save face image to MinIO : Mail (1), Female(0)
        base_image, base_face = random.choice(M_BASE if face.gender else F_BASE)

        img_face = face_swapper.get(base_image, base_face, face)

        if IS_FACE_RESTORATION_ENABLED:
            img_face = face_restorer.restore(img_face)

        id = str(uuid.uuid4())

        storage.upload_image(S3_IMAGE_BUCKET, f"{id}.jpg", image=img_face)

        face_data_list.append(dict(
            id=id,
            photo_title=photo_title,
            photo_id=photo_id,
            face_index=i,
            age=float(face.age),
            gender=int(face.gender),
            file_name=file_name,
            embedding=face.embedding.tolist()
        ))

    # Save processed image to MinIO
    storage.upload_image(S3_IMAGE_BUCKET, file_name, image=img)
    # Save face data to Qdrant
    db.save_face_data_batch(face_data_list)

    return {"bucket": S3_IMAGE_BUCKET, "file_name": file_name}

def get_image_list(file_name=None, photo_id=None):
    results = db.get_data(file_name=file_name, photo_id=photo_id)
    images = [
        {
            "id": item["id"],
            "file_name": item["file_name"],
            "photo_id": item["photo_id"],
            "photo_title": item["photo_title"],
            "age": item["age"],
            "gender": item["gender"],
            "face_index": item["face_index"],
        }
        for item in results
    ]
    return images

def get_average_faces():

    m_v = db.get_data_by_id(id=RESERVED_FACES[1])
    f_v = db.get_data_by_id(id=RESERVED_FACES[0])

    f_age = f_v["age"] if f_v else 0.0
    m_age = m_v["age"] if m_v else 0.0

    f_num_people = f_v["num_people"] if f_v else 0.0
    m_num_people = m_v["num_people"] if m_v else 0.0

    f_l = f_v["last_processed_at"] if f_v else 0.0
    m_l = m_v["last_processed_at"] if m_v else 0.0
    last_processed_at = max(f_l, m_l)

    # 현재 UTC 타임스탬프 문자열 생성
    timestamp = last_processed_at.strftime('%Y%m%d%H%M%S')

    # 새 파일명 생성
    file_name = f"mean_face.{timestamp}.jpg"

    average_faces_info = {
        "bucket": S3_IMAGE_BUCKET, 
        "file_name": file_name, 
        "f_age":f_age, 
        "m_age":m_age, 
        "f_num_people":f_num_people,
        "m_num_people":m_num_people
    }

    return average_faces_info