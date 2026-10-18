"use client";
import { AGENT_DEFS, AgentState } from "@/lib/types";

const ACCENT: Record<string, string> = {
  researcher: "#d97706",
  director: "#8b5cf6",
  voice: "#10b981",
  footage: "#3b82f6",
  visual: "#ec4899",
  editor: "#ef4444",
};

const HOLO = "#0ea5e9";

function HoloContent({ id, progress }: { id: string; progress: number }) {
  const o = 0.8;
  const line = (x: number, y: number, w: number) => (
    <rect x={x} y={y} width={w} height={6} rx={3} fill={HOLO} opacity={o * 0.7} />
  );
  switch (id) {
    case "researcher":
      return (
        <g>
          {line(-58, 84, 96)}
          {line(-58, 98, 80)}
          {line(-58, 112, 104)}
          {[0, 1, 2].map((i) => (
            <circle key={i} cx={-34 + i * 16} cy={140} r={5} fill={HOLO} opacity={0.9}
              className="tdot" style={{ animationDelay: `${i * 0.25}s` }} />
          ))}
          {[38, 58, 46].map((h, i) => (
            <rect key={i} x={28 + i * 16} y={152 - h} width={10} height={h} rx={2} fill={HOLO} opacity={0.55} />
          ))}
        </g>
      );
    case "director":
      return (
        <g>
          {line(-58, 84, 90)}
          {[52, 76, 40, 88, 64].map((h, i) => (
            <rect key={i} x={-52 + i * 24} y={160 - h} width={14} height={h} rx={3} fill={HOLO} opacity={0.6} />
          ))}
          <rect x={-58} y={160} width={116} height={2} fill={HOLO} opacity={0.4} />
        </g>
      );
    case "voice":
      return (
        <g>
          <text x={-58} y={92} fontSize={11} fontWeight={800} fill={HOLO} opacity={0.9} letterSpacing={2}>
            LIVE
          </text>
          <text x={52} y={94} fontSize={13} fontWeight={800} fill="#d97706" textAnchor="end">
            {Math.round(progress)}%
          </text>
          {Array.from({ length: 9 }).map((_, i) => {
            const h = 14 + ((i * 37) % 34);
            return (
              <rect key={i} x={-56 + i * 13} y={132 - h / 2} width={7} height={h} rx={3.5}
                fill={i % 3 === 0 ? "#10b981" : HOLO} opacity={0.85}
                className="eq-bar" style={{ animationDelay: `${i * 0.13}s` }} />
            );
          })}
        </g>
      );
    case "footage":
      return (
        <g>
          {["#d97706", "#8b5cf6", "#10b981", "#3b82f6", "#ec4899"].map((c, i) => (
            <rect key={i} x={-58 + i * 24} y={86} width={18} height={18} rx={5} fill={c} opacity={0.85} />
          ))}
          {line(-58, 116, 100)}
          {line(-58, 130, 72)}
          {[30, 52, 40].map((h, i) => (
            <rect key={i} x={30 + i * 18} y={162 - h} width={12} height={h} rx={2} fill={HOLO} opacity={0.55} />
          ))}
        </g>
      );
    case "visual":
      return (
        <g>
          {line(-58, 84, 100)}
          {line(-58, 98, 66)}
          <rect x={-58} y={114} width={52} height={40} rx={6} fill="none" stroke={HOLO} strokeWidth={1.5} opacity={0.6} />
          <circle cx={-32} cy={134} r={9} fill="none" stroke="#ec4899" strokeWidth={2} opacity={0.8} />
          {[44, 62, 36, 54].map((h, i) => (
            <rect key={i} x={4 + i * 16} y={158 - h} width={10} height={h} rx={2} fill="#ec4899" opacity={0.55} />
          ))}
        </g>
      );
    default: // editor
      return (
        <g>
          {line(-58, 84, 88)}
          <rect x={-58} y={102} width={44} height={14} rx={4} fill="#d97706" opacity={0.7} />
          <rect x={-10} y={102} width={60} height={14} rx={4} fill={HOLO} opacity={0.5} />
          <rect x={54} y={102} width={30} height={14} rx={4} fill="#ef4444" opacity={0.7} />
          <rect x={-58} y={126} width={70} height={14} rx={4} fill={HOLO} opacity={0.4} />
          <rect x={16} y={126} width={50} height={14} rx={4} fill="#8b5cf6" opacity={0.6} />
          {line(-58, 150, 96)}
        </g>
      );
  }
}

