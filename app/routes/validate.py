from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.models.envelope import ExecutionEnvelope
from app.services.validation import validate_envelope

router = APIRouter()

@router.post("/validate")
async def validate_endpoint(envelope: ExecutionEnvelope):
    try:
        updated_env = await validate_envelope(envelope)
        return updated_env
    except ValueError as e:
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
