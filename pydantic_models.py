from pydantic import BaseModel

class CompletionRequest(BaseModel):
    model: str
    messages: list[dict]
    temperature: float
    max_tokens: int
    top_p: float
    stream: bool


class ModelsResponse(BaseModel):
    object: str
    data: list[dict]


class CaptchaAnswer(BaseModel):
    captcha_answer: list[int]
