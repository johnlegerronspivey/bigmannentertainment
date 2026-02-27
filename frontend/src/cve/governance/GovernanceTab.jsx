import React, { useState, useEffect, useCallback } from "react";
import { Gauge, TrendingUp, Target, Users } from "lucide-react";
import { API, GOVERNANCE_API, fetcher } from "../shared";
import { OverviewView } from "./OverviewView";
import { TrendsView } from "./TrendsView";
import { SLAComplianceView } from "./SLAComplianceView";
import { OwnershipView } from "./OwnershipView";

export const GovernanceTab = ({ onRefresh }) => {
  const [metrics, setMetrics] = useState(null);
  const [trends, setTrends] = useState(null);
  const [sla, setSla] = useState(null);
  const [ownership, setOwnership] = useState(null);
  const [mttr, setMttr] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("overview");
  const [ownerInfo, setOwnerInfo] = useState(null);
  const [unassigned, setUnassigned] = useState(null);
  const [govAssignTarget, setGovAssignTarget] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [m, t, s, o, mt, ow, ua] = await Promise.all([
        fetcher(`${GOVERNANCE_API}/metrics`),
        fetcher(`${GOVERNANCE_API}/trends?days=30`),
        fetcher(`${GOVERNANCE_API}/sla`),
        fetcher(`${GOVERNANCE_API}/ownership`),
        fetcher(`${GOVERNANCE_API}/mttr`),
        fetcher(`${API}/owners`),
        fetcher(`${API}/unassigned?limit=20`),
      ]);
      setMetrics(m); setTrends(t); setSla(s); setOwnership(o); setMttr(mt); setOwnerInfo(ow); setUnassigned(ua);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading || !metrics) return (
    <div data-testid="governance-loading" className="space-y-6 animate-pulse">
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {[1,2,3,4].map((i) => <div key={i} className="h-9 w-28 bg-slate-800/60 rounded-lg" />)}
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {[...Array(6)].map((_, i) => <div key={i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5"><div className="h-4 bg-slate-700 rounded w-2/3 mb-3" /><div className="h-7 bg-slate-700 rounded w-1/3" /></div>)}
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => <div key={i} className="bg-slate-800/60 border border-slate-700/50 rounded-xl h-52" />)}
      </div>
    </div>
  );

  const views = [
    { id: "overview", label: "Overview", icon: Gauge },
    { id: "trends", label: "Trends", icon: TrendingUp },
    { id: "sla", label: "SLA Compliance", icon: Target },
    { id: "ownership", label: "Ownership", icon: Users },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 border-b border-slate-700/50 pb-2">
        {views.map((v) => (
          <button key={v.id} data-testid={`gov-view-${v.id}`} onClick={() => setView(v.id)} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${view === v.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <v.icon className="w-4 h-4" /> {v.label}
          </button>
        ))}
      </div>

      {view === "overview" && <OverviewView metrics={metrics} ownership={ownership} mttr={mttr} />}
      {view === "trends" && <TrendsView metrics={metrics} trends={trends} />}
      {view === "sla" && <SLAComplianceView sla={sla} />}
      {view === "ownership" && (
        <OwnershipView
          ownership={ownership}
          ownerInfo={ownerInfo}
          unassigned={unassigned}
          govAssignTarget={govAssignTarget}
          setGovAssignTarget={setGovAssignTarget}
          fetchAll={fetchAll}
          onRefresh={onRefresh}
        />
      )}
    </div>
  );
};
