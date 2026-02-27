import React from "react";
import { CheckCircle, XCircle, Clock, GitBranch, ExternalLink, AlertTriangle } from "lucide-react";

const conclusionColor = {
  success: "bg-emerald-500/15 text-emerald-300",
  failure: "bg-red-500/15 text-red-300",
  cancelled: "bg-slate-500/15 text-slate-300",
  skipped: "bg-slate-500/15 text-slate-400",
  timed_out: "bg-amber-500/15 text-amber-300",
};

export const GitHubRunsPanel = ({ data }) => {
  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) {
    return (
      <div className="pt-3">
        <div className="text-amber-400 text-sm mb-3"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>
        {data.available_repos && data.available_repos.length > 0 && (
          <div>
            <div className="text-xs text-slate-500 mb-2">Available repositories:</div>
            <div className="space-y-1">
              {data.available_repos.map((r, i) => (
                <div key={i} className="bg-slate-900/50 rounded px-3 py-2 text-sm text-slate-300 font-mono flex items-center gap-2">
                  <GitBranch className="w-3.5 h-3.5 text-slate-500" />
                  {r.full_name}
                  {r.private && <span className="text-[10px] bg-amber-500/15 text-amber-300 px-1.5 py-0.5 rounded">private</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
  if (!data.runs || data.runs.length === 0) return <div className="text-slate-500 text-sm py-4">No workflow runs found for {data.repo}</div>;

  return (
    <div className="space-y-2 pt-3">
      <div className="text-xs text-slate-500 mb-2">Repo: <span className="text-slate-300 font-mono">{data.repo}</span></div>
      {data.runs.map((run) => (
        <div key={run.id} data-testid={`gh-run-${run.id}`} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-3">
          <div className={`p-1.5 rounded-lg ${run.conclusion === "success" ? "bg-emerald-500/10" : run.conclusion === "failure" ? "bg-red-500/10" : "bg-slate-600/10"}`}>
            {run.conclusion === "success" ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : run.conclusion === "failure" ? <XCircle className="w-4 h-4 text-red-400" /> : <Clock className="w-4 h-4 text-slate-400" />}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm text-white font-medium truncate">{run.name}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${conclusionColor[run.conclusion] || "bg-slate-600/30 text-slate-400"}`}>
                {run.conclusion || run.status}
              </span>
            </div>
            <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
              <span>#{run.run_number}</span>
              <span>{run.branch}</span>
              <span>{run.event}</span>
            </div>
          </div>
          {run.html_url && (
            <a href={run.html_url} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:text-cyan-300" data-testid={`gh-run-link-${run.id}`}>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
          <div className="text-xs text-slate-600 whitespace-nowrap">{run.created_at ? new Date(run.created_at).toLocaleString() : ""}</div>
        </div>
      ))}
    </div>
  );
};
