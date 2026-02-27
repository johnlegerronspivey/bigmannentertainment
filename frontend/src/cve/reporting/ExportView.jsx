import React, { useState } from "react";
import { Download, FileText, BarChart3, AlertTriangle, Users, Save, Trash2 } from "lucide-react";
import { REPORTING_API } from "../shared";

export const ExportView = ({ days, savedReports, onDelete }) => {
  const [saving, setSaving] = useState(false);
  const [reportName, setReportName] = useState("");

  const downloadFile = (url, filename) => {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleExport = (type, format = "csv") => {
    const base = REPORTING_API;
    if (format === "pdf") {
      if (type === "cves") downloadFile(`${base}/export/cves-pdf`, "cve_database.pdf");
      else if (type === "executive") downloadFile(`${base}/export/executive-pdf?days=${days}`, "executive_report.pdf");
      else if (type === "team") downloadFile(`${base}/export/team-pdf`, "team_performance.pdf");
    } else {
      if (type === "cves") downloadFile(`${base}/export/cves`, "cve_export.csv");
      else if (type === "executive") downloadFile(`${base}/export/executive?days=${days}`, "executive_report.csv");
      else if (type === "team") downloadFile(`${base}/export/team`, "team_performance.csv");
    }
  };

  const handleSave = async () => {
    if (!reportName.trim()) return;
    setSaving(true);
    try {
      await fetch(`${REPORTING_API}/saved`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: reportName, report_type: "executive", config: { days } }),
      });
      setReportName("");
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  const EXPORT_CARDS = [
    { type: "cves", title: "CVE Database", desc: "Full CVE list with all fields", icon: AlertTriangle },
    { type: "executive", title: "Executive Summary", desc: `Summary for last ${days} days`, icon: BarChart3 },
    { type: "team", title: "Team Performance", desc: "Per-owner resolution stats", icon: Users },
  ];

  return (
    <div className="space-y-6">
      <h3 className="text-white font-semibold">Export Reports</h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {EXPORT_CARDS.map(({ type, title, desc, icon: Icon }) => (
          <div key={type} data-testid={`export-card-${type}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5 hover:border-slate-600/60 transition-colors">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-cyan-500/10 rounded-lg"><Icon className="w-5 h-5 text-cyan-400" /></div>
              <span className="text-white font-medium text-sm">{title}</span>
            </div>
            <p className="text-slate-500 text-xs mb-4">{desc}</p>
            <div className="flex items-center gap-2">
              <button data-testid={`export-${type}-csv-btn`} onClick={() => handleExport(type, "csv")} className="flex items-center gap-1.5 bg-slate-700/60 hover:bg-slate-600/60 text-slate-200 px-3 py-1.5 rounded-lg text-xs transition-colors border border-slate-600/40">
                <Download className="w-3.5 h-3.5" /> CSV
              </button>
              <button data-testid={`export-${type}-pdf-btn`} onClick={() => handleExport(type, "pdf")} className="flex items-center gap-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-300 px-3 py-1.5 rounded-lg text-xs transition-colors border border-red-500/30">
                <FileText className="w-3.5 h-3.5" /> PDF
              </button>
            </div>
          </div>
        ))}
      </div>

      <div data-testid="save-report-section" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <p className="text-white font-medium text-sm mb-3">Save Report Configuration</p>
        <div className="flex gap-3">
          <input data-testid="report-name-input" value={reportName} onChange={(e) => setReportName(e.target.value)} placeholder="Report name..." className="flex-1 bg-slate-900/60 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50" />
          <button data-testid="save-report-btn" onClick={handleSave} disabled={saving || !reportName.trim()} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
            <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      {savedReports?.reports?.length > 0 && (
        <div data-testid="saved-reports-list" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <p className="text-white font-medium text-sm mb-3">Saved Reports</p>
          <div className="space-y-2">
            {savedReports.reports.map((r) => (
              <div key={r.id} className="flex items-center justify-between bg-slate-900/40 rounded-lg px-4 py-3">
                <div>
                  <span className="text-white text-sm font-medium">{r.name}</span>
                  <span className="text-slate-500 text-xs ml-2">{r.report_type} — {new Date(r.created_at).toLocaleDateString()}</span>
                </div>
                <button data-testid={`delete-report-${r.id}`} onClick={() => onDelete(r.id)} className="p-1.5 hover:bg-red-500/20 rounded-lg transition-colors">
                  <Trash2 className="w-4 h-4 text-red-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
