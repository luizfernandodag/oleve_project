import openai
from ..config import settings

openai.api_key = settings.OPENAI_API_KEY

SYSTEM_PROMPT = (
    "You score how well an image matches an interior design prompt. "
    "Return JSON with 'match_score' (0..1) and 'explanation'."
)

async def score_image(prompt: str, image_url: str):
    try:
        response = openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Prompt: {prompt}"},
                {"role": "user", "content": f"Image URL: {image_url}"}
            ],
            temperature=0
        )
        text = response.choices[0].message.content
        import json
        parsed = json.loads(text)
        score = float(max(0.0, min(1.0, parsed.get("match_score", 0.0))))
        status = "approved" if score >= 0.5 else "disqualified"
        explanation = parsed.get("explanation", "")
    except Exception as e:
        score = 0.0
        status = "disqualified"
        explanation = f"error: {str(e)}"
    return score, status, explanation
