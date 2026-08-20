from app.downtime_report import build_downtime_docx
import uuid
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, Request, Response, HTTPException, status, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from app.db import init_db, get_db, BlueprintModel, DailyLogModel, ReportArchiveModel, UserSettingsModel, UserModel, DowntimeReportModel
from app.auth import get_current_user, sign_in_user, UserSession, is_supabase_enabled
from app.schemas import MagnitudeResponse, GenerateDowntimeDraftRequest, ExportDowntimeRequest, DowntimeReportResponse, LoginRequest, BlueprintCreate, BlueprintResponse, DailyLogUpdate, DailyLogResponse, ReportResponse, GenerateReportRequest, TelegramSettingsUpdate, TelegramSettingsResponse, GenerateHandoverDraftRequest, ExportHandoverRequest, GenerateSubsidiaryReportRequest, ExportSubsidiaryReportRequest, ChangePasswordRequest, CreateUserRequest
from app.reports import generate_csv_report, generate_pdf_report, generate_xlsx_report
from app.notifications import notify_user_event, send_telegram_message
from app.ai import generate_handover_content, generate_subsidiary_report_content, generate_downtime_draft
from app.handover import populate_handover_docx
from app.subsidiary_report import populate_subsidiary_docx

# Initialize database schemas
init_db()

app = FastAPI(title="Tholder API", description="Automated Daily Task Tracker Backend")

