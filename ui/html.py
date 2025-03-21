def average_faces_html(data, url):
    return f"""
    <div style="width: 100%; max-width: 1080px; margin: auto; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 20px;">
            <div style="flex: 1; padding: 10px; text-align: center; border: 1px solid #ddd; margin-right: 5px; border-radius: 8px;">
                <h3>여성 정보</h3>
                <p><strong>참여자 수:</strong> {data['f_num_people']}</p>
                <p><strong>평균 나이:</strong> {data['f_age']:.2f}</p>
            </div>
            <div style="flex: 1; padding: 10px; text-align: center; border: 1px solid #ddd; margin-left: 5px; border-radius: 8px;">
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
import os

def network_graph_html(data, main_node_id):
    """
    data: [{'photo_title': str, 'photo_id': str, 'score': float, 'gender': int, 'age': int}, ...]
    main_node_id: str (중심 노드의 photo_id)
    """
    nodes = []
    links = []

    # 노드 생성
    for item in data:
        nodes.append({
            'id': item['photo_id'],
            'name': item['photo_title'],
            'gender': item['gender'],
            'age': item['age'],
            'score': item['score']
        })

    # 중심 노드를 기준으로 링크 생성
    for item in data:
        if item['photo_id'] != main_node_id:
            links.append({
                'source': main_node_id,
                'target': item['photo_id'],
                'score': item['score']
            })

    import json
    graph_data = json.dumps({"nodes": nodes, "links": links})

    # 완전한 HTML 문서 (중괄호 이스케이프 처리)
    html_template = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <title>Network Graph</title>
        <script src='https://d3js.org/d3.v7.min.js'></script>
        <style>
            body {{ margin: 0; font-family: Arial; }}
            .link {{ stroke: #999; stroke-opacity: 0.6; }}
            .label {{ font-size: 12px; pointer-events: none; }}
        </style>
    </head>
    <body>
        <div id='graph'></div>
        <script>
            const data = __GRAPH_DATA__;
            const width = window.innerWidth;
            const height = window.innerHeight;

            const svg = d3.select('#graph').append('svg')
                .attr('width', width)
                .attr('height', height);

            function drag(simulation) {
                return d3.drag()
                    .on('start', function(event, d) {
                        if (!event.active) simulation.alphaTarget(0.3).restart();
                        d.fx = d.x;
                        d.fy = d.y;
                    })
                    .on('drag', function(event, d) {
                        d.fx = event.x;
                        d.fy = event.y;
                    })
                    .on('end', function(event, d) {
                        if (!event.active) simulation.alphaTarget(0);
                        d.fx = null;
                        d.fy = null;
                    });
            }

            const simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links).id(d => d.id).distance(200))
                .force('charge', d3.forceManyBody().strength(-400))
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.selectAll('.link')
                .data(data.links)
                .enter().append('line')
                .attr('class', 'link')
                .attr('stroke', '#999')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', d => Math.max(d.score * 10, 3));

            // 링크 위에 텍스트 (score)
            const linkLabel = svg.selectAll('.link-label')
                .data(data.links)
                .enter().append('text')
                .attr('class', 'label')
                .text(d => d.score.toFixed(2));

            const node = svg.selectAll('.node')
                .data(data.nodes)
                .enter().append('g')
                .attr('class', 'node')
                .call(drag(simulation));

            node.append('circle')
                .attr('r', 15)
                .attr('fill', d => d.gender === 0 ? '#ffb6c1' : '#add8e6')
                .attr('stroke', '#555')
                .attr('stroke-width', 2)
                .on('click', function(event, d) {
                    const connectedLink = data.links.find(l => l.target === d.id || l.source === d.id);
                    const score = connectedLink ? connectedLink.score.toFixed(2) : 'N/A';
                    alert(
                        'Photo ID: ' + d.id + "\\n" +
                        'Name: ' + d.name + "\\n" +
                        'Gender: ' + d.gender + "\\n" +
                        'Age: ' + d.age + "\\n" +
                        'Score: ' + d.score
                    );
                });

            node.append('text')
                .attr('class', 'label')
                .attr('dy', 4)
                .attr('x', 20)
                .text(d => d.id);

            simulation.on('tick', function() {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                linkLabel
                    .attr('x', d => (d.source.x + d.target.x) / 2)
                    .attr('y', d => (d.source.y + d.target.y) / 2);

                node
                    .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });
            });
        </script>
    </body>
    </html>
    """

    html_content = html_template.replace("__GRAPH_DATA__", graph_data)

    # 웹 배포 환경을 고려해 static 디렉토리에 저장
    static_dir = os.path.join(os.getcwd(), "static")
    os.makedirs(static_dir, exist_ok=True)
    file_name = f"graph_{main_node_id}.html"
    file_path = os.path.join(static_dir, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return f"<p>그래프가 <a href='/static/{file_name}' target='_blank'>새 창</a>에서 열립니다.</p>"
