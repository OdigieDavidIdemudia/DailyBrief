import asyncio
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "postgresql://neondb_owner:npg_ZQ80CFlOtPjp@ep-patient-breeze-aht4ab80-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.db import DailyLogModel, UserModel, UserSettingsModel

async def debug():
    db = SessionLocal()
    uid = 'beea6451-21be-491b-9183-476909a49068'

    # Get today's date
    from app.main import get_wat_date_string
    today_str = get_wat_date_string()
    print(f"Today: {today_str}")

    user = db.query(UserModel).filter(UserModel.id == uid).first()
    print(f"User: {user.username}")

    logs = db.query(DailyLogModel).filter(
        DailyLogModel.user_id == uid,
        DailyLogModel.date == today_str
    ).all()
    print(f"Total logs today: {len(logs)}")

    for i, log in enumerate(logs):
        bp = log.blueprint
        print(f"\n  Log #{i+1}:")
        print(f"    Title:          {bp.title if bp else 'DELETED'}")
        print(f"    Status:         {log.status}")
        print(f"    Summary:        '{log.summary}'")
        print(f"    notify_enabled: {log.notify_enabled}")

    settings = db.query(UserSettingsModel).filter(UserSettingsModel.user_id == uid).first()
    print(f"\nTelegram Settings:")
    print(f"  enabled:   {settings.telegram_enabled}")
    print(f"  bot_token: {'SET' if settings.telegram_bot_token else 'MISSING'}")
    print(f"  chat_id:   {'SET' if settings.telegram_chat_id else 'MISSING'}")

    # Build evening message
    date_parts = today_str.split('-')
    display_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
    formatted_name = " ".join(p.capitalize() for p in user.username.split("."))

    lines = [f"Daily Plan for {display_date} - {formatted_name}\n"]
    for log in logs:
        if not log.notify_enabled:
            print(f"  SKIPPING '{log.blueprint.title if log.blueprint else 'DELETED'}' — notify_enabled is False")
            continue
        bp = log.blueprint
        title = bp.title if bp else "Deleted Task"
        status_text = log.summary if log.summary else (log.status if log.status else "Pending")
        lines.append(f"- {title}\n   > {status_text}\n")

    message_text = "\n".join(lines)
    print(f"\n===== MESSAGE THAT WILL BE SENT =====")
    print(repr(message_text))
    print(f"=====================================\n")

    # Actually send it
    tg_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(tg_url, json={"chat_id": settings.telegram_chat_id, "text": message_text})
        print(f"Telegram HTTP Status: {resp.status_code}")
        print(f"Telegram Response: {resp.text}")

    db.close()

if __name__ == "__main__":
    asyncio.run(debug())
