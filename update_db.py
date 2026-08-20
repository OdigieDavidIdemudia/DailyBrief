with open('app/db.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add TeamModel
team_model = """
# 6. Team Model
class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    unit_head_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
"""

# insert it before init_db()
init_db_idx = content.find('# Initialize database tables')
content = content[:init_db_idx] + team_model + '\n' + content[init_db_idx:]

# Add team_id to UserModel
target = 'force_password_change = Column(Boolean, nullable=False, default=False)'
replacement = 'force_password_change = Column(Boolean, nullable=False, default=False)\n    team_id = Column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)'
content = content.replace(target, replacement)

with open('app/db.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated db.py with TeamModel and team_id')
