# face_play
---
### Installation & Running
#### 1. MinIO
##### 1-1. On Windows
- MinIO : https://min.io/docs/minio/windows/index.html
  Run Command : `.\minio.exe server C:\minio --console-address :9001`
##### 1-2. On Docker container
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
  Create and paste them to `S3_ACCESS_KEY`, `S3_SECRET_KEY` in `.env`
#### 2. Qdrant
##### 2-1. On Windows
- Qdrant : https://github.com/qdrant/qdrant/releases
  Run Command : `.\qdrant.exe --uri http://127.0.0.1:6333`
##### 2-2. On Docker container
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
  On Windows :
  ```bash
  curl -X PUT "http://127.0.0.1:6333/collections/face_embeddings" -H "Content-Type: application/json" -d "{\"vectors\":{\"size\":512,\"distance\":\"Cosine\"}}"
  ```
  - Response : 
  ```json
  {"result":true,"status":"ok","time":0.3824695}
  ```
- Create Index on the collection `face_embeddings`
  On Windows :
  ```bash
  curl -X POST "http://localhost:6333/collections/face_embeddings/index" ^
  -H "Content-Type: application/json" ^
  -d "{ \"field_name\": \"photo_id\", \"field_schema\": \"keyword\"}"
  ```
##### 2-3. 주요쿼리
- `face_embeddings` Data 전체 삭제
```bash
curl -X POST "http://127.0.0.1:6333/collections/face_embeddings/points/delete" ^
     -H "Content-Type: application/json" ^
     --data "{\"filter\": {}}"
```
```bash
curl -X POST "http://127.0.0.1:6333/collections/face_embeddings/points/delete" \
     -H "Content-Type: application/json" \
     --data '{"filter": {}}'
```
#### 3. App
##### 3-1. **Create a Virtual Environment**  
   Run the following command to create a virtual environment:
   ```bash
   python -m venv venv
   ```

##### 3-2. **Activate the Virtual Environment**  
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

##### 3-3. **Install Dependencies**  
   Install the packages listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
##### 3-4. Settings
- `.env` sample
```python
S3_ENDPOINT=www.leebalso.org:9000
S3_ACCESS_KEY=OwnKCLf4NR7905uuv3pI
S3_SECRET_KEY=nGhCbM81UHXuyblbMaizDURhUpZYL5h3lBLPyrQO
S3_SECURE=false
S3_PROCESSED_IMAGE_BUCKET=processed-images
VECTOR_DB=QDRANT
VECTOR_DB_HOST=192.168.0.4
VECTOR_DB_PORT=6333
```
- `config.py` sample
```python
...
# AI Model configuration
BUFFALO_L_PATH = "C:\\"
INSWAPPER_PATH = "C:\\models\\inswapper_128.onnx"
CODEFORMER_MODEL = "C:/GitHub/v-face_play/CodeFormer/weights/CodeFormer/codeformer.pth"
```

##### 3-5. **Run the Application**  
   Start the application by running:
   ```bash
   python run.py
   ```
### 4. Dockerize
```bash
Downloading: "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/detection_Resnet50_Final.pth" to /home/hennry/GitHub/v-face_play/lib/python3.10/site-packages/codeformer/weights/facelib/detection_Resnet50_Final.pth

100%|██████████████████████████████████████████████████████████████████████| 104M/104M [00:03<00:00, 30.8MB/s]
Downloading: "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_parsenet.pth" to /home/hennry/GitHub/v-face_play/lib/python3.10/site-packages/codeformer/weights/facelib/parsing_parsenet.pth

100%|████████████████████████████████████████████████████████████████████| 81.4M/81.4M [00:01<00:00, 60.3MB/s]
```