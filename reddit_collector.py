from __future__ import annotations
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence
from praw.models import Comment, Submission
from prawcore import exceptions as praw_exceptions 

import os
import time
import praw

from collector import Collector, Entry, utc_iso
from text_utils import clean_text, is_english, simulate_city


class RedditCollector(Collector):
    def __init__(
        self,
        subreddits: Sequence[str],
        post_limit_per_subreddit: int = 50,
        comment_limit_per_post: int = 50,
        include_comments: bool = True,
        simulate_cities: bool = True,
        max_retries: int = 6,
        backoff_seconds: float = 3.0,
    ) -> None:
        self.subreddits = list(subreddits)
        self.post_limit_per_subreddit = post_limit_per_subreddit
        self.comment_limit_per_post = comment_limit_per_post
        self.include_comments = include_comments
        self.simulate_cities = simulate_cities
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        self.reddit = self._create_client()

    def _create_client(self) -> praw.Reddit:
        client_id = os.environ.get("REDDIT_CLIENT_ID", "").strip()
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "").strip()
        user_agent = os.environ.get("REDDIT_USER_AGENT", "").strip()

        missing = [k for k, v in [
            ("REDDIT_CLIENT_ID", client_id),
            ("REDDIT_CLIENT_SECRET", client_secret),
            ("REDDIT_USER_AGENT", user_agent),
        ] if not v]
        if missing:
            raise RuntimeError(
                "Missing Reddit API env vars: "
                + ", ".join(missing)
                + ". Create an app at https://www.reddit.com/prefs/apps and set these."
            )

        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            check_for_async=False,
        )

    def _with_retries(self, fn, *, what: str):
        sleep_s = self.backoff_seconds
        for attempt in range(1, self.max_retries + 1):
            try:
                return fn()
            except praw_exceptions.TooManyRequests as e:
                wait = float(getattr(e, "sleep_time", sleep_s))
                time.sleep(max(wait, sleep_s))
                sleep_s *= 2
            except (
                praw_exceptions.ResponseException,
                praw_exceptions.ServerError,
                praw_exceptions.RequestException,
            ):
                time.sleep(sleep_s)
                sleep_s *= 2
            except Exception:
                if attempt >= self.max_retries:
                    raise
                time.sleep(sleep_s)
                sleep_s *= 2
        raise RuntimeError(f"Failed after retries while {what}")

    def collect(self) -> Iterable[Entry]:
        for sr in self.subreddits:
            yield from self._collect_subreddit(sr)

    def _collect_subreddit(self, subreddit: str) -> Iterable[Entry]:
        def get_posts():
            return list(self.reddit.subreddit(subreddit).hot(limit=self.post_limit_per_subreddit))

        posts: List[Submission] = self._with_retries(get_posts, what=f"fetching posts from r/{subreddit}")
        for post in posts:
            entry = self._submission_to_entry(post)
            if entry is not None:
                yield entry

            if self.include_comments:
                yield from self._collect_comments(post, parent_post_id=f"t3_{post.id}")

    def _submission_to_entry(self, s: Submission) -> Optional[Entry]:
        text = clean_text(f"{s.title}\n\n{s.selftext}".strip())
        if not text:
            return None
        if not is_english(text):
            return None

        city = simulate_city(seed=s.id) if self.simulate_cities else ""
        created = datetime.fromtimestamp(float(s.created_utc), tz=timezone.utc)
        return Entry(
            id=f"t3_{s.id}",
            type="post",
            parent_id=None,
            text=text,
            city=city,
            timestamp=utc_iso(created),
        )

    def _collect_comments(self, submission: Submission, parent_post_id: str) -> Iterable[Entry]:
        def expand():
            submission.comments.replace_more(limit=0)
            return submission.comments.list()

        comments = self._with_retries(expand, what=f"expanding comments for {parent_post_id}")
        count = 0
        for c in comments:
            if not isinstance(c, Comment):
                continue
            if count >= self.comment_limit_per_post:
                break
            entry = self._comment_to_entry(c, parent_post_id=parent_post_id)
            if entry is None:
                continue
            count += 1
            yield entry

    def _comment_to_entry(self, c: Comment, parent_post_id: str) -> Optional[Entry]:
        text = clean_text(getattr(c, "body", "") or "")
        if not text:
            return None
        if not is_english(text):
            return None

        city = simulate_city(seed=c.id) if self.simulate_cities else ""
        created = datetime.fromtimestamp(float(c.created_utc), tz=timezone.utc)
        return Entry(
            id=f"t1_{c.id}",
            type="comment",
            parent_id=parent_post_id,
            text=text,
            city=city,
            timestamp=utc_iso(created),
        )
