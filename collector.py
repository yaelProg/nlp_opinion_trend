from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Literal, Optional


@dataclass(frozen=True)
class Entry:
    id: str
    type: Literal["post", "comment"]
    parent_id: Optional[str]
    text: str
    city: str
    timestamp: str


class Collector:
    def collect(self) -> Iterable[Entry]:
        raise NotImplementedError


def utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
