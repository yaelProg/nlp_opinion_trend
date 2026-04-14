from __future__ import annotations
from typing import Any
from loguru import logger

import datetime as dt
import json
import sys
import httpx

import config


def _build_elastic_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "@timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "file": record["file"].name,
        "process": record["process"].id,
        "thread": record["thread"].id,
    }


def _elastic_sink(message) -> None:
    record = message.record
    payload = _build_elastic_payload(record)
    url = f"{config.ELASTICSEARCH_URL.rstrip('/')}/{config.ELASTICSEARCH_INDEX}/_doc"
    headers = {"Content-Type": "application/json"}
    if config.ELASTICSEARCH_API_KEY:
        headers["Authorization"] = f"ApiKey {config.ELASTICSEARCH_API_KEY}"

    try:
        httpx.post(
            url,
            headers=headers,
            content=json.dumps(payload),
            timeout=config.ELASTICSEARCH_TIMEOUT_SECONDS,
        )
    except Exception:
        pass


def setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )
    if config.KIBANA_LOGGING_ENABLED:
        logger.add(_elastic_sink, level="INFO")
