# backend/app/routes/pins.py
from fastapi import APIRouter, HTTPException, Query
from app.db import db
from app.utils import serialize_mongo
from bson import ObjectId
from app.services import scrape_runner  # importa o scrapper

router = APIRouter(prefix="/pins", tags=["pins"])

# --- Rota existente ---
@router.get("/{prompt_id}")
async def get_pins(prompt_id: str):
    try:
        obj_id = ObjectId(prompt_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid prompt_id format")

    pins_cursor = db.pins.find({"prompt_id": obj_id})
    pins_list = await pins_cursor.to_list(length=100)
    if not pins_list:
        raise HTTPException(status_code=404, detail=f"No pins found for prompt_id={prompt_id}")

    return serialize_mongo(pins_list)

# --- rota para testar scraping direto ---
@router.get("/scrape/")
async def scrape_pins(prompt: str = Query(..., description="Prompt para buscar no Pinterest")):
    try:
        pins = scrape_runner.scrape(prompt)  # chama seu scrapper
        if not pins:
            raise HTTPException(status_code=404, detail="Nenhuma imagem encontrada")
        return pins[:3]  # retorna apenas 3 imagens
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
