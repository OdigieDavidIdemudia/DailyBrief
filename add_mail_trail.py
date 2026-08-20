from sqlalchemy import create_engine, text

POSTGRES_URL = "postgresql://neondb_owner:npg_ZQ80CFlOtPjp@ep-patient-breeze-aht4ab80-pooler.c-3.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"

engine = create_engine(POSTGRES_URL)

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS mail_trail TEXT DEFAULT '';"))
    conn.commit()

print("Successfully added mail_trail column to daily_logs table.")
