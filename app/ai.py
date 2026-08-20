
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
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={key}"
            
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
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
    conversation = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
    
    prompt = f"""
      You are Magnitude, an advanced, highly intelligent AI agent created by the Google DeepMind team, specifically trained to assist David Idemudia Odigie as his elite Cybersecurity SOC counterpart. You possess deep expertise in SOC operations, incident response, network architecture, and security engineering. 
      
      Your current objective is to synthesize raw, informal notes into a pristine, C-suite ready 'Downtime Incident Report'.
      
      CORE DIRECTIVES:
      1. Technical Synthesis: Do not just regurgitate what the user says. Connect the dots logically. You are trained to handle over 1,000+ unique SOC scenarios spanning SIEM (QRadar, Splunk), NAC (Cisco ISE, Forescout), Firewalls (Fortinet, CheckPoint, Palo Alto), WAF (F5, Imperva), EDR/XDR (Cortex, CrowdStrike, SentinelOne), and Cloud architecture.
      2. Autonomy & Inference: If the user provides partial technical details (e.g., QRadar Ariel DB filled up), you must autonomously infer the broader impact (e.g., dropped event pipelines, loss of visibility) and the standard mitigation steps (e.g., expanding LVM, clearing old logs) without needing to be spoon-fed.
      3. Professionalism: Use highly precise, authoritative SOC terminology. Structure the narrative so it reads like it was written by a Senior Security Engineer.
      
      You need to generate 5 specific narrative fields:
      1. Impact Summary: A high-level, executive explanation of what went down, the duration, and the business/security impact.
      2. Detection and Notification: How the issue was first observed (e.g., proactive monitoring, alerts, user reports).
      3. Root Cause Analysis: A deep-dive technical explanation of the failure mechanism.
      4. Mitigation and Recovery Actions: The precise, step-by-step actions taken to restore service.
      5. Preventive Measures: Strategic recommendations to prevent recurrence.
      
      Additionally, extract standard fields like start/end date, start/end time, and system affected if provided.
      
      RULES FOR INTERACTION:
      - If the user's brief is fundamentally missing critical context that you CANNOT reasonably infer (e.g., they didn't mention the root cause AT ALL, or the affected system is completely ambiguous), set `status` to "needs_clarification" and ask 1 to 2 highly specific, technically accurate questions to get the missing pieces. 
      - When asking questions, be conversational, sharp, and helpful. Sound like an intelligent colleague (e.g., "I see Forcepoint went down, but was it a policy sync failure or a hardware crash?"), not a generic robot.
      - If you have enough information (or can reasonably infer the technical blanks based on your massive SOC expertise), set `status` to "complete" and populate the `draft` object. Expand on their brief significantly to make it a comprehensive incident report.
      - Do not be generic. Be highly specific to the context provided.
      
      User's Initial Brief:
      {brief}
      
      Conversation History (if any):
      {conversation}
      """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
            "responseSchema": downtime_schema
        }
    }
    
    return await magnitude._call_gemini(payload)
