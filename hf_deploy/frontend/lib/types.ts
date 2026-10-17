export type AgentStatus = "idle" | "working" | "done" | "error";

export interface AgentState {
  status: AgentStatus;
  progress: number;
  message: string;
}

export interface Scene {
  narration: string;
  keywords: string;
  seconds: number;
  transition?: string;
  screen_text?: string;
  music_mood?: string;
  audio?: string;
  clip?: string | null;
  image?: string | null;
}

export interface JobMeta {
  title: string;
  description: string;
  hashtags: string[];
}

export interface AgentDef {
  id: string;
  label: string;
  blurb: string;
  icon: string; // lucide icon key used by ProductionFloor
}

export const AGENT_DEFS: AgentDef[] = [
  { id: "researcher", label: "Researcher & Writer", blurb: "Script & scenes", icon: "search" },
  { id: "director", label: "Director", blurb: "Shots & pacing", icon: "clapperboard" },
  { id: "voice", label: "Voice & Sound", blurb: "TTS narration", icon: "mic" },
  { id: "footage", label: "Footage Hunter", blurb: "Stock clips", icon: "film" },
  { id: "visual", label: "Visual Artist", blurb: "AI fallback visuals", icon: "palette" },
  { id: "editor", label: "Editor", blurb: "FFmpeg render", icon: "scissors" },
];

export function idleAgents(): Record<string, AgentState> {
  const m: Record<string, AgentState> = {};
  for (const a of AGENT_DEFS) m[a.id] = { status: "idle", progress: 0, message: "Waiting…" };
  return m;
}

export interface CategoryDef {
  id: string;
  label: string;
  blurb: string;
  image: string;
}

export const CATEGORIES: CategoryDef[] = [
  { id: "Anime", label: "Anime", blurb: "Epic anime stories", image: "/categories/anime.jpg" },
  { id: "Cartoon", label: "Cartoon", blurb: "Fun 3D cartoons", image: "/categories/cartoon.jpg" },
  { id: "Documentary", label: "Documentary", blurb: "Real-world stories", image: "/categories/documentary.jpg" },
  { id: "Horror", label: "Horror", blurb: "Mystery & dread", image: "/categories/horror.jpg" },
  { id: "Islamic History", label: "Islamic History", blurb: "Golden age tales", image: "/categories/islamic.jpg" },
  { id: "Kids", label: "Kids", blurb: "Learn & play", image: "/categories/kids.jpg" },
  { id: "Motivational", label: "Motivational", blurb: "Rise & triumph", image: "/categories/motivational.jpg" },
  { id: "Tech/Science", label: "Tech/Science", blurb: "Future explained", image: "/categories/tech.jpg" },
];
