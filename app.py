import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

# تحميل ملف PDF
st.title("تطبيق Edge PDF مع Streamlit")
uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    # فتح ملف PDF باستخدام PyMuPDF
    doc = fitz.open(io.BytesIO(uploaded_file.read()))

    # عرض الصفحات في Streamlit
    page_num = st.slider("اختر رقم الصفحة", 1, len(doc), 1)
    page = doc.load_page(page_num - 1)
    
    # تحويل الصفحة إلى صورة لعرضها في Streamlit
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # عرض الصورة في Streamlit
    st.image(img)

    # إضافة تعليق (ملاحظة)
    comment = st.text_input("أضف تعليقًا على الصفحة:")
    if comment:
        # إضافة تعليق على الصفحة
        rect = fitz.Rect(50, 50, 300, 100)  # المنطقة التي سيظهر فيها التعليق
        page.add_text_annot(rect, comment)
        doc.save("output.pdf")

    # إبراز النصوص
    highlight = st.text_input("أدخل النص للإبراز:")
    if highlight:
        # البحث عن النص
        text_instances = page.search_for(highlight)
        for inst in text_instances:
            page.add_highlight_annot(inst)
        doc.save("output_highlighted.pdf")

    # تحميل التوقيع (صورة التوقيع)
    signature = st.file_uploader("رفع توقيعك", type=["png", "jpg"])
    if signature is not None:
        signature_img = Image.open(signature)
        signature_bytes = io.BytesIO()
        signature_img.save(signature_bytes, format="PNG")
        
        # إضافة التوقيع على الصفحة
        page.insert_image(fitz.Rect(50, 150, 150, 250), stream=signature_bytes.getvalue())
        doc.save("output_signed.pdf")

    # عرض خيارات حفظ الملف
    st.download_button("تحميل PDF المعدل", data=open("output.pdf", "rb").read(), file_name="output.pdf")
    st.download_button("تحميل PDF مع التوقيع", data=open("output_signed.pdf", "rb").read(), file_name="output_signed.pdf")
    st.download_button("تحميل PDF مع الإبراز", data=open("output_highlighted.pdf", "rb").read(), file_name="output_highlighted.pdf")
