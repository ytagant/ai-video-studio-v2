"use client";
import { useState } from "react";
import { Download, Image as ImageIcon } from "lucide-react";
import { API_BASE } from "@/lib/api";

export default function ThumbnailPreview({ jobId }: { jobId: string }) {
  const [failed, setFailed] = useState(false);
  const [loaded, setLoaded] = useState(false);

  // Backend may not serve a thumbnail yet — hide silently instead of
  // showing a broken image.
  if (failed) return null;

  const url = `${API_BASE}/api/jobs/${jobId}/thumbnail`;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-[12px] font-bold text-slate-800">
          <ImageIcon className="h-3.5 w-3.5 text-amber-600" />
          Thumbnail
        </span>
        <a
          href={url}
          download={`thumbnail-${jobId}.jpg`}
          className="flex items-center gap-1 rounded-lg border border-slate-200 bg-[#eef1f6] px-2.5 py-1 text-[11px] font-bold text-slate-700 transition hover:border-amber-500 hover:text-amber-700"
        >
          <Download className="h-3 w-3" />
          Download
        </a>
      </div>
      {!loaded && <div className="aspect-video w-full animate-pulse rounded-lg bg-slate-200" />}
      <img
        src={url}
        alt="Video thumbnail"
        onLoad={() => setLoaded(true)}
        onError={() => setFailed(true)}
        className={`w-full rounded-lg ${loaded ? "" : "hidden"}`}
      />
    </div>
  );
}
