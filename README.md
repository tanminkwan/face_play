# face_play
---
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