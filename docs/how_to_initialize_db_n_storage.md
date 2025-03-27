# How to Initialize Database and Storage

## 1. Delete All Data from Qdrant Collection `face_embeddings`
To remove all data from the `face_embeddings` collection in Qdrant, run the following `curl` command:

```bash
curl -X POST "http://<qdrant_db_domain>:6333/collections/face_embeddings/points/delete" ^
     -H "Content-Type: application/json" ^
     --data "{\"filter\": {}}"
```

This command sends a request to delete all stored points from the specified collection.

---

## 2. Delete All Data from MinIO Bucket `processed-images`
There are two ways to delete all images from the MinIO bucket:

### Option 1: Using MinIO Web Console
- Open the MinIO Web Console.
- Navigate to the `processed-images` bucket.
- Manually delete all objects inside.

### Option 2: Using Python Script
Run the following Python commands within the `face_play` environment to delete all objects in the MinIO bucket:

```bash
(v-face_play) C:\GitHub\face_play> python
```
```python
Python 3.12.1 (tags/v3.12.1:2305ca5, Dec  7 2023, 22:03:25) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from storage import storage_client
>>> from config import OBJECT_STORAGE, S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_SECURE, S3_IMAGE_BUCKET
>>> storage = storage_client(
...     OBJECT_STORAGE,
...     endpoint=S3_ENDPOINT,
...     access_key=S3_ACCESS_KEY,
...     secret_key=S3_SECRET_KEY,
...     secure=S3_SECURE
...     )
>>> storage.delete_all_objects_batch(S3_IMAGE_BUCKET)
```

This script will delete all objects from the specified MinIO bucket.

---

## Notes
- Ensure that you have the correct access credentials for Qdrant and MinIO before executing these commands.
- Be cautious when running these commands as they **permanently delete all stored data**.
- The Python script should be executed within the `face_play` environment.