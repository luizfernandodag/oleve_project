import asyncio
from fastapi import APIRouter, HTTPException
from app.db import db
from app.schemas import PromptIn
from app.services.warmup import warmup_pinterest
from app.services.scrape import scrape_pinterest
from app.services.validate import score_image

router = APIRouter()

async def log_step(prompt_oid, stage, msg):
    sess = await db.sessions.find_one({"prompt_id": prompt_oid, "stage": stage})
    if not sess:
        await db.sessions.insert_one({"prompt_id": prompt_oid, "stage": stage, "status":"pending", "log":[msg]})
    else:
        await db.sessions.update_one({"_id": sess["_id"]}, {"$push":{"log": msg}})

@router.post("/start")
async def start_agent(payload: PromptIn):
    prompt_doc = {"text": payload.text, "created_at": __import__("datetime").datetime.utcnow(), "status":"pending"}
    res = await db.prompts.insert_one(prompt_doc)
    prompt_oid = res.inserted_id
    try:
        await log_step(prompt_oid, "warmup", "starting warmup")
        await warmup_pinterest(payload.text, lambda m: asyncio.create_task(log_step(prompt_oid, "warmup", m)))
        await db.sessions.update_one({"prompt_id": prompt_oid, "stage":"warmup"}, {"$set":{"status":"completed"}})

        await log_step(prompt_oid, "scraping", "start scrape")
        pins = await scrape_pinterest(payload.text, lambda m: asyncio.create_task(log_step(prompt_oid, "scraping", m)))
        await db.sessions.update_one({"prompt_id": prompt_oid, "stage":"scraping"}, {"$set":{"status":"completed"}})

        await log_step(prompt_oid, "validation", f"validating {len(pins)} pins")
        for i, p in enumerate(pins, start=1):
            score, status, explanation = await score_image(payload.text, p["image_url"])
            pin_doc = {
                "prompt_id": prompt_oid,
                "image_url": p["image_url"],
                "pin_url": p["pin_url"],
                "title": p.get("title",""),
                "description": p.get("description",""),
                "match_score": score,
                "status": status,
                "ai_explanation": explanation,
                "metadata": {"collected_at": __import__("datetime").datetime.utcnow()}
            }
            await db.pins.insert_one(pin_doc)
            await log_step(prompt_oid, "validation", f"validated {i}/{len(pins)} score={score:.2f}")

        await db.sessions.update_one({"prompt_id": prompt_oid, "stage":"validation"}, {"$set":{"status":"completed"}})
        await db.prompts.update_one({"_id": prompt_oid}, {"$set":{"status":"completed"}})
        return {"prompt_id": str(prompt_oid)}
    except Exception as e:
        await db.prompts.update_one({"_id": prompt_oid}, {"$set":{"status":"error"}})
        raise HTTPException(status_code=500, detail=str(e))
