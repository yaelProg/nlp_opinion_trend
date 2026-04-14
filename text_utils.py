from __future__ import annotations
from typing import Optional

import random
import re

_URL_RE = re.compile(r"(https?://\S+|www\.\S+)", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    text = text or ""
    text = _URL_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip().lower()


def is_english(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False

    ascii_ratio = sum(1 for c in t if ord(c) < 128) / max(1, len(t))
    if ascii_ratio < 0.8:
        try:
            from langdetect import detect
        except Exception:
            return False
        try:
            return detect(t) == "en"
        except Exception:
            return False

    try:
        from langdetect import detect
    except Exception:
        return True
    try:
        return detect(t) == "en"
    except Exception:
        return True


def simulate_city(seed: Optional[str] = None) -> str:
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
