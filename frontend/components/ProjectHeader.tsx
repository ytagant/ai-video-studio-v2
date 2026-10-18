"use client";

export default function ProjectHeader({
  title,
  meta,
  workingCount,
  doneCount,
  elapsed,
}: {
  title: string | null;
  meta: string;
  workingCount: number;
  doneCount: number;
  elapsed: string | null;
}) {
  return (
    <div className="flex flex-wrap items-start gap-3">
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-[17px] font-extrabold text-slate-900">
          {title || "No active production"}
        </h1>
        <div className="mt-0.5 text-[11px] text-slate-400">{meta}</div>
      </div>
      <div className="flex items-center gap-5 text-right">
        <div>
          <div className="font-mono text-[15px] font-extrabold text-slate-900">{workingCount}</div>
          <div className="text-[10px] tracking-wide text-slate-400">WORKING</div>
        </div>
        <div>
          <div className="font-mono text-[15px] font-extrabold text-slate-900">{doneCount}/6</div>
          <div className="text-[10px] tracking-wide text-slate-400">DONE</div>
        </div>
        <div>
          <div className="font-mono text-[15px] font-extrabold text-slate-900">{elapsed || "0:00"}</div>
          <div className="text-[10px] tracking-wide text-slate-400">ELAPSED</div>
        </div>
      </div>
    </div>
  );
}
