
# 🏥 Local Ophthalmology Clinical LLM  
**(Ollama + Flask + Docker | CPU & GPU | Windows)**

This project provides a **fully self-hosted, private, clinician-to-clinician AI system** for **ophthalmology EMR interpretation**.

It is designed to behave like a **senior consultant ophthalmologist reviewing another doctor’s notes**, not a patient-facing chatbot.

✅ No OpenAI  
✅ No Gemini  
✅ No external APIs  
✅ Runs fully offline  
✅ Full clinical reasoning enabled  

---

## 🎯 Core Capabilities

- 🧠 **Doctor-level ophthalmology EMR interpretation**
- 👁️ Eye-wise (R/OD vs L/OS) clinical reasoning
- 📄 Accepts **structured EMR JSON**
- 🧾 Generates **shareable Markdown / PDF reports**
- 🔍 Identifies:
  - Normal vs abnormal findings
  - Missing but clinically essential data
  - Documentation quality gaps
  - Differential diagnoses (conditional)
  - Suggested next clinical steps

This system is **NOT patient-facing**.

---

## 🧱 Technology Stack

| Layer | Technology |
|-----|-----------|
| LLM Runtime | Ollama (Docker) |
| Model | LLaMA 3.1 (8B) |
| API | Flask |
| Export | Markdown / PDF |
| OS | Windows 10 / 11 |
| GPU (optional) | NVIDIA CUDA |

---

## 📁 Project Structure (Actual)

```
MODEL/
│
├── model/
│   ├── cpu/
│   │   └── docker-compose.yml      # CPU-only Ollama
│   │
│   └── gpu/
│       └── docker-compose.yml      # GPU-enabled Ollama
│
├── myenv/                           # Python virtual environment
│
├── server/
│   ├── app.py                      # Flask API
│   ├── Requirements.txt
│   ├── uploads/                    # Input files (optional)
│   └── outputs/                    # Generated MD / PDF reports
│
├── .gitignore
└── Readme.md

```

---

## 🧠 Architecture (Recommended)

```

Windows Host
│
├── Flask API (Python venv)
│   └── [http://localhost:5000](http://localhost:5000)
│
└── Docker Desktop
└── Ollama Runtime
└── [http://localhost:11434](http://localhost:11434)
└── llama3.1 model

````

✔ Flask runs natively on Windows  
✔ Ollama runs in Docker  
✔ No Docker rebuilds for Flask  
✔ Ideal for hospital / EMR environments  

---

## ✅ Prerequisites

- Windows 10 / 11
- Docker Desktop (WSL2 enabled)
- Python 3.11+
- NVIDIA GPU (optional, for GPU mode)

Verify:
```powershell
docker --version
python --version
curl --version
````

---

## 🐳 Step 1: Start Ollama (Choose ONE)

### ▶ CPU Mode

```powershell
cd model/cpu
docker compose up -d
```

### ▶ GPU Mode (NVIDIA)

```powershell
cd model/gpu
docker compose up -d
```

Verify:

```powershell
docker ps
```

---

## 📥 Step 2: Pull LLM Model (One-Time)

```powershell
docker exec -it ollama ollama pull llama3.1
```

Verify:

```powershell
docker exec -it ollama ollama list
```

---

## 🐍 Step 3: Python Virtual Environment

```powershell
cd MODEL
py -3.11 -m venv myenv
myenv\Scripts\Activate.ps1
```

---

## 📦 Step 4: Install Python Dependencies

```powershell
cd server
pip install -r Requirements.txt
```

---

## 🚀 Step 5: Run Flask API

```powershell
python app.py
```

API runs at:

```
http://localhost:5000
```

---

## 🔗 API Endpoints

### ✅ Health Check

```powershell
curl http://localhost:5000/health
```

---

### 🧠 Analyze Ophthalmology EMR (JSON)

**Doctor-level clinical interpretation**

```powershell
curl -X POST http://localhost:5000/analyze-examination-json `
  -H "Authorization: Bearer sk-local-key" `
  -H "Content-Type: application/json" `
  --data-binary "@exam.json"
```

Returns:

* Consultant-style interpretation
* Missing data analysis
* Differential diagnoses (conditional)
* Suggested next steps
* Documentation critique

---

### 📄 Export Shareable Report (MD / PDF)

#### Markdown

```powershell
curl -X POST "http://localhost:5000/export-examination?format=md" `
  -H "Authorization: Bearer sk-local-key" `
  -H "Content-Type: application/json" `
  --data-binary "@exam.json"
```

#### PDF

```powershell
curl -X POST "http://localhost:5000/export-examination?format=pdf" `
  -H "Authorization: Bearer sk-local-key" `
  -H "Content-Type: application/json" `
  --data-binary "@exam.json"
```

Files saved to:

```
server/outputs/
```

---

## 🧠 Model Behavior (Important)

The model is explicitly instructed to:
````
✔ Treat empty fields as **NOT DOCUMENTED**
✔ Never assume normal findings
✔ Never invent measurements
✔ Never correct EMR data
✔ Separate findings vs limitations
✔ Think like a real ophthalmologist
````
This avoids unsafe hallucinations.

---

## ⚠️ Clinical Disclaimer

This system is **for clinician-to-clinician decision support only**.

It does **not** replace:

* Independent medical judgment
* Physical examination
* Diagnostic confirmation

