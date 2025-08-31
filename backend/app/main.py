from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import prompts, sessions, pins

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(prompts, prefix="/prompts", tags=["prompts"])
app.include_router(sessions, prefix="/sessions", tags=["sessions"])
app.include_router(pins, prefix="/pins", tags=["pins"])

@app.get("/")
async def root():
    return {"status": "ok"}
