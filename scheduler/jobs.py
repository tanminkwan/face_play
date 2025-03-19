from scheduler import storage, db, face_detector, face_swapper, face_restorer
from config import S3_IMAGE_BUCKET
from config import RESERVED_FACES
import numpy as np
from ai_process.gadget import to_ndarray, create_face_from_vector

def update_mean_faces():

    mean_face_img = storage.load_image("base-images", "mean_face.jpg")

    m_v = db.get_data_by_id(id=RESERVED_FACES[1], with_vectors=True)
    f_v = db.get_data_by_id(id=RESERVED_FACES[0], with_vectors=True)
    
    f_l = f_v["last_processed_at"] if f_v else 0.0
    m_l = m_v["last_processed_at"] if m_v else 0.0

    last_processed_at = max(f_l, m_l)
    data_to_mean = db.get_data_after_date_sorted(last_processed_at, with_vectors=True)

    if not data_to_mean:
        print("No new data to process.")
        return

    last_processed_at = data_to_mean[-1]["created_at"]

    female_vectors = []
    male_vectors   = []
    female_age_tot = 0
    male_age_tot = 0

    for item in data_to_mean:
        if item.get("embedding") is not None:  # 'vector' 존재 및 None 체크
            if item.get("gender") == 0:
                female_vectors.append(item["embedding"])
                female_age_tot += item["age"]
            elif item.get("gender") == 1:
                male_vectors.append(item["embedding"])
                male_age_tot += item["age"]

    faces = face_detector.get(mean_face_img)
    
    # If no faces are detected, return an error message
    if not faces:
        return {"error": "No faces detected in the image. Please upload a valid image with faces."}

    faces = sorted(faces, key=lambda face: face.bbox[0])
    file_name = "mean_face.jpg"
    
    f_num_people = len(female_vectors)
    f_vector_mean = np.mean(female_vectors, axis=0)

    if f_num_people > 0:

        f_age_mean = female_age_tot/f_num_people        

        if f_v:

            weight_a = f_v["num_people"] / (f_v["num_people"] + f_num_people)
            weight_b = f_num_people / (f_v["num_people"] + f_num_people)
            f_vector_mean = (to_ndarray(f_v["embedding"]) * weight_a) + (f_vector_mean * weight_b)
            f_age_mean = (f_v["age"] * weight_a) + (f_age_mean * weight_b)

        db.save_special_face_data(
            id = RESERVED_FACES[0], 
            age = f_age_mean,
            gender = 1,
            num_people = (f_v["num_people"] if f_v else 0) + f_num_people,
            last_processed_at = last_processed_at, 
            embedding = f_vector_mean.tolist()
        )
        
        mean_face_img = face_swapper.get(mean_face_img, faces[0], create_face_from_vector(f_vector_mean))
    
    m_num_people = len(male_vectors)
    m_vector_mean = np.mean(male_vectors, axis=0)
    
    if m_num_people > 0:

        m_age_mean = male_age_tot/m_num_people        
   
        if m_v:

            weight_a = m_v["num_people"] / (m_v["num_people"] + m_num_people)
            weight_b = m_num_people / (m_v["num_people"] + m_num_people)
            m_vector_mean = (to_ndarray(m_v["embedding"]) * weight_a) + (m_vector_mean * weight_b)
            m_age_mean = (m_v["age"] * weight_a) + (m_age_mean * weight_b)

        db.save_special_face_data(
            id = RESERVED_FACES[1], 
            age = m_age_mean,
            gender = 1,
            num_people = (m_v["num_people"] if m_v else 0) + m_num_people,
            last_processed_at = last_processed_at, 
            embedding = m_vector_mean.tolist()
        )

        mean_face_img = face_swapper.get(mean_face_img, faces[1], create_face_from_vector(m_vector_mean))
    
    img_face = face_restorer.restore(mean_face_img)

    storage.upload_image(img_face, S3_IMAGE_BUCKET, file_name)