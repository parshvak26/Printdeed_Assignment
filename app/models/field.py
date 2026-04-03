from typing import Any
from pydantic import BaseModel, ConfigDict

class ExtractedField(BaseModel):
    model_config = ConfigDict(strict=True)
    value: Any
    confidence: float
