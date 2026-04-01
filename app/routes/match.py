from fastapi import APIRouter

from app.models.envelope import ExecutionEnvelope
from app.services.matching import match_commodity

router = APIRouter()

@router.post("/match")
async def match_endpoint(envelope: ExecutionEnvelope):
    """
    Endpoint to perform LLM-assisted commodity matching.
    """
    updated_env = await match_commodity(envelope)
    return updated_env.matching_result