function Plant({ x, y, s = 1 }: { x: number; y: number; s?: number }) {
  return (
    <g transform={`translate(${x},${y}) scale(${s})`}>
      <polygon points="-14,0 14,0 9,22 -9,22" fill="#7a4a28" />
      <ellipse cx={-10} cy={-16} rx={7} ry={16} fill="#3fae6a" transform="rotate(-24 -10 -16)" />
      <ellipse cx={0} cy={-22} rx={7} ry={20} fill="#4cc47a" />
      <ellipse cx={10} cy={-16} rx={7} ry={16} fill="#3fae6a" transform="rotate(24 10 -16)" />
    </g>
  );
}

function Robot({ id, label, x, state }: { id: string; label: string; x: number; state: AgentState }) {
  const accent = ACCENT[id];
  const working = state.status === "working";
  const done = state.status === "done";
  const visorFill = state.status === "error" ? "#f87171" : accent;

  return (
    <g>
      {/* floor shadow */}
      <ellipse cx={x} cy={492} rx={72} ry={10} fill="#0f172a" opacity={0.16} />

      {/* holographic screen */}
      <g>
        <rect x={x - 74} y={66} width={148} height={118} rx={10}
          fill="rgba(14,165,233,0.10)" stroke="rgba(14,165,233,0.45)" strokeWidth={1.5}
          className="holo" />
        <rect x={x - 74} y={66} width={148} height={118} rx={10} fill="none"
          stroke="rgba(14,165,233,0.22)" strokeWidth={5} />
        <HoloContent id={id} progress={state.progress} />
        <rect x={x - 70} y={70} width={140} height={3} rx={1.5} fill="rgba(14,165,233,0.6)"
          className={working ? "holo-scan" : ""} opacity={working ? 1 : 0} />
      </g>

      {/* robot body — animates only when working */}
      <g className={working ? "bot-working" : ""}>
        {/* arms */}
        <rect x={x - 54} y={352} width={17} height={46} rx={8.5} fill="#dfe5ef" stroke="#94a3b8" strokeWidth={1.5} />
        <rect x={x + 37} y={352} width={17} height={46} rx={8.5} fill="#dfe5ef" stroke="#94a3b8" strokeWidth={1.5} />
        {/* torso */}
        <rect x={x - 37} y={332} width={74} height={88} rx={26} fill="#eef1f6" stroke="#94a3b8" strokeWidth={2} />
        <circle cx={x} cy={388} r={7.5} fill={accent} className={working ? "blink" : ""} opacity={0.9} />
        <rect x={x - 20} y={402} width={40} height={6} rx={3} fill="#d4dae6" />
        {/* head */}
        <rect x={x - 31} y={276} width={62} height={56} rx={24} fill="#f4f6fa" stroke="#94a3b8" strokeWidth={2} />
        {/* antenna */}
        <line x1={x} y1={276} x2={x} y2={262} stroke="#9aa5bb" strokeWidth={3} strokeLinecap="round" />
        <circle cx={x} cy={258} r={5} fill={accent} opacity={working ? 1 : 0.55}
          className={working ? "blink" : ""} />
        {/* visor */}
        <rect x={x - 25} y={292} width={50} height={21} rx={10.5} fill={visorFill} className="visor" />
        <rect x={x - 15} y={297} width={11} height={11} rx={5.5} fill="rgba(0,0,0,0.55)" />
        <rect x={x + 4} y={297} width={11} height={11} rx={5.5} fill="rgba(0,0,0,0.55)" />
        {/* done badge */}
        {done && (
          <g>
            <circle cx={x + 46} cy={288} r={14} fill="#10b981" stroke="#064e3b" strokeWidth={2} />
            <path d={`M${x + 39} 288 l5 5 l9 -10`} stroke="#fff" strokeWidth={3} fill="none"
              strokeLinecap="round" strokeLinejoin="round" />
          </g>
        )}
      </g>

      {/* desk */}
      <rect x={x - 90} y={414} width={180} height={17} rx={7} fill="#8a5a33" stroke="#5e3c20" strokeWidth={1.5} />
      <rect x={x - 82} y={431} width={14} height={48} fill="#3a2a1a" />
      <rect x={x + 68} y={431} width={14} height={48} fill="#3a2a1a" />
      {/* laptop */}
      <rect x={x + 16} y={404} width={56} height={10} rx={3} fill="#1a2233" />
      <rect x={x + 20} y={370} width={48} height={34} rx={4} fill={accent} opacity={0.9} stroke="#0d1420" strokeWidth={2} />
      <rect x={x + 20} y={370} width={48} height={34} rx={4} fill="url(#screenSheen)" />

      {/* name label */}
      <text x={x} y={516} textAnchor="middle" fontSize={14.5} fontWeight={800} fill={accent}
        fontFamily="ui-sans-serif, system-ui, sans-serif">
        {label}
      </text>
    </g>
  );
}

