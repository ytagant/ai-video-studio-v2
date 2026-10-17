"use client";
import { useState } from "react";
import { Clapperboard, KeyRound, Loader2, Mic, Settings2 } from "lucide-react";
import { JobParams } from "@/lib/api";

const LANGUAGES = ["English", "Urdu", "Hindi"];
const STYLES = ["Documentary", "3D Recreation", "Cinematic Explainer"];
const VOICES: Record<string, string[]> = {
  English: ["default", "en-US-AriaNeural", "en-US-GuyNeural"],
  Urdu: ["default", "ur-PK-AsadNeural", "ur-PK-UzmaNeural"],
  Hindi: ["default", "hi-IN-SwaraNeural", "hi-IN-MadhurNeural"],
};

export default function Sidebar({
  running,
  onStart,
}: {
  running: boolean;
  onStart: (p: JobParams) => void;
}) {
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState(60);
  const [language, setLanguage] = useState("English");
  const [style, setStyle] = useState(STYLES[0]);
  const [voice, setVoice] = useState("default");
  const [showKeys, setShowKeys] = useState(false);

  const submit = () => {
    if (!topic.trim() || running) return;
    onStart({ topic: topic.trim(), duration, language, style, voice });
  };

  const field =
    "w-full rounded-lg bg-studio-card border border-white/10 px-3 py-2 text-sm outline-none focus:border-studio-gold/60";

  return (
    <aside className="w-full lg:w-80 shrink-0 bg-studio-panel border-r border-white/5 p-5 flex flex-col gap-5 overflow-y-auto">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-studio-gold to-orange-600 flex items-center justify-center">
          <Clapperboard className="w-5 h-5 text-black" />
        </div>
        <div>
          <div className="font-bold text-lg leading-tight">
            Video <span className="text-studio-gold">Studio</span>
          </div>
          <div className="text-[11px] text-white/40">AI Video Production</div>
        </div>
      </div>

      <div>
        <label className="text-xs text-white/50 mb-1 block">Video title / topic</label>
        <input
          className={field}
          placeholder="e.g. The Amazon: World's Largest Rainforest"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
        />
      </div>

      <div>
        <label className="text-xs text-white/50 mb-1 block">
          Video length: <span className="text-studio-gold font-semibold">
            {duration >= 60 ? `${Math.floor(duration / 60)} min${duration % 60 ? ` ${duration % 60}s` : ""}` : `${duration}s`}
          </span>
        </label>
        <div className="flex gap-1.5 mb-2">
          {[60, 120, 180, 300, 600].map((m) => (
            <button
              key={m}
              onClick={() => setDuration(m)}
              className={`flex-1 text-[11px] font-semibold rounded-lg py-1.5 border transition
                ${duration === m
                  ? "bg-studio-gold/20 border-studio-gold text-studio-gold"
                  : "bg-studio-card border-white/10 text-white/50 hover:border-white/25"}`}
            >
              {m / 60}m
            </button>
          ))}
        </div>
        <input
          type="range" min={15} max={600} step={15} value={duration}
          onChange={(e) => setDuration(Number(e.target.value))}
          className="w-full accent-amber-400"
        />
        <div className="text-[10px] text-white/30 mt-1">Slide for fine-tuning (15s – 10 min)</div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-white/50 mb-1 block">Language</label>
          <select className={field} value={language}
            onChange={(e) => { setLanguage(e.target.value); setVoice("default"); }}>
            {LANGUAGES.map((l) => <option key={l}>{l}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-white/50 mb-1 block">Style</label>
          <select className={field} value={style} onChange={(e) => setStyle(e.target.value)}>
            {STYLES.map((s) => <option key={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className="text-xs text-white/50 mb-1 flex items-center gap-1">
          <Mic className="w-3 h-3" /> Voice
        </label>
        <select className={field} value={voice} onChange={(e) => setVoice(e.target.value)}>
          {VOICES[language].map((v) => <option key={v} value={v}>{v}</option>)}
        </select>
      </div>

      <button
        onClick={() => setShowKeys(!showKeys)}
        className="flex items-center gap-2 text-xs text-white/50 hover:text-white/80"
      >
        <KeyRound className="w-3.5 h-3.5" /> API connections
        <Settings2 className="w-3 h-3 ml-auto" />
      </button>
      {showKeys && (
        <div className="rounded-lg bg-studio-card border border-white/10 p-3 text-[11px] text-white/50 space-y-1">
          <p>Keys live in <code className="text-studio-gold">backend/.env</code>:</p>
          <p>• GEMINI_API_KEY — script writer</p>
          <p>• PEXELS_API_KEY / PIXABAY_API_KEY — footage</p>
          <p>• Edge-TTS voice needs no key</p>
        </div>
      )}

      <button
        onClick={submit}
        disabled={running || !topic.trim()}
        className="mt-auto rounded-xl bg-gradient-to-r from-studio-gold to-orange-500 text-black font-bold py-3
                   disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 transition flex items-center justify-center gap-2"
      >
        {running ? <><Loader2 className="w-4 h-4 animate-spin" /> Producing…</> : "Generate Video"}
      </button>
    </aside>
  );
}
