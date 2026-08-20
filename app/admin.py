from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext

from app.db import get_db, UserModel, TeamModel
from app.schemas import TeamCreate, TeamOut
from app.auth import get_current_user, UserSession
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/admin", tags=["admin"])
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Dependency to verify admin role
async def get_admin_user(current_user: UserSession = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges"
        )
    return current_user

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: str = "user"
    status: str = "active"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

class UserOut(BaseModel):
    id: str
    username: str
    email: Optional[str]
    role: str
    status: str
    failed_login_attempts: int
    locked_out_until: Optional[datetime]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("/users", response_model=List[UserOut])
def list_users(admin_user: UserSession = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

@router.post("/users", response_model=UserOut)
def create_user(user: UserCreate, admin_user: UserSession = Depends(get_admin_user), db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(
        (UserModel.username == user.username) | 
        (UserModel.email == user.email if user.email else False)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_pwd = pwd_context.hash(user.password)
    new_user = UserModel(
        username=user.username,
        email=user.email,
        password_hash=hashed_pwd,
        role=user.role,
        status=user.status
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, updates: UserUpdate, admin_user: UserSession = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if updates.username is not None:
        user.username = updates.username
    if updates.email is not None:
        user.email = updates.email
    if updates.role is not None:
        user.role = updates.role
    if updates.status is not None:
        user.status = updates.status

    db.commit()
    db.refresh(user)
    return user

@router.post("/users/{user_id}/deactivate")
def deactivate_user(user_id: str, admin_user: UserSession = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "deactivated"
    db.commit()
    return {"success": True, "message": "User deactivated"}

@router.post("/users/{user_id}/reactivate")
def reactivate_user(user_id: str, admin_user: UserSession = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "active"
    db.commit()
    return {"success": True, "message": "User reactivated"}

@router.post("/users/{user_id}/unlock")
def unlock_user(user_id: str, admin_user: UserSession = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.locked_out_until = None
    user.failed_login_attempts = 0
    db.commit()
    return {"success": True, "message": "User unlocked"}

@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: str, admin_user: UserSession = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Just setting a temporary password for now so the admin can give it to the user.
    temp_password = "TemporaryPassword123!"
    user.password_hash = pwd_context.hash(temp_password)
    user.locked_out_until = None
    user.failed_login_attempts = 0
    db.commit()
    return {"success": True, "message": f"Password reset to: {temp_password} (Please change immediately)"}

@router.get("/teams", response_model=List[TeamOut])
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

@router.post("/teams", response_model=TeamOut)
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

@router.put("/teams/{team_id}/head")
def set_team_head(team_id: str, unit_head_id: str, db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.unit_head_id = unit_head_id
    db.commit()
    return {"status": "success"}

@router.put("/teams/{team_id}/members")
def set_team_members(team_id: str, payload: dict, db: Session = Depends(get_db)):
    user_ids = payload.get("user_ids", [])
    # First remove all users from this team
    db.query(UserModel).filter(UserModel.team_id == team_id).update({"team_id": None})
    # Then add the selected users
    if user_ids:
        db.query(UserModel).filter(UserModel.id.in_(user_ids)).update({"team_id": team_id})
    db.commit()
    return {"status": "success"}
