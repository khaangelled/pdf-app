import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas
import tempfile

# Title of the app
st.title("Live PDF Editor with Streamlit")

# Description
st.markdown("Upload a PDF, view it, add text annotations, and draw on it.")

# Upload a PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Session state to hold the PDF document
if 'doc' not in st.session_state:
    st.session_state.doc = None

# Check if a PDF is uploaded
if uploaded_file is not None:
    # Open the uploaded PDF with PyMuPDF (fitz)
    st.session_state.doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.session_state.page_number = 0

    # Display the first page of the PDF
    page = st.session_state.doc.load_page(st.session_state.page_number)
    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    # Save the image to a temporary file to use in st_canvas
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
        img.save(tmpfile, format="PNG")
        tmpfile_path = tmpfile.name

    # Show the image of the first page in Streamlit
    st.image(img)

    # Text input for adding text annotations
    text_to_add = st.text_input("Enter the text you want to add:", "")

    # Add text to PDF
    if st.button("Add Text"):
        if text_to_add:
            page = st.session_state.doc.load_page(st.session_state.page_number)
            page.insert_text((100, 100), text_to_add, fontsize=12, color=(0, 0, 0))
            st.session_state.doc.save("temp.pdf")
            st.success("Text added successfully!")
        else:
            st.warning("Please enter text to add to the PDF.")

    # Canvas for Drawing Annotations using `streamlit-drawable-canvas`
    st.subheader("Draw on the PDF:")

    # Create a canvas for free drawing
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Transparent drawing color
        width=img.width,
        height=img.height,
        drawing_mode="freedraw",
        key="drawing",
        background_image=tmpfile_path,  # Pass the temp image path
        stroke_width=3,
        stroke_color="black",
        display_toolbar=True,
    )

    # If there is any drawing, get coordinates and apply them to the PDF
    if canvas_result.json_data is not None:
        coords = canvas_result.json_data["objects"]
        for coord in coords:
            if coord["type"] == "path":
                points = coord["path"]
                page = st.session_state.doc.load_page(st.session_state.page_number)
                page.draw_lines(points, color=(255, 0, 0), width=2)
        
        # Save the updated PDF with drawings
        st.session_state.doc.save("temp.pdf")
        st.success("Drawing updated!")

    # Download the modified PDF
    st.download_button(
        label="Download the modified PDF",
        data=open("temp.pdf", "rb").read(),
        file_name="edited_output.pdf",
        mime="application/pdf"
    )

else:
    st.warning("Please upload a PDF file.")
