"use client";
import { useState } from "react";
import { Check, Copy, Download, Hash, Sparkles, Type } from "lucide-react";
import { JobMeta, Scene } from "@/lib/types";
import { downloadUrl, reeditJob } from "@/lib/api";

function CopyBtn({ text }: { text: string }) {
  const [ok, setOk] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setOk(true); setTimeout(() => setOk(false), 1500); }}
      className="p-1.5 rounded-md hover:bg-white/10 text-white/50 hover:text-white"
      title="Copy"
    >
      {ok ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
    </button>
  );
}

export default function Storyboard({
  jobId, scenes, meta, videoReady,
}: {
  jobId: string | null;
  scenes: Scene[];
  meta: JobMeta | null;
  videoReady: boolean;
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
    <section className="rounded-2xl bg-studio-panel border border-white/5 p-5">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <h2 className="font-bold text-lg">Storyboard</h2>
        {videoReady && jobId && (
          <a
            href={downloadUrl(jobId)}
            className="flex items-center gap-2 rounded-xl bg-emerald-500/15 border border-emerald-500/40
                       text-emerald-300 font-semibold px-4 py-2 text-sm hover:bg-emerald-500/25 transition"
          >
            <Download className="w-4 h-4" /> Download MP4
          </a>
        )}
      </div>

      {scenes.length === 0 && (
        <p className="text-white/35 text-sm py-8 text-center">
          No scenes yet — configure your video on the left and hit <b>Generate Video</b>.
        </p>
      )}

      {videoReady && jobId && (
        <div className="mb-5 rounded-xl overflow-hidden border border-white/10 bg-black">
          <video
            key={jobId}
            src={downloadUrl(jobId)}
            controls
            playsInline
            preload="metadata"
            className="w-full max-h-[420px]"
          />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {scenes.map((s, i) => (
          <div key={i} className="rounded-xl bg-studio-card border border-white/10 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-studio-gold bg-studio-gold/10 px-2 py-0.5 rounded">
                SCENE {i + 1}
              </span>
              <span className="text-[11px] text-white/40 font-mono">{s.seconds.toFixed(1)}s</span>
            </div>
            <p className="text-sm text-white/85 leading-relaxed line-clamp-4">{s.narration}</p>
            <div className="mt-3 space-y-1 text-[11px] text-white/40">
              <div className="truncate">🎬 {s.keywords}</div>
              {s.transition && <div>✂️ transition: {s.transition}</div>}
              {s.clip ? <div className="text-emerald-400/80">● stock footage</div>
                      : <div className="text-amber-400/80">● AI-painted visual</div>}
            </div>
          </div>
        ))}
      </div>

      {meta && (
        <div className="mt-5 rounded-xl bg-studio-card border border-white/10 p-4 space-y-3">
          <div className="flex items-start gap-2">
            <Type className="w-4 h-4 mt-0.5 text-studio-gold shrink-0" />
            <div className="flex-1">
              <div className="text-xs text-white/40 mb-0.5">Title</div>
              <div className="text-sm font-semibold flex items-center justify-between gap-2">
                <span>{meta.title}</span><CopyBtn text={meta.title} />
              </div>
            </div>
          </div>
          <div className="text-sm text-white/60 flex items-start justify-between gap-2">
            <span className="line-clamp-3">{meta.description}</span>
            <CopyBtn text={meta.description} />
          </div>
          <div className="flex items-start gap-2">
            <Hash className="w-4 h-4 mt-0.5 text-studio-gold shrink-0" />
            <div className="flex flex-wrap gap-1.5 flex-1">
              {meta.hashtags.map((h) => (
                <span key={h} className="text-[11px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-white/60">{h}</span>
              ))}
            </div>
            <CopyBtn text={meta.hashtags.join(" ")} />
          </div>
        </div>
      )}

      {jobId && scenes.length > 0 && (
        <div className="mt-5 flex gap-2">
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && doReedit()}
            placeholder="Re-edit with AI… e.g. make narration more dramatic"
            className="flex-1 rounded-xl bg-studio-card border border-white/10 px-4 py-2.5 text-sm outline-none focus:border-studio-gold/60"
          />
          <button
            onClick={doReedit}
            disabled={reediting || !prompt.trim()}
            className="flex items-center gap-2 rounded-xl bg-studio-gold/15 border border-studio-gold/40
                       text-studio-gold font-semibold px-4 text-sm hover:bg-studio-gold/25 disabled:opacity-40"
          >
            <Sparkles className="w-4 h-4" /> {reediting ? "Working…" : "Re-edit"}
          </button>
        </div>
      )}
    </section>
  );
}
