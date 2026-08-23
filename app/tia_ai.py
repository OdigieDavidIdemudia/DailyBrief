import os
import json
from app.ai import magnitude
from app.schemas_tia import TIAGenerateRequest, TIAStructuredOutput
from bs4 import BeautifulSoup
import requests
import asyncio
from datetime import datetime
import uuid

def _get_memory_guidelines() -> str:
    # Memory for user corrections
    memory_path = os.path.join(os.path.dirname(__file__), "memory", "magnitude_guidelines.txt")
    if os.path.exists(memory_path):
        with open(memory_path, "r") as f:
            content = f.read().strip()
            if content:
                return f"\nUSER PREFERENCES / MEMORY (APPLY THESE STRICTLY):\n{content}\n"
    return ""

async def _fetch_url_content(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract meaningful text
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ')
        return ' '.join(text.split())[:15000] # Limit to avoid huge context sizes
    except Exception as e:
        return f"[Failed to fetch {url}: {e}]"


tia_schema = {
    "type": "object",
    "properties": {
        "report_id": {"type": "string"},
        "title": {"type": "string"},
        "date": {"type": "string"},
        "prepared_by": {"type": "string"},
        "reviewed_by": {"type": "string"},
        "org_unit": {"type": "string"},
        "threat_categories": {"type": "array", "items": {"type": "string"}},
        "cve": {"type": "array", "items": {"type": "string"}},
        "how": {"type": "string"},
        "malware_score": {"type": "integer", "nullable": True},
        "severity_assessed": {"type": "string"},
        "executive_summary": {"type": "string"},
        "threat_landscape": {"type": "string"},
        "detection_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "logic": {"type": "string"},
                    "notes": {"type": "string"}
                },
                "required": ["target", "logic"]
            }
        },
        "iocs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "value": {"type": "string"},
                    "context": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["confirmed", "high", "medium", "low"]},
                    "provenance": {"type": "string", "enum": ["user_supplied", "magnitude_research"]},
                    "source_url": {"type": "string"}
                },
                "required": ["type", "value", "confidence", "provenance"]
            }
        },
        "impact_assessment": {"type": "string"},
        "affected_assets": {"type": "array", "items": {"type": "string"}},
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "sub_items": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["action"]
            }
        },
        "references": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["source", "title", "url"]
            }
        },
        "appendices": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "title", "executive_summary", "threat_landscape", "iocs", "threat_categories", 
        "severity_assessed", "impact_assessment", "recommendations", "references"
    ]
}


tia_schema = {
    "type": "object",
    "properties": {
        "report_id": {"type": "string"},
        "title": {"type": "string"},
        "date": {"type": "string"},
        "prepared_by": {"type": "string"},
        "reviewed_by": {"type": "string"},
        "org_unit": {"type": "string"},
        "threat_categories": {"type": "array", "items": {"type": "string"}},
        "cve": {"type": "array", "items": {"type": "string"}},
        "how": {"type": "string"},
        "malware_score": {"type": "integer"},
        "severity_assessed": {"type": "string"},
        "executive_summary": {"type": "string"},
        "threat_landscape": {"type": "string"},
        "detection_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "logic": {"type": "string"},
                    "notes": {"type": "string"}
                },
                "required": ["target", "logic"]
            }
        },
        "iocs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "value": {"type": "string"},
                    "context": {"type": "string"},
                    "confidence": {"type": "string"},
                    "provenance": {"type": "string"},
                    "source_url": {"type": "string"}
                },
                "required": ["type", "value", "confidence", "provenance"]
            }
        },
        "impact_assessment": {"type": "string"},
        "affected_assets": {"type": "array", "items": {"type": "string"}},
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "sub_items": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["action"]
            }
        },
        "references": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["source", "title", "url"]
            }
        },
        "appendices": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "title", "executive_summary", "threat_landscape", "iocs", "threat_categories", 
        "severity_assessed", "impact_assessment", "recommendations", "references"
    ]
}

