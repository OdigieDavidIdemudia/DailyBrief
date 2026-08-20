import sys
import os

schema = '''
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
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured"}
        
    prompt = f"""
    You are a highly analytical SOC Operations Manager reporting on a subsidiary's security posture.
    Review the provided raw database logs for the subsidiary '{subsidiary_name}' and synthesize a professional Subsidiary Security Status Report.
    
    Populate the summary, sections (Cortex XDR, SIEM, NAC, DLP, Web Proxy, SHELT, WAF), and the key risks requiring CISO attention.
    If information is missing for a specific metric in the logs, use 'N/A' or a brief statement indicating no data is available.
    Output strictly as JSON matching the required schema.

    Raw Logs for Subsidiary {subsidiary_name}:
    {logs_text}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
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
    
    try:
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
        return {"error": f"Failed to generate AI content: {str(e)}"}
'''

with open('app/ai.py', 'a', encoding='utf-8') as f:
    f.write('\n' + schema + '\n')
print('Appended successfully')
