"""Style engine for AI Video Studio v2.

11 production styles. Each style drives the whole pipeline: the Gemini script
prompt (tone), the footage hunt (visual_bias), music choice, scene pacing
(clip_seconds) and the graphics overlay plan (graphics + caption_style).
"""
from __future__ import annotations

from typing import Dict, List

STYLES: Dict[str, Dict] = {
    "documentary": {
        "id": "documentary",
        "name": "Documentary",
        "name_ur": "دستاویزی فلم",
        "blurb": "Authoritative Netflix/BBC-style narration over real footage.",
        "tone": (
            "Write with the authority of a Netflix/BBC documentary narrator. Open with a "
            "vivid, scene-setting hook that drops the viewer into the moment, then layer "
            "verified facts with cinematic pacing. Every claim must feel researched and real "
            "\u2014 use names, dates and places from the research brief. Keep sentences short "
            "and punchy; let the footage carry the visuals while the narration delivers insight."
        ),
        "visual_bias": ["aerial landscape", "city skyline", "ocean waves",
                        "mountain vista", "historic building", "busy street"],
        "music_mood": "epic orchestral, slow build",
        "clip_seconds": 8,
        "graphics": {"title_card": True, "lower_third": True, "fact_cards": True},
        "caption_style": "clean white subtitles, bottom center, thin black outline",
        "color": "#1e40af",
    },
    "cinematic": {
        "id": "cinematic",
        "name": "Cinematic Explainer",
        "name_ur": "سنیمائی وضاحت",
        "blurb": "Big hooks and cause-and-effect storytelling, YouTube-essay style.",
        "tone": (
            "Write like a top YouTube video essayist: open with a bold hook or surprising "
            "question in the first 10 seconds. Explain with clear cause-and-effect chains, "
            "dramatic reveals and satisfying payoffs. Use vivid analogies, escalate curiosity "
            "scene by scene, and end with a memorable takeaway the viewer will quote."
        ),
        "visual_bias": ["dramatic sky", "city timelapse", "neon lights",
                        "close up hands", "aerial drone", "light rays"],
        "music_mood": "uplifting modern cinematic",
        "clip_seconds": 6,
        "graphics": {"title_card": True, "lower_third": True, "fact_cards": True},
        "caption_style": "bold captions with yellow keyword highlights, bottom center",
        "color": "#f59e0b",
    },
    "recreation": {
        "id": "recreation",
        "name": "3D Recreation",
        "name_ur": "تھری ڈی منظر کشی",
        "blurb": "Dramatic reenactment feel \u2014 tense, dynamic, cinematic.",
        "tone": (
            "Write as a dramatic reenactment script: present-tense, high-tension narration "
            "that recreates the event as if it is happening right now. Describe scenes with "
            "dynamic camera language (close-up, slow push-in, aerial sweep). Build suspense "
            "with cliffhangers between scenes and land a powerful emotional climax."
        ),
        "visual_bias": ["dramatic reenactment", "historic street", "ancient ruins",
                        "storm clouds", "crowd running", "fire night"],
        "music_mood": "dark cinematic pulse",
        "clip_seconds": 6,
        "graphics": {"title_card": True, "lower_third": True, "fact_cards": False},
        "caption_style": "cinematic letterbox captions, centered",
        "color": "#7c3aed",
    },
    "storytelling": {
        "id": "storytelling",
        "name": "Storytelling / Kahani",
        "name_ur": "کہانی",
        "blurb": "Warm narrative arcs with characters, tension and emotion.",
        "tone": (
            "Write a warm, gripping story with a real narrative arc: introduce a character or "
            "situation, build tension through rising action, and land an emotional or "
            "surprising resolution. Use sensory details and dialogue-like lines. The viewer "
            "should feel they watched a short film, not a lecture."
        ),
        "visual_bias": ["village life", "family home", "sunset field",
                        "old street", "child smiling", "rain window"],
        "music_mood": "emotional acoustic, gentle build",
        "clip_seconds": 7,
        "graphics": {"title_card": True, "lower_third": True, "fact_cards": False},
        "caption_style": "soft storybook subtitles, bottom center",
        "color": "#059669",
    },
    "tech": {
        "id": "tech",
        "name": "Tech / Science Explainer",
        "name_ur": "ٹیکنالوجی و سائنس",
        "blurb": "Sharp how-it-works breakdowns with future vision.",
        "tone": (
            "Write like a sharp tech YouTuber: explain complex ideas with simple, visual "
            "language anyone can follow. Structure every video as how-it-works, then "
            "why-it-matters, then what-comes-next. Drop concrete numbers, comparisons and "
            "'here is the crazy part' moments. Keep energy high and jargon at zero."
        ),
        "visual_bias": ["circuit board", "laboratory", "robot",
                        "space earth", "data center", "futuristic city"],
        "music_mood": "futuristic electronic pulse",
        "clip_seconds": 6,
        "graphics": {"title_card": True, "lower_third": True, "fact_cards": True},
        "caption_style": "tech-style captions with stat callouts",
        "color": "#06b6d4",
    },
    "kids": {
        "id": "kids",
        "name": "Kids / Educational",
        "name_ur": "بچوں کی دنیا",
        "blurb": "Cheerful, simple, wonder-filled learning for young minds.",
        "tone": (
            "Write for curious kids aged 6-12: super simple words, short sentences, playful "
            "wonder and fun questions ('Did you know...?'). Turn every fact into a mini "
            "adventure. Be cheerful and encouraging \u2014 no scary or complex content. End with "
            "a fun challenge or question for the viewer."
        ),
        "visual_bias": ["children playing", "colorful toys", "cute animals",
                        "park playground", "balloons", "school kids"],
        "music_mood": "playful cheerful ukulele",
        "clip_seconds": 5,
        "graphics": {"title_card": True, "lower_third": False, "fact_cards": True},
        "caption_style": "big playful rounded captions, high contrast",
        "color": "#fb923c",
    },
    "history": {
        "id": "history",
        "name": "History / Islamic History",
        "name_ur": "تاریخ اسلام",
        "blurb": "Respectful, epic retelling of real history.",
        "tone": (
            "Write with the respect and grandeur history deserves: transport the viewer to "
            "the era with rich scene-setting, real names, dates and places from the research "
            "brief. Honor the scholars, builders and heroes of the Islamic golden age and "
            "world history. Keep it factual and dignified, with an epic, timeless feel."
        ),
        "visual_bias": ["islamic architecture", "mosque interior", "desert caravan",
                        "ancient manuscript", "historic city", "calligraphy art"],
        "music_mood": "epic middle-eastern orchestral",
        "clip_seconds": 8,
        "graphics": {"title_card": True, "lower_third": True, "fact_cards": True},
        "caption_style": "elegant serif-style captions, bottom center",
        "color": "#0d9488",
    },
    "facts": {
        "id": "facts",
        "name": "Facts / Top 10",
        "name_ur": "حیران کن حقائق",
        "blurb": "Punchy numbered facts \u2014 rapid-fire curiosity.",
        "tone": (
            "Write a rapid-fire top-facts countdown: each scene is ONE mind-blowing fact with "
            "a number. Open with the promise ('7 facts that will break your brain'). Keep each "
            "fact to 1-2 punchy sentences with a concrete number or comparison. Escalate \u2014 "
            "save the wildest fact for last."
        ),
        "visual_bias": ["surprised face", "magnifying glass", "space galaxy",
                        "ocean deep", "microscopic", "world map"],
        "music_mood": "energetic pop electronic",
        "clip_seconds": 4,
        "graphics": {"title_card": True, "lower_third": False, "fact_cards": True},
        "caption_style": "big numbered fact cards, center screen",
        "color": "#e11d48",
    },
    "mystery": {
        "id": "mystery",
        "name": "Mystery / Unsolved",
        "name_ur": "پراسرار کہانی",
        "blurb": "Slow dread, eerie questions, chilling reveals.",
        "tone": (
            "Write like a true mystery channel: slow-burn dread, unanswered questions and "
            "chilling reveals. Start with the enigma ('Nobody knows what happened that "
            "night...'). Present clues and theories without resolving everything \u2014 let the "
            "mystery linger. Keep the tone dark, curious and cinematic."
        ),
        "visual_bias": ["dark forest", "foggy night", "abandoned building",
                        "candle dark", "moon clouds", "old door"],
        "music_mood": "dark ambient drone, sparse piano",
        "clip_seconds": 7,
        "graphics": {"title_card": True, "lower_third": False, "fact_cards": True},
        "caption_style": "eerie typewriter-style captions",
        "color": "#7e22ce",
    },
    "motivational": {
        "id": "motivational",
        "name": "Motivational",
        "name_ur": "حوصلہ افزائی",
        "blurb": "Powerful speeches: struggle, grit, triumph.",
        "tone": (
            "Write a powerful motivational speech: speak directly to the viewer ('you') about "
            "struggle, discipline and comeback. Use short, rhythmic, punchy lines that hit "
            "like drumbeats. Paint the pain of giving up against the glory of pushing "
            "through. End with a call to action that makes the viewer want to start TODAY."
        ),
        "visual_bias": ["sunrise mountain", "runner sprint", "gym workout",
                        "ocean waves", "city dawn", "climbing summit"],
        "music_mood": "inspiring epic build, powerful drums",
        "clip_seconds": 5,
        "graphics": {"title_card": True, "lower_third": False, "fact_cards": True},
        "caption_style": "bold all-caps power captions, center",
        "color": "#ca8a04",
    },
    "newsroom": {
        "id": "newsroom",
        "name": "Newsroom",
        "name_ur": "نیوز روم",
        "blurb": "TV-news energy: breaking stories, name straps, ticker feel.",
        "tone": (
            "Write like a prime-time news anchor covering a breaking story: lead with the "
            "headline, then the key facts \u2014 who, what, when, where \u2014 drawn from the research "
            "brief. Keep sentences short and urgent. Add context and reactions, and always "
            "name key figures with their roles (these become lower-third straps). End with "
            "what happens next \u2014 the developing angle."
        ),
        "visual_bias": ["news studio", "city street", "red carpet",
                        "crowd event", "microphone press", "building exterior"],
        "music_mood": "urgent news pulse, dramatic stings",
        "clip_seconds": 5,
        "graphics": {"title_card": True, "lower_third": True, "fact_cards": True},
        "caption_style": "news ticker lower captions + name straps",
        "color": "#dc2626",
    },
}

