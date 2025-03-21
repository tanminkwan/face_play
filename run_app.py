from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging
import gradio as gr
import pandas as pd
from config import S3_IMAGE_BUCKET
from app import storage
from app.face_process import process_image, get_image_list, get_average_faces, \
    view_network_graph
from ui.html import average_faces_html, network_graph_html
from ui.css import css

app = FastAPI()

# static 폴더를 정적으로 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_image(image, photo_title, photo_id):
    logger.info("Uploading image...")
    result = process_image(image, photo_title, photo_id)
    
    # Check if an error occurred during processing
    if "error" in result:
        logger.error(result["error"])
        return f"<p style='color: red;'>{result['error']}</p>"

    logger.info(f"Image processed and saved to bucket: {result['bucket']}, file: {result['file_name']}")
    url = storage.get_file_url(result["bucket"], result["file_name"])
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

    url = storage.get_file_url(S3_IMAGE_BUCKET, id)
    return f"<img src='{url}' style='max-width: 1080px; height: auto;'/>"

def view_average_faces():
    """
    Calls get_average_faces() and returns an HTML string with:
      - Female/male participant count
      - Female/male average ages
      - Image loaded from the returned bucket & file_name
    """
    data = get_average_faces()  # => { bucket, file_name, f_age, m_age, f_num_people, m_num_people }

    # Fetch image URL using the returned bucket & file_name
    url = storage.get_file_url(data["bucket"], data["file_name"])

    # Create an HTML block with the stats and the image    
    return average_faces_html(data, url)

def render_network_graph(id):
    logger.info(f"Rendering network graph for ID: {id}")

    if not id:
        return "<p style='color:red;'>Please provide a valid ID.</p>"

    # 데이터 가져오기
    data, main_node_id = view_network_graph(id)  # 데이터 형식: [{'photo_title', 'photo_id', 'score', 'gender', 'age'}, ...]

    # 데이터프레임으로 변환
    df = pd.DataFrame(data)[["photo_id", "photo_title", "gender", "age", "score"]]
    df.columns = ["Photo ID", "Photo Title", "Gender", "Age", "Score"]

    # network_graph_html 함수에 데이터를 주입해 HTML을 렌더링
    html = network_graph_html(data, main_node_id)
    return df, html

logger.info("Starting Gradio app...")

with gr.Blocks(css=css) as demo:

    with gr.Tab("Upload Image"):
        image_input = gr.Image(type="filepath", label="Upload Image")
        photo_title = gr.Textbox(label="Photo Title")
        photo_id = gr.Textbox(label="Photo ID")
        output_html = gr.HTML(label="Processed Image", elem_id="out_html")
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
    # --- Tab 3: Average Faces ---
    with gr.Tab("Average Faces"):
        gr.Markdown("Click below to see aggregate info about the faces and the merged (average) face image.")

        average_button = gr.Button("Show Average Faces")
        average_output = gr.HTML(label="Average Faces Details", elem_id="out_html")

        average_button.click(
            fn=view_average_faces,
            inputs=None,
            outputs=average_output
        )

    with gr.Tab("Network Graph"):
        gr.Markdown("Enter an ID to visualize the associated network graph.")

        input_id = gr.Textbox(label="ID", placeholder="Enter ID")
        view_button = gr.Button("View")

        network_output = gr.HTML(label="Network Graph", elem_id="out_html")
        data_table = gr.Dataframe(headers=["Photo ID", "Photo Name", "Gender", "Age", "Score"], label="Graph Data")

        view_button.click(
            fn=render_network_graph,
            inputs=input_id,
            outputs=[data_table, network_output]
        )

#demo.queue()
#demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=["./static"], debug=True)
logger.info("Gradio app launched successfully.")
# Gradio 앱을 FastAPI에 통합
app = gr.mount_gradio_app(app, demo, path="/")