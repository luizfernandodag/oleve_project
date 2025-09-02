# backend/app/main.py
import os
import subprocess
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.pins import router as pins
from app.routes.prompts import router as prompts
from app.routes.sessions import router as sessions

app = FastAPI()

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Routers
# -------------------------------
app.include_router(prompts)
app.include_router(sessions)
app.include_router(pins)

from pydantic import BaseModel

class ScraperRequest(BaseModel):
    text: str
# -------------------------------
# Endpoint para rodar scrape_runner via subprocesso
# -------------------------------
@app.post("/scraper/run")
async def run_scraper_subprocess(payload: ScraperRequest):
    """
    Executa scrape_runner.py em subprocesso (visível no Windows) para evitar erros de asyncio.
    """
    try:
        prompt_text = payload.text
        project_root = os.path.dirname(os.path.abspath(__file__))  # backend/app
        scrape_path = os.path.join(project_root,"app",  "services", "scrape_runner.py")

        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(project_root)

        process = subprocess.Popen(
            [sys.executable, scrape_path, prompt_text],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return {"status": "error", "message": stderr.strip() or "Erro desconhecido"}

        # JSON retornado pelo scrape_runner
        try:
            import json
            pins = json.loads(stdout)
        except Exception as e:
            return {"status": "error", "message": f"Falha ao decodificar JSON: {e}"}

        return {"status": "success", "pins": pins}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# -------------------------------
# Endpoints simples
# -------------------------------
@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/hello")
async def hello():
    return {"message": "Olá, Luiz! Backend funcionando 🚀"}
