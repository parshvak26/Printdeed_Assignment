# README

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn pydantic pytest httpx
```

2. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- **POST `/validate`**: Validate an execution envelope.
- **POST `/match`**: Perform LLM-assisted commodity matching on an envelope.
- **POST `/process`**: Run full pipeline (validate -> match if needed -> return enriched envelope).
- **GET `/health`**: Health check endpoint (returns `{"status": "ok"}`).

## Example Request/Response

### Request (Process Envelope):

```json
{
  "shipment_id": {"value": "SHIP123", "confidence": 0.95},
  "recipient_name": {"value": "Alice", "confidence": 0.90},
  "commodity_code": {"value": "HS999", "confidence": 0.60},
  "commodity_desc": {"value": "Red apples", "confidence": 0.85},
  "ship_date": {"value": "2025-10-01", "confidence": 0.90},
  "processing_instructions": {"confidence_threshold": 0.80, "hitl_on_failure": true}
}
```

### Response:

```json
{
  "shipment_id": {"value": "SHIP123", "confidence": 0.95},
  "recipient_name": {"value": "Alice", "confidence": 0.90},
  "commodity_code": {"value": "HS999", "confidence": 0.60},
  "commodity_desc": {"value": "Red apples", "confidence": 0.85},
  "ship_date": {"value": "2025-10-01", "confidence": 0.90},
  "processing_instructions": {"confidence_threshold": 0.80, "hitl_on_failure": true},
  "decision": {"route": "hitl_review"},
  "matching_result": {
    "matched_code": "HS001",
    "match_confidence": 1.0,
    "rationale": "Exact match found for description 'red apples'",
    "fallback_used": true,
    "source": "catalog_exact"
  },
  "audit_trail": [
    {
      "timestamp": "2026-04-01T12:34:56.789Z",
      "service": "validation",
      "action": "validate",
      "envelope_id": "SHIP123",
      "result": "failed",
      "details": {"commodity_code": "Confidence 0.6 below threshold 0.8"}
    }
  ]
}
```

