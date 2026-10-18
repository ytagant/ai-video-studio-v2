"""Trending topics via the Wikimedia pageviews API (no API key needed).

trending_topics(category, limit) returns real currently-trending topics from
English Wikipedia's daily top-articles feed. For "Celebrity News" it prefers
entertainment/person articles (checked via parallel summary fetches).

Guarantees: stdlib + requests only, 10s timeouts, try/except everywhere,
NEVER raises and NEVER returns an empty list (curated per-category
fallbacks cover every failure mode).
"""
from __future__ import annotations

import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import requests

_UA = {"User-Agent": "AIVideoStudio/1.0 (educational video project)"}
_TIMEOUT = 10

_SKIP_TITLES = {"Main_Page"}
_SKIP_PREFIXES = ("Special:", "Wikipedia:", "File:", "Category:", "Portal:",
                  "Template:", "Help:", "Draft:", "Talk:", "User:", "MediaWiki:")

# description/title keywords that mark an article as entertainment-relevant
_ENT_KEYS = ("actor", "actress", "singer", "musician", "rapper", "film ",
             "television", "tv series", "reality", "celebrity", "influencer",
             "youtuber", "tiktoker", "model", "comedian", "presenter", "host",
             "wrestler", "dancer", "director", "producer", "band", "pop star",
             "film", "movie", "show")

_CAT_KEYS: Dict[str, Tuple[str, ...]] = {
    "celebrity news": _ENT_KEYS,
    "tech/science": ("technology", "software", "company", "artificial intelligence",
                     "scientist", "physicist", "engineer", "space", "nasa",
                     "computer", "internet", "robot", "startup"),
    "anime": ("anime", "manga"),
    "cartoon": ("cartoon", "animated"),
    "islamic history": ("islam", "muslim", "mosque", "caliph", "ottoman",
                        "mughal", "prophet", "quran"),
    "horror": ("horror", "thriller"),
}


def _norm_cat(category: str) -> str:
    return (category or "General").strip().lower()


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "general"


def _fmt_views(n: int) -> str:
    try:
        n = int(n or 0)
    except Exception:
        return "trending"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def _get_json(url: str) -> dict:
    r = requests.get(url, headers=_UA, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _top_articles(limit: int = 30) -> Tuple[List[Dict], str]:
    """Top Wikipedia articles by pageviews.

    The top-articles feed lags ~3-4 days behind real time, so walk back up
    to a week until a day with data is found.
    """
    for days_ago in range(1, 8):
        d = datetime.now(timezone.utc) - timedelta(days=days_ago)
        url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
               f"en.wikipedia.org/all-access/{d:%Y}/{d:%m}/{d:%d}")
        try:
            data = _get_json(url)
            arts = data["items"][0]["articles"]
            out = []
            for a in arts:
                t = a.get("article", "")
                if not t or t in _SKIP_TITLES or ":" in t:
                    continue
                out.append({"title": t.replace("_", " "), "views": a.get("views", 0)})
                if len(out) >= limit:
                    break
            if out:
                return out, d.date().isoformat()
        except Exception:
            continue
    return [], ""


def _describe(title: str) -> str:
    """Short 'description + extract head' blob for relevance filtering."""
    try:
        t = urllib.parse.quote(title.replace(" ", "_"))
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{t}",
                         headers=_UA, timeout=_TIMEOUT)
        if r.status_code != 200:
            return ""
        j = r.json()
        return ((j.get("description") or "") + " " + (j.get("extract") or ""))[:400]
    except Exception:
        return ""


def _relevant(title: str, blob: str, keys: Tuple[str, ...]) -> bool:
    if not keys:
        return True
    hay = (title + " " + blob).lower()
    return any(k in hay for k in keys)


# ---------------------------------------------------------------- fallbacks
# Curated evergreen topics per category — used whenever the live API fails or
# yields too few relevant articles. Guarantees a non-empty result.

