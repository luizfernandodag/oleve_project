# backend/app/routes/prompts.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.scrape_runner import scrape_and_validate  # <- função atualizada
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(prefix="/prompts", tags=["prompts"])

executor = ThreadPoolExecutor(max_workers=2)  # threads para scraping sync

class ScrapeValidateRequest(BaseModel):
    prompt: str

@router.post("/scrape-validate")
async def scrape_validate(payload: ScrapeValidateRequest):
    """
    Executa o scraper Pinterest + validação AI.
    """
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="Prompt é obrigatório")

    try:
        pins =  await scrape_and_validate(payload.prompt) 
        return {"status": "success", "pins": pins}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
