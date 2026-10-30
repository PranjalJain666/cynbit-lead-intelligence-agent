from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.config import settings
from app.schemas.inquiry import (
    InquiryCreateRequest,
    InquiryAnalysisResponse,
    InquiryListItem,
    HealthResponse,
)
from app.services.groq_service import analyze_inquiry_with_ai
from app.database.db import (
    save_inquiry,
    get_inquiry,
    list_inquiries,
    delete_inquiry,
    count_inquiries,
)

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Diagnostic Check",
    tags=["Diagnostics"]
)
def health_check():
    """Returns runtime health, Groq API key readiness, and database status."""
    db_ok = True
    inquiry_count = 0
    try:
        inquiry_count = count_inquiries()
    except Exception:
        db_ok = False

    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        groq_api_configured=bool(settings.GROQ_API_KEY and len(settings.GROQ_API_KEY.strip()) > 5),
        model_name=settings.GROQ_MODEL,
        database_connected=db_ok,
        total_inquiries_stored=inquiry_count,
    )


@router.post(
    "/inquiries/analyze",
    response_model=InquiryAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze and Qualify a Client Project Inquiry",
    tags=["Inquiries"]
)
def process_inquiry(inquiry: InquiryCreateRequest):
    """
    Submits a client inquiry for automated AI intelligence processing:
    1. Extracts explicit & implicit technical requirements.
    2. Identifies matching Cynbit service categories.
    3. Surfaces missing specs and risk factors.
    4. Computes explainable 0-100 lead qualification score.
    5. Saves full record into database for sales tracking.
    """
    try:
        analysis_result = analyze_inquiry_with_ai(inquiry)
        # Persist to database
        save_inquiry(analysis_result.model_dump())
        return analysis_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process inquiry: {str(e)}"
        )


@router.get(
    "/inquiries",
    response_model=List[InquiryListItem],
    summary="List Processed Inquiries",
    tags=["Inquiries"]
)
def get_all_inquiries(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of inquiries to return"),
    priority: Optional[str] = Query(None, description="Filter by priority tier (High, Medium, Low)")
):
    """Retrieves list of recently processed project inquiries with metadata."""
    try:
        return list_inquiries(limit=limit, priority=priority)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch inquiries: {str(e)}"
        )


@router.get(
    "/inquiries/{inquiry_id}",
    response_model=InquiryAnalysisResponse,
    summary="Get Detailed Inquiry Intelligence Report",
    tags=["Inquiries"]
)
def get_inquiry_detail(inquiry_id: str):
    """Retrieves full analysis report for a specific inquiry ID."""
    record = get_inquiry(inquiry_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquiry with ID '{inquiry_id}' not found."
        )
    return record


@router.delete(
    "/inquiries/{inquiry_id}",
    summary="Delete an Inquiry Record",
    tags=["Inquiries"]
)
def remove_inquiry(inquiry_id: str):
    """Deletes an inquiry from the database."""
    deleted = delete_inquiry(inquiry_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquiry with ID '{inquiry_id}' not found."
        )
    return {"message": f"Inquiry {inquiry_id} successfully deleted.", "success": True}


@router.get(
    "/cynbit/services",
    summary="Cynbit Service Capabilities Catalog",
    tags=["Cynbit Catalog"]
)
def get_cynbit_services():
    """Returns Cynbit's official core competency taxonomy."""
    return {
        "company": "Cynbit",
        "description": "Innovative software and AI/ML engineering company",
        "services": [
            {
                "name": "AI/ML & Autonomous Agents",
                "focus": "LLM solutions, RAG pipelines, autonomous agents, computer vision, predictive intelligence",
                "target_clients": "Enterprises and high-growth startups seeking intelligent automation"
            },
            {
                "name": "Full-Stack Web & Cloud Platforms",
                "focus": "Modern scalable web applications, FastAPI/Node microservices, Next.js, AWS/GCP DevOps",
                "target_clients": "Digital businesses needing robust cloud architecture"
            },
            {
                "name": "Mobile Application Engineering",
                "focus": "Cross-platform Flutter & React Native apps, native iOS/Android, offline-first sync",
                "target_clients": "B2C & B2B mobile-first products"
            },
            {
                "name": "Enterprise CRM & Workflow Automation",
                "focus": "Lead pipelines, CRM integrations, ERP automation, business process efficiency",
                "target_clients": "Operational teams eliminating repetitive manual overhead"
            },
            {
                "name": "Custom Software Solutions",
                "focus": "Bespoke internal tools, system refactoring, high-security enterprise solutions",
                "target_clients": "Organizations with specialized domain workflows"
            }
        ]
    }
