import os
import sys
import json
import requests
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Cynbit Lead Intelligence Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .badge-high {
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        display: inline-block;
    }
    .badge-medium {
        background-color: #FEF3C7;
        color: #92400E;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        display: inline-block;
    }
    .badge-low {
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Backend API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

# Sidebar Configuration
with st.sidebar:
    st.image("https://cynbit.in/logo.png", width=180) if False else st.markdown("## ⚡ Cynbit AI")
    st.markdown("### **Lead Intelligence Agent**")
    st.caption("AI/ML Engineer Assessment POC")
    
    st.markdown("---")
    st.markdown("#### **System Diagnostics**")
    
    backend_status = False
    health_info = {}
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if resp.status_code == 200:
            backend_status = True
            health_info = resp.json()
    except Exception:
        backend_status = False

    if backend_status:
        st.success("🟢 FastAPI Backend: Online")
        if health_info.get("groq_api_configured"):
            st.success(f"🤖 Groq LLM: {health_info.get('model_name', 'Active')}")
        else:
            st.info("ℹ️ Groq LLM: Heuristic Fallback (Set GROQ_API_KEY in .env)")
        st.caption(f"Stored Inquiries: **{health_info.get('total_inquiries_stored', 0)}**")
    else:
        st.warning("🟡 FastAPI Offline: Direct local mode enabled")

    st.markdown("---")
    st.markdown("#### **Quick Presets (1-Click Fill)**")
    
    demo_samples = {
        "AI Enterprise Platform (High Lead)": {
            "name": "Vikram Sethi",
            "email": "vikram@finscale.ai",
            "company": "FinScale Analytics",
            "budget": 350000,
            "timeline": "8 weeks",
            "description": (
                "We need an AI-powered automated document analysis and fraud detection platform. "
                "The system must ingest enterprise invoices and contracts (PDF/scans), perform OCR, "
                "utilize an LLM extraction pipeline with structured JSON outputs, and flag discrepancies. "
                "Must include a FastAPI microservice backend, role-based access control, and a React dashboard."
            )
        },
        "Mobile Logistics App (Medium Lead)": {
            "name": "Ananya Roy",
            "email": "ananya@quickfreight.in",
            "company": "QuickFreight Logistics",
            "budget": 120000,
            "timeline": "6 weeks",
            "description": (
                "Looking to build a cross-platform mobile app in Flutter for our delivery drivers. "
                "Features include GPS route tracking, digital proof-of-delivery signatures, and order history. "
                "Needs to sync with our existing PostgreSQL backend via REST APIs."
            )
        },
        "Vague Web Request (Low Lead)": {
            "name": "Rohit Verma",
            "email": "rohit@verma.com",
            "company": "Verma Traders",
            "budget": 20000,
            "timeline": "ASAP",
            "description": (
                "Need a simple website for our wholesale business as soon as possible. "
                "Just show our products and contact details."
            )
        }
    }

    selected_sample = st.selectbox("Select a Sample Scenario:", ["-- Manual Entry --"] + list(demo_samples.keys()))

    st.markdown("---")
    st.markdown("### **Cynbit Candidate Details**")
    st.markdown("**Applicant:** Pranjal Jain")
    st.markdown("**Role:** AI/ML Engineer Intern")
    st.markdown("**Deadline:** Oct 31, 2026, 4:01 AM")

# Header
st.markdown('<div class="main-header">⚡ Cynbit Lead Intelligence Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Automated Project Inquiry Analysis, Scope Extraction & Explainable Lead Qualification</div>',
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs(["🚀 Analyze New Inquiry", "📊 Lead Intelligence Pipeline", "📑 Technical Architecture"])

# ----------------- TAB 1: ANALYZE NEW INQUIRY -----------------
with tab1:
    default_vals = demo_samples.get(selected_sample, {
        "name": "", "email": "", "company": "", "budget": 0, "timeline": "", "description": ""
    })

    with st.form("inquiry_form"):
        st.subheader("1. Client & Inquiry Information")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            customer_name = st.text_input("Client Contact Name *", value=default_vals.get("name", ""), placeholder="e.g. Rahul Sharma")
            company_name = st.text_input("Company / Organization", value=default_vals.get("company", ""), placeholder="e.g. TechCorp Solutions")
        with col_b:
            email = st.text_input("Business Email *", value=default_vals.get("email", ""), placeholder="e.g. rahul@techcorp.in")
            timeline = st.text_input("Stated Delivery Timeline", value=default_vals.get("timeline", ""), placeholder="e.g. 8 weeks, 2 months, ASAP")
        with col_c:
            budget_inr = st.number_input(
                "Estimated Budget (INR)",
                min_value=0,
                max_value=10000000,
                step=10000,
                value=int(default_vals.get("budget", 0)),
                help="Stated commercial budget for the project."
            )
        
        st.subheader("2. Project Requirement Description")
        project_description = st.text_area(
            "Project Scope / Client Raw Description *",
            value=default_vals.get("description", ""),
            height=140,
            placeholder="Paste raw client project description, RFQ brief, or email inquiry here..."
        )

        submit_btn = st.form_submit_button("⚡ Analyze Inquiry with Cynbit AI", use_container_width=True)

    if submit_btn:
        if not customer_name or not email or not project_description:
            st.error("Please fill in Client Name, Email, and Project Description.")
        elif len(project_description.strip()) < 15:
            st.warning("Please provide a more detailed project description (at least 15 characters).")
        else:
            with st.spinner("Processing inquiry through Cynbit AI Intelligence Pipeline..."):
                payload = {
                    "customer_name": customer_name,
                    "email": email,
                    "company_name": company_name if company_name else None,
                    "project_description": project_description,
                    "budget_inr": float(budget_inr) if budget_inr > 0 else None,
                    "timeline": timeline if timeline else None
                }

                result = None
                # Try API first
                try:
                    resp = requests.post(f"{API_BASE_URL}/inquiries/analyze", json=payload, timeout=25)
                    if resp.status_code in [200, 201]:
                        result = resp.json()
                except Exception:
                    pass

                # Local fallback if API is offline
                if not result:
                    # Import local service directly
                    try:
                        sys.path.insert(0, str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))))
                        from app.services.groq_service import analyze_inquiry_with_ai
                        from app.schemas.inquiry import InquiryCreateRequest
                        from app.database.db import save_inquiry
                        
                        req = InquiryCreateRequest(**payload)
                        analysis_obj = analyze_inquiry_with_ai(req)
                        save_inquiry(analysis_obj.model_dump())
                        result = analysis_obj.model_dump()
                    except Exception as loc_err:
                        st.error(f"Analysis failed: {loc_err}")

                if result:
                    st.success("✅ Analysis Complete! Executive Intelligence Report Generated.")
                    
                    # Store in session state
                    st.session_state["latest_analysis"] = result

    # Display Analysis Results
    if "latest_analysis" in st.session_state:
        res = st.session_state["latest_analysis"]
        score_data = res["lead_score"]
        tier = score_data["priority_tier"]
        badge_class = f"badge-{tier.lower()}"

        st.markdown("---")
        st.subheader("📋 Executive Intelligence Summary")
        
        # Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:0.85rem; color:#64748B;">LEAD PRIORITY</div>
                <div style="margin-top:6px;"><span class="{badge_class}">{tier.upper()} PRIORITY</span></div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:0.85rem; color:#64748B;">QUALIFICATION SCORE</div>
                <div style="font-size:1.6rem; font-weight:700; color:#0F172A;">{score_data['total_score']} / 100</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:0.85rem; color:#64748B;">SERVICE CATEGORY</div>
                <div style="font-size:1.05rem; font-weight:700; color:#1E293B;">{res['service_category']}</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:0.85rem; color:#64748B;">ESTIMATED DELIVERY</div>
                <div style="font-size:1.2rem; font-weight:700; color:#2563EB;">{res['estimated_timeline_range']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Explainable Score Breakdown
        with st.expander("🔍 **Explainable Lead Scoring Breakdown (Transparent Criteria)**", expanded=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("**Scoring Factors:**")
                st.write(f"• **Budget Sufficiency:** {score_data['budget_score']} / 25 pts")
                st.progress(score_data['budget_score'] / 25.0)
                
                st.write(f"• **Timeline Clarity & Realism:** {score_data['timeline_score']} / 20 pts")
                st.progress(score_data['timeline_score'] / 20.0)

                st.write(f"• **Scope & Technical Clarity:** {score_data['scope_clarity_score']} / 30 pts")
                st.progress(score_data['scope_clarity_score'] / 30.0)

                st.write(f"• **Cynbit Strategic Alignment:** {score_data['cynbit_fit_score']} / 25 pts")
                st.progress(score_data['cynbit_fit_score'] / 25.0)
            
            with col2:
                st.markdown("**Qualification Rationale:**")
                for r in score_data.get("rationale", []):
                    st.markdown(f"- {r}")
                st.caption(f"Engine: `{res.get('processing_engine', 'N/A')}`")

        # Project Brief & Scope
        st.markdown("#### **Project Executive Brief**")
        st.info(res.get("executive_summary", "No summary generated."))

        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("#### **Identified Requirements & Scope**")
            for req in res.get("extracted_requirements", []):
                st.markdown(f"- ✅ {req}")

            st.markdown("#### **Recommended Tech Stack for Cynbit**")
            st.markdown(" ".join([f"`{t}`" for t in res.get("recommended_tech_stack", [])]))

        with c_right:
            st.markdown("#### **⚠️ Missing Information & Spec Gaps**")
            for gap in res.get("missing_information", []):
                st.markdown(f"- ⚠️ {gap}")

            st.markdown("#### **Suggested Discovery Call Questions**")
            for q in res.get("discovery_questions", []):
                st.markdown(f"- ❓ *\"{q}\"*")

        st.markdown("#### **Recommended Next Operational Actions**")
        for act in res.get("suggested_next_actions", []):
            st.markdown(f"- 👉 **{act}**")

# ----------------- TAB 2: CRM DASHBOARD -----------------
with tab2:
    st.subheader("📊 Cynbit Inquiry Intelligence Pipeline")
    
    inquiries_list = []
    # Try fetching from API or direct SQLite
    try:
        resp = requests.get(f"{API_BASE_URL}/inquiries", timeout=3)
        if resp.status_code == 200:
            inquiries_list = resp.json()
    except Exception:
        pass

    if not inquiries_list:
        try:
            sys.path.insert(0, str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))))
            from app.database.db import list_inquiries
            inquiries_list = list_inquiries()
        except Exception:
            inquiries_list = []

    if inquiries_list:
        # Filter row
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            tier_filter = st.selectbox("Filter by Priority:", ["All", "High", "Medium", "Low"])
        
        filtered = [
            i for i in inquiries_list
            if tier_filter == "All" or i.get("priority_tier", "").lower() == tier_filter.lower()
        ]

        # Metric stats
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Inquiries", len(inquiries_list))
        s2.metric("High Priority Leads", sum(1 for i in inquiries_list if i.get("priority_tier") == "High"))
        s3.metric("Medium Priority Leads", sum(1 for i in inquiries_list if i.get("priority_tier") == "Medium"))
        s4.metric("Avg Qualification Score", f"{sum(i.get('total_score', 0) for i in inquiries_list) / max(len(inquiries_list), 1):.1f}")

        st.markdown("---")
        
        # Display table
        table_rows = []
        for i in filtered:
            budget_str = f"₹{i['budget_inr']:,.0f}" if i.get("budget_inr") else "Unstated"
            table_rows.append({
                "ID": i["inquiry_id"][:10],
                "Client": i["customer_name"],
                "Company": i.get("company_name") or "-",
                "Category": i["service_category"],
                "Priority": i["priority_tier"],
                "Score": f"{i['total_score']} / 100",
                "Budget": budget_str,
                "Timeline": i.get("timeline") or "-"
            })
        
        st.dataframe(table_rows, use_container_width=True)

        # Download button
        st.download_button(
            "📥 Download Inquiries JSON",
            data=json.dumps(inquiries_list, indent=2),
            file_name=f"cynbit_inquiries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    else:
        st.info("No inquiries processed yet. Submit your first inquiry in the 'Analyze New Inquiry' tab!")

# ----------------- TAB 3: TECHNICAL ARCHITECTURE -----------------
with tab3:
    st.subheader("📑 Architecture & Engineering Overview")
    
    st.markdown("""
    ### System Architecture & Pipeline Flow
    
    ```
    ┌─────────────────────────┐
    │ Streamlit Web Dashboard │
    │  (Client Inquiry Entry) │
    └───────────┬─────────────┘
                │ HTTP POST /inquiries/analyze
                ▼
    ┌────────────────────────────────────────────────────────┐
    │             FastAPI Microservice Engine                │
    ├────────────────────────┬───────────────────────────────┤
    │  Pydantic Validation   │ Validates schema, budget, txt │
    │  Groq LLM Pipeline     │ Llama-3.3-70B-Versatile       │
    │  Heuristic Fallback    │ Robust offline resilience     │
    │  Scoring Engine        │ Transparent 0-100 rules       │
    │  SQLite Persistence    │ ACID lead storage             │
    └────────────────────────┴───────────────────────────────┘
                │
                ▼
    ┌────────────────────────────────────────────────────────┐
    │        Cynbit Engineering & Sales Action Items         │
    │ - Scored Lead Tier (High / Med / Low)                  │
    │ - Automated Technical Brief & Discovery Qs             │
    │ - Missing Specs & Risk Warnings                        │
    └────────────────────────────────────────────────────────┘
    ```
    
    ### Key Engineering Innovations:
    1. **Zero Hallucination Scoring**: The lead priority score (0-100) is governed by transparent, explainable deterministic mathematical rules rather than unconstrained LLM speculation.
    2. **Low-Latency Inference**: Powered by **Groq LPU Inference Engine** (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`), processing complete inquiries in under 400ms.
    3. **Resilient Dual-Mode Operation**: Includes a comprehensive heuristic parsing fallback so that demos, unit tests, and offline environments work seamlessly without breaking.
    4. **Production FastAPI Backend**: Fully documented with interactive Swagger docs at `http://127.0.0.1:8000/docs`.
    """)
