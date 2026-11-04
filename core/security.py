from fastapi import Cookie, Header, HTTPException, Response
from core.config import IS_PRODUCTION, supabase

def set_auth_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key="sb-access-token",
        value=access_token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
        max_age=3600,
    )

def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key="sb-access-token",
        httponly=True,
        samesite="lax",
        secure=IS_PRODUCTION,
    )

def get_authenticated_user(access_token: str | None):
    if not access_token:
        return None
    try:
        response = supabase.auth.get_user(access_token)
        return response.user if response and response.user else None
    except Exception:
        return None

def get_access_token(
    authorization: str | None = Header(default=None),
    cookie_token: str | None = Cookie(default=None, alias="sb-access-token"),
) -> str:
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Invalid Authorization header")
        return token
    if cookie_token:
        return cookie_token
    raise HTTPException(status_code=401, detail="Authentication is required")