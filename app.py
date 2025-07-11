import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.title("PDF Viewer and Editor")

# تحميل ملف PDF
uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    # فتح ملف PDF
    doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
    
    # عرض الصفحات
    page_num = st.slider("اختر رقم الصفحة", 1, len(doc), 1)
    page = doc.load_page(page_num - 1)
    
    # تحويل الصفحة إلى صورة لعرضها في Streamlit
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # عرض الصورة
    st.image(img, caption="Page {}".format(page_num))
    
    # إضافة مربع نص أو تعليق (تفاعل مباشر مع الصفحة)
    st.subheader("أضف تعليقًا أو نصًا")
    
    # نعرض قائمة الأدوات في الأعلى
    selected_tool = st.selectbox("اختر الأداة", ["أداة النص", "أداة الإبراز", "أداة التوقيع"])
    
    if selected_tool == "أداة النص":
        # تحديد مكان النص الذي نريد إضافته
        x_pos = st.slider("الموضع الأفقي للنص", 0, pix.width, 100)
        y_pos = st.slider("الموضع الرأسي للنص", 0, pix.height, 100)
        text = st.text_input("اكتب النص الذي تريد إضافته:")
        
        if text:
            # إضافة النص إلى الصفحة
            rect = fitz.Rect(x_pos, y_pos, x_pos + 200, y_pos + 30)
            page.insert_text(rect.tl, text, fontsize=12)
            doc.save("output_with_text.pdf")

    elif selected_tool == "أداة الإبراز":
        highlight_text = st.text_input("اكتب النص للإبراز:")
        if highlight_text:
            # البحث عن النص وتحديده للإبراز
            text_instances = page.search_for(highlight_text)
            for inst in text_instances:
                page.add_highlight_annot(inst)
            doc.save("output_with_highlight.pdf")

    elif selected_tool == "أداة التوقيع":
        signature = st.file_uploader("رفع توقيعك", type=["png", "jpg"])
        if signature is not None:
            signature_img = Image.open(signature)
            signature_bytes = io.BytesIO()
            signature_img.save(signature_bytes, format="PNG")
            
            # إضافة التوقيع
            page.insert_image(fitz.Rect(50, 150, 150, 250), stream=signature_bytes.getvalue())
            doc.save("output_with_signature.pdf")

    # تحميل النسخ المعدلة
    st.download_button("تحميل PDF مع النصوص", data=open("output_with_text.pdf", "rb").read(), file_name="output_with_text.pdf")
    st.download_button("تحميل PDF مع الإبراز", data=open("output_with_highlight.pdf", "rb").read(), file_name="output_with_highlight.pdf")
    st.download_button("تحميل PDF مع التوقيع", data=open("output_with_signature.pdf", "rb").read(), file_name="output_with_signature.pdf")
