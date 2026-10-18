"use client";
import { useState } from "react";
import { ChevronDown, Clapperboard, Loader2, Mic } from "lucide-react";
import { CATEGORIES } from "@/lib/types";
import type { JobParams } from "@/lib/api";

// Displayed style cards -> backend-valid style values.
const STYLES: { id: string; backend: string; blurb: string; tag?: string }[] = [
  {
    id: "3D Recreation",
    backend: "3D Recreation",
    blurb: "3D-style recreation scenes, red event clock, archive footage",
    tag: "AI images need billing — stock footage used",
  },
  {
    id: "Cinematic explainer documentary",
    backend: "Cinematic Explainer",
    blurb: "Vox / Johnny Harris look: chapter labels, letterbox, fact and quote cards",
  },
  {
    id: "Documentary",
    backend: "Documentary",
    blurb: "Netflix / BBC style: calm narrator, facts, dates, cinematic grade",
  },
  {
    id: "Storytelling / Kahani",
    backend: "Documentary",
    blurb: "Warm storyteller tone, folk tales and moral stories",
  },
];

const LANGUAGES = ["English", "Urdu", "Hindi"];
const VOICE_MAP: Record<string, Record<string, string>> = {
  English: { Male: "en-US-GuyNeural", Female: "en-US-AriaNeural" },
  Urdu: { Male: "ur-PK-AsadNeural", Female: "ur-PK-UzmaNeural" },
  Hindi: { Male: "hi-IN-MadhurNeural", Female: "hi-IN-SwaraNeural" },
};

const field =
  "w-full rounded-xl bg-studio-input border border-slate-200 px-3.5 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 outline-none focus:border-studio-gold/60 transition";

function Toggle({ on, onChange, label, sub }: { on: boolean; onChange: (v: boolean) => void; label: string; sub?: string }) {
  return (
    <div className="flex items-start justify-between gap-3">
      <div>
        <div className="text-[12px] font-semibold text-slate-600">{label}</div>
        {sub && <div className="text-[10px] text-slate-400">{sub}</div>}
      </div>
      <button className="toggle" data-on={on} onClick={() => onChange(!on)} aria-label={label}>
        <span className="knob" />
      </button>
    </div>
  );
}

