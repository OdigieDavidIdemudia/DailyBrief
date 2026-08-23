import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
MEMORY_FILE = os.path.join(os.path.dirname(__file__), 'memory', 'magnitude_guidelines.txt')

class MemoryAddRequest(BaseModel):
    instruction: str

@router.post("/api/memory/add")
async def add_memory(req: MemoryAddRequest):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, 'a') as f:
        f.write(f"- {req.instruction}\n")
    return {"status": "success", "message": "Memory added successfully"}

@router.get("/api/memory")
async def get_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"guidelines": ""}
    with open(MEMORY_FILE, 'r') as f:
        return {"guidelines": f.read()}
