# upload 할 얼굴 사진 파일을 한 폴더에 모음
- 예) E:\faces_pjt\test_1000
# 필요하다면 vector db 와 minio 의 transaction data를 초기화
- Qdrant collection `face_embeddings` Data 전체 삭제
```bash
curl -X POST "http://127.0.0.1:6333/collections/face_embeddings/points/delete" ^
     -H "Content-Type: application/json" ^
     --data "{\"filter\": {}}"
```
- MinIO bucket `processed-images` 전체 삭제
# scheduler 실행
- `python run_scheduler.py`
# 대량 upload 실행
- `python run_app_batch.py <directory path>`
