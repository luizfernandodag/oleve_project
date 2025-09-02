from pydantic import BaseModel

class PromptIn(BaseModel):
    text: str
