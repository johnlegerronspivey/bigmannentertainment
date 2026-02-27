import React, { useState } from "react";
import {
  GitBranch, GitCommit, GitPullRequest, ExternalLink,
  AlertTriangle, Star, Lock, Globe, Code
} from "lucide-react";

const TabButton = ({ active, onClick, icon: Icon, label, count }) => (
  <button
    onClick={onClick}
    data-testid={`gh-tab-${label.toLowerCase()}`}
    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
      active
        ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
        : "text-slate-400 hover:text-slate-300 border border-transparent"
    }`}
  >
    <Icon className="w-3.5 h-3.5" />
    {label}
    {count != null && (
      <span className="ml-1 px-1.5 py-0.5 rounded-full bg-slate-700/60 text-[10px]">{count}</span>
    )}
  </button>
);

export const GitHubRepoPanel = ({ data }) => {
  const [tab, setTab] = useState("commits");

  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;

  const repo = data.repo || {};

  return (
    <div className="space-y-4 pt-3" data-testid="github-repo-panel">
      {/* Repo header */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          {repo.private ? <Lock className="w-4 h-4 text-amber-400" /> : <Globe className="w-4 h-4 text-emerald-400" />}
          <span className="text-white font-semibold text-sm font-mono">{repo.name}</span>
        </div>
        {repo.language && (
          <span className="flex items-center gap-1 text-xs text-slate-400">
            <Code className="w-3 h-3" />{repo.language}
          </span>
        )}
        <span className="flex items-center gap-1 text-xs text-slate-400">
          <Star className="w-3 h-3" />{repo.stars}
        </span>
        <span className="flex items-center gap-1 text-xs text-slate-400">
          <GitBranch className="w-3 h-3" />{repo.forks} forks
        </span>
        <span className="text-xs text-slate-500">
          {repo.size_kb ? `${(repo.size_kb / 1024).toFixed(1)} MB` : ""}
        </span>
      </div>
      {repo.description && <div className="text-xs text-slate-400">{repo.description}</div>}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700/40 pb-2">
        <TabButton active={tab === "commits"} onClick={() => setTab("commits")} icon={GitCommit} label="Commits" count={data.commits?.length} />
        <TabButton active={tab === "branches"} onClick={() => setTab("branches")} icon={GitBranch} label="Branches" count={data.branches?.length} />
        <TabButton active={tab === "pulls"} onClick={() => setTab("pulls")} icon={GitPullRequest} label="PRs" count={data.pulls?.length} />
      </div>

      {/* Commits */}
      {tab === "commits" && (
        <div className="space-y-1.5">
          {(!data.commits || data.commits.length === 0) && <div className="text-slate-500 text-sm">No commits found</div>}
          {data.commits?.map((c, i) => (
            <div key={i} data-testid={`commit-${c.sha}`} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-2.5">
              <GitCommit className="w-4 h-4 text-cyan-400 flex-shrink-0" />
              <span className="text-xs text-cyan-300 font-mono flex-shrink-0">{c.sha}</span>
              <span className="text-sm text-slate-300 truncate flex-1">{c.message}</span>
              <span className="text-xs text-slate-500 flex-shrink-0">{c.author}</span>
              {c.html_url && (
                <a href={c.html_url} target="_blank" rel="noopener noreferrer" className="text-slate-500 hover:text-cyan-400">
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
              <span className="text-[10px] text-slate-600 flex-shrink-0 whitespace-nowrap">
                {c.date ? new Date(c.date).toLocaleDateString() : ""}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Branches */}
      {tab === "branches" && (
        <div className="space-y-1.5">
          {(!data.branches || data.branches.length === 0) && <div className="text-slate-500 text-sm">No branches found</div>}
          {data.branches?.map((b, i) => (
            <div key={i} data-testid={`branch-${b.name}`} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-2.5">
              <GitBranch className="w-4 h-4 text-violet-400 flex-shrink-0" />
              <span className="text-sm text-white font-mono">{b.name}</span>
              {b.protected && (
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/20">protected</span>
              )}
              <span className="text-xs text-slate-600 font-mono ml-auto">{b.sha}</span>
            </div>
          ))}
        </div>
      )}

      {/* Pull Requests */}
      {tab === "pulls" && (
        <div className="space-y-1.5">
          {(!data.pulls || data.pulls.length === 0) && <div className="text-slate-500 text-sm">No open pull requests</div>}
          {data.pulls?.map((pr, i) => (
            <div key={i} data-testid={`pr-${pr.number}`} className="flex items-center gap-3 bg-slate-900/50 rounded-lg px-4 py-2.5">
              <GitPullRequest className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span className="text-xs text-slate-500">#{pr.number}</span>
              <span className="text-sm text-white truncate flex-1">{pr.title}</span>
              {pr.draft && <span className="px-2 py-0.5 rounded text-[10px] bg-slate-600/30 text-slate-400">draft</span>}
              {pr.labels?.map((l, li) => (
                <span key={li} className="px-2 py-0.5 rounded text-[10px] bg-violet-500/15 text-violet-300">{l}</span>
              ))}
              <span className="text-xs text-slate-500">{pr.author}</span>
              {pr.html_url && (
                <a href={pr.html_url} target="_blank" rel="noopener noreferrer" className="text-slate-500 hover:text-cyan-400">
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
