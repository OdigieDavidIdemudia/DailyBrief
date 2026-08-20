import os
from fastapi import Request

# I'll create a script to append the endpoints directly to app/main.py.

append_text = """
# ==============================================================================
# DOWNTIME REGISTER ENDPOINTS (Magnitude AI)
# ==============================================================================

@app.get("/downtime", response_class=HTMLResponse)
async def downtime_page(request: Request, db: Session = Depends(get_db)):
    auth_res = await get_current_user_from_cookie(request, db)
    if isinstance(auth_res, RedirectResponse):
        return auth_res
    return templates.TemplateResponse("downtime.html", {"request": request})

@app.post("/api/downtime/chat", response_model=schemas.MagnitudeResponse)
async def api_downtime_chat(req: schemas.GenerateDowntimeDraftRequest, db: Session = Depends(get_db)):
    # 1. We just pass the brief and history to Magnitude
    # Convert Pydantic MagnitudeMessage to dict
    history = [{"role": msg.role, "content": msg.content} for msg in req.history]
    
    result = await ai.generate_downtime_draft(req.brief, history)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

@app.post("/api/downtime/export")
async def api_downtime_export(req: schemas.ExportDowntimeRequest, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if isinstance(user, RedirectResponse):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Save to db
    report = db.query(models.DowntimeReportModel).filter(models.DowntimeReportModel.downtime_id == req.downtime_id).first()
    if not report:
        report = models.DowntimeReportModel(
            id=str(uuid.uuid4()),
            user_id=user.id,
            downtime_id=req.downtime_id
        )
        db.add(report)
    
    report.start_date = req.start_date
    report.start_time = req.start_time
    report.end_date = req.end_date
    report.end_time = req.end_time
    report.duration = req.duration
    report.system_affected = req.system_affected
    report.severity = req.severity
    report.reported_by = req.reported_by
    report.position = req.position
    
    report.impact_summary = req.impact_summary
    report.detection_and_notification = req.detection_and_notification
    report.root_cause_analysis = req.root_cause_analysis
    report.mitigation_and_recovery = req.mitigation_and_recovery
    report.preventive_measures = req.preventive_measures
    report.internal_communication = req.internal_communication
    report.external_communication = req.external_communication
    report.resource = req.resource
    
    db.commit()

    # Generate DOCX
    from app.downtime_report import build_downtime_docx
    data = req.dict()
    docx_path = build_downtime_docx(data)
    
    return FileResponse(
        path=docx_path,
        filename=os.path.basename(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/api/downtime/reports", response_model=List[schemas.DowntimeReportResponse])
async def api_downtime_reports(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if isinstance(user, RedirectResponse):
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    reports = db.query(models.DowntimeReportModel).filter(models.DowntimeReportModel.user_id == user.id).order_by(models.DowntimeReportModel.created_at.desc()).all()
    return reports
"""

with open("app/main.py", "a", encoding="utf-8") as f:
    f.write(append_text)
