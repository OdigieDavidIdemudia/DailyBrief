with open('app/schemas.py', 'a', encoding='utf-8') as f:
    f.write('''
# Downtime Register Schemas
class MagnitudeMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class GenerateDowntimeDraftRequest(BaseModel):
    brief: str
    history: List[MagnitudeMessage] = []
    
    # Metadata context from UI
    start_date: str = ""
    start_time: str = ""
    end_date: str = ""
    end_time: str = ""
    system_affected: str = ""

class MagnitudeResponse(BaseModel):
    status: str # "needs_clarification" or "complete"
    questions: Optional[List[str]] = None
    draft: Optional[dict] = None

class ExportDowntimeRequest(BaseModel):
    downtime_id: str
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    duration: str
    system_affected: str
    severity: str
    reported_by: str
    position: str
    
    impact_summary: str
    detection_and_notification: str
    root_cause_analysis: str
    mitigation_and_recovery: str
    preventive_measures: str
    internal_communication: str
    external_communication: str
    resource: str

class DowntimeReportResponse(BaseModel):
    id: str
    downtime_id: str
    start_date: str
    system_affected: str
    severity: str
    created_at: str

    class Config:
        from_attributes = True
''')
