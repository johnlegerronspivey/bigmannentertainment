import React, { useState, useEffect, useCallback } from "react";
import { Shield, TrendingUp, Users, Download, Scan } from "lucide-react";
import { REPORTING_API, fetcher } from "../shared";
import { ExecutiveView } from "./ExecutiveView";
import { TrendsView } from "./TrendsView";
import { TeamView } from "./TeamView";
import { ScannerView } from "./ScannerView";
import { ExportView } from "./ExportView";

const SUB_TABS = [
  { id: "executive", label: "Executive Summary", icon: Shield },
  { id: "trends", label: "Trends", icon: TrendingUp },
  { id: "team", label: "Team Performance", icon: Users },
  { id: "scanners", label: "Scanner Stats", icon: Scan },
  { id: "export", label: "Export", icon: Download },
];

export const ReportingTab = () => {
  const [subTab, setSubTab] = useState("executive");
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [severityTrends, setSeverityTrends] = useState(null);
  const [statusDist, setStatusDist] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [scannerData, setScannerData] = useState(null);
  const [savedReports, setSavedReports] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [sum, tr, sev, st, team, scan, saved] = await Promise.all([
        fetcher(`${REPORTING_API}/summary?days=${days}`),
        fetcher(`${REPORTING_API}/trends?days=${days}`),
        fetcher(`${REPORTING_API}/severity-trends?days=${days}`),
        fetcher(`${REPORTING_API}/status-distribution`),
        fetcher(`${REPORTING_API}/team-performance`),
        fetcher(`${REPORTING_API}/scanner-stats`),
        fetcher(`${REPORTING_API}/saved`),
      ]);
      setSummary(sum); setTrends(tr); setSeverityTrends(sev);
      setStatusDist(st); setTeamData(team); setScannerData(scan); setSavedReports(saved);
    } catch (e) { console.error("Failed to load reporting data:", e); }
    setLoading(false);
  }, [days]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleDeleteReport = async (id) => {
    try {
      await fetcher(`${REPORTING_API}/saved/${id}`, { method: "DELETE" });
      setSavedReports((prev) => ({
        ...prev,
        reports: (prev?.reports || []).filter((r) => r.id !== id),
      }));
    } catch (e) { console.error(e); }
  };

  return (
    <div data-testid="reporting-tab" className="space-y-6">
      <div className="flex items-center gap-1 bg-slate-800/40 rounded-xl p-1 overflow-x-auto">
        {SUB_TABS.map((t) => (
          <button key={t.id} data-testid={`reporting-subtab-${t.id}`} onClick={() => setSubTab(t.id)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all whitespace-nowrap ${subTab === t.id ? "bg-cyan-500/10 text-cyan-400 font-medium" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
            <t.icon className="w-4 h-4" /> {t.label}
          </button>
        ))}
      </div>

      {subTab === "executive" && <ExecutiveView data={summary} loading={loading} />}
      {subTab === "trends" && <TrendsView trends={trends} severityTrends={severityTrends} statusDist={statusDist} loading={loading} days={days} setDays={setDays} />}
      {subTab === "team" && <TeamView data={teamData} loading={loading} />}
      {subTab === "scanners" && <ScannerView data={scannerData} loading={loading} />}
      {subTab === "export" && <ExportView days={days} savedReports={savedReports} onDelete={handleDeleteReport} />}
    </div>
  );
};
