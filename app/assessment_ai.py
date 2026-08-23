import json
from app.ai import magnitude
from app.schemas_assessment import GenerateFindingRequest, BulkGenerateRequest

def _get_memory_guidelines() -> str:
    try:
        with open('memory.txt', 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            if not lines: return ""
            return "\n".join([f"- {l}" for l in lines])
    except:
        return ""

async def generate_finding_text(req: GenerateFindingRequest) -> dict:
    sys_prompt = f"""You are Magnitude, the elite AI Threat Intelligence Engine for GTBank.
Your task is to take a raw observation from a security tool assessment and draft two precise fields:
1. 'impact': 1-3 sentences outlining the business/security consequence. No fluff.
2. 'recommendation': 1-2 sentences in the imperative mood providing a concrete remediation action.

Tone: Match existing GTBank findings -- direct, technical, no hedging.

FEW SHOT EXAMPLES:
Title: Outdated Switches
Note: lots of switches past EOL, no refresh plan
Impact: Lack of security features and vulnerabilities.
Recommendation: A hardware refresh for outdated switches.

Title: No Backup Setup
Note: no backup server or drive observed for NAC config
Impact: Not having a backup drive risks configuration loss, prolonged downtime, manual errors, no rollback, compliance failures, and costly recovery after device failure or security incidents.
Recommendation: Implement NAC configuration backups.

USER GUIDELINES FROM LONG-TERM MEMORY:
{_get_memory_guidelines()}

Output strict JSON with two keys: "impact" and "recommendation". Do NOT wrap in markdown.
"""

    user_prompt = f"""
Tool: {req.tool_display_name}
Segment: {req.observation.segment_sector}
Severity: {req.observation.severity}
Title: {req.observation.title}
Raw Note: {req.observation.raw_note}
"""
    
    raw_response = await magnitude.generate(
        system_instruction=sys_prompt,
        prompt=user_prompt
    )
    
    # Clean JSON
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:-3]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:-3]
        
    try:
        return json.loads(cleaned.strip())
    except:
        return {"impact": "Failed to generate.", "recommendation": "Failed to generate."}

async def generate_bulk_findings(req: BulkGenerateRequest) -> list:
    sys_prompt = f"""You are Magnitude, the elite AI Threat Intelligence Engine for GTBank.
Your task is to take a messy, bulk string of raw auditor notes from a security tool assessment and parse it into individual findings.

For each distinct finding you discover in the raw notes, generate:
1. 'segment_sector': E.g. 'Policy & Access', 'Network Security', 'Configuration', 'Endpoint'. Guess based on context.
2. 'title': A short, punchy 2-4 word title.
3. 'severity': Either 'HIGH', 'MEDIUM', or 'LOW'.
4. 'impact': 1-3 sentences outlining the business/security consequence. No fluff.
5. 'recommendation': 1-2 sentences in the imperative mood providing concrete remediation.
6. 'raw_note': Extract the specific sentence or phrase from the raw notes that led to this finding.

USER GUIDELINES FROM LONG-TERM MEMORY:
{_get_memory_guidelines()}

Output strict JSON as a LIST of objects. Do NOT wrap in markdown.
Example format:
[
  {{"segment_sector": "Policy & Access", "title": "Outdated Switches", "severity": "HIGH", "impact": "Lack of security features...", "recommendation": "Hardware refresh...", "raw_note": "lots of switches past EOL"}}
]
"""

    user_prompt = f"""
Tool being audited: {req.tool_display_name}
Bulk Auditor Notes:
{req.raw_bulk_notes}
"""
    
    raw_response = await magnitude.generate(
        system_instruction=sys_prompt,
        prompt=user_prompt
    )
    
    # Clean JSON
    cleaned = raw_response.strip()
    if cleaned.startswith("`json"):
        cleaned = cleaned[7:-3]
    elif cleaned.startswith("`"):
        cleaned = cleaned[3:-3]
        
    try:
        return json.loads(cleaned.strip())
    except:
        return []
