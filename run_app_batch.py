import os
import glob
import sys
from app.face_process import process_image

# Image file extensions to process
IMAGE_EXTENSIONS = ('*.jpg', '*.png', '*.webp')

def process_images(target_dir):
    # Find all image file paths
    image_files = []
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(glob.glob(os.path.join(target_dir, ext)))

    total_files = len(image_files)
    print(f"Total images to process: {total_files}")

    processed_count = 0

    for image_path in image_files:
        folder_name = os.path.basename(os.path.normpath(target_dir))
        file_name_with_ext = os.path.basename(image_path)
        file_name, _ = os.path.splitext(file_name_with_ext)

        photo_title = f"{folder_name}__{file_name_with_ext}"
        photo_id = file_name

        # Call the provided function
        process_image(image_path, photo_title, photo_id)

        processed_count += 1
        sys.stdout.write(f"\r{processed_count}/{total_files} Progress: {(processed_count / total_files) * 100:.2f}%")
        sys.stdout.flush()

    print("\nAll images have been processed successfully.")  # Completion message

if __name__ == "__main__":
    target_directory = input("Enter the directory path containing images to process: ")
    if os.path.isdir(target_directory):
        process_images(target_directory)
    else:
        print("Invalid directory path.")
