import json
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import auth, pages

ATTRACTIONS_CACHE: list[Any] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ATTRACTIONS_CACHE
    json_path = os.path.join("static", "attractions.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            ATTRACTIONS_CACHE = json.load(file)
    yield

app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)