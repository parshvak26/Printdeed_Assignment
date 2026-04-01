from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, model_validator

from app.models.match import MatchingResult
from app.models.audit import AuditEntry
from app.models.decision import Decision
from app.models.processing import ProcessingInstructions
from app.models.field import ExtractedField

class ExecutionEnvelope(BaseModel):
    """
    The main envelope containing extracted data, instructions, and fields
    to be enriched.
    """
    model_config = ConfigDict(strict=True)

    shipment_id: ExtractedField
    recipient_name: ExtractedField
    commodity_code: Optional[ExtractedField] = None
    commodity_desc: Optional[ExtractedField] = None
    ship_date: ExtractedField
    processing_instructions: ProcessingInstructions

    # Enriched fields (to be appended by services)
    audit_trail: List[AuditEntry] = []
    decision: Optional[Decision] = None
    matching_result: Optional[MatchingResult] = None

    @model_validator(mode='after')
    def check_required_fields(cls, env: ExecutionEnvelope) -> ExecutionEnvelope:
        """
        Ensure at least one of commodity_code or commodity_desc is provided.
        If both are missing, validation fails.
        """
        if env.commodity_code is None and env.commodity_desc is None:
            raise ValueError("At least one of commodity_code or commodity_desc must be provided")
        return env
