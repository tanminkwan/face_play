import uuid
import cv2
import numpy as np
from config import S3_PROCESSED_IMAGE_BUCKET
from app import BASE_IMAGE, BASE_FACE, db, face_detector, face_swapper, face_restorer

def process_image(image, photo_title, photo_id, upload_to_s3_func):

    with open(image, "rb") as f:
        file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    faces = face_detector.get(img)
    
    # If no faces are detected, return an error message
    if not faces:
        return {"error": "No faces detected in the image. Please upload a valid image with faces."}

    faces = sorted(faces, key=lambda face: face.bbox[0])
    file_name = f"{str(uuid.uuid4())}.jpg"

    for i, face in enumerate(faces):
        # 얼굴 영역 표시
        bbox = face.bbox.astype(int)
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        # Draw labels
        text_color = (235, 45, 45)
        cv2.putText(img, f"IDX : {i}", (bbox[0] + 5, bbox[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        cv2.putText(img, f"Age: {face.age}", (bbox[0] + 5, bbox[1] + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        cv2.putText(img, f"Gender: {'M' if face.gender else 'F'}", (bbox[0] + 5, bbox[1] + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        # Save face data to Qdrant
        id = str(uuid.uuid4())
        db.save_face_data(
            id=id,
            photo_title=photo_title,
            photo_id=photo_id,
            face_index=i,
            age=int(face.age),
            gender=int(face.gender),
            file_name=file_name,
            embedding=face.embedding.tolist()
        )

        # Save face image to MinIO
        base_image = BASE_IMAGE[int(face.gender)]
        base_face = BASE_FACE[int(face.gender)]

        img_face = face_swapper.get(base_image, base_face, face)
        img_face = face_restorer.restore(img_face)
        upload_to_s3_func(img_face, S3_PROCESSED_IMAGE_BUCKET, f"{id}.jpg")

    # Save processed image to MinIO
    upload_to_s3_func(img, S3_PROCESSED_IMAGE_BUCKET, file_name)

    return {"bucket": S3_PROCESSED_IMAGE_BUCKET, "file_name": file_name}

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
