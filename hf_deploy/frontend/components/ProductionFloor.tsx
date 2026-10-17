"use client";
import { motion } from "framer-motion";
import {
  Bot, CheckCircle2, Clapperboard, Film, Loader2, Mic, Palette, Search, Scissors, XCircle,
} from "lucide-react";
import { AGENT_DEFS, AgentState } from "@/lib/types";

const ICONS: Record<string, any> = {
  search: Search, clapperboard: Clapperboard, mic: Mic,
  film: Film, palette: Palette, scissors: Scissors,
};

const STATUS_STYLE: Record<string, string> = {
  idle: "border-white/10 text-white/40",
  working: "border-studio-gold/60 text-studio-gold",
  done: "border-emerald-500/50 text-emerald-400",
  error: "border-red-500/60 text-red-400",
};

function AgentCard({ def, state }: { def: (typeof AGENT_DEFS)[number]; state: AgentState }) {
  const Icon = ICONS[def.icon] ?? Bot;
  const working = state.status === "working";
  return (
    <motion.div
      animate={working ? { scale: [1, 1.03, 1] } : { scale: 1 }}
      transition={working ? { repeat: Infinity, duration: 1.6 } : {}}
      className={`rounded-2xl border bg-studio-card p-4 ${STATUS_STYLE[state.status]}`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0
          ${working ? "bg-studio-gold/20" : state.status === "done" ? "bg-emerald-500/15" : "bg-white/5"}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-semibold text-sm text-white truncate">{def.label}</div>
          <div className="text-[11px] opacity-70 truncate">{def.blurb}</div>
        </div>
        {state.status === "working" && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
        {state.status === "done" && <CheckCircle2 className="w-4 h-4 shrink-0" />}
        {state.status === "error" && <XCircle className="w-4 h-4 shrink-0" />}
      </div>

      <div className="mt-3 h-1.5 rounded-full bg-white/10 overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${state.status === "done" ? "bg-emerald-400" : "bg-studio-gold"}`}
          animate={{ width: `${state.progress}%` }}
          transition={{ ease: "easeOut", duration: 0.4 }}
        />
      </div>
      <div className="mt-2 flex items-center justify-between text-[11px]">
        <span className="opacity-70 truncate pr-2">{state.message}</span>
        <span className="font-mono shrink-0">{state.progress}%</span>
      </div>
    </motion.div>
  );
}

export default function ProductionFloor({ agents }: { agents: Record<string, AgentState> }) {
  const activeCount = AGENT_DEFS.filter((a) => agents[a.id]?.status === "working").length;
  const doneCount = AGENT_DEFS.filter((a) => agents[a.id]?.status === "done").length;
  return (
    <section className="rounded-2xl bg-studio-panel border border-white/5 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-bold text-lg">
          Production Floor{" "}
          <span className="text-xs font-normal text-white/40 ml-1">
            {activeCount > 0 ? `${activeCount} working` : doneCount === AGENT_DEFS.length ? "all done" : "idle"}
          </span>
        </h2>
        <div className="flex items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-full bg-studio-gold/15 text-studio-gold border border-studio-gold/30 font-semibold">
            ● In production
          </span>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {AGENT_DEFS.map((def) => (
          <AgentCard key={def.id} def={def} state={agents[def.id]} />
        ))}
      </div>
    </section>
  );
}
