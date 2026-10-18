import os
import json
from fastapi import Cookie, FastAPI, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
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


@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse(request, "signup.html", {"request": request})

@app.post("/signup")
async def handle_signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"full_name": name}
            }
        })
        
        res = Response(status_code=200)
        res.headers["HX-Redirect"] = "/login"
        return res
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Registration failed: {str(e)}"}
        )

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@app.post("/login")
async def login(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        access_token = response.session.access_token
        
        res = Response(status_code=200)
        res.set_cookie(key="sb-access-token", value=access_token, httponly=True)
        res.headers["HX-Redirect"] = "/"
        return res
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": "Login failed", "error": str(e)}
        )
    

@app.get("/profile", response_class=HTMLResponse)
async def get_profile(request: Request, sb_access_token: str = Cookie(default=None)):
    if sb_access_token:
        try:
            
            user_response = supabase.auth.get_user(sb_access_token)
            if user_response and user_response.user:

                user_metadata = user_response.user.user_metadata or {}
                user_name = user_metadata.get("full_name", "User")
                
                return templates.TemplateResponse(
                    request=request, 
                    name="profile.html", 
                    context={
                        "user_name": user_name,
                        "is_guest": False
                    }
                )
        except Exception:
            pass

    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={
            "user_name": "guest",
            "is_guest": True
        }
    )