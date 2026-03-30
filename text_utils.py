"""
Text cleaning + optional helpers (language check, city simulation).
"""

from __future__ import annotations

import random
import re
from typing import Optional


_URL_RE = re.compile(r"(https?://\S+|www\.\S+)", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """
    Remove URLs and normalize whitespace.

    Keeps punctuation/emojis/etc. intact; only removes URLs and collapses
    whitespace to a single space.
    """
    text = text or ""
    text = _URL_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def is_english(text: str) -> bool:
    """
    Best-effort English detection.

    Uses langdetect if installed; otherwise falls back to a light heuristic.
    """
    t = (text or "").strip()
    if not t:
        return False

    # Fast path heuristic: if it's mostly ASCII, it's *likely* English.
    # This is intentionally permissive; langdetect provides better quality.
    ascii_ratio = sum(1 for c in t if ord(c) < 128) / max(1, len(t))
    if ascii_ratio < 0.8:
        try:
            from langdetect import detect  # type: ignore
        except Exception:
            return False
        try:
            return detect(t) == "en"
        except Exception:
            return False

    # If langdetect is available, use it for better filtering.
    try:
        from langdetect import detect  # type: ignore
    except Exception:
        return True
    try:
        return detect(t) == "en"
    except Exception:
        return True


def simulate_city(seed: Optional[str] = None) -> str:
    """
    Optional city simulation when real location isn't available.

    Reddit content typically doesn't include author location. This function gives
    you a deterministic-ish city if you pass a seed (e.g., entry id), otherwise
    random.
    """
    cities = [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Phoenix",
        "Philadelphia",
        "San Antonio",
        "San Diego",
        "Dallas",
        "San Jose",
        "London",
        "Toronto",
        "Sydney",
        "Dublin",
        "Seattle",
    ]
    rng = random.Random(seed) if seed is not None else random
    return rng.choice(cities)

