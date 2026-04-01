from datetime import datetime
import httpx

from app.models.envelope import ExecutionEnvelope
from app.models.match import MatchingResult
from app.models.audit import AuditEntry

# In-memory dataset for commodity matching
HS_CATALOG = [
    {"hs_code": "HS001", "description": "Red apples", "category": "Fruit", "restricted": False, "typical_weight_kg": 0.1},
    {"hs_code": "HS002", "description": "Green apples", "category": "Fruit", "restricted": False, "typical_weight_kg": 0.1},
    {"hs_code": "HS003", "description": "Bananas", "category": "Fruit", "restricted": False, "typical_weight_kg": 0.2},
    {"hs_code": "HS004", "description": "Strawberries", "category": "Fruit", "restricted": False, "typical_weight_kg": 0.05},
    {"hs_code": "HS005", "description": "Laptops", "category": "Electronics", "restricted": False, "typical_weight_kg": 2.0},
    {"hs_code": "HS006", "description": "Smartphones", "category": "Electronics", "restricted": False, "typical_weight_kg": 0.5},
    {"hs_code": "HS007", "description": "Chocolate", "category": "Food", "restricted": False, "typical_weight_kg": 0.01},
    {"hs_code": "HS008", "description": "Wine", "category": "Beverage", "restricted": True, "typical_weight_kg": 1.5},
    {"hs_code": "HS009", "description": "Cigarettes", "category": "Tobacco", "restricted": True, "typical_weight_kg": 0.02},
    {"hs_code": "HS010", "description": "Perfume", "category": "Cosmetics", "restricted": False, "typical_weight_kg": 0.1}
]

async def call_llm(commodity_desc: str) -> dict:
    """
    Calls an LLM API to find the best HS code match for the description.
    Returns a dict with keys: code, confidence, rationale.
    """
    # Example: using a hypothetical LLM endpoint (this should be configurable)
    LLM_ENDPOINT = "https://api.example.com/llm-match"
    prompt = (
        f"Given the product description '{commodity_desc}', find the best matching HS code. "
        f"Possible HS codes and descriptions: {HS_CATALOG}."
    )
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(LLM_ENDPOINT, json={"prompt": prompt})
        response.raise_for_status()
        data = response.json()
        return data

async def match_commodity(envelope: ExecutionEnvelope) -> ExecutionEnvelope:
    """
    Match commodity description to HS code using an in-memory catalog and LLM.
    """
    desc_field = envelope.commodity_desc
    code_field = envelope.commodity_code

    threshold = envelope.processing_instructions.confidence_threshold

    # If existing code has high confidence, skip matching
    if code_field is not None and code_field.confidence >= threshold:
        # Use existing code as a fallback exact match
        result = MatchingResult(
            matched_code=code_field.value,
            match_confidence=code_field.confidence,
            rationale="Existing HS code above threshold, using directly",
            fallback_used=True,
            source="catalog_exact"
        )
        envelope.matching_result = result
        return envelope

    # Try exact description match in catalog
    if desc_field:
        desc = str(desc_field.value).lower()
        for item in HS_CATALOG:
            if item["description"].lower() == desc:
                result = MatchingResult(
                    matched_code=item["hs_code"],
                    match_confidence=1.0,
                    rationale=f"Exact match found for description '{desc}'",
                    fallback_used=True,
                    source="catalog_exact"
                )
                envelope.matching_result = result
                return envelope

    # Use LLM to find best match
    try:
        llm_response = await call_llm(desc_field.value) # type: ignore
        matched_code = llm_response.get("code")
        confidence = float(llm_response.get("confidence", 0))
        rationale = llm_response.get("rationale", "")

        result = MatchingResult(
            matched_code=matched_code,
            match_confidence=confidence,
            rationale=rationale,
            fallback_used=False,
            source="llm_match"
        )
    except Exception as e:
        # LLM call failed or returned bad output
        result = MatchingResult(
            matched_code=None,
            match_confidence=0.0,
            rationale=f"LLM matching failed: {str(e)}",
            fallback_used=False,
            source="no_match"
        )
        # Append audit for LLM failure
        audit_entry = AuditEntry(
            timestamp=datetime.utcnow(),
            service="matching",
            action="llm_match",
            envelope_id=str(envelope.shipment_id.value),
            result="failed",
            details={"error": str(e)}
        )
        envelope.audit_trail.append(audit_entry)

    # Decision override if confidence too low
    if result.match_confidence < 0.70 and envelope.decision:
        envelope.decision.route = "hitl_review"

    envelope.matching_result = result
    return envelope
