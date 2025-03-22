import uuid
import random
import cv2
from datetime import datetime
import numpy as np
from config import S3_IMAGE_BUCKET, RESERVED_FACES, IS_FACE_RESTORATION_ENABLED
from app import F_BASE, M_BASE, db, storage, face_detector, face_swapper, face_restorer
from library.gadget import load_and_resize_image
from database.models import FaceEmbeddings

def process_image(image, photo_title, photo_id):
    img = load_and_resize_image(image, max_width=1024, max_height=1024)
    faces = face_detector.get(img)

    if not faces:
        return {"error": "No faces detected in the image. Please upload a valid image with faces."}

    faces = sorted(faces, key=lambda face: face.bbox[0])
    file_name = f"{str(uuid.uuid4())}.jpg"

    face_data_list = []
    for i, face in enumerate(faces): # 얼굴 영역 표시
        bbox = face.bbox.astype(int)
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        text_color = (235, 45, 45)
        cv2.putText(img, f"IDX : {i}", (bbox[0] + 5, bbox[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        cv2.putText(img, f"Age: {face.age}", (bbox[0] + 5, bbox[1] + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        cv2.putText(img, f"Gender: {'M' if face.gender else 'F'}", (bbox[0] + 5, bbox[1] + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        base_image, base_face = random.choice(M_BASE if face.gender else F_BASE)
        img_face = face_swapper.get(base_image, base_face, face)

        if IS_FACE_RESTORATION_ENABLED:
            img_face = face_restorer.restore(img_face)

        id = str(uuid.uuid4())
        storage.upload_image(S3_IMAGE_BUCKET, f"{id}.jpg", image=img_face)

        face_data_list.append(FaceEmbeddings(
            id=id,
            photo_title=photo_title,
            photo_id=photo_id,
            face_index=i,
            age=float(face.age),
            gender=int(face.gender),
            file_name=file_name,
            embedding=face.embedding.tolist()
        ))

    storage.upload_image(S3_IMAGE_BUCKET, file_name, image=img)
    db.save_data_batch(face_data_list)

    return {"bucket": S3_IMAGE_BUCKET, "file_name": file_name}

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

    timestamp = datetime.fromtimestamp(last_processed_at).strftime('%Y%m%d%H%M%S')

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

def view_network_graph(id):
    me = db.get_data_by_id(id)

    if not me:
        return [], "<p style='color:red;'>No data found for the given ID.</p>"

    data = db.search_vectors_by_min_score(id, min_score=0.2, batch_size=50)
    data.append(me.copy())

    for item in data:
        if item.face_index is not None:
            item.photo_id = f"{item.photo_id}__{item.face_index}"

    main_photo_id = me.photo_id or "Me"
    if me.face_index is not None:
        main_photo_id = f"{main_photo_id}__{me.face_index}"

    return data, main_photo_id
