import React, { useState, useEffect, useCallback } from "react";
import { Plus, Layers, FileText, Package, Eye } from "lucide-react";
import { API, fetcher } from "./shared";

const CreateServiceModal = ({ onClose, onCreated }) => {
  const [form, setForm] = useState({ name: "", description: "", repo_url: "", owner: "", team: "", environment: "production", criticality: "medium", tech_stack: "" });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await fetcher(`${API}/services`, {
        method: "POST",
        body: JSON.stringify({ ...form, tech_stack: form.tech_stack ? form.tech_stack.split(",").map((s) => s.trim()) : [] }),
      });
      onCreated();
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 w-full max-w-lg mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-white text-lg font-semibold mb-4">Register Service</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input data-testid="service-create-name" required placeholder="Service Name *" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input placeholder="Description" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <input placeholder="Repository URL" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.repo_url} onChange={(e) => setForm({ ...form, repo_url: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input placeholder="Owner" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.owner} onChange={(e) => setForm({ ...form, owner: e.target.value })} />
            <input placeholder="Team" className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.team} onChange={(e) => setForm({ ...form, team: e.target.value })} />
            <select className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}>
              <option value="production">Production</option><option value="staging">Staging</option><option value="development">Development</option>
            </select>
            <select className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.criticality} onChange={(e) => setForm({ ...form, criticality: e.target.value })}>
              <option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
            </select>
          </div>
          <input placeholder="Tech Stack (comma-separated)" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm" value={form.tech_stack} onChange={(e) => setForm({ ...form, tech_stack: e.target.value })} />
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-slate-400 hover:text-white text-sm">Cancel</button>
            <button data-testid="service-create-submit" type="submit" disabled={saving} className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50">{saving ? "Saving..." : "Register"}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export const ServicesTab = ({ onRefresh }) => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const fetchServices = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetcher(`${API}/services`);
      setServices(data);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchServices(); }, [fetchServices]);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this service?")) return;
    try {
      await fetcher(`${API}/services/${id}`, { method: "DELETE" });
      fetchServices();
      onRefresh();
    } catch (e) { console.error(e); }
  };

  const critColors = { critical: "text-red-400 bg-red-500/10 border-red-500/30", high: "text-orange-400 bg-orange-500/10 border-orange-500/30", medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30", low: "text-blue-400 bg-blue-500/10 border-blue-500/30" };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="text-slate-400 text-sm">{services.length} registered service{services.length !== 1 ? "s" : ""}</div>
        <button data-testid="service-create-btn" onClick={() => setShowCreate(true)} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
          <Plus className="w-4 h-4" /> Register Service
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {services.map((s) => (
          <div key={s.id} data-testid={`service-card-${s.name}`} className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-white font-semibold">{s.name}</div>
                <div className="text-xs text-slate-400 mt-0.5">{s.description}</div>
              </div>
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${critColors[s.criticality] || critColors.medium}`}>{s.criticality?.toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs mb-3">
              <div><span className="text-slate-500">Owner:</span> <span className="text-white ml-1">{s.owner || "—"}</span></div>
              <div><span className="text-slate-500">Team:</span> <span className="text-white ml-1">{s.team || "—"}</span></div>
              <div><span className="text-slate-500">Env:</span> <span className="text-white ml-1">{s.environment}</span></div>
              <div><span className="text-slate-500">Open CVEs:</span> <span className={`ml-1 font-medium ${s.open_cves > 0 ? "text-red-400" : "text-emerald-400"}`}>{s.open_cves || 0}</span></div>
            </div>
            {s.tech_stack?.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {s.tech_stack.map((t) => <span key={t} className="px-2 py-0.5 bg-slate-700/50 rounded text-xs text-slate-300">{t}</span>)}
              </div>
            )}
            {s.repo_url && <a href={s.repo_url} target="_blank" rel="noopener noreferrer" className="text-xs text-cyan-400 hover:underline">{s.repo_url}</a>}
            <div className="mt-3 pt-3 border-t border-slate-700/40 flex justify-end">
              <button onClick={() => handleDelete(s.id)} className="text-xs text-red-400 hover:text-red-300 transition-colors">Delete</button>
            </div>
          </div>
        ))}
      </div>
      {loading && <div className="text-center text-slate-400 py-8">Loading services...</div>}
      {!loading && services.length === 0 && <div className="text-center text-slate-500 py-8">No services registered. Seed sample data or add services.</div>}

      {showCreate && <CreateServiceModal onClose={() => setShowCreate(false)} onCreated={() => { setShowCreate(false); fetchServices(); onRefresh(); }} />}
    </div>
  );
};

export const SBOMTab = ({ onRefresh }) => {
  const [sboms, setSboms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedSbom, setSelectedSbom] = useState(null);
  const [sbomDetail, setSbomDetail] = useState(null);

  const fetchSboms = useCallback(async () => {
    setLoading(true);
    try { setSboms(await fetcher(`${API}/sbom/list`)); } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchSboms(); }, [fetchSboms]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await fetcher(`${API}/sbom/generate`, { method: "POST" });
      fetchSboms();
      onRefresh();
    } catch (e) { console.error(e); }
    setGenerating(false);
  };

  const handleView = async (id) => {
    if (selectedSbom === id) { setSelectedSbom(null); setSbomDetail(null); return; }
    try {
      const detail = await fetcher(`${API}/sbom/${id}`);
      setSbomDetail(detail);
      setSelectedSbom(id);
    } catch (e) { console.error(e); }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <div className="text-white font-semibold">Software Bill of Materials</div>
          <div className="text-slate-400 text-xs mt-0.5">Track every dependency in your stack</div>
        </div>
        <button data-testid="sbom-generate-btn" onClick={handleGenerate} disabled={generating} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50">
          <Layers className="w-4 h-4" /> {generating ? "Generating..." : "Generate SBOM"}
        </button>
      </div>

      <div className="space-y-3">
        {sboms.map((s) => (
          <div key={s.id} className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-700/30 transition-colors" onClick={() => handleView(s.id)}>
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-purple-400" />
                <div>
                  <div className="text-white text-sm font-medium">{s.service_name} — {s.environment}</div>
                  <div className="text-xs text-slate-400">{new Date(s.generated_at).toLocaleString()} | {s.total_components} components | Hash: {s.hash?.slice(0, 12)}...</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded">FE: {s.frontend_components}</span>
                <span className="text-xs text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded">BE: {s.backend_components}</span>
                <Eye className="w-4 h-4 text-slate-400" />
              </div>
            </div>
            {selectedSbom === s.id && sbomDetail && (
              <div className="px-4 pb-4 border-t border-slate-700/50 pt-3">
                <div className="text-xs text-slate-400 mb-2">{sbomDetail.components?.length || 0} components</div>
                <div className="max-h-60 overflow-y-auto space-y-1">
                  {(sbomDetail.components || []).map((c, i) => (
                    <div key={i} className="flex items-center justify-between bg-slate-900/50 rounded px-3 py-1.5 text-xs">
                      <div className="flex items-center gap-2">
                        <Package className="w-3 h-3 text-slate-500" />
                        <span className="text-white">{c.name}</span>
                        <span className="text-slate-500">@{c.version}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-1.5 py-0.5 rounded ${c.layer === "frontend" ? "bg-purple-500/10 text-purple-300" : "bg-cyan-500/10 text-cyan-300"}`}>{c.layer}</span>
                        <span className="text-slate-500">{c.type}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-center text-slate-400 py-8">Loading SBOMs...</div>}
        {!loading && sboms.length === 0 && <div className="text-center text-slate-500 py-8">No SBOMs generated yet. Click &quot;Generate SBOM&quot; to create one.</div>}
      </div>
    </div>
  );
};
