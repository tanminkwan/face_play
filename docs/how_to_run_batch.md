# FacePlay Batch Processing Guide

## 1. Run Batch Processing for Face Analysis and Registration

### Step 1: Prepare Face Image Files
- Gather all face images to be uploaded into a single directory.
- Example directory structure:
  ```
  E:\faces_pjt\test_1000
  ```

### Step 2: Execute the Batch Processing Script
Run the batch script with the path to the directory containing face images.
```sh
python run_app_batch.py E:\faces_pjt\test_1000
```

This will process all images in the specified folder and register them accordingly.

---

## Notes
- Ensure that all dependencies are installed before running the scripts.
- The `.env` file should be properly configured before starting the scheduler.
- The batch processing script should be executed with the correct directory path containing the images.

