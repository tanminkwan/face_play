import os
import logging
import gradio as gr
import pandas as pd
from config import S3_IMAGE_BUCKET
from app import storage
from app.face_process import process_image, get_image_list, get_average_faces, \
    view_network_graph
from ui.html import average_faces_html, network_graph_html, render_images_table
from ui.css import css
from ui.js import js_to_network_graph_tab, js_send_faceid_to_selectedid

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

def list_images(photo_id=None, photo_title=None):
    logger.info(f"Fetching image list for photo_title: {photo_title}, photo_id: {photo_id}")
    images = get_image_list(photo_id, photo_title)
    logger.info(f"Retrieved {len(images)} images.")

    # Sort images by 'file_name' and 'face_index' in ascending order
    images.sort(key=lambda x: (x['file_name'], x['face_index']))

    return render_images_table(images)
"""
def on_row_click(evt: gr.SelectData):
    logger.info(f"[on_row_click] Event data:\n{evt.value} {evt}")
    if not evt.value:
        return ""
    # Suppose your DataFrame columns are ["id", "photo_id", "photo_title", "age", "gender", "face_index"]
    row_data = evt.value  # This might be a list like ["abc123", "my-photo-id", ...]
    
    # The ID would be row_data[0] if the first column is "id"
    selected_id = row_data
    return str(selected_id)
"""
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
        return "", pd.DataFrame(), "<p style='color:red;'>Please provide a valid ID.</p>"

    # 데이터 가져오기
    data, _ = view_network_graph(id)
    if not data:
        return "", pd.DataFrame(), "<p style='color:red;'>No data found for the given ID.</p>"

    # 데이터프레임으로 변환
    df = pd.DataFrame([{
        "photo_id": item.photo_id,
        "photo_title": item.photo_title,
        "gender": "Male" if item.gender == 1 else "Female",
        "age": item.age,
        "score": item.score
    } for item in data])

    # Return the FastAPI URL for the network graph
    html = f"<p>View the network graph <a href='/network-graph/{id}' target='_blank'>here</a>.</p>"
    return "", df, html

logger.info("Starting Gradio app...")

with gr.Blocks(css=css) as demo:

    selected_id = gr.Textbox(label="Current Face ID", elem_id="selected_id", interactive=False, visible=False)
    original_file_name = gr.Textbox(elem_id="original_file_name", visible=False)

    with gr.Tab("Upload Image"):
        image_input = gr.Image(type="filepath", label="Upload Image")
        with gr.Row():
            photo_id = gr.Textbox(label="Photo ID")
            photo_title = gr.Textbox(label="Photo Title")
        upload_button = gr.Button("Upload")
        output_html = gr.HTML(label="Processed Image", elem_id="out_html")
        upload_button.click(
            fn=upload_image,
            inputs=[image_input, photo_title, photo_id],
            outputs=output_html
        )

    with gr.Tab("Image List"):
        with gr.Row():
            photo_id_input = gr.Textbox(label="Photo Id", placeholder="Enter Photo Id to filter")
            photo_title_input = gr.Textbox(label="Photo Title", placeholder="Enter photo title to filter")
        
        refresh_button = gr.Button("View List")

        """
        image_list = gr.Dataframe(
            headers=["Face ID", "Photo ID", "Photo Title", "Age", "Gender", "Face Index", "File Name"],
            value=[],
            interactive=True
        )
        """
        image_list_html = gr.HTML(label="Image List", elem_id="out_html")
        
        with gr.Row():
            details_button = gr.Button("View Face")
            original_button = gr.Button("View Original Photo")
            go_network_button = gr.Button("Go to Network Graph")

        refresh_button.click(
            fn=list_images,
            inputs=[photo_id_input, photo_title_input],
            #outputs=image_list
            outputs=image_list_html
        ).then(
            fn=None,
            inputs=None,
            outputs=None,
            js=js_send_faceid_to_selectedid
        )

        """
        image_list.select(
            fn=on_row_click,  # Function to extract id
            inputs=None,             # typically None here
            outputs=selected_id  # Store the result in the hidden Textbox
        )
        """

        details_output = gr.HTML(label="Image Details")
        
        details_button.click(
            fn=view_image_details,  # Function to fetch and display image
            inputs=selected_id,  # Pass the hidden Textbox value as input
            outputs=details_output
        )

        original_button.click(
            fn=view_image_details,  # Function to fetch and display image
            inputs=original_file_name,  # Pass the hidden Textbox value as input
            outputs=details_output
        )

        progress_html = gr.HTML(label="Drawing Network Graph", elem_id="out_html")

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

        input_id = gr.Textbox(label="Face ID", placeholder="Enter Face ID")
        view_button = gr.Button("View")

        # → 여기서 정의
        data_table = gr.Dataframe(
            headers=["Photo ID", "Photo Title", "Score", "Gender", "Age"],
            label="Graph Data"
        )
        network_output = gr.HTML(label="Network Graph", elem_id="out_html")
        # (중요) data_table, network_output을 탭 내에서 새로 만들지 않고,
        #       이미 정의해둔 컴포넌트(data_table, network_output)를 "표시"만.
        view_button.click(
            fn=render_network_graph,
            inputs=input_id,
            outputs=[network_output, data_table, network_output]
        )

    go_network_button.click(
        fn=render_network_graph,
        inputs=selected_id,                 # pass the hidden text ID
        outputs=[progress_html, data_table, network_output],
    ).then(
        fn=None,
        inputs=None,
        outputs=None,
        js=js_to_network_graph_tab
    )
#demo.queue()
#demo.launch(server_name="0.0.0.0", server_port=7860, allowed_paths=["./static"], debug=True)
logger.info("Gradio app launched successfully.")