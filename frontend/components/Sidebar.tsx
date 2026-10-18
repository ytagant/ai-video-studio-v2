"use client";
import { useState } from "react";
import {
  Activity, BarChart3, Check, Crown, Download, FolderDown, Headset,
  LayoutGrid, Settings, Star, Users, Video,
} from "lucide-react";
import { downloadUrl } from "@/lib/api";

export interface HistoryEntry {
  id: string;
  title: string;
}

const CONNECTIONS: { name: string; state: "connected" | "missing" | "optional" | "none" }[] = [
  { name: "Gemini", state: "connected" },
  { name: "Pixabay", state: "connected" },
  { name: "ElevenLabs", state: "connected" },
  { name: "Pexels", state: "missing" },
  { name: "Unsplash", state: "optional" },
  { name: "Claude", state: "optional" },
  { name: "Music", state: "none" },
];

const DOT: Record<string, string> = {
  connected: "bg-emerald-400",
  missing: "bg-amber-400",
  optional: "bg-slate-900/10",
  none: "bg-slate-900/10",
};

function SoonTip({ children }: { children: React.ReactNode }) {
  return (
    <span className="pointer-events-none absolute left-full top-1/2 z-50 ml-3 -translate-y-1/2 whitespace-nowrap rounded-lg border border-slate-200 bg-studio-card px-2.5 py-1 text-[11px] text-slate-600 opacity-0 shadow-xl transition-opacity group-hover:opacity-100">
      {children}
    </span>
  );
}

function NavItem({
  icon: Icon, label, active, badge, soon,
}: {
  icon: any; label: string; active?: boolean; badge?: string; soon?: boolean;
}) {
  return (
    <button
      className={`group relative flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition
        ${active
          ? "bg-gradient-to-r from-studio-gold to-amber-500 font-bold text-black shadow-glow"
          : "text-slate-500 hover:bg-slate-900/5 hover:text-slate-900"}`}
    >
      <Icon className="h-[18px] w-[18px] shrink-0" />
      <span className="truncate">{label}</span>
      {badge && (
        <span className={`ml-auto rounded-full px-2 py-0.5 text-[10px] font-bold ${active ? "bg-black/20 text-black" : "bg-slate-900/5 text-slate-500"}`}>
          {badge}
        </span>
      )}
      {soon && <SoonTip>Coming soon</SoonTip>}
    </button>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-2 px-2 text-[10px] font-bold tracking-[0.14em] text-slate-400">{title}</div>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

export default function Sidebar({ history }: { history: HistoryEntry[] }) {
  const [showOutput, setShowOutput] = useState(false);
  const [showConn, setShowConn] = useState(false);
  const connectedCount = CONNECTIONS.filter((c) => c.state === "connected").length;

  return (
    <aside className="hidden w-60 shrink-0 flex-col gap-5 overflow-y-auto border-r border-slate-200 bg-studio-deep px-4 py-5 lg:flex">
      {/* Brand */}
      <div className="flex items-center gap-3 px-1">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-studio-gold to-orange-600 shadow-glow">
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="white">
            <path d="M8 5.5v13l11-6.5z" />
          </svg>
        </div>
        <div>
          <div className="text-[17px] font-extrabold leading-tight text-amber-600">Video Studio</div>
          <div className="text-[11px] text-slate-400">AI Video Production</div>
        </div>
      </div>

      <Section title="CREATE">
        <NavItem icon={LayoutGrid} label="Studio" active />
        <NavItem icon={Video} label="Projects" badge="9" soon />
      </Section>

      <Section title="TOOLS">
        <NavItem icon={Activity} label="Activity" badge="10" soon />
        <NavItem icon={BarChart3} label="Analytics" soon />
        <NavItem icon={Star} label="Brand Kit" soon />
        <button
          onClick={() => setShowOutput(!showOutput)}
          className="flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-500 transition hover:bg-slate-900/5 hover:text-slate-900"
        >
          <FolderDown className="h-[18px] w-[18px] shrink-0" />
          <span className="truncate">Output Folder</span>
          {history.length > 0 && (
            <span className="ml-auto rounded-full bg-studio-gold/15 px-2 py-0.5 text-[10px] font-bold text-amber-600">
              {history.length}
            </span>
          )}
        </button>
        {showOutput && (
          <div className="ml-4 space-y-1 border-l border-slate-200 pl-3 pt-1">
            {history.length === 0 && (
              <div className="px-2 py-1 text-[11px] text-slate-400">No videos yet</div>
            )}
            {history.slice(0, 6).map((h) => (
              <a
                key={h.id}
                href={downloadUrl(h.id)}
                className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-[11px] text-slate-500 transition hover:bg-slate-900/5 hover:text-slate-900"
                title={h.title}
              >
                <Download className="h-3 w-3 shrink-0 text-amber-600/70" />
                <span className="truncate">{h.title}</span>
              </a>
            ))}
          </div>
        )}
      </Section>

      <Section title="BUSINESS">
        <NavItem icon={Users} label="Customers" soon />
      </Section>

      <Section title="ACCOUNT">
        <NavItem icon={Settings} label="Settings" soon />
        <NavItem icon={Crown} label="Membership" soon />
        <NavItem icon={Headset} label="Help & Support" soon />
      </Section>

      {/* Connections */}
      <div>
        <button
          onClick={() => setShowConn(!showConn)}
          className="flex w-full items-center gap-2 rounded-xl px-2.5 py-2 text-[12px] transition hover:bg-slate-900/5"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
          <span className="font-semibold text-slate-600">Connections</span>
          <span className="ml-auto rounded-full bg-emerald-400/10 px-2 py-0.5 text-[10px] font-bold text-emerald-600">
            {connectedCount} connected
          </span>
        </button>
        {showConn && (
          <div className="mt-1 space-y-0.5">
            {CONNECTIONS.map((c) => (
              <div key={c.name} className="flex items-center gap-2.5 rounded-lg px-2.5 py-1.5 text-[12px]">
                <span className={`h-1.5 w-1.5 rounded-full ${DOT[c.state]}`} />
                <span className="text-slate-600">{c.name}</span>
                <span className="ml-auto text-[11px] capitalize text-slate-400">{c.state}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Owner mode panel */}
      <div className="mt-auto rounded-2xl border border-studio-gold/40 bg-gradient-to-b from-studio-gold/10 to-transparent p-4">
        <div className="mb-1 flex items-center gap-1.5 text-[13px] font-extrabold text-amber-600">
          <Crown className="h-4 w-4" /> Owner mode
        </div>
        <div className="mb-2.5 text-[11px] text-slate-500">Everything unlocked</div>
        <ul className="mb-3 space-y-1.5 text-[11px] text-slate-600">
          {["Unlimited videos", "All styles & AI models", "Issue customer keys"].map((t) => (
            <li key={t} className="flex items-center gap-2">
              <Check className="h-3 w-3 shrink-0 text-amber-600" /> {t}
            </li>
          ))}
        </ul>
        <button
          title="Coming soon"
          className="group relative w-full rounded-xl bg-gradient-to-r from-studio-gold to-amber-500 py-2 text-[12px] font-extrabold text-black transition hover:brightness-110"
        >
          Manage customers →
          <SoonTip>Coming soon</SoonTip>
        </button>
      </div>
    </aside>
  );
}
