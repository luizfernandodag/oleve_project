# backend/app/routes/prompts.py
import os
import sys
import json
import subprocess
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/prompts", tags=["prompts"])

class ScrapeDirectRequest(BaseModel):
    prompt: str

@router.post("/scrape-direct")
async def scrape_direct(payload: ScrapeDirectRequest):
    """
    Executa o scraper Pinterest em subprocesso (síncrono, tela visível).
    """
    if not payload.prompt:
        raise HTTPException(status_code=400, detail="Prompt é obrigatório")

    script_path = os.path.join(os.path.dirname(__file__), "..", "services", "scrape_runner.py")
    script_path = os.path.abspath(script_path)

    try:
        result = subprocess.run(
            [sys.executable, script_path, payload.prompt],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Erro no subprocesso: {result.stderr.strip()}")

        stdout_clean = result.stdout.strip()
        if not stdout_clean:
            raise HTTPException(status_code=500, detail=f"Subprocesso retornou stdout vazio. Stderr: {result.stderr.strip()}")

        pins = json.loads(stdout_clean)
        return {"status": "success", "pins": pins}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
