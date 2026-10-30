"""
Cynbit Lead Intelligence Agent - Quick Demo & Runner Script
Demonstrates end-to-end pipeline execution and verification.
"""

import sys
import json
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.schemas.inquiry import InquiryCreateRequest
from app.services.groq_service import analyze_inquiry_with_ai
from app.database.db import init_db, save_inquiry, count_inquiries

def main():
    print("=" * 70)
    print("  CYNBIT LEAD INTELLIGENCE AGENT - END-TO-END DEMO EXECUTION")
    print("=" * 70)
    
    # Initialize DB
    init_db()
    print("✅ SQLite database initialized.")
    
    # Sample inquiry
    sample = InquiryCreateRequest(
        customer_name="Vikram Sethi",
        email="vikram@finscale.ai",
        company_name="FinScale Analytics",
        project_description=(
            "We need an AI-powered automated document analysis and fraud detection platform. "
            "The system must ingest enterprise invoices and contracts (PDF/scans), perform OCR, "
            "utilize an LLM extraction pipeline with structured JSON outputs, and flag discrepancies. "
            "Must include a FastAPI microservice backend, role-based access control, and a React dashboard."
        ),
        budget_inr=350000.0,
        timeline="8 weeks"
    )

    print(f"\n📥 Ingesting Client Inquiry from: {sample.customer_name} ({sample.company_name})")
    print(f"💰 Stated Budget: ₹{sample.budget_inr:,.0f} | ⏱️ Timeline: {sample.timeline}")
    print(f"📝 Raw Description: {sample.project_description[:80]}...\n")

    print("🤖 Processing through Cynbit AI Intelligence Pipeline...")
    analysis = analyze_inquiry_with_ai(sample)
    
    # Save to SQLite
    save_inquiry(analysis.model_dump())
    print("💾 Record successfully persisted to database.\n")

    # Display results
    score = analysis.lead_score
    print("=" * 70)
    print("                    ANALYSIS & SCORING REPORT")
    print("=" * 70)
    print(f"• Inquiry ID         : {analysis.inquiry_id}")
    print(f"• Service Category   : {analysis.service_category}")
    print(f"• Lead Priority Tier : {score.priority_tier.upper()} PRIORITY")
    print(f"• Total Score        : {score.total_score} / 100")
    print(f"• Delivery Estimate  : {analysis.estimated_timeline_range}")
    print(f"• Processing Engine  : {analysis.processing_engine}")

    print("\n[Scoring Breakdown & Explainability]")
    print(f"  - Budget Fit Score     : {score.budget_score} / 25 pts")
    print(f"  - Timeline Feasibility : {score.timeline_score} / 20 pts")
    print(f"  - Scope Clarity        : {score.scope_clarity_score} / 30 pts")
    print(f"  - Cynbit Alignment     : {score.cynbit_fit_score} / 25 pts")
    print("  - Rationale Points:")
    for r in score.rationale:
        print(f"    * {r}")

    print("\n[Identified Technical Requirements]")
    for req in analysis.extracted_requirements[:4]:
        print(f"  ✅ {req}")

    print("\n[Flagged Missing Information / Spec Gaps]")
    for gap in analysis.missing_information[:3]:
        print(f"  ⚠️ {gap}")

    print("\n[Suggested Discovery Call Questions]")
    for q in analysis.discovery_questions[:3]:
        print(f"  ❓ \"{q}\"")

    print("\n" + "=" * 70)
    print(f"Total Stored Inquiries in DB: {count_inquiries()}")
    print("=" * 70)
    print("\nTo launch the interactive Web Dashboard:")
    print("  streamlit run frontend/streamlit_app.py")
    print("\nTo run the FastAPI backend server:")
    print("  uvicorn backend.app.main:app --reload --port 8000")
    print("=" * 70)

if __name__ == "__main__":
    main()
