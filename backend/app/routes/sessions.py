from fastapi import APIRouter, HTTPException
from app.db import db

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/{prompt_id}")
def get_sessions(prompt_id: str):
    sessions_collection = db["sessions"]

    sessions = list(sessions_collection.find({"prompt_id": prompt_id}, {"_id": 0}))

    if not sessions:
        raise HTTPException(status_code=404, detail=f"No sessions found for prompt_id={prompt_id}")

    return {"sessions": sessions}
