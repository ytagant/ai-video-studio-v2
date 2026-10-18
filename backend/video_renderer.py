"""FFmpeg timeline renderer: per-scene video + narration + music + burned-in subtitles."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List, Optional

W, H, FPS = 1280, 720, 25  # 720p segments: 512MB containers SIGKILL 1080p encodes


def sh(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def _srt_time(sec: float) -> str:
    ms = int(max(0, sec) * 1000)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def build_srt(scenes: List[Dict], path: Path) -> Path:
    t, blocks = 0.0, []
    for i, s in enumerate(scenes, 1):
        dur = float(s["seconds"])
        blocks.append(f"{i}\n{_srt_time(t)} --> {_srt_time(t + dur)}\n{s['narration']}\n")
        t += dur
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def render_timeline(scenes: List[Dict], workdir: Path, music: Optional[str] = None):
    """Composite scenes into final MP4. Returns (final_path, subtitles_burned).

    Built for 512MB containers: the heavy subtitle-burn runs with a single
    x264 thread, and if it still gets OOM-killed the job delivers the video
    without burned subtitles instead of failing.
    """
    segs: List[Path] = []
    auds: List[str] = []

    for i, s in enumerate(scenes):
        dur = float(s["seconds"])
        seg = workdir / f"seg_{i:02d}.mp4"
        if s.get("clip"):
            vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,"
                  f"fade=t=in:st=0:d=0.4,fade=t=out:st={max(0.4, dur - 0.4):.2f}:d=0.4,format=yuv420p")
            sh(["ffmpeg", "-y", "-stream_loop", "-1", "-i", s["clip"], "-t", f"{dur:.2f}",
                "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast",
                "-threads", "2", "-crf", "23", "-an", str(seg)])
        else:
            img = s.get("image")
            if not img:
                raise RuntimeError(f"scene {i} has no visual (no clip, no image)")
            frames = max(1, int(dur * FPS))
            vf = (f"scale=2560:-1,"
                  f"zoompan=z='min(1+0.0012*on,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={frames}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p")
            sh(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", img,
                "-vf", vf, "-frames:v", str(frames),
                "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2", "-crf", "23", "-an", str(seg)])
        segs.append(seg)
        auds.append(s["audio"])

    vlist = workdir / "vlist.txt"
    vlist.write_text("".join(f"file '{p}'\n" for p in segs))
    vcat = workdir / "video_cat.mp4"
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(vlist), "-c", "copy", str(vcat)])

    alist = workdir / "alist.txt"
    alist.write_text("".join(f"file '{p}'\n" for p in auds))
    narr = workdir / "narration.m4a"
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(alist),
        "-c:a", "aac", "-b:a", "128k", str(narr)])

    # --- audio track (optional music bed), audio-only = light ---
    if music and Path(music).exists():
        mixed = workdir / "audio_mix.m4a"
        sh(["ffmpeg", "-y", "-i", str(narr), "-stream_loop", "-1", "-i", str(music),
            "-filter_complex",
            "[1:a]volume=0.12,apad[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
            "-map", "[a]", "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "44100",
            str(mixed)])
        audio = mixed
    else:
        audio = narr

    # --- light A/V mux first (video stream-copied, already 720p) ---
    av = workdir / "av.mp4"
    sh(["ffmpeg", "-y", "-i", str(vcat), "-i", str(audio),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "44100",
        "-shortest", str(av)])

    # --- subtitle burn (the memory-heavy step) ---
    srt = build_srt(scenes, workdir / "subs.srt")
    # Noto Sans Arabic covers Urdu/Arabic script (default DejaVu shows boxes)
    sub = ("subtitles='" + str(srt) + "':force_style="
           "'FontName=Noto Sans Arabic,FontSize=22,PrimaryColour=&HFFFFFF,"
           "OutlineColour=&H80000000,BorderStyle=1,Outline=2,MarginV=40'")
    vf_final = sub + ",setsar=1,format=yuv420p"  # already 720p — no scale needed
    final = workdir / "final.mp4"
    try:
        sh(["ffmpeg", "-y", "-i", str(av), "-vf", vf_final,
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
            "-pix_fmt", "yuv420p", "-preset", "ultrafast", "-threads", "1",
            "-crf", "23", "-movflags", "+faststart", "-c:a", "copy", str(final)])
        return final, True
    except Exception:
        # subtitle burn OOM-killed: deliver the video without burned subtitles
        # rather than failing the whole job
        if final.exists():
            final.unlink()
        av.rename(final)
        return final, False
