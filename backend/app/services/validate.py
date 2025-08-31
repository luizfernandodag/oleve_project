import httpx
from ..config import settings

SYSTEM_PROMPT = (
    "You score how well an image matches an interior design prompt. Return JSON:"
    " { match_score: number (0..1), explanation: string }"
)

async def score_image(prompt: str, image_url: str):
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    body = {
      "model": settings.OPENAI_MODEL,
      "input": [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":[{"type":"input_text","text":f"Prompt: {prompt}"},{"type":"input_image","image_url":image_url}]}
      ],
      "modalities":["text"],
      "prediction":{"type":"json_object","schema":{"type":"object","properties":{"match_score":{"type":"number"},"explanation":{"type":"string"}},"required":["match_score","explanation"]}}
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://api.openai.com/v1/responses", headers=headers, json=body)
        r.raise_for_status()
        j = r.json()
        try:
            parsed = j["output"][0]["content"][0]["json"]
        except Exception:
            parsed = {"match_score": 0.0, "explanation": "parse_error"}
    score = float(max(0.0, min(1.0, parsed.get("match_score", 0.0))))
    status = "approved" if score >= 0.5 else "disqualified"
    return score, status, parsed.get("explanation", "")
