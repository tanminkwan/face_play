def average_faces_html(data, url):
    return f"""
    <div style="width: 100%; max-width: 1080px; margin: auto; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 20px;">

            <!-- 여성 정보 div -->
            <div 
                style="flex: 1; padding: 10px; text-align: center; border: 1px solid #ddd; margin-right: 5px; border-radius: 8px; cursor: pointer;"
                onclick="window.open('/network-graph/00000000-0000-0000-0000-000000000000', '_blank');"
            >
                <h3>여성 정보</h3>
                <p><strong>참여자 수:</strong> {data['f_num_people']}</p>
                <p><strong>평균 나이:</strong> {data['f_age']:.2f}</p>
            </div>

            <!-- 남성 정보 div -->
            <div 
                style="flex: 1; padding: 10px; text-align: center; border: 1px solid #ddd; margin-left: 5px; border-radius: 8px; cursor: pointer;"
                onclick="window.open('/network-graph/11111111-1111-1111-1111-111111111111', '_blank');"
            >
                <h3>남성 정보</h3>
                <p><strong>참여자 수:</strong> {data['m_num_people']}</p>
                <p><strong>평균 나이:</strong> {data['m_age']:.2f}</p>
            </div>
        </div>
        <div style="text-align: center;">
            <img src="{url}" style="width:100%; height:auto; max-width: 1080px; border-radius: 8px;"/>
        </div>
    </div>
    """

# ui/html.py에 추가할 코드
from jinja2 import Environment, FileSystemLoader
import os
from app import storage
from config import S3_IMAGE_BUCKET

def network_graph_html(data, main_node_id):
    """
    Render the network graph HTML using Jinja2.

    :param data: List of dictionaries containing node and link data.
    :param main_node_id: The ID of the main node.
    :return: Rendered HTML as a string.
    """
    nodes = []
    links = []

    # Prepare nodes and links
    for item in data:
        file_name = f"{item.id}.jpg"
        file_url = storage.get_file_url(S3_IMAGE_BUCKET, file_name)
        print(file_url)
        nodes.append({
            'id': item.id,
            'photo_id': item.photo_id,
            'name': item.photo_title,
            'gender': "Male" if item.gender == 1 else "Female",
            'age': item.age,
            'score': item.score,
            'face_index': item.face_index,
            'file_url': file_url
        })

    for item in data:
        if item.id != main_node_id:
            links.append({
                'source': main_node_id,
                'target': item.id,
                'score': item.score
            })

    sorted_nodes = sorted(nodes, key=lambda x: x['score'], reverse=True)
    graph_data = {"nodes": sorted_nodes, "links": links}

    # Load the Jinja2 template
    template_dir = os.path.join(os.getcwd(), "ui")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("network_graph.html")

    # Render the template with graph data
    return template.render(graph_data=graph_data)