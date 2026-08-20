import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute('''
    CREATE TABLE teams (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        unit_head_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL
    );
    ''')
    print('Created teams table')
except Exception as e:
    print('teams error:', e)

try:
    cur.execute('ALTER TABLE users ADD COLUMN team_id VARCHAR(36) REFERENCES teams(id) ON DELETE SET NULL;')
    print('Added team_id to users')
except Exception as e:
    print('users error:', e)

cur.close()
conn.close()
