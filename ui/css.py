css=\
"""
/* 전체 app에서 이미지와 컨테이너가 화면을 초과하지 않게 함 */
.gradio-container {
    max-width: 100% !important;
    overflow-x: hidden !important;
}

img {
    max-width: 100% !important;
    height: auto !important;
}

#out_html {
    max-height: none !important;
    overflow: visible !important;
}
"""