_FALLBACKS: Dict[str, List[Tuple[str, str]]] = {
    "general": [
        ("The Untold Story of the Titanic", "Evergreen: one of history's most-searched tragedies"),
        ("How the Pyramids Were Really Built", "Evergreen: ancient mystery with massive search interest"),
        ("The Mystery of the Bermuda Triangle", "Evergreen: unsolved mystery audiences love"),
        ("What Happens Inside a Black Hole", "Evergreen: space curiosity never fades"),
        ("The Fall of the Roman Empire", "Evergreen: epic history with drama and lessons"),
        ("Inside the Secret World of Deep Sea Creatures", "Evergreen: nature's strangest wonders"),
        ("How Your Brain Makes Memories", "Evergreen: science everyone relates to"),
        ("The Rise and Fall of Ancient Egypt", "Evergreen: pharaohs, gold and mystery"),
    ],
    "celebrity news": [
        ("Shah Rukh Khan: The King of Bollywood's Empire", "Curated: global superstar, huge fan searches"),
        ("Taylor Swift's Record-Breaking Eras Tour", "Curated: biggest music story of the decade"),
        ("Cristiano Ronaldo: From Madeira to Legend", "Curated: most-followed person on the planet"),
        ("The Rise of MrBeast: YouTube's Biggest Star", "Curated: creator-economy phenomenon"),
        ("Virat Kohli's Fitness Revolution", "Curated: cricket icon with massive desi audience"),
        ("BTS: How They Conquered the World", "Curated: biggest fandom on earth"),
        ("Tom Cruise's Craziest Real Stunts", "Curated: action legend, endlessly watchable"),
        ("Alia Bhatt's Journey to Stardom", "Curated: Bollywood's brightest star"),
    ],
    "documentary": [
        ("The Untold Story of the Titanic", "Evergreen documentary subject"),
        ("How the Pyramids Were Really Built", "Evergreen documentary subject"),
        ("The Fall of the Roman Empire", "Evergreen documentary subject"),
        ("The Secret World of Deep Sea Creatures", "Evergreen documentary subject"),
        ("What Happens Inside a Black Hole", "Evergreen documentary subject"),
        ("The Rise and Fall of Ancient Egypt", "Evergreen documentary subject"),
        ("The Mystery of the Bermuda Triangle", "Evergreen documentary subject"),
        ("How Your Brain Makes Memories", "Evergreen documentary subject"),
    ],
    "anime": [
        ("The Genius of Hayao Miyazaki", "Curated: the master behind Studio Ghibli"),
        ("How Naruto Changed Anime Forever", "Curated: a generation-defining series"),
        ("Demon Slayer's Animation Revolution", "Curated: record-breaking visuals"),
        ("One Piece: 25 Years of Adventure", "Curated: the longest-running epic"),
        ("Studio Ghibli's Hidden Details", "Curated: rewatch-bait for millions of fans"),
        ("Attack on Titan's Ending Explained", "Curated: the most debated finale"),
        ("The Rise of Anime Around the World", "Curated: global phenomenon story"),
        ("Your Name: A Modern Masterpiece", "Curated: beloved film, endless analysis"),
    ],
    "cartoon": [
        ("Tom and Jerry: 85 Years of Chaos", "Curated: the most beloved cartoon rivalry"),
        ("How Pixar Makes You Cry", "Curated: storytelling secrets of a giant"),
        ("The Secret Formula of Peppa Pig", "Curated: preschool phenomenon decoded"),
        ("SpongeBob's Bikini Bottom Explained", "Curated: 25 years of memes and lore"),
        ("How Looney Tunes Changed Comedy", "Curated: legends of animation"),
        ("The Magic Behind Disney Classics", "Curated: timeless animation craft"),
        ("Why Kids Love Cocomelon", "Curated: YouTube's cartoon empire"),
        ("Avatar: The Last Airbender's Perfect Story", "Curated: fan-favorite deep dive"),
    ],
    "horror": [
        ("The World's Most Haunted Places", "Curated: real locations, real fear"),
        ("Unsolved: The Dyatlov Pass Mystery", "Curated: chilling true mystery"),
        ("The Legend of Bloody Mary", "Curated: urban legend deep dive"),
        ("True Stories Behind Famous Horror Films", "Curated: reality is scarier"),
        ("The Disappearance of the Sodder Children", "Curated: unsolved case that haunts"),
        ("Cursed Objects in Museums", "Curated: creepy artifacts with dark pasts"),
        ("The Bell Witch Haunting", "Curated: America's most famous haunting"),
        ("Mysterious Disappearances at Sea", "Curated: ships that vanished"),
    ],
    "islamic history": [
        ("The Golden Age of Baghdad", "Curated: when Baghdad ruled science"),
        ("Salahuddin: The Noble Warrior", "Curated: legendary sultan, timeless respect"),
        ("How Muslims Invented Algebra", "Curated: Al-Khwarizmi's world-changing gift"),
        ("The Rise of the Ottoman Empire", "Curated: 600 years of power"),
        ("Ibn Sina: Father of Modern Medicine", "Curated: genius who shaped healing"),
        ("Al-Andalus: Islam's Golden Spain", "Curated: libraries, palaces and poetry"),
        ("The Voyages of Ibn Battuta", "Curated: history's greatest traveler"),
        ("The Architecture of the Taj Mahal", "Curated: wonder of Islamic art"),
    ],
    "kids": [
        ("Why Is the Sky Blue?", "Curated: the classic kid question"),
        ("How Do Bees Make Honey?", "Curated: nature's sweetest factory"),
        ("Dinosaurs: Giants of the Past", "Curated: every kid's obsession"),
        ("The Water Cycle Adventure", "Curated: science as a story"),
        ("Why Do We Dream?", "Curated: mystery kids love"),
        ("How Do Volcanoes Erupt?", "Curated: explosive science"),
        ("The Secret Life of Ants", "Curated: tiny world, big wonder"),
        ("What Makes a Rainbow?", "Curated: colorful science magic"),
    ],
    "motivational": [
        ("The Mindset of Champions", "Curated: how winners think"),
        ("How Failure Builds Success", "Curated: every legend failed first"),
        ("Discipline Over Motivation", "Curated: the uncomfortable truth"),
        ("Stories of Epic Comebacks", "Curated: from rock bottom to glory"),
        ("The Power of Small Habits", "Curated: tiny changes, huge results"),
        ("From Homeless to Millionaire", "Curated: real rags-to-riches stories"),
        ("Never Give Up: Real Stories", "Curated: perseverance that paid off"),
        ("The 5AM Club Secret", "Curated: mornings of high achievers"),
    ],
    "tech/science": [
        ("How AI Really Works", "Curated: the question everyone asks"),
        ("The Race to Mars", "Curated: humanity's next giant leap"),
        ("Quantum Computers Explained", "Curated: the future of computing"),
        ("The Future of Electric Cars", "Curated: the EV revolution"),
        ("How the Internet Travels the World", "Curated: invisible infrastructure"),
        ("CRISPR: Editing Human DNA", "Curated: science's boldest frontier"),
        ("The James Webb Telescope's Discoveries", "Curated: seeing the first stars"),
        ("Will Robots Take Our Jobs?", "Curated: the automation debate"),
    ],
}


