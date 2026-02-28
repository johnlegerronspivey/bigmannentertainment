import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area } from "recharts";
import { AlertTriangle } from "lucide-react";
import { ChartTooltip } from "../components";

export const BreachTimelineView = ({ breachTimeline }) => {
  const timeline = breachTimeline?.timeline || [];
  const totalBreaches = timeline.reduce((s, d) => s + d.new_breaches, 0);
  const peakDay = timeline.reduce((max, d) => (d.new_breaches > (max?.new_breaches || 0) ? d : max), timeline[0]);

  // Filter to show meaningful data points
  const data = timeline.length <= 15
    ? timeline
    : timeline.filter((_, i) => i % Math.ceil(timeline.length / 15) === 0 || i === timeline.length - 1);

  // Running total for cumulative view
  let cumulative = 0;
  const cumulativeData = timeline.map((d) => {
    cumulative += d.new_breaches;
    return { ...d, cumulative };
  });
  const cumulativeFiltered = cumulativeData.length <= 15
    ? cumulativeData
    : cumulativeData.filter((_, i) => i % Math.ceil(cumulativeData.length / 15) === 0 || i === cumulativeData.length - 1);

  return (
    <div data-testid="breach-timeline-view" className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="text-xs text-slate-400 mb-1">Total Breaches</div>
          <div className="text-3xl font-bold text-red-400">{totalBreaches}</div>
          <div className="text-xs text-slate-500 mt-1">in {breachTimeline?.period_days || 30} days</div>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="text-xs text-slate-400 mb-1">Peak Day</div>
          <div className="text-lg font-bold text-amber-400">{peakDay?.label || "--"}</div>
          <div className="text-xs text-slate-500 mt-1">{peakDay?.new_breaches || 0} breaches</div>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="text-xs text-slate-400 mb-1">Daily Average</div>
          <div className="text-3xl font-bold text-white">{timeline.length > 0 ? (totalBreaches / timeline.length).toFixed(1) : 0}</div>
          <div className="text-xs text-slate-500 mt-1">breaches/day</div>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <div className="text-xs text-slate-400 mb-1">Zero-Breach Days</div>
          <div className="text-3xl font-bold text-emerald-400">{timeline.filter((d) => d.new_breaches === 0).length}</div>
          <div className="text-xs text-slate-500 mt-1">of {timeline.length} days</div>
        </div>
      </div>

      {totalBreaches === 0 ? (
        <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-8 text-center">
          <AlertTriangle className="w-10 h-10 text-emerald-400 mx-auto mb-3 opacity-60" />
          <p className="text-emerald-400 font-semibold">No SLA Breaches</p>
          <p className="text-xs text-slate-400 mt-1">No new SLA breaches detected in the selected period</p>
        </div>
      ) : (
        <>
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">SLA Breaches by Severity Over Time</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data} barCategoryGap="15%">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                <Bar dataKey="critical" name="Critical" fill="#ef4444" stackId="a" />
                <Bar dataKey="high" name="High" fill="#f97316" stackId="a" />
                <Bar dataKey="medium" name="Medium" fill="#eab308" stackId="a" />
                <Bar dataKey="low" name="Low" fill="#3b82f6" stackId="a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-4 text-sm">Cumulative SLA Breaches</h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={cumulativeFiltered}>
                <defs>
                  <linearGradient id="gradBreach" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} allowDecimals={false} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="cumulative" name="Total Breaches" stroke="#ef4444" fill="url(#gradBreach)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
};
