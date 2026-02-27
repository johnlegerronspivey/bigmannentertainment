import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { ChartTooltip, LoadingState, EmptyState } from "../components";

export const TeamView = ({ data, loading }) => {
  if (loading) return <LoadingState />;
  if (!data?.teams?.length) return <EmptyState text="No team data — assign CVEs to owners first" />;

  return (
    <div className="space-y-6">
      <h3 className="text-white font-semibold">Team Performance</h3>

      <div data-testid="team-bar-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <p className="text-slate-400 text-sm mb-4">Assigned vs Resolved by Owner</p>
        <ResponsiveContainer width="100%" height={Math.max(200, data.teams.length * 40)}>
          <BarChart data={data.teams} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis type="category" dataKey="owner" tick={{ fill: "#94a3b8", fontSize: 11 }} width={100} />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            <Bar dataKey="assigned" name="Assigned" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            <Bar dataKey="resolved" name="Resolved" fill="#10b981" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div data-testid="team-table" className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                {["Owner", "Assigned", "Open", "Resolved", "Rate", "Avg MTTR", "Crit", "High", "Med", "Low"].map((h) => (
                  <th key={h} className="text-left text-slate-400 font-medium px-4 py-3 text-xs">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.teams.map((t) => (
                <tr key={t.owner} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                  <td className="px-4 py-3 text-white font-medium">{t.owner}</td>
                  <td className="px-4 py-3 text-slate-300">{t.assigned}</td>
                  <td className="px-4 py-3 text-orange-400">{t.open}</td>
                  <td className="px-4 py-3 text-emerald-400">{t.resolved}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${t.resolution_rate >= 80 ? "bg-emerald-500/20 text-emerald-300" : t.resolution_rate >= 50 ? "bg-yellow-500/20 text-yellow-300" : "bg-red-500/20 text-red-300"}`}>
                      {t.resolution_rate}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-cyan-400">{t.avg_resolution_hours}h</td>
                  <td className="px-4 py-3 text-red-400">{t.critical}</td>
                  <td className="px-4 py-3 text-orange-400">{t.high}</td>
                  <td className="px-4 py-3 text-yellow-400">{t.medium}</td>
                  <td className="px-4 py-3 text-blue-400">{t.low}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
