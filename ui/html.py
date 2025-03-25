from jinja2 import Environment, FileSystemLoader, Template
import os
from app import storage
from config import S3_IMAGE_BUCKET

def average_faces_html(data, url):
    template_str = """
    <div style="width: 100%; max-width: 1080px; margin: auto; font-family: sans-serif; position: relative;">
        <img src="{{ url }}" style="width:100%; height:auto; max-width: 1080px; border-radius: 8px;"/>
        <div style="position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(0, 0, 0, 0.5); color: #fff; padding: 10px; border-radius: 0 0 8px 8px;">
            <div style="display: flex; justify-content: space-between;">
                <!-- 여성 정보 div -->
                <div style="flex: 1; text-align: center;">
                    <h3 style="margin: 0;">여성 정보</h3>
                    <p style="margin: 0;"><strong>참여자 수:</strong> {{ data['f_num_people'] }}</p>
                    <p style="margin: 0;"><strong>평균 나이:</strong> {{ data['f_age']|round(2) }}</p>
                </div>
                <!-- 남성 정보 div -->
                <div style="flex: 1; text-align: center;">
                    <h3 style="margin: 0;">남성 정보</h3>
                    <p style="margin: 0;"><strong>참여자 수:</strong> {{ data['m_num_people'] }}</p>
                    <p style="margin: 0;"><strong>평균 나이:</strong> {{ data['m_age']|round(2) }}</p>
                </div>
            </div>
        </div>
    </div>
    """

    template = Template(template_str)
    return template.render(data=data, url=url)

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

def images_table_html(images):
    """
    images: [{face_id, photo_id, photo_title, age, gender, face_index, file_name}, ...]
    """
    template_str = """
<table border="1" style="border-collapse: collapse;">
    <thead>
        <tr>
            <th>Face ID</th>
            <th>Photo ID(+index)</th>
            <th>Photo Title</th>
            <th>Age</th>
            <th>Gender</th>
            <th style="display:none;">Face Index</th>
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
            <td>{{ row['photo_id'] }}__{{ row['face_index'] }}</td>
            <td>{{ row['photo_title'] }}</td>
            <td>{{ row['age'] }}</td>
            <td>{{ 'Male' if row['gender'] else 'Female'}}</td>
            <td style="display:none;">{{ row['face_index'] }}</td>
            <td style="display:none;">{{ row['file_name'] }}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
    """

    # jinja2 템플릿 렌더링
    template = Template(template_str)
    return template.render(images=images)