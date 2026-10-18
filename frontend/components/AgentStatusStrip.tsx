"use client";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { AGENT_DEFS } from "@/lib/types";
import type { AgentState } from "@/lib/types";

const DOT: Record<string, string> = {
  researcher: "bg-studio-gold",
  director: "bg-purple-400",
  voice: "bg-emerald-400",
  footage: "bg-blue-400",
  visual: "bg-pink-400",
  editor: "bg-red-400",
};

const BAR: Record<string, string> = {
  researcher: "bg-studio-gold",
  director: "bg-purple-400",
  voice: "bg-emerald-400",
  footage: "bg-blue-400",
  visual: "bg-pink-400",
  editor: "bg-red-400",
};

export default function AgentStatusStrip({ agents }: { agents: Record<string, AgentState> }) {
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-6">
      {AGENT_DEFS.map((def) => {
        const st = agents[def.id] ?? { status: "idle", progress: 0, message: "Waiting…" };
        const working = st.status === "working";
        return (
          <div
            key={def.id}
            className={`rounded-xl border bg-studio-card px-3 py-2.5 transition ${
              working ? "border-studio-gold/40" : "border-slate-200"
            }`}
          >
            <div className="flex items-center gap-1.5">
              <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT[def.id]}`} />
              <span className="truncate text-[11px] font-bold text-slate-700">{def.label}</span>
              {working && <Loader2 className="ml-auto h-3 w-3 shrink-0 animate-spin text-amber-600" />}
              {st.status === "done" && <CheckCircle2 className="ml-auto h-3 w-3 shrink-0 text-emerald-600" />}
              {st.status === "error" && <XCircle className="ml-auto h-3 w-3 shrink-0 text-red-600" />}
            </div>
            <div className="mt-1 truncate text-[10px] text-slate-400">{st.message}</div>
            <div className="mt-1.5 h-1 rounded-full bg-slate-900/5">
              <div
                className={`h-full rounded-full transition-all duration-500 ${st.status === "done" ? "bg-emerald-400" : BAR[def.id]}`}
                style={{ width: `${st.progress}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
