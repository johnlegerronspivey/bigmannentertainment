import React from "react";
import { AlertTriangle, Clock, CheckCircle, Shield, Server, Box, Activity } from "lucide-react";
import { SEVERITY_COLORS, StatCard, SeverityBadge, StatusBadge } from "./shared";

export const OverviewTab = ({ dashboard, onRefresh, loading }) => {
  if (!dashboard) return <div className="text-slate-400 p-8 text-center">Loading...</div>;
  const { severity_breakdown: sb } = dashboard;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <StatCard icon={AlertTriangle} label="Open CVEs" value={dashboard.open_cves} color="text-red-400" />
        <StatCard icon={Clock} label="Overdue" value={dashboard.overdue_cves} color="text-orange-400" />
        <StatCard icon={CheckCircle} label="Fixed" value={dashboard.fixed_cves} color="text-emerald-400" />
        <StatCard icon={Shield} label="Verified" value={dashboard.verified_cves} color="text-green-400" />
        <StatCard icon={Server} label="Services" value={dashboard.total_services} color="text-cyan-400" />
        <StatCard icon={Box} label="SBOMs" value={dashboard.total_sboms} color="text-purple-400" />
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-4">Open CVEs by Severity</h3>
        <div className="grid grid-cols-5 gap-3">
          {["critical", "high", "medium", "low", "info"].map((s) => {
            const c = SEVERITY_COLORS[s];
            return (
              <div key={s} className={`${c.bg} border ${c.border} rounded-lg p-4 text-center`}>
                <div className={`text-2xl font-bold ${c.text}`}>{sb[s] || 0}</div>
                <div className={`text-xs ${c.text} mt-1 uppercase`}>{s}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Recent CVEs</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {(dashboard.recent_cves || []).map((c) => (
              <div key={c.id} className="flex items-center justify-between bg-slate-700/30 rounded-lg px-3 py-2">
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-white truncate">{c.cve_id}</div>
                  <div className="text-xs text-slate-400 truncate">{c.title}</div>
                </div>
                <div className="flex items-center gap-2 ml-2 shrink-0">
                  <SeverityBadge severity={c.severity} />
                  <StatusBadge status={c.status} />
                </div>
              </div>
            ))}
            {(!dashboard.recent_cves || dashboard.recent_cves.length === 0) && (
              <div className="text-slate-500 text-sm text-center py-4">No CVEs yet. Run a scan to detect vulnerabilities.</div>
            )}
          </div>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3">Recent Activity</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {(dashboard.recent_activity || []).map((a) => (
              <div key={a.id} className="flex items-start gap-3 bg-slate-700/30 rounded-lg px-3 py-2">
                <Activity className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <div className="text-sm text-white truncate">{a.message}</div>
                  <div className="text-xs text-slate-500">{new Date(a.timestamp).toLocaleString()}</div>
                </div>
              </div>
            ))}
            {(!dashboard.recent_activity || dashboard.recent_activity.length === 0) && (
              <div className="text-slate-500 text-sm text-center py-4">No activity recorded yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
