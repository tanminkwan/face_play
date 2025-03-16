import os
import logging
import gradio as gr
from app.face_process import process_image
from app.file_process import get_image_list, get_presigned_url, upload_to_minio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_image(image, photo_title, photo_id):
    logger.info("Uploading image...")
    result = process_image(image, photo_title, photo_id, upload_to_minio)
    logger.info(f"Image processed and saved to bucket: {result['bucket']}, file: {result['file_name']}")
    url = get_presigned_url(result["bucket"], result["file_name"])
    return f"<img src='{url}' style='width: 100%; max-width: 1080px; height: auto;'/>"

def list_images():
    logger.info("Fetching image list...")
    images = get_image_list()
    logger.info(f"Retrieved {len(images)} images.")
    return [{"photo_id": img["photo_id"], "photo_title": img["photo_title"]} for img in images]

def view_image_details(photo_id):
    logger.info(f"Fetching details for photo ID: {photo_id}")
    image_data = get_presigned_url(photo_id["bucket"], photo_id["file_name"])
    return image_data

if __name__ == "__main__":
    logger.info("Starting Gradio app...")
    with gr.Blocks() as demo:
        with gr.Tab("Upload Image"):
            image_input = gr.Image(type="filepath", label="Upload Image")
            photo_title = gr.Textbox(label="Photo Title")
            photo_id = gr.Textbox(label="Photo ID")
            #output_image = gr.Image(type="url", label="Processed Image")            
            output_html = gr.HTML(label="Processed Image")
            upload_button = gr.Button("Upload")
            upload_button.click(upload_image, inputs=[image_input, photo_title, photo_id], outputs=output_html)

        with gr.Tab("Image List"):
            image_list = gr.Dataframe(headers=["Photo ID", "Photo Title"])
            details_button = gr.Button("View Details")
            details_output = gr.Image(label="Image Details")
            details_button.click(view_image_details, inputs=image_list, outputs=details_output)

    #demo.launch(allowed_paths=ALLOWED_PATHS, debug=True)
    demo.launch(debug=True)
    logger.info("Gradio app launched successfully.")
