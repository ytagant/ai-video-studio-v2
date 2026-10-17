"use client";
import { Check } from "lucide-react";
import { motion } from "framer-motion";
import type { AgentState, AgentStatus } from "@/lib/types";

export interface Stage {
  key: string;
  label: string;
}

export const STAGES: Stage[] = [
  { key: "researcher", label: "Research" },
  { key: "director", label: "Script" },
  { key: "voice", label: "Review" },
  { key: "footage", label: "Assets" },
  { key: "visual", label: "Edit" },
  { key: "editor", label: "Mix" },
  { key: "publish", label: "Publish" },
];

function stageStatus(
  key: string, agents: Record<string, AgentState>, jobStatus: string | null, running: boolean,
): AgentStatus {
  if (key === "publish") {
    if (jobStatus === "done") return "done";
    if (jobStatus === "error") return "error";
    if (running && agents.editor?.status === "done") return "working";
    return "idle";
  }
  const a = agents[key];
  if (!a) return "idle";
  return a.status;
}

export default function Pipeline({
  agents, jobStatus, running,
}: {
  agents: Record<string, AgentState>;
  jobStatus: string | null;
  running: boolean;
}) {
  const doneCount = STAGES.filter((s) => stageStatus(s.key, agents, jobStatus, running) === "done").length;
  const pct = Math.round((doneCount / STAGES.length) * 100);

  return (
    <div className="relative px-1 py-2">
      {/* connecting line */}
      <div className="absolute left-6 right-6 top-[22px] h-[3px] rounded-full bg-white/10" />
      <div
        className="absolute left-6 top-[22px] h-[3px] rounded-full bg-gradient-to-r from-studio-gold to-orange-500 transition-all duration-700"
        style={{ width: `calc((100% - 48px) * ${pct / 100})` }}
      />
      <div className="relative grid grid-cols-7">
        {STAGES.map((s, i) => {
          const st = stageStatus(s.key, agents, jobStatus, running);
          return (
            <div key={s.key} className="flex flex-col items-center gap-1.5">
              <motion.div
                animate={st === "working" ? { scale: [1, 1.14, 1] } : { scale: 1 }}
                transition={st === "working" ? { repeat: Infinity, duration: 1.5 } : {}}
                className={`flex h-9 w-9 items-center justify-center rounded-full border-2 text-[12px] font-extrabold
                  ${st === "done"
                    ? "border-emerald-400 bg-emerald-400/15 text-emerald-300"
                    : st === "working"
                      ? "border-studio-gold bg-studio-gold/15 text-studio-gold shadow-glow"
                      : st === "error"
                        ? "border-red-500 bg-red-500/15 text-red-400"
                        : "border-white/15 bg-studio-card text-white/30"}`}
              >
                {st === "done" ? <Check className="h-4 w-4" strokeWidth={3} /> : i + 1}
              </motion.div>
              <div className={`text-[10px] font-semibold sm:text-[11px] ${
                st === "idle" ? "text-white/30" : st === "done" ? "text-emerald-300" : "text-white/80"
              }`}>
                {s.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
