"use client";
import { useEffect, useState } from "react";
import { Flame } from "lucide-react";
import { API_BASE } from "@/lib/api";

export interface TrendingItem {
  id: string;
  title: string;
  reason: string;
}

export default function TrendingRow({
  category,
  onPick,
}: {
  category: string;
  onPick: (title: string) => void;
}) {
  const [items, setItems] = useState<TrendingItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let live = true;
    setLoading(true);
    (async () => {
      try {
        const r = await fetch(
          `${API_BASE}/api/trending?category=${encodeURIComponent(category)}`
        );
        if (!r.ok) throw new Error("trending fetch failed");
        const data = await r.json();
        if (live) setItems(Array.isArray(data) ? data : []);
      } catch {
        if (live) setItems([]);
      } finally {
        if (live) setLoading(false);
      }
    })();
    return () => {
      live = false;
    };
  }, [category]);

  if (!loading && items.length === 0) return null;

  return (
    <div>
      <div className="mb-1 flex items-center gap-1 text-[11px] font-semibold text-slate-500">
        <Flame className="h-3 w-3 text-amber-600" />
        Trending in {category}
      </div>
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {loading
          ? [0, 1, 2].map((i) => (
              <div
                key={i}
                className="h-8 w-32 shrink-0 animate-pulse rounded-full bg-slate-200"
              />
            ))
          : items.map((t) => (
              <button
                key={t.id}
                type="button"
                title={t.reason || t.title}
                onClick={() => onPick(t.title)}
                className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-[11px] font-semibold text-slate-700 transition hover:border-amber-500 hover:text-amber-700"
              >
                {t.title}
              </button>
            ))}
      </div>
    </div>
  );
}
