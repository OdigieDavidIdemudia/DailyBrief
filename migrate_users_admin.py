import sqlite3
import os
from datetime import datetime

def migrate():
    db_path = 'tholder.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        # Columns to add
        new_cols = [
            ("email", "VARCHAR(255)"),
            ("role", "VARCHAR(50) DEFAULT 'user' NOT NULL"),
            ("status", "VARCHAR(50) DEFAULT 'active' NOT NULL"),
            ("failed_login_attempts", "INTEGER DEFAULT 0 NOT NULL"),
            ("locked_out_until", "DATETIME"),
            ("last_login_at", "DATETIME"),
            ("created_at", "DATETIME"),
            ("updated_at", "DATETIME"),
        ]

        for col_name, col_type in new_cols:
            if col_name not in columns:
                print(f"Adding column {col_name}...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                
                # If created_at or updated_at, set default to now for existing rows
                if col_name in ("created_at", "updated_at"):
                    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
                    cursor.execute(f"UPDATE users SET {col_name} = ?", (now_str,))
        
        # Grant admin role to the 'admin' user
        print("Setting 'admin' role for admin user...")
        cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
        
        conn.commit()
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
