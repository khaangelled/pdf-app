import streamlit as st
import io
import os
import tempfile
import uuid

# Configure page settings
st.set_page_config(
    page_title="PDF Live Editor",
    page_icon="📝",
    layout="wide"
)

# Check for required packages
try:
    import fitz  # PyMuPDF
    from PIL import Image
    PYMUPDF_AVAILABLE = True
except ImportError:
    st.error("PyMuPDF (fitz) package is missing. Please install it using: pip install pymupdf")
    PYMUPDF_AVAILABLE = False

try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    st.error("Streamlit-drawable-canvas package is missing. Please install it using: pip install streamlit-drawable-canvas")
    CANVAS_AVAILABLE = False

# Initialize session state variables
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'pdf_document' not in st.session_state:
    st.session_state.pdf_document = None
if 'total_pages' not in st.session_state:
    st.session_state.total_pages = 0
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 'annotations' not in st.session_state:
    st.session_state.annotations = {}
if 'text_annotations' not in st.session_state:
    st.session_state.text_annotations = {}
if 'current_tool' not in st.session_state:
    st.session_state.current_tool = "pen"

def load_pdf(pdf_file):
    """Load a PDF file and save it to session state."""
    if not PYMUPDF_AVAILABLE:
        st.error("Cannot load PDF: PyMuPDF is not available")
        return False
        
    try:
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_path = tmp_file.name
        
        # Open the PDF with PyMuPDF
        doc = fitz.open(tmp_path)
        st.session_state.pdf_document = doc
        st.session_state.total_pages = len(doc)
        st.session_state.current_page = 0
        st.session_state.pdf_path = tmp_path
        st.session_state.annotations = {i: [] for i in range(len(doc))}
        st.session_state.text_annotations = {i: [] for i in range(len(doc))}
        return True
    except Exception as e:
        st.error(f"Error loading PDF: {e}")
        return False

def render_pdf_page(page_num):
    """Render a specific page of the PDF."""
    if not PYMUPDF_AVAILABLE:
        st.error("Cannot render PDF: PyMuPDF is not available")
        return None
        
    if st.session_state.pdf_document is None:
        return None

    try:
        page = st.session_state.pdf_document[page_num]
        # Render the page to an image
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        st.error(f"Error rendering page: {e}")
        return None

def save_annotations_to_pdf():
    """Save all annotations to the PDF."""
    if not PYMUPDF_AVAILABLE:
        st.error("Cannot save annotations: PyMuPDF is not available")
        return None
        
    if st.session_state.pdf_document is None:
        return None
    
    try:
        # Create a copy of the original PDF
        doc = st.session_state.pdf_document
        
        # Add drawing annotations
        for page_num, annotations in st.session_state.annotations.items():
            if annotations:
                page = doc[page_num]
                for annotation in annotations:
                    # Convert stroke data to PDF annotation
                    points = annotation.get("points", [])
                    if points and len(points) > 1:
                        # Create path for the stroke
                        path = []
                        for i, point in enumerate(points):
                            x, y = point
                            if i == 0:
                                path.append((fitz.Point(x, y), "m"))
                            else:
                                path.append((fitz.Point(x, y), "l"))
                        
                        # Add the path as an ink annotation
                        color = annotation.get("stroke", "#FF0000")
                        thickness = annotation.get("strokeWidth", 2)
                        page.add_ink_annot([path], color=fitz.utils.getColorFromString(color), width=thickness)
        
        # Add text annotations
        for page_num, text_items in st.session_state.text_annotations.items():
            if text_items:
                page = doc[page_num]
                for item in text_items:
                    text = item.get("text", "")
                    x = item.get("x", 100)
                    y = item.get("y", 100)
                    page.add_text_annot(fitz.Point(x, y), text, icon="Note")
        
        # Save the document to a BytesIO object
        output_buffer = io.BytesIO()
        doc.save(output_buffer)
        output_buffer.seek(0)
        return output_buffer
    except Exception as e:
        st.error(f"Error saving annotations: {e}")
        return None

def add_drawing_annotation(stroke_data, page_num):
    """Add a drawing annotation to the current page."""
    if page_num not in st.session_state.annotations:
        st.session_state.annotations[page_num] = []
    st.session_state.annotations[page_num].append(stroke_data)

def add_text_annotation(text, x, y, page_num):
    """Add a text annotation to the current page."""
    if page_num not in st.session_state.text_annotations:
        st.session_state.text_annotations[page_num] = []
    st.session_state.text_annotations[page_num].append({
        "text": text,
        "x": x,
        "y": y,
    })

# App Header
st.title("PDF Live Editor")
st.write("Upload a PDF file and edit it online")

# Package version info
if not PYMUPDF_AVAILABLE or not CANVAS_AVAILABLE:
    st.error("⚠️ Some required packages are missing. Please check the error messages above.")
    st.info("To fix this issue, run: pip install pymupdf streamlit-drawable-canvas")

