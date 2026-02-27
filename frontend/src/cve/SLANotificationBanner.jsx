import React, { useState, useEffect } from "react";
import { AlertTriangle, X, Wifi, WifiOff, ChevronDown, ChevronUp } from "lucide-react";
import { useSLAWebSocket } from "./hooks/useSLAWebSocket";

const SEVERITY_STYLES = {
  critical: "border-red-500/60 bg-red-950/80 text-red-200",
  high: "border-orange-500/60 bg-orange-950/80 text-orange-200",
  medium: "border-yellow-500/60 bg-yellow-950/80 text-yellow-200",
  low: "border-blue-500/60 bg-blue-950/80 text-blue-200",
};

const TYPE_LABELS = {
  sla_breach: "SLA BREACH",
  sla_warning: "SLA WARNING",
  escalation_run: "ESCALATION RUN",
};

function EventItem({ event, onDismiss }) {
  const sev = event.severity || "medium";
  const style = SEVERITY_STYLES[sev] || SEVERITY_STYLES.medium;
  const label = TYPE_LABELS[event.type] || event.type?.toUpperCase();

  if (event.type === "escalation_run") {
    if (event.escalations_created === 0) return null;
    return (
      <div data-testid="sla-ws-event-escalation" className="flex items-center gap-3 px-3 py-2 border border-orange-500/40 bg-orange-950/60 rounded-lg text-sm">
        <AlertTriangle className="w-4 h-4 text-orange-400 shrink-0" />
        <span className="text-orange-200 flex-1">
          <span className="font-semibold">{label}:</span> {event.escalations_created} new escalation(s) from {event.checked} CVEs checked
        </span>
        <button onClick={onDismiss} className="text-orange-400/60 hover:text-orange-300"><X className="w-3.5 h-3.5" /></button>
      </div>
    );
  }

  return (
    <div data-testid={`sla-ws-event-${event.type}`} className={`flex items-center gap-3 px-3 py-2 border rounded-lg text-sm ${style}`}>
      <AlertTriangle className="w-4 h-4 shrink-0" />
      <span className="flex-1">
        <span className="font-semibold">{label}:</span>{" "}
        {event.cve_id}{" "}
        <span className="opacity-80">({sev.toUpperCase()})</span>
        {event.type === "sla_breach" && <span className="ml-1">— {event.hours_overdue}h overdue</span>}
        {event.type === "sla_warning" && <span className="ml-1">— {event.pct_elapsed}% elapsed</span>}
      </span>
      <button onClick={onDismiss} className="opacity-60 hover:opacity-100"><X className="w-3.5 h-3.5" /></button>
    </div>
  );
}

export function SLANotificationBanner() {
  const { events, connected, clearEvent, clearAll } = useSLAWebSocket();
  const [collapsed, setCollapsed] = useState(false);
  const [hasNew, setHasNew] = useState(false);

  useEffect(() => {
    if (events.length > 0) setHasNew(true);
  }, [events.length]);

  if (events.length === 0) {
    return (
      <div data-testid="sla-ws-status" className="flex items-center gap-2 text-xs text-slate-500 px-1 py-1">
        {connected ? <Wifi className="w-3 h-3 text-emerald-500" /> : <WifiOff className="w-3 h-3 text-red-400" />}
        <span>SLA Live {connected ? "Connected" : "Disconnected"}</span>
      </div>
    );
  }

  const visible = collapsed ? [] : events.slice(0, 5);

  return (
    <div data-testid="sla-notification-banner" className="space-y-2 mb-4">
      <div className="flex items-center justify-between">
        <button
          data-testid="sla-ws-toggle"
          onClick={() => { setCollapsed(!collapsed); setHasNew(false); }}
          className="flex items-center gap-2 text-xs text-slate-400 hover:text-white transition-colors"
        >
          {connected ? <Wifi className="w-3 h-3 text-emerald-500" /> : <WifiOff className="w-3 h-3 text-red-400" />}
          <span className="font-medium">SLA Live Alerts</span>
          <span className="px-1.5 py-0.5 bg-red-500/20 text-red-300 rounded text-xs font-bold">{events.length}</span>
          {collapsed ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          {hasNew && collapsed && <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />}
        </button>
        {!collapsed && events.length > 0 && (
          <button data-testid="sla-ws-clear-all" onClick={clearAll} className="text-xs text-slate-500 hover:text-white transition-colors">
            Clear all
          </button>
        )}
      </div>
      {visible.map((evt, i) => (
        <EventItem key={`${evt.type}-${evt.cve_id || ""}-${evt.timestamp}-${i}`} event={evt} onDismiss={() => clearEvent(i)} />
      ))}
      {!collapsed && events.length > 5 && (
        <div className="text-xs text-slate-500 text-center">+ {events.length - 5} more alerts</div>
      )}
    </div>
  );
}
