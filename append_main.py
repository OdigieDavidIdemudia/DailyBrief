import sys

endpoints = '''
# API: Generate Subsidiary Report Draft
@app.post("/api/generate-subsidiary-draft")
async def api_generate_subsidiary_draft(
    req: GenerateSubsidiaryReportRequest,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    if not req.included_tasks:
        raise HTTPException(status_code=400, detail="No tasks selected for report.")
        
    task_ids = [t.id for t in req.included_tasks]
    
    logs = db.query(DailyLogModel).filter(
        DailyLogModel.id.in_(task_ids),
        DailyLogModel.user_id == current_user.id
    ).all()
    
    if not logs:
        raise HTTPException(status_code=404, detail="Selected logs not found.")
        
    logs_text = ""
    for log in logs:
        logs_text += f"Task Title: {log.blueprint.title if log.blueprint else log.title}\\n"
        logs_text += f"Category: {log.blueprint.category if log.blueprint else log.category}\\n"
        logs_text += f"Status: {log.status}\\n"
        logs_text += f"Summary: {log.summary}\\n"
        logs_text += f"Challenges: {log.challenges}\\n"
        logs_text += f"Critical: {log.is_critical}\\n"
        logs_text += "-" * 40 + "\\n"
        
    # Call Gemini API
    ai_response = await generate_subsidiary_report_content(logs_text, req.subsidiary_name)
    
    if "error" in ai_response:
        raise HTTPException(status_code=500, detail=ai_response["error"])
        
    return {"success": True, "ai_data": ai_response}

# API: Export Subsidiary Report DOCX
@app.post("/api/export-subsidiary-report")
async def api_export_subsidiary_report(
    req: ExportSubsidiaryReportRequest,
    current_user: UserSession = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # Verify user
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Determine which template to use
    template_name = "Subsidiary_Report_Template.docx"
    template_path = os.path.join(os.getcwd(), "static", "templates", template_name)
    
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail=f"Template {template_name} not found on server.")
        
    # Generate unique output filename
    output_filename = f"subsidiary_{uuid.uuid4().hex[:8]}.docx"
    output_path = os.path.join(tempfile.gettempdir(), output_filename)
    
    try:
        populate_subsidiary_docx(req.ai_data, template_path, output_path, req.subsidiary_name, req.date_str)
        return FileResponse(
            path=output_path,
            filename=f"Subsidiary_Report_{req.subsidiary_name}_{req.date_str}.docx",
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            background=background_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")
'''

with open('app/main.py', 'a', encoding='utf-8') as f:
    f.write('\n' + endpoints + '\n')
print('Appended endpoints successfully')
