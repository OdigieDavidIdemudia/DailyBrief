from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class Observation(BaseModel):
    segment_sector: str
    title: str
    raw_note: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    evidence_screenshot_path: Optional[str] = None
    
class Advisory(BaseModel):
    topic: str
    context: str
    recommendation: str

class Finding(Observation):
    id: str # UUID
    finding_number: Optional[int] = None
    impact: str = ""
    recommendation: str = ""
    generated_by: Literal["magnitude", "manual_override", "pending"] = "pending"
    reviewed: bool = False

class ToolAssessment(BaseModel):
    tool_id: str
    tool_display_name: str
    assessment_date: str
    performed_by: str
    status: Literal["in_progress", "ready_to_generate", "generated", "logged_to_master", "closed"] = "in_progress"
    findings: List[Finding] = []
    advisories: List[Advisory] = []

class Subsidiary(BaseModel):
    subsidiary_name: str = ""
    country: str = ""
    engagement_ref: str = ""
    assessment_period_start: str = ""
    assessment_period_end: str = ""
    lead_assessor: str = ""

# API Request Models
class GenerateFindingRequest(BaseModel):
    tool_display_name: str
    observation: Observation

class ExportDocxRequest(BaseModel):
    subsidiary_name: str
    tool: ToolAssessment

class ExportExcelRequest(BaseModel):
    subsidiary_name: str
    tools: List[ToolAssessment] # To log all tools that are ready

# The persistence state file schema
class AssessmentState(BaseModel):
    subsidiary: Subsidiary = Subsidiary()
    tools: Dict[str, ToolAssessment] = {}

class BulkGenerateRequest(BaseModel):
    tool_display_name: str
    raw_bulk_notes: str
