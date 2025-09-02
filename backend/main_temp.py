# backend/app/main.py
import os
import subprocess
import sys
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.routes.pins import router as pins
from backend.app.routes.prompts1 import router as prompts
from app.routes.sessions import router as sessions

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI()

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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

# -------------------------------
# Warmup Playwright on startup
# -------------------------------
@app.on_event("startup")
async def startup_event():
    """
    Rodar warmup_runner.py em subprocesso para evitar NotImplementedError
    do asyncio no Windows com Playwright.
    """
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))  # backend/app
        warmup_path = os.path.join(project_root, "app", "services", "warmup_runner.py")

        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(project_root)

        process = subprocess.Popen(
            [sys.executable, warmup_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Log síncrono do subprocesso
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(f"[Warmup stdout] {line.strip()}")
        if process.stderr:
            for line in iter(process.stderr.readline, ''):
                print(f"[Warmup stderr] {line.strip()}")

        print("[Warmup] Warmup script started in separate process.")
    except Exception as e:
        print(f"[Warmup Error] {e}")

# -------------------------------
# Payload para prompts
# -------------------------------
class PromptPayload(BaseModel):
    text: str

# -------------------------------
# Endpoints simples
# -------------------------------
@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/hello")
async def hello():
    return {"message": "Olá, Luiz! Backend funcionando 🚀"}
