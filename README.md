# 🎬 AI Video Studio — Self-Hosted Multi-Agent Video Production Floor

A complete web app where **six autonomous AI agents** collaborate live to turn a topic
into a finished MP4: research → directing → voiceover → stock footage → AI visuals → FFmpeg render.

- **Frontend:** Next.js 14 (App Router) + Tailwind + Framer Motion + Lucide, dark studio theme
- **Backend:** FastAPI + WebSockets, async agent orchestrator
- **Engine:** FFmpeg — scene compositing, TTS audio, subtitles burn-in, music mix

## 📁 Folder tree

```
video-studio/
├── frontend/                  # Next.js app (localhost:3000)
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # main studio screen
│   │   └── globals.css
│   ├── components/
│   │   ├── Sidebar.tsx        # inputs: topic, style, voice, API keys
│   │   ├── ProductionFloor.tsx# live agent bots + progress
│   │   └── Storyboard.tsx     # scenes, download, re-edit, metadata
│   ├── lib/
│   │   ├── api.ts             # backend client
│   │   └── types.ts
│   ├── package.json  tsconfig.json  next.config.mjs
│   ├── tailwind.config.ts  postcss.config.mjs  Dockerfile
├── backend/                   # FastAPI (localhost:8000)
│   ├── main.py                # REST + WebSocket API
│   │   #  POST /api/jobs  ·  WS /ws/{job_id}  ·  GET /api/jobs/{id}/download
│   ├── orchestrator.py        # runs the 6 agents in order
│   ├── agents.py              # researcher, director, voice, footage, visual, editor
│   ├── video_renderer.py      # FFmpeg timeline compositing
│   ├── requirements.txt  .env.example  Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Run locally (without Docker)

**1. Backend** — needs Python 3.10+ and `ffmpeg` installed:
```bash
cd video-studio/backend
cp .env.example .env        # add API keys (all optional — fallbacks built in)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**2. Frontend** — needs Node 18+:
```bash
cd video-studio/frontend
npm install
npm run dev
```

**3. Open 👉 http://localhost:3000**

## 🐳 Run with Docker

```bash
cd video-studio
cp backend/.env.example backend/.env   # optional keys
docker compose up --build
# frontend: http://localhost:3000   backend: http://localhost:8000
```

## 🔑 API keys (all optional — every agent has a fallback)

| Key | Agent | Without it |
|---|---|---|
| `GEMINI_API_KEY` | Researcher | Built-in template scriptwriter |
| `PEXELS_API_KEY` / `PIXABAY_API_KEY` | Footage Hunter | Visual Artist paints cinematic placeholders |
| `ELEVENLABS_API_KEY` | — | Edge-TTS is default and needs **no** key |
| `MUSIC_FILE` | Editor | No background music mix |

Get free keys: [Google AI Studio](https://aistudio.google.com),
[Pexels](https://www.pexels.com/api/), [Pixabay](https://pixabay.com/api/docs/).

## 🤖 The six agents

1. **Researcher & Writer** — topic → scene-by-scene script (Gemini JSON) with narration,
   footage keywords, title, description, hashtags. Languages: English, Urdu, Hindi.
2. **Director** — shot pacing, screen text, transitions, music mood per style.
3. **Voice & Sound** — Edge-TTS narration per scene (`ur-PK`, `hi-IN`, `en-US` voices);
   scene duration auto-fits the audio.
4. **Footage Hunter** — Pexels → Pixabay stock clips per scene keywords, cached locally.
5. **Visual Artist** — cinematic AI-painted fallback frames when no clip is found.
6. **Editor** — FFmpeg: trims/loops footage, Ken Burns on stills, concats scenes,
   mixes narration (+ optional music), burns in subtitles → `final.mp4`.

Progress streams over WebSocket: each agent reports `working → done` with live %.
The storyboard shows every scene, the MP4 download, auto title/description/hashtags,
and an **AI re-edit box** to rewrite narration.

## ⚠️ Notes

- First run downloads Python/Node deps — allow a few minutes.
- Rendering speed depends on scene count; `veryfast` preset is used by default.
- Videos are AI-generated: add an "AI-generated" disclosure wherever you publish.
