import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas_assessment import (
    AssessmentState, GenerateFindingRequest, BulkGenerateRequest, ExportDocxRequest, ExportExcelRequest, Finding, ToolAssessment
)
from app.assessment_ai import generate_finding_text, generate_bulk_findings
from app.assessment_docx import render_assessment_report
from app.assessment_excel import append_tool_findings_to_excel, get_dashboard_metrics
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/assessment", tags=["Assessment Pipeline"])

STATE_FILE = "assessment_state.json"

def _load_state() -> AssessmentState:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return AssessmentState.model_validate_json(f.read())
        except Exception as e:
            print("Failed to load state:", e)
    return AssessmentState()

def _save_state(state: AssessmentState):
    with open(STATE_FILE, "w") as f:
        f.write(state.model_dump_json(indent=2))

@router.get("/state", response_model=AssessmentState)
async def get_state():
    return _load_state()

@router.post("/state", response_model=AssessmentState)
async def update_state(state: AssessmentState):
    _save_state(state)
    return state


@router.post("/generate/bulk")
async def bulk_generate(req: BulkGenerateRequest):
    # Call AI
    ai_results = await generate_bulk_findings(req)
    
    findings = []
    for item in ai_results:
        f = Finding(
            id=str(uuid.uuid4()),
            segment_sector=item.get("segment_sector", "General"),
            title=item.get("title", "Untitled Finding"),
            raw_note=item.get("raw_note", ""),
            severity=item.get("severity", "MEDIUM"),
            impact=item.get("impact", ""),
            recommendation=item.get("recommendation", "")
        )
        findings.append(f)
    return findings

@router.post("/generate")
async def generate_finding(req: GenerateFindingRequest):
    # Call AI
    ai_result = await generate_finding_text(req)
    
    # Create Finding object
    finding = Finding(
        id=str(uuid.uuid4()),
        segment_sector=req.observation.segment_sector,
        title=req.observation.title,
        raw_note=req.observation.raw_note,
        severity=req.observation.severity,
        evidence_screenshot_path=req.observation.evidence_screenshot_path,
        impact=ai_result.get("impact", ""),
        recommendation=ai_result.get("recommendation", ""),
        generated_by="magnitude",
        reviewed=False
    )
    return finding

@router.post("/export/docx")
async def export_docx(req: ExportDocxRequest):
    out_dir = os.path.join("reports", req.subsidiary_name or "Unknown")
    os.makedirs(out_dir, exist_ok=True)
    
    # Check if there are any unreviewed findings
    has_unreviewed = any(not f.reviewed for f in req.tool.findings)
    draft_tag = "-DRAFT" if has_unreviewed else ""
    
    safe_date = req.tool.assessment_date.replace("/", "-")
    filename = f"{req.subsidiary_name} - {req.tool.tool_display_name} Assessment Findings - {safe_date}{draft_tag}.docx"
    out_path = os.path.join(out_dir, filename)
    
    try:
        render_assessment_report(req.subsidiary_name, req.tool, out_path)
        return {"file_url": f"/reports/{req.subsidiary_name or 'Unknown'}/{filename}", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/excel")
async def export_excel(req: ExportExcelRequest):
    out_dir = os.path.join("reports", req.subsidiary_name or "Unknown")
    os.makedirs(out_dir, exist_ok=True)
    
    master_template = os.path.join("static", "reports", "Security_Assessment_Master_Template.xlsx")
    target_excel = os.path.join(out_dir, "Security_Assessment_Master.xlsx")
    
    # If the target doesn't exist yet for this subsidiary, copy the master template
    if not os.path.exists(target_excel):
        import shutil
        shutil.copy(master_template, target_excel)
        
    try:
        # We append tools one by one
        for tool in req.tools:
            append_tool_findings_to_excel(tool, target_excel, target_excel)
            
        return {"file_url": f"/reports/{req.subsidiary_name or 'Unknown'}/Security_Assessment_Master.xlsx", "filename": "Security_Assessment_Master.xlsx"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_dashboard(subsidiary_name: str):
    target_excel = os.path.join("reports", subsidiary_name, "Security_Assessment_Master.xlsx")
    metrics = get_dashboard_metrics(target_excel)
    return metrics
