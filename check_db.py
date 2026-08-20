import os
import psycopg2

URL = "postgres://default:Yt6BhwS1pOPK@ep-young-snow-a45g08at-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"

try:
    conn = psycopg2.connect(URL)
    cur = conn.cursor()

    cur.execute("SELECT id, username, team_id, unit_head_id FROM users;")
    users = cur.fetchall()
    print("USERS:")
    for u in users:
        print(f"ID: {u[0]}, Username: {u[1]}, Team: {u[2]}, UnitHead: {u[3]}")

    cur.execute("SELECT id, title, user_id, assigned_by FROM task_blueprints;")
    blueprints = cur.fetchall()
    print("\nBLUEPRINTS:")
    for b in blueprints:
        print(f"ID: {b[0]}, Title: {b[1]}, User: {b[2]}, AssignedBy: {b[3]}")

    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
