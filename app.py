import streamlit as st
import fitz  # PyMuPDF

# Title of the app
st.title("PDF Editor using Python and Streamlit")

# Description
st.markdown("Upload a PDF, view it, and add text annotations.")

# Upload a PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Check if a PDF is uploaded
if uploaded_file is not None:
    # Open the uploaded PDF with PyMuPDF (fitz)
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    # Display the first page of the PDF
    page_number = 0
    page = doc.load_page(page_number)
    pix = page.get_pixmap()
    img = pix.tobytes("png")
    
    # Show the image of the first page in Streamlit
    st.image(img)

    # Add text to the PDF
    text_to_add = st.text_input("Enter the text you want to add:", "")
    
    if st.button("Add Text"):
        if text_to_add:
            # Add text to the first page at position (100, 100)
            page.insert_text((100, 100), text_to_add, fontsize=12, color=(0, 0, 0))

            # Save the modified PDF
            output_pdf_path = "edited_output.pdf"
            doc.save(output_pdf_path)

            # Let the user download the modified PDF
            st.success("Text added successfully!")
            st.download_button("Download the modified PDF", output_pdf_path, file_name="edited_output.pdf")

        else:
            st.warning("Please enter text to add to the PDF.")

else:
    st.warning("Please upload a PDF file.")
