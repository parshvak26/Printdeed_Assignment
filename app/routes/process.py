from fastapi import APIRouter

from app.models.envelope import ExecutionEnvelope
from app.services.validation import validate_envelope
from app.services.matching import match_commodity

router = APIRouter()

@router.post("/process")
async def process_endpoint(envelope: ExecutionEnvelope):
    envelope = await validate_envelope(envelope)

    code_field = envelope.commodity_code
    threshold = envelope.processing_instructions.confidence_threshold

    if code_field is None or code_field.confidence < threshold:
        envelope = await match_commodity(envelope)

    return envelope
