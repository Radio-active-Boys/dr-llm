from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime
import markdown
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

OLLAMA_URL = "http://10.10.78.175:11434/v1/chat/completions"
MODEL_NAME = "dolphin3.0-llama3.1-8b"      # Stable on GTX 1650 (4GB VRAM)
API_KEY = "sk-local-key"

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REQUEST_TIMEOUT = 300

DOCTOR_ASSIST_PROMPT = """
You are a senior consultant ophthalmologist assisting another ophthalmologist.

This is a private, clinician-to-clinician clinical decision support system.

You are EXPECTED to:
- Interpret findings using real-world ophthalmology reasoning
- Clearly distinguish between documented findings, absent findings, and undocumented findings
- Identify normal vs abnormal findings ONLY when explicitly supported by data
- Highlight missing but clinically essential data that limits interpretation
- Infer reasonable clinical implications WITHOUT overreach
- Suggest DIFFERENTIAL DIAGNOSES only when supported by objective findings
- If data is insufficient, explicitly state that diagnosis cannot be established
- Suggest appropriate next investigations or management steps
- Critically assess documentation quality

CRITICAL CLINICAL RULES (MANDATORY):
- Empty arrays or blank fields mean "NOT DOCUMENTED", NOT "NORMAL"
- Absence of documentation does NOT imply absence of disease
- History alone (e.g., “mild injury”) does NOT justify pathology without objective signs
- Do NOT invent findings, severity, or risk
- Do NOT escalate to serious diagnoses without supporting evidence
- Differentials must be framed as conditional possibilities, not conclusions
- When data is insufficient, clearly state limitations instead of guessing

DO NOT:
- Refuse
- Say “I cannot help”
- Use patient-facing language
- Add legal disclaimers except the final section

MANDATORY OUTPUT STRUCTURE (STRICT):

1. Case Overview
2. Documented Positive Findings
3. Documented Negative / Normal Findings
4. Clinically Significant Missing Data
5. Laterality & Asymmetry Analysis
6. Clinical Interpretation
7. Differential Diagnostic Considerations
8. Suggested Next Clinical Steps
9. Documentation Quality Assessment
10. Explicit Disclaimer

STYLE REQUIREMENTS:
- Use formal ophthalmology terminology
- Be concise, precise, and clinically realistic
- Prefer “cannot be assessed” over speculation
- Write exactly like a consultant reviewing another doctor’s notes
"""

def auth_failed(req):
    return req.headers.get("Authorization") != f"Bearer {API_KEY}"

def ollama_chat(messages, temperature=0.25):
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": temperature
        },
        timeout=REQUEST_TIMEOUT
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def build_markdown(title, body, meta):
    meta_block = "\n".join([f"- **{k}**: {v}" for k, v in meta.items()])
    return f"""# {title}

{meta_block}

---

{body}

---

### Disclaimer
This document is auto-generated for clinician-to-clinician decision support.  
It does not replace independent medical judgment.

Generated on: {datetime.utcnow().isoformat()} UTC
"""

def save_markdown(filename, md):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    return path

def markdown_to_pdf(md_text, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    html = markdown.markdown(md_text)
    elements = [
        Paragraph(p, styles["Normal"])
        for p in html.split("\n") if p.strip()
    ]
    doc.build(elements)
    return path

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/analyze-examination-json", methods=["POST"])
def analyze_exam_json():
    if auth_failed(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    analysis = ollama_chat([
        {"role": "system", "content": DOCTOR_ASSIST_PROMPT},
        {"role": "user", "content": json.dumps(data, indent=2)}
    ])

    return jsonify({
        "patient_id": data.get("patient_id", "UNKNOWN"),
        "case_id": data.get("case_id", "UNKNOWN"),
        "analysis": analysis
    })

@app.route("/export-examination", methods=["POST"])
def export_exam():
    if auth_failed(request):
        return jsonify({"error": "Unauthorized"}), 401

    fmt = request.args.get("format", "md")  # md | pdf
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    analysis = ollama_chat([
        {"role": "system", "content": DOCTOR_ASSIST_PROMPT},
        {"role": "user", "content": json.dumps(data, indent=2)}
    ])

    md = build_markdown(
        title="Ophthalmology Clinical Interpretation Report",
        body=analysis,
        meta={
            "Patient ID": data.get("patient_id", "NOT FOUND"),
            "Case ID": data.get("case_id", "NOT FOUND"),
            "Examination": "Full Eye Examination"
        }
    )

    if fmt == "pdf":
        path = markdown_to_pdf(md, f"{data.get('case_id','exam')}.pdf")
    else:
        path = save_markdown(f"{data.get('case_id','exam')}.md", md)

    return jsonify({
        "status": "success",
        "file": os.path.basename(path),
        "path": path
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