export default function NewVideoPanel({
  running,
  onStart,
  onCategoryChange,
  onStyleChange,
  onLanguageChange,
}: {
  running: boolean;
  onStart: (p: JobParams) => void;
  onCategoryChange: (c: string) => void;
  onStyleChange: (s: string) => void;
  onLanguageChange: (l: string) => void;
}) {
  const [topic, setTopic] = useState("");
  const [styleId, setStyleId] = useState(STYLES[1].id);
  const [category, setCategory] = useState("Documentary");
  const [language, setLanguage] = useState("English");
  const [gender, setGender] = useState<"Male" | "Female">("Male");
  const [duration, setDuration] = useState(60);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [toggles, setToggles] = useState({
    review: true,
    research: true,
    music: true,
    subtitles: true,
  });

  const submit = () => {
    if (!topic.trim() || running) return;
    const st = STYLES.find((s) => s.id === styleId)!;
    onStart({
      topic: topic.trim(),
      duration,
      language,
      style: st.backend,
      category,
      voice: VOICE_MAP[language][gender],
    });
  };

  const durLabel = duration >= 60 ? `${Math.floor(duration / 60)} min` : `${duration}s`;
  const fill = ((duration - 15) / (600 - 15)) * 100;

  const setT = (k: keyof typeof toggles) => (v: boolean) =>
    setToggles((t) => ({ ...t, [k]: v }));

  return (
    <section className="flex h-full flex-col rounded-2xl border border-slate-200 bg-studio-panel p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-[15px] font-extrabold text-slate-900">New video</h2>
        <span className="text-[11px] text-slate-400">Brief</span>
      </div>

      <div className="space-y-4">
        <div className="flex gap-2">
          <select className={field} defaultValue="none" aria-label="Brand profile">
            <option value="none">Brand profile: none</option>
          </select>
          <button title="Coming soon" className="shrink-0 rounded-xl border border-slate-200 bg-studio-input px-4 text-sm font-semibold text-slate-500 transition hover:border-studio-gold/40 hover:text-slate-900">
            Save
          </button>
        </div>

        <div>
          <label className="mb-1.5 block text-xs text-slate-500">What&apos;s the video about?</label>
          <textarea
            className={`${field} min-h-[76px] resize-y`}
            placeholder="e.g. The Billionaire's Mansion That Was Abandoned Overnight"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs text-slate-500">Style</label>
          <div className="space-y-2">
            {STYLES.map((s) => {
              const active = s.id === styleId;
              return (
                <button
                  key={s.id}
                  onClick={() => { setStyleId(s.id); onStyleChange(s.backend); }}
                  className={`block w-full rounded-xl border-2 p-3 text-left transition
                    ${active ? "border-studio-gold bg-studio-gold/5 shadow-glow" : "border-slate-200 bg-studio-card hover:border-slate-300"}`}
                >
                  <div className={`text-[13px] font-bold ${active ? "text-amber-600" : "text-slate-700"}`}>
                    {s.id}
                  </div>
                  <div className="mt-0.5 text-[11px] leading-snug text-slate-400">{s.blurb}</div>
                  {s.tag && (
                    <div className="mt-1.5 inline-block rounded-md bg-slate-900/5 px-1.5 py-0.5 text-[10px] text-slate-500">
                      {s.tag}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1.5 block text-xs text-slate-500">Language</label>
            <select className={field} value={language} onChange={(e) => { setLanguage(e.target.value); onLanguageChange(e.target.value); }}>
              {LANGUAGES.map((l) => <option key={l}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1.5 flex items-center gap-1 text-xs text-slate-500">
              <Mic className="h-3 w-3" /> Voice
            </label>
            <div className="grid grid-cols-2 gap-1 rounded-xl border border-slate-200 bg-studio-input p-1">
              {(["Male", "Female"] as const).map((g) => (
                <button
                  key={g}
                  onClick={() => setGender(g)}
                  className={`rounded-lg py-1.5 text-[12px] font-bold transition
                    ${gender === g ? "bg-studio-gold/20 text-amber-600" : "text-slate-500 hover:text-slate-900"}`}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div>
          <label className="mb-1.5 block text-xs text-slate-500">
            Duration: <span className="font-bold text-amber-600">{durLabel}</span>
          </label>
          <div className="mb-2 flex gap-1.5">
            {[60, 120, 180, 300, 600].map((m) => (
              <button
                key={m}
                onClick={() => setDuration(m)}
                className={`flex-1 rounded-lg border py-1.5 text-[11px] font-bold transition
                  ${duration === m
                    ? "border-studio-gold bg-studio-gold/15 text-amber-600"
                    : "border-slate-200 bg-studio-input text-slate-500 hover:border-slate-300"}`}
              >
                {m / 60}m
              </button>
            ))}
          </div>
          <input
            type="range" min={15} max={600} step={15} value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="studio-range w-full"
            style={{ ["--fill" as any]: `${fill}%` }}
          />
        </div>

        <div>
          <label className="mb-1.5 block text-xs text-slate-500">Format</label>
          <div className="grid grid-cols-2 gap-2">
            <button className="rounded-xl border-2 border-studio-gold bg-studio-gold/10 px-3 py-2.5 text-center">
              <div className="text-[12px] font-bold text-amber-600">Long-form 16:9</div>
            </button>
            <button
              disabled
              title="Coming soon"
              className="relative cursor-not-allowed rounded-xl border border-slate-200 bg-studio-input px-3 py-2.5 text-center opacity-50"
            >
              <div className="text-[12px] font-bold text-slate-500">Short 9:16</div>
              <span className="absolute right-2 top-2 rounded-full bg-slate-900/5 px-1.5 py-0.5 text-[9px] font-bold text-slate-400">soon</span>
            </button>
          </div>
        </div>

        <div className="space-y-2.5 border-t border-slate-200 pt-3">
          <Toggle on={toggles.review} onChange={setT("review")} label="Review plan before rendering" sub="Edit the script and scenes, then approve" />
          <Toggle on={toggles.research} onChange={setT("research")} label="Live Google research" />
          <Toggle on={toggles.music} onChange={setT("music")} label="Background music" />
          <Toggle on={toggles.subtitles} onChange={setT("subtitles")} label="Burned-in subtitles" />
        </div>

        <div className="border-t border-slate-200 pt-2">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex w-full items-center gap-1 py-1 text-[12px] font-semibold text-amber-600/80 transition hover:text-amber-600"
          >
            <ChevronDown className={`h-3.5 w-3.5 transition-transform ${showAdvanced ? "rotate-180" : ""}`} />
            Footage sources & advanced
          </button>
          {showAdvanced && (
            <div className="mt-2 space-y-1.5 rounded-xl border border-slate-200 bg-studio-card p-3 text-[11px]">
              <div className="flex items-center gap-2 text-slate-600">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Pixabay <span className="ml-auto text-slate-400">connected</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400" /> Pexels <span className="ml-auto text-slate-400">unavailable</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Wikimedia Commons <span className="ml-auto text-slate-400">fallback</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> ElevenLabs voice <span className="ml-auto text-slate-400">priority</span>
              </div>
            </div>
          )}
        </div>

        {/* hidden category sync — category comes from storyboard context default */}
        <div>
          <label className="mb-1.5 block text-xs text-slate-500">Category</label>
          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map((c) => (
              <button
                key={c.id}
                onClick={() => { setCategory(c.id); onCategoryChange(c.id); }}
                className={`rounded-lg border px-2.5 py-1.5 text-[11px] font-bold transition
                  ${category === c.id
                    ? "border-studio-gold bg-studio-gold/15 text-amber-600"
                    : "border-slate-200 bg-studio-input text-slate-500 hover:border-slate-300"}`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-5 space-y-2">
        <button
          onClick={submit}
          disabled={running || !topic.trim()}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-studio-gold to-orange-500 py-3 text-[15px] font-extrabold text-black transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {running ? (
            <><Loader2 className="h-4 w-4 animate-spin" /> Producing…</>
          ) : (
            <><Clapperboard className="h-4 w-4" /> Generate video</>
          )}
        </button>
        <button
          onClick={() => { if (!running) setTopic(""); }}
          className="w-full rounded-xl border border-slate-200 bg-studio-input py-2.5 text-sm font-bold text-red-600/80 transition hover:bg-slate-900/5"
        >
          Cancel
        </button>
      </div>
    </section>
  );
}

export { STYLES };
