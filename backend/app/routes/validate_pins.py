from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import asyncio
from datetime import datetime

from ..services import scrape_runner
from ..services.validate import score_image

router = APIRouter()

@router.get("/validate-pins")
async def validate_pins(prompt: str = Query(..., description="Visual prompt text")):
    """
    Executa scraping no Pinterest, avalia cada imagem com IA e retorna resultados.
    """
    try:
        # 1️⃣ Scrape Pinterest
        scraped_pins = scrape_runner.scrape(prompt)
        if not scraped_pins:
            return JSONResponse(content={"status": "error", "message": "Nenhum pin encontrado."})

        # 2️⃣ Avaliar cada pin usando IA
        async def validate_pin(pin):
            score, status, explanation = await score_image(prompt, pin["image_url"])
            pin["match_score"] = score
            pin["status"] = status
            pin["ai_explanation"] = explanation
            pin["metadata"] = {"collected_at": datetime.utcnow().isoformat()}
            return pin

        validated_pins = await asyncio.gather(*(validate_pin(pin) for pin in scraped_pins))

        return JSONResponse(content={"status": "success", "pins": validated_pins})

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})
