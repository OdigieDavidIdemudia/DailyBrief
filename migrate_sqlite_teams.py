import sqlite3

conn = sqlite3.connect('tholder.db')
cur = conn.cursor()

try:
    cur.execute('''
    CREATE TABLE teams (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        unit_head_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL
    );
    ''')
    print('Created teams table in SQLite')
except Exception as e:
    print('teams error:', e)

try:
    cur.execute('ALTER TABLE users ADD COLUMN team_id VARCHAR(36) REFERENCES teams(id) ON DELETE SET NULL;')
    print('Added team_id to users in SQLite')
except Exception as e:
    print('users error:', e)

conn.commit()
conn.close()
