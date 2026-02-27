import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { ChartTooltip, LoadingState, EmptyState } from "../components";

export const ScannerView = ({ data, loading }) => {
  if (loading) return <LoadingState />;
  if (!data?.scanners?.length) return <EmptyState text="No scanner data — run a scan first" />;

  return (
    <div className="space-y-6">
      <h3 className="text-white font-semibold">Scanner Effectiveness</h3>

      <div data-testid="scanner-bar-chart" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <p className="text-slate-400 text-sm mb-4">CVEs Found per Scanner</p>
        <ResponsiveContainer width="100%" height={Math.max(200, data.scanners.length * 50)}>
          <BarChart data={data.scanners} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis type="category" dataKey="scanner" tick={{ fill: "#94a3b8", fontSize: 11 }} width={100} />
            <Tooltip content={<ChartTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
            <Bar dataKey="total_scans" name="Total Scans" fill="#6366f1" radius={[0, 4, 4, 0]} />
            <Bar dataKey="cves_found" name="CVEs Found" fill="#f97316" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.scanners.map((s) => (
          <div key={s.scanner} data-testid={`scanner-card-${s.scanner}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-white font-medium text-sm">{s.scanner}</span>
              <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded">{s.total_scans} scans</span>
            </div>
            <div className="text-2xl font-bold text-orange-400 mb-1">{s.cves_found}</div>
            <div className="text-xs text-slate-500">CVEs found ({s.avg_findings_per_scan} avg/scan)</div>
          </div>
        ))}
      </div>
    </div>
  );
};
