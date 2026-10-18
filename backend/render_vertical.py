"""Vertical (9:16) timeline renderer — mirror of video_renderer.render_timeline.

Same OOM-safe strategy for 512MB containers: light A/V mux first
(video stream-copied), then a single-x264-thread subtitle burn; if the
burn is OOM-killed the job delivers the video without subtitles.

Graphics: scenes may carry ``lt_png`` / ``fact_png`` (full-frame
transparent PNGs from graphics.py, composited with plain overlay=0:0).
``title_card_png`` (opaque full-frame PNG) becomes a 3s intro segment;
narration audio is padded with 3s of silence so A/V stay in sync and
subtitle timings shift by the intro length.

Contract: render_timeline_vertical(scenes, workdir, music=None,
title_card_png=None) -> (final_path, subtitles_burned)
Scene dict keys used: seconds, narration, clip|image, audio,
optional lt_png, fact_png.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from video_renderer import sh  # NOTE: we do NOT reuse build_srt here — see build_ass_vertical

VW, VH, VFPS = 720, 1280, 25  # 720x1280 segments for TikTok/Shorts

INTRO_SECONDS = 3.0

SUB_FONT_SIZE = 20
SUB_MARGIN_V = 260  # px from bottom: clear of TikTok's bottom UI + our lower-third strap


def _ass_time(sec: float) -> str:
    ms = int(max(0, sec) * 1000)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h}:{m:02}:{s:02}.{ms // 10:02}"


def build_ass_vertical(scenes: List[Dict], path: Path, offset: float = 0.0) -> Path:
    """Write an ASS subtitle file with PlayRes == video size (720x1280).

    Why ASS and not SRT: without a PlayRes header libass falls back to
    PlayResY=288 and scales MarginV by 1280/288 (~4.44x), so MarginV=260
    lands at the TOP of the frame. Declaring PlayResX/Y makes MarginV
    exact video pixels on any libass build.
    """
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {VW}\n"
        f"PlayResY: {VH}\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour,"
        " OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,"
        " ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow,"
        " Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: VSub,Noto Sans Arabic,"
        f"{SUB_FONT_SIZE},&H00FFFFFF,&H000019FF,&H80000000,&H00000000,"
        "0,0,0,0,100,100,0,0,1,2,0,2,40,40,"
        f"{SUB_MARGIN_V},1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV,"
        " Effect, Text\n"
    )
    t, events = offset, []
    for s in scenes:
        dur = float(s["seconds"])
        text = _wrap_narration(s["narration"], 6).replace("\n", "\\N").strip()
        if text:
            events.append(
                f"Dialogue: 0,{_ass_time(t)},{_ass_time(t + dur)},VSub,,0,0,0,,{text}")
        t += dur
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return path


def _wrap_narration(text: str, words_per_line: int = 6) -> str:
    words = (text or "").split()
    lines = [" ".join(words[i:i + words_per_line])
             for i in range(0, len(words), words_per_line)]
    return "\n".join(lines) or " "


def _overlay_chain(base_vf: str, overlays: List[Tuple[str, float, float]]) -> str:
    """Append full-frame PNG overlays to a base video filter.

    overlays: [(input_index, show_from, show_to), ...] -> filter_complex body
    ending in [vout].
    """
    fc = base_vf + "[bg];"
    cur = "bg"
    for n, (idx, t0, t1) in enumerate(overlays, 1):
        nxt = f"v{n}"
        fc += (f"[{idx}:v]format=rgba[ov{n}];"
               f"[{cur}][ov{n}]overlay=0:0:"
               f"enable='between(t,{t0:.1f},{t1:.1f})'[{nxt}];")
        cur = nxt
    fc += f"[{cur}]format=yuv420p[vout]"
    return fc


def _scene_cmd(s: Dict, i: int, workdir: Path) -> None:
    dur = float(s["seconds"])
    seg = workdir / f"vseg_{i:02d}.mp4"
    fout = max(0.4, dur - 0.4)

    overlays: List[Tuple[int, float, float]] = []
    inputs: List[str] = []
    has_lt = bool(s.get("lt_png") and Path(s["lt_png"]).exists())
    has_fact = bool(s.get("fact_png") and Path(s["fact_png"]).exists())
    if has_lt and has_fact:
        # stagger: strap first, fact card second
        overlays.append((1, 0.8, min(4.2, dur - 0.3)))
        overlays.append((2, 4.4, min(8.4, dur - 0.3)))
        inputs += ["-i", str(s["lt_png"]), "-i", str(s["fact_png"])]
    elif has_lt:
        overlays.append((1, 0.8, min(4.8, dur - 0.3)))
        inputs += ["-i", str(s["lt_png"])]
    elif has_fact:
        overlays.append((1, 0.8, min(4.8, dur - 0.3)))
        inputs += ["-i", str(s["fact_png"])]

    if s.get("clip"):
        base = (f"scale={VW}:{VH}:force_original_aspect_ratio=increase,"
                f"crop={VW}:{VH},setsar=1,"
                f"fade=t=in:st=0:d=0.4,fade=t=out:st={fout:.2f}:d=0.4")
        cmd = (["ffmpeg", "-y", "-stream_loop", "-1", "-i", s["clip"]] + inputs +
               ["-t", f"{dur:.2f}"])
        vfilter: Optional[str] = _overlay_chain(f"[0:v]{base}", overlays) if overlays else base
        cmd += (["-r", str(VFPS)] +
                (["-filter_complex", vfilter, "-map", "[vout]"] if overlays
                 else ["-vf", vfilter]) +
                ["-c:v", "libx264", "-preset", "ultrafast",
                 "-threads", "2", "-crf", "23", "-an", str(seg)])
        sh(cmd)
    else:
        img = s.get("image")
        if not img:
            raise RuntimeError(f"scene {i} has no visual (no clip, no image)")
        frames = max(1, int(dur * VFPS))
        base = (f"scale={VW}:{VH}:force_original_aspect_ratio=increase,"
                f"crop={VW}:{VH},"
                f"zoompan=z='min(1+0.0012*on,1.25)':x='iw/2-(iw/zoom/2)'"
                f":y='ih/2-(ih/zoom/2)':d={frames}:s={VW}x{VH}:fps={VFPS},"
                f"setsar=1")
        cmd = (["ffmpeg", "-y", "-loop", "1", "-framerate", str(VFPS),
                "-i", img] + inputs)
        vfilter = _overlay_chain(f"[0:v]{base}", overlays) if overlays else base
        cmd += ((["-filter_complex", vfilter, "-map", "[vout]"] if overlays
                 else ["-vf", vfilter]) +
                ["-frames:v", str(frames),
                 "-c:v", "libx264", "-preset", "ultrafast",
                 "-threads", "2", "-crf", "23", "-an", str(seg)])
        sh(cmd)


def _intro_segment(title_png: Path, workdir: Path) -> Path:
    seg = workdir / "vseg_intro.mp4"
    vf = (f"scale={VW}:{VH},setsar=1,format=yuv420p,"
          f"fade=t=in:st=0:d=0.4,fade=t=out:st={INTRO_SECONDS - 0.4:.2f}:d=0.4")
    sh(["ffmpeg", "-y", "-loop", "1", "-framerate", str(VFPS), "-i", str(title_png),
        "-t", f"{INTRO_SECONDS:.2f}", "-vf", vf, "-r", str(VFPS),
        "-c:v", "libx264", "-preset", "ultrafast", "-threads", "2",
        "-crf", "23", "-an", str(seg)])
    return seg


def _silence(seconds: float, dest: Path) -> Path:
    sh(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", f"{seconds:.2f}", "-c:a", "aac", "-b:a", "128k", str(dest)])
    return dest


def render_timeline_vertical(scenes: List[Dict], workdir: Path,
                             music: Optional[str] = None,
                             title_card_png: Optional[Path] = None):
    """Composite scenes into a 720x1280 MP4. Returns (final_path, subtitles_burned)."""
    workdir = Path(workdir)
    segs: List[Path] = []
    auds: List[str] = []

    has_intro = bool(title_card_png and Path(title_card_png).exists())
    if has_intro:
        segs.append(_intro_segment(Path(title_card_png), workdir))
        auds.append(str(_silence(INTRO_SECONDS, workdir / "intro_silence.m4a")))

    for i, s in enumerate(scenes):
        _scene_cmd(s, i, workdir)
        segs.append(workdir / f"vseg_{i:02d}.mp4")
        auds.append(s["audio"])

    vlist = workdir / "vvlist.txt"
    vlist.write_text("".join(f"file '{p}'\n" for p in segs))
    vcat = workdir / "vvideo_cat.mp4"
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(vlist),
        "-c", "copy", str(vcat)])

    alist = workdir / "valist.txt"
    alist.write_text("".join(f"file '{p}'\n" for p in auds))
    narr = workdir / "vnarration.m4a"
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(alist),
        "-c:a", "aac", "-b:a", "128k", str(narr)])

    # --- audio track (optional music bed), audio-only = light ---
    if music and Path(music).exists():
        mixed = workdir / "vaudio_mix.m4a"
        sh(["ffmpeg", "-y", "-i", str(narr), "-stream_loop", "-1", "-i", str(music),
            "-filter_complex",
            "[1:a]volume=0.12,apad[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
            "-map", "[a]", "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "44100",
            str(mixed)])
        audio = mixed
    else:
        audio = narr

    # --- light A/V mux first (video stream-copied, already 720x1280) ---
    av = workdir / "vav.mp4"
    sh(["ffmpeg", "-y", "-i", str(vcat), "-i", str(audio),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "44100",
        "-shortest", str(av)])

    # --- subtitle burn (the memory-heavy step): vertical-safe styling ---
    # ASS with PlayRes=720x1280 (see build_ass_vertical) — MarginV is exact
    # pixels here; Noto Sans Arabic covers Urdu/Arabic script.
    ass = build_ass_vertical(
        scenes, workdir / "vsubs.ass",
        offset=INTRO_SECONDS if has_intro else 0.0)
    vf_final = f"subtitles='{ass}',setsar=1,format=yuv420p"  # already 720x1280 — no scale needed
    final = workdir / "vfinal.mp4"
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