# Legacy style names from the old 3-style UI -> new ids (forgiving lookup).
_LEGACY_IDS = {
    "documentary": "documentary",
    "3d recreation": "recreation",
    "cinematic explainer": "cinematic",
}


def get_style(style_id: str) -> Dict:
    """Return the style dict for style_id; fall back to documentary."""
    key = (style_id or "").strip().lower()
    key = _LEGACY_IDS.get(key, key)
    return STYLES.get(key, STYLES["documentary"])


def list_styles() -> List[Dict]:
    """Lightweight style list for the GET /api/styles endpoint."""
    return [
        {"id": s["id"], "name": s["name"], "name_ur": s["name_ur"],
         "blurb": s["blurb"], "color": s["color"]}
        for s in STYLES.values()
    ]


# Content categories: the 8 existing + Celebrity News.
CATEGORIES: List[str] = [
    "Anime", "Cartoon", "Documentary", "Horror", "Islamic History",
    "Kids", "Motivational", "Tech/Science", "Celebrity News",
]

# agents.py CATEGORIES entry to add for the new category.
CELEBRITY_NEWS_CATEGORY = {
    "tone": ("entertainment-news tone: celebrity stories and trending showbiz moments "
             "with verified facts, red-carpet energy, respectful but juicy"),
    "visual": "celebrity red carpet event",
}
