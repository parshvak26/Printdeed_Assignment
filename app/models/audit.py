from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, ConfigDict

class AuditEntry(BaseModel):
    """
    A record of actions taken on the envelope for audit purposes.
    """
    model_config = ConfigDict(strict=True)
    timestamp: datetime
    service: str
    action: str
    envelope_id: str
    result: str
    details: Optional[Dict[str, str]] = None
