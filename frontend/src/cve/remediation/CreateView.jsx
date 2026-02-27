import React from "react";
import { CheckCircle, Github, GitBranch, Loader2 } from "lucide-react";
import { SeverityBadge } from "../shared";

export const CreateView = ({ cves, creating, repoConnected, onCreateIssue, onCreatePR }) => {
  return (
    <div className="space-y-4">
      <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
        <h3 className="text-white font-semibold mb-1">Create GitHub Issues & PRs from Detected CVEs</h3>
        <p className="text-sm text-slate-400">Select a CVE below to create a GitHub issue or pull request for automated remediation.</p>
      </div>

      {cves.length === 0 ? (
        <div className="text-center py-12 bg-slate-800/40 rounded-xl border border-slate-700/50">
          <CheckCircle className="w-10 h-10 text-emerald-600 mx-auto mb-3" />
          <p className="text-slate-400 text-sm">No open CVEs detected. All vulnerabilities have been triaged.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {cves.map((cve) => (
            <div key={cve.id} data-testid={`cve-remediate-${cve.id}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 flex items-center justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <SeverityBadge severity={cve.severity} />
                  <span className="text-xs text-slate-500 font-mono">{cve.cve_id}</span>
                </div>
                <h4 className="text-white text-sm font-medium truncate">{cve.title}</h4>
                {cve.affected_package && <p className="text-xs text-slate-400 mt-1"><span className="font-mono text-slate-300">{cve.affected_package}</span> {cve.affected_version && `@ ${cve.affected_version}`} {cve.fixed_version && <span className="text-emerald-400">→ fix: {cve.fixed_version}</span>}</p>}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button data-testid={`create-issue-${cve.id}`} onClick={() => onCreateIssue(cve.id)} disabled={creating[`issue_${cve.id}`] || !repoConnected} className="flex items-center gap-1.5 px-3 py-1.5 bg-yellow-600/20 hover:bg-yellow-600/40 text-yellow-300 border border-yellow-500/30 rounded-lg text-xs transition-colors disabled:opacity-50">
                  {creating[`issue_${cve.id}`] ? <Loader2 className="w-3 h-3 animate-spin" /> : <Github className="w-3 h-3" />} Create Issue
                </button>
                <button data-testid={`create-pr-${cve.id}`} onClick={() => onCreatePR(cve.id)} disabled={creating[`pr_${cve.id}`] || !repoConnected || !cve.fixed_version} className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 border border-purple-500/30 rounded-lg text-xs transition-colors disabled:opacity-50" title={!cve.fixed_version ? "No fixed version available" : ""}>
                  {creating[`pr_${cve.id}`] ? <Loader2 className="w-3 h-3 animate-spin" /> : <GitBranch className="w-3 h-3" />} Create PR
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
