# face_play
---
### Settings
- `.env` sample
```python
MINIO_ENDPOINT=www.leebalso.org:9000
MINIO_ACCESS_KEY=OwnKCLf4NR7905uuv3pI
MINIO_SECRET_KEY=nGhCbM81UHXuyblbMaizDURhUpZYL5h3lBLPyrQO
MINIO_SECURE=false
MINIO_PROCESSED_IMAGE_BUCKET=processed-images
QDRANT_HOST=192.168.0.4
QDRANT_PORT=6333
BUFFALO_L_PATH=C:\
```
---
### Installation
#### 1. MinIO
##### 1-1. for windows
- MinIO : https://min.io/docs/minio/windows/index.html
  Run Command : `.\minio.exe server C:\minio --console-address :9001`
##### 1-2. Docker container
- MinIO docker compose
```yaml
version: '3.8'
services:
  minio:
    image: minio/minio:latest
    restart: always
    container_name: minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: admin123
    command: server /data --console-address ":9001"
volumes:
  minio_data:
```
##### 1-3. Init
- Create Bucket
  Bucker name : `processed-images`, `base-images`
  Upload Base images : `f_base.jpg`, `m_base.jpg` 를 `base-images` bucket에 upload
- Create access key
  Create and paste them to `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` in `.env`
#### 2. Qdrant
##### 2-1. for windows
- Qdrant : https://github.com/qdrant/qdrant/releases
  Run Command : `.\qdrant.exe --uri http://127.0.0.1:6333`
##### 2-2. Docker container
- Qdrant docker compose
```yaml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant:latest
    restart: always
    container_name: qdrant
    ports:
      - "6333:6333"  # Qdrant 기본 포트
    volumes:
      - qdrant_data:/qdrant/storage  # 데이터를 영구적으로 저장하기 위한 Volume 설정
volumes:
  qdrant_data:
    driver: local
```
##### 2-3. Init
- Create Collection
  For Windows :
  ```bash
  curl -X PUT "http://127.0.0.1:6333/collections/face_embeddings" -H "Content-Type: application/json" -d "{\"vectors\":{\"size\":512,\"distance\":\"Cosine\"}}"
  ```
  - Response : 
  ```json
  {"result":true,"status":"ok","time":0.3824695}
  ```
##### 2-3. 주요쿼리
- `face_embeddings` Data 전체 삭제
```bash
curl -X POST "http://127.0.0.1:6333/collections/face_embeddings/points/delete" ^
     -H "Content-Type: application/json" ^
     --data "{\"filter\": {}}"
```
