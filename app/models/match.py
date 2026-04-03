from typing import Literal
from pydantic import BaseModel, ConfigDict

class MatchingResult(BaseModel):
    model_config = ConfigDict(strict=True)
    matched_code: str | None
    match_confidence: float
    rationale: str
    fallback_used: bool
    source: Literal["catalog_exact", "llm_match", "no_match"]