# Sidebar for PDF upload and controls
with st.sidebar:
    st.header("Controls")
    
    # PDF Upload
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file is not None and (st.session_state.pdf_document is None or 
                                      uploaded_file.name != getattr(st.session_state, 'last_uploaded_file_name', None)):
        st.session_state.last_uploaded_file_name = uploaded_file.name
        if load_pdf(uploaded_file):
            st.success("PDF loaded successfully!")
    
    if st.session_state.pdf_document is not None:
        # Page Navigation
        st.subheader("Page Navigation")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Previous Page", key="prev_page"):
                if st.session_state.current_page > 0:
                    st.session_state.current_page -= 1
        
        with col2:
            if st.button("Next Page", key="next_page"):
                if st.session_state.current_page < st.session_state.total_pages - 1:
                    st.session_state.current_page += 1
        
        st.write(f"Page: {st.session_state.current_page + 1}/{st.session_state.total_pages}")
        
        # Jump to page
        jump_page = st.number_input("Jump to page", min_value=1, 
                                    max_value=st.session_state.total_pages, 
                                    value=st.session_state.current_page + 1)
        if st.button("Go"):
            st.session_state.current_page = jump_page - 1
        
        if CANVAS_AVAILABLE:
            # Annotation Tools
            st.subheader("Annotation Tools")
            tool = st.radio(
                "Select tool",
                ["pen", "highlighter", "text", "eraser"],
                key="tool_selection"
            )
            st.session_state.current_tool = tool
            
            # Tool settings
            if tool in ["pen", "highlighter"]:
                stroke_color = st.color_picker("Color", "#FF0000" if tool == "pen" else "#FFFF00")
                stroke_width = st.slider("Width", min_value=1, max_value=10, value=2 if tool == "pen" else 5)
            
            elif tool == "text":
                text_content = st.text_input("Text content", "Note")
                st.session_state.text_content = text_content
        else:
            st.warning("Annotation tools are not available because streamlit-drawable-canvas is not installed.")
        
        # Save button
        if st.button("Save Edited PDF"):
            edited_pdf = save_annotations_to_pdf()
            if edited_pdf:
                st.download_button(
                    label="Download edited PDF",
                    data=edited_pdf,
                    file_name="edited_document.pdf",
                    mime="application/pdf"
                )

# Main area for PDF display and editing
if st.session_state.pdf_document is not None and PYMUPDF_AVAILABLE:
    # Get the current page image
    page_image = render_pdf_page(st.session_state.current_page)
    
    if page_image:
        # Display current page number
        st.subheader(f"Page {st.session_state.current_page + 1} of {st.session_state.total_pages}")
        
        # Create a unique key for the canvas
        canvas_key = f"canvas_{st.session_state.current_page}_{uuid.uuid4()}"
        
        if CANVAS_AVAILABLE:
            # Determine tool settings
            drawing_mode = {
                "pen": "freedraw",
                "highlighter": "freedraw",
                "text": "transform",
                "eraser": "freedraw"
            }[st.session_state.current_tool]
            
            stroke_color = "#FF0000"  # Default red for pen
            stroke_width = 2
            
            if st.session_state.current_tool == "highlighter":
                stroke_color = "rgba(255, 255, 0, 0.5)"  # Transparent yellow
                stroke_width = 5
            elif st.session_state.current_tool == "eraser":
                stroke_color = "#FFFFFF"
                stroke_width = 10
            
            # Convert PIL Image to bytes for display
            img_bytes = io.BytesIO()
            page_image.save(img_bytes, format="PNG")
            img_data = img_bytes.getvalue()
            
            try:
                # Create drawable canvas over the PDF page
                # Avoid using use_container_width which is not supported
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    background_image=page_image,  # Pass the PIL Image directly
                    update_streamlit=True,
                    height=page_image.height,
                    width=page_image.width,
                    drawing_mode=drawing_mode,
                    key=canvas_key
                )
                
                # Handle drawing annotations
                if canvas_result.json_data is not None:
                    objects = canvas_result.json_data.get("objects")
                    if objects:
                        last_object = objects[-1]
                        if st.session_state.current_tool in ["pen", "highlighter"] and "path" in last_object:
                            add_drawing_annotation(last_object, st.session_state.current_page)
                        elif st.session_state.current_tool == "text":
                            # Get text position from click
                            if canvas_result.json_data.get("objects"):
                                for obj in canvas_result.json_data.get("objects"):
                                    if obj.get("type") == "rect":
                                        x = obj.get("left", 0)
                                        y = obj.get("top", 0)
                                        text = st.session_state.get("text_content", "Note")
                                        add_text_annotation(text, x, y, st.session_state.current_page)
            except Exception as e:
                st.error(f"Error with drawing canvas: {e}")
                # Use width_column without the deprecated parameter
                st.image(page_image)
        else:
            # If canvas is not available, just display the PDF image
            st.warning("Drawing functionality is not available. Please install streamlit-drawable-canvas.")
            # Use width_column without the deprecated parameter
            st.image(page_image)
else:
    st.info("Please upload a PDF file from the sidebar to begin editing.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        PDF Live Editor - Edit your PDFs online similar to Microsoft Edge PDF editor
    </div>
    """, 
    unsafe_allow_html=True
)
