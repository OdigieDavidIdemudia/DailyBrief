import os
import json
import httpx
from typing import List, Dict, Optional

class MagnitudeAI:
    def __init__(self):
        self.keys_file = os.path.join(os.path.dirname(__file__), "memory", "ai_keys.json")
        self.api_keys = []
        self.current_key_idx = 0
        self.load_keys()
        
    def load_keys(self):
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, "r") as f:
                    data = json.load(f)
                if data:
                    self.api_keys = [{"key": k, "model": "gemini-3.6-flash"} if isinstance(k, str) else k for k in data]
                    return
            except Exception:
                pass
        
        keys_str = os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", ""))
        self.api_keys = [{"key": k.strip(), "model": "gemini-3.6-flash"} for k in keys_str.split(",") if k.strip()]

    def set_keys(self, keys: List[str]):
        self.api_keys = keys
        self.current_key_idx = 0
        os.makedirs(os.path.dirname(self.keys_file), exist_ok=True)
        with open(self.keys_file, "w") as f:
            json.dump(self.api_keys, f)

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

        import asyncio
        max_retries = max(3, len(self.api_keys) * 2)
        last_error = None

        for attempt in range(max_retries):
            key_info = self.get_key()
            key_val = key_info["key"] if isinstance(key_info, dict) else key_info
            model_val = key_info["model"] if isinstance(key_info, dict) else "gemini-3.6-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_val}:generateContent?key={key_val}"
            
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 429:
                        print(f"Key {self.current_key_idx} exhausted (429). Rotating...")
                        self.rotate_key()
                        await asyncio.sleep(1)
                        continue
                        
                    if response.status_code in [500, 502, 503, 504]:
                        print(f"Google API transient error {response.status_code}. Retrying...")
                        await asyncio.sleep(2)
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
                if isinstance(e, httpx.HTTPStatusError):
                    if e.response.status_code == 429:
                        self.rotate_key()
                        await asyncio.sleep(1)
                        continue
                    if e.response.status_code in [500, 502, 503, 504]:
                        last_error = str(e)
                        await asyncio.sleep(2)
                        continue
                        
                # Handle network disconnects (ReadError, ConnectError)
                if isinstance(e, httpx.RequestError):
                    print(f"Network error ({type(e).__name__}). Retrying...")
                    last_error = str(e)
                    await asyncio.sleep(2)
                    continue

                last_error = str(e)
                return {"error": f"Failed to generate AI content: {last_error}"}

        return {"error": "All API keys exhausted or retries failed. Last error: " + str(last_error)}

magnitude = MagnitudeAI()


# Define the structured schema for the Handover
handover_schema = {
    "type": "object",
    "properties": {
        "executive_summary": {
            "type": "string",
            "description": "A concise 2-sentence summary of the operational period."
        },
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
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": handover_schema
        }
    }
    
    return await magnitude._call_gemini(payload)


