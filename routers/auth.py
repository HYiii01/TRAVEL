from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.config import supabase
from core.security import set_auth_cookie, clear_auth_cookie
from services.auth_service import get_auth_error_message

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html", {"user_name": "guest", "is_guest": True})

@router.post("/signup")
async def handle_signup(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": name}}
        })

        if response.user and not response.user.identities:
            return JSONResponse(status_code=409, content={"message": "This email is already registered. Please log in instead."})

        res = Response(status_code=200)
        res.headers["HX-Redirect"] = "/login?registered=1"
        return res
    except Exception as e:
        return JSONResponse(
            status_code=409 if "already" in str(e).lower() else 400,
            content={"message": get_auth_error_message(e, "signup")}
        )

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "user_name": "guest",
            "is_guest": True,
            "success_message": "Account created successfully." if request.query_params.get("registered") == "1" else "",
        },
    )

@router.post("/login")
async def handle_login(email: str = Form(...), password: str = Form(...)):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if not response.session:
            return JSONResponse(status_code=401, content={"message": "Login failed. Please verify your email before logging in."})

        res = Response(status_code=200)
        set_auth_cookie(res, response.session.access_token)
        res.headers["HX-Redirect"] = "/"
        return res
    except Exception as e:
        return JSONResponse(status_code=401, content={"message": get_auth_error_message(e, "login")})

@router.get("/logout")
@router.post("/logout")
def logout(request: Request):
    if request.headers.get("HX-Request"):
        res = Response(status_code=200)
        clear_auth_cookie(res)
        res.headers["HX-Redirect"] = "/login"
        return res

    res = RedirectResponse(url="/login", status_code=303)
    clear_auth_cookie(res)
    return res