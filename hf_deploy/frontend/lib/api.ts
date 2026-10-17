// Same-origin by default (backend serves the frontend in deployment).
// Override with NEXT_PUBLIC_API_BASE for split dev setup.
function apiBase(): string {
  const env = process.env.NEXT_PUBLIC_API_BASE;
  if (env) return env;
  if (typeof window !== "undefined") return window.location.origin;
  return "";
}
function wsBase(): string {
  const env = process.env.NEXT_PUBLIC_WS_BASE;
  if (env) return env;
  if (typeof window !== "undefined") {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${proto}//${window.location.host}`;
  }
  return "";
}
export const API_BASE = apiBase();
export const WS_BASE = wsBase();

export interface JobParams {
  topic: string;
  duration: number;
  language: string;
  style: string;
  category?: string;
  voice: string;
}

export async function createJob(params: JobParams): Promise<{ job_id: string }> {
  const r = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function reeditJob(jobId: string, instruction: string) {
  const r = await fetch(`${API_BASE}/api/jobs/${jobId}/reedit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ instruction }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export function downloadUrl(jobId: string) {
  return `${API_BASE}/api/jobs/${jobId}/download`;
}
