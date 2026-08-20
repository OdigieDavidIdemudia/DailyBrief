from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext
import uuid

from app.db import get_db, UserModel, BlueprintModel, DailyLogModel, TeamModel
from app.auth import get_current_user, UserSession
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/unit", tags=["unit_head"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Dependency to verify unit_head role
async def get_unit_head_user(current_user: UserSession = Depends(get_current_user)):
    if current_user.role != 'unit_head':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires unit head privileges"
        )
    return current_user

class TeamMemberCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class TeamMemberOut(BaseModel):
    id: str
    username: str
    email: Optional[str]
    role: str
    status: str
    team_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class UnitBlueprintCreate(BaseModel):
    title: str
    category: str
    priority: str
    assigned_to: str # user_id of the team member

class UnitBlueprintOut(BaseModel):
    id: str
    user_id: str # The team member it's assigned to
    assigned_by: str # The unit head
    title: str
    category: str
    priority: str

    class Config:
        from_attributes = True

class TeamInfoOut(BaseModel):
    id: str
    name: str

@router.get("/my_team", response_model=TeamInfoOut)
def get_my_team(unit_head: UserSession = Depends(get_unit_head_user), db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.unit_head_id == unit_head.id).first()
    if not team:
        raise HTTPException(status_code=404, detail="No team assigned")
    return {"id": team.id, "name": team.name}

@router.get("/members", response_model=List[TeamMemberOut])
def list_team_members(unit_head: UserSession = Depends(get_unit_head_user), db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.unit_head_id == unit_head.id).first()
    if not team:
        return []
    members = db.query(UserModel).filter(UserModel.team_id == team.id).all()
    return members

@router.post("/members", response_model=TeamMemberOut)
def create_team_member(member: TeamMemberCreate, unit_head: UserSession = Depends(get_unit_head_user), db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.unit_head_id == unit_head.id).first()
    if not team:
        raise HTTPException(status_code=400, detail="You are not assigned to a team to add members to.")

    existing = db.query(UserModel).filter(
        (UserModel.username == member.username) | 
        (UserModel.email == member.email if member.email else False)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_pwd = pwd_context.hash(member.password)
    new_user = UserModel(
        username=member.username,
        email=member.email,
        password_hash=hashed_pwd,
        role="user",
        status="active",
        team_id=team.id,
        force_password_change=True # Force password change on first login
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/tasks", response_model=List[UnitBlueprintOut])
def list_team_tasks(unit_head: UserSession = Depends(get_unit_head_user), db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.unit_head_id == unit_head.id).first()
    if not team:
        return []
    # get tasks for members of this team, or tasks directly assigned by this unit head
    # we'll stick to tasks assigned by this unit head
    tasks = db.query(BlueprintModel).filter(BlueprintModel.assigned_by == unit_head.id).all()
    return tasks

@router.post("/tasks", response_model=UnitBlueprintOut)
def assign_task(task: UnitBlueprintCreate, unit_head: UserSession = Depends(get_unit_head_user), db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.unit_head_id == unit_head.id).first()
    if not team:
        raise HTTPException(status_code=400, detail="You must be assigned to a team to assign tasks.")

    # Verify the user is a team member of this unit head's team
    member = db.query(UserModel).filter(UserModel.id == task.assigned_to, UserModel.team_id == team.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found in your team")

    new_task = BlueprintModel(
        user_id=member.id,
        title=task.title,
        category=task.category,
        priority=task.priority,
        assigned_by=unit_head.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
