import streamlit as st
from docx import Document
import fitz  # PyMuPDF
import os
import google.generativeai as genai

# ----------------------------
# Setup API Key
# ----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ Gemini API Key not found. Please set it in Streamlit Secrets.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------
# Helper Functions
# ----------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def check_document_with_adgm(full_text):
    """Send the entire document at once to Gemini."""
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
# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="ADGM Corporate Agent (Gemini)", layout="wide")
st.title("🏛️ ADGM Corporate Agent Compliance Checker (Gemini)")

uploaded_file = st.file_uploader("📄 Upload a .docx or .pdf file", type=["docx", "pdf"])

if uploaded_file:
    file_path = f"temp.{uploaded_file.name.split('.')[-1]}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_docx(file_path)

    st.subheader("📜 Extracted Document Text")
    st.text_area("Extracted Text", text, height=200)

if st.button("✅ Run ADGM Compliance Check"):
    with st.spinner("Checking document with Gemini..."):
        result = check_document_with_adgm(text)
    st.subheader("📊 Compliance Results")
    st.write(result)
        with st.spinner("Checking clauses with Gemini..."):
            for para in paragraphs:
                check_result = check_clause_with_adgm(para)
                results.append({"clause": para, "result": check_result})

        st.subheader("📊 Compliance Results")
        for res in results:
            st.markdown(f"**Clause:** {res['clause']}")
            st.markdown(f"**Result:** {res['result']}")
            st.markdown("---")
