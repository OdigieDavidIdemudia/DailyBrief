import json, os
from datetime import datetime
from app.ai import magnitude
from app.schemas_ks import KSGenerateRequest

def _get_spec() -> str:
    path = os.path.join(os.path.dirname(__file__), "ks_slide_spec.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""

ks_schema = {
    "type": "object",
    "properties": {
        "presentation_title": {"type": "string"},
        "target_audience":    {"type": "string"},
        "date":               {"type": "string"},
        "author":             {"type": "string"},
        "accent_primary":     {"type": "string", "description": "Hex color chosen for its semantic meaning e.g. 8FA8FF for info, E8998C for risk"},
        "accent_secondary":   {"type": "string", "description": "Second accent hex color or empty string"},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slide_number":  {"type": "integer"},
                    "content_type":  {"type": "string", "description": "definition|comparison|process|threat_chain|risk_control|architecture|metrics|case_study|before_after|list|timeline|summary"},
                    "layout_type":   {"type": "string", "description": "horizontal_process|two_column_comparison|definition_plus_example|attack_chain|risk_control_mapping|metric_dashboard|case_study|structured_list|before_after|timeline|layered_model"},
                    "eyebrow":       {"type": "string", "description": "OPTIONAL short uppercase label e.g. THREAT LANDSCAPE"},
                    "title":         {"type": "string"},
                    "subtitle":      {"type": "string", "description": "One punchy sentence framing the slide angle"},
                    "main_message":  {"type": "string", "description": "The single most important takeaway in one sentence"},
                    "items": {
                        "type": "array",
                        "description": "Primary content items — adapt structure to layout_type",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label":   {"type": "string"},
                                "content": {"type": "string"},
                                "role":    {"type": "string", "description": "primary|secondary|step|risk|control|metric|before|after|phase"}
                            },
                            "required": ["label", "content"]
                        }
                    },
                    "flow_steps": {
                        "type": "array",
                        "description": "Ordered steps for process/attack_chain layouts",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_number": {"type": "integer"},
                                "label":       {"type": "string"},
                                "detail":      {"type": "string"}
                            }
                        }
                    },
                    "definition":     {"type": "string", "description": "Plain-English definition for definition slides"},
                    "presenter_script": {"type": "string", "description": "4-6 sentences the speaker says aloud"}
                },
                "required": ["slide_number", "content_type", "layout_type", "title", "items", "presenter_script"]
            }
        }
    },
    "required": ["presentation_title", "target_audience", "date", "author", "accent_primary", "slides"]
}

async def generate_ks_draft(req: KSGenerateRequest) -> dict:
    spec = _get_spec()
    sys_prompt = f"""You are Magnitude, an elite AI for GTCO Security Monitoring and Threat Intelligence.
You generate professional Knowledge Sharing presentations following a strict design specification.

=== DESIGN SPEC ===
{spec}
===================

GENERATION INSTRUCTIONS:
- Always classify each slide's content_type first, then select the matching layout_type.
- Never use 'structured_list' as the default. Use it ONLY when items are truly independent.
- For process content: use 'horizontal_process' with flow_steps array.
- For attack/threat sequences: use 'attack_chain' with flow_steps.
- For comparisons: use 'two_column_comparison' with items having role='before'/'after' or label as the column header.
- For risk/control content: use 'risk_control_mapping' with items having role='risk' or role='control'.
- For the definition of a key concept: use 'definition_plus_example' with definition field filled.
- For metrics/statistics: use 'metric_dashboard' with items as metric values.
- Choose accent_primary and accent_secondary based on the topic's semantic meaning (not defaults).
- Produce 7-8 slides total. Each slide must genuinely teach something.
- Every bullet in items.content introduces NEW information. No filler, no repetition.
"""
    user_prompt = f"""Topic: {req.input_data.topic}
Target Audience: {req.input_data.target_audience}
Raw Notes/Details:
{req.input_data.details}

Author: {req.generation_options.author}"""

    payload = {
        "contents": [{"role": "user", "parts": [{"text": sys_prompt + "\n\n" + user_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.45,
            "responseSchema": ks_schema
        }
    }
    draft = await magnitude._call_gemini(payload)
    if "error" in draft:
        return draft
    if not draft.get("date"):
        draft["date"] = datetime.now().strftime("%d %B %Y")
    if not draft.get("author"):
        draft["author"] = req.generation_options.author
    return draft

async def refine_ks_draft(draft: dict, corrections: str) -> dict:
    sys_prompt = "You are Magnitude. Refine the Knowledge Sharing draft. Maintain valid data. Respect the original layout_type and content_type choices unless the correction specifically requires changing them. Output must match the JSON schema exactly."
    user_prompt = f"--- CURRENT DRAFT ---\n{json.dumps(draft, indent=2)}\n\n--- CORRECTIONS ---\n{corrections}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": sys_prompt + "\n\n" + user_prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2, "responseSchema": ks_schema}
    }
    return await magnitude._call_gemini(payload)
