from jinja2 import Environment, FileSystemLoader, Template
import os
from app import storage
from config import S3_IMAGE_BUCKET

def average_faces_html(data, url):
    return f"""
    <div style="width: 100%; max-width: 1080px; margin: auto; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 20px;">

            <!-- 여성 정보 div -->
            <div 
                style="flex: 1; padding: 10px; text-align: center; border: 1px solid #ddd; margin-right: 5px; border-radius: 8px; cursor: pointer;"
            >
                <h3>여성 정보</h3>
                <p><strong>참여자 수:</strong> {data['f_num_people']}</p>
                <p><strong>평균 나이:</strong> {data['f_age']:.2f}</p>
            </div>

            <!-- 남성 정보 div -->
            <div 
                style="flex: 1; padding: 10px; text-align: center; border: 1px solid #ddd; margin-left: 5px; border-radius: 8px; cursor: pointer;"
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
        
        nodes.append({
            'id': item.id,
            'photo_id': item.photo_id,
            'name': item.photo_title,
            'gender': "Male" if item.gender == 1 else "Female",
            'age': item.age,
            'score': item.score,
            'face_index': item.face_index if item.face_index else 0,
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

def render_images_table(images):
    """
    images: [{face_id, photo_id, photo_title, age, gender, face_index, file_name}, ...]
    """
    template_str = """
<table border="1" style="border-collapse: collapse;">
    <thead>
        <tr>
            <th>Face ID</th>
            <th>Photo ID</th>
            <th>Photo Title</th>
            <th>Age</th>
            <th>Gender</th>
            <th>Face Index</th>
            <!-- File Name 헤더는 숨김 -->
            <th style="display:none;">File Name</th>
        </tr>
    </thead>
    <tbody>
    {% for row in images %}
        <tr style="cursor:pointer;" 
            onclick="(function(){
                var rows = this.parentNode.querySelectorAll('tr');
                for(var i=0; i < rows.length; i++){
                    rows[i].style.backgroundColor = '';
                }
                window.rowClick('{{ row['face_id'] }}', '{{ row['file_name'] }}');
                this.style.setProperty('background-color', '#808080', 'important');
            }).call(this);">
            <td>{{ row['face_id'] }}</td>
            <td>{{ row['photo_id'] }}</td>
            <td>{{ row['photo_title'] }}</td>
            <td>{{ row['age'] }}</td>
            <td>{{ 'Male' if row['gender'] else 'Female'}}</td>
            <td>{{ row['face_index'] }}</td>
            <!-- File Name 칼럼은 숨김 -->
            <td style="display:none;">{{ row['file_name'] }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
    """

    # jinja2 템플릿 렌더링
    template = Template(template_str)
    return template.render(images=images)