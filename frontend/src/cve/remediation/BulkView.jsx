import React from "react";
import { ArrowUpRight, Loader2 } from "lucide-react";
import { SEVERITY_COLORS } from "../shared";

export const BulkView = ({ stats, bulkCreating, repoConnected, onBulkCreate }) => {
  return (
    <div className="space-y-4">
      <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
        <h3 className="text-white font-semibold mb-1">Bulk Issue Creation</h3>
        <p className="text-sm text-slate-400">Automatically create GitHub issues for all detected CVEs matching a severity level.</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {["critical", "high", "medium", "low"].map((sev) => {
          const c = SEVERITY_COLORS[sev];
          const count = stats.by_severity?.[sev] || 0;
          return (
            <div key={sev} className={`${c.bg} border ${c.border} rounded-xl p-5`}>
              <div className="flex items-center justify-between mb-3">
                <h4 className={`${c.text} font-semibold text-sm uppercase`}>{sev}</h4>
                <span className={`${c.text} text-2xl font-bold`}>{count}</span>
              </div>
              <p className="text-xs text-slate-400 mb-4">{count} active remediation item{count !== 1 ? "s" : ""}</p>
              <button data-testid={`bulk-create-${sev}`} onClick={() => onBulkCreate(sev)} disabled={bulkCreating || !repoConnected} className={`w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-50 ${c.bg} border ${c.border} ${c.text} hover:opacity-80`}>
                {bulkCreating ? <Loader2 className="w-3 h-3 animate-spin" /> : <ArrowUpRight className="w-3 h-3" />}
                Create Issues for {sev}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
