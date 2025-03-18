FROM python:3.12-slim

# (1) 필수 OS 패키지 설치
RUN apt-get update && \
    apt-get install -y wget git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# (2) requirements.txt 복사 & 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (3) CodeFormer에서 참조할 디렉토리 준비
#     - codeformer/weights/ 밑에 메인 모델(.pth)
#     - codeformer/weights/facelib/ 밑에 detection/parsing 모델들
#RUN mkdir -p /app/codeformer/weights/facelib

# (4) wget으로 모델 다운로드
#RUN wget -q --show-progress -O /app/codeformer/weights/codeformer-v0.1.0.pth \
#    https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer-v0.1.0.pth

#RUN wget -q --show-progress -O /app/codeformer/weights/facelib/detection_Resnet50_Final.pth \
#    https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/detection_Resnet50_Final.pth

#RUN wget -q --show-progress -O /app/codeformer/weights/facelib/parsing_parsenet.pth \
#    https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_parsenet.pth

# (5) 나머지 소스코드 복사
COPY . .

# (6) 컨테이너 실행 명령
CMD ["python", "run.py"]
