from __future__ import annotations
from typing import Iterable, List
from openpyxl import Workbook

import config

from collector import Entry
from reddit_collector import RedditCollector
from twitter_collector import TwitterCollector


FIELDS = ["id", "type", "parent_id", "text", "city", "timestamp"]


def write_excel(entries: Iterable[Entry], out_path: str) -> int:
    n = 0
    wb = Workbook()
    ws = wb.active
    ws.title = "data"
    ws.append(FIELDS)
    for e in entries:
        ws.append([e.id, e.type, e.parent_id or "", e.text, e.city, e.timestamp])
        n += 1
    wb.save(out_path)
    return n


def main() -> None:
    collectors: List[Iterable[Entry]] = []
    twitter_collector = None

    if config.SOURCE in ("reddit", "both"):
        subreddits: List[str] = config.SUBREDDITS
        reddit_collector = RedditCollector(
            subreddits=subreddits,
            post_limit_per_subreddit=config.POSTS_LIMIT,
            comment_limit_per_post=config.COMMENTS_LIMIT,
            include_comments=config.INCLUDE_COMMENTS,
            simulate_cities=config.SIMULATE_CITY,
        )
        collectors.append(reddit_collector.collect())

    if config.SOURCE in ("twitter", "both"):
        queries: List[str] = config.QUERIES
        twitter_collector = TwitterCollector(
            queries=queries,
            max_results_per_query=config.POSTS_LIMIT,
            simulate_cities=config.SIMULATE_CITY,
        )
        collectors.append(twitter_collector.collect())

    def merged_entries() -> Iterable[Entry]:
        for col in collectors:
            for e in col:
                yield e

    try:
        entries = merged_entries()
        n = write_excel(entries, config.OUTPUT_FILE)
        print(f"Wrote {n} rows to {config.OUTPUT_FILE}")
    except Exception as e:
        msg = str(e)
        if "402 Payment Required" in msg or "does not have any credits" in msg:
            print("Twitter API request failed: your account does not have API credits.")
            print("Add billing/credits in your Twitter/X developer account and try again.")
        else:
            print(f"Data collection failed: {msg}")
        return
    if config.DEBUG and twitter_collector is not None:
        print("Twitter debug stats:")
        print(f"  queries={twitter_collector.stats['queries']}")
        print(f"  fetched={twitter_collector.stats['fetched']}")
        print(f"  kept={twitter_collector.stats['kept']}")
        print(f"  filtered_lang={twitter_collector.stats['filtered_lang']}")
        print(f"  filtered_empty={twitter_collector.stats['filtered_empty']}")
        print(f"  filtered_non_english={twitter_collector.stats['filtered_non_english']}")


if __name__ == "__main__":
    main()
