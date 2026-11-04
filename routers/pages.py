from fastapi import APIRouter, Cookie, Request
from fastapi.templating import Jinja2Templates
from services.profile_service import get_authenticated_context

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def home(request: Request, sb_access_token: str | None = Cookie(default=None, alias="sb-access-token")):
    context = get_authenticated_context(sb_access_token)
    if context is None:
        context = {
            "is_guest": True,
            "user_name": "Guest",
            "user_initials": "",
            "user_avatar_url": None,
        }
    return templates.TemplateResponse(request, "index.html", context)