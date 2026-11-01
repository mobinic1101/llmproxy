from pydantic import BaseModel

class CompletionRequest(BaseModel):
    model: str | None = None
    messages: list[dict]
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    stream: bool | None = None


class ModelsResponse(BaseModel):
    object: str
    data: list[dict]


class CaptchaAnswer(BaseModel):
    captcha_answer: list[int]
