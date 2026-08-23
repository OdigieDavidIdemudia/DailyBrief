from pydantic import BaseModel, Field
from typing import List, Optional

class KnowledgeSharingInput(BaseModel):
    topic: str = Field(..., description="Main topic title")
    target_audience: str = Field(default="Security Team", description="Who the presentation is for")
    details: str = Field(..., description="Raw notes or details to include")

class KSGenerationOptions(BaseModel):
    author: str = "David Odigie"
    org_unit: str = "Security Monitoring and Threat Intelligence"

class KSGenerateRequest(BaseModel):
    input_data: KnowledgeSharingInput
    generation_options: Optional[KSGenerationOptions] = KSGenerationOptions()

class KSRefineRequest(BaseModel):
    draft: dict
    corrections: str

class KSExportRequest(BaseModel):
    draft: dict
    format: str = "pptx"
