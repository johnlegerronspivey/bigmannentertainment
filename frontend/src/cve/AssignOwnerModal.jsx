import React, { useState, useEffect } from "react";
import { Users } from "lucide-react";
import { API, fetcher } from "./shared";

export const AssignOwnerModal = ({ cve, onClose, onAssigned }) => {
  const [form, setForm] = useState({ assigned_to: cve?.assigned_to || "", assigned_team: cve?.assigned_team || "", notes: "" });
  const [owners, setOwners] = useState({ people: [], teams: [] });
  const [saving, setSaving] = useState(false);
  const [customPerson, setCustomPerson] = useState(false);
  const [customTeam, setCustomTeam] = useState(false);

  useEffect(() => {
    fetcher(`${API}/owners`).then(setOwners).catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(`${API}/entries/${cve.id}/owner`, { method: "PUT", body: JSON.stringify(form) });
      onAssigned();
    } catch (err) { console.error(err); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-white text-lg font-semibold mb-1">Assign Owner</h3>
        <p className="text-slate-400 text-sm mb-4">{cve.cve_id} &mdash; {cve.title}</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-slate-400 block mb-1">Assignee</label>
            {!customPerson && owners.people.length > 0 ? (
              <div className="flex gap-2">
                <select data-testid="assign-owner-select" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}>
                  <option value="">Unassigned</option>
                  {owners.people.map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
                <button type="button" onClick={() => setCustomPerson(true)} className="px-3 py-2 text-xs text-cyan-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">New</button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input data-testid="assign-owner-input" placeholder="Enter person name" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_to} onChange={(e) => setForm({ ...form, assigned_to: e.target.value })} />
                {owners.people.length > 0 && <button type="button" onClick={() => setCustomPerson(false)} className="px-3 py-2 text-xs text-slate-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">List</button>}
              </div>
            )}
          </div>
          <div>
            <label className="text-sm text-slate-400 block mb-1">Team</label>
            {!customTeam && owners.teams.length > 0 ? (
              <div className="flex gap-2">
                <select data-testid="assign-team-select" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_team} onChange={(e) => setForm({ ...form, assigned_team: e.target.value })}>
                  <option value="">No Team</option>
                  {owners.teams.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
                <button type="button" onClick={() => setCustomTeam(true)} className="px-3 py-2 text-xs text-cyan-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">New</button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input data-testid="assign-team-input" placeholder="Enter team name" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.assigned_team} onChange={(e) => setForm({ ...form, assigned_team: e.target.value })} />
                {owners.teams.length > 0 && <button type="button" onClick={() => setCustomTeam(false)} className="px-3 py-2 text-xs text-slate-400 bg-slate-900 border border-slate-700 rounded-lg hover:bg-slate-700">List</button>}
              </div>
            )}
          </div>
          <div>
            <label className="text-sm text-slate-400 block mb-1">Notes</label>
            <input placeholder="Assignment notes (optional)" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="assign-owner-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Saving..." : "Assign Owner"}</button>
          </div>
        </form>
      </div>
    </div>
  );
};
