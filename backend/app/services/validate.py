# backend/app/services/validate.py
import json
import asyncio
from ..config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You score how well an image matches an interior design prompt. "
    "Return JSON with 'match_score' (0..1) and 'explanation'."
)

async def score_image(prompt: str, pin: dict):
    try:
        # Executa a chamada do OpenAI em uma thread para não bloquear o event loop
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Prompt: {prompt}"},
                    {"role": "user", "content": f"Image URL: {pin['image_url']}"}
                ],
                temperature=0
            )
        )

        # Extrai o conteúdo do chat
        text = response.choices[0].message.content
        parsed = json.loads(text)

        score = float(max(0.0, min(1.0, parsed.get("match_score", 0.0))))
        status = "approved" if score >= 0.5 else "disqualified"
        explanation = parsed.get("explanation", "")

    except Exception as e:
        score = 0.0
        status = "disqualified"
        explanation = f"error: {e}"

    pin["match_score"] = score
    pin["status"] = status
    pin["ai_explanation"] = explanation
    return pin
