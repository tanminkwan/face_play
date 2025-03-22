from scheduler import storage, db, face_detector, face_swapper, face_restorer
from config import S3_IMAGE_BUCKET, RESERVED_FACES
import numpy as np
from datetime import datetime
from library.gadget import to_ndarray, create_face_from_vector
from database.models import FaceEmbeddings

def update_mean_faces():
    file_name = "mean_face.jpg"
    mean_face_img = storage.load_image("base-images", file_name)

    f_v = db.get_data_by_id(id=RESERVED_FACES[0], with_vectors=True)
    m_v = db.get_data_by_id(id=RESERVED_FACES[1], with_vectors=True)

    f_l = f_v.last_processed_at if f_v else 0.0
    m_l = m_v.last_processed_at if m_v else 0.0

    last_processed_at = max(f_l, m_l)
    data_to_mean = db.get_data_after_date(last_processed_at, with_vectors=True)

    if not data_to_mean:
        print("No new data to process.")
        return

    last_processed_at = data_to_mean[-1].created_at

    female_vectors = []
    male_vectors = []
    female_age_tot = 0
    male_age_tot = 0

    for item in data_to_mean:
        if item.embedding is not None:
            if item.gender == 0:
                female_vectors.append(item.embedding)
                female_age_tot += item.age
            elif item.gender == 1:
                male_vectors.append(item.embedding)
                male_age_tot += item.age

    faces = face_detector.get(mean_face_img)

    if not faces:
        return {"error": "No faces detected in the image. Please upload a valid image with faces."}
    elif len(faces) < 2:
        return {"error": "Please upload an image with at least 2 faces."}

    faces = sorted(faces, key=lambda face: face.bbox[0])

    updated_f_v = None
    f_num_people = len(female_vectors)

    if f_num_people > 0:
        f_vector_mean = np.mean(female_vectors, axis=0)
        f_age_mean = female_age_tot / f_num_people

        if f_v:
            weight_a = f_v.num_people / (f_v.num_people + f_num_people)
            weight_b = f_num_people / (f_v.num_people + f_num_people)
            f_vector_mean = (to_ndarray(f_v.embedding) * weight_a) + (f_vector_mean * weight_b)
            f_age_mean = (f_v.age * weight_a) + (f_age_mean * weight_b)

        updated_f_v = FaceEmbeddings(
            id=RESERVED_FACES[0],
            age=f_age_mean,
            gender=0,
            photo_title="Average Female Face",
            photo_id="average_female_face",
            num_people=(f_v.num_people if f_v else 0) + f_num_people,
            last_processed_at=last_processed_at,
            embedding=f_vector_mean.tolist()
        )
    elif f_v:

        f_vector_mean = f_v.embedding.copy()

    if f_num_people > 0 or f_v:
        mean_face_img = face_swapper.get(mean_face_img, faces[0], create_face_from_vector(f_vector_mean))

    updated_m_v = None
    m_num_people = len(male_vectors)

    if m_num_people > 0:
        m_vector_mean = np.mean(male_vectors, axis=0)
        m_age_mean = male_age_tot / m_num_people

        if m_v:
            weight_a = m_v.num_people / (m_v.num_people + m_num_people)
            weight_b = m_num_people / (m_v.num_people + m_num_people)
            m_vector_mean = (to_ndarray(m_v.embedding) * weight_a) + (m_vector_mean * weight_b)
            m_age_mean = (m_v.age * weight_a) + (m_age_mean * weight_b)

        updated_m_v = FaceEmbeddings(
            id=RESERVED_FACES[1],
            age=m_age_mean,
            gender=1,
            photo_title="Average Male Face",
            photo_id="average_male_face",
            num_people=(m_v.num_people if m_v else 0) + m_num_people,
            last_processed_at=last_processed_at,
            embedding=m_vector_mean.tolist()
        )
    elif m_v:

        m_vector_mean = m_v.embedding.copy()

    if m_num_people > 0 or m_v:
        mean_face_img = face_swapper.get(mean_face_img, faces[1], create_face_from_vector(m_vector_mean))

    img_face = face_restorer.restore(mean_face_img)

    timestamp = datetime.fromtimestamp(last_processed_at).strftime('%Y%m%d%H%M%S')
    new_filename = f"mean_face.{timestamp}.jpg"

    storage.upload_image(S3_IMAGE_BUCKET, new_filename, image=img_face)

    if updated_f_v:
        db.save_data(updated_f_v)

    if updated_m_v:
        db.save_data(updated_m_v)
