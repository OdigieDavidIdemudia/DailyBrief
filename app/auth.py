import os
import json
import base64
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, status
try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

def is_supabase_enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)

# Helper to get supabase client
def get_supabase_client() -> Client:
    if not is_supabase_enabled():
        raise RuntimeError("Supabase credentials not configured.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# User Session Structure
class UserSession:
    def __init__(self, user_id: str, email: str, role: str = 'user', status: str = 'active', force_password_change: bool = False):
        self.id = user_id
        self.email = email
        self.role = role
        self.status = status
        self.force_password_change = force_password_change

    def to_dict(self):
        return {"id": self.id, "email": self.email, "role": self.role, "status": self.status, "force_password_change": self.force_password_change}

# Authenticate user from Request cookie
async def get_current_user(request: Request) -> UserSession:
    token = request.cookies.get("tholder_session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # 1. Supabase Auth
    if is_supabase_enabled():
        try:
            supabase = get_supabase_client()
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                return UserSession(
                    user_id=user_response.user.id,
                    email=user_response.user.email or ""
                )
        except Exception as e:
            print(f"Supabase auth check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Supabase session"
            )
    
    # 2. Local Fallback / Mock Auth
    if token.startswith("mock:"):
        try:
            encoded = token.split(":", 1)[1]
            decoded = base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
            if "|" in decoded:
                user_id, email = decoded.split("|", 1)
            else:
                email = decoded
                user_id = f"mock-user-{email.replace('@', '-').replace('.', '-')}"
            
            # Revalidate against database for status/role
            from app.db import SessionLocal, UserModel
            db = SessionLocal()
            try:
                user = db.query(UserModel).filter(UserModel.id == user_id).first()
                if not user:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
                if user.status == 'deactivated':
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")
                if user.locked_out_until and user.locked_out_until > datetime.utcnow():
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is temporarily locked")
                
                return UserSession(user_id=user.id, email=user.email or user.username, role=user.role, status=user.status, force_password_change=user.force_password_change)
            finally:
                db.close()
                
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid mock session"
            )
            
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication session"
    )

# Sign in handler
async def sign_in_user(email: str, password: str = None) -> dict:
    if is_supabase_enabled():
        try:
            supabase = get_supabase_client()
            if password:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            else:
                response = supabase.auth.sign_in_with_otp({"email": email})
                return {"success": True, "message": "Magic link sent to your email", "supabase_otp": True}
            
            if response.session:
                return {
                    "success": True,
                    "session_token": response.session.access_token,
                    "user": {"id": response.user.id, "email": response.user.email}
                }
            raise Exception("Session creation failed")
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        # Local SQLite login
        if not email or not password:
            return {"success": False, "error": "Username and password are required"}
        
        from app.db import SessionLocal, UserModel
        from passlib.context import CryptContext
        from sqlalchemy import or_
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        
        db = SessionLocal()
        try:
            # Allow login with email or username
            user = db.query(UserModel).filter(
                or_(UserModel.username == email, UserModel.email == email)
            ).first()
            
            if not user:
                return {"success": False, "error": "Invalid username or password"}
                
            if user.status == 'deactivated':
                return {"success": False, "error": "Account is deactivated."}
                
            now = datetime.utcnow()
            if user.locked_out_until and user.locked_out_until > now:
                mins_left = int((user.locked_out_until - now).total_seconds() / 60)
                return {"success": False, "error": f"Account locked. Try again in {mins_left} minutes or contact an admin."}
                
            if not pwd_context.verify(password, user.password_hash):
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_out_until = now + timedelta(minutes=15)
                db.commit()
                return {"success": False, "error": "Invalid username or password"}
                
            # Success
            user.failed_login_attempts = 0
            user.locked_out_until = None
            user.last_login_at = now
            db.commit()
                
            token_payload = f"{user.id}|{email}"
            encoded_payload = base64.b64encode(token_payload.encode("utf-8")).decode("utf-8")
            session_token = f"mock:{encoded_payload}"
            
            return {
                "success": True,
                "session_token": session_token,
                "user": {"id": user.id, "email": user.email or user.username, "role": user.role, "force_password_change": user.force_password_change}
            }
        finally:
            db.close()
