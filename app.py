import streamlit as st
from docx import Document
from io import BytesIO
import json
import os
from openai import OpenAI

# Load API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit page config
st.set_page_config(page_title="ADGM Corporate Agent", layout="centered")
st.title(" ADGM Corporate Agent – Legal Compliance Checker")
st.write("Upload your company incorporation documents (.docx) and check them for ADGM compliance.")

# File upload
uploaded_file = st.file_uploader(" Upload a .docx file", type=["docx"])

# Function to read DOCX
def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip() != ""])

# Compliance check using OpenAI
def check_clause_with_adgm(clause_text):
    prompt = f"""
    You are an expert in ADGM legal compliance.
    Check the following clause for compliance with ADGM company incorporation rules.
    Respond in JSON format with:
    - issue: string
    - severity: High/Medium/Low
    - suggestion: string
    - reference: string

    Clause: {clause_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an ADGM compliance expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {
            "issue": "Could not parse AI response",
            "severity": "Low",
            "suggestion": "Check manually",
            "reference": "N/A"
        }

# Process uploaded file
if uploaded_file:
    text_content = read_docx(uploaded_file)
    st.subheader(" Extracted Text")
    st.text_area("", text_content, height=200)

    if st.button(" Run ADGM Compliance Check"):
        clauses = [p for p in text_content.split("\n") if p.strip()]
        results = []

        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            if para.text.strip():
                res = check_clause_with_adgm(para.text.strip())
                results.append({
                    "clause": para.text.strip(),
                    "result": res
                })
                if res.get("issue") != "No issues":
                    para.add_comment(f"Issue: {res['issue']}\nSuggestion: {res['suggestion']}")

        # Save reviewed DOCX
        reviewed_bytes = BytesIO()
        doc.save(reviewed_bytes)
        reviewed_bytes.seek(0)

        # Show JSON report
        st.subheader("Compliance Report")
        st.json(results)

        # Download button
        st.download_button(
            label="⬇ Download Reviewed Document",
            data=reviewed_bytes,
            file_name="reviewed_document.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # Save JSON
        st.download_button(
            label="⬇ Download JSON Report",
            data=json.dumps(results, indent=2),
            file_name="compliance_report.json",
            mime="application/json"
        )
