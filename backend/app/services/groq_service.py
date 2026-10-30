import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.config import settings
from app.schemas.inquiry import InquiryCreateRequest, InquiryAnalysisResponse
from app.services.scoring import calculate_lead_score

logger = logging.getLogger(__name__)

CYNBIT_SERVICES_KNOWLEDGE = """
Cynbit Core Business Capabilities:
1. "AI/ML & Autonomous Agents": LLM integration, intelligent workflows, RAG, agentic automation, predictive analytics, NLP, computer vision.
2. "Full-Stack Web & Cloud Platforms": Modern web applications, scalable APIs (FastAPI/Node), React/Next.js, cloud deployment (AWS/GCP), microservices.
3. "Mobile Application Development": Cross-platform apps (Flutter, React Native), native iOS/Android, offline-first architectures.
4. "Enterprise CRM & Workflow Automation": CRM customization, business process automation, pipeline management, ERP integrations.
5. "Custom Software Solutions": Tailored enterprise software, database engineering, system modernizations.
"""

SYSTEM_PROMPT = f"""
You are the AI Project Inquiry & Lead Intelligence Agent for Cynbit (a modern tech & AI engineering company).
Your role is to deeply analyze prospective client project inquiries and extract actionable technical intelligence for Cynbit's engineering and sales leadership.

{CYNBIT_SERVICES_KNOWLEDGE}

You must return a STRICT JSON object with these exact keys:
{{
  "service_category": "One of: AI/ML & Autonomous Agents | Full-Stack Web & Cloud Platforms | Mobile Application Development | Enterprise CRM & Workflow Automation | Custom Software Solutions",
  "secondary_services": ["list of complementary services if any"],
  "confidence_score": 0.95,
  "executive_summary": "2-3 sentences summarizing the client project, target outcome, and core value proposition.",
  "extracted_requirements": ["bulleted list of specific technical and functional requirements found in the inquiry"],
  "missing_information": ["critical questions or missing specs needed before proposal, e.g. user scale, cloud choice, auth type, integrations"],
  "recommended_tech_stack": ["list of recommended frameworks, databases, and tools appropriate for this project"],
  "suggested_next_actions": ["immediate operational actions for Cynbit team, e.g. schedule 30-min discovery call, prepare preliminary architectural blueprint"],
  "discovery_questions": ["3-4 sharp, high-impact technical and business discovery questions to ask the client on call"],
  "estimated_timeline_range": "e.g. 6-10 weeks"
}}
Do NOT output any markdown backticks or preamble. Output raw valid JSON only.
"""

def _extract_heuristically(inquiry: InquiryCreateRequest) -> Dict[str, Any]:
    """
    Intelligent heuristic fallback processor when Groq API key is unconfigured
    or in offline development environments.
    """
    desc = inquiry.project_description.lower()
    
    # 1. Classify service category
    if any(k in desc for k in ["ai", "machine learning", "ml", "llm", "agent", "predictive", "recommendation", "nlp", "chatbot", "vision"]):
        category = "AI/ML & Autonomous Agents"
        secondary = ["Full-Stack Web & Cloud Platforms"]
        tech_stack = ["Python", "FastAPI", "Groq / OpenAI API", "LangChain / LlamaIndex", "Vector DB (Chroma/FAISS)", "PostgreSQL"]
        timeline = "8-12 weeks"
    elif any(k in desc for k in ["mobile", "ios", "android", "flutter", "react native", "app"]):
        category = "Mobile Application Development"
        secondary = ["Full-Stack Web & Cloud Platforms"]
        tech_stack = ["Flutter", "Dart", "Firebase / Supabase", "FastAPI Backend", "PostgreSQL"]
        timeline = "6-10 weeks"
    elif any(k in desc for k in ["crm", "erp", "salesforce", "lead", "pipeline", "workflow automation"]):
        category = "Enterprise CRM & Workflow Automation"
        secondary = ["AI/ML & Autonomous Agents"]
        tech_stack = ["Python", "FastAPI", "PostgreSQL", "Celery / Redis", "React Admin", "Webhook Integrations"]
        timeline = "4-8 weeks"
    elif any(k in desc for k in ["web", "website", "platform", "dashboard", "portal", "cloud", "api"]):
        category = "Full-Stack Web & Cloud Platforms"
        secondary = ["Custom Software Solutions"]
        tech_stack = ["FastAPI / Node.js", "React / Next.js", "Tailwind CSS", "Docker", "PostgreSQL / Redis"]
        timeline = "6-10 weeks"
    else:
        category = "Custom Software Solutions"
        secondary = ["Full-Stack Web & Cloud Platforms"]
        tech_stack = ["Python", "FastAPI", "Docker", "PostgreSQL"]
        timeline = "4-8 weeks"

    # 2. Extract requirements
    sentences = [s.strip() for s in inquiry.project_description.replace("\n", ". ").split(".") if len(s.strip()) > 8]
    extracted_reqs = []
    for s in sentences[:6]:
        clean_s = s.capitalize()
        if not clean_s.endswith("."):
            clean_s += "."
        extracted_reqs.append(clean_s)
    
    if not extracted_reqs:
        extracted_reqs = ["Custom application delivery aligned with client specifications."]

    # 3. Identify missing information
    missing = []
    if inquiry.budget_inr is None:
        missing.append("Target investment ceiling or budget range is unspecified.")
    if not inquiry.timeline:
        missing.append("Explicit target go-live milestone or phased release dates are unstated.")
    if not any(k in desc for k in ["user", "scale", "traffic", "volume", "concurrent"]):
        missing.append("Anticipated concurrent user volume, database volume, and load requirements.")
    if not any(k in desc for k in ["auth", "login", "role", "sso", "security"]):
        missing.append("Authentication requirements (e.g. SSO, Multi-tenant roles, OAuth2).")
    if not any(k in desc for k in ["deploy", "aws", "gcp", "azure", "server", "host"]):
        missing.append("Preferred cloud deployment infrastructure (AWS, Azure, GCP, or on-premise).")

    # 4. Generate Discovery Questions
    discovery_qs = [
        f"What is the primary business metric (e.g. conversion, operational speed) defining success for this {category.lower()} solution?",
        "Are there existing legacy databases or third-party APIs that our system must integrate with?",
        "What is your target launch date for Phase 1 MVP versus full release?"
    ]

    # 5. Suggested Next Actions
    actions = [
        "Schedule 30-minute discovery consultation call with technical solutions architect.",
        "Draft preliminary high-level architecture diagram and scope of work.",
        "Deliver tailored capability deck showcasing Cynbit's recent domain case studies."
    ]

    exec_summary = (
        f"Project inquiry from {inquiry.customer_name}"
        f"{f' ({inquiry.company_name})' if inquiry.company_name else ''} focused on "
        f"{category}. The client seeks an engineered solution addressing "
        f"core operational requirements within a target budget of "
        f"{f'₹{inquiry.budget_inr:,.0f}' if inquiry.budget_inr else 'an unspecified commercial range'}."
    )

    return {
        "service_category": category,
        "secondary_services": secondary,
        "confidence_score": 0.88,
        "executive_summary": exec_summary,
        "extracted_requirements": extracted_reqs,
        "missing_information": missing,
        "recommended_tech_stack": tech_stack,
        "suggested_next_actions": actions,
        "discovery_questions": discovery_qs,
        "estimated_timeline_range": timeline,
        "engine": "heuristic-rule-engine"
    }


