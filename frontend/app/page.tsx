"use client";
import { useEffect, useRef, useState } from "react";
import Sidebar, { HistoryEntry } from "@/components/Sidebar";
import TopBar from "@/components/TopBar";
import Pipeline from "@/components/Pipeline";
import ProjectHeader from "@/components/ProjectHeader";
import NewVideoPanel from "@/components/NewVideoPanel";
import ProductionFloor from "@/components/ProductionFloor";
import AgentStatusStrip from "@/components/AgentStatusStrip";
import Storyboard from "@/components/Storyboard";
import { AgentState, JobMeta, Scene, idleAgents } from "@/lib/types";
import { JobParams, createJob, getJob } from "@/lib/api";

function fmtElapsed(ms: number): string {
  const s = Math.floor(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export default function Home() {
  const [agents, setAgents] = useState<Record<string, AgentState>>(idleAgents());
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [meta, setMeta] = useState<JobMeta | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [videoReady, setVideoReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState("Documentary");
  const [style, setStyle] = useState("cinematic");
  const [aspect, setAspect] = useState<"16:9" | "9:16">("16:9");
  const [language, setLanguage] = useState("English");
  const [jobTitle, setJobTitle] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => () => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (timerRef.current) clearInterval(timerRef.current);
  }, []);

  async function start(params: JobParams) {
    setError(null); setScenes([]); setMeta(null);
    setVideoReady(false); setAgents(idleAgents());
    setJobStatus(null); setJobTitle(params.topic.split("\n")[0].slice(0, 70));
    try {
      const { job_id } = await createJob(params);
      setJobId(job_id); setRunning(true); setJobStatus("running");
      const t0 = Date.now();
      setElapsed("0:00");
      if (timerRef.current) clearInterval(timerRef.current);
      timerRef.current = setInterval(() => setElapsed(fmtElapsed(Date.now() - t0)), 1000);

      // HTTP polling for progress (some free hosts block WebSockets).
      if (pollRef.current) clearInterval(pollRef.current);
      const applySnapshot = (job: any) => {
        if (job.agents) {
          setAgents((prev) => {
            const next = { ...prev };
            for (const [id, a] of Object.entries<any>(job.agents))
              next[id] = { ...next[id], status: a.status, progress: a.progress, message: a.message };
            return next;
          });
        }
        if (Array.isArray(job.scenes) && job.scenes.length) setScenes(job.scenes);
        if (job.metadata && job.metadata.title) setMeta(job.metadata);
        if (job.status) setJobStatus(job.status);
      };
      const stop = () => {
        if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
        if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
      };
      pollRef.current = setInterval(async () => {
        try {
          const job = await getJob(job_id);
          applySnapshot(job);
          if (job.status === "done") {
            stop(); setRunning(false); setVideoReady(true);
            const title = job.metadata?.title || params.topic.split("\n")[0].slice(0, 70);
            setHistory((h) => [{ id: job_id, title }, ...h].slice(0, 12));
          } else if (job.status === "error") {
            stop(); setRunning(false); setError(job.error || "Production failed");
          }
        } catch {
          // transient network hiccup — keep polling
        }
      }, 2500);
    } catch (e: any) {
      setError("Could not start job: " + (e?.message || e));
      setRunning(false);
    }
  }

  const agentVals = Object.values(agents);
  const workingCount = agentVals.filter((a) => a.status === "working").length;
  const doneCount = agentVals.filter((a) => a.status === "done").length;
  const avgProgress = Math.round(agentVals.reduce((s, a) => s + (a.progress || 0), 0) / 6);
  const metaLine = `${style.toLowerCase()} · ${language.toLowerCase()} · ${aspect} · ${avgProgress}%`;

  return (
    <div className="flex min-h-screen bg-studio-bg">
      <Sidebar history={history} />

      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar running={running} agentsDone={doneCount} progress={avgProgress} jobId={jobId} />

        <main className="mx-auto w-full max-w-[1560px] flex-1 p-4 lg:p-5">
          {error && (
            <div className="mb-4 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
            {/* left: new video brief */}
            <NewVideoPanel
              running={running}
              onStart={start}
              onCategoryChange={setCategory}
              onStyleChange={setStyle}
              onAspectChange={setAspect}
              onLanguageChange={setLanguage}
            />

            {/* main column */}
            <div className="min-w-0 space-y-4">
              <ProjectHeader
                title={jobTitle}
                meta={metaLine}
                workingCount={workingCount}
                doneCount={doneCount}
                elapsed={elapsed}
              />
              <div className="rounded-2xl border border-slate-200 bg-studio-panel px-4 pb-3 pt-4">
                <Pipeline agents={agents} jobStatus={jobStatus} running={running} />
              </div>
              <ProductionFloor agents={agents} />
              <AgentStatusStrip agents={agents} />
              <Storyboard
                jobId={jobId}
                scenes={scenes}
                meta={meta}
                videoReady={videoReady}
                category={category}
              />
            </div>
          </div>

          <footer className="pb-4 pt-4 text-center text-[11px] text-slate-400">
            Video Studio · six AI agents · FFmpeg engine
          </footer>
        </main>
      </div>
    </div>
  );
}
