import sys
from pathlib import Path

# Add backend to path for tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.scoring import calculate_lead_score

def test_high_priority_lead_scoring():
    """Validates that a comprehensive AI project with high budget scores in the High tier."""
    score = calculate_lead_score(
        project_description=(
            "We need an AI-powered predictive maintenance and analytics pipeline for industrial equipment. "
            "System must ingest IoT sensor telemetry, run automated anomaly detection using machine learning models, "
            "provide a real-time FastAPI backend, React dashboard, role-based authentication, and automated alerts."
        ),
        budget_inr=350000.0,
        timeline="8 weeks",
        service_category="AI/ML & Autonomous Agents",
        extracted_features_count=5
    )

    assert score.priority_tier == "High"
    assert score.total_score >= 75.0
    assert score.budget_score == 25.0
    assert score.timeline_score == 20.0
    assert score.cynbit_fit_score == 25.0
    assert len(score.rationale) >= 4


def test_medium_priority_lead_scoring():
    """Validates that a moderate budget mobile app project receives a Medium tier score."""
    score = calculate_lead_score(
        project_description=(
            "We want to build a cross-platform mobile application for customer loyalty rewards. "
            "Requires user authentication, QR code scanning, and Firebase integration."
        ),
        budget_inr=90000.0,
        timeline="6 weeks",
        service_category="Mobile Application Development",
        extracted_features_count=3
    )

    assert score.priority_tier in ["Medium", "High"]
    assert 50.0 <= score.total_score <= 85.0
    assert score.budget_score == 15.0
    assert len(score.rationale) >= 3


def test_low_priority_vague_lead_scoring():
    """Validates that a brief, unbudgeted, urgent inquiry falls into the Low priority tier."""
    score = calculate_lead_score(
        project_description="Make a quick website for our shop as soon as possible.",
        budget_inr=None,
        timeline="ASAP",
        service_category="Custom Software Solutions",
        extracted_features_count=1
    )

    assert score.priority_tier == "Low"
    assert score.total_score < 50.0
    assert score.budget_score == 10.0  # missing budget
    assert score.timeline_score == 10.0 # urgent timeline risk
    assert len(score.rationale) >= 3
