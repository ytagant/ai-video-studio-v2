"""AI Video Studio backend — FastAPI + WebSocket orchestration."""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from orchestrator import run_production

load_dotenv()

BASE = Path(__file__).parent
JOBS_DIR = BASE / "jobs"
JOBS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Video Studio")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

jobs: Dict[str, Dict[str, Any]] = {}
queues: Dict[str, asyncio.Queue] = {}


class JobRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    duration: int = Field(default=60, ge=15, le=600)
    language: str = Field(default="English", pattern="^(English|Urdu|Hindi)$")
    style: str = Field(default="Documentary",
                       pattern="^(Documentary|3D Recreation|Cinematic Explainer)$")
    category: str = Field(default="Documentary",
                       pattern="^(Anime|Cartoon|Documentary|Horror|Islamic History|Kids|Motivational|Tech/Science)$")
    voice: str = "default"


class ReeditRequest(BaseModel):
    instruction: str = Field(min_length=3, max_length=500)


async def send(job_id: str, msg: Dict[str, Any]) -> None:
    q = queues.get(job_id)
    if q is not None:
        await q.put(msg)


@app.post("/api/jobs")
async def create_job(req: JobRequest):
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {"id": job_id, "status": "queued", "params": req.model_dump(),
                    "scenes": [], "metadata": {}, "video": None, "error": None}
    queues[job_id] = asyncio.Queue()
    asyncio.create_task(run_production(job_id, req.model_dump(), JOBS_DIR / job_id, send, jobs))
    return {"job_id": job_id}


@app.websocket("/ws/{job_id}")
async def ws_endpoint(ws: WebSocket, job_id: str):
    await ws.accept()
    q = queues.get(job_id)
    if q is None:
        await ws.send_json({"type": "error", "error": "unknown job"})
        await ws.close()
        return
    await ws.send_json({"type": "snapshot", "job": _public(jobs.get(job_id))})
    try:
        while True:
            msg = await q.get()
            await ws.send_json(msg)
            if msg.get("type") in ("done", "error"):
                break
    except WebSocketDisconnect:
        pass


def _public(job: Dict[str, Any] | None) -> Dict[str, Any] | None:
    if not job:
        return None
    out = dict(job)
    out["video_url"] = f"/api/jobs/{job['id']}/download" if job.get("video") else None
    return out


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return _public(job)


@app.get("/api/jobs/{job_id}/download")
async def download(job_id: str):
    job = jobs.get(job_id)
    if not job or not job.get("video"):
        raise HTTPException(404, "video not ready")
    return FileResponse(job["video"], media_type="video/mp4",
                        filename=f"studio_{job_id}.mp4")


@app.post("/api/jobs/{job_id}/reedit")
async def reedit(job_id: str, req: ReeditRequest):
    from agents import apply_reedit
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    if job["status"] != "done":
        raise HTTPException(409, "job not finished yet")
    scenes = await apply_reedit(job, req.instruction)
    job["scenes"] = scenes
    await send(job_id, {"type": "scenes", "scenes": scenes})
    return {"scenes": scenes}


@app.get("/api/health")
async def health():
    return {"ok": True}


# ---- Serve the built frontend (single-container deployment) ----
# API/WS routes above take precedence; everything else serves the SPA.
try:
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    _FRONTEND_DIR = Path(__file__).resolve().parent / "static"
    if _FRONTEND_DIR.is_dir():
        @app.get("/{full_path:path}")
        async def _spa(full_path: str):
            candidate = _FRONTEND_DIR / full_path
            if full_path and candidate.is_file():
                return FileResponse(candidate)
            index = _FRONTEND_DIR / "index.html"
            if index.is_file():
                return FileResponse(index)
            return {"ok": True, "ui": "not built"}
except Exception:
    pass
