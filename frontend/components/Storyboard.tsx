"use client";
import { useState } from "react";
import { Check, Copy, Download, Film, Hash, Sparkles, Type } from "lucide-react";
import { CATEGORIES, JobMeta, Scene } from "@/lib/types";
import { downloadUrl, reeditJob } from "@/lib/api";
import ThumbnailPreview from "./ThumbnailPreview";

function CopyBtn({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setOk(true); setTimeout(() => setOk(false), 1500); }}
      className="rounded-md p-1.5 text-slate-500 transition hover:bg-slate-900/5 hover:text-slate-900"
      title="Copy"
    >
      {ok ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
    </button>
  );
}

function thumbFor(category: string | null): string {
  const c = CATEGORIES.find((x) => x.id === category);
  return c ? c.image : "/categories/documentary.jpg";
}

export default function Storyboard({
  jobId, scenes, meta, videoReady, category,
}: {
  jobId: string | null;
  scenes: Scene[];
  meta: JobMeta | null;
  videoReady: boolean;
  category: string | null;
}) {
  const [prompt, setPrompt] = useState("");
  const [reediting, setReediting] = useState(false);

  const doReedit = async () => {
    if (!jobId || !prompt.trim() || reediting) return;
    setReediting(true);
    try { await reeditJob(jobId, prompt.trim()); setPrompt(""); }
    catch (e) { alert("Re-edit failed: " + e); }
    finally { setReediting(false); }
  };

  return (
    <section className="rounded-2xl border border-slate-200 bg-studio-panel p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-[15px] font-extrabold text-slate-900">Storyboard</h2>
        <div className="flex items-center gap-3">
          <div className="hidden gap-1.5 text-[10px] font-bold text-slate-400 sm:flex">
            {["STOCK", "REAL", "ARCHIVE", "AI"].map((t) => (
              <span key={t} className="rounded border border-slate-200 px-1.5 py-0.5">{t}</span>
            ))}
          </div>
          {videoReady && jobId && (
            <a
              href={downloadUrl(jobId)}
              className="flex items-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/15 px-4 py-2 text-sm font-bold text-emerald-600 transition hover:bg-emerald-500/25"
            >
              <Download className="h-4 w-4" /> Download MP4
            </a>
          )}
        </div>
      </div>

      {scenes.length === 0 && (
        <p className="py-8 text-center text-sm text-slate-400">
          Each scene appears here as soon as the script is ready
        </p>
      )}

      {videoReady && jobId && (
        <div className="mb-5 overflow-hidden rounded-xl border border-slate-200 bg-black">
          <video
            key={jobId}
            src={downloadUrl(jobId)}
            controls
            playsInline
            preload="metadata"
            className="max-h-[380px] w-full"
          />
        </div>
      )}

      {videoReady && jobId && (
        <div className="mb-5">
          <ThumbnailPreview jobId={jobId} />
        </div>
      )}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {scenes.map((s, i) => (
          <div key={i} className="overflow-hidden rounded-xl border border-slate-200 bg-studio-card">
            <div className="relative">
              <img src={thumbFor(category)} alt={`Scene ${i + 1}`} className="h-24 w-full object-cover" loading="lazy" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
              <span className="absolute left-2.5 top-2.5 rounded-md bg-studio-gold px-2 py-0.5 text-[10px] font-extrabold text-black">
                SCENE {i + 1}
              </span>
              <span className="absolute bottom-2 right-2.5 font-mono text-[10px] text-slate-600">
                {s.seconds.toFixed(1)}s
              </span>
              {s.clip_source && (
                <span className="absolute bottom-2 left-2.5 flex items-center gap-1 rounded-md bg-black/60 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-600">
                  <Film className="h-3 w-3" /> {s.clip_source}
                </span>
              )}
            </div>
            <div className="p-3.5">
              <p className="line-clamp-3 text-[13px] leading-relaxed text-slate-700">{s.narration}</p>
              <div className="mt-2 truncate text-[11px] text-slate-400">🎬 {s.keywords}</div>
            </div>
          </div>
        ))}
      </div>

      {meta && (
        <div className="mt-4 space-y-3 rounded-xl border border-slate-200 bg-studio-card p-4">
          <div className="flex items-start gap-2">
            <Type className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
            <div className="flex-1">
              <div className="mb-0.5 text-xs text-slate-400">Title</div>
              <div className="flex items-center justify-between gap-2 text-sm font-bold text-slate-900">
                <span>{meta.title}</span><CopyBtn text={meta.title} />
              </div>
            </div>
          </div>
          <div className="flex items-start justify-between gap-2 text-sm text-slate-500">
            <span className="line-clamp-3">{meta.description}</span>
            <CopyBtn text={meta.description} />
          </div>
          <div className="flex items-start gap-2">
            <Hash className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
            <div className="flex flex-1 flex-wrap gap-1.5">
              {meta.hashtags.map((h) => (
                <span key={h} className="rounded-full border border-slate-200 bg-slate-900/5 px-2 py-0.5 text-[11px] text-slate-500">{h}</span>
              ))}
            </div>
            <CopyBtn text={meta.hashtags.join(" ")} />
          </div>
          {meta.credits && (
            <div className="flex items-center gap-1.5 border-t border-slate-200 pt-2.5 text-[11px] text-slate-400">
              <span>🎬</span><span>{meta.credits}</span>
            </div>
          )}
        </div>
      )}

      {jobId && scenes.length > 0 && (
        <div className="mt-4 flex gap-2">
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && doReedit()}
            placeholder="Re-edit with AI… e.g. make narration more dramatic"
            className="flex-1 rounded-xl border border-slate-200 bg-studio-input px-4 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 outline-none transition focus:border-studio-gold/60"
          />
          <button
            onClick={doReedit}
            disabled={reediting || !prompt.trim()}
            className="flex items-center gap-2 rounded-xl border border-studio-gold/40 bg-studio-gold/15 px-4 text-sm font-bold text-amber-600 transition hover:bg-studio-gold/25 disabled:opacity-40"
          >
            <Sparkles className="h-4 w-4" /> {reediting ? "Working…" : "Re-edit"}
          </button>
        </div>
      )}
    </section>
  );
}
