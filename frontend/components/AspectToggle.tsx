"use client";
import { RectangleHorizontal, Smartphone, type LucideIcon } from "lucide-react";

export type Aspect = "16:9" | "9:16";

const OPTIONS: { id: Aspect; label: string; sub: string; icon: LucideIcon }[] = [
  { id: "16:9", label: "16:9", sub: "Long-form", icon: RectangleHorizontal },
  { id: "9:16", label: "9:16", sub: "Short", icon: Smartphone },
];

export default function AspectToggle({
  value,
  onChange,
}: {
  value: Aspect;
  onChange: (v: Aspect) => void;
}) {
  return (
    <div>
      <span className="mb-1.5 block text-xs font-semibold text-slate-500">Format</span>
      <div className="grid grid-cols-2 gap-1 rounded-xl bg-[#eef1f6] p-1">
        {OPTIONS.map((o) => {
          const Icon = o.icon;
          const active = value === o.id;
          return (
            <button
              key={o.id}
              type="button"
              onClick={() => onChange(o.id)}
              aria-pressed={active}
              className={`flex items-center justify-center gap-1.5 rounded-lg py-2 transition ${
                active
                  ? "bg-white text-amber-700 shadow"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="text-[12px] font-bold">{o.label}</span>
              <span className="text-[10px] font-medium text-slate-400">{o.sub}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
