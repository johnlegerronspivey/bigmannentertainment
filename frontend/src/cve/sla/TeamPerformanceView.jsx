import React from "react";
import { Users, Award, AlertTriangle, Clock, CheckCircle2 } from "lucide-react";

const PerformanceBar = ({ pct }) => {
  const color = pct >= 90 ? "bg-emerald-500" : pct >= 70 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="w-full bg-slate-700/50 rounded-full h-2">
      <div className={`h-2 rounded-full transition-all ${color}`} style={{ width: `${Math.min(pct, 100)}%` }} />
    </div>
  );
};

export const TeamPerformanceView = ({ teamData }) => {
  const team = teamData?.team || [];

  if (team.length === 0) {
    return (
      <div data-testid="team-performance-empty" className="text-center py-16 text-slate-500">
        <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p className="text-sm">No team performance data available yet</p>
        <p className="text-xs text-slate-600 mt-1">Assign CVEs to team members to see performance metrics</p>
      </div>
    );
  }

  const topPerformer = team.find((t) => t.resolved > 0) || team[0];

  return (
    <div data-testid="team-performance-view" className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-lg bg-cyan-500/10"><Users className="w-5 h-5 text-cyan-400" /></div>
            <span className="text-slate-400 text-sm">Team Members</span>
          </div>
          <div className="text-3xl font-bold text-white">{team.length}</div>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10"><CheckCircle2 className="w-5 h-5 text-emerald-400" /></div>
            <span className="text-slate-400 text-sm">Total Resolved</span>
          </div>
          <div className="text-3xl font-bold text-white">{team.reduce((s, t) => s + t.resolved, 0)}</div>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-lg bg-red-500/10"><AlertTriangle className="w-5 h-5 text-red-400" /></div>
            <span className="text-slate-400 text-sm">Total Breached</span>
          </div>
          <div className="text-3xl font-bold text-white">{team.reduce((s, t) => s + t.breached, 0)}</div>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-lg bg-amber-500/10"><Award className="w-5 h-5 text-amber-400" /></div>
            <span className="text-slate-400 text-sm">Top Performer</span>
          </div>
          <div className="text-lg font-bold text-white truncate">{topPerformer?.assignee || "--"}</div>
          <div className="text-xs text-emerald-400">{topPerformer?.compliance_pct}% compliance</div>
        </div>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="p-5 border-b border-slate-700/50">
          <h3 className="text-white font-semibold text-sm">Team SLA Performance</h3>
          <p className="text-xs text-slate-400 mt-0.5">Per-assignee resolution metrics and SLA compliance</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50 bg-slate-900/30">
                <th className="text-left px-5 py-3 text-slate-400 font-medium text-xs">Assignee</th>
                <th className="text-left px-4 py-3 text-slate-400 font-medium text-xs">Team</th>
                <th className="text-center px-4 py-3 text-slate-400 font-medium text-xs">Total</th>
                <th className="text-center px-4 py-3 text-slate-400 font-medium text-xs">Open</th>
                <th className="text-center px-4 py-3 text-slate-400 font-medium text-xs">Resolved</th>
                <th className="text-center px-4 py-3 text-slate-400 font-medium text-xs">Breached</th>
                <th className="text-center px-4 py-3 text-slate-400 font-medium text-xs">MTTR</th>
                <th className="px-5 py-3 text-slate-400 font-medium text-xs min-w-[160px]">Compliance</th>
              </tr>
            </thead>
            <tbody>
              {team.map((member, i) => (
                <tr key={member.assignee} data-testid={`team-row-${i}`} className="border-b border-slate-700/20 hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-slate-700/80 flex items-center justify-center text-xs text-slate-300 font-medium">
                        {member.assignee.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-white font-medium text-sm">{member.assignee}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3.5 text-slate-400 text-xs">{member.team || "--"}</td>
                  <td className="px-4 py-3.5 text-center text-white">{member.total}</td>
                  <td className="px-4 py-3.5 text-center text-amber-400">{member.open}</td>
                  <td className="px-4 py-3.5 text-center text-emerald-400">{member.resolved}</td>
                  <td className="px-4 py-3.5 text-center text-red-400">{member.breached}</td>
                  <td className="px-4 py-3.5 text-center">
                    <span className="text-xs text-slate-300 font-mono">
                      {member.avg_mttr_hours > 0 ? `${member.avg_mttr_days}d` : "--"}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <PerformanceBar pct={member.compliance_pct} />
                      <span className={`text-xs font-medium min-w-[40px] text-right ${member.compliance_pct >= 90 ? "text-emerald-400" : member.compliance_pct >= 70 ? "text-amber-400" : "text-red-400"}`}>
                        {member.compliance_pct}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
