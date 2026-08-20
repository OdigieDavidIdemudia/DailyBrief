import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import ReportArchiveModel

POSTGRES_URL = "postgresql://neondb_owner:npg_ZQ80CFlOtPjp@ep-patient-breeze-aht4ab80-pooler.c-3.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()
bad_reports = db.query(ReportArchiveModel).filter(
    ReportArchiveModel.file_url.like("%_daily_brief_%")
).all()

print(f"Found {len(bad_reports)} bad reports.")
for r in bad_reports:
    print("Deleting:", r.file_url)
    db.delete(r)

db.commit()
db.close()
print("Done.")
