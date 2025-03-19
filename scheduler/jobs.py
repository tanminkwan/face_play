from scheduler import storage, db
from config import RESERVED_FACES
import numpy as np

def update_mean_faces():

    gender_group = [ 
        (
            r["gender"], 
            storage.load_image("base-images", r["file_name"]),
            db.get_data(id=r["db_id"])
        ) \
        for r in RESERVED_FACES if r["type"]=="mean_face" 
    ]

    for gender, image, data in gender_group:

        if not data:
            last_processed_at = 0.0
        else:
            last_processed_at = max(last_processed_at, data["created_at"])

    data_to_mean = db.get_data_after_date_sorted(last_processed_at, with_vectors=True)

    # 1) 각각의 gender 그룹에 대한 벡터를 모읍니다.
    female_vectors = []
    male_vectors   = []

    for item in data_to_mean:
        if item.get("embedding") is not None:  # 'vector' 존재 및 None 체크
            if item.get("gender") == 0:
                female_vectors.append(item["embedding"])
            elif item.get("gender") == 1:
                male_vectors.append(item["embedding"])

    # 2) 각 그룹별 건수(count) 계산
    female_count = len(female_vectors)
    male_count   = len(male_vectors)

    # 3) 각 그룹별 평균(mean) 계산
    if female_count > 0:
        # female_vectors가 리스트의 리스트라고 가정할 경우
        female_mean = np.mean(female_vectors, axis=0)
        save_special_face_data(id, age, num_people, last_processed_at, embedding):        
    else:
        female_mean = None

    if male_count > 0:
        male_mean = np.mean(male_vectors, axis=0)
    else:
        male_mean = None

    #print(f"male_mean : {male_mean}, female_mean : {female_mean}, male_count : {male_count}, female_count : {female_count}")