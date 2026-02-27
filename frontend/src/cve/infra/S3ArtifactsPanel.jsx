import React, { useState, useCallback } from "react";
import {
  HardDrive, File, Folder, AlertTriangle, Search, ChevronRight
} from "lucide-react";

const getFileIcon = (key) => {
  if (key.endsWith("/")) return <Folder className="w-4 h-4 text-amber-400" />;
  if (key.match(/\.(zip|tar|gz)$/)) return <File className="w-4 h-4 text-violet-400" />;
  if (key.match(/\.(mp3|wav|aac|flac)$/)) return <File className="w-4 h-4 text-cyan-400" />;
  if (key.match(/\.(png|jpg|jpeg|webp|gif)$/)) return <File className="w-4 h-4 text-emerald-400" />;
  if (key.match(/\.(mp4|mov|avi)$/)) return <File className="w-4 h-4 text-red-400" />;
  return <File className="w-4 h-4 text-slate-400" />;
};

const getStorageClassBadge = (sc) => {
  const map = {
    STANDARD: "bg-emerald-500/15 text-emerald-300",
    INTELLIGENT_TIERING: "bg-cyan-500/15 text-cyan-300",
    GLACIER: "bg-blue-500/15 text-blue-300",
    DEEP_ARCHIVE: "bg-violet-500/15 text-violet-300",
  };
  return map[sc] || "bg-slate-600/30 text-slate-400";
};

export const S3ArtifactsPanel = ({ data, onNavigate }) => {
  const [filter, setFilter] = useState("");

  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;

  const filtered = (data.objects || []).filter(o =>
    !filter || o.key.toLowerCase().includes(filter.toLowerCase())
  );

  const prefixes = new Set();
  filtered.forEach(o => {
    const parts = o.key.split("/");
    if (parts.length > 1) prefixes.add(parts[0]);
  });

  return (
    <div className="space-y-4 pt-3" data-testid="s3-artifacts-panel">
      {/* Summary */}
      <div className="flex items-center gap-4 flex-wrap text-xs text-slate-400">
        <span className="flex items-center gap-1.5">
          <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-white font-semibold">{data.bucket}</span>
        </span>
        <span>{data.total_objects} object(s)</span>
        <span>{data.total_size_display}</span>
        {data.is_truncated && <span className="text-amber-400">(truncated — more objects exist)</span>}
        {data.prefix && (
          <span className="flex items-center gap-1 font-mono text-cyan-300">
            <ChevronRight className="w-3 h-3" />{data.prefix}
          </span>
        )}
      </div>

      {/* Filter */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          data-testid="s3-filter-input"
          type="text"
          placeholder="Filter objects..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-slate-900/60 border border-slate-700/50 rounded-lg text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-cyan-500/40"
        />
      </div>

      {/* Folder shortcuts */}
      {prefixes.size > 0 && (
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => onNavigate?.("")}
            data-testid="s3-prefix-root"
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              !data.prefix ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "bg-slate-800/60 text-slate-400 border border-slate-700/50 hover:border-slate-600"
            }`}
          >
            /root
          </button>
          {[...prefixes].sort().map(p => (
            <button
              key={p}
              onClick={() => onNavigate?.(p + "/")}
              data-testid={`s3-prefix-${p}`}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                data.prefix === p + "/" ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "bg-slate-800/60 text-slate-400 border border-slate-700/50 hover:border-slate-600"
              }`}
            >
              {p}/
            </button>
          ))}
        </div>
      )}

      {/* Objects */}
      <div className="space-y-1">
        {filtered.length === 0 && <div className="text-slate-500 text-sm">No objects found</div>}
        {filtered.map((o, i) => (
          <div key={i} data-testid={`s3-obj-${i}`} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-2.5">
            {getFileIcon(o.key)}
            <span className="text-sm text-slate-300 font-mono truncate flex-1">{o.key}</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${getStorageClassBadge(o.storage_class)}`}>
              {o.storage_class}
            </span>
            <span className="text-xs text-slate-500 w-20 text-right">{o.size_display}</span>
            <span className="text-[10px] text-slate-600 w-24 text-right whitespace-nowrap">
              {o.last_modified ? new Date(o.last_modified).toLocaleDateString() : ""}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
