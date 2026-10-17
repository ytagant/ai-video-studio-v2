"""Production orchestrator — runs the six agents in order, streaming progress."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Awaitable, Callable, Dict

from agents import (
    Ctx,
    director_agent,
    editor_agent,
    footage_agent,
    researcher_agent,
    visual_artist_agent,
    voice_agent,
)

SendFn = Callable[[str, Dict[str, Any]], Awaitable[None]]


async def run_production(job_id: str, params: Dict[str, Any], workdir: Path,
                         send: SendFn, jobs: Dict[str, Dict[str, Any]]) -> None:
    job = jobs[job_id]
    workdir.mkdir(parents=True, exist_ok=True)

    async def emit(agent: str, status: str, progress: int, message: str) -> None:
        await send(job_id, {"type": "agent", "agent": agent, "status": status,
                            "progress": progress, "message": message})

    ctx = Ctx(job_id, params, workdir, emit)
    try:
        job["status"] = "running"
        await send(job_id, {"type": "job", "status": "started", "job_id": job_id})

        script = await researcher_agent(ctx)
        job["scenes"] = script["scenes"]
        job["metadata"] = {"title": script.get("title", params["topic"]),
                           "description": script.get("description", ""),
                           "hashtags": script.get("hashtags", [])}
        await send(job_id, {"type": "scenes", "scenes": job["scenes"]})
        await send(job_id, {"type": "metadata", "metadata": job["metadata"]})

        await director_agent(ctx)
        await voice_agent(ctx)
        await send(job_id, {"type": "scenes", "scenes": job["scenes"]})  # durations updated
        await footage_agent(ctx)
        await visual_artist_agent(ctx)
        final = await editor_agent(ctx)

        job["status"] = "done"
        job["video"] = str(final)
        await send(job_id, {"type": "done",
                            "video_url": f"/api/jobs/{job_id}/download",
                            "scenes": job["scenes"],
                            "metadata": job["metadata"]})
    except Exception as e:  # noqa: BLE001
        job["status"] = "error"
        job["error"] = str(e)
        await send(job_id, {"type": "error", "error": str(e)})
