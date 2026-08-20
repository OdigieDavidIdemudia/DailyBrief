import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_ZQ80CFlOtPjp@ep-patient-breeze-aht4ab80-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

try:
    print("Connecting to remote database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'task_blueprints';
    """)
    columns = [row[0] for row in cursor.fetchall()]
    print(f"Existing columns in task_blueprints: {columns}")

    if 'assigned_by' not in columns:
        print("Adding assigned_by column...")
        cursor.execute("ALTER TABLE task_blueprints ADD COLUMN assigned_by VARCHAR(255)")
        print("Added.")

    conn.commit()
    print("Remote migration successful.")
except Exception as e:
    print(f"Migration failed: {e}")
finally:
    if 'conn' in locals():
        conn.close()
