"""Unit tests for CREBrokerAI custom tools."""

import json

import pytest


def test_lead_scoring_tool():
    from crebrokerai.tools.scoring_tool import LeadScoringTool

    tool = LeadScoringTool()
    result = json.loads(tool._run(json.dumps({
        "lease_expiry": "2026-09-30",
        "growth_signal_strength": "high",
        "recent_funding_m": 35.0,
        "market_heat": "hot",
        "size_fit": "good",
    })))

    assert "lead_score" in result
    assert "lead_tier" in result
    assert 1 <= result["lead_score"] <= 100
    assert result["lead_tier"] in ("hot", "warm", "cold")


def test_lead_scoring_cold():
    from crebrokerai.tools.scoring_tool import LeadScoringTool

    tool = LeadScoringTool()
    result = json.loads(tool._run(json.dumps({
        "lease_expiry": "2028-12-31",
        "growth_signal_strength": "low",
        "recent_funding_m": 0,
        "market_heat": "cool",
        "size_fit": "poor",
    })))

    assert result["lead_tier"] == "cold"
    assert result["lead_score"] < 50


def test_property_matching_tool():
    from crebrokerai.tools.matching_tool import PropertyMatchingTool

    tool = PropertyMatchingTool()
    result = json.loads(tool._run(json.dumps({
        "company_name": "Test Corp",
        "industry": "SaaS / Technology",
        "city": "Austin",
        "state": "TX",
        "current_lease_sqft": 8000,
        "employee_count": 100,
    })))

    assert isinstance(result, list)
    assert len(result) <= 3
    if result:
        assert "building_name" in result[0]
        assert "match_score_pct" in result[0]


def test_cre_lease_search():
    from crebrokerai.tools.cre_data import CRELeaseSearchTool

    tool = CRELeaseSearchTool()
    result = json.loads(tool._run(json.dumps({
        "markets": ["Austin"],
        "industries": ["technology"],
    })))

    assert isinstance(result, list)
    assert len(result) > 0
    assert "company_name" in result[0]


def test_cre_company_research():
    from crebrokerai.tools.cre_data import CRECompanyResearchTool

    tool = CRECompanyResearchTool()
    result = json.loads(tool._run("NovaTech"))

    assert "company_name" in result
    assert "NovaTech" in result["company_name"]


def test_email_tool_mock():
    from crebrokerai.tools.email_tool import SendGridEmailTool

    tool = SendGridEmailTool()
    result = json.loads(tool._run(json.dumps({
        "to_email": "test@example.com",
        "subject": "Office Space Opportunity",
        "body": "Hi, we have space for you.\n\nReply STOP to unsubscribe.",
        "prospect_name": "Test User",
    })))

    assert result["status"] == "mock_sent"


def test_voice_tool_mock():
    from crebrokerai.tools.voice_tool import TwilioVoiceCallTool

    tool = TwilioVoiceCallTool()
    result = json.loads(tool._run(json.dumps({
        "phone": "+15125551234",
        "prospect_name": "Jane Doe",
        "company_name": "Test Corp",
        "call_script": "Hello, this is a test call.",
    })))

    assert result["status"] == "mock_completed"
    assert "outcome" in result


def test_compliance_email():
    from crebrokerai.utils.compliance import check_email_compliance

    # Should fail: no unsubscribe
    result = check_email_compliance("Test Subject", "Just a body.", "test@email.com")
    assert not result.passed

    # Should pass
    result = check_email_compliance(
        "Test Subject",
        "Body content.\n\nReply STOP to unsubscribe.",
        "test@email.com",
    )
    assert result.passed


def test_compliance_call():
    from crebrokerai.utils.compliance import check_call_compliance

    result = check_call_compliance("+15125551234")
    assert result.passed

    result = check_call_compliance("123")
    assert not result.passed
