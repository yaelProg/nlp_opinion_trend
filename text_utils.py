from __future__ import annotations

import random
import re
from typing import Optional

_URL_RE = re.compile(r"(https?://\S+|www\.\S+)", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")
_spacy_nlp = None


def _lemma_backend() -> str:
    import config

    return config.LEMMA_BACKEND


def _lemmatize_spacy(text: str) -> str:
    global _spacy_nlp
    import spacy

    if _spacy_nlp is None:
        _spacy_nlp = spacy.load("en_core_web_sm")
    doc = _spacy_nlp(text)
    parts = [t.lemma_.lower() for t in doc if not t.is_space and not t.is_punct]
    return " ".join(parts)


def _apply_lemma(text_lower: str) -> str:
    backend = _lemma_backend()
    if backend in ("", "none", "off", "false"):
        return text_lower
    if backend in ("spacy", "lemma"):
        return _lemmatize_spacy(text_lower)
    return text_lower


def clean_text(text: str) -> str:
    text = text or ""
    text = _URL_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text)
    text = text.strip().lower()
    return _apply_lemma(text)


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
