from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from ui.html import network_graph_html
from app.face_process import view_network_graph
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/network-graph/{id}", response_class=HTMLResponse)
def get_network_graph(id: str):
    logger.info(f"Generating network graph for ID: {id}")

    data, main_node_id = view_network_graph(id)
    if not data:
        return "<p style='color:red;'>No data found for the given ID.</p>"

    return network_graph_html(data, main_node_id)
