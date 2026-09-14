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

# --- STANDALONE CONFIG REVIEW SCHEMAS ---
class StandaloneFinding(BaseModel):
    title: str
    severity: Literal['HIGH', 'MID', 'LOW']
    observations: List[str]
    impact: List[str]
    recommendations: List[str]

class StandaloneAssessmentDraft(BaseModel):
    assessment_name: str
    scope: str
    introduction: str
    scope_items: List[str]
    findings: List[StandaloneFinding]

class GenerateStandaloneRequest(BaseModel):
    assessment_name: str
    scope: str
    raw_notes: str

class ExportStandaloneRequest(BaseModel):
    draft: StandaloneAssessmentDraft


# --- EXECUTIVE SUMMARY SCHEMAS ---
class ExSumObservationHighlight(BaseModel):
    domain: str
    finding_highlight: str

class ExSumTableRow1(BaseModel):
    domain: str
    critical: int
    high: int
    medium: int
    low: int
    total: int

class ExSumRecommendation(BaseModel):
    title: str
    impact: str
    action: str

class ExSumTableRow2(BaseModel):
    risk_rating: str
    critical: int
    high: int
    medium: int
    total: int

class ExSumFinding(BaseModel):
    finding_name: str
    description: str
    recommendation_step: str

class ExSumNistScore(BaseModel):
    function: str
    score: float
    rationale: str

class ExSumRoadmapYear(BaseModel):
    year_label: str
    theme: str
    initiatives: str

class ExecutiveSummaryDraft(BaseModel):
    bank_name: str
    country: str
    assessment_period: str
    scope_domains: List[str]
    overall_posture_rating: str
    overall_posture_summary: str
    critical_highlights: List[ExSumObservationHighlight]
    impact_highlights: List[str]
    table1_rows: List[ExSumTableRow1]
    additional_recommendations: List[ExSumRecommendation]
    risk_scope: str
    table2_rows: List[ExSumTableRow2]
    key_findings: List[ExSumFinding]
    soc_frameworks: str
    soc_purpose: str
    soc_overall_maturity_rating: str
    soc_overall_maturity_rationale: str
    nist_scores: List[ExSumNistScore]
    soc_cmm_target: str
    soc_key_gaps: List[str]
    soc_roadmap: List[ExSumRoadmapYear]

class GenerateExSumRequest(BaseModel):
    state: AssessmentState

class ExportExSumRequest(BaseModel):
    draft: ExecutiveSummaryDraft

