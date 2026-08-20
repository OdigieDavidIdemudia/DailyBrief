import os
from dotenv import load_dotenv
load_dotenv()

from app.db import SessionLocal, UserModel, DailyLogModel, ReportArchiveModel, UserSettingsModel, BlueprintModel

db = SessionLocal()

try:
    users = db.query(UserModel).all()
    print(f"Found {len(users)} users")
    
    for user in users:
        username = user.username
        real_id = user.id
        mock_id = f"mock-user-{username.replace('@', '-').replace('.', '-')}"
        
        if mock_id == real_id:
            print(f"  {username}: already using real UUID, skip")
            continue
        
        logs_updated = db.query(DailyLogModel).filter(DailyLogModel.user_id == mock_id).update(
            {"user_id": real_id}, synchronize_session=False
        )
        
        blueprints_updated = db.query(BlueprintModel).filter(BlueprintModel.user_id == mock_id).update(
            {"user_id": real_id}, synchronize_session=False
        )
        
        reports = db.query(ReportArchiveModel).filter(ReportArchiveModel.user_id == mock_id).all()
        for r in reports:
            r.user_id = real_id
            if mock_id in r.file_url:
                r.file_url = r.file_url.replace(mock_id, real_id)
        reports_updated = len(reports)
        
        settings_updated = db.query(UserSettingsModel).filter(UserSettingsModel.user_id == mock_id).update(
            {"user_id": real_id}, synchronize_session=False
        )
        
        print(f"  User: {username}")
        print(f"    Logs migrated:     {logs_updated}")
        print(f"    Reports migrated:  {reports_updated}")
        print(f"    Settings migrated: {settings_updated}")
    
    db.commit()
    print("Migration committed successfully!")
except Exception as e:
    db.rollback()
    print(f"ERROR: {e}")
    raise
finally:
    db.close()
