import sys
from pathlib import Path
import pytest

# Add backend to path for tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database.db import init_db
from app.schemas.inquiry import InquiryCreateRequest
from app.api.routes import (
    health_check,
    get_cynbit_services,
    process_inquiry,
    get_all_inquiries,
    get_inquiry_detail,
    remove_inquiry,
)
from app.main import root

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    yield

def test_root_endpoint():
    data = root()
    assert data["status"] == "online"
    assert "Cynbit" in data["company"]
    assert "Pranjal Jain" in data["author"]

def test_health_check_endpoint():
    res = health_check()
    assert res.status == "healthy"
    assert res.database_connected is True
    assert res.total_inquiries_stored >= 0

def test_cynbit_services_catalog():
    res = get_cynbit_services()
    assert len(res["services"]) >= 5
    service_names = [s["name"] for s in res["services"]]
    assert "AI/ML & Autonomous Agents" in service_names
    assert "Full-Stack Web & Cloud Platforms" in service_names

def test_inquiry_processing_and_retrieval_flow():
    payload = InquiryCreateRequest(
        customer_name="Test Enterprise Client",
        email="enterprise@cynbittest.com",
        company_name="Apex Global Ventures",
        project_description=(
            "We require an enterprise autonomous agent system that ingests financial PDFs, "
            "extracts structured ledger records, detects anomalies, and sends notifications. "
            "Must have a FastAPI microservices backend, PostgreSQL, and a modern dashboard."
        ),
        budget_inr=300000.0,
        timeline="8 weeks"
    )

    # 1. Process inquiry
    analysis = process_inquiry(payload)
    assert analysis.customer_name == "Test Enterprise Client"
    assert analysis.service_category == "AI/ML & Autonomous Agents"
    assert len(analysis.extracted_requirements) > 0
    assert analysis.lead_score.total_score >= 70.0
    assert analysis.lead_score.priority_tier in ["High", "Medium"]
    inquiry_id = analysis.inquiry_id

    # 2. Retrieve by ID
    retrieved = get_inquiry_detail(inquiry_id)
    assert retrieved["inquiry_id"] == inquiry_id
    assert retrieved["company_name"] == "Apex Global Ventures"

    # 3. Retrieve all inquiries
    inquiries_list = get_all_inquiries(limit=50)
    assert any(item["inquiry_id"] == inquiry_id for item in inquiries_list)

    # 4. Cleanup / deletion test
    del_res = remove_inquiry(inquiry_id)
    assert del_res["success"] is True
