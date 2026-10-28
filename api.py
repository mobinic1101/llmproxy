import json
import pathlib
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from dependency_functions import get_prompt_messages
from conf import HOST, PORT, captcha_form_url
from helper import open_captcha_browser
from llmwebsite import start_website
from llmwebsite.duckai import DuckAI
from llmwebsite.base import Messages
import pydantic_models


TEMPLATES_DIR = pathlib.Path(__file__).resolve().parent / "templates"
STATIC_DIR = pathlib.Path(__file__).resolve().parent / "static"

api = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

messages = Messages()
duck = DuckAI(messages, headless=False, captcha_screenshot_path=str((STATIC_DIR/"screenshot.png").resolve().absolute()))
start_website(duck)

@api.post("/chat/completions")
@api.post("/v1/chat/completions/")
def stream_sse_response(prompt_messages: Annotated[list[dict], Depends(get_prompt_messages)]):
    if not messages.prompt_q.empty():
        return Response("only one request at a time is allowed.", status.HTTP_400_BAD_REQUEST)

    messages.put_prompt(json.dumps(prompt_messages))

    def pool_sse_response():
        browser_opened = False
        while True:
            if messages.require_captcha.is_set():
                if not browser_opened:
                    open_captcha_browser(f"http://localhost:{PORT}{captcha_form_url}")
                    browser_opened = True
                messages.captcha_result.wait()
                if state:=messages.captcha_result.event_type == "success":
                    messages.require_captcha.clear()

            elif messages.response_complete.is_set():
                messages.response_complete.clear()
                return
            if messages.sse_response_line_q.empty():
                continue
            yield messages.get_sse_response_line()

    return StreamingResponse(pool_sse_response(), media_type="text/event-stream")


# boiler plate function, it must return the actual website's available models.
@api.get("/v1/models", response_model=pydantic_models.ModelsResponse)
def models():
    return {
  "object": "list",
  "data": [
    {"id": "gpt-6-luna", "object": "model", "created": 1694268190, "owned_by": "openai"},
  ]
}


@api.get(captcha_form_url, response_class=HTMLResponse)
def captcha_form(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse(request, "captcha.html")

@api.get("/captcha_image", name="captcha_image")
def get_captcha_image(cache_buster: str | None = None):
    return FileResponse(STATIC_DIR / "screenshot.png", headers={"Cache-Control": "no-cache"})

@api.post("/captcha-answer")
def captcha_answer(data: pydantic_models.CaptchaAnswer):
    print(data.captcha_answer)
    messages.put_captcha_answer(data.captcha_answer) 
    messages.captcha_result.wait()

    state = messages.captcha_result.event_type
    messages.captcha_result.clear()
    # DEBUG ATTENTION: a sleep may be needed in here since the frontend reloads the image immediately but llmwebsite may not have updated the captcha picture yet, so front-end still gets the old image.
    if state == "failure": # either validation failed or the actual answer was wrong.
        return {"result": "failure"}
    elif state == "success":
        messages.require_captcha.clear()
        return {"result": "success"}