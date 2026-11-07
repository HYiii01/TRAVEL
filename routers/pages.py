from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.attraction_service import get_attractions
from services.profile_service import get_authenticated_context

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def home(
    request: Request,
    sb_access_token: str | None = Cookie(default=None, alias="sb-access-token"),
):
    context = get_authenticated_context(sb_access_token)
    if context is None:
        context = {
            "is_guest": True,
            "user_name": "Guest",
            "user_initials": "",
            "user_avatar_url": None,
        }
    return templates.TemplateResponse(request, "index.html", context)

@router.get("/overview", response_class=HTMLResponse)
async def get_overview(
    request: Request,
    sb_access_token: str | None = Cookie(default=None, alias="sb-access-token"),
):
    context = get_authenticated_context(sb_access_token)
    
    if not context:
        return RedirectResponse(url="/login", status_code=303)

    context.update({
        "recent_trips": [],
        "wishlist": [],
    })
    return templates.TemplateResponse(
        request=request,
        name="overview.html",
        context=context,
    )

@router.get("/trips", response_class=HTMLResponse)
async def profile_trips(
    request: Request,
    sb_access_token: str | None = Cookie(default=None, alias="sb-access-token"),
):
    context = get_authenticated_context(sb_access_token)
    if not context:
        return RedirectResponse(url="/login", status_code=303)

    attractions_list = get_attractions()

    context.update({
        "attractions": attractions_list,
    })
    return templates.TemplateResponse(
        request=request,
        name="trips.html",
        context=context,
    )

@router.get("/profile", response_class=HTMLResponse)
async def get_profile(
    request: Request,
    sb_access_token: str | None = Cookie(default=None, alias="sb-access-token"),
):
    context = get_authenticated_context(sb_access_token)
    if context:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context=context,
        )

    return RedirectResponse(url="/login", status_code=303)