# ⚡ Cynbit Lead Intelligence Agent
### AI-Powered Project Inquiry Analysis, Scope Extraction & Explainable Lead Qualification

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io/)
[![Groq LPU](https://img.shields.io/badge/Groq-Llama--3.3--70B-orange.svg)](https://groq.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-success.svg)](https://docs.pytest.org/)

**Candidate:** Pranjal Jain  
**Assessment:** AI/ML Engineer Intern Technical Task — Identify an AI Opportunity for Cynbit  
**Candidate Submission Portal:** [Cynbit Talent Hub](https://www.cynbit.in/candidate/cmsnk9t1y000104ldjd4q4bk1)  
**Submission Deadline:** Saturday, October 31, 2026, 04:01 AM  

---

## 📌 Executive Overview

Technology consulting firms like **Cynbit** receive hundreds of project inquiries across web forms, emails, and RFPs. Evaluating each inquiry manually creates a severe operational bottleneck: senior solutions architects spend 5–8 hours weekly triaging inquiries, drafting preliminary scopes, and asking basic discovery questions, while prospective clients often wait 24–48 hours for a response.

The **Cynbit Lead Intelligence Agent** is an end-to-end AI engineering solution that acts as an autonomous **AI Technical Solutions Architect**:
1. **Parses & Extracts Requirements:** Converts informal client prose into structured functional and technical specifications.
2. **Maps to Cynbit Taxonomy:** Classifies incoming inquiries into Cynbit's primary competencies (*AI/ML & Autonomous Agents*, *Full-Stack Web & Cloud*, *Mobile Application Engineering*, *Enterprise CRM & Automation*, *Custom Software*).
3. **Surfaces Missing Information:** Detects missing critical variables (concurrency scale, cloud preference, authentication protocols, budget gaps).
4. **Transparent Lead Qualification (0–100):** Executes an explainable, deterministic mathematical scoring algorithm evaluating budget fit, timeline feasibility, technical scope depth, and strategic alignment with Cynbit.
5. **Generates Discovery Toolkits:** Automatically crafts 3–4 targeted questions and next actions for the sales engineering team before the first discovery call.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│   Streamlit Web Interface (Port 8501) / External Webhook   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP JSON Request
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Microservice Engine                 │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Pydantic Schema Validation (InquiryCreateRequest)  │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Clean Typed Data             │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 2. AI Intelligence Engine (GroqService)              │  │
│  │    • Primary: Groq LPU (Llama-3.3-70B-Versatile)      │  │
│  │    • Fallback: Groq Llama-3.1-8B-Instant              │  │
│  │    • Offline Resilience: Heuristic Feature Parser     │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Structured Extraction        │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 3. Deterministic Lead Scoring Engine (ScoringService) │  │
│  │    • Budget Sufficiency (0-25 pts)                    │  │
│  │    • Timeline Clarity (0-20 pts)                      │  │
│  │    • Technical Scope Depth (0-30 pts)                 │  │
│  │    • Cynbit Strategic Alignment (0-25 pts)            │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │ Complete Analysis Model      │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 4. Persistence Layer (SQLite Database)                │  │
│  │    • ACID transactions, indexed queries by priority   │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Complete JSON Response
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Cynbit Sales & Engineering Team                │
│  • Instant Priority Tier Badge (High / Medium / Low)        │
│  • Automated Executive Brief & Scope Summary                │
│  • Missing Technical Specifications Alert                   │
│  • 3-4 High-Impact Discovery Call Questions                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
cynbit-intern-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entrypoint & lifespan
│   │   ├── config.py            # Environment settings and configuration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py        # REST endpoints (/analyze, /inquiries, /health)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── inquiry.py       # Pydantic V2 validation schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── groq_service.py  # Groq LPU LLM integration & heuristic fallback
│   │   │   └── scoring.py       # Explainable 4-factor scoring algorithm
│   │   └── database/
│   │       ├── __init__.py
│   │       └── db.py            # Thread-safe SQLite database manager
│   ├── inquiries.db             # Local SQLite database
│   └── requirements.txt         # Backend dependencies
├── frontend/
│   └── streamlit_app.py         # Multi-tab interactive Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py          # Unit tests for scoring algorithm
│   └── test_api.py              # Functional integration tests for API
├── reports/
│   ├── AI_Opportunity_Report.md # Deliverable 1: Strategic business & opportunity analysis
│   └── Technical_Approach.md    # Deliverable 3: Architecture, models, and execution plan
├── run_demo.py                  # One-click CLI end-to-end verification script
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git exclusion rules
├── requirements.txt             # Project root dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
* Python 3.10, 3.11, or 3.12 installed.
* Optional: A free [Groq Cloud API Key](https://console.groq.com/keys) (the application includes an intelligent offline heuristic engine that works out of the box even without an API key).

### 2. Installation
Clone the repository and install dependencies:
```bash
# Clone the repository
git clone <your-github-repo-url>
cd "Cynbit intern project"

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Inside `.env`, set your Groq API key:
```ini
GROQ_API_KEY=gsk_your_actual_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 🖥️ Running the Application

### Option A: Run the Automated CLI Demo (Instant Verification)
Run the automated end-to-end pipeline script to process a sample enterprise inquiry:
```bash
python run_demo.py
```

### Option B: Run the FastAPI Backend Server
Launch the FastAPI microservice with auto-reload:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
* **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc API Explorer:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Endpoint:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

### Option C: Launch the Streamlit Web Dashboard
In a separate terminal, launch the Streamlit frontend:
```bash
streamlit run frontend/streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
* Use the **1-Click Presets** in the sidebar (e.g., *AI Enterprise Platform*, *Mobile Logistics App*, *Vague Web Request*) to test different lead tiers instantly.
* View explainable score bars, missing information warnings, and discovery call questions.
* Explore the **Lead Intelligence Pipeline** tab to filter past inquiries and download raw JSON.

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
python -m pytest tests/ -v
```

All 7 test cases covering the scoring engine, API endpoints, schema validation, and database operations execute in **under 1.5 seconds**.

---

## 📊 Explainable Lead Qualification Matrix

Unlike black-box LLM scoring, our hybrid engine uses deterministic mathematical rules to guarantee score consistency:

$$\text{Total Score} = S_{\text{budget}} + S_{\text{timeline}} + S_{\text{scope}} + S_{\text{fit}}$$

| Dimension | Max Points | Evaluation Criteria |
|---|---|---|
| **Budget Adequacy ($S_{\text{budget}}$)** | 25 pts | $\ge ₹2.5\text{L}$ (25 pts), $₹1.2\text{L} - ₹2.5\text{L}$ (20 pts), $₹50\text{k} - ₹1.2\text{L}$ (15 pts), $< ₹50\text{k}$ (8 pts), Unstated (10 pts) |
| **Timeline Realism ($S_{\text{timeline}}$)** | 20 pts | Defined schedule 3–16 weeks (20 pts), Extended $>16$ weeks (15 pts), Urgent/ASAP risk (10 pts), Unstated (8 pts) |
| **Scope & Tech Depth ($S_{\text{scope}}$)** | 30 pts | Analyzes word density and technical architectural keywords (`api`, `auth`, `database`, `pipeline`, `docker`, etc.) |
| **Cynbit Strategic Alignment ($S_{\text{fit}}$)** | 25 pts | AI/ML & LLM Agents (25 pts), Full-Stack & Cloud (22 pts), Mobile Development (20 pts), General Software (15 pts) |

### Qualification Tiers
* 🟢 **High Priority ($\ge 75$):** Fast-tracked directly to a Senior Solutions Architect.
* 🟡 **Medium Priority ($50 - 74$):** Standard pre-sales queue; brief discovery call scheduled.
* 🔴 **Low Priority ($< 50$):** Automated nurturing sequence sent to clarify scope and budget.

---

## 📑 Required Deliverables Mapping

| Required Deliverable | Project Artifact | Description |
|---|---|---|
| **1. AI Opportunity Report** | [`reports/AI_Opportunity_Report.md`](reports/AI_Opportunity_Report.md) | Business case, 5 evaluated AI opportunities, in-depth analysis of selected opportunity, and ROI model. |
| **2. AI/ML Proof of Concept (POC)** | [`backend/`](backend/) & [`frontend/`](frontend/) | Fully functional FastAPI backend + Streamlit dashboard + Groq LLM integration + SQLite database. |
| **3. Technical Approach Report** | [`reports/Technical_Approach.md`](reports/Technical_Approach.md) | Technical architecture, Groq LPU model selection, zero-hallucination scoring, security, and scaling roadmap. |

---

## 👨‍💻 Candidate Submission Notes

* **Candidate:** Pranjal Jain
* **Application Role:** AI/ML Engineer Intern

