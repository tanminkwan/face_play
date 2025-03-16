from app.db_process import save_face_data
import cv2
import insightface
from config import BUFFALO_L_PATH, MINIO_PROCESSED_IMAGE_BUCKET

model = insightface.app.FaceAnalysis(name='buffalo_l', root=BUFFALO_L_PATH)
model.prepare(ctx_id=0)

def process_image(image, photo_title, photo_id, upload_to_minio_func):
    img = cv2.imread(image)
    faces = model.get(img)
    faces = sorted(faces, key=lambda face: face.bbox[0])

    for i, face in enumerate(faces):

        # 얼굴 영역 표시
        bbox = face.bbox.astype(int)
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        # Draw labels
        
        text_color = (235, 45, 45)
        cv2.putText(img, f"IDX : {i}", (bbox[0] + 5, bbox[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        cv2.putText(img, f"Age: {face.age}", (bbox[0] + 5, bbox[1] + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        cv2.putText(img, f"Gender: {face.gender}", (bbox[0] + 5, bbox[1] + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        # Save face data to Qdrant
        save_face_data(photo_title, photo_id, i, int(face.age), int(face.gender), face.embedding.tolist())

    # Save processed image to MinIO
    file_name = f"{photo_id}_processed.jpg"
    bucket = MINIO_PROCESSED_IMAGE_BUCKET
    upload_to_minio_func(img, bucket, file_name)

    return {"bucket": bucket, "file_name": file_name}