async def generate_tia_draft(req: TIAGenerateRequest) -> dict:
    # Stage 1-2: Gathering context (Web Fetching for source_urls)
    research_context = ""
    if req.threat.source_urls:
        research_context += "\n--- FETCHED SOURCE CONTENT ---\n"
        for url in req.threat.source_urls:
            content = await _fetch_url_content(url)
            research_context += f"\nSOURCE: {url}\nCONTENT:\n{content}\n"
            
    # Stage 3-5: Engine generation
    sys_prompt = f"""You are Magnitude, the elite AI Threat Intelligence Engine for GTCO.
You are tasked with analyzing a threat and producing a highly structured Threat Intelligence Advisory.
Follow the 7-stage processing pipeline strictly. 
Particularly for IOCs: Do NOT fabricate IOCs. If auto_enrich_iocs is false or you cannot find reliable IOCs, output 'No indicators of compromise...'.
Every derived IOC must be tagged as 'magnitude_research' and explicitly cited in references.
User-supplied IOCs must be tagged as 'user_supplied'.
{_get_memory_guidelines()}
"""
    
    user_prompt = f"""
--- USER THREAT INPUT ---
{req.threat.model_dump_json(indent=2)}

--- USER SUPPLIED IOCs ---
{("Raw text provided by user, parse these into standard IOC categories (ip, domain, hash, etc.) and mark them as 'user_supplied' with confidence 'confirmed':\\n" + req.raw_iocs) if req.raw_iocs else (json.dumps([ioc.model_dump() for ioc in req.iocs], indent=2) if req.iocs else "None")}

--- GENERATION OPTIONS ---
{req.generation_options.model_dump_json(indent=2)}

{research_context}

Analyze the input, extract all relevant facts, research gaps based on the provided sources (or general knowledge of the threat), and generate the complete structured JSON representation of the Threat Intelligence Advisory.
Ensure output EXACTLY matches the TIAStructuredOutput schema.
"""

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": sys_prompt + "\n" + user_prompt}]}
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
            "responseSchema": tia_schema,
            "responseSchema": tia_schema
        }
    }
    
    draft = await magnitude._call_gemini(payload)
    if "error" in draft:
        return draft
        
    try:
        # Post-processing: set report_id, dates if missing
        if not draft.get('report_id'):
            date_str = datetime.now().strftime("%y%m%d")
            seq = str(uuid.uuid4().int)[:3]
            prefix = req.generation_options.report_id_prefix
            draft['report_id'] = f"{prefix}({date_str}/{seq})"
            
        if not draft.get('date'):
            draft['date'] = datetime.now().strftime("%d %B %Y")
            
        if not draft.get('prepared_by'):
            draft['prepared_by'] = req.generation_options.author
            
        if not draft.get('reviewed_by'):
            draft['reviewed_by'] = req.generation_options.reviewer
            
        if not draft.get('org_unit'):
            draft['org_unit'] = req.generation_options.org_unit
            
        return draft
    except Exception as e:
        return {"error": f"Failed to post-process model output: {str(e)}"}

async def refine_tia_draft(draft: dict, corrections: str) -> dict:
    sys_prompt = f"""You are Magnitude. Refine the provided Threat Intelligence Advisory draft based on the user's specific corrections.
Maintain all existing valid data. Only change what is requested or implicitly required by the correction.
Ensure output remains exactly in the TIAStructuredOutput JSON format.
{_get_memory_guidelines()}
"""
    user_prompt = f"--- CURRENT DRAFT ---\n{json.dumps(draft, indent=2)}\n\n--- CORRECTIONS ---\n{corrections}"
    
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": sys_prompt + "\n" + user_prompt}]}
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
            "responseSchema": tia_schema,
            "responseSchema": tia_schema
        }
    }
    
    return await magnitude._call_gemini(payload)
