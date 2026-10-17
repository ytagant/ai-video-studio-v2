"use client";
import { Bell, Crown, HelpCircle, LayoutGrid, Search, Sun } from "lucide-react";

export default function TopBar({
  running, agentsDone, progress, jobId,
}: {
  running: boolean;
  agentsDone: number;
  progress: number;
  jobId: string | null;
}) {
  return (
    <div className="flex items-center gap-3 border-b border-white/5 bg-studio-deep/60 px-4 py-3 lg:px-6">
      {/* mobile brand */}
      <div className="flex items-center gap-2 lg:hidden">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-studio-gold to-orange-600">
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="white">
            <path d="M8 5.5v13l11-6.5z" />
          </svg>
        </div>
        <span className="text-sm font-extrabold text-studio-gold">Video Studio</span>
      </div>

      {/* search */}
      <div className="relative mx-auto w-full max-w-xl">
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-white/30" />
        <input
          placeholder="Search your videos and projects..."
          className="w-full rounded-xl border border-white/10 bg-studio-input py-2.5 pl-10 pr-4 text-sm text-white/80 placeholder:text-white/25 outline-none transition focus:border-studio-gold/50"
        />
      </div>

      {/* pills + icons + owner */}
      <div className="ml-auto hidden items-center gap-2 md:flex">
        <span
          className={`rounded-full border px-3 py-1.5 text-[11px] font-bold ${
            running
              ? "border-studio-gold/50 bg-studio-gold/10 text-studio-gold"
              : "border-white/10 bg-white/5 text-white/40"
          }`}
        >
          {running ? "● In production" : "○ Idle"}
        </span>
        <span className="hidden rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-[11px] font-semibold text-white/50 xl:block">
          Unlimited videos
        </span>
        <span className="hidden items-center gap-1.5 rounded-full bg-gradient-to-r from-studio-gold to-amber-500 px-3 py-1.5 text-[11px] font-extrabold text-black lg:flex">
          <Crown className="h-3.5 w-3.5" /> Membership
        </span>
        <span className="hidden font-mono text-[11px] text-white/50 xl:block">
          {agentsDone}/6 · {Math.round(progress)}%
        </span>
        {jobId && (
          <span className="hidden font-mono text-[10px] text-white/25 2xl:block">
            {jobId.slice(0, 8)}
          </span>
        )}
        <div className="ml-1 hidden items-center gap-1 lg:flex">
          {[Bell, HelpCircle, Sun, LayoutGrid].map((Icon, i) => (
            <button
              key={i}
              title="Coming soon"
              className="rounded-full p-2 text-white/40 transition hover:bg-white/10 hover:text-white"
            >
              <Icon className="h-4 w-4" />
            </button>
          ))}
        </div>
        <div className="ml-1 hidden items-center gap-2 xl:flex">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-studio-gold to-orange-600 text-sm font-black text-black">
            O
          </div>
          <div className="leading-tight">
            <div className="text-[12px] font-bold text-white">Owner</div>
            <div className="text-[10px] text-white/40">Owner mode</div>
          </div>
        </div>
      </div>
    </div>
  );
}
