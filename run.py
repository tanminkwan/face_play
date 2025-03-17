import os
import logging
import gradio as gr
import pandas as pd
from app.face_process import process_image
from app.file_process import get_image_list, get_presigned_url, upload_to_minio
from config import MINIO_PROCESSED_IMAGE_BUCKET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_image(image, photo_title, photo_id):
    logger.info("Uploading image...")
    result = process_image(image, photo_title, photo_id, upload_to_minio)
    logger.info(f"Image processed and saved to bucket: {result['bucket']}, file: {result['file_name']}")
    url = get_presigned_url(result["bucket"], result["file_name"])
    return f"<img src='{url}' style='max-width: 1080px; height: auto;'/>"

def list_images():
    logger.info("Fetching image list...")
    images = get_image_list()
    logger.info(f"Retrieved {len(images)} images.")

    # 예: 최대 10개만 추출
    data = images[:10]

    # Pandas DataFrame으로 변환
    df = pd.DataFrame(data, columns=["photo_id", "photo_title"])
    df.columns = ["Photo ID", "Photo Title"]  # 컬럼명 변경
    return df

def on_row_click(value, evt: gr.SelectData):
    """
    DataFrame에서 특정 행이 클릭되면 호출되는 핸들러.
    - value: DataFrame이 들고 있는 전체 값 (굳이 안 써도 됨)
    - evt: Gradio가 넘겨주는 이벤트 정보. evt.value가 클릭된 행의 데이터(dict 형태).
    """
    logger.info(f"[on_row_click] Entire value:\n{value}")
    logger.info(f"[on_row_click] Event data:\n{evt}")

    if evt.value is None:
        return ""
    selected_row = evt.value  # 딕셔너리 형태. 예: {"Photo ID": "xxx", "Photo Title": "yyy"}
    photo_id = selected_row.get("Photo ID", "")
    logger.info(f"Selected Photo ID: {photo_id}")
    return photo_id

def view_image_details(photo_id):
    """
    선택된 Photo ID로 실제 이미지를 조회한 뒤 <img> 태그를 반환
    """
    logger.info(f"Fetching details for photo ID: {photo_id}")
    if not photo_id:
        return "<p>No Photo ID selected.</p>"
    url = get_presigned_url(MINIO_PROCESSED_IMAGE_BUCKET, f"{photo_id}_processed.jpg")
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
            refresh_button = gr.Button("Refresh List")

            # DataFrame 컴포넌트. interactive=True를 설정하면 사용자가 행을 클릭할 수 있음
            image_list = gr.Dataframe(
                headers=["Photo ID", "Photo Title"],
                value=[],
                interactive=True
            )
            selected_photo_id = gr.Textbox(visible=False)

            # "Refresh List" 버튼을 누르면 list_images()를 실행해 DataFrame 갱신
            refresh_button.click(
                fn=list_images,
                outputs=image_list
            )

            # DataFrame의 행을 클릭하면 on_row_click 이벤트 핸들러가 실행됨
            image_list.select(
                fn=on_row_click,
                outputs=selected_photo_id
            )

            details_button = gr.Button("View Details")
            details_output = gr.HTML(label="Image Details")
            details_button.click(
                fn=view_image_details,
                inputs=selected_photo_id,
                outputs=details_output
            )

    demo.launch(debug=True)
    logger.info("Gradio app launched successfully.")
