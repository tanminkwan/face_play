from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
from scheduler.jobs import update_mean_faces

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    scheduler = BackgroundScheduler()

    # 5분 주기로 실행하되, 동시에 하나의 인스턴스만 실행되도록 설정
    scheduler.add_job(update_mean_faces, 'interval', minutes=1, max_instances=1)
    scheduler.start()

    print("Scheduler started. Press Ctrl+C to exit.")

    try:
        # 메인 스레드를 계속 실행시켜 백그라운드 작업이 계속 동작하도록 함
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped.")
