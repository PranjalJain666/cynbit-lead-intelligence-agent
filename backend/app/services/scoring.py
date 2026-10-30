import re
from typing import Optional, List, Tuple
from app.schemas.inquiry import LeadScoreBreakdown

def calculate_lead_score(
    project_description: str,
    budget_inr: Optional[float] = None,
    timeline: Optional[str] = None,
    service_category: Optional[str] = None,
    extracted_features_count: int = 0
) -> LeadScoreBreakdown:
    """
    Computes an explainable, rule-based qualification score (0-100)
    evaluating budget sufficiency, timeline feasibility, scope clarity,
    and strategic alignment with Cynbit's core competencies.
    """
    rationale: List[str] = []

    # 1. Budget Score (0 to 25 points)
    budget_score = 0.0
    if budget_inr is not None and budget_inr > 0:
        if budget_inr >= 250000:
            budget_score = 25.0
            rationale.append(f"Strong enterprise/growth budget of ₹{budget_inr:,.0f} (+25/25 pts)")
        elif budget_inr >= 120000:
            budget_score = 20.0
            rationale.append(f"Moderate commercial budget of ₹{budget_inr:,.0f} (+20/25 pts)")
        elif budget_inr >= 50000:
            budget_score = 15.0
            rationale.append(f"Standard MVP budget of ₹{budget_inr:,.0f} (+15/25 pts)")
        else:
            budget_score = 8.0
            rationale.append(f"Low stated budget (₹{budget_inr:,.0f}) may require phased MVP scoping (+8/25 pts)")
    else:
        budget_score = 10.0
        rationale.append("Budget not specified; requires discovery qualification (+10/25 pts)")

    # 2. Timeline Score (0 to 20 points)
    timeline_score = 0.0
    timeline_str = (timeline or "").lower().strip()
    if timeline_str:
        # Check for urgent/unrealistic words
        if any(w in timeline_str for w in ["asap", "immediate", "urgent", "yesterday", "1 week", "few days"]):
            timeline_score = 10.0
            rationale.append(f"Urgent timeline '{timeline}' poses expedited delivery delivery risk (+10/20 pts)")
        elif any(w in timeline_str for w in ["month", "week", "quarter", "days"]):
            # Extract digits if possible
            match = re.search(r"(\d+)\s*(month|week)", timeline_str)
            if match:
                val = int(match.group(1))
                unit = match.group(2)
                weeks = val * 4 if "month" in unit else val
                if 3 <= weeks <= 16:
                    timeline_score = 20.0
                    rationale.append(f"Realistic, well-defined delivery schedule of '{timeline}' (+20/20 pts)")
                elif weeks > 16:
                    timeline_score = 15.0
                    rationale.append(f"Extended timeline '{timeline}' allows structured milestones (+15/20 pts)")
                else:
                    timeline_score = 12.0
                    rationale.append(f"Compressed delivery timeline '{timeline}' (+12/20 pts)")
            else:
                timeline_score = 16.0
                rationale.append(f"Specific timeline provided: '{timeline}' (+16/20 pts)")
        else:
            timeline_score = 14.0
            rationale.append(f"Custom timeline stated: '{timeline}' (+14/20 pts)")
    else:
        timeline_score = 8.0
        rationale.append("No timeline stated; timeline milestone definition needed (+8/20 pts)")

    # 3. Scope Clarity Score (0 to 30 points)
    scope_score = 0.0
    desc_words = len(project_description.strip().split())
    
    # Assess technical clarity indicators
    tech_signals = [
        "api", "database", "dashboard", "auth", "real-time", "analytics", "payment",
        "frontend", "backend", "cloud", "aws", "docker", "mobile", "integration",
        "model", "pipeline", "predictive", "recommendation", "automation", "workflow"
    ]
    detected_tech = [t for t in tech_signals if t in project_description.lower()]
    
    clarity_points = 0.0
    if desc_words >= 80 or extracted_features_count >= 5:
        clarity_points += 18.0
    elif desc_words >= 40 or extracted_features_count >= 3:
        clarity_points += 13.0
    else:
        clarity_points += 7.0

    # Bonus for detected concrete tech/feature elements
    tech_bonus = min(12.0, len(detected_tech) * 2.5)
    scope_score = min(30.0, clarity_points + tech_bonus)
    
    if scope_score >= 25:
        rationale.append(f"High technical depth: {desc_words} words, identified {len(detected_tech)} architectural markers (+{scope_score:.1f}/30 pts)")
    elif scope_score >= 17:
        rationale.append(f"Moderate requirements clarity: {desc_words} words with foundational requirements (+{scope_score:.1f}/30 pts)")
    else:
        rationale.append(f"Brief/high-level inquiry ({desc_words} words); scope needs discovery extraction (+{scope_score:.1f}/30 pts)")

    # 4. Strategic Alignment with Cynbit Offerings (0 to 25 points)
    cynbit_fit_score = 0.0
    desc_lower = project_description.lower()
    cat_lower = (service_category or "").lower()

    if any(k in desc_lower or k in cat_lower for k in ["ai", "machine learning", "ml", "llm", "agent", "automation", "computer vision", "predictive", "nlp"]):
        cynbit_fit_score = 25.0
        rationale.append("Directly aligns with Cynbit's flagship AI/ML & Autonomous Agents practice (+25/25 pts)")
    elif any(k in desc_lower or k in cat_lower for k in ["full stack", "cloud", "devops", "enterprise", "saas", "crm", "erp", "web"]):
        cynbit_fit_score = 22.0
        rationale.append("Strong alignment with Cynbit's Full Stack Web & Cloud Engineering division (+22/25 pts)")
    elif any(k in desc_lower or k in cat_lower for k in ["mobile", "app", "ios", "android", "flutter", "react native"]):
        cynbit_fit_score = 20.0
        rationale.append("Matches Cynbit's Mobile App Development capabilities (+20/25 pts)")
    else:
        cynbit_fit_score = 15.0
        rationale.append("Standard custom software inquiry within Cynbit's broader engineering umbrella (+15/25 pts)")

    # Total Score computation
    total_score = round(budget_score + timeline_score + scope_score + cynbit_fit_score, 1)

    # Tier assignment
    if total_score >= 75.0:
        priority_tier = "High"
    elif total_score >= 50.0:
        priority_tier = "Medium"
    else:
        priority_tier = "Low"

    return LeadScoreBreakdown(
        budget_score=round(budget_score, 1),
        timeline_score=round(timeline_score, 1),
        scope_clarity_score=round(scope_score, 1),
        cynbit_fit_score=round(cynbit_fit_score, 1),
        total_score=total_score,
        priority_tier=priority_tier,
        rationale=rationale
    )
