import json
from app.ai import magnitude
from app.schemas_assessment import GenerateFindingRequest, BulkGenerateRequest, GenerateStandaloneRequest, StandaloneAssessmentDraft, ExecutiveSummaryDraft, GenerateExSumRequest

def _get_memory_guidelines() -> str:
    try:
        with open('memory.txt', 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            if not lines: return ""
            return "\n".join([f"- {l}" for l in lines])
    except:
        return ""

async def generate_finding_text(req: GenerateFindingRequest) -> dict:
    sys_prompt = f"""You are an elite Security Analyst for GTBank.
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
    cleaned = cleaned.strip()
    cleaned = cleaned.strip()
        
    try:
        return json.loads(cleaned.strip())
    except:
        return {"impact": "Failed to generate.", "recommendation": "Failed to generate."}

async def generate_bulk_findings(req: BulkGenerateRequest) -> list:
    sys_prompt = f"""You are an elite Security Analyst for GTBank.
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
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:-3]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:-3]
    cleaned = cleaned.strip()
    cleaned = cleaned.strip()
        
    try:
        return json.loads(cleaned.strip())
    except:
        return []


async def generate_standalone_review(req: GenerateStandaloneRequest) -> StandaloneAssessmentDraft:
    sys_prompt = f"""You are an elite GTCO Security Assessor. 
You are performing a standalone configuration review for {req.assessment_name}.
You will be given raw notes from an auditor.
You must extract the information into a strict JSON structure representing a Standalone Assessment Draft.
Each finding MUST have a title, severity (HIGH, MID, or LOW), and lists of observations, impact, and recommendations.
DO NOT fabricate evidence. If impact or recommendations are missing, extrapolate intelligently based on standard enterprise security best practices for {req.assessment_name}.
"""
    user_prompt = f"--- RAW AUDITOR NOTES ---\n{req.raw_notes}"
    
    schema = StandaloneAssessmentDraft.model_json_schema()
    payload = {
        "contents": [{"role": "user", "parts": [{"text": sys_prompt + "\n" + user_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3,
            "responseSchema": schema
        }
    }
    
    res = await call_gemini(payload)
    if "error" in res:
        raise Exception(res["error"])
        
    try:
        raw_text = res["text"].strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
        
        data = json.loads(raw_text)
        return StandaloneAssessmentDraft(**data)
    except Exception as e:
        print("PARSE ERROR:", str(e))
        raise Exception(f"Failed to parse AI output: {str(e)}")


async def generate_executive_summary(req: GenerateExSumRequest) -> ExecutiveSummaryDraft:
    sys_prompt = """You are a C-Level Cybersecurity Consultant for Guaranty Trust Bank.
Your task is to review the complete, holistic data from an enterprise-wide technical security assessment 
(which spans multiple domains like NAC, XDR, AD, PAM, etc.) and write a high-level Executive Summary report.
This report is strictly for the Board of Directors. Do not get bogged down in deep technical specifics; roll up the findings into strategic risk statements.
You MUST output JSON matching the ExecutiveSummaryDraft schema perfectly.
Make sure the counts in table1_rows match the length of critical_highlights domains, as the template strictly enforces a 1:1 mapping there.
For table2_rows (Information Security Risk Management), you MUST OMIT the 'low' column entirely, as leadership only cares about Critical, High, and Medium.
For NIST scores, use the standard 5 functions (Identify, Protect, Detect, Respond, Recover). You may include 'Govern' if applicable, making it 6. Provide a float score out of 5.0.
"""
    
    # We dump the entire AssessmentState dict so the LLM has all findings across all tools
    raw_state_json = req.state.model_dump_json()
    
    user_prompt = f"--- HOLISTIC ASSESSMENT DATA ---\n{raw_state_json}"
    
    schema = ExecutiveSummaryDraft.model_json_schema()
    payload = {
        "contents": [{"role": "user", "parts": [{"text": sys_prompt + "\n" + user_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3,
            "responseSchema": schema
        }
    }
    
    res = await call_gemini(payload)
    if "error" in res:
        raise Exception(res["error"])
        
    try:
        raw_text = res["text"].strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
        
        import json
        data = json.loads(raw_text)
        return ExecutiveSummaryDraft(**data)
    except Exception as e:
        print("PARSE ERROR:", str(e))
        raise Exception(f"Failed to parse AI output for Executive Summary: {str(e)}")