def analyze_inquiry_with_ai(inquiry: InquiryCreateRequest) -> InquiryAnalysisResponse:
    """
    Analyzes an inquiry using the Groq LLM API if configured,
    or falls back intelligently to the robust heuristic engine.
    """
    raw_ai_output = None
    engine_used = "groq-unconfigured (offline-engine)"
    
    if settings.GROQ_API_KEY and len(settings.GROQ_API_KEY.strip()) > 5:
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY.strip())
            
            user_content = (
                f"Client Name: {inquiry.customer_name}\n"
                f"Company: {inquiry.company_name or 'N/A'}\n"
                f"Stated Budget (INR): {f'₹{inquiry.budget_inr:,.0f}' if inquiry.budget_inr else 'Not specified'}\n"
                f"Stated Timeline: {inquiry.timeline or 'Not specified'}\n\n"
                f"Project Description:\n{inquiry.project_description}"
            )
            
            # Attempt with primary model
            models_to_try = [settings.GROQ_MODEL, settings.GROQ_FALLBACK_MODEL]
            response = None
            last_err = None

            for model_name in models_to_try:
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_content}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.2,
                        max_tokens=1500
                    )
                    engine_used = f"groq-{model_name}"
                    break
                except Exception as m_err:
                    last_err = m_err
                    logger.warning(f"Failed calling model {model_name}: {m_err}")
            
            if response and response.choices and response.choices[0].message.content:
                parsed = json.loads(response.choices[0].message.content)
                raw_ai_output = parsed
                raw_ai_output["engine"] = engine_used
            else:
                logger.error(f"Groq API call returned empty response. Error: {last_err}")
        except Exception as e:
            logger.error(f"Error invoking Groq API: {e}")
            raw_ai_output = None

    # Fallback if Groq unavailable or failed
    if not raw_ai_output:
        raw_ai_output = _extract_heuristically(inquiry)
        engine_used = raw_ai_output.get("engine", "heuristic-rule-engine")

    # Compute rule-based explainable score
    lead_score = calculate_lead_score(
        project_description=inquiry.project_description,
        budget_inr=inquiry.budget_inr,
        timeline=inquiry.timeline,
        service_category=raw_ai_output.get("service_category"),
        extracted_features_count=len(raw_ai_output.get("extracted_requirements", []))
    )

    inquiry_id = f"inq_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    return InquiryAnalysisResponse(
        inquiry_id=inquiry_id,
        timestamp=now_iso,
        customer_name=inquiry.customer_name,
        email=str(inquiry.email),
        company_name=inquiry.company_name,
        original_description=inquiry.project_description,
        budget_inr=inquiry.budget_inr,
        timeline=inquiry.timeline,
        service_category=raw_ai_output.get("service_category", "Custom Software Solutions"),
        secondary_services=raw_ai_output.get("secondary_services", []),
        confidence_score=float(raw_ai_output.get("confidence_score", 0.85)),
        executive_summary=raw_ai_output.get("executive_summary", ""),
        extracted_requirements=raw_ai_output.get("extracted_requirements", []),
        missing_information=raw_ai_output.get("missing_information", []),
        recommended_tech_stack=raw_ai_output.get("recommended_tech_stack", []),
        suggested_next_actions=raw_ai_output.get("suggested_next_actions", []),
        discovery_questions=raw_ai_output.get("discovery_questions", []),
        estimated_timeline_range=raw_ai_output.get("estimated_timeline_range", "4-8 weeks"),
        lead_score=lead_score,
        processing_engine=engine_used
    )
