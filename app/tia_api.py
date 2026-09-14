from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import os
import uuid
from app.auth import get_current_user, UserSession
from app.schemas_tia import TIAGenerateRequest, TIARefineRequest, TIAExportRequest
from app.tia_ai import generate_tia_draft, refine_tia_draft
from app.tia_docx import render_tia_report
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/api/tia/generate")
async def api_tia_generate(
    req: TIAGenerateRequest,
    current_user: UserSession = Depends(get_current_user)
):
    try:
        draft = await generate_tia_draft(req)
        if "error" in draft:
            raise HTTPException(status_code=500, detail=draft["error"])
        return {"success": True, "draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/tia/refine")
async def api_tia_refine(
    req: TIARefineRequest,
    current_user: UserSession = Depends(get_current_user)
):
    try:
        draft = await refine_tia_draft(req.draft, req.corrections)
        if "error" in draft:
            raise HTTPException(status_code=500, detail=draft["error"])
        return {"success": True, "draft": draft}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/tia/export")
async def api_tia_export(
    req: TIAExportRequest,
    current_user: UserSession = Depends(get_current_user)
):
    try:
        static_dir = os.path.join(os.getcwd(), "static", "reports")
        os.makedirs(static_dir, exist_ok=True)
        
        # Determine format
        if req.format == "structured_json":
            
            title = req.draft.get('title', '')
            report_id = req.draft.get('report_id', 'TIA')
            import re
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
            if safe_title:
                base_name = f"{report_id} {safe_title}".replace('/', '_')
            else:
                base_name = report_id.replace('/', '_')
            
            out_filename = f"{base_name}.json"
            out_path = os.path.join(static_dir, out_filename)
            import json
            with open(out_path, "w") as f:
                json.dump(req.draft, f, indent=2)
            return FileResponse(out_path, filename=out_filename)
            
        elif req.format == "csv":
            
            title = req.draft.get('title', '')
            report_id = req.draft.get('report_id', 'TIA')
            import re
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
            if safe_title:
                base_name = f"{report_id} {safe_title}".replace('/', '_')
            else:
                base_name = report_id.replace('/', '_')
            
            out_filename = f"{base_name}_IOCs.csv"
            out_path = os.path.join(static_dir, out_filename)
            import csv
            with open(out_path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Indicator", "Type", "Reputation_Verdict", "Reputation_Scores", "Enrichment_Sources", "Confidence", "Context", "Location", "ISP", "API_Errors", "Report_ID"])
                for ioc in req.draft.get("iocs", []):
                    writer.writerow([
                        ioc.get("value", ""), 
                        ioc.get("type", ""), 
                        ioc.get("reputation_verdict", "Not Enriched"),
                        ioc.get("reputation_scores", ""),
                        ioc.get("enrichment_sources", ""),
                        ioc.get("confidence", ""), 
                        ioc.get("context", ""), 
                        ioc.get("location", ""),
                        ioc.get("isp", ""),
                        ioc.get("api_errors", ""),
                        req.draft.get("report_id", "")
                    ])
            return FileResponse(out_path, filename=out_filename, media_type="text/csv")
            
        elif req.format == "docx":
            
            title = req.draft.get('title', '')
            report_id = req.draft.get('report_id', 'TIA')
            import re
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
            if safe_title:
                base_name = f"{report_id} {safe_title}".replace('/', '_')
            else:
                base_name = report_id.replace('/', '_')
            
            out_filename = f"{base_name}.docx"
            out_path = os.path.join(static_dir, out_filename)
            render_tia_report(req.draft, out_path)
            return FileResponse(out_path, filename=out_filename)
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


