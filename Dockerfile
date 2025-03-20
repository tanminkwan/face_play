FROM python:3.12-slim

# (1) 필수 OS 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0

WORKDIR /face-play

# (2) requirements.txt 복사 & 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (5) 나머지 소스코드 복사
COPY app /face-play/app
COPY library /face-play/library
COPY storage /face-play/storage
COPY database /face-play/database
COPY ui /face-play/ui
COPY scheduler /face-play/scheduler
COPY config.py .
COPY download_models.py .
COPY run_app.py .
COPY run_scheduler.py .

COPY inswapper_128.onnx /models/inswapper_128.onnx
COPY codeformer.pth /models/codeformer.pth
RUN python download_models.py

# (6) 컨테이너 실행 명령
# CMD ["python", "run.py"]
