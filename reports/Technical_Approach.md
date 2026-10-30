# Technical Approach Report: Architecture, Models & Pipeline Design

**Project:** AI-Powered Project Inquiry & Lead Intelligence Agent  
**Author:** Pranjal Jain  
**Role:** AI/ML Engineer Intern Assessment  
**Company:** Cynbit  
**Candidate Portal:** [Cynbit Candidate Portal](https://www.cynbit.in/candidate/cmsnk9t1y000104ldjd4q4bk1)  
**Date:** October 30, 2026  

---

## 1. System Architecture Overview

The Cynbit Lead Intelligence Agent is engineered as a production-grade, modular microservice architecture. It separates concerns across data validation, LLM reasoning, deterministic scoring, and client presentation.

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

## 2. Model Selection Rationale

### 2.1 Why Groq LPU + Open-Weights Models?
For high-volume pre-sales intelligence, four criteria drive model selection:
1. **Inference Latency:** Client conversion correlates directly with response speed. Groq's Language Processing Units (LPUs) deliver generation speeds exceeding **300 tokens/second**, completing full multi-key JSON extractions in **under 400 milliseconds** (compared to 3-6 seconds on traditional GPU cloud endpoints).
2. **Deterministic JSON Reliability:** `llama-3.3-70b-versatile` natively supports OpenAI-compatible structured JSON mode (`response_format={"type": "json_object"}`), virtually eliminating JSON parsing syntax errors.
3. **Reasoning Density:** Llama 3.3 70B possesses state-of-the-art coding and architectural reasoning benchmarks comparable to GPT-4o, allowing it to accurately disambiguate complex engineering terms (e.g., distinguishing between "Kafka event streams" and "batch cron ETL").
4. **Cost Efficiency:** At ~$0.59 per million input tokens, processing an inquiry costs approximately **$0.0003 (less than ₹0.03)**, providing an order-of-magnitude cost advantage over proprietary closed-source models.

### 2.2 Graceful Degradation Strategy
The architecture implements a multi-tier fallback mechanism:
1. **Tier 1 (Default):** `llama-3.3-70b-versatile` for maximal extraction quality and nuance.
2. **Tier 2 (Fallback):** `llama-3.1-8b-instant` if rate limits or quota boundaries are encountered.
3. **Tier 3 (Offline / Sandbox):** Built-in deterministic Heuristic Parser that uses NLP pattern matching and Cynbit domain taxonomies, ensuring the system never crashes during internet outages, local sandbox testing, or CI test pipelines.

---

## 3. Data Pipeline & Prompt Engineering Strategy

### 3.1 Strict Schema Enforcement
Incoming payloads are rigorously validated using Pydantic V2 schemas before hitting the LLM:
* `customer_name`: Non-empty string, trimmed.
* `email`: Pattern-validated RFC format.
* `project_description`: Minimum 15 characters to prevent zero-context token waste.
* `budget_inr`: Non-negative float.

### 3.2 System Prompt Design
The system prompt injects Cynbit's specific service taxonomy directly into the model's instruction context:
```python
CYNBIT_SERVICES_KNOWLEDGE = """
Cynbit Core Business Capabilities:
1. "AI/ML & Autonomous Agents": LLM integration, intelligent workflows, RAG, agentic automation.
2. "Full-Stack Web & Cloud Platforms": Scalable APIs (FastAPI/Node), React/Next.js, AWS/GCP, microservices.
3. "Mobile Application Development": Cross-platform apps (Flutter, React Native), native iOS/Android.
4. "Enterprise CRM & Workflow Automation": CRM customization, pipeline management, ERP integrations.
5. "Custom Software Solutions": Bespoke enterprise systems, system modernizations.
"""
```

### 3.3 Zero-Hallucination Guardrails
To prevent hallucinated client commitments or fabricated pricing:
* The LLM is restricted to **classification, extraction, and synthesis**.
* Numerical qualification scoring is **explicitly removed from the LLM prompt** and computed by a deterministic Python engine.

---

## 4. The Lead Qualification Scoring Algorithm

A common flaw in purely LLM-based lead scoring is non-deterministic "drift" (where the same inquiry gets 80/100 one time and 60/100 another). We resolved this through a **Hybrid Architecture**: LLMs extract structured features; deterministic math calculates the score.

$$\text{Total Score} = S_{\text{budget}} + S_{\text{timeline}} + S_{\text{scope}} + S_{\text{fit}}$$

### 4.1 Scoring Dimensions

#### 1. Budget Adequacy ($S_{\text{budget}}$, Max 25 Points)
* $\ge ₹250,000$: **25 pts** (Healthy commercial project)
* $₹120,000 - ₹249,999$: **20 pts** (Solid mid-market engagement)
* $₹50,000 - ₹119,999$: **15 pts** (Standard MVP scope)
* $< ₹50,000$: **8 pts** (Low-margin; requires phased MVP)
* Unstated budget: **10 pts** (Baseline; requires discovery call qualification)

#### 2. Timeline Clarity ($S_{\text{timeline}}$, Max 20 Points)
* Defined, realistic schedule (3 to 16 weeks): **20 pts**
* Extended timeline (> 16 weeks): **15 pts**
* High-risk urgency ("ASAP", "immediately", "< 1 week"): **10 pts**
* Unstated timeline: **8 pts**

#### 3. Scope & Technical Depth ($S_{\text{scope}}$, Max 30 Points)
Evaluated on word count density and architectural signals (e.g., `api`, `database`, `auth`, `real-time`, `analytics`, `pipeline`, `docker`):
* High technical depth ($\ge 80$ words or $\ge 5$ extracted features + tech signals): **25-30 pts**
* Moderate clarity ($40-80$ words or $2-4$ features): **17-24 pts**
* Low/vague clarity ($< 40$ words): **7-16 pts**

#### 4. Cynbit Strategic Alignment ($S_{\text{fit}}$, Max 25 Points)
* AI/ML, LLM Agents, Automation, Computer Vision: **25 pts**
* Full-Stack Web & Cloud Platforms, SaaS, DevOps: **22 pts**
* Mobile App Development (Flutter/React Native): **20 pts**
* General bespoke software: **15 pts**

### 4.2 Priority Tiers
* **High Priority ($\ge 75$):** Routed immediately to Senior Solutions Architect; automated calendar invite dispatched.
* **Medium Priority ($50 - 74$):** Standard discovery queue; pre-sales engineer assigned.
* **Low Priority ($< 50$):** Automated nurturing sequence requesting further project specifications.

---

## 5. Security, Reliability & Data Governance

1. **Confidentiality:** Client inquiries are transmitted over TLS with ephemeral processing; prompt instructions instruct models never to cache PII.
2. **Environment Isolation:** Secrets (`GROQ_API_KEY`) are managed via `.env` files and excluded from git version control via `.gitignore`.
3. **Database Concurrency:** SQLite is configured with thread-safe connection pooling, row factories, and indexed queries on `priority_tier` and `timestamp`.
4. **CORS Hardening:** Configured with parameterized origins for seamless local and production hosting.

---

## 6. Production Deployment Roadmap

| Phase | Milestone | Deliverables |
|---|---|---|
| **Phase 1 (Current)** | **Modular MVP** | FastAPI backend, Groq service, rule-based scoring, Streamlit UI, SQLite, Pytest test suite. |
| **Phase 2 (Immediate)** | **CRM Integration** | Webhook receivers for Cynbit website contact forms (HubSpot/Zapier/Webhook listeners). |
| **Phase 3 (Scale)** | **Cloud Native Deployment** | Docker multi-stage containerization, PostgreSQL migration, Celery background task worker for asynchronous batch processing. |
| **Phase 4 (Advanced)** | **Multi-Agent Expansion** | Autonomous discovery email generator and automated Scope of Work (SOW) markdown compiler. |
