from pydantic import BaseModel, Field
from typing import Optional, List

# Auth schemas
class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None

# Blueprint schemas
class BlueprintCreate(BaseModel):
    title: str = Field(..., min_length=1)
    category: str = Field(default="Daily")  # 'Daily' | 'Monthly'
    priority: str = Field(default="Standard")  # 'Low' | 'Medium' | 'High' | 'Critical'

class BlueprintResponse(BaseModel):
    id: str
    user_id: str
    title: str
    category: str
    priority: str
    assigned_by: Optional[str] = None
    notify_enabled: bool = True

    class Config:
        from_attributes = True

# Daily Log schemas
class DailyLogUpdate(BaseModel):
    status: str
    summary: str
    challenges: str
    mail_trail: Optional[str] = ""
    is_critical: bool
    notify_enabled: bool = True

class DailyLogResponse(BaseModel):
    id: str
    user_id: str
    blueprint_id: Optional[str] = None
    date: str
    status: str
    summary: str
    challenges: str
    mail_trail: Optional[str] = ""
    is_critical: bool
    notify_enabled: bool = True
    # Flattened blueprint details (optional)
    title: Optional[str] = "Orphaned Task"
    category: Optional[str] = "Daily"
    priority: Optional[str] = "Standard"
    assigned_by: Optional[str] = None

    class Config:
        from_attributes = True

# Report Archive schemas
class ReportResponse(BaseModel):
    id: str
    user_id: str
    date_generated: str
    file_url: str
    format: str

    class Config:
        from_attributes = True

# Handover schemas
class TaskAssignment(BaseModel):
    id: str
    assignee: str

class GenerateHandoverDraftRequest(BaseModel):
    included_tasks: List[TaskAssignment]
    is_update: bool
    team_members: Optional[str] = ""
    duration: Optional[str] = ""

class ExportHandoverRequest(BaseModel):
    is_update: bool
    location: str
    date_str: str
    duration: Optional[str] = ""
    ai_data: dict

    class Config:
        from_attributes = True

class GenerateReportRequest(BaseModel):
    date: Optional[str] = None
    included_log_ids: Optional[List[str]] = None

# Telegram Settings schemas
class TelegramSettingsUpdate(BaseModel):
    enabled: bool
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None

class TelegramSettingsResponse(BaseModel):
    enabled: bool
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    new_password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str


class GenerateSubsidiaryReportRequest(BaseModel):
    included_tasks: List[TaskAssignment]
    subsidiary_name: str

class ExportSubsidiaryReportRequest(BaseModel):
    subsidiary_name: str
    date_str: str
    ai_data: dict

    class Config:
        from_attributes = True


class TeamCreate(BaseModel):
    name: str
    unit_head_id: Optional[str] = None

class TeamOut(BaseModel):
    id: str
    name: str
    unit_head_id: Optional[str] = None
    member_count: int = 0

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
