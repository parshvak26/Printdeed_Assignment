from pydantic import BaseModel, ConfigDict

class ProcessingInstructions(BaseModel):
    """
    Instructions guiding processing, including confidence threshold and HITL flag.
    """
    model_config = ConfigDict(strict=True)
    confidence_threshold: float
    hitl_on_failure: bool
