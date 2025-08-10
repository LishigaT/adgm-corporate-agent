import streamlit as st
from docx import Document
import google.generativeai as genai
from io import BytesIO

# --- Streamlit Page Config ---
st.set_page_config(page_title="ADGM Corporate Agent", layout="wide")

# --- Load Gemini API Key from Streamlit secrets ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# --- App Title ---
st.title("🏢 ADGM Corporate Agent – Compliance Checker")
st.write("Upload your company documents (.docx) to check for ADGM compliance.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])

def extract_text_from_docx(file):
    """Extracts text from uploaded DOCX file."""
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())
    return "\n".join(full_text)

def check_document_with_adgm(full_text):
    """Sends the entire document to Gemini for compliance checking."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are an ADGM Corporate Agent compliance checker.
    Analyze the following document for ADGM compliance issues.
    For each clause:
    - State if it's Compliant or Non-Compliant
    - Give details of the issue (if any)
    - Suggest a correction if non-compliant

    Document:
    {full_text}
    """
    response = model.generate_content(prompt)
    return response.text

# --- Processing ---
if uploaded_file:
    text = extract_text_from_docx(uploaded_file)
    st.subheader("📄 Extracted Document Text")
    st.text_area("Extracted Text", text, height=200)

    if st.button("✅ Run ADGM Compliance Check"):
        with st.spinner("Checking document with Gemini..."):
            result = check_document_with_adgm(text)
        st.subheader("📊 Compliance Results")
        st.write(result)
