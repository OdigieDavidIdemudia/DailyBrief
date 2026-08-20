import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Boolean, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

# Determine database URL: fallback to local SQLite file
DATABASE_URL = os.getenv("REAL_DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://neondb_owner:npg_ZQ80CFlOtPjp@ep-patient-breeze-aht4ab80-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Create engine. If SQLite, enable thread sharing for FastAPI
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. Blueprint Model
class BlueprintModel(Base):
    __tablename__ = "task_blueprints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # 'Daily' | 'Monthly'
    priority = Column(String(50), nullable=False)  # 'Low' | 'Medium' | 'High' | 'Critical'
    assigned_by = Column(String(255), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notify_enabled = Column(Boolean, nullable=False, default=True)

# 2. Daily Log Model
class DailyLogModel(Base):
    __tablename__ = "daily_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    blueprint_id = Column(String(36), ForeignKey("task_blueprints.id", ondelete="SET NULL"), nullable=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    status = Column(String(50), nullable=False, default="Pending")  # 'Pending' | 'In Progress' | 'Completed' | 'Flagged' | 'Blocked'
    summary = Column(Text, nullable=False, default="")
    challenges = Column(Text, nullable=False, default="")
    mail_trail = Column(Text, default="")
    is_critical = Column(Boolean, nullable=False, default=False)
    notify_enabled = Column(Boolean, nullable=False, default=True)

    blueprint = relationship("BlueprintModel")

class DowntimeReportModel(Base):
    __tablename__ = "downtime_reports"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    downtime_id = Column(String, index=True) # e.g. SOC/19082026/001
    
    # Metadata
    start_date = Column(String)
    start_time = Column(String)
    end_date = Column(String)
    end_time = Column(String)
    duration = Column(String)
    system_affected = Column(String)
    severity = Column(String)
    reported_by = Column(String)
    position = Column(String)
    
    # Narrative Fields
    impact_summary = Column(Text)
    detection_and_notification = Column(Text)
    root_cause_analysis = Column(Text)
    mitigation_and_recovery = Column(Text)
    preventive_measures = Column(Text)
    internal_communication = Column(Text)
    external_communication = Column(Text)
    resource = Column(String)
    
    # Raw conversation history (JSON string) for Magnitude
    chat_history = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# 3. Reports Archive Model
class ReportArchiveModel(Base):
    __tablename__ = "reports_archive"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    date_generated = Column(String(255), nullable=False, default=lambda: datetime.utcnow().isoformat())
    file_url = Column(Text, nullable=False)
    format = Column(String(10), nullable=False)  # 'pdf' | 'csv'

# 4. User Settings Model
class UserSettingsModel(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    telegram_enabled = Column(Boolean, nullable=False, default=False)
    telegram_bot_token = Column(String(255), nullable=True)
    telegram_chat_id = Column(String(255), nullable=True)

# 5. User Model for Authentication
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user") # 'user' or 'admin' or 'unit_head'
    status = Column(String(50), nullable=False, default="active") # 'active' or 'deactivated'
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_out_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    unit_head_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    force_password_change = Column(Boolean, nullable=False, default=False)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 6. Team Model
class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    unit_head_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

# Initialize database tables
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Initialize default admin user if not exists
    db = SessionLocal()
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        
        admin_user = db.query(UserModel).filter(UserModel.username == "admin").first()
        if not admin_user:
            hashed_pwd = pwd_context.hash("admin2026")
            new_admin = UserModel(username="admin", password_hash=hashed_pwd)
            db.add(new_admin)
            db.commit()

        # Seed david.odigie
        david_user = db.query(UserModel).filter(UserModel.username == "david.odigie").first()
        if not david_user:
            hashed_pwd = pwd_context.hash("Icanbuild2026")
            new_david = UserModel(username="david.odigie", password_hash=hashed_pwd)
            db.add(new_david)
            db.commit()

        # Seed david.odige
        david_user2 = db.query(UserModel).filter(UserModel.username == "david.odige").first()
        if not david_user2:
            hashed_pwd = pwd_context.hash("Icanbuild2026")
            new_david2 = UserModel(username="david.odige", password_hash=hashed_pwd)
            db.add(new_david2)
            db.commit()

        # Seed estylily.johnson
        esty_user = db.query(UserModel).filter(UserModel.username == "estylily.johnson").first()
        if not esty_user:
            hashed_pwd = pwd_context.hash("ICanbuild!123")
            new_esty = UserModel(username="estylily.johnson", password_hash=hashed_pwd)
            db.add(new_esty)
            db.commit()
    except Exception as e:
        print(f"Failed to initialize admin user: {e}")
    finally:
        db.close()

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

