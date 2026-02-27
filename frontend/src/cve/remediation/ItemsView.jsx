import React from "react";
import { Wrench, Github, ExternalLink, GitBranch, Loader2 } from "lucide-react";
import { SeverityBadge } from "../shared";
import { REMEDIATION_STATUS_COLORS, REMEDIATION_STATUSES } from "./constants";

export const ItemsView = ({ items, totalItems, loading, filterStatus, setFilterStatus, filterSeverity, setFilterSeverity, onStatusChange }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <select data-testid="remediation-status-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {REMEDIATION_STATUSES.map((s) => <option key={s} value={s}>{s.replace(/_/g, " ").toUpperCase()}</option>)}
        </select>
        <select data-testid="remediation-severity-filter" className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={filterSeverity} onChange={(e) => setFilterSeverity(e.target.value)}>
          <option value="">All Severities</option>
          {["critical", "high", "medium", "low"].map((s) => <option key={s} value={s}>{s.toUpperCase()}</option>)}
        </select>
        <span className="text-sm text-slate-400 ml-auto">{totalItems} item{totalItems !== 1 ? "s" : ""}</span>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400"><Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" /> Loading...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
          <Wrench className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400 text-sm">No remediation items yet. Create issues from the CVE database.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} data-testid={`remediation-item-${item.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <SeverityBadge severity={item.severity} />
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${REMEDIATION_STATUS_COLORS[item.status] || REMEDIATION_STATUS_COLORS.open}`}>{item.status.replace(/_/g, " ").toUpperCase()}</span>
                    <span className="text-xs text-slate-500 font-mono">{item.cve_id}</span>
                  </div>
                  <h4 className="text-white text-sm font-medium truncate">{item.title || item.cve_id}</h4>
                  {item.affected_package && <p className="text-xs text-slate-400 mt-1">Package: <span className="text-slate-300 font-mono">{item.affected_package}</span> {item.affected_version && `@ ${item.affected_version}`} {item.fixed_version && <span className="text-emerald-400">→ {item.fixed_version}</span>}</p>}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {item.github_issue_url && (
                    <a href={item.github_issue_url} target="_blank" rel="noreferrer" data-testid={`issue-link-${item.id}`} className="flex items-center gap-1 px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded text-xs text-white transition-colors">
                      <Github className="w-3 h-3" /> #{item.github_issue_number} <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {item.github_pr_url && (
                    <a href={item.github_pr_url} target="_blank" rel="noreferrer" data-testid={`pr-link-${item.id}`} className="flex items-center gap-1 px-2 py-1 bg-purple-600/30 hover:bg-purple-600/50 rounded text-xs text-purple-300 transition-colors">
                      <GitBranch className="w-3 h-3" /> PR #{item.github_pr_number} <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  <select className="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-xs text-white" value={item.status} onChange={(e) => onStatusChange(item.id, e.target.value)}>
                    {REMEDIATION_STATUSES.map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
