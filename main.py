from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api import api, STATIC_DIR
from conf import HOST, PORT


app = FastAPI()
app.include_router(api)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host=HOST, port=PORT)