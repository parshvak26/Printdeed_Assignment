import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime
from unittest.mock import AsyncMock

client = TestClient(app)

def make_envelope(shipment_id="SHIP123", recipient_name="Alice",
                  commodity_desc="Red apples",
                  commodity_code=None, ship_date=None, threshold=0.8,
                  hitl=True):
    if ship_date is None:
        ship_date = datetime.utcnow().date().isoformat()
        
    envelope = {
        "shipment_id": {"value": shipment_id, "confidence": 0.95},
        "recipient_name": {"value": recipient_name, "confidence": 0.9},
        "ship_date": {"value": ship_date, "confidence": 0.9},
        "processing_instructions": {"confidence_threshold": threshold,
                                    "hitl_on_failure": hitl}
    }
    
    if commodity_code is not None:
        envelope["commodity_code"] = {"value": commodity_code, "confidence": 0.9}
        
    if commodity_desc is not None:
        envelope["commodity_desc"] = {"value": commodity_desc, "confidence": 0.9}
        
    return envelope

def test_happy_path_auto_approve():
    env = make_envelope(commodity_code="HS001", commodity_desc="Red apples", threshold=0.8)
    response = client.post("/process", json=env)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"]["route"] == "auto_approve"
    assert data["audit_trail"][-1]["result"] == "passed"

def test_low_confidence_hitl_review():
    env = make_envelope(commodity_code="HS002", commodity_desc="Green apples",
                        threshold=0.95, hitl=True)
    response = client.post("/process", json=env)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"]["route"] == "hitl_review"
    assert "commodity_code" in data["audit_trail"][-1]["details"]

def test_matching_results_added(monkeypatch):
    env = make_envelope(commodity_desc="Laptops", commodity_code=None,
                        threshold=0.95, hitl=False)
                        
    mock_response = {"code": "HS005", "confidence": 0.85, "rationale": "Matched Laptops to HS005"}
    async_mock = AsyncMock(return_value=mock_response)
    monkeypatch.setattr("app.services.matching.call_llm", async_mock)
    
    response = client.post("/process", json=env)
    assert response.status_code == 200
    data = response.json()
    
    assert data["matching_result"]["matched_code"] == "HS005"
    assert data["matching_result"]["match_confidence"] == 0.85
    assert data["matching_result"]["source"] == "llm_match"
    assert data["decision"]["route"] != "hitl_review"

def test_invalid_input_missing_required():
    env = {
        "shipment_id": {"value": "SHIP", "confidence": 0.9},
        "recipient_name": {"value": "Bob", "confidence": 0.9},
        "ship_date": {"value": datetime.utcnow().date().isoformat(), "confidence": 0.9},
        "processing_instructions": {"confidence_threshold": 0.8,
        "hitl_on_failure": False}
    }
    response = client.post("/process", json=env)
    assert response.status_code == 422

def test_llm_failure_graceful(monkeypatch):
    env = make_envelope(commodity_desc="Unknown product", commodity_code=None,
                        threshold=0.95, hitl=False)
                        
    async_mock = AsyncMock(side_effect=Exception("LLM API down"))
    monkeypatch.setattr("app.services.matching.call_llm", async_mock)
    
    response = client.post("/process", json=env)
    assert response.status_code == 200
    data = response.json()
    
    assert data["matching_result"]["source"] == "no_match"
    assert data["matching_result"]["fallback_used"] is False
    assert data["decision"]["route"] == "hitl_review"
    
    audit_msgs = [entry for entry in data["audit_trail"] if entry["service"] == "matching"]
    assert any("LLM API down" in entry.get("details", {}).get("error", "") for entry in audit_msgs)
