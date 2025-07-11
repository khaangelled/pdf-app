import streamlit as st
import base64
from PIL import Image

# عرض عنوان
st.title("PDF Editor with Interactive Toolbar")

# رفع ملف PDF
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# إذا تم رفع الملف، نعرضه داخل التطبيق
if uploaded_file is not None:
    pdf_data = base64.b64encode(uploaded_file.read()).decode('utf-8')  # تحويل PDF إلى Base64
    
    # HTML & JavaScript لإنشاء شريط الأدوات وتفاعلاته
    pdf_html = f"""
    <html>
        <head>
            <style>
                .toolbar {{
                    background-color: #f1f1f1;
                    padding: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .toolbar button {{
                    padding: 10px;
                    margin: 5px;
                    cursor: pointer;
                    background-color: #e0e0e0;
                    border: none;
                    border-radius: 4px;
                }}
                .pdf-canvas {{
                    width: 100%;
                    height: 600px;
                    border: 1px solid #ccc;
                }}
            </style>
        </head>
        <body>
            <div class="toolbar">
                <button onclick="zoomIn()">Zoom In</button>
                <button onclick="zoomOut()">Zoom Out</button>
                <button onclick="addText()">Add Text</button>
                <button onclick="highlightText()">Highlight</button>
                <button onclick="searchText()">Search</button>
            </div>
            <canvas id="pdf-canvas" class="pdf-canvas"></canvas>
            <div>
                <input type="text" id="add-text" placeholder="Enter text here">
                <button onclick="placeText()">Place Text on PDF</button>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.min.js"></script>
            <script>
                var pdfData = atob("{pdf_data}");
                var canvas = document.getElementById('pdf-canvas');
                var ctx = canvas.getContext('2d');
                var pdfDoc = null;
                var pageNum = 1;
                var pageRendering = false;

                function renderPage(num) {{
                    pageRendering = true;
                    pdfDoc.getPage(num).then(function(page) {{
                        var viewport = page.getViewport({{ scale: 1 }});
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        var renderContext = {{
                            canvasContext: ctx,
                            viewport: viewport
                        }};
                        page.render(renderContext).promise.then(function() {{
                            pageRendering = false;
                        }});
                    }});
                }}

                pdfjsLib.getDocument({{data: pdfData}}).promise.then(function(pdf) {{
                    pdfDoc = pdf;
                    renderPage(pageNum);
                }});

                function zoomIn() {{
                    canvas.style.transform = "scale(1.2)";
                }}

                function zoomOut() {{
                    canvas.style.transform = "scale(0.8)";
                }}

                function addText() {{
                    var text = document.getElementById('add-text').value;
                    var x = 100;
                    var y = 100;
                    ctx.fillStyle = 'black';
                    ctx.font = '20px Arial';
                    ctx.fillText(text, x, y);
                }}
            </script>
        </body>
    </html>
    """
    
    # عرض شريط الأدوات مع الـ PDF
    st.components.v1.html(pdf_html, height=800)
