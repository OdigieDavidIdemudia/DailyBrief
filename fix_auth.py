with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_downtime_html_auth = """    auth_res = await get_current_user_from_cookie(request, db)
    if isinstance(auth_res, RedirectResponse):
        return auth_res"""
good_downtime_html_auth = """    token = request.cookies.get("tholder_session_token")
    if not token:
        return RedirectResponse(url="/login")"""

content = content.replace(bad_downtime_html_auth, good_downtime_html_auth)

bad_chat_sig = 'async def api_downtime_chat(req: GenerateDowntimeDraftRequest, db: Session = Depends(get_db)):'
good_chat_sig = 'async def api_downtime_chat(req: GenerateDowntimeDraftRequest, current_user: UserSession = Depends(get_current_user), db: Session = Depends(get_db)):'
content = content.replace(bad_chat_sig, good_chat_sig)

bad_export_sig = """async def api_downtime_export(req: ExportDowntimeRequest, request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if isinstance(user, RedirectResponse):
        raise HTTPException(status_code=401, detail="Unauthorized")"""
good_export_sig = """async def api_downtime_export(req: ExportDowntimeRequest, current_user: UserSession = Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_user"""
content = content.replace(bad_export_sig, good_export_sig)

bad_reports_sig = """async def api_downtime_reports(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if isinstance(user, RedirectResponse):
        raise HTTPException(status_code=401, detail="Unauthorized")"""
good_reports_sig = """async def api_downtime_reports(current_user: UserSession = Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_user"""
content = content.replace(bad_reports_sig, good_reports_sig)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed authentication references.')