@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Setup static folders
STATIC_DIR = os.path.join(os.getcwd(), "static")
REPORTS_DIR = os.path.join(STATIC_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# WAT Helper (West Africa Time is UTC+1)
def get_wat_date_string() -> str:
    # Get current UTC datetime and add 1 hour
    wat_now = datetime.utcnow() + timedelta(hours=1)
    return wat_now.strftime("%Y-%m-%d")

# Page Routes (serving HTML templates directly)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # If cookie exists, redirect to dashboard, otherwise login
    token = request.cookies.get("tholder_session_token")
    if token:
        return RedirectResponse(url="/dashboard")
    
    login_path = os.path.join(STATIC_DIR, "login.html")
    if not os.path.exists(login_path):
        raise HTTPException(status_code=404, detail="login.html template missing")
    return FileResponse(login_path)

@app.get("/admin", response_class=HTMLResponse)
async def read_admin(request: Request):
    token = request.cookies.get("tholder_session_token")
    if not token:
        return RedirectResponse(url="/login")
    admin_path = os.path.join(STATIC_DIR, "admin.html")
    if not os.path.exists(admin_path):
        raise HTTPException(status_code=404, detail="admin.html template missing")
    return FileResponse(admin_path)

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    token = request.cookies.get("tholder_session_token")
    if not token:
        return RedirectResponse(url="/login")
        
    dashboard_path = os.path.join(STATIC_DIR, "dashboard.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=404, detail="dashboard.html template missing")
    return FileResponse(dashboard_path)

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    token = request.cookies.get("tholder_session_token")
    if token:
        return RedirectResponse(url="/dashboard")
        
    login_path = os.path.join(STATIC_DIR, "login.html")
    if not os.path.exists(login_path):
        raise HTTPException(status_code=404, detail="login.html template missing")
    return FileResponse(login_path)

@app.get("/change_password", response_class=HTMLResponse)
async def get_change_password(request: Request):
    token = request.cookies.get("tholder_session_token")
    if not token:
        return RedirectResponse(url="/login")

    cp_path = os.path.join(STATIC_DIR, "change_password.html")
    if not os.path.exists(cp_path):
        raise HTTPException(status_code=404, detail="change_password.html template missing")
    return FileResponse(cp_path)

@app.get("/unit_head", response_class=HTMLResponse)
async def get_unit_head(request: Request):
    token = request.cookies.get("tholder_session_token")
    if not token:
        return RedirectResponse(url="/login")

    uh_path = os.path.join(STATIC_DIR, "unit_head.html")
    if not os.path.exists(uh_path):
        raise HTTPException(status_code=404, detail="unit_head.html template missing")
    return FileResponse(uh_path)

@app.get("/configure", response_class=HTMLResponse)
async def get_configure(request: Request):
    token = request.cookies.get("tholder_session_token")
    if not token:
        return RedirectResponse(url="/login")
        
    configure_path = os.path.join(STATIC_DIR, "configure.html")
    if not os.path.exists(configure_path):
        raise HTTPException(status_code=404, detail="configure.html template missing")
    return FileResponse(configure_path)

# API: Auth Routes
@app.post("/api/auth/change_password")
async def api_change_password(req: ChangePasswordRequest, current_user: UserSession = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    user.password_hash = pwd_context.hash(req.new_password)
    user.force_password_change = False
    db.commit()
    return {"success": True, "message": "Password changed successfully"}

@app.post("/api/auth/login")
async def api_login(credentials: LoginRequest, response: Response):
    res = await sign_in_user(credentials.email, credentials.password)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Sign in failed"))
    
    # Set session cookie
    if "session_token" in res:
        response.set_cookie(
            key="tholder_session_token",
            value=res["session_token"],
            httponly=True,
            max_age=60 * 60 * 24 * 7, # 1 week
            path="/",
            samesite="lax",
            secure=False  # Set True for production https
        )
    return res

@app.post("/api/auth/logout")
async def api_logout(response: Response):
    response.delete_cookie(key="tholder_session_token", path="/")
    return {"success": True, "message": "Signed out successfully"}

@app.get("/api/auth/me")
async def api_me(current_user: UserSession = Depends(get_current_user)):
    return {
        "success": True,
        "user": current_user.to_dict(),
        "is_supabase": is_supabase_enabled()
    }

@app.post("/api/auth/change-password")
async def api_change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    user = db.query(UserModel).filter(UserModel.username == current_user.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    user.password_hash = pwd_context.hash(req.new_password)
    db.commit()
    return {"success": True, "message": "Password changed successfully"}

@app.post("/api/auth/create-user")
async def api_create_user(
    req: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    if current_user.email != "admin":
        raise HTTPException(status_code=403, detail="Only administrator can perform this action")
        
    existing = db.query(UserModel).filter(UserModel.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
        
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    hashed_pwd = pwd_context.hash(req.password)
    
    new_user = UserModel(username=req.username, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"success": True, "message": f"User {req.username} created successfully"}


# API: Telegram Settings
@app.get("/api/settings/telegram", response_model=TelegramSettingsResponse)
async def api_get_telegram_settings(
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    settings = db.query(UserSettingsModel).filter(
        UserSettingsModel.user_id == current_user.id
    ).first()
    
    if not settings:
        return TelegramSettingsResponse(enabled=False, bot_token="", chat_id="")
        
    return TelegramSettingsResponse(
        enabled=settings.telegram_enabled,
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id
    )

@app.put("/api/settings/telegram")
async def api_update_telegram_settings(
    payload: TelegramSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    settings = db.query(UserSettingsModel).filter(
        UserSettingsModel.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = UserSettingsModel(user_id=current_user.id)
        db.add(settings)
        
    settings.telegram_enabled = payload.enabled
    settings.telegram_bot_token = payload.bot_token
    settings.telegram_chat_id = payload.chat_id
    
    db.commit()
    return {"success": True, "message": "Telegram settings updated successfully."}

@app.post("/api/settings/telegram/test")
async def api_test_telegram_settings(
    payload: TelegramSettingsUpdate,
    current_user: UserSession = Depends(get_current_user)
):
    if not payload.bot_token or not payload.chat_id:
        raise HTTPException(status_code=400, detail="Bot token and Chat ID are required to send a test message.")
        
    test_msg = f"🔔 *Tholder Test Alert*\n\nHello operator! This is a test notification verifying your Telegram integration settings work correctly."
    success = send_telegram_message(payload.bot_token, payload.chat_id, test_msg)
    
    if not success:
        raise HTTPException(status_code=400, detail="Telegram sending failed. Check bot token, chat ID, and make sure you started the bot (/start).")
        
    return {"success": True, "message": "Test notification sent successfully."}


# API: Blueprints
@app.get("/api/blueprints", response_model=List[BlueprintResponse])
async def api_get_blueprints(
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    blueprints = db.query(BlueprintModel).filter(
        BlueprintModel.user_id == current_user.id
    ).order_by(BlueprintModel.title.asc()).all()
    return blueprints

@app.post("/api/blueprints", response_model=BlueprintResponse)
async def api_create_blueprint(
    blueprint: BlueprintCreate,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    db_blueprint = BlueprintModel(
        user_id=current_user.id,
        title=blueprint.title,
        category=blueprint.category,
        priority=blueprint.priority
    )
    db.add(db_blueprint)
    db.commit()
    db.refresh(db_blueprint)
    return db_blueprint

@app.delete("/api/blueprints/{id}")
async def api_delete_blueprint(
    id: str,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    db_blueprint = db.query(BlueprintModel).filter(
        BlueprintModel.id == id,
        BlueprintModel.user_id == current_user.id
    ).first()
    
    if not db_blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
        
    db.delete(db_blueprint)
    db.commit()
    return {"success": True, "message": "Blueprint deleted successfully"}

# API: Daily Logs
@app.get("/api/logs", response_model=List[DailyLogResponse])
async def api_get_logs(
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    target_date = date or get_wat_date_string()
    
    # Clean up ANY orphaned logs (where blueprint is deleted)
    orphans_to_delete = db.query(DailyLogModel).filter(
        DailyLogModel.user_id == current_user.id,
        DailyLogModel.blueprint_id == None
    ).all()
    
    if orphans_to_delete:
        for orphan in orphans_to_delete:
            db.delete(orphan)
        db.commit()

    # 2. Fetch remaining logs
    logs = db.query(DailyLogModel).filter(
        DailyLogModel.user_id == current_user.id,
        DailyLogModel.date == target_date
    ).all()
    
    # 3. Carry over the most recent previous state if today's log is completely untouched
    try:
        from sqlalchemy import or_
        
        untouched_logs = [l for l in logs if l.status == "Pending" and not l.summary and not l.challenges and not l.mail_trail]
        if untouched_logs:
            db_modified = False
            for l in untouched_logs:
                # Find the most recent log for this blueprint before the target date that has actual content/status
                prev = db.query(DailyLogModel).filter(
                    DailyLogModel.user_id == current_user.id,
                    DailyLogModel.blueprint_id == l.blueprint_id,
                    DailyLogModel.date < target_date,
                    or_(
                        DailyLogModel.status != "Pending",
                        DailyLogModel.summary != "",
                        DailyLogModel.challenges != "",
                        DailyLogModel.mail_trail != ""
                    )
                ).order_by(DailyLogModel.date.desc()).first()
                
                if prev:
                    l.status = prev.status
                    l.summary = prev.summary
                    l.challenges = prev.challenges
                    l.mail_trail = prev.mail_trail
                    l.is_critical = prev.is_critical
                    db_modified = True
            
            if db_modified:
                db.commit()
    except Exception as e:
        print(f"Error carrying over logs: {e}")
    
    # Flatten/Join blueprint details
    response_logs = []
    for log in logs:
        blueprint = log.blueprint
        response_logs.append(
            DailyLogResponse(
                id=log.id,
                user_id=log.user_id,
                blueprint_id=log.blueprint_id,
                date=log.date,
                status=log.status,
                summary=log.summary,
                challenges=log.challenges,
                mail_trail=log.mail_trail,
                is_critical=log.is_critical,
                title=blueprint.title if blueprint else "Deleted Task",
                category=blueprint.category if blueprint else "Archived",
                priority=blueprint.priority if blueprint else "Standard",
                assigned_by=blueprint.assigned_by if blueprint else None
            )
        )
    return response_logs

@app.put("/api/logs/{id}", response_model=DailyLogResponse)
async def api_update_log(
    id: str,
    log_update: DailyLogUpdate,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    db_log = db.query(DailyLogModel).filter(
        DailyLogModel.id == id,
        DailyLogModel.user_id == current_user.id
    ).first()
    
    if not db_log:
        raise HTTPException(status_code=404, detail="Log entry not found")
        
    previously_critical = db_log.is_critical
    previously_blocked = db_log.status == "Blocked"
    
    db_log.status = log_update.status
    db_log.summary = log_update.summary
    db_log.challenges = log_update.challenges
    db_log.mail_trail = log_update.mail_trail
    db_log.is_critical = log_update.is_critical
    db_log.notify_enabled = log_update.notify_enabled
    
    db.commit()
    db.refresh(db_log)
    
    blueprint = db_log.blueprint
    
    # Trigger Telegram notifications on status/blocker transitions
    if (db_log.is_critical and not previously_critical) or (db_log.status == "Blocked" and not previously_blocked):
        task_title = blueprint.title if blueprint else "Deleted Task"
        priority = blueprint.priority if blueprint else "Standard"
        challenges = db_log.challenges if db_log.challenges else "No details provided."
        alert_msg = (
            f"🚨 *Critical Blocker Alert*\n\n"
            f"*Task*: {task_title}\n"
            f"*Priority*: {priority}\n"
            f"*Status*: {db_log.status}\n"
            f"*Challenges*: {challenges}\n\n"
            f"Review immediately on dashboard."
        )
        notify_user_event(current_user.id, db, alert_msg)
        
    return DailyLogResponse(
        id=db_log.id,
        user_id=db_log.user_id,
        blueprint_id=db_log.blueprint_id,
        date=db_log.date,
        status=db_log.status,
        summary=db_log.summary,
        challenges=db_log.challenges,
        mail_trail=db_log.mail_trail,
        is_critical=db_log.is_critical,
        title=blueprint.title if blueprint else "Deleted Task",
        category=blueprint.category if blueprint else "Archived",
        priority=blueprint.priority if blueprint else "Standard",
                assigned_by=blueprint.assigned_by if blueprint else None
    )

# API: Roster locking
@app.post("/api/roster/lock")
async def api_lock_roster(
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    blueprints = db.query(BlueprintModel).filter(
        BlueprintModel.user_id == current_user.id
    ).all()
    
    if not blueprints:
        raise HTTPException(status_code=400, detail="No task blueprints configured. Create blueprints first.")
        
    # Generate dates for the remainder of the current month in WAT
    wat_now = datetime.utcnow() + timedelta(hours=1)
    year = wat_now.year
    month = wat_now.month
    
    # Find last day of the current month
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    current_day = wat_now.day
    
    count = 0
    for day in range(current_day, last_day + 1):
        date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
        
        for bp in blueprints:
            # Check duplicate conflict
            exists = db.query(DailyLogModel).filter(
                DailyLogModel.user_id == current_user.id,
                DailyLogModel.blueprint_id == bp.id,
                DailyLogModel.date == date_str
            ).first()
            
            if not exists:
                db_log = DailyLogModel(
                    user_id=current_user.id,
                    blueprint_id=bp.id,
                    date=date_str,
                    status="Pending",
                    summary="",
                    challenges="",
                    is_critical=False
                )
                db.add(db_log)
                count += 1
                
    db.commit()
    
    # Notify user via Telegram
    month_name = wat_now.strftime("%B %Y")
    lock_msg = f"🔒 *Roster Locked for {month_name}*\n\nStaged {count} task logs for the remainder of this month."
    notify_user_event(current_user.id, db, lock_msg)
    
    return {"success": True, "message": f"Generated roster: staged {count} logs for the remainder of this month."}

# API: Generate Reports
async def handle_generate_report(user_id: str, email: str, date_str: str, db: Session, included_log_ids: Optional[List[str]] = None) -> dict:
    logs = db.query(DailyLogModel).filter(
        DailyLogModel.user_id == user_id,
        DailyLogModel.date == date_str
    ).all()
    
    if not logs:
        return {"success": False, "error": f"No task logs found for date {date_str}."}

    if included_log_ids is not None:
        logs = [l for l in logs if l.id in included_log_ids]
    # Get username for friendly download name
    username = email.split("@")[0] if email else "User"
        
    try:
        # Keep filename as user_id to prevent parsing errors in serve_report
        pdf_filename = f"{user_id}_{date_str}.pdf"
        csv_filename = f"{user_id}_{date_str}.csv"
        xlsx_filename = f"{user_id}_{date_str}.xlsx"
        
        query_str = f"?name={username}"
        if included_log_ids is not None:
            query_str += "&included=" + ",".join(included_log_ids)
        
        pdf_url = f"/reports/{pdf_filename}{query_str}"
        csv_url = f"/reports/{csv_filename}{query_str}"
        xlsx_url = f"/reports/{xlsx_filename}{query_str}"
        
        # Check and record report archive
        # PDF report log
        pdf_report = db.query(ReportArchiveModel).filter(
            ReportArchiveModel.user_id == user_id,
            ReportArchiveModel.file_url == pdf_url,
            ReportArchiveModel.format == "pdf"
        ).first()
        if not pdf_report:
            pdf_report = ReportArchiveModel(user_id=user_id, file_url=pdf_url, format="pdf", date_generated=datetime.utcnow().isoformat())
            db.add(pdf_report)
            
        # CSV report log
        csv_report = db.query(ReportArchiveModel).filter(
            ReportArchiveModel.user_id == user_id,
            ReportArchiveModel.file_url == csv_url,
            ReportArchiveModel.format == "csv"
        ).first()
        if not csv_report:
            csv_report = ReportArchiveModel(user_id=user_id, file_url=csv_url, format="csv", date_generated=datetime.utcnow().isoformat())
            db.add(csv_report)
            
        # XLSX report log
        xlsx_report = db.query(ReportArchiveModel).filter(
            ReportArchiveModel.user_id == user_id,
            ReportArchiveModel.file_url == xlsx_url,
            ReportArchiveModel.format == "xlsx"
        ).first()
        if not xlsx_report:
            xlsx_report = ReportArchiveModel(user_id=user_id, file_url=xlsx_url, format="xlsx", date_generated=datetime.utcnow().isoformat())
            db.add(xlsx_report)
            
        db.commit()
        db.refresh(pdf_report)
        db.refresh(csv_report)
        db.refresh(xlsx_report)
        
        # Trigger Telegram alert for daily report generation
        pdf_url_full = f"http://127.0.0.1:3000{pdf_url}"
        csv_url_full = f"http://127.0.0.1:3000{csv_url}"
        xlsx_url_full = f"http://127.0.0.1:3000{xlsx_url}"
        
        total = len(logs)
        completed = len([l for l in logs if l.status == 'Completed'])
        critical = len([l for l in logs if l.is_critical])
        
        report_msg = (
            f"📄 *Daily Operations Report Generated*\n\n"
            f"*Date*: {date_str}\n"
            f"*Total Tasks*: {total}\n"
            f"*Completed*: {completed}\n"
            f"*Blocked / Critical*: {critical}\n\n"
            f"📥 [Download PDF Brief]({pdf_url_full})\n"
            f"📥 [Download XLSX Spreadsheet]({xlsx_url_full})\n"
            f"📥 [Download CSV Log]({csv_url_full})"
        )
        notify_user_event(user_id, db, report_msg)
        
        return {
            "success": True,
            "pdf": ReportResponse.model_validate(pdf_report),
            "csv": ReportResponse.model_validate(csv_report),
            "xlsx": ReportResponse.model_validate(xlsx_report)
        }
    except Exception as e:
        print(f"Report generation error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/reports/generate")
async def api_generate_report(
    req: GenerateReportRequest,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    target_date = req.date or get_wat_date_string()
    res = await handle_generate_report(current_user.id, current_user.email, target_date, db, req.included_log_ids)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@app.get("/api/reports", response_model=List[ReportResponse])
async def api_get_reports(
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    reports = db.query(ReportArchiveModel).filter(
        ReportArchiveModel.user_id == current_user.id
    ).order_by(ReportArchiveModel.date_generated.desc()).all()
    return reports

async def format_user_name(username: str) -> str:
    parts = username.split('.')
    return ' '.join(p.capitalize() for p in parts)

@app.get("/api/cron/morning-plan")
@app.post("/api/cron/morning-plan")
async def api_cron_morning_plan(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("authorization")
    cron_secret = os.getenv("CRON_SECRET")
    if cron_secret and auth_header != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized cron request")
        
    today_str = get_wat_date_string()
    
    # Query distinct user IDs with tasks today
    active_users = db.query(DailyLogModel.user_id).filter(
        DailyLogModel.date == today_str
    ).distinct().all()
    
    user_ids = [u[0] for u in active_users]
    results = []
    
    for uid in user_ids:
        # Fetch user
        user = db.query(UserModel).filter(UserModel.id == uid).first()
        if not user:
            continue
        
        # Fetch tasks for today
        logs = db.query(DailyLogModel).filter(
            DailyLogModel.user_id == uid,
            DailyLogModel.date == today_str
        ).all()
        
        if not logs:
            continue
            
        formatted_name = await format_user_name(user.username)
        # Format DD/MM/YYYY
        date_parts = today_str.split('-')
        display_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}" if len(date_parts) == 3 else today_str
        
        lines = [f"Daily Plan for {display_date} - {formatted_name}\n"]
        for log in logs:
            if not log.notify_enabled:
                continue
            blueprint = log.blueprint
            title = blueprint.title if blueprint else "Deleted Task"
            lines.append(f"- {title}")
            
        # Send via telegram (split into chunks if too long)
        settings = db.query(UserSettingsModel).filter(UserSettingsModel.user_id == uid).first()
        if settings and settings.telegram_enabled and settings.telegram_bot_token and settings.telegram_chat_id:
            try:
                import httpx
                tg_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
                # Build chunks under 4096 chars, keeping header in first chunk
                header = lines[0]
                task_lines = lines[1:]
                chunks = []
                current = header
                for entry in task_lines:
                    if len(current) + len(entry) + 1 > 4000:
                        chunks.append(current)
                        current = entry
                    else:
                        current = current + "\n" + entry
                if current:
                    chunks.append(current)
                async with httpx.AsyncClient() as client:
                    for chunk in chunks:
                        await client.post(tg_url, json={"chat_id": settings.telegram_chat_id, "text": chunk})
                results.append({"user_id": uid, "status": "SUCCESS"})
            except Exception as e:
                results.append({"user_id": uid, "status": "FAILED", "error": str(e)})
        else:
            results.append({"user_id": uid, "status": "SKIPPED", "error": "Telegram not configured"})
            
    return {"results": results}

@app.get("/api/cron/evening-summary")
@app.post("/api/cron/evening-summary")
async def api_cron_evening_summary(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("authorization")
    cron_secret = os.getenv("CRON_SECRET")
    if cron_secret and auth_header != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Unauthorized cron request")
        
    today_str = get_wat_date_string()
    
    # Query distinct user IDs with tasks today
    active_users = db.query(DailyLogModel.user_id).filter(
        DailyLogModel.date == today_str
    ).distinct().all()
    
    user_ids = [u[0] for u in active_users]
    results = []
    
    for uid in user_ids:
        # Fetch user
        user = db.query(UserModel).filter(UserModel.id == uid).first()
        if not user:
            continue
        
        # Fetch tasks for today
        logs = db.query(DailyLogModel).filter(
            DailyLogModel.user_id == uid,
            DailyLogModel.date == today_str
        ).all()
        
        if not logs:
            continue
            
        formatted_name = await format_user_name(user.username)
        date_parts = today_str.split('-')
        display_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}" if len(date_parts) == 3 else today_str
        
        lines = [f"Daily Plan for {display_date} - {formatted_name}\n"]
        for log in logs:
            if not log.notify_enabled:
                continue
            # Skip untouched tasks (no summary and still Pending)
            if not log.summary and log.status == "Pending":
                continue
            blueprint = log.blueprint
            title = blueprint.title if blueprint else "Deleted Task"
            status_text = log.summary if log.summary else log.status
            lines.append(f"- {title}\n   > {status_text}\n")
            
        # Send via telegram (split into chunks if too long)
        settings = db.query(UserSettingsModel).filter(UserSettingsModel.user_id == uid).first()
        if settings and settings.telegram_enabled and settings.telegram_bot_token and settings.telegram_chat_id:
            try:
                import httpx
                tg_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
                # Build chunks under 4096 chars, keeping header in first chunk
                header = lines[0]
                task_lines = lines[1:]
                chunks = []
                current = header
                for entry in task_lines:
                    if len(current) + len(entry) + 1 > 4000:
                        chunks.append(current)
                        current = entry
                    else:
                        current = current + "\n" + entry
                if current:
                    chunks.append(current)
                async with httpx.AsyncClient() as client:
                    for chunk in chunks:
                        await client.post(tg_url, json={"chat_id": settings.telegram_chat_id, "text": chunk})
                results.append({"user_id": uid, "status": "SUCCESS"})
            except Exception as e:
                results.append({"user_id": uid, "status": "FAILED", "error": str(e)})
        else:
            results.append({"user_id": uid, "status": "SKIPPED", "error": "Telegram not configured"})
            
    return {"results": results}

# API: Visualizer
@app.get("/api/visualizer/weekly")
async def api_get_visualizer_weekly(
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    # Return completion rates for the past 7 days (ending today)
    wat_now = datetime.utcnow() + timedelta(hours=1)
    
    days = []
    # Loop back 6 days + today = 7 days
    for i in range(6, -1, -1):
        day_date = wat_now - timedelta(days=i)
        date_str = day_date.strftime("%Y-%m-%d")
        day_name = day_date.strftime("%A")
        
        # Calculate completion rate
        logs = db.query(DailyLogModel).filter(
            DailyLogModel.user_id == current_user.id,
            DailyLogModel.date == date_str
        ).all()
        
        total = len(logs)
        completed = len([l for l in logs if l.status == "Completed"])
        
        rate = int((completed / total) * 100) if total > 0 else 0
        label = "Today" if i == 0 else day_name[:3]
        
        # Determine status
        if total == 0:
            status = "empty"
        elif completed == total:
            status = "consistent"
        elif i == 0:
            status = "pending" # Today is still in progress
        else:
            status = "missed"
            
        if day_name not in ("Saturday", "Sunday"):
            days.append({
                "day": day_name,
                "rate": rate,
                "label": label,
                "date": date_str,
                "total": total,
                "completed": completed,
                "status": status
            })
        
    # Calculate active streak (days where all scheduled tasks were completed)
    streak = 0
    # Walk backward up to 30 days
    for d_offset in range(30):
        check_date = wat_now - timedelta(days=d_offset)
        check_date_str = check_date.strftime("%Y-%m-%d")
        
        logs = db.query(DailyLogModel).filter(
            DailyLogModel.user_id == current_user.id,
            DailyLogModel.date == check_date_str
        ).all()
        
        total = len(logs)
        completed = len([l for l in logs if l.status == "Completed"])
        
        if total > 0:
            if completed == total:
                streak += 1
            else:
                if d_offset == 0:
                    # Today is incomplete. We skip today but don't break the streak.
                    pass
                else:
                    break
        else:
            # Empty days don't increment, but don't break the streak either
            pass
            
    return {
        "streak": streak,
        "days": days
    }

# API: Generate Handover Draft
@app.post("/api/generate-handover-draft")
async def api_generate_handover_draft(
    req: GenerateHandoverDraftRequest,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    if not req.included_tasks:
        raise HTTPException(status_code=400, detail="No tasks selected for handover.")
        
    task_ids = [t.id for t in req.included_tasks]
    assignee_map = {t.id: t.assignee for t in req.included_tasks}
        
    logs = db.query(DailyLogModel).filter(
        DailyLogModel.user_id == current_user.id,
        DailyLogModel.id.in_(task_ids)
    ).all()
    
    if not logs:
        raise HTTPException(status_code=404, detail="No valid task logs found.")
        
    # Format logs into a readable string for the AI
    logs_text = ""
    for l in logs:
        blueprint_title = l.blueprint.title if l.blueprint else "Deleted Task"
        assignee = assignee_map.get(l.id, "")
        logs_text += f"Task: {blueprint_title}\nAssignee: {assignee}\nStatus: {l.status}\nSummary: {l.summary}\nChallenges: {l.challenges}\nMail Trail: {l.mail_trail}\n\n"
        
    # Call Gemini API
    ai_response = await generate_handover_content(logs_text, req.team_members, req.is_update)
    
    if "error" in ai_response:
        raise HTTPException(status_code=500, detail=ai_response["error"])
        
    return {"success": True, "ai_data": ai_response}

# API: Export Handover DOCX
@app.post("/api/export-handover")
async def api_export_handover(
    req: ExportHandoverRequest,
    current_user: UserSession = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    import uuid
    import tempfile
    from fastapi.responses import FileResponse
    
    # Determine which template to use
    template_name = "Handover Update.docx" if req.is_update else "Handover.docx"
    template_path = os.path.join(os.getcwd(), "static", "templates", template_name)
    
    if not os.path.exists(template_path):
        raise HTTPException(status_code=500, detail=f"Template {template_name} not found on server.")
        
    # Generate unique output filename
    output_filename = f"handover_{uuid.uuid4().hex[:8]}.docx"
    output_path = os.path.join(tempfile.gettempdir(), output_filename)
    
    try:
        populate_handover_docx(req.ai_data, template_path, output_path, req.is_update, req.location, req.date_str, req.duration)
        # In a robust implementation we might delete the file after, but /tmp will be cleaned up
        return FileResponse(
            path=output_path, 
            filename=output_filename, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Access-Control-Expose-Headers": "Content-Disposition"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")

# Serve generated static report files directly
@app.get("/reports/{filename}")
async def serve_report(filename: str, included: Optional[str] = None, name: Optional[str] = None, db: Session = Depends(get_db)):
    parts = filename.rsplit("_", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid report format")
    
    user_id = parts[0]
    date_and_ext = parts[1].rsplit(".", 1)
    if len(date_and_ext) != 2:
        raise HTTPException(status_code=400, detail="Invalid report format")
        
    date_str = date_and_ext[0]
    ext = date_and_ext[1]
    
    logs = db.query(DailyLogModel).filter(
        DailyLogModel.user_id == user_id,
        DailyLogModel.date == date_str
    ).all()
    
    if not logs:
        raise HTTPException(status_code=404, detail="No task logs found for this date")

    if included:
        included_ids = included.split(",")
        logs = [l for l in logs if l.id in included_ids]
        if not logs:
            raise HTTPException(status_code=404, detail="No selected task logs found")
        
    if ext == "pdf":
        content = bytes(generate_pdf_report(logs, date_str))
        media_type = "application/pdf"
    elif ext == "csv":
        content = generate_csv_report(logs, date_str)
        media_type = "text/csv"
    elif ext == "xlsx":
        content = generate_xlsx_report(logs, date_str)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
        
    username = name if name else "User"
    download_name = f"{username.replace('.', '_')}_daily_brief_{date_str}.{ext}"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={download_name}"}
    )

# Mount served static web assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")




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
        logs_text += f"Task Title: {log.blueprint.title if log.blueprint else log.title}\n"
        logs_text += f"Category: {log.blueprint.category if log.blueprint else log.category}\n"
        logs_text += f"Status: {log.status}\n"
        logs_text += f"Summary: {log.summary}\n"
        logs_text += f"Challenges: {log.challenges}\n"
        logs_text += f"Critical: {log.is_critical}\n"
        logs_text += "-" * 40 + "\n"
        
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
    import uuid
    import tempfile
    from fastapi.responses import FileResponse

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


from app.admin import router as admin_router
app.include_router(admin_router)

from app.unit_head import router as unit_head_router
app.include_router(unit_head_router)

# Dummy change to force Vercel rebuild

# ==============================================================================
# DOWNTIME REGISTER ENDPOINTS (Magnitude AI)
# ==============================================================================

@app.get("/downtime", response_class=HTMLResponse)
async def downtime_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("tholder_session_token")
    if not token:
        return RedirectResponse(url="/login")
    downtime_path = os.path.join(STATIC_DIR, "downtime.html")
    if not os.path.exists(downtime_path):
        raise HTTPException(status_code=404, detail="downtime.html template missing")
    return FileResponse(downtime_path)

@app.post("/api/downtime/chat", response_model=MagnitudeResponse)
async def api_downtime_chat(req: GenerateDowntimeDraftRequest, current_user: UserSession = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. We just pass the brief and history to Magnitude
    # Convert Pydantic MagnitudeMessage to dict
    history = [{"role": msg.role, "content": msg.content} for msg in req.history]
    
    result = await generate_downtime_draft(req.brief, history)
    
    if "error" in result:
        return {"status": "complete", "draft": {"impact_summary": "DEBUG ERROR: " + str(result["error"]), "detection_and_notification": "", "root_cause_analysis": "", "mitigation_and_recovery": "", "preventive_measures": ""}}
        
    return result

@app.post("/api/downtime/export")
async def api_downtime_export(req: ExportDowntimeRequest, current_user: UserSession = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = current_user
        
        report = db.query(DowntimeReportModel).filter(DowntimeReportModel.downtime_id == req.downtime_id).first()
        if not report:
            report = DowntimeReportModel(
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
        
        out_path = build_downtime_docx(req.dict())
        
        return FileResponse(out_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=os.path.basename(out_path))
    except Exception as e:
        print("EXPORT ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/downtime/reports", response_model=List[DowntimeReportResponse])
async def api_downtime_reports(current_user: UserSession = Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_user
        
    reports = db.query(DowntimeReportModel).filter(DowntimeReportModel.user_id == user.id).order_by(DowntimeReportModel.created_at.desc()).all()
    return reports


# Catch-all: mount static fallback for root files
@app.get("/{filename}")
async def serve_static_root_files(filename: str):
    # E.g. favicon.ico, custom icons, fallback loads
    file_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    # If HTML request and file not found, fall back to /
    if filename.endswith(".html"):
        return RedirectResponse(url="/")
    raise HTTPException(status_code=404, detail="File not found")