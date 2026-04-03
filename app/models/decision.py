from typing import Literal
from pydantic import BaseModel, ConfigDict

class Decision(BaseModel):
    model_config = ConfigDict(strict=True)
    route: Literal["auto_approve", "hitl_review", "rejected"]
