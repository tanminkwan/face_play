from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
from app import storage, face_detector
from app.jobs import update_mean_faces

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    print("Starting scheduler...")

    images = storage.load_base_images_list("base-images", ["mean_face"])
    logger.info(f"Loaded {len(images['mean_face'])} mean face images.")
    
    mean_face_imgs = []
    for f in images["mean_face"]:

        faces = face_detector.get(f)

        if not faces:
            logger.info("No faces detected in the image. Please upload a valid image with faces.")
            exit 
        elif len(faces) < 2:
            logger.info("Please upload an image with at least 2 faces.")
            exit

        faces = sorted(faces, key=lambda face: face.bbox[0])

        mean_face_imgs.append((f, faces))

    mean_f_face_img = storage.load_image("base-images", "mean_f_face.jpg")
    mean_m_face_img = storage.load_image("base-images", "mean_m_face.jpg")

    scheduler = BackgroundScheduler()

    # 5분 주기로 실행하되, 동시에 하나의 인스턴스만 실행되도록 설정
    scheduler.add_job(
        update_mean_faces, 
        'interval', 
        minutes=3, 
        max_instances=1,
        args=[mean_face_imgs, mean_f_face_img, mean_m_face_img],  # 인자 전달
        )
    scheduler.start()

    logger.info("Scheduler started. Press Ctrl+C to exit.")

    try:
        # 메인 스레드를 계속 실행시켜 백그라운드 작업이 계속 동작하도록 함
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
