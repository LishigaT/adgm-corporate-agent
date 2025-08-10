import streamlit as st
from docx import Document
import google.generativeai as genai
from io import BytesIO
import json

# --- Streamlit Page Config ---
st.set_page_config(page_title="ADGM Corporate Agent", layout="wide")

# --- Load Gemini API Key ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# --- App Title ---
st.title("🏢 ADGM Corporate Agent – Compliance Checker")
st.write("Upload your company documents (.docx) to check for ADGM compliance.")

# --- Multi-file Upload ---
uploaded_files = st.file_uploader("Upload one or more .docx files", type=["docx"], accept_multiple_files=True)

# --- Required checklist for incorporation ---
REQUIRED_FOR_INCORPORATION = [
    "Articles of Association",
    "Memorandum of Association",
    "Incorporation Application Form",
    "UBO Declaration Form",
    "Register of Members and Directors"
]

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
if uploaded_files:
    # Gather all file names
    present_types = [f.name for f in uploaded_files]

    # Detect process
    detected_process = "Company Incorporation" if any("association" in f.lower() for f in present_types) else "Unknown"

    # Missing documents
    missing_docs = [doc for doc in REQUIRED_FOR_INCORPORATION if doc.lower() not in " ".join(present_types).lower()]

    # Show missing docs alert
    if detected_process == "Company Incorporation":
        if missing_docs:
            st.error(f"⚠ You are attempting {detected_process}. Missing {len(missing_docs)} required document(s): {', '.join(missing_docs)}")
        else:
            st.success("✅ All required documents for Company Incorporation are present.")

    # Combine text from all uploaded files
    combined_text = ""
    for f in uploaded_files:
        combined_text += f"\n\n--- {f.name} ---\n\n"
        combined_text += extract_text_from_docx(f)

    st.subheader("📄 Extracted Document Text")
    st.text_area("Extracted Text", combined_text, height=300)

    # Run AI Compliance Check
    if st.button("✅ Run ADGM Compliance Check"):
        with st.spinner("Checking document(s) with Gemini..."):
            result = check_document_with_adgm(combined_text)
        st.subheader("📊 Compliance Results")
        st.write(result)

        # JSON Report
        issues_list = [
            {
                "document": f.name,
                "section": "Unknown",
                "issue": "See AI-generated analysis",
                "severity": "Review",
                "suggestion": "Refer to compliance results above"
            } for f in uploaded_files
        ]

        final_report = {
            "process": detected_process,
            "documents_uploaded": len(present_types),
            "required_documents": len(REQUIRED_FOR_INCORPORATION),
            "missing_documents": missing_docs,
            "issues_found": issues_list
        }

        st.download_button(
            label="⬇ Download JSON Report",
            data=json.dumps(final_report, indent=2),
            file_name="compliance_report.json",
            mime="application/json"
        )
