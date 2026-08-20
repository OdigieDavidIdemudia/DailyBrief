import os
import json
import httpx
from typing import List, Dict, Optional

class MagnitudeAI:
    def __init__(self):
        keys_str = os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", ""))
        self.api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self.current_key_idx = 0

    def get_key(self):
        if not self.api_keys:
            return None
        return self.api_keys[self.current_key_idx]

    def rotate_key(self):
        if self.api_keys:
            self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)

    async def _call_gemini(self, payload: dict) -> dict:
        if not self.api_keys:
            return {"error": "GEMINI_API_KEYS not configured"}

        max_retries = max(1, len(self.api_keys))
        last_error = None

        for _ in range(max_retries):
            key = self.get_key()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 429:
                        print(f"Key {self.current_key_idx} exhausted. Rotating...")
                        self.rotate_key()
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    if "candidates" in data and len(data["candidates"]) > 0:
                        text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                        try:
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            return {"error": "Failed to parse JSON", "raw": text_content}
                    else:
                        return {"error": "Invalid response format from Gemini API."}
            except Exception as e:
                # If network error or 500, we can also rotate or just fail
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                    self.rotate_key()
                    continue
                last_error = str(e)
                return {"error": f"Failed to generate AI content: {last_error}"}

        return {"error": "All API keys exhausted or failed. Last error: " + str(last_error)}

magnitude = MagnitudeAI()

# Define schemas for the different modules
handover_schema = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "string"},
        "handover_tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "project_task": {"type": "string"},
                    "current_status": {"type": "string"},
                    "next_actions": {"type": "string"},
                    "contact_person": {"type": "string"},
                    "assignee": {"type": "string"}
                },
                "required": ["project_task", "current_status", "next_actions", "contact_person", "assignee"]
            }
        },
        "update_tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "project_task": {"type": "string"},
                    "previous_status": {"type": "string"},
                    "current_status": {"type": "string"}
                },
                "required": ["project_task", "previous_status", "current_status"]
            }
        },
        "risks_and_blockers": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["executive_summary", "handover_tasks", "update_tasks", "risks_and_blockers"]
}

async def generate_handover_content(logs_text: str, team_members: str, is_update: bool) -> dict:
    mode_text = "Handover Update (Returning to work)" if is_update else "Handover (Going on leave)"
    prompt = f"""
    You are a highly analytical SOC Operations Manager. Review the provided raw database logs and synthesize a professional {mode_text} Document.
    
    If this is a "Handover (Going on leave)", populate the `handover_tasks` array. For each task, apply the following strict mapping rules:
    - `current_status`: Must exactly match the text from the task's "Summary" field in the raw logs.
    - `contact_person`: Must exactly match the text from the task's "Mail Trail" field in the raw logs.
    - `next_actions`: Must be an empty string ("") as the user will fill this in manually.
    - `assignee`: Use the "Assignee" value provided in the raw logs, or "TBD" if none is provided.

    If this is a "Handover Update (Returning to work)", populate the `update_tasks` array by inferring the previous status and the current status based on the logs.
    
    Extract any critical blockers, risks, or dependencies into `risks_and_blockers`.
    Output strictly as JSON matching the required schema.

    Raw Logs:
    {logs_text}
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": handover_schema
        }
    }
    return await magnitude._call_gemini(payload)

# (Subsidiary report logic copied over)
subsidiary_report_schema = {
    # Schema omitted for brevity here, I will append the rest from a second write to keep it clean.
}
