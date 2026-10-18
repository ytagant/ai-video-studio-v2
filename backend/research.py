"""Real-data research brief via Wikipedia (no API key needed).

research_brief(topic, language) fetches the best-matching Wikipedia article
summary and returns a concise markdown brief (key facts, dates, names) that
gets injected into the Gemini script prompt — so scripts read like a big
YouTuber's researched video instead of generic AI filler.

Guarantees: stdlib + requests only, 10s timeouts, try/except everywhere,
returns "" on any failure, completes in well under 15s.
"""
from __future__ import annotations

import urllib.parse
from typing import List, Optional

import requests

_UA = {"User-Agent": "AIVideoStudio/1.0 (educational video project)"}
_TIMEOUT = 10
_MAX_WORDS = 300


def _get_json(url: str) -> dict:
    r = requests.get(url, headers=_UA, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _wiki_search(topic: str, lang: str = "en") -> List[str]:
    """Best-matching article titles for topic (namespace 0 only)."""
    q = urllib.parse.quote_plus(topic)
    url = (f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search"
           f"&srsearch={q}&format=json&srlimit=5&srnamespace=0")
    data = _get_json(url)
    return [h["title"] for h in data.get("query", {}).get("search", [])
            if h.get("title")]


def _wiki_summary(title: str, lang: str = "en") -> Optional[dict]:
    """REST summary for one article; None on any failure."""
    try:
        t = urllib.parse.quote(title.replace(" ", "_"))
        return _get_json(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{t}")
    except Exception:
        return None


def _trim_words(text: str, n: int) -> str:
    words = (text or "").split()
    if len(words) <= n:
        return " ".join(words)
    return " ".join(words[:n]) + "\u2026"


def _format_brief(summary: dict, language: str) -> str:
    title = summary.get("displaytitle") or summary.get("title") or "Topic"
    # strip any html tags from displaytitle
    import re
    title = re.sub(r"<[^>]+>", "", title)
    extract = (summary.get("extract") or "").strip()
    if not extract:
        return ""
    desc = (summary.get("description") or "").strip()
    page = ((summary.get("content_urls") or {}).get("desktop") or {}).get("page", "")
    lines = [f"## Research brief: {title}"]
    if desc:
        lines.append(f"**{desc}**")
    lines.append(_trim_words(extract, _MAX_WORDS))
    if page:
        lines.append(f"Source: Wikipedia ({page})")
    lines.append(
        "INSTRUCTIONS FOR THE SCRIPTWRITER: Use the facts above (names, dates, "
        "places) in the script. Do NOT invent dates, names or statistics \u2014 if a "
        "fact is missing from the brief, write around it instead of guessing."
    )
    return "\n\n".join(lines)


def research_brief(topic: str, language: str = "English") -> str:
    """Return a markdown research brief for topic, or "" on any failure.

    Tries the narration language's Wikipedia first (ur/hi), then English.
    Skips disambiguation pages. Never raises.
    """
    try:
        return _research_brief(topic, language)
    except Exception:
        return ""


def _research_brief(topic: str, language: str) -> str:
    topic = (topic or "").strip()
    if not topic:
        return ""
    langs = ["en"]
    if language == "Urdu":
        langs = ["ur", "en"]
    elif language == "Hindi":
        langs = ["hi", "en"]
    for lang in langs:
        try:
            titles = _wiki_search(topic, lang)
        except Exception:
            continue
        for title in titles:
            s = _wiki_summary(title, lang)
            if not s or s.get("type") == "disambiguation":
                continue
            brief = _format_brief(s, language)
            if brief:
                return brief
    return ""
