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
