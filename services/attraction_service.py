import json
import os
from typing import Any

_ATTRACTIONS_CACHE: list[Any] = []

def get_attractions() -> list[Any]:
    global _ATTRACTIONS_CACHE
    
    if _ATTRACTIONS_CACHE:
        return _ATTRACTIONS_CACHE

    json_path = os.path.join("static", "attractions.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            _ATTRACTIONS_CACHE = json.load(f)
            return _ATTRACTIONS_CACHE

    return []