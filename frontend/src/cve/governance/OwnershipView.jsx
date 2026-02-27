import React from "react";
import { AlertTriangle, Users } from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { SeverityBadge } from "../shared";
import { ChartTooltip } from "../components";
import { AssignOwnerModal } from "../AssignOwnerModal";
import { CHART_COLORS, STATUS_CHART_COLORS } from "../constants";

const CustomTooltip = ChartTooltip;

export const OwnershipView = ({ ownership, ownerInfo, unassigned, govAssignTarget, setGovAssignTarget, fetchAll, onRefresh }) => {
  const statusPieData = (ownership?.by_status || []).map((s) => ({ name: s.status.replace("_", " "), value: s.count, fill: STATUS_CHART_COLORS[s.status] || "#64748b" }));
  const sourcePieData = (ownership?.by_source || []).map((s, i) => ({ name: s.source, value: s.count, fill: CHART_COLORS[i % CHART_COLORS.length] }));

  return (
    <div className="space-y-6">
      {(ownerInfo?.unassigned_open_cves || 0) > 0 && (
        <div data-testid="unassigned-alert" className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <div>
              <span className="text-amber-300 font-semibold text-sm">{ownerInfo.unassigned_open_cves} unassigned open CVE{ownerInfo.unassigned_open_cves !== 1 ? "s" : ""}</span>
              <p className="text-amber-400/70 text-xs mt-0.5">These vulnerabilities need an owner for accountability and SLA tracking</p>
            </div>
          </div>
        </div>
      )}

      {(unassigned?.items || []).length > 0 && (
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3 text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" /> Unassigned CVEs
            <span className="text-xs text-slate-500 font-normal ml-1">({unassigned.total} total)</span>
          </h3>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {(unassigned.items || []).map((c) => (
              <div key={c.id} data-testid={`unassigned-cve-${c.id}`} className="flex items-center justify-between bg-slate-900/50 rounded-lg px-3 py-2">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <span className="text-cyan-400 font-mono text-xs">{c.cve_id}</span>
                  <SeverityBadge severity={c.severity} />
                  <span className="text-xs text-slate-300 truncate">{c.title}</span>
                </div>
                <button data-testid={`gov-assign-btn-${c.id}`} onClick={() => setGovAssignTarget(c)} className="ml-2 px-2.5 py-1 rounded text-xs bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/40 transition-colors border border-cyan-500/30 shrink-0">
                  <Users className="w-3 h-3 inline mr-1" />Assign
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Team</h3>
          {(ownership?.by_team || []).length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm">No team assignments yet</div>
          ) : (
            <div className="space-y-2">
              {(ownership?.by_team || []).map((t) => {
                const maxCount = Math.max(...(ownership?.by_team || []).map((x) => x.count), 1);
                return (
                  <div key={t.team} className="flex items-center gap-3">
                    <span className="text-sm text-slate-300 w-32 truncate">{t.team}</span>
                    <div className="flex-1 bg-slate-700/50 rounded-full h-3">
                      <div className="h-3 rounded-full bg-cyan-500/70" style={{ width: `${(t.count / maxCount) * 100}%` }} />
                    </div>
                    <span className="text-sm text-white font-medium w-8 text-right">{t.count}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4 text-sm">Open CVEs by Assignee</h3>
          {(ownership?.by_person || []).length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm">No individual assignments yet</div>
          ) : (
            <div className="space-y-2">
              {(ownership?.by_person || []).map((p) => {
                const maxCount = Math.max(...(ownership?.by_person || []).map((x) => x.count), 1);
                return (
                  <div key={p.person} className="flex items-center gap-3">
                    <span className="text-sm text-slate-300 w-32 truncate">{p.person}</span>
                    <div className="flex-1 bg-slate-700/50 rounded-full h-3">
                      <div className="h-3 rounded-full bg-purple-500/70" style={{ width: `${(p.count / maxCount) * 100}%` }} />
                    </div>
                    <span className="text-sm text-white font-medium w-8 text-right">{p.count}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3 text-sm">Registered Owners</h3>
          {(ownerInfo?.people || []).length === 0 ? (
            <p className="text-slate-500 text-sm">No owners registered yet. Assign an owner to a CVE to populate this list.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {(ownerInfo?.people || []).map((p) => (
                <span key={p} className="px-3 py-1 bg-purple-500/15 text-purple-300 rounded-lg text-xs border border-purple-500/20">{p}</span>
              ))}
            </div>
          )}
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-3 text-sm">Registered Teams</h3>
          {(ownerInfo?.teams || []).length === 0 ? (
            <p className="text-slate-500 text-sm">No teams registered yet. Assign a team to a CVE to populate this list.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {(ownerInfo?.teams || []).map((t) => (
                <span key={t} className="px-3 py-1 bg-cyan-500/15 text-cyan-300 rounded-lg text-xs border border-cyan-500/20">{t}</span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4 text-sm">CVE Sources</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={sourcePieData} cx="50%" cy="50%" innerRadius={35} outerRadius={65} paddingAngle={3} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                {sourcePieData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4 text-sm">Status Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={statusPieData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" name="Count" radius={[4, 4, 0, 0]} barSize={30}>
                {statusPieData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {govAssignTarget && <AssignOwnerModal cve={govAssignTarget} onClose={() => setGovAssignTarget(null)} onAssigned={() => { setGovAssignTarget(null); fetchAll(); onRefresh(); }} />}
    </div>
  );
};
