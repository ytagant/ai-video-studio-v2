"use client";
import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import { CATEGORIES } from "@/lib/types";

export default function CategorySelector({
  selected,
  onSelect,
}: {
  selected: string;
  onSelect: (id: string) => void;
}) {
  return (
    <section className="rounded-2xl bg-studio-panel border border-white/5 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-bold text-lg">
          Choose a Category{" "}
          <span className="text-xs font-normal text-white/40 ml-1">
            the video will be made in this style
          </span>
        </h2>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {CATEGORIES.map((c) => {
          const active = c.id === selected;
          return (
            <motion.button
              key={c.id}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => onSelect(c.id)}
              className={`relative rounded-xl overflow-hidden border-2 text-left transition
                ${active ? "border-studio-gold shadow-[0_0_18px_rgba(245,185,66,0.35)]" : "border-white/10 hover:border-white/25"}`}
            >
              <img
                src={c.image}
                alt={c.label}
                className="w-full h-24 sm:h-28 object-cover"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/25 to-transparent" />
              {active && (
                <CheckCircle2 className="absolute top-2 right-2 w-5 h-5 text-studio-gold drop-shadow" />
              )}
              <div className="absolute bottom-0 left-0 right-0 p-2.5">
                <div className={`font-bold text-sm ${active ? "text-studio-gold" : "text-white"}`}>
                  {c.label}
                </div>
                <div className="text-[11px] text-white/60">{c.blurb}</div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </section>
  );
}
