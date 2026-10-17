import os
import json
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key is not set in the environment variables.")


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def load_attractions():
    try:
        with open("attractions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/test")
def test(request: Request):
    attractions_list = load_attractions()
    
    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={"attractions": attractions_list}
    )

@app.get("/profile")
def profile(request: Request):
    return templates.TemplateResponse(request, "profile.html", {"request": request})

@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse(request, "signup.html", {"request": request})

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})