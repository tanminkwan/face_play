import os
import logging
import gradio as gr
import pandas as pd
from app.face_process import process_image, get_image_list
from app.file_process import get_presigned_url, upload_to_s3
from config import S3_PROCESSED_IMAGE_BUCKET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_image(image, photo_title, photo_id):
    logger.info("Uploading image...")
    result = process_image(image, photo_title, photo_id, upload_to_s3)
    
    # Check if an error occurred during processing
    if "error" in result:
        logger.error(result["error"])
        return f"<p style='color: red;'>{result['error']}</p>"

    logger.info(f"Image processed and saved to bucket: {result['bucket']}, file: {result['file_name']}")
    url = get_presigned_url(result["bucket"], result["file_name"])
    return f"<img src='{url}' style='max-width: 1080px; height: auto;'/>"

def list_images(file_name=None, photo_id=None):
    logger.info(f"Fetching image list for file_name: {file_name}, photo_id: {photo_id}")
    images = get_image_list(file_name, photo_id)
    logger.info(f"Retrieved {len(images)} images.")
    return pd.DataFrame(images, columns=["id", "file_name", "photo_id", "photo_title", "age", "gender", "face_index"])

def on_row_click(evt: gr.SelectData):
    logger.info(f"[on_row_click] Event data:\n{evt}")
    if not evt.value:
        return ""
    # Suppose your DataFrame columns are ["id", "photo_id", "photo_title", "age", "gender", "face_index"]
    row_data = evt.value  # This might be a list like ["abc123", "my-photo-id", ...]
    
    # The ID would be row_data[0] if the first column is "id"
    selected_id = row_data
    return str(selected_id)

def view_image_details(id):
    logger.info(f"Fetching details for ID: {id}")
    if not id:
        return "<p>No ID selected.</p>"

    # If `id` does not end with ".jpg", append ".jpg"
    if not id.endswith(".jpg"):
        id += ".jpg"

    url = get_presigned_url(S3_PROCESSED_IMAGE_BUCKET, id)
    return f"<img src='{url}' style='max-width: 1080px; height: auto;'/>"

if __name__ == "__main__":
    logger.info("Starting Gradio app...")

    with gr.Blocks() as demo:
        with gr.Tab("Upload Image"):
            image_input = gr.Image(type="filepath", label="Upload Image")
            photo_title = gr.Textbox(label="Photo Title")
            photo_id = gr.Textbox(label="Photo ID")
            output_html = gr.HTML(label="Processed Image")

            upload_button = gr.Button("Upload")
            upload_button.click(
                fn=upload_image,
                inputs=[image_input, photo_title, photo_id],
                outputs=output_html
            )

        with gr.Tab("Image List"):
            file_name_input = gr.Textbox(label="File Name", placeholder="Enter file name to filter")
            photo_id_input = gr.Textbox(label="Photo Id", placeholder="Enter Photo Id to filter")
            refresh_button = gr.Button("Refresh List")

            image_list = gr.Dataframe(
                headers=["ID", "File Name", "Photo ID", "Photo Title", "Age", "Gender", "Face Index"],
                value=[],
                interactive=True
            )
            selected_id = gr.Textbox(visible=False)  # Hidden Textbox to store id

            refresh_button.click(
                fn=list_images,
                inputs=[file_name_input, photo_id_input],
                outputs=image_list
            )

            image_list.select(
                fn=on_row_click,  # Function to extract id
                inputs=None,             # typically None here
                outputs=selected_id  # Store the result in the hidden Textbox
            )

            details_button = gr.Button("View Details")
            details_output = gr.HTML(label="Image Details")
            details_button.click(
                fn=view_image_details,  # Function to fetch and display image
                inputs=selected_id,  # Pass the hidden Textbox value as input
                outputs=details_output
            )

    demo.launch(server_name="0.0.0.0", server_port=7860, debug=True)
    logger.info("Gradio app launched successfully.")
