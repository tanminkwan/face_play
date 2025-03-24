import logging
import gradio as gr
import pandas as pd
from app.face_process import process_image, get_image_list, get_average_faces, \
    view_network_graph, get_image_url
from ui.html import average_faces_html, render_images_table
from ui.css import css
from ui.js import js_to_network_graph_tab, js_send_faceid_to_selectedid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_image(image, photo_title, photo_id):
    
    logger.info("Uploading image...")
    file_name = process_image(image, photo_title, photo_id)
    url = get_image_url(file_name)

    return f"<img src='{url}' style='max-width: 1080px; height: auto;'/>"

def list_images(photo_id=None, photo_title=None):

    logger.info(f"Fetching image list for photo_title: {photo_title}, photo_id: {photo_id}")
    images = get_image_list(photo_id, photo_title)
    logger.info(f"Retrieved {len(images)} images.")

    # Sort images by 'file_name' and 'face_index' in ascending order
    images.sort(key=lambda x: (x['file_name'], x['face_index']))

    return render_images_table(images)

def view_image_details(id):

    logger.info(f"Fetching details for ID: {id}")
    if not id:
        return "<p>No ID selected.</p>"

    # If `id` does not end with ".jpg", append ".jpg"
    if not id.endswith(".jpg"):
        id += ".jpg"

    url = get_image_url(id)
    return f"<img src='{url}' style='max-width: 1080px; height: auto;'/>"

def view_average_faces():
    """
    Calls get_average_faces() and returns an HTML string with:
      - Female/male participant count
      - Female/male average ages
      - Image loaded from the returned bucket & file_name
    """
    data = get_average_faces()

    url = get_image_url(data['file_name'])

    # Create an HTML block with the stats and the image    
    return average_faces_html(data, url)

def render_network_graph_iframe(id):
    if not id:
        return "<p style='color:red;'>유효한 ID를 입력해주세요.</p>"
    # face_id를 사용해 해당 네트워크 그래프 페이지 URL 구성
    url = f"/network-graph/{id}"
    # iframe을 사용하여 페이지 로드. 스타일은 상황에 맞게 조정하세요.
    return f"<iframe src='{url}' style='width:100%; height:1000px; border:none;'></iframe>", ""

logger.info("Starting Gradio app...")

with gr.Blocks(theme=gr.themes.Monochrome(), css=css) as demo:

    selected_id = gr.Textbox(label="Current Face ID", elem_id="selected_id", interactive=False, visible=False)
    original_file_name = gr.Textbox(elem_id="original_file_name", visible=False)
    const_f_face_id = gr.Textbox(value="00000000-0000-0000-0000-000000000000", visible=False)
    const_m_face_id = gr.Textbox(value="11111111-1111-1111-1111-111111111111", visible=False)

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
        with gr.Row():
            female_average_button = gr.Button("Go to Network Graph")
            male_average_button = gr.Button("Go to Network Graph")

    with gr.Tab("Network Graph"):

        with gr.Row():
            input_id = gr.Textbox(label="Face ID", placeholder="Enter Face ID")
            view_button = gr.Button("View")

        network_output = gr.HTML(label="Network Graph", elem_classes="network-graph-html")
        progress_html = gr.HTML(label="Drawing Network Graph", elem_id="out_html")
        # (중요) data_table, network_output을 탭 내에서 새로 만들지 않고,
        #       이미 정의해둔 컴포넌트(data_table, network_output)를 "표시"만.
        view_button.click(
            fn=render_network_graph_iframe,
            inputs=input_id,
            outputs=[network_output, progress_html]
        )

    go_network_button.click(
        fn=render_network_graph_iframe,
        inputs=selected_id,                 # pass the hidden text ID
        outputs=[network_output, progress_html],
    ).then(
        fn=None,
        inputs=None,
        outputs=None,
        js=js_to_network_graph_tab
    )

    female_average_button.click(
        fn=render_network_graph_iframe,
        inputs=const_f_face_id,
        outputs=[network_output, average_output],
    ).then(
        fn=None,
        inputs=None,
        outputs=None,
        js=js_to_network_graph_tab
    )

    male_average_button.click(
        fn=render_network_graph_iframe,
        inputs=const_m_face_id,
        outputs=[network_output, average_output],
    ).then(
        fn=None,
        inputs=None,
        outputs=None,
        js=js_to_network_graph_tab
    )