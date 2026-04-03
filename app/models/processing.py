from pydantic import BaseModel, ConfigDict

class ProcessingInstructions(BaseModel):
    model_config = ConfigDict(strict=True)
    confidence_threshold: float
    hitl_on_failure: bool
