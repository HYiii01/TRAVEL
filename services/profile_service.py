import logging
from datetime import datetime
from typing import Any
from fastapi import HTTPException
from supabase import Client, create_client
from supabase.lib.client_options import SyncClientOptions

from core.config import SUPABASE_URL, SUPABASE_KEY
from core.security import get_authenticated_user

logger = logging.getLogger(__name__)


def format_joined_date(created_at: str | datetime | None) -> str:
    if not created_at:
        return ""

    try:
        joined_at = (
            created_at
            if isinstance(created_at, datetime)
            else datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        )
    except ValueError:
        logger.warning("Invalid user created_at value: %r", created_at)
        return ""

    return joined_at.strftime("%B %d, %Y")


def get_user_client(access_token: str) -> Client:
    client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        SyncClientOptions(headers={"Authorization": f"Bearer {access_token}"}),
    )
    client.postgrest.auth(access_token)
    return client

def load_profile(access_token: str, user_id: str) -> dict[str, Any]:
    try:
        response = (
            get_user_client(access_token)
            .table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else {}
    except Exception:
        logger.exception("Failed to load profile for user %s", user_id)
        return {}

def build_user_context(user, profile: dict[str, Any] | None = None):
    profile = profile or {}
    metadata = user.user_metadata or {}
    user_name = profile.get("username") or metadata.get("full_name") or user.email or "User"
    initials = "".join(part[0] for part in user_name.split()[:2]).upper() or "U"

    return {
        "name": user_name,
        "email": user.email or "",
        "initials": initials,
        "bio": profile.get("bio") or "",
        "location": profile.get("location") or "",
        "language": profile.get("language") or "English",
        "avatar_url": profile.get("avatar_url") or metadata.get("avatar_url"),
        "preferences": profile.get("preferences") or [],
        "joined_date": format_joined_date(getattr(user, "created_at", None)),
    }

def get_authenticated_context(access_token: str | None):
    user = get_authenticated_user(access_token)
    if not user:
        return None

    profile = load_profile(access_token, user.id)
    user_context = build_user_context(user, profile)
    return {
        "user": user_context,
        "user_name": user_context["name"],
        "user_email": user_context["email"],
        "user_initials": user_context["initials"],
        "user_bio": user_context["bio"],
        "user_location": user_context["location"],
        "user_language": user_context["language"],
        "user_avatar_url": user_context["avatar_url"],
        "user_preferences": user_context["preferences"],
        "user_joined_date": user_context["joined_date"],
        "is_guest": False,
    }

def update_profile_row(access_token: str, user_id: str, update_payload: dict[str, Any]):
    try:
        response = (
            get_user_client(access_token)
            .table("profiles")
            .upsert({"id": user_id, **update_payload}, on_conflict="id")
            .execute()
        )
        return response.data or []
    except Exception:
        logger.exception("Failed to update profile for user %s", user_id)
        raise HTTPException(status_code=502, detail="Unable to update profile database.")