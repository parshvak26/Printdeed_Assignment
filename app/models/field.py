from typing import Any
from pydantic import BaseModel, ConfigDict

class ExtractedField(BaseModel):
    """
    Represents an extracted field with its value and confidence.
    """
    model_config = ConfigDict(strict=True)
    value: Any
    confidence: float
