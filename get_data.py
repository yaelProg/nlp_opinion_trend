from __future__ import annotations
from typing import Iterable, List

import argparse
import csv

from collector import Entry
from reddit_collector import RedditCollector
from twitter_collector import TwitterCollector


CSV_FIELDS = ["id", "type", "parent_id", "text", "city", "timestamp"]


def write_csv(entries: Iterable[Entry], out_path: str) -> int:
    n = 0
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for e in entries:
            w.writerow(
                {
                    "id": e.id,
                    "type": e.type,
                    "parent_id": e.parent_id or "",
                    "text": e.text,
                    "city": e.city,
                    "timestamp": e.timestamp,
                }
            )
            n += 1
    return n


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Collect Reddit posts/comments and Twitter posts into a unified CSV"
    )
    p.add_argument(
        "--source",
        choices=["reddit", "twitter", "both"],
        default="reddit",
        help="Data source to use (default: reddit)",
    )
    p.add_argument(
        "--subreddit",
        action="append",
        default=[],
        help="Subreddit to pull from. Repeatable. Example: --subreddit news --subreddit worldnews",
    )
    p.add_argument("--posts", type=int, default=50, help="Posts per subreddit/query (default: 50)")
    p.add_argument("--comments", type=int, default=50, help="Comments per Reddit post (default: 50)")
    p.add_argument("--no-comments", action="store_true", help="Collect Reddit posts only")
    p.add_argument("--no-city-sim", action="store_true", help="Leave city empty (no simulation)")
    p.add_argument("--query", action="append", default=[], help="Twitter search query (repeatable)")
    p.add_argument(
        "--out",
        default="social_data.csv",
        help="Output CSV path (default: social_data.csv)",
    )
    return p


def main() -> None:
    args = build_arg_parser().parse_args()

    collectors: List[Iterable[Entry]] = []

    if args.source in ("reddit", "both"):
        subreddits: List[str] = args.subreddit or ["news"]
        reddit_collector = RedditCollector(
            subreddits=subreddits,
            post_limit_per_subreddit=int(args.posts),
            comment_limit_per_post=int(args.comments),
            include_comments=not bool(args.no_comments),
            simulate_cities=not bool(args.no_city_sim),
        )
        collectors.append(reddit_collector.collect())

    if args.source in ("twitter", "both"):
        queries: List[str] = args.query or ["news"]
        twitter_collector = TwitterCollector(
            queries=queries,
            max_results_per_query=int(args.posts),
            simulate_cities=not bool(args.no_city_sim),
        )
        collectors.append(twitter_collector.collect())

    def merged_entries() -> Iterable[Entry]:
        for col in collectors:
            for e in col:
                yield e

    entries = merged_entries()
    n = write_csv(entries, args.out)
    print(f"Wrote {n} rows to {args.out}")


if __name__ == "__main__":
    main()
