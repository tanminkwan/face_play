import numpy as np
import random
import logging
from app import storage, db, face_detector, face_swapper, face_restorer
from config import S3_IMAGE_BUCKET, RESERVED_FACES
from datetime import datetime
from library.gadget import create_face_from_vector, update_mean_vector
from database.models import FaceEmbeddings
from app.common import update_images_by_face

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_mean_faces(mean_face_imgs, mean_f_face_img, mean_m_face_img):

    MEAN_FEMALE_FACE_ID = RESERVED_FACES[0]
    MEAN_MAIL_FACE_ID = RESERVED_FACES[1]

    f_v = db.get_data_by_id(id=MEAN_FEMALE_FACE_ID, with_vectors=True)
    m_v = db.get_data_by_id(id=MEAN_MAIL_FACE_ID, with_vectors=True)

    f_l, f_age, f_embedding, f_num_people = \
        (f_v.last_processed_at, f_v.age, f_v.embedding, f_v.num_people) \
        if f_v else (0.0, 0, None, 0)
    m_l, m_age, m_embedding, m_num_people = \
        (m_v.last_processed_at, m_v.age, m_v.embedding, m_v.num_people) \
        if m_v else (0.0, 0, None, 0)

    max_l = max(f_l, m_l)
    data_to_mean = db.get_data_after_date(max_l, with_vectors=True)

    if not data_to_mean:
        logger.info("No new data to process.")
        return
    else :
        logger.info(f"Processing {len(data_to_mean)} new data.")

    last_processed_at = data_to_mean[-1].created_at

    new_f_embedding = []
    new_m_embedding = []
    new_f_ages = []
    new_m_ages = []

    for item in data_to_mean:
        if item.embedding is not None:
            if item.gender == 0:
                new_f_embedding.append(item.embedding)
                new_f_ages.append(item.age)
            elif item.gender == 1:
                new_m_embedding.append(item.embedding)
                new_m_ages.append(item.age)
    
    num_ = random.randint(0, len(mean_face_imgs)-1)
    logger.info(f"Using {num_}th  mean face image. {len(mean_face_imgs)} images in total.")
    mean_face_img, mean_faces = mean_face_imgs[num_]

    updated_female_v = None
    new_f_num_people = len(new_f_embedding)

    if new_f_num_people > 0:

        new_f_embedding_mean = update_mean_vector(f_embedding, f_num_people, new_f_embedding)
        new_f_age_mean = float(update_mean_vector(f_age, f_num_people, new_f_ages))

        updated_female_v = FaceEmbeddings(
            id=MEAN_FEMALE_FACE_ID,
            age=new_f_age_mean,
            gender=0,
            photo_title="Average Female Face",
            photo_id="average_female_face",
            num_people=f_num_people + new_f_num_people,
            last_processed_at=last_processed_at,
            embedding=new_f_embedding_mean.tolist()
        )

        update_images_by_face(
            S3_IMAGE_BUCKET,
            f"{MEAN_FEMALE_FACE_ID}.jpg",
            mean_f_face_img,
            create_face_from_vector(new_f_embedding_mean),
            restore=True
        )

    elif f_v:

        new_f_embedding_mean = f_embedding.copy()

    if new_f_num_people > 0 or f_v:
        mean_face_img = face_swapper.get(mean_face_img, mean_faces[0], create_face_from_vector(new_f_embedding_mean))

    updated_male_v = None
    new_m_num_people = len(new_m_embedding)

    if new_m_num_people > 0:

        new_m_embedding_mean = update_mean_vector(m_embedding, m_num_people, new_m_embedding)
        new_m_age_mean = float(update_mean_vector(m_age, m_num_people, new_m_ages))

        updated_male_v = FaceEmbeddings(
            id=MEAN_MAIL_FACE_ID,
            age=new_m_age_mean,
            gender=1,
            photo_title="Average Male Face",
            photo_id="average_male_face",
            num_people=m_num_people + new_m_num_people,
            last_processed_at=last_processed_at,
            embedding=new_m_embedding_mean.tolist()
        )

        update_images_by_face(
            S3_IMAGE_BUCKET,
            f"{MEAN_MAIL_FACE_ID}.jpg",
            mean_m_face_img,
            create_face_from_vector(new_m_embedding_mean),
            restore=True
        )
    elif m_v:

        new_m_embedding_mean = m_v.embedding.copy()

    if new_m_num_people > 0 or m_v:
        mean_face_img = face_swapper.get(mean_face_img, mean_faces[1], create_face_from_vector(new_m_embedding_mean))

    img_face = face_restorer.restore(mean_face_img)

    timestamp = datetime.fromtimestamp(last_processed_at).strftime('%Y%m%d%H%M%S')
    new_filename = f"mean_face.{timestamp}.jpg"

    storage.upload_image(S3_IMAGE_BUCKET, new_filename, image=img_face)

    if updated_female_v:
        db.save_data(updated_female_v)

    if updated_male_v:
        db.save_data(updated_male_v)