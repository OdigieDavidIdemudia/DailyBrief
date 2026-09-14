from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict

class ThreatInput(BaseModel):
    raw_text: str = Field(..., description="The user's free-text description of the threat.")
    title: Optional[str] = None
    date: Optional[str] = None
    cve: Optional[List[str]] = None
    how: Optional[str] = None
    severity_hint: Optional[Literal["low", "medium", "high", "critical"]] = None
    source_urls: Optional[List[str]] = None
    malware_score: Optional[int] = Field(None, ge=0, le=100)

class IOCInput(BaseModel):
    type: Literal["ip_address", "domain", "url", "file_name", "file_path", "file_hash_md5", "file_hash_sha1", "file_hash_sha256", "registry_key", "user_account", "email_address", "c2_address", "mutex", "user_agent", "process_name", "other"]
    value: str
    context: Optional[str] = None
    confidence: Literal["confirmed", "high", "medium", "low"] = "confirmed"

class GenerationOptions(BaseModel):
    auto_enrich_iocs: bool = True
    ioc_target_count: int = Field(8, ge=3)
    reference_target_count: int = Field(5, ge=2, le=10)
    author: str = "David Odigie"
    reviewer: str = "Fatima Jinadu"
    org_unit: str = "Security Monitoring and Threat Intelligence"
    report_id_prefix: str = "TIA"
    output_formats: List[Literal["docx", "structured_json"]] = ["docx", "structured_json"]

class DetectionRuleOutput(BaseModel):
    target: str
    logic: str
    notes: Optional[str] = None

class IOCOutput(BaseModel):
    type: str
    value: str
    context: Optional[str] = None
    confidence: Literal["confirmed", "high", "medium", "low"]
    provenance: Literal["user_supplied", "magnitude_research"]
    source_url: Optional[str] = None

class RecommendationOutput(BaseModel):
    action: str
    sub_items: Optional[List[str]] = None

class ReferenceOutput(BaseModel):
    source: str
    title: str
    url: str
    date: Optional[str] = None


class AttackChainStep(BaseModel):
    step_title: str
    step_description: str

class MitreAttckMapping(BaseModel):
    technique_id: str
    technique_name: str
    context: str

class ManualCheck(BaseModel):
    label: str
    code: str
    note: Optional[str] = None

class ActionPlan(BaseModel):
    label: str
    code: Optional[str] = None
    note: Optional[str] = None
    action_items: Optional[List[str]] = None

class TIAStructuredOutput(BaseModel):
    report_id: str
    title: str
    date: str
    prepared_by: str
    reviewed_by: str
    org_unit: str
    executive_summary: str
    critical_impact: str
    threat_mechanism: str
    attack_chain: List[AttackChainStep]
    tactics_and_red_flags: List[str]
    affected_distributions: List[str]
    mitre_attck: List[MitreAttckMapping]
    iocs: List[IOCOutput]
    manual_checks: List[ManualCheck]
    assessment_statement: str
    assessment_priority: str
    immediate_mitigations: List[ActionPlan]
    priority_actions: List[ActionPlan]
    alternative_controls: List[ActionPlan]
    environmental_considerations: str
    references: List[ReferenceOutput]
class TIAGenerateRequest(BaseModel):
    threat: ThreatInput
    raw_iocs: Optional[str] = None
    iocs: Optional[List[IOCInput]] = []
    generation_options: Optional[GenerationOptions] = GenerationOptions()

class TIARefineRequest(BaseModel):
    draft: dict
    corrections: str

class TIAExportRequest(BaseModel):
    draft: dict
    format: str = "docx"
