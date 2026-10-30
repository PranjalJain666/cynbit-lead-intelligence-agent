from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class InquiryCreateRequest(BaseModel):
    """Schema for incoming client inquiry payload."""
    customer_name: str = Field(..., min_length=2, max_length=100, description="Name of the prospective client")
    email: str = Field(..., pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$", description="Contact email address")
    company_name: Optional[str] = Field(None, max_length=150, description="Company or organization name")
    project_description: str = Field(..., min_length=15, description="Raw inquiry or project requirement description")
    budget_inr: Optional[float] = Field(None, ge=0, description="Estimated budget in INR")
    timeline: Optional[str] = Field(None, description="Stated target delivery timeframe, e.g., '6 weeks', '3 months'")
    contact_phone: Optional[str] = Field(None, description="Optional phone number")

    model_config = {
        "json_schema_extra": {
            "example": {
                "customer_name": "Rahul Sharma",
                "email": "rahul@techcorp.in",
                "company_name": "TechCorp Logistics",
                "project_description": (
                    "We need an AI-powered fleet management and logistics dispatch dashboard. "
                    "Features must include real-time route optimization using GPS data, automated "
                    "driver assignment, predictive vehicle maintenance alerts, and an executive analytics portal. "
                    "We expect to integrate with our existing ERP."
                ),
                "budget_inr": 350000.0,
                "timeline": "8 weeks",
                "contact_phone": "+91 9876543210"
            }
        }
    }


class LeadScoreBreakdown(BaseModel):
    """Detailed explainable breakdown of the lead qualification score."""
    budget_score: float = Field(..., ge=0, le=25, description="Score based on budget adequacy and presence (0-25)")
    timeline_score: float = Field(..., ge=0, le=20, description="Score based on timeline realism and clarity (0-20)")
    scope_clarity_score: float = Field(..., ge=0, le=30, description="Score based on requirement detail and technical depth (0-30)")
    cynbit_fit_score: float = Field(..., ge=0, le=25, description="Score based on alignment with Cynbit service offerings (0-25)")
    total_score: float = Field(..., ge=0, le=100, description="Overall qualification score (0-100)")
    priority_tier: str = Field(..., description="High, Medium, or Low")
    rationale: List[str] = Field(default_factory=list, description="Bullet points explaining why this score was assigned")


class InquiryAnalysisResponse(BaseModel):
    """Complete analyzed intelligence report returned for an inquiry."""
    inquiry_id: str = Field(..., description="Unique inquiry identifier (UUID)")
    timestamp: str = Field(..., description="ISO 8601 creation timestamp")
    customer_name: str
    email: str
    company_name: Optional[str] = None
    original_description: str
    budget_inr: Optional[float] = None
    timeline: Optional[str] = None
    
    # AI Extraction & Categorization
    service_category: str = Field(..., description="Primary Cynbit service matching the inquiry")
    secondary_services: List[str] = Field(default_factory=list, description="Related service disciplines")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI classification confidence")
    executive_summary: str = Field(..., description="Concise executive brief of the project for sales & engineering")
    extracted_requirements: List[str] = Field(default_factory=list, description="List of identified features and technical requirements")
    missing_information: List[str] = Field(default_factory=list, description="Gaps, missing specs, or unclarified assumptions")
    recommended_tech_stack: List[str] = Field(default_factory=list, description="Suggested technologies matching Cynbit expertise")
    suggested_next_actions: List[str] = Field(default_factory=list, description="Operational next steps for Cynbit team")
    discovery_questions: List[str] = Field(default_factory=list, description="Targeted questions for discovery call")
    estimated_timeline_range: str = Field(..., description="Estimated realistic delivery range")
    
    # Qualification Scoring
    lead_score: LeadScoreBreakdown
    processing_engine: str = Field(..., description="LLM model or heuristic processor used")


class InquiryListItem(BaseModel):
    """Lightweight summary schema for dashboard lists."""
    inquiry_id: str
    timestamp: str
    customer_name: str
    company_name: Optional[str] = None
    service_category: str
    priority_tier: str
    total_score: float
    budget_inr: Optional[float] = None
    timeline: Optional[str] = None


class HealthResponse(BaseModel):
    """System health and status response."""
    status: str
    service: str
    version: str
    groq_api_configured: bool
    model_name: str
    database_connected: bool
    total_inquiries_stored: int
