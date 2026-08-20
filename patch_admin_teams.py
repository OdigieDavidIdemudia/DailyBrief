import os

def update_schemas():
    with open('app/schemas.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Add team_id to UserOut
    if 'team_id: Optional[str] = None' not in content:
        content = content.replace('unit_head_id: Optional[str] = None', 'unit_head_id: Optional[str] = None\n    team_id: Optional[str] = None')

    # Add Team schemas
    if 'class TeamCreate' not in content:
        content += '''
class TeamCreate(BaseModel):
    name: str
    unit_head_id: Optional[str] = None

class TeamOut(BaseModel):
    id: str
    name: str
    unit_head_id: Optional[str] = None
    member_count: int = 0
'''
    with open('app/schemas.py', 'w', encoding='utf-8') as f:
        f.write(content)

def update_admin():
    with open('app/admin.py', 'r', encoding='utf-8') as f:
        content = f.read()

    if 'from app.db import UserModel, TeamModel' not in content:
        content = content.replace('from app.db import UserModel', 'from app.db import UserModel, TeamModel')
    
    if 'from app.schemas import UserOut, UserCreate, UserUpdate' in content:
        content = content.replace('from app.schemas import UserOut, UserCreate, UserUpdate', 'from app.schemas import UserOut, UserCreate, UserUpdate, TeamCreate, TeamOut')

    if '@admin_router.get("/teams"' not in content:
        endpoints = '''
@admin_router.get("/teams", response_model=List[TeamOut])
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(TeamModel).all()
    result = []
    for t in teams:
        member_count = db.query(UserModel).filter(UserModel.team_id == t.id).count()
        result.append({
            "id": t.id,
            "name": t.name,
            "unit_head_id": t.unit_head_id,
            "member_count": member_count
        })
    return result

@admin_router.post("/teams", response_model=TeamOut)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    new_team = TeamModel(name=team.name, unit_head_id=team.unit_head_id)
    db.add(new_team)
    db.commit()
    return {
        "id": new_team.id,
        "name": new_team.name,
        "unit_head_id": new_team.unit_head_id,
        "member_count": 0
    }

@admin_router.put("/teams/{team_id}/head")
def set_team_head(team_id: str, unit_head_id: str, db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.unit_head_id = unit_head_id
    db.commit()
    return {"status": "success"}

@admin_router.put("/teams/{team_id}/members")
def set_team_members(team_id: str, payload: dict, db: Session = Depends(get_db)):
    user_ids = payload.get("user_ids", [])
    # First remove all users from this team
    db.query(UserModel).filter(UserModel.team_id == team_id).update({"team_id": None})
    # Then add the selected users
    if user_ids:
        db.query(UserModel).filter(UserModel.id.in_(user_ids)).update({"team_id": team_id})
    db.commit()
    return {"status": "success"}
'''
        content += endpoints

    with open('app/admin.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_schemas()
    update_admin()
    print('Patched schemas.py and admin.py')
