from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentSaveRequest(BaseModel):
    module: str
    title: str
    file_path: str
    format: str

class DocumentResponse(BaseModel):
    id: str
    module: str
    title: str
    file_path: str
    format: str
    date_generated: datetime

    class Config:
        from_attributes = True