def _fallback(category: str, limit: int) -> List[Dict]:
    cat = _norm_cat(category)
    items = _FALLBACKS.get(cat, _FALLBACKS["general"])
    base = _slug(cat)
    return [
        {"id": f"{base}-{i + 1}", "title": t, "reason": f"\U0001F4CC {r}"}
        for i, (t, r) in enumerate(items[:limit])
    ]


def trending_topics(category: str = "General", limit: int = 8) -> List[Dict]:
    """Return up to `limit` trending topics for category.

    Each item: {"id", "title", "reason"}. Uses live Wikimedia pageviews data
    when available, otherwise curated fallbacks. Never raises, never empty.
    """
    try:
        limit = max(1, min(20, int(limit or 8)))
    except Exception:
        limit = 8
    try:
        return _trending(_norm_cat(category), limit) or _fallback(category, limit)
    except Exception:
        try:
            return _fallback(category, limit)
        except Exception:
            return _fallback("General", limit)


def _trending(cat: str, limit: int) -> List[Dict]:
    arts, day = _top_articles(30)
    if not arts:
        return []
    keys = _CAT_KEYS.get(cat, ())
    # fetch descriptions in parallel for relevance filtering
    blobs: Dict[str, str] = {}
    if keys:
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(_describe, a["title"]): a["title"] for a in arts}
            for fut, title in futs.items():
                try:
                    blobs[title] = fut.result(timeout=15) or ""
                except Exception:
                    blobs[title] = ""
    ranked = [a for a in arts if _relevant(a["title"], blobs.get(a["title"], ""), keys)]
    ranked += [a for a in arts if a not in ranked]  # top-up with the rest
    base = _slug(cat)
    out = []
    for i, a in enumerate(ranked[:limit]):
        out.append({
            "id": f"{base}-{i + 1}",
            "title": a["title"],
            "reason": f"\U0001F525 {_fmt_views(a['views'])} views on Wikipedia ({day})",
        })
    return out
