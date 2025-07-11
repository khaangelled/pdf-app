import streamlit as st
import base64
import io
from PIL import Image

# Title
st.title("Interactive PDF Editor")

# Upload PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Display PDF as image or use pdf.js (We'll use PDF.js embedded in HTML/JS below)
    
    # Embed PDF.js with HTML and JS
    pdf_data = base64.b64encode(uploaded_file.read()).decode('utf-8')  # convert file to base64
    
    # HTML template to load PDF and add interactivity
    pdf_html = f"""
    <html>
        <body>
            <h1>PDF Viewer & Editor</h1>
            <canvas id="pdf-canvas" width="800" height="600"></canvas>
            <div>
                <label for="add-text">Add Text:</label>
                <input type="text" id="add-text" placeholder="Enter text here" />
                <button onclick="addText()">Add Text to PDF</button>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.min.js"></script>
            <script>
                var pdfData = atob("{pdf_data}"); // Decode base64 data
                var canvas = document.getElementById('pdf-canvas');
                var ctx = canvas.getContext('2d');
                var pdfDoc = null;
                var pageNum = 1;
                var pageRendering = false;
                var pageNumPending = null;

                // Load the PDF
                function renderPage(num) {
                    pageRendering = true;
                    pdfDoc.getPage(num).then(function(page) {
                        var viewport = page.getViewport({ scale: 1 });
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        var renderContext = {
                            canvasContext: ctx,
                            viewport: viewport
                        };
                        page.render(renderContext).promise.then(function() {
                            pageRendering = false;
                            if (pageNumPending !== null) {
                                renderPage(pageNumPending);
                                pageNumPending = null;
                            }
                        });
                    });
                }

                pdfjsLib.getDocument({data: pdfData}).promise.then(function(pdf) {
                    pdfDoc = pdf;
                    renderPage(pageNum);
                });

                // Add text on canvas
                function addText() {
                    var text = document.getElementById('add-text').value;
                    var x = Math.random() * canvas.width;
                    var y = Math.random() * canvas.height;
                    ctx.fillStyle = 'black';
                    ctx.font = '20px Arial';
                    ctx.fillText(text, x, y);
                }
            </script>
        </body>
    </html>
    """

    # Render HTML content in Streamlit app
    st.components.v1.html(pdf_html, height=800)
