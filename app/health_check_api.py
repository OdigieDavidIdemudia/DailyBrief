import os
import uuid
import fitz  # PyMuPDF
import docx
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from app.auth import get_current_user, UserSession
from app.health_check_ai import generate_health_check_model
from app.health_check_docx import render_health_check_report

router = APIRouter()

def extract_text_from_file(filepath: str, filename: str) -> str:
    text = ""
    if filename.lower().endswith('.pdf'):
        try:
            doc = fitz.open(filepath)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")
    elif filename.lower().endswith('.docx'):
        try:
            doc = docx.Document(filepath)
            for p in doc.paragraphs:
                if p.text.strip():
                    text += p.text + "\n"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read DOCX: {e}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or DOCX.")
    return text

from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any

class ExportHealthCheckRequest(BaseModel):
    report_title: str
    report_date: str
    prepared_by: str
    reviewed_by: str
    introduction: str
    observations: List[Dict[str, Any]]
    conclusion: str

class RefineHealthCheckRequest(BaseModel):
    draft: dict
    corrections: str

from app.health_check_ai import refine_health_check_model

@router.post("/api/health-check/refine")
async def refine_health_check(
    req: RefineHealthCheckRequest,
    current_user: UserSession = Depends(get_current_user)
):
    ai_res = await refine_health_check_model(req.draft, req.corrections)
    if "error" in ai_res:
        raise HTTPException(status_code=500, detail=ai_res["error"])
    return {"success": True, "draft": ai_res}

@router.post("/api/health-check/analyze")
async def analyze_health_check(
    file: UploadFile = File(...),
    user_notes: str = Form(...),
    prepared_by: str = Form("David Odigie"),
    reviewed_by: str = Form("Fatima Jinadu"),
    current_user: UserSession = Depends(get_current_user)
):
    # Save the uploaded file temporarily
    temp_id = str(uuid.uuid4())
    temp_dir = os.path.join("/tmp", "health_check")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{temp_id}_{file.filename}")
    
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    try:
        # 1. Extract text from the vendor report
        vendor_text = extract_text_from_file(temp_path, file.filename)
        
        # 2. Ask Gemini to extract findings and map to user notes
        ai_res = await generate_health_check_model(vendor_text, user_notes, prepared_by, reviewed_by)
        
        if "error" in ai_res:
            raise HTTPException(status_code=500, detail=ai_res["error"])
            
        return {"success": True, "draft": ai_res}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp upload
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/api/health-check/export")
async def export_health_check(
    req: ExportHealthCheckRequest,
    current_user: UserSession = Depends(get_current_user)
):
    try:
        document_model = req.dict()
        
        static_dir = os.path.join(os.getcwd(), "static", "reports")
        os.makedirs(static_dir, exist_ok=True)
        temp_id = str(uuid.uuid4())[:8]
        out_filename = f"Health_Check_Report_{temp_id}.docx"
        out_path = os.path.join(static_dir, out_filename)
        
        render_health_check_report(document_model, out_path)
        
        return FileResponse(
            out_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=out_filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
