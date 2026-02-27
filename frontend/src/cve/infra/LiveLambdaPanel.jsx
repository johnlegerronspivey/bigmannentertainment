import React from "react";
import { Zap, AlertTriangle } from "lucide-react";

export const LiveLambdaPanel = ({ data }) => {
  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (!data.functions || data.functions.length === 0) return <div className="text-slate-500 text-sm py-4">No Lambda functions found in {data.region || "region"}</div>;

  return (
    <div className="space-y-3 pt-3">
      <div className="text-xs text-slate-500 mb-2">{data.total} function(s) found</div>
      {data.functions.map((fn, i) => (
        <div key={i} data-testid={`live-lambda-${fn.name}`} className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-white font-semibold text-sm">{fn.name}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${fn.state === "Active" ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"}`}>
                {fn.state}
              </span>
            </div>
            <span className="text-xs text-slate-600">{fn.runtime}</span>
          </div>
          {fn.description && <div className="text-xs text-slate-400 mb-3">{fn.description}</div>}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 mb-3">
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Memory</div>
              <div className="text-sm text-slate-300">{fn.memory_mb} MB</div>
            </div>
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Timeout</div>
              <div className="text-sm text-slate-300">{fn.timeout}s</div>
            </div>
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Code Size</div>
              <div className="text-sm text-slate-300">{(fn.code_size_bytes / 1024).toFixed(1)} KB</div>
            </div>
            <div className="bg-slate-800/60 rounded px-3 py-2">
              <div className="text-[10px] text-slate-500">Handler</div>
              <div className="text-sm text-slate-300 font-mono truncate">{fn.handler}</div>
            </div>
          </div>
          {fn.metrics && (
            <div className="grid grid-cols-4 gap-2">
              <div className="bg-cyan-500/5 border border-cyan-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-cyan-400">Invocations (24h)</div>
                <div className="text-lg font-bold text-white">{fn.metrics.invocations ?? "-"}</div>
              </div>
              <div className="bg-red-500/5 border border-red-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-red-400">Errors (24h)</div>
                <div className="text-lg font-bold text-white">{fn.metrics.errors ?? "-"}</div>
              </div>
              <div className="bg-violet-500/5 border border-violet-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-violet-400">Avg Duration</div>
                <div className="text-lg font-bold text-white">{fn.metrics.duration != null ? `${fn.metrics.duration}ms` : "-"}</div>
              </div>
              <div className="bg-amber-500/5 border border-amber-500/10 rounded px-3 py-2 text-center">
                <div className="text-[10px] text-amber-400">Throttles (24h)</div>
                <div className="text-lg font-bold text-white">{fn.metrics.throttles ?? "-"}</div>
              </div>
            </div>
          )}
          {fn.last_modified && (
            <div className="text-[10px] text-slate-600 mt-2">Last modified: {new Date(fn.last_modified).toLocaleString()}</div>
          )}
        </div>
      ))}
    </div>
  );
};
