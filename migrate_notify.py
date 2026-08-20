import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("REAL_DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://neondb_owner:npg_ZQ80CFlOtPjp@ep-patient-breeze-aht4ab80-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE task_blueprints ADD COLUMN notify_enabled BOOLEAN DEFAULT TRUE;"))
        conn.commit()
        print("Added notify_enabled to task_blueprints")
    except Exception as e:
        print("Error altering task_blueprints:", e)
        
    try:
        conn.execute(text("ALTER TABLE daily_logs ADD COLUMN notify_enabled BOOLEAN DEFAULT TRUE;"))
        conn.commit()
        print("Added notify_enabled to daily_logs")
    except Exception as e:
        print("Error altering daily_logs:", e)
