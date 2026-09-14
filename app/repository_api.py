import uuid
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from app.db import get_db, RepositoryDocumentModel
from app.auth import get_current_user, UserSession

router = APIRouter(prefix="/api/repository", tags=["repository"])


class SaveDocumentRequest(BaseModel):
    module: str
    title: str
    file_path: str
    format: str = "docx"


@router.get("/list")
async def list_documents(
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    docs = db.query(RepositoryDocumentModel).order_by(
        RepositoryDocumentModel.date_generated.desc()
    ).all()
    return [
        {
            "id": d.id,
            "module": d.module,
            "title": d.title,
            "file_path": d.file_path,
            "format": d.format,
            "saved_by": d.saved_by,
            "date_generated": d.date_generated.isoformat() if d.date_generated else None
        }
        for d in docs
    ]


@router.post("/save")
async def save_document(
    req: SaveDocumentRequest,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    doc = RepositoryDocumentModel(
        id=str(uuid.uuid4()),
        module=req.module,
        title=req.title,
        file_path=req.file_path,
        format=req.format,
        saved_by=current_user.email,
        date_generated=datetime.utcnow()
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"success": True, "id": doc.id, "message": f"'{req.title}' saved to Repository."}


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    doc = db.query(RepositoryDocumentModel).filter(RepositoryDocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Also delete the physical file if it's local
    if doc.file_path and not doc.file_path.startswith("http"):
        full_path = os.path.join(os.getcwd(), doc.file_path.lstrip("/\\").replace("\\", "/"))
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception:
                pass

    db.delete(doc)
    db.commit()
    return {"success": True, "message": "Document deleted."}


@router.get("/download/{doc_id}")
async def download_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    doc = db.query(RepositoryDocumentModel).filter(RepositoryDocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.file_path.startswith("http"):
        return RedirectResponse(url=doc.file_path)

    full_path = os.path.join(os.getcwd(), doc.file_path.lstrip("/\\").replace("\\", "/"))
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=full_path,
        filename=os.path.basename(full_path),
        media_type="application/octet-stream"
    )
