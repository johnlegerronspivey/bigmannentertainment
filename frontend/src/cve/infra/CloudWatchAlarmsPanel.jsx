import React from "react";
import { Bell, AlertTriangle, CheckCircle, Clock } from "lucide-react";

const stateConfig = {
  OK: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-500/10", badge: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20" },
  ALARM: { icon: AlertTriangle, color: "text-red-400", bg: "bg-red-500/10", badge: "bg-red-500/15 text-red-300 border-red-500/20" },
  INSUFFICIENT_DATA: { icon: Clock, color: "text-amber-400", bg: "bg-amber-500/10", badge: "bg-amber-500/15 text-amber-300 border-amber-500/20" },
};

export const CloudWatchAlarmsPanel = ({ data }) => {
  if (!data) return <div className="text-slate-500 text-sm py-4">Loading...</div>;
  if (!data.connected) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;
  if (data.error) return <div className="text-amber-400 text-sm py-4"><AlertTriangle className="w-4 h-4 inline mr-1" />{data.error}</div>;

  const allAlarms = [...(data.alarms || []), ...(data.composite_alarms || [])];

  if (allAlarms.length === 0) return (
    <div className="text-slate-500 text-sm py-4 flex items-center gap-2">
      <Bell className="w-4 h-4" />No CloudWatch alarms configured
    </div>
  );

  return (
    <div className="space-y-3 pt-3" data-testid="cloudwatch-alarms-panel">
      {/* Summary */}
      <div className="flex items-center gap-4 text-xs text-slate-400">
        <span>{data.total} alarm(s)</span>
        {data.in_alarm > 0 && (
          <span className="flex items-center gap-1 text-red-400 font-semibold">
            <AlertTriangle className="w-3 h-3" />{data.in_alarm} in ALARM state
          </span>
        )}
      </div>

      {/* Alarms list */}
      {allAlarms.map((a, i) => {
        const cfg = stateConfig[a.state] || stateConfig.INSUFFICIENT_DATA;
        const Icon = cfg.icon;
        return (
          <div key={i} data-testid={`alarm-${a.name}`} className="bg-slate-900/60 border border-slate-700/40 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className={`p-1.5 rounded-lg ${cfg.bg}`}>
                <Icon className={`w-4 h-4 ${cfg.color}`} />
              </div>
              <span className="text-white font-semibold text-sm flex-1 truncate">{a.name}</span>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${cfg.badge}`}>
                {a.state}
              </span>
            </div>
            {a.description && <div className="text-xs text-slate-400 mb-2">{a.description}</div>}
            <div className="flex items-center gap-4 text-xs text-slate-500 flex-wrap">
              {a.metric && <span>Metric: <span className="text-slate-300 font-mono">{a.namespace}/{a.metric}</span></span>}
              {a.threshold != null && <span>Threshold: <span className="text-slate-300">{a.comparison} {a.threshold}</span></span>}
              {a.period > 0 && <span>Period: {a.period}s</span>}
              {a.rule && <span className="text-slate-300 font-mono text-[10px]">Rule: {a.rule}</span>}
              {a.updated_at && <span className="ml-auto">Updated: {new Date(a.updated_at).toLocaleString()}</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
};
