from __future__ import annotations

import random
import re
from typing import Optional

_URL_RE = re.compile(r"(https?://\S+|www\.\S+)", flags=re.IGNORECASE)
_WHITESPACE_RE = re.compile(r"\s+")
_spacy_nlp = None
_nltk_ready = False


def _lemma_backend() -> str:
    import config

    return config.LEMMA_BACKEND


def _ensure_nltk_data() -> None:
    global _nltk_ready
    if _nltk_ready:
        return
    import nltk

    for pkg in (
        "punkt",
        "punkt_tab",
        "wordnet",
        "omw-1.4",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
    ):
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass
    _nltk_ready = True


def _nltk_pos_to_wordnet(tag: str) -> str:
    if tag.startswith("J"):
        return "a"
    if tag.startswith("V"):
        return "v"
    if tag.startswith("N"):
        return "n"
    if tag.startswith("R"):
        return "r"
    return "n"


def _lemmatize_nltk_stem(text: str) -> str:
    import nltk
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize

    _ensure_nltk_data()
    stemmer = PorterStemmer()
    try:
        tokens = word_tokenize(text)
    except LookupError:
        _ensure_nltk_data()
        tokens = word_tokenize(text)
    return " ".join(stemmer.stem(t) for t in tokens if t)


def _lemmatize_nltk_lemma(text: str) -> str:
    import nltk
    from nltk.stem import WordNetLemmatizer
    from nltk.tag import pos_tag
    from nltk.tokenize import word_tokenize

    _ensure_nltk_data()
    lemmatizer = WordNetLemmatizer()
    try:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
    except LookupError:
        _ensure_nltk_data()
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
    out: list[str] = []
    for word, tag in tagged:
        w = word.lower()
        if not w:
            continue
        wn_pos = _nltk_pos_to_wordnet(tag)
        out.append(lemmatizer.lemmatize(w, wn_pos))
    return " ".join(out)


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
    if backend in ("nltk_stem", "stem"):
        return _lemmatize_nltk_stem(text_lower)
    if backend in ("nltk_lemma", "nltk", "lemma"):
        return _lemmatize_nltk_lemma(text_lower)
    if backend in ("spacy",):
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
