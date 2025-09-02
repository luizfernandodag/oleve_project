# backend/app/routes/prompts.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.scrape_runner import scrape

router = APIRouter(prefix="/prompts", tags=["prompts"])

class ScrapeDirectRequest(BaseModel):
    prompt: str

@router.post("/scrape-direct")
async def scrape_direct(payload: ScrapeDirectRequest):
    """
    Executa o scraper Pinterest diretamente (tela visível no Windows).
    """
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="Prompt é obrigatório")

    try:
        pins = scrape(payload.prompt)  # 🚀 Chamada direta
        return {"status": "success", "pins": pins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
