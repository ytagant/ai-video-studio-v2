"use client";
import { useEffect, useState } from "react";
import { API_BASE } from "@/lib/api";

export interface StyleDef {
  id: string;
  name: string;
  name_ur: string;
  blurb: string;
  color: string;
}

/** Offline fallback — ids must match backend GET /api/styles exactly. */
export const FALLBACK_STYLES: StyleDef[] = [
  { id: "documentary", name: "Documentary", name_ur: "دستاویزی", blurb: "Netflix/BBC style: calm narrator, facts, dates, cinematic grade", color: "#0ea5e9" },
  { id: "cinematic", name: "Cinematic Explainer", name_ur: "سنیماٹک وضاحت", blurb: "Vox / Johnny Harris look: chapter labels, letterbox, fact cards", color: "#8b5cf6" },
  { id: "recreation", name: "3D Recreation", name_ur: "3D ری کریشن", blurb: "3D-style recreation scenes, red event clock, archive footage", color: "#f59e0b" },
  { id: "storytelling", name: "Storytelling / Kahani", name_ur: "کہانی", blurb: "Warm storyteller tone, folk tales and moral stories", color: "#ec4899" },
  { id: "tech", name: "Tech / Science", name_ur: "ٹیک / سائنس", blurb: "How things work — explained simply with crisp visuals", color: "#06b6d4" },
  { id: "kids", name: "Kids / Educational", name_ur: "بچوں کا", blurb: "Playful, bright and simple — learning made fun", color: "#22c55e" },
  { id: "history", name: "History / Islamic History", name_ur: "اسلامی تاریخ", blurb: "Golden-age tales, heritage and timeless lessons", color: "#b45309" },
  { id: "facts", name: "Facts / Top 10", name_ur: "ٹاپ 10 حقائق", blurb: "Rapid-fire facts and countdown lists that hook viewers", color: "#eab308" },
  { id: "mystery", name: "Mystery / Unsolved", name_ur: "پراسرار", blurb: "Dark cases, unsolved files and eerie reveals", color: "#6366f1" },
  { id: "motivational", name: "Motivational", name_ur: "موٹیویشنل", blurb: "Rise-and-triumph stories with powerful pacing", color: "#f97316" },
  { id: "newsroom", name: "Newsroom", name_ur: "نیوز روم", blurb: "TV-news feel: red straps, breaking banners, clean facts", color: "#ef4444" },
];

export default function StylePicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (id: string) => void;
}) {
  const [styles, setStyles] = useState<StyleDef[]>(FALLBACK_STYLES);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/styles`);
        if (!r.ok) throw new Error("styles fetch failed");
        const data = await r.json();
        if (live && Array.isArray(data) && data.length > 0) setStyles(data);
      } catch {
        /* fallback list already in place */
      } finally {
        if (live) setLoading(false);
      }
    })();
    return () => {
      live = false;
    };
  }, []);

  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500">Style</span>
        {loading && <span className="text-[10px] text-slate-400">loading…</span>}
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {styles.map((s) => {
          const active = s.id === value;
          return (
            <button
              key={s.id}
              type="button"
              onClick={() => onChange(s.id)}
              aria-pressed={active}
              className={`overflow-hidden rounded-xl border-2 bg-white text-left transition ${
                active
                  ? "border-amber-500 shadow-[0_0_0_3px_rgba(245,158,11,0.18)]"
                  : "border-slate-200 hover:border-slate-300"
              }`}
            >
              <div className="h-1.5 w-full" style={{ backgroundColor: s.color }} />
              <div className="p-2.5">
                <div
                  className={`text-[12px] font-bold leading-tight ${
                    active ? "text-amber-700" : "text-slate-800"
                  }`}
                >
                  {s.name}
                </div>
                <div className="text-[10px] text-slate-400">{s.name_ur}</div>
                <div className="mt-1 text-[10px] leading-snug text-slate-500">{s.blurb}</div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
