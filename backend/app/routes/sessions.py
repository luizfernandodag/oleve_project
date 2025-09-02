from app.db import db
from app.utils import serialize_mongo
from bson import ObjectId
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/{prompt_id}")
async def get_sessions(prompt_id: str):
    try:
        oid = ObjectId(prompt_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid prompt_id format")

    sessions = await db.sessions.find({"prompt_id": oid}).to_list(length=None)
    if not sessions:
        raise HTTPException(status_code=404, detail=f"No sessions found for prompt_id={prompt_id}")

    return serialize_mongo(sessions)
