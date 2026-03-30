"""
Twitter/X collector using Tweepy.

Authentication via environment variables (Twitter API v2 or v1.1):
  - TWITTER_BEARER_TOKEN  (recommended, app-only v2 search)

Notes:
  - Real location/city is rarely available directly; we use the same city
    simulation helper as the Reddit collector.
  - This collector is intentionally simple: it searches recent Tweets by query
    and yields them as `Entry` objects with type='post'. Replies/threads could
    be mapped to type='comment' later if needed.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence

import tweepy

from collector import Collector, Entry, utc_iso
from text_utils import clean_text, is_english, simulate_city


class TwitterCollector(Collector):
    def __init__(
        self,
        queries: Sequence[str],
        max_results_per_query: int = 50,
        simulate_cities: bool = True,
        max_retries: int = 6,
        backoff_seconds: float = 3.0,
    ) -> None:
        self.queries = list(queries)
        self.max_results_per_query = max_results_per_query
        self.simulate_cities = simulate_cities
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.client = self._create_client()

    def _create_client(self) -> tweepy.Client:
        bearer = os.environ.get("TWITTER_BEARER_TOKEN", "").strip()
        if not bearer:
            raise RuntimeError(
                "Missing TWITTER_BEARER_TOKEN env var. Create a Twitter/X app and set this token."
            )
        return tweepy.Client(bearer_token=bearer, wait_on_rate_limit=True)

    def _with_retries(self, fn, *, what: str):
        sleep_s = self.backoff_seconds
        for attempt in range(1, self.max_retries + 1):
            try:
                return fn()
            except tweepy.TooManyRequests:
                time.sleep(sleep_s)
                sleep_s *= 2
            except tweepy.TweepyException:
                time.sleep(sleep_s)
                sleep_s *= 2
            except Exception:
                if attempt >= self.max_retries:
                    raise
                time.sleep(sleep_s)
                sleep_s *= 2
        raise RuntimeError(f"Failed after retries while {what}")

    def collect(self) -> Iterable[Entry]:
        for q in self.queries:
            yield from self._collect_query(q)

    def _collect_query(self, query: str) -> Iterable[Entry]:
        def search():
            # recent search; you can adjust query to include lang filter too
            return self.client.search_recent_tweets(
                query=query,
                max_results=min(self.max_results_per_query, 100),
                tweet_fields=["created_at", "lang"],
            )

        response = self._with_retries(search, what=f"searching tweets for query={query!r}")
        if not response or not response.data:
            return []

        results: List[Entry] = []
        for tweet in response.data:
            entry = self._tweet_to_entry(tweet)
            if entry is not None:
                results.append(entry)
        return results

    def _tweet_to_entry(self, tweet) -> Optional[Entry]:
        # tweet.lang is a quick language hint from Twitter
        if getattr(tweet, "lang", None) and tweet.lang != "en":
            return None

        text = clean_text(getattr(tweet, "text", "") or "")
        if not text:
            return None
        if not is_english(text):
            return None

        city = simulate_city(seed=tweet.id) if self.simulate_cities else ""
        created_at = getattr(tweet, "created_at", None) or datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return Entry(
            id=str(tweet.id),
            type="post",
            parent_id=None,
            text=text,
            city=city,
            timestamp=utc_iso(created_at),
        )