subsidiary_report_schema = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "object",
            "properties": {
                "overallSecurityMonitoringStatus": {"type": "string"},
                "criticalIssues": {"type": "string"},
                "escalations": {"type": "string"}
            },
            "required": ["overallSecurityMonitoringStatus", "criticalIssues", "escalations"]
        },
        "sections": {
            "type": "object",
            "properties": {
                "cortexXDR": {
                    "type": "object",
                    "properties": {
                        "brokerVMStatus": {"type": "string"},
                        "connectedAgents": {"type": "string"},
                        "disconnectedAgents": {"type": "string"},
                        "connectionLost": {"type": "string"},
                        "pendingIncidents": {"type": "string"},
                        "otherObservations": {"type": "string"},
                        "priorityActionRequired": {"type": "string"}
                    },
                    "required": ["brokerVMStatus", "connectedAgents", "disconnectedAgents", "connectionLost", "pendingIncidents", "otherObservations", "priorityActionRequired"]
                },
                "siem": {
                    "type": "object",
                    "properties": {
                        "reportingDevices": {"type": "string"},
                        "nonReportingDevices": {"type": "string"},
                        "pendingIncidents": {"type": "string"},
                        "logIngestionHealth": {"type": "string"},
                        "otherObservations": {"type": "string"},
                        "priorityActionRequired": {"type": "string"}
                    },
                    "required": ["reportingDevices", "nonReportingDevices", "pendingIncidents", "logIngestionHealth", "otherObservations", "priorityActionRequired"]
                },
                "nac": {
                    "type": "object",
                    "properties": {
                        "implementationStatus": {"type": "string"},
                        "connectedDevices": {"type": "string"},
                        "compliancePoliciesActive": {"type": "string"},
                        "nonCompliantDevices": {"type": "string"},
                        "otherObservations": {"type": "string"},
                        "priorityActionRequired": {"type": "string"}
                    },
                    "required": ["implementationStatus", "connectedDevices", "compliancePoliciesActive", "nonCompliantDevices", "otherObservations", "priorityActionRequired"]
                },
                "dlp": {
                    "type": "object",
                    "properties": {
                        "systemStatus": {"type": "string"},
                        "activePolicies": {"type": "string"},
                        "integratedAgents": {"type": "string"},
                        "policyViolations": {"type": "string"},
                        "otherObservations": {"type": "string"},
                        "priorityActionRequired": {"type": "string"}
                    },
                    "required": ["systemStatus", "activePolicies", "integratedAgents", "policyViolations", "otherObservations", "priorityActionRequired"]
                },
                "webProxy": {
                    "type": "object",
                    "properties": {
                        "systemStatus": {"type": "string"},
                        "devicesOnboarded": {"type": "string"},
                        "activeRulesPolicies": {"type": "string"},
                        "coverageIssues": {"type": "string"},
                        "otherObservations": {"type": "string"},
                        "priorityActionRequired": {"type": "string"}
                    },
                    "required": ["systemStatus", "devicesOnboarded", "activeRulesPolicies", "coverageIssues", "otherObservations", "priorityActionRequired"]
                },
                "shelt": {
                    "type": "object",
                    "properties": {
                        "totalPendingIssues": {"type": "string"},
                        "criticalFindings": {"type": "string"},
                        "currentHealthStatus": {"type": "string"},
                        "priorityActionRequired": {"type": "string"}
                    },
                    "required": ["totalPendingIssues", "criticalFindings", "currentHealthStatus", "priorityActionRequired"]
                },
                "waf": {
                    "type": "object",
                    "properties": {
                        "numberOfWebsites": {"type": "string"},
                        "mode": {"type": "string"},
                        "otherObservations": {"type": "string"},
                        "priorityActionRequired": {"type": "string"}
                    },
                    "required": ["numberOfWebsites", "mode", "otherObservations", "priorityActionRequired"]
                }
            },
            "required": ["cortexXDR", "siem", "nac", "dlp", "webProxy", "shelt", "waf"]
        },
        "keyRisksRequiringCISOAttention": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "risk": {"type": "string"},
                    "impact": {"type": "string"},
                    "owner": {"type": "string"}
                },
                "required": ["risk", "impact", "owner"]
            }
        }
    },
    "required": ["summary", "sections", "keyRisksRequiringCISOAttention"]
}

