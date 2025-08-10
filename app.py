import streamlit as st
from docx import Document
from io import BytesIO
import json

st.set_page_config(page_title="ADGM Corporate Agent (Demo)", layout="centered")

st.title("🏛️ ADGM Corporate Agent — Demo (Simulated)")
st.write("Upload a .docx with company docs. The app will simulate ADGM compliance checks and return a reviewed file + JSON report.")

uploaded_file = st.file_uploader("Upload a .docx file", type=["docx"])

def simulated_check(clause):
    # This is simulated. Replace with real API call later.
    if "UAE Federal Court" in clause or "UAE Federal Courts" in clause:
        return {
            "issue": "Incorrect jurisdiction (not ADGM)",
            "severity": "High",
            "suggestion": "Change jurisdiction to 'Abu Dhabi Global Market (ADGM) Courts'.",
            "reference": "ADGM Companies Regulations (simulated)"
        }
    if "signature" not in clause.lower() and "signatory" not in clause.lower():
        return {
            "issue": "Missing signatory info",
            "severity": "Medium",
            "suggestion": "Add an authorized signatory section.",
            "reference": "ADGM checklist (simulated)"
        }
    return {"issue": None, "severity": "OK", "suggestion": "No immediate issue found.", "reference": ""}

def review_and_annotate(filelike):
    doc = Document(filelike)
    report = []
    for para in list(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        result = simulated_check(text)
        report.append({"clause": text, "analysis": result})
        note = doc.add_paragraph()
        note_run = note.add_run(f"[Compliance Note] {result['issue'] or 'No issues'} - {result['suggestion']}")
        note_run.italic = True

    out_b = BytesIO()
    doc.save(out_b)
    out_b.seek(0)
    json_b = BytesIO()
    json_b.write(json.dumps(report, indent=2).encode("utf-8"))
    json_b.seek(0)
    return out_b, json_b

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")
    if st.button("Run review"):
        reviewed_doc, report_json = review_and_annotate(uploaded_file)
        st.download_button("⬇ Download reviewed .docx", data=reviewed_doc, file_name="reviewed_"+uploaded_file.name)
        st.download_button("⬇ Download JSON report", data=report_json, file_name="review_report.json")
        st.write("Done — download the reviewed document and report.")
