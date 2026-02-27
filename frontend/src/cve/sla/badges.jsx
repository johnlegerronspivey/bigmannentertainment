import React from "react";

export const SLAStatusBadge = ({ status }) => {
  const styles = {
    breached: "bg-red-500/20 text-red-300 border-red-500/30",
    warning: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    approaching: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  };
  return (
    <span data-testid={`sla-badge-${status}`} className={`px-2 py-0.5 rounded text-xs font-medium border ${styles[status] || styles.approaching}`}>
      {status.toUpperCase()}
    </span>
  );
};

export const EscStatusBadge = ({ status }) => {
  const map = {
    open: "bg-red-500/20 text-red-300 border-red-500/30",
    acknowledged: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    assigned: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    resolved: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  };
  return (
    <span data-testid={`esc-status-${status}`} className={`px-2 py-0.5 rounded text-xs font-medium border ${map[status] || map.open}`}>
      {(status || "open").toUpperCase()}
    </span>
  );
};

export const CountdownTimer = ({ remainingHours, percentElapsed }) => {
  const isOverdue = remainingHours <= 0;
  const absHours = Math.abs(remainingHours);
  const days = Math.floor(absHours / 24);
  const hours = Math.floor(absHours % 24);
  const barPct = Math.min(percentElapsed, 200);
  const barColor = percentElapsed >= 100 ? "bg-red-500" : percentElapsed >= 75 ? "bg-amber-500" : "bg-emerald-500";
  return (
    <div data-testid="countdown-timer" className="flex items-center gap-3 min-w-[180px]">
      <div className="flex-1">
        <div className="w-full bg-slate-700/50 rounded-full h-1.5 mb-1">
          <div className={`h-1.5 rounded-full transition-all ${barColor}`} style={{ width: `${Math.min(barPct / 2, 100)}%` }} />
        </div>
        <div className={`text-xs font-mono ${isOverdue ? "text-red-400" : "text-slate-300"}`}>
          {isOverdue ? "+" : ""}{days > 0 ? `${days}d ` : ""}{hours}h {isOverdue ? "overdue" : "left"}
        </div>
      </div>
    </div>
  );
};
