from fastapi import APIRouter, HTTPException
from app.db import db

router = APIRouter(prefix="/pins", tags=["pins"])

@router.get("/{prompt_id}")
def get_pins(prompt_id: str):
    pins_collection = db["pins"]

    # Busca pins pelo prompt_id
    pins = list(pins_collection.find({"prompt_id": prompt_id}, {"_id": 0}))

    if not pins:
        raise HTTPException(status_code=404, detail=f"No pins found for prompt_id={prompt_id}")

    return {"pins": pins}
