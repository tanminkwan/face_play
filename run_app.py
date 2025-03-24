from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
from app.routes import router as app_router
from ui.gradio_app import demo  # Gradio 앱 UI

app = FastAPI()

# static 폴더를 정적으로 서빙
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 등록
app.include_router(app_router) 

# Gradio 앱을 FastAPI에 통합
app = gr.mount_gradio_app(app, demo, path="/")