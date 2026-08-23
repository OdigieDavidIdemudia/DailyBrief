from app.ai import magnitude

health_check_schema = {
    "type": "object",
    "properties": {
        "report_title": {"type": "string"},
        "report_date": {"type": "string"},
        "prepared_by": {"type": "string"},
        "reviewed_by": {"type": "string"},
        "organization_unit": {"type": "string"},
        "introduction": {"type": "string", "description": "1-3 sentence summary referencing vendor name, system/platform, and period."},
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer"},
                    "title": {"type": "string"},
                    "observation": {"type": "string"},
                    "remediation_label": {"type": "string", "enum": ["Remediation Action", "Remediation / Test Outcome"]},
                    "remediation_text": {"type": "string"},
                    "status": {"type": "string", "enum": ["Closed", "Ongoing", "Pending"]}
                },
                "required": ["number", "title", "observation", "remediation_label", "remediation_text", "status"]
            }
        },
        "conclusion": {"type": "string", "description": "2-4 sentence summary reflecting closed vs ongoing ratio."},
        "appendices": {
            "type": "array",
            "items": {"type": "string"}
        },
        "references": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": [
        "report_title", "report_date", "prepared_by", "reviewed_by", 
        "organization_unit", "introduction", "observations", 
        "conclusion", "appendices", "references"
    ]
}

import os

def _get_memory_guidelines():
    memory_path = os.path.join(os.path.dirname(__file__), 'memory', 'magnitude_guidelines.txt')
    if os.path.exists(memory_path):
        with open(memory_path, 'r') as f:
            return f.read().strip()
    return ""

async def generate_health_check_model(vendor_text: str, user_notes: str, prepared_by: str, reviewed_by: str) -> dict:
    memory = _get_memory_guidelines()
    memory_directive = f"\nUSER GUIDELINES (LONG-TERM MEMORY):\nAlways adhere to these permanent rules:\n{memory}\n" if memory else ""
    
    prompt = f"""
    You are Magnitude, an elite Cybersecurity SOC assistant.
    
    Your objective is to read a raw Vendor Health Check Report and the user's freeform Remediation Notes, and generate a highly structured Document Model for a final corporate report.
    
    CORE DIRECTIVES:
    1. Humanization & Tone: You are an executive communicator. Translate all technical findings into clear, straightforward, and human-readable language. Avoid overly dense technical jargon. Ensure the report reads like it was written by a human manager for an executive audience.
    2. Extract Findings: Extract all legitimate findings/observations from the Vendor text. Prioritize explicit 'Actionable Points' or 'Observations' sections. Ignore raw terminal dumps or generic preamble fluff. Summarize each finding concisely.
    3. Map to Actions: Parse the User's Remediation Notes. For each extracted finding, map it to the corresponding user action (if mentioned). 
       - If mapped and the user indicates completion, set status to 'Closed'.
       - If mapped but ongoing, set status to 'Ongoing'.
       - If the finding is completely unmentioned by the user, set status to 'Pending' and use a neutral placeholder for `remediation_text` (e.g. 'Pending review'). NEVER invent an action that the user did not state.
    4. Structural Defaults: 
       - `organization_unit` should be 'Security Monitoring and Threat Intelligence'.
       - `appendices` usually ['None'].
       - `references` should mention the vendor name and report name.
       - Use 'Remediation Action' or 'Remediation / Test Outcome' for the `remediation_label`.
       {memory_directive}
       
    Identity Override:
    Ensure the `prepared_by` field uses: "{prepared_by}" and `reviewed_by` uses: "{reviewed_by}".
    Generate a dynamic `report_title` based on the vendor report details.
    
    --- VENDOR HEALTH CHECK TEXT ---
    {vendor_text[:30000]}
    
    --- USER REMEDIATION NOTES ---
    {user_notes}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": health_check_schema
        }
    }
    
    return await magnitude._call_gemini(payload)

async def refine_health_check_model(draft: dict, corrections: str) -> dict:
    memory = _get_memory_guidelines()
    memory_directive = f"\nUSER GUIDELINES (LONG-TERM MEMORY):\nAlways adhere to these permanent rules:\n{memory}\n" if memory else ""
    
    prompt = f"""
    You are Magnitude, an elite Cybersecurity SOC assistant.
    The user has provided feedback/corrections for a Health Check Draft Report.
    
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
            "responseSchema": health_check_schema
        }
    }
    return await magnitude._call_gemini(payload)
