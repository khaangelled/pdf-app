import streamlit as st
from ironpdf import ChromePdfRenderer, PdfDocument, PdfSignature
from datetime import datetime

# Initialize PDF renderer
renderer = ChromePdfRenderer()

# Helper function to render HTML as PDF
def render_pdf_from_html(html_content):
    pdf = renderer.RenderHtmlAsPdf(html_content)
    return pdf

# Function to edit an existing PDF
def edit_pdf(input_pdf):
    # Load the existing PDF document
    pdf = PdfDocument(input_pdf)
    
    # Example: Add a footer to the PDF
    renderer.RenderingOptions.HtmlFooter = "<center><i>{page} of {total-pages}<i></center>"
    renderer.RenderingOptions.HtmlFooter.DrawDividerLine = True
    renderer.RenderingOptions.MarginBottom = 25  # mm
    
    # Add watermark (Text or Image)
    pdf.ApplyWatermark("<h2 style='color:red'>SAMPLE</h2>", 30, VerticalAlignment.Middle, HorizontalAlignment.Center)
    
    # Save the edited PDF
    pdf.SaveAs("edited_output.pdf")

# Streamlit UI to get HTML input from user
st.title("Online PDF Editor")
st.write("Use this app to edit your PDFs by adding footers, watermarks, or modifying content.")

# Text input for HTML content
html_content = st.text_area("Enter HTML Content for PDF:", "<h1>Hello, World!</h1>")

# Button to generate PDF from HTML content
if st.button("Generate PDF"):
    pdf = render_pdf_from_html(html_content)
    pdf.SaveAs("generated_pdf.pdf")
    st.success("PDF generated successfully!")
    st.download_button("Download PDF", "generated_pdf.pdf", "application/pdf")

# Upload a PDF to edit
uploaded_file = st.file_uploader("Choose a PDF file to edit", type="pdf")

if uploaded_file is not None:
    # Display the uploaded PDF
    st.write("Preview of Uploaded PDF:")
    st.write(uploaded_file.name)
    
    # Call the edit function to add watermark
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(uploaded_file.read())
    
    edit_pdf("temp_uploaded.pdf")
    st.success("PDF edited successfully!")
    st.download_button("Download Edited PDF", "edited_output.pdf", "application/pdf")
