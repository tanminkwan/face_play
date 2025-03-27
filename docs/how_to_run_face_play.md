# FacePlay Installation & Running Guide

## 1. Install and Run MinIO

### 1.1 Install & Run on Windows
- Follow the installation guide: [MinIO Windows Installation](https://min.io/docs/minio/windows/index.html)
- Run MinIO with the following command (assuming data directory is `C:\minio`):
  ```sh
  .\minio.exe server C:\minio --console-address :9001
  ```

### 1.2 Install & Run on Docker Container
- Use the following `docker-compose.yml` to run MinIO:

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

### 1.3 Initialize MinIO for FacePlay
- **Create Buckets**: `processed-images`, `base-images`
- **Upload Template Images**: Use `./resources` images or other custom images into `base-images`.

#### Template Image Naming Rules:
- `f_*.jpg` : Female face template images
- `m_*.jpg` : Male face template images
- `mean_f_face.jpg` : Average female face template
- `mean_m_face.jpg` : Average male face template
- `mean_face_*.jpg` : Multi-person average face templates

#### Configure `.env` File
1. **Generate Access Key** using MinIO Web Console.
2. **Set Environment Variables** in `.env`:
> `IS_FACE_RESTORATION_ENABLED` : Whether to use the face restoration feature when replacing the input face with the template face (applying this may cause processing delays).
```sh
S3_ENDPOINT=70.121.154.136:9000
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_SECURE=false
S3_IMAGE_BUCKET=processed-images
VECTOR_DB=QDRANT
VECTOR_DB_HOST=127.0.0.1
VECTOR_DB_PORT=6333
IS_FACE_RESTORATION_ENABLED=false 
```

---

## 2. Install and Run Qdrant

### 2.1 Install & Run on Windows
- Download from: [https://github.com/qdrant/qdrant/releases](https://github.com/qdrant/qdrant/releases)
- Run with the following command:
  ```sh
  .\qdrant.exe --uri http://127.0.0.1:6333
  ```

### 2.2 Install & Run on Docker Container
- Use the following `docker-compose.yml` to run Qdrant:

```yaml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant:latest
    restart: always
    container_name: qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
volumes:
  qdrant_data:
    driver: local
```

### 2.3 Initialize Qdrant for FacePlay
- **Create Collection `face_embeddings`**
  ```sh
  curl -X PUT "http://127.0.0.1:6333/collections/face_embeddings" -H "Content-Type: application/json" -d "{\"vectors\":{\"size\":512,\"distance\":\"Cosine\"}}"
  ```
- **Create Index on `face_embeddings`**
  ```sh
  curl -X PUT "http://localhost:6333/collections/face_embeddings/index" ^
       -H "Content-Type: application/json" ^
       -d "{ \"field_name\": \"photo_id\", \"field_schema\": \"keyword\" }"
  ```

---

## 3. Install and Run FacePlay

### 3.1 Download FacePlay
- Clone the repository: [https://github.com/tanminkwan/face_play.git](https://github.com/tanminkwan/face_play.git)

### 3.2 Download AI Models
- `inswapper_128`: [https://huggingface.co/ezioruan/inswapper_128.onnx/tree/main](https://huggingface.co/ezioruan/inswapper_128.onnx/tree/main)
- `codeformer.pth`: [https://github.com/sczhou/CodeFormer/releases](https://github.com/sczhou/CodeFormer/releases)

### 3.3 Set Up Python Virtual Environment
```sh
python -m venv venv
```
- **Activate Virtual Environment**
  - Windows: `venv\Scripts\activate`
  - Unix/MacOS: `source venv/bin/activate`

- **Install Dependencies**
  ```sh
  pip install -r requirements.txt
  ```

- **Run the Application**
  ```sh
  uvicorn run_app:app --host 0.0.0.0 --port 7860
  ```

---

## 4. Run FacePlay in Docker

### 4.1 Copy AI Models
Place `inswapper_128.onnx` and `codeformer.pth` in the FacePlay root directory.

### 4.2 Build Docker Image
```sh
docker build -t face-play .
```

### 4.3 Run with Docker Compose
Create `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  face-play:
    image: face-play
    container_name: face-play
    ports:
      - "7860:7860"
    environment:
      S3_ENDPOINT: your_minio_endpoint
      S3_ACCESS_KEY: your_access_key
      S3_SECRET_KEY: your_secret_key
      S3_SECURE: "false"
      S3_IMAGE_BUCKET: processed-images
      VECTOR_DB: QDRANT
      VECTOR_DB_HOST: your_qdrant_host
      VECTOR_DB_PORT: "6333"
      IS_FACE_RESTORATION_ENABLED: "false"
    command: uvicorn run_app:app --host 0.0.0.0 --port 7860
```

- **Run Docker Compose**
```sh
docker compose up -d
```

### 4.4 Run the Scheduler
The scheduler periodically generates average face embeddings and updates the average face images. It runs independently from the FacePlay application.

#### Step 1: Set Execution Interval
- Define the execution interval (in minutes) by updating the `SCHEDULER_INTERVAL_MINUTES` environment variable in the `.env` file.

```sh
...
SCHEDULER_INTERVAL_MINUTES=3
...
```

#### Step 2: Run the Scheduler
Execute the scheduler script to start the scheduled face processing.

```sh
python run_scheduler.py
```
#### Run Scheduler in Docker
If running in a Docker container, use the following docker-compose.yml configuration:

```yaml
version: '3.8'
services:
  face-play-scheduler:
    image: face-play
    container_name: face-play-scheduler
    environment:
      S3_ENDPOINT: your_minio_endpoint
      S3_ACCESS_KEY: your_access_key
      S3_SECRET_KEY: your_secret_key
      S3_SECURE: "false"
      S3_IMAGE_BUCKET: processed-images
      VECTOR_DB: QDRANT
      VECTOR_DB_HOST: your_qdrant_host
      VECTOR_DB_PORT: "6333"
      IS_FACE_RESTORATION_ENABLED: "false"
      SCHEDULER_INTERVAL_MINUTES: 3
    command: ["python", "run_scheduler.py"]
```