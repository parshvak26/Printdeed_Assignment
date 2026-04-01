from datetime import datetime, timedelta
from typing import Dict

from app.models.envelope import ExecutionEnvelope
from app.models.audit import AuditEntry
from app.models.decision import Decision

async def validate_envelope(envelope: ExecutionEnvelope) -> ExecutionEnvelope:
    """
    Perform validation on the envelope:
    - Check confidence thresholds
    - Check date rules
    - Set decision.route
    - Append audit entry
    """
    failures: Dict[str, str] = {}
    threshold = envelope.processing_instructions.confidence_threshold

    # Check confidence for all fields
    fields_to_check = {
        'shipment_id': envelope.shipment_id,
        'recipient_name': envelope.recipient_name,
        'ship_date': envelope.ship_date
    }

    # Include code and desc if provided
    if envelope.commodity_code is not None:
        fields_to_check['commodity_code'] = envelope.commodity_code
    if envelope.commodity_desc is not None:
        fields_to_check['commodity_desc'] = envelope.commodity_desc

    for field_name, field in fields_to_check.items():
        # flag if confidence below threshold
        if field.confidence < threshold:
            failures[field_name] = f"Confidence {field.confidence} below threshold {threshold}"

    # Validate ship_date range
    try:
        ship_date = datetime.fromisoformat(str(envelope.ship_date.value))
        now = datetime.utcnow()
        # Check not in future
        if ship_date > now:
            failures['ship_date'] = "Ship date is in the future"
        # Check not older than 365 days
        elif now - ship_date > timedelta(days=365):
            failures['ship_date'] = "Ship date is older than 365 days"
    except Exception as e:
        failures['ship_date'] = f"Invalid date format: {envelope.ship_date.value}"

    # Determine decision route
    hitl = envelope.processing_instructions.hitl_on_failure
    if not failures:
        route = "auto_approve"
        result = "passed"
    else:
        if hitl:
            route = "hitl_review"
        else:
            route = "rejected"
        result = "failed"

    envelope.decision = Decision(route=route)

    # Create audit entry
    audit_entry = AuditEntry(
        timestamp=datetime.utcnow(),
        service="validation",
        action="validate",
        envelope_id=str(envelope.shipment_id.value),
        result=result,
        details=failures if failures else None
    )
    envelope.audit_trail.append(audit_entry)

    return envelope
