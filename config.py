from __future__ import annotations

import os


def _get_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _get_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


SOURCE = os.environ.get("DATA_SOURCE", "reddit").strip().lower()
SUBREDDITS = _get_list("SUBREDDITS", ["news"])
QUERIES = _get_list("TWITTER_QUERIES", ["news"])
POSTS_LIMIT = _get_int("POSTS_LIMIT", 50)
COMMENTS_LIMIT = _get_int("COMMENTS_LIMIT", 50)
INCLUDE_COMMENTS = _get_bool("INCLUDE_COMMENTS", True)
SIMULATE_CITY = _get_bool("SIMULATE_CITY", True)
DEBUG = _get_bool("DEBUG", False)
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "social_data.xlsx").strip() or "social_data.xlsx"

INPUT_FILE = os.environ.get("INPUT_FILE", "social_data.xlsx").strip() or "social_data.xlsx"
CLEAN_OUTPUT_FILE = os.environ.get("CLEAN_OUTPUT_FILE", "clean_data.xlsx").strip() or "clean_data.xlsx"
MIN_WORDS = _get_int("MIN_WORDS", 4)

