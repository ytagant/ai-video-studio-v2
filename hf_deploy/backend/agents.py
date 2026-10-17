"""
AI Video Studio — multi-agent pipeline.
Agents: researcher, director, voice, footage, visual_artist, editor.
Every agent is async and reports live progress via ctx.emit(agent, status, progress, message).
Status is one of: working | done | error
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

EmitFn = Callable[[str, str, int, str], Awaitable[None]]

VOICES: Dict[str, List[str]] = {
    "English": ["en-US-AriaNeural", "en-US-GuyNeural"],
    "Urdu": ["ur-PK-AsadNeural", "ur-PK-UzmaNeural"],
    "Hindi": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"],
}

STYLE_GUIDE = {
    "Documentary": "authoritative documentary narration, factual, vivid scene-setting, Netflix/BBC tone",
    "3D Recreation": "dramatic 3D-rendered reenactment feel, dynamic camera language, cinematic tension",
    "Cinematic Explainer": "cinematic explainer style, clear cause-and-effect storytelling, strong hooks",
}

MUSIC_MOODS = {
    "Documentary": "epic orchestral, slow build",
    "3D Recreation": "dark cinematic pulse",
    "Cinematic Explainer": "uplifting modern cinematic",
}

# Content categories — selected in the UI; drive script tone + footage keywords
CATEGORIES = {
    "Anime": {
        "tone": "energetic anime storytelling: dramatic arcs, rivalries, power-ups, emotional peaks",
        "visual": "anime style",
    },
    "Cartoon": {
        "tone": "playful cartoon storytelling: funny gags, lovable characters, simple moral lessons",
        "visual": "3d cartoon",
    },
    "Documentary": {
        "tone": "authoritative documentary narration, factual, vivid scene-setting",
        "visual": "cinematic documentary",
    },
    "Horror": {
        "tone": "suspenseful horror narration: slow dread, eerie mysteries, chilling reveals",
        "visual": "dark horror cinematic",
    },
    "Islamic History": {
        "tone": "respectful historical narration about Islamic golden age: scholars, discoveries, legacy",
        "visual": "islamic historic",
    },
    "Kids": {
        "tone": "cheerful kids educational storytelling: simple words, wonder, fun facts",
        "visual": "kids educational colorful",
    },
    "Motivational": {
        "tone": "powerful motivational speech: struggle, perseverance, triumph",
        "visual": "inspiring cinematic",
    },
    "Tech/Science": {
        "tone": "sharp tech explainer: breakthroughs, how-it-works, future vision",
        "visual": "futuristic tech",
    },
}


class Ctx:
    def __init__(self, job_id: str, params: Dict[str, Any], workdir: Path, emit: EmitFn):
        self.job_id = job_id
        self.params = params
        self.workdir = workdir
        self.assets = workdir / "assets"
        self.assets.mkdir(parents=True, exist_ok=True)
        self.emit = emit
        self.data: Dict[str, Any] = {}

    def p(self, key: str, default: Any = None) -> Any:
        return self.params.get(key, default)


# ------------------------------------------------------------- helpers

def sh(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def ffprobe_duration(path: Path) -> float:
    try:
        r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def estimate_seconds(text: str, language: str) -> float:
    wpm = {"English": 150, "Urdu": 125, "Hindi": 135}.get(language, 140)
    words = max(1, len(text.split()))
    return max(3.0, round(words / wpm * 60 + 1.0, 1))


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


# ------------------------------------------------------------- 1. researcher

def _gemini_script(api_key: str, topic: str, style: str, language: str,
                   n_scenes: int, target: int, category: str = "Documentary") -> Dict[str, Any]:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    guide = STYLE_GUIDE.get(style, STYLE_GUIDE["Documentary"])
    cat_tone = CATEGORIES.get(category, CATEGORIES["Documentary"])["tone"]
    prompt = (
        f"You are a professional {guide} scriptwriter writing in the {category} category: {cat_tone}.\n"
        f"Write a video script about: {topic}\n"
        f"Language of narration: {language}. Target total duration ~{target} seconds across {n_scenes} scenes.\n"
        "Return STRICT JSON only, no markdown fences:\n"
        '{"title":"...","description":"...","hashtags":["#..",...],'
        '"scenes":[{"narration":"...","keywords":"3-5 english footage search keywords","seconds":8}, ...]}\n'
        "Each narration 1-3 sentences. Seconds per scene 5-12. Hashtags 8-12."
    )
    resp = model.generate_content(prompt)
    data = extract_json(getattr(resp, "text", ""))
    if not data or "scenes" not in data:
        raise ValueError("Gemini did not return valid script JSON")
    return data


def _template_script(topic: str, style: str, language: str, n_scenes: int, target: int,
                     category: str = "Documentary") -> Dict[str, Any]:
    per = max(4, round(target / max(1, n_scenes)))
    cat = CATEGORIES.get(category, CATEGORIES["Documentary"])["tone"].split(":")[0]
    if language == "Urdu":
        beats = [
            ("hook", f"کیا آپ نے کبھی {topic} کے بارے میں سوچا ہے؟ یہ داستان آپ کی سوچ بدل کر رکھ دے گی۔"),
            ("context", f"{topic} کو سمجھنے کے لیے ہمیں وہیں لوٹنا ہوگا جہاں سے اس کی ابتدا ہوئی۔"),
            ("deep", f"{topic} کی سب سے خاص بات یہ ہے — جو اکثر نظروں سے اوجھل رہتی ہے۔"),
            ("deep", f"آج بھی ماہرین {topic} پر حیرت زدہ ہیں، اور نئی دریافتیں سامنے آ رہی ہیں۔"),
            ("deep", f"لیکن {topic} کا ایک اور رخ بھی ہے — پراسرار اور سوالوں سے بھرا ہوا۔"),
            ("twist", f"جب آپ سمجھیں کہ {topic} کو جان گئے، تو ایک حیران کن موڑ سب کچھ بدل دیتا ہے۔"),
            ("close", f"حیرت سے حکمت تک — {topic} ہمیں یاد دلاتا ہے کہ دنیا ہماری سوچ سے کہیں بڑی ہے۔"),
            ("cta", f"اگر {topic} کی یہ کہانی آپ کو پسند آئی تو شیئر کریں — اور متجسس رہیں۔"),
        ]
    elif language == "Hindi":
        beats = [
            ("hook", f"क्या आपने कभी {topic} के बारे में सोचा है? यह कहानी आपकी सोच बदल देगी।"),
            ("context", f"{topic} को समझने के लिए हमें वहीं लौटना होगा जहाँ से इसकी शुरुआत हुई।"),
            ("deep", f"{topic} की सबसे खास बात यह है — जो अक्सर नज़रों से ओझल रहती है।"),
            ("deep", f"आज भी विशेषज्ञ {topic} पर हैरान हैं, और नई खोजें सामने आ रही हैं।"),
            ("deep", f"लेकिन {topic} का एक और पहलू भी है — रहस्यमय और सवालों से भरा।"),
            ("twist", f"जब आपको लगे कि आप {topic} को समझ गए, तो एक हैरान करने वाला मोड़ सब कुछ बदल देता है।"),
            ("close", f"हैरत से हिकमत तक — {topic} हमें याद दिलाता है कि दुनिया हमारी सोच से बड़ी है।"),
            ("cta", f"अगर {topic} की यह कहानी पसंद आई तो शेयर करें — और जिज्ञासु बने रहें।"),
        ]
    else:
        beats = [
            ("hook", f"Have you ever wondered about {topic}? This {cat} story will change how you see it forever."),
            ("context", f"To understand {topic}, we go back to where it all began — the origins most people never hear about."),
            ("deep", f"Here is what makes {topic} truly remarkable — details hidden in plain sight."),
            ("deep", f"Experts remain fascinated by {topic}, and new discoveries keep emerging."),
            ("deep", f"But there is another side to {topic} — full of mystery and unanswered questions."),
            ("twist", f"Just when you think you understand {topic}, a surprising twist rewrites everything."),
            ("close", f"From mystery to meaning — {topic} reminds us the world is more extraordinary than it seems."),
            ("cta", f"If this {cat} story of {topic} amazed you, share it — and stay curious."),
        ]
    scenes = []
    # short footage queries: 2-3 significant topic words + a beat noun
    # (stock APIs AND every term — long queries return nothing)
    twords = [w.strip(",:;") for w in topic.split() if len(w.strip(",:;")) > 3][:3]
    tshort = " ".join(twords) if twords else topic
    beat_noun = {"hook": "establishing", "context": "history", "deep": "detail",
                 "twist": "dramatic", "close": "wide", "cta": "inspiring"}
    for i in range(n_scenes):
        kind, line = beats[min(i, len(beats) - 1)] if i < len(beats) else beats[2]
        scenes.append({
            "narration": line,
            "keywords": f"{tshort} {beat_noun.get(kind, 'cinematic')}",
            "seconds": per,
        })
    return {
        "title": f"{topic} — {category} {style}",
        "description": f"An AI-produced {category.lower()} {style.lower()} about {topic}. Narrated in {language}.",
        "hashtags": ["#" + category.lower().replace("/", "").replace(" ", ""),
                     "#ai", "#explainer", "#cinematic", "#storytelling"],
        "scenes": scenes,
    }


async def researcher_agent(ctx: Ctx) -> Dict[str, Any]:
    await ctx.emit("researcher", "working", 5, "Researching topic & writing script…")
    topic = ctx.p("topic"); style = ctx.p("style", "Documentary")
    language = ctx.p("language", "English"); target = int(ctx.p("duration", 60))
    category = ctx.p("category", "Documentary")
    n_scenes = max(3, min(12, round(target / 8)))
    script: Optional[Dict[str, Any]] = None
    key = os.getenv("GEMINI_API_KEY")
    if key:
        await ctx.emit("researcher", "working", 30, "Asking Gemini for scene-by-scene script…")
        try:
            script = await asyncio.to_thread(_gemini_script, key, topic, style, language, n_scenes, target, category)
        except Exception as e:
            await ctx.emit("researcher", "working", 45, f"Gemini unavailable ({e}); using local writer…")
    if script is None:
        script = _template_script(topic, style, language, n_scenes, target, category)
    # normalize
    total = 0.0
    for s in script["scenes"]:
        s["seconds"] = float(s.get("seconds") or 8)
        s.setdefault("keywords", topic)
        total += s["seconds"]
    ctx.data["script"] = script
    await ctx.emit("researcher", "done", 100,
                   f"Script ready: {len(script['scenes'])} scenes (~{int(total)}s)")
    return script


# ------------------------------------------------------------- 2. director

async def director_agent(ctx: Ctx) -> Dict[str, Any]:
    await ctx.emit("director", "working", 5, "Planning shots, pacing & music…")
    script = ctx.data["script"]
    style = ctx.p("style", "Documentary")
    transitions = ["fade", "fade", "slide", "fade"]
    for i, s in enumerate(script["scenes"]):
        words = s["narration"].split()
        s["screen_text"] = " ".join(words[:7])
        s["transition"] = transitions[i % len(transitions)]
        s["music_mood"] = MUSIC_MOODS.get(style, MUSIC_MOODS["Documentary"])
        await ctx.emit("director", "working", int((i + 1) / len(script["scenes"]) * 90),
                       f"Blocking scene {i + 1}/{len(script['scenes'])}…")
    await ctx.emit("director", "done", 100, "Shot list locked, pacing set")
    return script


# ------------------------------------------------------------- 3. voice & sound

async def voice_agent(ctx: Ctx) -> Dict[str, Any]:
    await ctx.emit("voice", "working", 5, "Warming up voices…")
    try:
        import edge_tts  # noqa
        tts_ok = True
    except Exception:
        tts_ok = False
    language = ctx.p("language", "English")
    voices = VOICES.get(language, VOICES["English"])
    voice = ctx.p("voice") if ctx.p("voice") not in (None, "", "default") else voices[0]
    scenes = ctx.data["script"]["scenes"]
    for i, s in enumerate(scenes):
        out = ctx.assets / f"scene_{i:02d}_narr.mp3"
        dur = 0.0
        if tts_ok:
            try:
                import edge_tts
                await edge_tts.Communicate(s["narration"], voice).save(str(out))
                dur = ffprobe_duration(out)
            except Exception:
                tts_ok = False
        if dur <= 0:
            # gTTS fallback (works when edge-tts is network-blocked)
            try:
                from gtts import gTTS
                glang = {"Urdu": "ur", "Hindi": "hi"}.get(language, "en")
                await asyncio.to_thread(
                    gTTS(s["narration"], lang=glang).save, str(out))
                dur = ffprobe_duration(out)
            except Exception:
                dur = 0.0
        if dur <= 0:
            dur = estimate_seconds(s["narration"], language)
            sh(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-t", f"{dur:.1f}", "-q:a", "9", "-acodec", "libmp3lame", str(out)])
        s["audio"] = str(out)
        s["seconds"] = round(dur + 0.6, 1)
        await ctx.emit("voice", "working", int((i + 1) / len(scenes) * 100),
                       f"Voiced scene {i + 1}/{len(scenes)}")
    await ctx.emit("voice", "done", 100, f"Narration complete ({voice})")
    return ctx.data["script"]


# ------------------------------------------------------------- 4. footage hunter

def _pexels_clip(api_key: str, query: str, dest: Path) -> Optional[Path]:
    import requests
    r = requests.get("https://api.pexels.com/videos/search",
                     headers={"Authorization": api_key},
                     params={"query": query, "per_page": 3, "orientation": "landscape",
                             "size": "medium"}, timeout=25)
    r.raise_for_status()
    for v in r.json().get("videos", []):
        files = sorted(v.get("video_files", []), key=lambda f: f.get("width", 0), reverse=True)
        for f in files:
            link = f.get("link", "")
            if link and f.get("width", 0) >= 960 and link.endswith(".mp4"):
                d = requests.get(link, stream=True, timeout=60)
                d.raise_for_status()
                with open(dest, "wb") as fh:
                    for chunk in d.iter_content(1 << 20):
                        fh.write(chunk)
                return dest
    return None


def _pixabay_clip(api_key: str, query: str, dest: Path) -> Optional[Path]:
    import requests
    r = requests.get("https://pixabay.com/api/videos/",
                     params={"key": api_key, "q": query, "per_page": 3}, timeout=25)
    r.raise_for_status()
    for v in r.json().get("hits", []):
        vids = v.get("videos", {})
        for q in ("large", "medium", "small"):
            link = (vids.get(q) or {}).get("url")
            if link:
                d = requests.get(link, stream=True, timeout=60)
                d.raise_for_status()
                with open(dest, "wb") as fh:
                    for chunk in d.iter_content(1 << 20):
                        fh.write(chunk)
                return dest
    return None


_COMMONS_BLOCK = ("burning", "paludan", "protest", "riot", "war", "army",
                  "military", "humvee", "tank", "isis", "terror", "killing",
                  "dead", "corpse", "funeral", "crying")


# Per-category Commons search terms — short, visual, high-hit-rate.
# (Scene-keyword queries are too specific; Commons ANDs every term.)
FOOTAGE_QUERIES = {
    "Islamic History": ["mosque", "islamic architecture", "muslim prayer",
                        "quran", "desert", "islamic art", "baghdad",
                        "islamic calligraphy"],
    "Anime": ["tokyo", "japan", "neon city", "cherry blossom"],
    "Documentary": ["nature", "city", "ocean", "mountains"],
    "Horror": ["dark forest", "fog", "abandoned", "night"],
    "Kids": ["children playing", "toys", "park", "animals"],
    "Cartoon": ["animation", "colorful", "drawing"],
    "Motivational": ["sunrise", "mountain summit", "running", "city timelapse"],
    "Tech/Science": ["technology", "laboratory", "space", "robot"],
}


def _commons_clip(query: str, dest: Path, used: Optional[set] = None) -> Optional[Path]:
    """Fetch a free stock clip from Wikimedia Commons (no API key needed).

    Uses videoinfo derivatives (transcoded ~480p/720p files, small downloads).
    Titles matching _COMMONS_BLOCK are skipped. `used` is a set of already
    picked source URLs for this job — they are skipped so scenes don't repeat
    the same clip. Returns dest on success.
    """
    import urllib.parse
    import urllib.request
    ua = {"User-Agent": "AIVideoStudio/1.0 (educational video project)"}

    def _get_json(url):
        req = urllib.request.Request(url, headers=ua)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)

    data = None
    # Commons ANDs every search term, so long queries return nothing.
    # Try progressively shorter queries until one hits.
    words = [w for w in query.split() if len(w) > 3]
    attempts = []
    if words:
        attempts.append(" ".join(words))
    if len(words) > 3:
        attempts.append(" ".join(words[:3]))
    if len(words) > 2:
        attempts.append(" ".join(words[:2]))
    if words:
        attempts.append(words[0])
    for attempt in attempts:
        aq = urllib.parse.quote_plus(f"filetype:video {attempt}")
        search_url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
                      f"&generator=search&gsrsearch={aq}&gsrnamespace=6&gsrlimit=10"
                      "&prop=imageinfo&iiprop=mime")
        try:
            data = _get_json(search_url)
        except Exception:
            continue
        if data.get("query", {}).get("pages"):
            break
        data = None
    if not data:
        return None
    titles = []
    for p in data.get("query", {}).get("pages", {}).values():
        title = p.get("title", "")
        if any(b in title.lower() for b in _COMMONS_BLOCK):
            continue
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime", "").startswith("video/"):
            titles.append(title)
    if not titles:
        return None

    tparam = urllib.parse.quote("|".join(titles[:8]))
    vi_url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
              f"&titles={tparam}&prop=videoinfo&viprop=derivatives|mime")
    vdata = _get_json(vi_url)

    def _ranked(derivs, duration):
        ranked = []
        for d in derivs:
            src = d.get("src", "")
            if not src:
                continue
            w = d.get("width", 0) or 0
            ext = src.rsplit(".", 1)[-1].lower()
            if w < 480 or w > 1920:
                continue
            # prefer ~480p (fast download on slow links; upscaled to 1080p later)
            fmt_score = 0 if ext in ("mp4", "mov", "m4v") else 1
            # shorter source videos first — scenes only need ~10-20s
            dur_score = 0 if duration and duration <= 120 else (1 if duration and duration <= 240 else 2)
            ranked.append(((dur_score, abs(w - 480), fmt_score), src))
        ranked.sort(key=lambda r: r[0])
        return [src for _, src in ranked]

    for p in vdata.get("query", {}).get("pages", {}).values():
        vi = (p.get("videoinfo") or [{}])[0]
        dur = vi.get("duration") or 0
        if dur and dur > 600:  # skip very long videos (talks etc.) — transcodes are huge
            continue
        for link in _ranked(vi.get("derivatives", []), dur):
            if used is not None and link in used:
                continue
            try:
                # NOTE: upload.wikimedia.org often reports a bogus huge
                # Content-Length on HEAD for transcoded files — cap while streaming.
                dreq = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(dreq, timeout=180) as d, open(dest, "wb") as fh:
                    total = 0
                    while True:
                        chunk = d.read(1 << 20)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > 80_000_000:  # abort oversized downloads
                            raise OSError("clip too large")
                        fh.write(chunk)
                if dest.stat().st_size <= 200_000:
                    continue
                # sanity: must be a real video container, not an image
                with open(dest, "rb") as fh:
                    head = fh.read(16)
                if head[4:8] == b"ftyp" or head[:4] in (b"\x1a\x45\xdf\xa3", b"OggS"):
                    if used is not None:
                        used.add(link)
                    return dest
            except Exception:
                continue
    return None


async def footage_agent(ctx: Ctx) -> Dict[str, Any]:
    await ctx.emit("footage", "working", 5, "Hunting stock footage…")
    pexels = os.getenv("PEXELS_API_KEY"); pixabay = os.getenv("PIXABAY_API_KEY")
    cat_visual = CATEGORIES.get(ctx.p("category", "Documentary"), CATEGORIES["Documentary"])["visual"]
    scenes = ctx.data["script"]["scenes"]
    used_urls: set = set()  # don't reuse the same clip twice in one video
    for i, s in enumerate(scenes):
        dest = ctx.assets / f"scene_{i:02d}_clip.mp4"
        query = f"{s['keywords']} {cat_visual}"
        clip = None
        try:  # 1) Pexels via stored connector credential (secure, key never in files)
            clip = await asyncio.to_thread(_pexels_connector_clip, query, dest)
        except Exception:
            clip = None
        if clip is None and pexels:
            try:
                clip = await asyncio.to_thread(_pexels_clip, pexels, query, dest)
            except Exception:
                clip = None
        if clip is None and pixabay:
            try:
                clip = await asyncio.to_thread(_pixabay_clip, pixabay, query, dest)
            except Exception:
                clip = None
        if clip is None:  # Wikimedia Commons — free, no API key needed
            try:
                # rotate through proven per-category queries (fast, relevant)
                cqueries = FOOTAGE_QUERIES.get(ctx.p("category", ""), [])
                cquery = cqueries[i % len(cqueries)] if cqueries else query
                clip = await asyncio.to_thread(_commons_clip, cquery, dest, used_urls)
            except Exception:
                clip = None
        s["clip"] = str(clip) if clip else None
        await ctx.emit("footage", "working", int((i + 1) / len(scenes) * 100),
                       f"Footage {i + 1}/{len(scenes)} {'found' if clip else '— will be AI-painted'}")
    found = sum(1 for s in scenes if s.get("clip"))
    await ctx.emit("footage", "done", 100, f"Footage locked: {found}/{len(scenes)} clips")
    return ctx.data["script"]


def _pexels_connector_clip(query: str, dest: Path):
    """Fetch one stock clip via the custom.pexels connector helper.

    The API key lives in the Secure Vault; the helper uses a dynamic
    credential surrogate so the key never appears in files or logs.
    Returns dest Path on success, None on any failure.
    """
    import json as _json
    import shutil as _shutil
    import subprocess as _sp
    import sys as _sys
    helper = Path.home() / "workspace/custom-connectors/custom.pexels/bin/pexels_fetch.py"
    if not helper.exists():
        return None
    tmpdir = dest.parent / "pexels_tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)
    try:
        r = _sp.run([_sys.executable, str(helper), query, "2", str(tmpdir)],
                    capture_output=True, text=True, timeout=240)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    try:
        files = _json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return None
    if not files or isinstance(files, dict):
        return None
    src = Path(files[0])
    try:
        if src.exists() and src.stat().st_size > 100_000:
            _shutil.move(str(src), str(dest))
            return dest
    except Exception:
        pass
    return None


# ------------------------------------------------------------- 5. visual artist

def _paint_fallback(keywords: str, idx: int, dest: Path) -> Path:
    from PIL import Image, ImageDraw, ImageFont
    import random
    random.seed(idx * 7919)
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H))
    px = img.load()
    top = (random.randint(8, 30), random.randint(10, 35), random.randint(30, 70))
    bot = (random.randint(40, 90), random.randint(30, 70), random.randint(60, 110))
    for y in range(H):
        t = y / H
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(24):  # soft light streaks
        x = random.randint(0, W); w = random.randint(60, 320)
        d.rectangle([x, 0, x + w, H], fill=(255, 255, 255, 8))
    d.rectangle([0, 0, W, H], fill=(0, 0, 0, 90))  # vignette-ish dim
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 90)
    except Exception:
        font = ImageFont.load_default()
    label = keywords[:42].upper()
    bb = d.textbbox((0, 0), label, font=font)
    d.text(((W - (bb[2] - bb[0])) / 2, H / 2 - 60), label, font=font, fill=(255, 255, 255, 200))
    img.save(dest, quality=92)
    return dest


async def visual_artist_agent(ctx: Ctx) -> Dict[str, Any]:
    await ctx.emit("visual", "working", 5, "Painting missing visuals…")
    scenes = ctx.data["script"]["scenes"]
    missing = [i for i, s in enumerate(scenes) if not s.get("clip")]
    for n, i in enumerate(missing):
        s = scenes[i]
        dest = ctx.assets / f"scene_{i:02d}_bg.jpg"
        await asyncio.to_thread(_paint_fallback, s["keywords"], i, dest)
        s["image"] = str(dest)
        await ctx.emit("visual", "working", int((n + 1) / max(1, len(missing)) * 100),
                       f"Painted scene {i + 1}")
    await ctx.emit("visual", "done", 100,
                   f"Visuals ready ({len(missing)} AI-painted)" if missing else "All scenes have footage")
    return ctx.data["script"]


# ------------------------------------------------------------- 6. editor

async def editor_agent(ctx: Ctx) -> Path:
    await ctx.emit("editor", "working", 5, "Cutting timeline…")
    from video_renderer import render_timeline
    music = os.getenv("MUSIC_FILE")
    total = len(ctx.data["script"]["scenes"])
    await ctx.emit("editor", "working", 25, "Compositing scenes…")
    final = await asyncio.to_thread(render_timeline, ctx.data["script"]["scenes"], ctx.workdir, music)
    await ctx.emit("editor", "working", 85, "Burning subtitles & mixing audio…")
    await ctx.emit("editor", "done", 100, f"Render complete: {final.name}")
    return final


# ------------------------------------------------------------- re-edit helper

async def apply_reedit(job: Dict[str, Any], instruction: str) -> List[Dict[str, Any]]:
    scenes = job["scenes"]
    key = os.getenv("GEMINI_API_KEY")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            payload = json.dumps([s["narration"] for s in scenes])
            resp = await asyncio.to_thread(
                model.generate_content,
                f"Rewrite each narration per this instruction: {instruction}\n"
                f"Return STRICT JSON only: {{\"narrations\":[\"...\", ...]}}\n{ payload}")
            data = extract_json(getattr(resp, "text", ""))
            if data and isinstance(data.get("narrations"), list) and len(data["narrations"]) == len(scenes):
                for s, n in zip(scenes, data["narrations"]):
                    s["narration"] = n
                return scenes
        except Exception:
            pass
    for s in scenes:
        s["narration"] = f"{s['narration']} {instruction}"
    return scenes