export default function ProductionFloor({ agents }: { agents: Record<string, AgentState> }) {
  const workingCount = AGENT_DEFS.filter((a) => agents[a.id]?.status === "working").length;
  const doneCount = AGENT_DEFS.filter((a) => agents[a.id]?.status === "done").length;
  const xs = [104, 302, 500, 698, 896, 1094];

  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200 bg-studio-panel">
      <div className="flex items-center justify-between px-5 pt-4">
        <h2 className="text-[15px] font-extrabold text-slate-900">
          Production floor{" "}
          <span className="ml-1 text-[11px] font-normal text-slate-400">
            {workingCount > 0
              ? `${workingCount} working · ${doneCount} done`
              : doneCount === AGENT_DEFS.length
                ? "all done"
                : doneCount > 0 ? `${doneCount} done` : "standing by"}
          </span>
        </h2>
        <div className="flex items-center gap-3 text-[10px] text-slate-400">
          <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-slate-900/10" /> Idle</span>
          <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-studio-gold" /> Working</span>
          <span className="flex items-center gap-1"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Done</span>
        </div>
      </div>

      <div className="px-3 pb-1">
        <svg viewBox="0 0 1200 540" className="h-auto w-full" role="img" aria-label="AI agents production floor">
          <defs>
            <linearGradient id="roomGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#ffffff" />
              <stop offset="0.75" stopColor="#eef2f7" />
              <stop offset="1" stopColor="#dde5ef" />
            </linearGradient>
            <linearGradient id="screenSheen" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#fff" stopOpacity="0.35" />
              <stop offset="0.5" stopColor="#fff" stopOpacity="0" />
            </linearGradient>
            <filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
              <feGaussianBlur stdDeviation="10" />
            </filter>
          </defs>

          {/* room */}
          <rect x={0} y={0} width={1200} height={540} fill="url(#roomGrad)" />
          {/* wooden slat wall, right */}
          {Array.from({ length: 9 }).map((_, i) => (
            <rect key={i} x={1122 + i * 9} y={0} width={4.5} height={540}
              fill={i % 2 ? "#4a3320" : "#3a2818"} opacity={0.85} />
          ))}
          {/* ceiling light strips */}
          {[
            { x: 150, w: 230 }, { x: 500, w: 200 }, { x: 810, w: 250 },
          ].map((l, i) => (
            <g key={i}>
              <rect x={l.x} y={14} width={l.w} height={9} rx={4.5} fill="#f5a623"
                opacity={0.28} filter="url(#softGlow)" />
              <rect x={l.x} y={14} width={l.w} height={9} rx={4.5} fill="#f5a623" opacity={0.75} />
            </g>
          ))}
          {/* floor */}
          <rect x={0} y={486} width={1200} height={54} fill="#d7dee9" />
          <rect x={0} y={486} width={1200} height={2} fill="#0f172a" opacity={0.08} />

          {/* plants between robots */}
          <Plant x={203} y={486} s={0.9} />
          <Plant x={401} y={486} s={1.05} />
          <Plant x={599} y={486} s={0.9} />
          <Plant x={797} y={486} s={1.05} />
          <Plant x={995} y={486} s={0.9} />
          <Plant x={30} y={500} s={1.25} />
          <Plant x={1170} y={500} s={1.25} />

          {/* robots */}
          {AGENT_DEFS.map((def, i) => (
            <Robot
              key={def.id}
              id={def.id}
              label={def.label}
              x={xs[i]}
              state={agents[def.id] ?? { status: "idle", progress: 0, message: "" }}
            />
          ))}
        </svg>
      </div>
    </section>
  );
}
