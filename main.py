from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import auth, pages

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)