async def generate_subsidiary_report_content(logs_text: str, subsidiary_name: str) -> dict:
    prompt = f"""
    You are a highly analytical SOC Operations Manager reporting on a subsidiary's security posture.
    You are generating this report on behalf of David Idemudia Odigie (Idemudia).
    
    Review the provided raw database logs for the subsidiary '{subsidiary_name}' and synthesize a professional Subsidiary Security Status Report.
    
    
    Global Subsidiary Responsibility Matrix:
    - Ghana: XDR=Victoria, SIEM=N/R, NAC=Victoria, DLP=Victoria, WAF=Victoria, DAM=Victoria, SHELT=Victoria
    - SierraLeone: Akhere (All)
    - U.K: XDR=Idemudia, SIEM=N/R, NAC=Idemudia, DLP=N/R, WAF=N/R, DAM=Idemudia, SHELT=Idemudia
    - Cote D'Ivoire: Temitayo (All)
    - Gambia: Edidiong (All)
    - Tanzania: Moyin (All)
    - Uganda: Godwin (All)
    - Rwanda: XDR=Victoria, SIEM=N/R, NAC=Janet, DLP=Idemudia, WAF=Idemudia, DAM=Godwin, SHELT=Akhere
    - Liberia: David (Idemudia) (All)
    - Kenya: Janet (All)
    - GTPension: XDR=Idemudia, SIEM=Idemudia, NAC=N/R, DLP=N/R, WAF=N/R, DAM=N/R, SHELT=N/R
    - Senegal: XDR=Moyin, SIEM=N/R, NAC=N/R, DLP=N/R, WAF=N/R, DAM=N/R, SHELT=N/R


    CRITICAL INSTRUCTION:
    Based on the matrix above, identify if 'Idemudia' (or David) is responsible for a specific tool in '{subsidiary_name}'.
    If Idemudia IS responsible: Extract the status from the raw logs and provide detailed metrics. If no data is in logs, use 'N/A'.
    If Idemudia is NOT responsible (e.g. it is assigned to Victoria, N/R, etc.): Do NOT extract logs for this tool. Instead, for all fields in that section, explicitly state 'N/A'.
    
    Populate the summary, sections (Cortex XDR, SIEM, NAC, DLP, Web Proxy, SHELT, WAF), and the key risks requiring CISO attention.
    Output strictly as JSON matching the required schema.

    Raw Logs for Subsidiary {subsidiary_name}:
    {logs_text}
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": subsidiary_report_schema
        }
    }
    
    return await magnitude._call_gemini(payload)



downtime_schema = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "description": "Always return 'complete'"
        },
        "draft": {
            "type": "object",
            "properties": {
                "impact_summary": {"type": "string"},
                "detection_and_notification": {"type": "string"},
                "root_cause_analysis": {"type": "string"},
                "mitigation_and_recovery": {"type": "string"},
                "preventive_measures": {"type": "string"},
                "internal_communication": {"type": "string"},
                "external_communication": {"type": "string"},
                "resource": {"type": "string"},
                "start_date": {"type": "string", "description": "Extracted start date e.g. 19/08/2026"},
                "start_time": {"type": "string", "description": "Extracted start time e.g. 14:00"},
                "end_date": {"type": "string"},
                "end_time": {"type": "string"},
                "system_affected": {"type": "string"},
                "duration": {"type": "string", "description": "e.g. 2 hours"}
            },
            "required": ["impact_summary", "detection_and_notification", "root_cause_analysis", "mitigation_and_recovery", "preventive_measures", "internal_communication", "external_communication", "resource", "system_affected"]
        }
    },
    "required": ["status", "draft"]
}

import os

def _get_memory_guidelines():
    memory_path = os.path.join(os.path.dirname(__file__), 'memory', 'magnitude_guidelines.txt')
    if os.path.exists(memory_path):
        with open(memory_path, 'r') as f:
            return f.read().strip()
    return ""

async def generate_downtime_draft(brief: str, history: List[Dict[str, str]]) -> dict:
      conversation = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
      
      memory = _get_memory_guidelines()
      memory_directive = f"\nUSER GUIDELINES (LONG-TERM MEMORY):\nAlways adhere to these permanent rules:\n{memory}\n" if memory else ""
      
      prompt = f"""
        You are Magnitude, an elite Cybersecurity SOC assistant.
        
        Your objective is to synthesize raw, informal notes into a pristine, concise, and factual 'Downtime Incident Report'.
        
        CORE DIRECTIVES:
        1. Humanization & Tone: You are an executive communicator. Translate all technical incidents into clear, straightforward, and human-readable language. Avoid overly dense technical jargon. Ensure the report reads like it was written by a human manager for an executive audience.
        2. Be Extremely Concise: Keep explanations short, factual, and strictly to the point. Eliminate all fluff, filler text, and verbosity.
        3. No Hallucinations: Do NOT invent specific filenames, daemons, or fictional technical parameters. Do NOT invent a numbered list for preventive measures unless the user explicitly gave you the points.
        4. Precise Technical Synthesis: Use authoritative SOC terminology but do not add unnecessary technical details that were not implied by the brief.
        5. Auto-Fill Communication: If the user mentions escalating to a vendor or team, place that in the `internal_communication` or `external_communication` fields. If they mention resources, use the `resource` field.
        {memory_directive}
        
        You need to generate the narrative fields: Impact Summary, Detection and Notification, Root Cause Analysis, Mitigation and Recovery Actions, Preventive Measures, Internal Communication, External Communication, and Resource.
        
        Review the current conversation history below:
        {conversation}
        """
      
      payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": downtime_schema
        }
      }
      return await magnitude._call_gemini(payload)

async def refine_downtime_draft(draft: dict, corrections: str) -> dict:
      memory = _get_memory_guidelines()
      memory_directive = f"\nUSER GUIDELINES (LONG-TERM MEMORY):\nAlways adhere to these permanent rules:\n{memory}\n" if memory else ""
      
      prompt = f"""
        You are Magnitude, an elite Cybersecurity SOC assistant.
        The user has provided feedback/corrections for a Downtime Incident Report Draft.
        
        You must output a newly rewritten JSON draft that perfectly applies their feedback.
        
        CORE DIRECTIVES:
        1. Humanization & Tone: You are an executive communicator. Use clear, straightforward, and human-readable language. Avoid overly dense technical jargon.
        {memory_directive}
        
        --- USER CORRECTIONS ---
        {corrections}
        
        --- CURRENT DRAFT JSON ---
        {draft}
        """
      
      payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": downtime_schema
        }
      }
      return await magnitude._call_gemini(payload)
