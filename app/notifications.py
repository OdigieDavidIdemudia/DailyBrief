import urllib.request
import urllib.parse
import json
from sqlalchemy.orm import Session
from app.db import UserSettingsModel

def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    if not bot_token or not chat_id:
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            return res_data.get("ok", False)
    except Exception as e:
        print(f"Telegram notification failed: {e}")
        return False

def notify_user_event(user_id: str, db: Session, message: str) -> bool:
    settings = db.query(UserSettingsModel).filter(
        UserSettingsModel.user_id == user_id
    ).first()
    
    if not settings or not settings.telegram_enabled:
        return False
        
    return send_telegram_message(
        settings.telegram_bot_token,
        settings.telegram_chat_id,
        message
    )
