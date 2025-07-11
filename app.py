import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
import os

# --- PDF File Manipulation Functions ---

# Function to extract text from the first page of a PDF
def extract_text_from_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        first_page = reader.pages[0]
        text = first_page.extract_text()
    return text

# Function to merge two PDFs
def merge_pdfs(pdf1_path, pdf2_path, output_path):
    pdf1 = PyPDF2.PdfReader(pdf1_path)
    pdf2 = PyPDF2.PdfReader(pdf2_path)
    
    pdf_writer = PyPDF2.PdfWriter()
    
    # Add all pages from the first PDF
    for page_num in range(len(pdf1.pages)):
        page = pdf1.pages[page_num]
        pdf_writer.add_page(page)
    
    # Add all pages from the second PDF
    for page_num in range(len(pdf2.pages)):
        page = pdf2.pages[page_num]
        pdf_writer.add_page(page)
    
    # Write the merged PDF to a new file
    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)

# --- PDF Generation Function using ReportLab ---
def create_pdf_with_reportlab(output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    c.drawString(100, 750, "Hello, Streamlit! This is a new PDF created with ReportLab.")
    c.save()

# --- Streamlit App UI ---

# Title of the app
st.title("PDF Manipulation with PyPDF2 & ReportLab")

# File uploader to upload a PDF
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract text from the uploaded PDF
    st.subheader("Extracted Text from the First Page:")
    extracted_text = extract_text_from_pdf("uploaded_file.pdf")
    st.text(extracted_text)

    # Merge with another uploaded PDF
    st.subheader("Merge with Another PDF:")
    second_pdf = st.file_uploader("Upload a second PDF file", type=["pdf"], key="second_pdf")
    
    if second_pdf is not None:
        with open("second_pdf.pdf", "wb") as f:
            f.write(second_pdf.getbuffer())
        
        output_pdf_path = "merged_output.pdf"
        merge_pdfs("uploaded_file.pdf", "second_pdf.pdf", output_pdf_path)
        st.write(f"Merged PDF saved as {output_pdf_path}")

        # Provide download link for the merged PDF
        with open(output_pdf_path, "rb") as f:
            st.download_button("Download Merged PDF", f, file_name="merged_output.pdf", mime="application/pdf")

# Button to create a new PDF with ReportLab
if st.button("Create New PDF with ReportLab"):
    new_pdf_path = "new_pdf_output.pdf"
    create_pdf_with_reportlab(new_pdf_path)
    st.write(f"New PDF created: {new_pdf_path}")
    
    # Provide download link for the newly created PDF
    with open(new_pdf_path, "rb") as f:
        st.download_button("Download New PDF", f, file_name="new_pdf_output.pdf", mime="application/pdf")
