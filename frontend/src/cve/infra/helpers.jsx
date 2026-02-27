import React from "react";
import { Wifi, WifiOff } from "lucide-react";

export const StatusDot = ({ ok }) => (
  <span className={`inline-block w-2.5 h-2.5 rounded-full ${ok ? "bg-emerald-400" : "bg-slate-600"}`} />
);

export const LiveBadge = ({ connected, detail }) => (
  <span
    data-testid="live-badge"
    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${
      connected ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" : "bg-slate-700/60 text-slate-400 border border-slate-600/40"
    }`}
    title={detail}
  >
    {connected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
    {connected ? "LIVE" : "OFFLINE"}
  </span>
);
