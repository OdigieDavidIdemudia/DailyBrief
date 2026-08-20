import os
import re

with open("app/ai.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add Magnitude class at the top
magnitude_class = """
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
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                    self.rotate_key()
                    continue
                last_error = str(e)
                return {"error": f"Failed to generate AI content: {last_error}"}

        return {"error": "All API keys exhausted or failed. Last error: " + str(last_error)}

magnitude = MagnitudeAI()

"""

# Replace the imports
content = re.sub(r"import os\nimport json\nimport httpx\nfrom typing import List, Dict, Optional\n", magnitude_class, content)

# Replace the network calls in handover and subsidiary
old_network_call = """    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from Gemini response
            if "candidates" in data and len(data["candidates"]) > 0:
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content)
            else:
                return {"error": "Invalid response format from Gemini API."}
    except Exception as e:
        return {"error": f"Failed to generate AI content: {str(e)}"}"""

old_network_call_sub = """    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if "candidates" in data and len(data["candidates"]) > 0:
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content)
            else:
                return {"error": "Invalid response format from Gemini API."}
    except Exception as e:
        return {"error": f"Failed to generate AI content: {str(e)}"}"""

content = content.replace(old_network_call, "    return await magnitude._call_gemini(payload)")
content = content.replace(old_network_call_sub, "    return await magnitude._call_gemini(payload)")

# Clean up the api key fetching logic
content = re.sub(r'    api_key = os\.environ\.get\("GEMINI_API_KEY"\)\n    if not api_key:\n        return {"error": "GEMINI_API_KEY not configured"}\n        \n', '', content)
content = re.sub(r'    url = f"https://generativelanguage\.googleapis\.com/v1beta/models/gemini-2\.5-flash:generateContent\?key={api_key}"\n    \n', '', content)

# Append Downtime Report AI Logic
downtime_ai = """

downtime_schema = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Must be either 'needs_clarification' or 'complete'"
        },
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Array of 1-3 clarifying questions if status is 'needs_clarification'"
        },
        "draft": {
            "type": "object",
            "properties": {
                "impact_summary": {"type": "string"},
                "detection_and_notification": {"type": "string"},
                "root_cause_analysis": {"type": "string"},
                "mitigation_and_recovery": {"type": "string"},
                "preventive_measures": {"type": "string"},
                "start_date": {"type": "string", "description": "Extracted start date e.g. 19/08/2026"},
                "start_time": {"type": "string", "description": "Extracted start time e.g. 9:00 AM"},
                "end_date": {"type": "string"},
                "end_time": {"type": "string"},
                "system_affected": {"type": "string"}
            },
            "required": ["impact_summary", "detection_and_notification", "root_cause_analysis", "mitigation_and_recovery", "preventive_measures"]
        }
    },
    "required": ["status"]
}

async def generate_downtime_draft(brief: str, history: List[Dict[str, str]]) -> dict:
    conversation = "\\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
    
    prompt = f\"\"\"
    You are Magnitude, an expert Cybersecurity SOC Assistant. Your goal is to help the user draft a professional 'Downtime Incident Report'.
    
    The user has provided a brief describing a downtime incident. 
    You need to generate 5 specific narrative fields:
    1. Impact Summary
    2. Detection and Notification
    3. Root Cause Analysis
    4. Mitigation and Recovery Actions
    5. Preventive Measures
    
    Additionally, extract standard fields like start/end date, start/end time, and system affected if provided.
    
    RULES:
    - If the user's brief is too vague or lacks critical information (e.g., they didn't mention the root cause, or what actions were taken to fix it), set `status` to "needs_clarification" and provide 1 to 3 specific `questions` to ask the user.
    - If you have enough information to write a sensible draft for ALL 5 fields, set `status` to "complete" and populate the `draft` object with professional, formal SOC terminology. Expand on their brief appropriately.
    - DO NOT make up random root causes or actions. If it's missing, ask!
    - Only ask a maximum of 3 questions at a time.
    
    User's Initial Brief:
    {brief}
    
    Conversation History (if any):
    {conversation}
    \"\"\"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
            "responseSchema": downtime_schema
        }
    }
    
    return await magnitude._call_gemini(payload)
"""

content += downtime_ai

with open("app/ai.py", "w", encoding="utf-8") as f:
    f.write(content)
