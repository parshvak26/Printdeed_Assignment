from typing import Literal
from pydantic import BaseModel, ConfigDict

class Decision(BaseModel):
    """
    Decision result for the envelope, indicating routing.
    """
    model_config = ConfigDict(strict=True)
    route: Literal["auto_approve", "hitl_review", "rejected"]
