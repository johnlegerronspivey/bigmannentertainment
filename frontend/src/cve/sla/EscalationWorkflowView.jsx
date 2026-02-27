import React, { useState } from "react";
import { CheckCircle2, UserPlus, XCircle } from "lucide-react";
import { SLA_API, fetcher, SeverityBadge } from "../shared";
import { EscStatusBadge } from "./badges";

export const EscalationWorkflowView = ({ escLog, escStats, fetchAll }) => {
  const [actionLoading, setActionLoading] = useState("");
  const [assignModal, setAssignModal] = useState(null);
  const [resolveModal, setResolveModal] = useState(null);
  const [assignee, setAssignee] = useState("");
  const [resolveNote, setResolveNote] = useState("");

  const doAction = async (logId, action, body = {}) => {
    setActionLoading(`${logId}-${action}`);
    try {
      await fetcher(`${SLA_API}/escalation-log/${logId}/${action}`, { method: "POST", body: JSON.stringify(body) });
      fetchAll();
    } catch (e) { console.error(e); }
    setActionLoading("");
  };

  const handleAssign = async () => {
    if (!assignModal || !assignee.trim()) return;
    await doAction(assignModal, "assign", { assignee: assignee.trim(), performed_by: "admin" });
    setAssignModal(null);
    setAssignee("");
  };

  const handleResolve = async () => {
    if (!resolveModal) return;
    await doAction(resolveModal, "resolve", { resolution_note: resolveNote.trim(), performed_by: "admin" });
    setResolveModal(null);
    setResolveNote("");
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { label: "Total", val: escStats?.total || 0, color: "text-white" },
          { label: "Open", val: escStats?.open || 0, color: "text-red-400" },
          { label: "Acknowledged", val: escStats?.acknowledged || 0, color: "text-amber-400" },
          { label: "Assigned", val: escStats?.assigned || 0, color: "text-blue-400" },
          { label: "Resolved", val: escStats?.resolved || 0, color: "text-emerald-400" },
        ].map((s) => (
          <div key={s.label} data-testid={`esc-stat-${s.label.toLowerCase()}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 text-center">
            <div className={`text-xl font-bold ${s.color}`}>{s.val}</div>
            <div className="text-xs text-slate-400 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-4 text-sm">
          Escalation Workflow <span className="text-slate-400 font-normal ml-1">({escLog?.total || 0} total)</span>
        </h3>
        {(escLog?.items || []).length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-6">No escalations triggered yet.</p>
        ) : (
          <div className="space-y-3 max-h-[500px] overflow-y-auto">
            {(escLog?.items || []).map((e) => (
              <div key={e.id} data-testid={`esc-workflow-${e.id}`} className="bg-slate-900/50 rounded-xl p-4 border border-slate-700/30">
                <div className="flex items-center gap-3 flex-wrap mb-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${e.level >= 3 ? "bg-red-500/20 text-red-300" : e.level >= 2 ? "bg-orange-500/20 text-orange-300" : "bg-amber-500/20 text-amber-300"}`}>L{e.level}</span>
                  <span className="text-cyan-400 font-mono text-xs">{e.cve_id}</span>
                  <SeverityBadge severity={e.severity} />
                  <EscStatusBadge status={e.status || "open"} />
                  <span className="text-xs text-slate-500 ml-auto">{new Date(e.created_at).toLocaleString()}</span>
                </div>
                <p className="text-xs text-slate-400 mb-2">{e.rule_name} — {e.actual_pct}% of SLA elapsed</p>
                {e.assignee && <p className="text-xs text-blue-400 mb-1">Assigned to: {e.assignee}</p>}
                {e.resolution_note && <p className="text-xs text-emerald-400 mb-1">Resolution: {e.resolution_note}</p>}

                {(e.status || "open") !== "resolved" && (
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-slate-700/30">
                    {(e.status || "open") === "open" && (
                      <button data-testid={`ack-btn-${e.id}`} onClick={() => doAction(e.id, "acknowledge", { performed_by: "admin" })} disabled={actionLoading === `${e.id}-acknowledge`} className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 rounded-lg text-xs transition-colors disabled:opacity-50">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Acknowledge
                      </button>
                    )}
                    {(e.status || "open") !== "resolved" && (
                      <button data-testid={`assign-btn-${e.id}`} onClick={() => { setAssignModal(e.id); setAssignee(e.assignee || ""); }} className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 rounded-lg text-xs transition-colors">
                        <UserPlus className="w-3.5 h-3.5" /> Assign
                      </button>
                    )}
                    <button data-testid={`resolve-btn-${e.id}`} onClick={() => setResolveModal(e.id)} className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 rounded-lg text-xs transition-colors">
                      <XCircle className="w-3.5 h-3.5" /> Resolve
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {assignModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setAssignModal(null)}>
          <div data-testid="assign-modal" className="bg-slate-800 border border-slate-600 rounded-xl p-6 w-full max-w-sm" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-white font-semibold text-sm mb-4">Assign Escalation</h3>
            <input data-testid="assign-input" className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm mb-4" placeholder="Assignee name or email" value={assignee} onChange={(e) => setAssignee(e.target.value)} />
            <div className="flex justify-end gap-2">
              <button onClick={() => setAssignModal(null)} className="px-3 py-2 bg-slate-700 text-slate-300 rounded-lg text-xs">Cancel</button>
              <button data-testid="assign-confirm-btn" onClick={handleAssign} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs">Assign</button>
            </div>
          </div>
        </div>
      )}

      {resolveModal && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setResolveModal(null)}>
          <div data-testid="resolve-modal" className="bg-slate-800 border border-slate-600 rounded-xl p-6 w-full max-w-sm" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-white font-semibold text-sm mb-4">Resolve Escalation</h3>
            <textarea data-testid="resolve-note-input" className="w-full bg-slate-900/70 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm mb-4 h-24 resize-none" placeholder="Resolution note (optional)" value={resolveNote} onChange={(e) => setResolveNote(e.target.value)} />
            <div className="flex justify-end gap-2">
              <button onClick={() => setResolveModal(null)} className="px-3 py-2 bg-slate-700 text-slate-300 rounded-lg text-xs">Cancel</button>
              <button data-testid="resolve-confirm-btn" onClick={handleResolve} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs">Resolve</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
