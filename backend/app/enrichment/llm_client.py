import json
import logging
import re
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_SYSTEM = """You are a news analyst for Puerto Vallarta / Banderas Bay, Mexico.
Given a headline and short excerpt, respond with ONLY a compact JSON object (no markdown) with keys:
category (one of: general, safety, infrastructure, event),
summary_en (one English sentence),
summary_es (one Spanish sentence),
neighborhood_hint (short English place name or empty string if unknown).
"""


def _parse_json_blob(text: str) -> dict[str, Any] | None:
    text = text.strip()
    m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def enrich_with_ollama(title: str, summary: str | None) -> dict[str, Any] | None:
    base = (settings.ollama_base_url or "").rstrip("/")
    if not base:
        return None
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {
                "role": "user",
                "content": f"Title: {title}\nExcerpt: {summary or ''}",
            },
        ],
        "stream": False,
    }
    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.post(f"{base}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
        msg = (data.get("message") or {}).get("content") or ""
        if not msg and data.get("choices"):
            msg = data["choices"][0].get("message", {}).get("content") or ""
        return _parse_json_blob(msg)
    except Exception as e:  # noqa: BLE001
        logger.warning("Ollama enrichment failed: %s", e)
        return None


def enrich_with_groq(title: str, summary: str | None) -> dict[str, Any] | None:
    key = settings.groq_api_key
    if not key:
        return None
    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {
                "role": "user",
                "content": f"Title: {title}\nExcerpt: {summary or ''}",
            },
        ],
        "temperature": 0.2,
    }
    try:
        with httpx.Client(
            timeout=60.0,
            headers={"Authorization": f"Bearer {key}"},
        ) as client:
            r = client.post("https://api.groq.com/openai/v1/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
        msg = data["choices"][0]["message"]["content"]
        return _parse_json_blob(msg)
    except Exception as e:  # noqa: BLE001
        logger.warning("Groq enrichment failed: %s", e)
        return None


def enrich_text(title: str, summary: str | None) -> dict[str, Any] | None:
    out = enrich_with_ollama(title, summary)
    if out:
        return out
    return enrich_with_groq(title, summary)
