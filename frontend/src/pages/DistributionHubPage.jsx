import React, { useState, useEffect, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import { Send, Upload, Package, Shield, Radio, Film, Music, Image, Video, ChevronDown, ChevronRight, Check, X, RefreshCw, Search, Download, Globe, Zap, BarChart3, FileText, Link2, Clock, CheckCircle2, AlertCircle, Loader2, ArrowRight, Layers, Mic, Share2, Plus, Trash2, Edit3, Copy, Camera, Monitor, Hexagon, Star, Eye, EyeOff, Wifi, WifiOff } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const TABS = [
  { id: "dashboard", label: "Hub Dashboard", icon: BarChart3 },
  { id: "content", label: "Content Library", icon: FileText },
  { id: "distribute", label: "Distribute", icon: Send },
  { id: "templates", label: "Templates", icon: Layers },
  { id: "tracking", label: "Delivery Tracking", icon: Package },
  { id: "rights", label: "Rights & Metadata", icon: Shield },
  { id: "connections", label: "Platform Connections", icon: Link2 },
];

const TYPE_ICONS = { audio: Music, video: Video, image: Image, film: Film };
const TYPE_COLORS = {
  audio: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  video: "bg-green-500/10 text-green-400 border-green-500/20",
  image: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  film: "bg-purple-500/10 text-purple-400 border-purple-500/20",
};

const STATUS_STYLES = {
  delivered: "bg-emerald-500/10 text-emerald-400",
  queued: "bg-yellow-500/10 text-yellow-400",
  export_ready: "bg-cyan-500/10 text-cyan-400",
  preparing: "bg-blue-500/10 text-blue-400",
  delivering: "bg-indigo-500/10 text-indigo-400",
  failed: "bg-red-500/10 text-red-400",
  draft: "bg-gray-500/10 text-gray-400",
};

// Resolve platform IDs to display names (populated from API)
const ALL_HUB_PLATFORMS_MAP = {};

function getToken() {
  return localStorage.getItem("token");
}

async function apiFetch(path, opts = {}) {
  const headers = { Authorization: `Bearer ${getToken()}`, ...opts.headers };
  if (!(opts.body instanceof FormData)) headers["Content-Type"] = "application/json";
  const res = await fetch(`${API}/api/distribution-hub${path}`, { ...opts, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

// ──────────────────────────────────────────────
// HUB DASHBOARD TAB
// ──────────────────────────────────────────────
function HubDashboard({ stats, loading }) {
  if (loading) return <LoadingState text="Loading hub statistics..." />;
  if (!stats) return null;

  const statCards = [
    { label: "Total Content", value: stats.content_count, icon: FileText, color: "text-blue-400" },
    { label: "Deliveries", value: stats.total_deliveries, icon: Send, color: "text-purple-400" },
    { label: "Delivered", value: stats.delivered, icon: CheckCircle2, color: "text-emerald-400" },
    { label: "Queued", value: stats.queued, icon: Clock, color: "text-yellow-400" },
    { label: "Export Ready", value: stats.export_ready, icon: Download, color: "text-cyan-400" },
    { label: "Failed", value: stats.failed, icon: AlertCircle, color: "text-red-400" },
  ];

  return (
    <div data-testid="hub-dashboard">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {statCards.map((s) => (
          <div key={s.label} className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-4" data-testid={`stat-${s.label.toLowerCase().replace(/\s/g, "-")}`}>
            <s.icon className={`w-5 h-5 ${s.color} mb-2`} />
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-xs text-gray-400 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Content Types</h3>
          <div className="space-y-3">
            {Object.entries(stats.content_types || {}).map(([type, count]) => {
              const Icon = TYPE_ICONS[type] || FileText;
              return (
                <div key={type} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-300 capitalize">{type}</span>
                  </div>
                  <span className="text-white font-medium">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Distribution Overview</h3>
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1">
              <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${stats.success_rate}%` }} />
              </div>
            </div>
            <span className="text-emerald-400 font-bold text-lg">{stats.success_rate}%</span>
          </div>
          <p className="text-gray-400 text-sm">Success rate across {stats.total_platforms_available} available platforms</p>
        </div>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────
// CONTENT LIBRARY TAB
// ──────────────────────────────────────────────
function ContentLibrary({ content, loading, onRefresh, onAddContent }) {
  const [filter, setFilter] = useState("all");
  const [showAddForm, setShowAddForm] = useState(false);

  const filtered = filter === "all" ? content : content.filter((c) => c.content_type === filter);

  return (
    <div data-testid="content-library">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex gap-2 flex-wrap">
          {["all", "audio", "video", "image", "film"].map((f) => (
            <button key={f} onClick={() => setFilter(f)} data-testid={`filter-${f}`}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors capitalize ${filter === f ? "bg-purple-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"}`}>
              {f}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <button onClick={onRefresh} className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 text-gray-400" data-testid="refresh-content-btn"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={() => setShowAddForm(!showAddForm)} data-testid="add-content-btn"
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium">
            <Upload className="w-4 h-4" /> Add Content
          </button>
        </div>
      </div>

      {showAddForm && <AddContentForm onSubmit={(data) => { onAddContent(data); setShowAddForm(false); }} onCancel={() => setShowAddForm(false)} />}

      {loading ? <LoadingState text="Loading content..." /> : filtered.length === 0 ? (
        <EmptyState icon={FileText} text="No content yet" subtext="Add your first piece of content to start distributing" />
      ) : (
        <div className="grid gap-4">
          {filtered.map((item) => {
            const Icon = TYPE_ICONS[item.content_type] || FileText;
            const colorClass = TYPE_COLORS[item.content_type] || TYPE_COLORS.audio;
            return (
              <div key={item.id} className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-4 hover:border-gray-600/50 transition-colors" data-testid={`content-item-${item.id}`}>
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-lg border flex items-center justify-center ${colorClass}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-white font-medium truncate">{item.title}</h4>
                    <p className="text-gray-400 text-sm capitalize">{item.content_type}{item.metadata?.basic?.artist ? ` - ${item.metadata.basic.artist}` : ""}{item.metadata?.basic?.genre ? ` / ${item.metadata.basic.genre}` : ""}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">{new Date(item.created_at).toLocaleDateString()}</p>
                    {item.metadata?.advanced?.isrc && <span className="text-xs text-cyan-400">ISRC: {item.metadata.advanced.isrc}</span>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// ADD CONTENT FORM
// ──────────────────────────────────────────────
function AddContentForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState({ title: "", content_type: "audio", description: "", artist: "", album: "", genre: "", release_date: "", isrc: "", upc: "", copyright_holder: "", publisher: "", record_label: "", licensing_type: "", tags: "" });
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    try {
      if (file) {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("title", form.title);
        fd.append("content_type", form.content_type);
        fd.append("description", form.description);
        fd.append("artist", form.artist);
        fd.append("genre", form.genre);
        const res = await fetch(`${API}/api/distribution-hub/upload`, {
          method: "POST", headers: { Authorization: `Bearer ${getToken()}` }, body: fd,
        });
        if (!res.ok) throw new Error("Upload failed");
        onSubmit(await res.json());
      } else {
        const data = { ...form, tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean) };
        await apiFetch("/content", { method: "POST", body: JSON.stringify(data) });
        onSubmit(data);
      }
    } catch (err) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-800/80 border border-gray-700/50 rounded-xl p-6 mb-6" data-testid="add-content-form">
      <h3 className="text-lg font-semibold text-white mb-4">Add New Content</h3>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Title *</label>
          <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required data-testid="content-title-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Content Type *</label>
          <select value={form.content_type} onChange={(e) => setForm({ ...form, content_type: e.target.value })} data-testid="content-type-select"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none">
            <option value="audio">Audio</option>
            <option value="video">Video</option>
            <option value="image">Image</option>
            <option value="film">Film</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Artist</label>
          <input value={form.artist} onChange={(e) => setForm({ ...form, artist: e.target.value })} data-testid="content-artist-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Genre</label>
          <input value={form.genre} onChange={(e) => setForm({ ...form, genre: e.target.value })} data-testid="content-genre-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm text-gray-400 mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} data-testid="content-desc-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Upload File</label>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} data-testid="content-file-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-purple-600 file:text-white hover:file:bg-purple-700" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Tags (comma-separated)</label>
          <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} data-testid="content-tags-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" placeholder="hip-hop, single, 2026" />
        </div>

        {/* Advanced metadata fields */}
        <div>
          <label className="block text-sm text-gray-400 mb-1">ISRC</label>
          <input value={form.isrc} onChange={(e) => setForm({ ...form, isrc: e.target.value })} data-testid="content-isrc-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" placeholder="e.g. QZ9H8xxxxxx" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">UPC / EAN</label>
          <input value={form.upc} onChange={(e) => setForm({ ...form, upc: e.target.value })} data-testid="content-upc-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Copyright Holder</label>
          <input value={form.copyright_holder} onChange={(e) => setForm({ ...form, copyright_holder: e.target.value })} data-testid="content-copyright-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Publisher</label>
          <input value={form.publisher} onChange={(e) => setForm({ ...form, publisher: e.target.value })} data-testid="content-publisher-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Record Label</label>
          <input value={form.record_label} onChange={(e) => setForm({ ...form, record_label: e.target.value })} data-testid="content-label-input"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Licensing Type</label>
          <select value={form.licensing_type} onChange={(e) => setForm({ ...form, licensing_type: e.target.value })} data-testid="content-licensing-select"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none">
            <option value="">Select...</option>
            <option value="exclusive">Exclusive</option>
            <option value="non_exclusive">Non-Exclusive</option>
            <option value="creative_commons">Creative Commons</option>
            <option value="public_domain">Public Domain</option>
            <option value="sync_license">Sync License</option>
            <option value="mechanical_license">Mechanical License</option>
          </select>
        </div>
      </div>
      <div className="flex gap-3 mt-6">
        <button type="submit" disabled={uploading || !form.title} data-testid="submit-content-btn"
          className="flex items-center gap-2 px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium disabled:opacity-50">
          {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          {uploading ? "Uploading..." : "Add Content"}
        </button>
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm" data-testid="cancel-content-btn">Cancel</button>
      </div>
    </form>
  );
}

// ──────────────────────────────────────────────
// DISTRIBUTE TAB
// ──────────────────────────────────────────────
function DistributeTab({ content, platforms, onDistribute, distributing, templates }) {
  const [selectedContent, setSelectedContent] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [search, setSearch] = useState("");
  const [appliedTemplate, setAppliedTemplate] = useState(null);
  const [liveAdapters, setLiveAdapters] = useState([]);

  useEffect(() => {
    apiFetch("/adapters").then((d) => setLiveAdapters(d.adapters || [])).catch(() => {});
  }, []);

  const toggleCategory = (catId) => setExpandedCategories((prev) => ({ ...prev, [catId]: !prev[catId] }));
  const togglePlatform = (pid) => { setSelectedPlatforms((prev) => prev.includes(pid) ? prev.filter((x) => x !== pid) : [...prev, pid]); setAppliedTemplate(null); };

  const applyTemplate = (tpl) => {
    setSelectedPlatforms(tpl.platform_ids || []);
    setAppliedTemplate(tpl);
    // Auto-expand relevant categories
    const catSet = {};
    (tpl.platform_ids || []).forEach((pid) => {
      const p = allPlatformsList.find((x) => x.id === pid);
      if (p) catSet[p.category] = true;
    });
    setExpandedCategories(catSet);
  };

  const handleDistribute = () => {
    if (!selectedContent || selectedPlatforms.length === 0) return;
    onDistribute(selectedContent.id, selectedPlatforms);
  };

  const allPlatformsList = platforms ? Object.entries(platforms.categories || {}).flatMap(([catId, catData]) =>
    Object.entries(catData.platforms || {}).map(([pid, p]) => ({ ...p, id: pid, category: catId, categoryLabel: catData.label }))
  ) : [];

  const filteredPlatforms = search ? allPlatformsList.filter((p) => p.name.toLowerCase().includes(search.toLowerCase())) : allPlatformsList;

  // Group by category
  const grouped = {};
  filteredPlatforms.forEach((p) => {
    if (!grouped[p.category]) grouped[p.category] = { label: p.categoryLabel, platforms: [] };
    grouped[p.category].platforms.push(p);
  });

  const selectableContentForType = selectedContent ? allPlatformsList.filter((p) => p.formats.includes(selectedContent.content_type)) : allPlatformsList;
  const compatiblePlatformIds = new Set(selectableContentForType.map((p) => p.id));

  return (
    <div data-testid="distribute-tab">
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Step 1: Select Content */}
        <div>
          <div className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-5">
            <h3 className="text-white font-semibold mb-1 flex items-center gap-2"><span className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center text-xs font-bold">1</span> Select Content</h3>
            <p className="text-gray-400 text-xs mb-4">Choose content to distribute</p>
            {content.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-6">No content available. Add content first.</p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {content.map((item) => {
                  const Icon = TYPE_ICONS[item.content_type] || FileText;
                  const isSelected = selectedContent?.id === item.id;
                  return (
                    <button key={item.id} onClick={() => { setSelectedContent(item); setSelectedPlatforms([]); }}
                      data-testid={`select-content-${item.id}`}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${isSelected ? "border-purple-500 bg-purple-500/10" : "border-gray-700 hover:border-gray-600 bg-gray-900/50"}`}>
                      <div className="flex items-center gap-3">
                        <Icon className={`w-5 h-5 ${isSelected ? "text-purple-400" : "text-gray-500"}`} />
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium truncate ${isSelected ? "text-white" : "text-gray-300"}`}>{item.title}</p>
                          <p className="text-xs text-gray-500 capitalize">{item.content_type}</p>
                        </div>
                        {isSelected && <Check className="w-4 h-4 text-purple-400" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Select Platforms */}
        <div className="lg:col-span-2">
          <div className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-5">
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-white font-semibold flex items-center gap-2"><span className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center text-xs font-bold">2</span> Select Platforms</h3>
              <span className="text-sm text-purple-400 font-medium">{selectedPlatforms.length} selected</span>
            </div>
            <p className="text-gray-400 text-xs mb-4">Choose where to send your content</p>

            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search platforms..."
                data-testid="platform-search-input"
                className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
            </div>

            {/* Template Quick-Select */}
            {templates && templates.length > 0 && (
              <div className="mb-4" data-testid="template-quick-select">
                <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wide">Quick Templates</p>
                <div className="flex gap-2 flex-wrap">
                  {templates.map((tpl) => {
                    const isApplied = appliedTemplate?.id === tpl.id;
                    return (
                      <button key={tpl.id} onClick={() => applyTemplate(tpl)} data-testid={`apply-template-${tpl.id}`}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${isApplied ? "bg-purple-600 text-white border-purple-500" : "bg-gray-800/80 text-gray-300 border-gray-700 hover:border-purple-500/50 hover:text-white"}`}>
                        <TemplateIcon name={tpl.icon} className="w-3.5 h-3.5" />
                        {tpl.name}
                        <span className={`ml-1 px-1.5 py-0.5 rounded text-[10px] ${isApplied ? "bg-white/20" : "bg-gray-700 text-gray-400"}`}>{tpl.platform_count || tpl.platform_ids?.length || 0}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            <div className="space-y-2 max-h-[28rem] overflow-y-auto pr-1">
              {Object.entries(grouped).map(([catId, catData]) => (
                <div key={catId} className="border border-gray-700/50 rounded-lg overflow-hidden">
                  <button onClick={() => toggleCategory(catId)} className="w-full flex items-center justify-between p-3 bg-gray-900/50 hover:bg-gray-900/80 transition-colors" data-testid={`category-${catId}`}>
                    <span className="text-sm font-medium text-gray-300">{catData.label} ({catData.platforms.length})</span>
                    {expandedCategories[catId] ? <ChevronDown className="w-4 h-4 text-gray-500" /> : <ChevronRight className="w-4 h-4 text-gray-500" />}
                  </button>
                  {expandedCategories[catId] && (
                    <div className="grid sm:grid-cols-2 gap-2 p-3">
                      {catData.platforms.map((p) => {
                        const isCompatible = !selectedContent || compatiblePlatformIds.has(p.id);
                        const isSelected = selectedPlatforms.includes(p.id);
                        return (
                          <button key={p.id} onClick={() => isCompatible && togglePlatform(p.id)} disabled={!isCompatible}
                            data-testid={`platform-${p.id}`}
                            className={`text-left p-2.5 rounded-lg border text-sm transition-colors ${!isCompatible ? "opacity-40 cursor-not-allowed border-gray-800" : isSelected ? "border-purple-500 bg-purple-500/10" : "border-gray-700 hover:border-gray-600"}`}>
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${p.method === "api_push" ? "bg-green-400" : "bg-cyan-400"}`} />
                              <span className={isSelected ? "text-white font-medium" : "text-gray-300"}>{p.name}</span>
                              {isSelected && <Check className="w-3.5 h-3.5 text-purple-400 ml-auto" />}
                            </div>
                            <div className="flex items-center gap-2 mt-1 ml-4">
                              <span className={`text-[10px] px-1.5 py-0.5 rounded ${p.method === "api_push" ? "bg-green-500/10 text-green-400" : "bg-cyan-500/10 text-cyan-400"}`}>
                                {p.method === "api_push" ? "Auto-Push" : "Export"}
                              </span>
                              {liveAdapters.includes(p.id) && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-semibold">LIVE API</span>
                              )}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Distribute Button */}
            <div className="mt-6 pt-4 border-t border-gray-700/50 flex items-center justify-between">
              <p className="text-gray-400 text-sm">
                {selectedContent ? `"${selectedContent.title}"` : "No content selected"} → {selectedPlatforms.length} platform{selectedPlatforms.length !== 1 ? "s" : ""}
              </p>
              <button onClick={handleDistribute} disabled={!selectedContent || selectedPlatforms.length === 0 || distributing}
                data-testid="distribute-btn"
                className="flex items-center gap-2 px-6 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-semibold disabled:opacity-50 transition-colors">
                {distributing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {distributing ? "Distributing..." : "Distribute Now"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────
// DELIVERY TRACKING TAB
// ──────────────────────────────────────────────
function DeliveryTracking({ deliveries, loading, onRefresh, onMarkDelivered, onExport, onRetry, activeBatchId, userId }) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [batchProgress, setBatchProgress] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const pingRef = useRef(null);
  const filtered = statusFilter === "all" ? deliveries : deliveries.filter((d) => d.status === statusFilter);

  // WebSocket connection for real-time delivery updates
  useEffect(() => {
    if (!activeBatchId || !userId) { setBatchProgress(null); setWsConnected(false); return; }

    const wsUrl = API.replace(/^http/, "ws") + `/api/ws/delivery?user_id=${userId}`;
    let ws;
    let reconnectTimeout;
    let active = true;

    const connect = () => {
      if (!active) return;
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        // Start ping keepalive every 25s
        pingRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) ws.send("ping");
        }, 25000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "pong" || data.type === "heartbeat") return;

          if (data.type === "batch_progress" && data.batch_id === activeBatchId) {
            setBatchProgress(data);
            if (data.is_complete) {
              setBatchProgress(null);
              onRefresh();
            }
          }

          if (data.type === "delivery_update" && data.batch_id === activeBatchId) {
            // Refresh deliveries list when individual delivery updates arrive
            onRefresh();
          }
        } catch {}
      };

      ws.onclose = () => {
        setWsConnected(false);
        if (pingRef.current) clearInterval(pingRef.current);
        // Reconnect after 3s if still active
        if (active) reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    // Also do an initial HTTP fetch for current progress
    (async () => {
      try {
        const data = await apiFetch(`/deliveries/batch/${activeBatchId}/progress`);
        if (active) {
          setBatchProgress(data);
          if (data.is_complete) { setBatchProgress(null); onRefresh(); }
        }
      } catch {}
    })();

    return () => {
      active = false;
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (pingRef.current) clearInterval(pingRef.current);
      if (ws && ws.readyState <= WebSocket.OPEN) ws.close();
      wsRef.current = null;
      setWsConnected(false);
    };
  }, [activeBatchId, userId, onRefresh]);

  return (
    <div data-testid="delivery-tracking">
      {/* Batch Progress Bar */}
      {batchProgress && !batchProgress.is_complete && (
        <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-xl p-4 mb-6" data-testid="batch-progress">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
              <span className="text-white font-medium text-sm">Delivering to {batchProgress.total} platforms...</span>
            </div>
            <div className="flex items-center gap-3">
              <span data-testid="ws-status" className={`flex items-center gap-1 text-xs ${wsConnected ? "text-emerald-400" : "text-yellow-400"}`}>
                {wsConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                {wsConnected ? "Live" : "Reconnecting..."}
              </span>
              <span className="text-indigo-300 font-bold">{batchProgress.progress_pct}%</span>
            </div>
          </div>
          <div className="h-2.5 bg-gray-800 rounded-full overflow-hidden mb-2">
            <div className="h-full bg-indigo-500 rounded-full transition-all duration-500" style={{ width: `${batchProgress.progress_pct}%` }} />
          </div>
          <div className="flex gap-4 text-xs">
            <span className="text-emerald-400">{batchProgress.delivered} delivered</span>
            <span className="text-indigo-400">{batchProgress.delivering} in progress</span>
            <span className="text-cyan-400">{batchProgress.export_ready} export ready</span>
            <span className="text-yellow-400">{batchProgress.queued} queued</span>
            {batchProgress.failed > 0 && <span className="text-red-400">{batchProgress.failed} failed</span>}
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex gap-2 flex-wrap">
          {["all", "queued", "preparing", "delivering", "delivered", "export_ready", "failed"].map((s) => (
            <button key={s} onClick={() => setStatusFilter(s)} data-testid={`delivery-filter-${s}`}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-colors ${statusFilter === s ? "bg-purple-600 text-white" : "bg-gray-800 text-gray-400 hover:text-white"}`}>
              {s.replace("_", " ")}
            </button>
          ))}
        </div>
        <button onClick={onRefresh} className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded-lg hover:bg-gray-700 text-gray-400 text-sm" data-testid="refresh-deliveries-btn">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {loading ? <LoadingState text="Loading deliveries..." /> : filtered.length === 0 ? (
        <EmptyState icon={Package} text="No deliveries yet" subtext="Distribute content to see delivery status here" />
      ) : (
        <div className="space-y-3">
          {filtered.map((d) => (
            <div key={d.id} className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-4" data-testid={`delivery-${d.id}`}>
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="text-white font-medium truncate">{d.content_title}</h4>
                    <ArrowRight className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                    <span className="text-gray-300 text-sm">{d.platform_name}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 flex-wrap">
                    <span className="text-xs text-gray-500">{d.platform_category} | Batch: {d.batch_id?.slice(0, 8)}...</span>
                    {d.platform_response?.message && (
                      <span className="text-xs text-gray-500 italic">- {d.platform_response.message.slice(0, 60)}</span>
                    )}
                  </div>
                  {d.error_message && (
                    <p className="text-xs text-red-400 mt-1">{d.error_message}</p>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${STATUS_STYLES[d.status] || STATUS_STYLES.draft}`}>
                    {d.status === "delivering" && <Loader2 className="w-3 h-3 inline mr-1 animate-spin" />}
                    {d.status?.replace("_", " ")}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${d.delivery_method === "api_push" ? "bg-green-500/10 text-green-400" : "bg-cyan-500/10 text-cyan-400"}`}>
                    {d.delivery_method === "api_push" ? "Auto" : "Export"}
                  </span>
                  {d.platform_response?.platform_content_id && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400">LIVE</span>
                  )}
                  {d.status === "export_ready" && (
                    <button onClick={() => onExport(d.id)} className="px-2 py-1 bg-cyan-600/20 text-cyan-400 rounded text-xs hover:bg-cyan-600/30" data-testid={`export-${d.id}`}>
                      <Download className="w-3 h-3 inline mr-1" />Export
                    </button>
                  )}
                  {d.status === "failed" && onRetry && (
                    <button onClick={() => onRetry(d.id)} className="px-2 py-1 bg-amber-600/20 text-amber-400 rounded text-xs hover:bg-amber-600/30" data-testid={`retry-${d.id}`}>
                      <RefreshCw className="w-3 h-3 inline mr-1" />Retry
                    </button>
                  )}
                  {(d.status === "queued" || d.status === "export_ready") && (
                    <button onClick={() => onMarkDelivered(d.id)} className="px-2 py-1 bg-emerald-600/20 text-emerald-400 rounded text-xs hover:bg-emerald-600/30" data-testid={`mark-delivered-${d.id}`}>
                      <CheckCircle2 className="w-3 h-3 inline mr-1" />Delivered
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// RIGHTS & METADATA TAB
// ──────────────────────────────────────────────
function RightsMetadataTab({ content, onUpdateMetadata }) {
  const [selected, setSelected] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({});

  const startEdit = (item) => {
    setSelected(item);
    setFormData({
      title: item.title || "",
      artist: item.metadata?.basic?.artist || "",
      genre: item.metadata?.basic?.genre || "",
      description: item.description || "",
      isrc: item.metadata?.advanced?.isrc || "",
      upc: item.metadata?.advanced?.upc || "",
      copyright_holder: item.metadata?.advanced?.copyright_holder || "",
      publisher: item.metadata?.advanced?.publisher || "",
      record_label: item.metadata?.advanced?.record_label || "",
      licensing_type: item.metadata?.advanced?.licensing_type || "",
      copyright_info: item.rights?.copyright_info || "",
      licensing_terms: item.rights?.licensing_terms || "",
    });
    setEditMode(true);
  };

  const handleSave = async () => {
    if (!selected) return;
    await onUpdateMetadata(selected.id, {
      title: formData.title,
      description: formData.description,
      basic: { artist: formData.artist, genre: formData.genre },
      advanced: { isrc: formData.isrc, upc: formData.upc, copyright_holder: formData.copyright_holder, publisher: formData.publisher, record_label: formData.record_label, licensing_type: formData.licensing_type },
      rights: { copyright_info: formData.copyright_info, licensing_terms: formData.licensing_terms },
    });
    setEditMode(false);
    setSelected(null);
  };

  return (
    <div data-testid="rights-metadata-tab">
      {editMode && selected ? (
        <div className="bg-gray-800/80 border border-gray-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Edit Metadata & Rights — {selected.title}</h3>
            <button onClick={() => setEditMode(false)} className="text-gray-400 hover:text-white" data-testid="close-edit-btn"><X className="w-5 h-5" /></button>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {Object.entries(formData).map(([key, val]) => (
              <div key={key}>
                <label className="block text-sm text-gray-400 mb-1 capitalize">{key.replace(/_/g, " ")}</label>
                {key === "licensing_terms" || key === "copyright_info" ? (
                  <textarea value={val} onChange={(e) => setFormData({ ...formData, [key]: e.target.value })} rows={2} data-testid={`meta-${key}`}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
                ) : (
                  <input value={val} onChange={(e) => setFormData({ ...formData, [key]: e.target.value })} data-testid={`meta-${key}`}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" />
                )}
              </div>
            ))}
          </div>
          <div className="flex gap-3 mt-6">
            <button onClick={handleSave} data-testid="save-metadata-btn" className="flex items-center gap-2 px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium">
              <Check className="w-4 h-4" /> Save Changes
            </button>
            <button onClick={() => setEditMode(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm">Cancel</button>
          </div>
        </div>
      ) : (
        <>
          <p className="text-gray-400 text-sm mb-6">Click on any content to edit its metadata, rights information, and licensing details.</p>
          {content.length === 0 ? (
            <EmptyState icon={Shield} text="No content to manage" subtext="Add content to the hub first" />
          ) : (
            <div className="space-y-3">
              {content.map((item) => {
                const Icon = TYPE_ICONS[item.content_type] || FileText;
                return (
                  <button key={item.id} onClick={() => startEdit(item)} className="w-full text-left bg-gray-800/60 border border-gray-700/50 rounded-xl p-4 hover:border-purple-500/30 transition-colors"
                    data-testid={`rights-item-${item.id}`}>
                    <div className="flex items-center gap-4">
                      <Icon className="w-5 h-5 text-gray-400" />
                      <div className="flex-1 min-w-0">
                        <h4 className="text-white font-medium">{item.title}</h4>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {item.metadata?.advanced?.isrc && <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded">ISRC: {item.metadata.advanced.isrc}</span>}
                          {item.metadata?.advanced?.upc && <span className="text-[10px] px-1.5 py-0.5 bg-green-500/10 text-green-400 rounded">UPC: {item.metadata.advanced.upc}</span>}
                          {item.metadata?.advanced?.copyright_holder && <span className="text-[10px] px-1.5 py-0.5 bg-amber-500/10 text-amber-400 rounded">&copy; {item.metadata.advanced.copyright_holder}</span>}
                          {item.metadata?.advanced?.licensing_type && <span className="text-[10px] px-1.5 py-0.5 bg-purple-500/10 text-purple-400 rounded">{item.metadata.advanced.licensing_type}</span>}
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// PLATFORM CONNECTIONS TAB
// ──────────────────────────────────────────────
const PLATFORM_COLORS = {
  youtube: { accent: "text-red-400", border: "border-red-500/30", bg: "bg-red-500/10", dot: "bg-red-400" },
  twitter_x: { accent: "text-sky-400", border: "border-sky-500/30", bg: "bg-sky-500/10", dot: "bg-sky-400" },
  tiktok: { accent: "text-pink-400", border: "border-pink-500/30", bg: "bg-pink-500/10", dot: "bg-pink-400" },
  soundcloud: { accent: "text-orange-400", border: "border-orange-500/30", bg: "bg-orange-500/10", dot: "bg-orange-400" },
  vimeo: { accent: "text-cyan-400", border: "border-cyan-500/30", bg: "bg-cyan-500/10", dot: "bg-cyan-400" },
  bluesky: { accent: "text-blue-400", border: "border-blue-500/30", bg: "bg-blue-500/10", dot: "bg-blue-400" },
  discord: { accent: "text-indigo-400", border: "border-indigo-500/30", bg: "bg-indigo-500/10", dot: "bg-indigo-400" },
  telegram: { accent: "text-sky-300", border: "border-sky-400/30", bg: "bg-sky-400/10", dot: "bg-sky-300" },
  instagram: { accent: "text-fuchsia-400", border: "border-fuchsia-500/30", bg: "bg-fuchsia-500/10", dot: "bg-fuchsia-400" },
  facebook: { accent: "text-blue-500", border: "border-blue-600/30", bg: "bg-blue-600/10", dot: "bg-blue-500" },
};

const DEFAULT_COLOR = { accent: "text-purple-400", border: "border-purple-500/30", bg: "bg-purple-500/10", dot: "bg-purple-400" };

function CredentialField({ field, value, onChange }) {
  const [visible, setVisible] = useState(false);
  const isPassword = field.type === "password";

  return (
    <div className="space-y-1">
      <label className="text-xs text-gray-400 font-medium">{field.label}</label>
      <div className="relative">
        <input
          type={isPassword && !visible ? "password" : "text"}
          value={value || ""}
          onChange={(e) => onChange(field.key, e.target.value)}
          placeholder={field.placeholder}
          data-testid={`cred-field-${field.key}`}
          className="w-full bg-gray-900/80 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500/30 pr-10"
        />
        {isPassword && (
          <button type="button" onClick={() => setVisible(!visible)} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300" data-testid={`toggle-vis-${field.key}`}>
            {visible ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>
      {field.help && <p className="text-[11px] text-gray-500">{field.help}</p>}
    </div>
  );
}

function PlatformConnectionsTab({ connectedPlatforms, onConnect, onDisconnect }) {
  const [guide, setGuide] = useState(null);
  const [loadingGuide, setLoadingGuide] = useState(true);
  const [expandedPlatform, setExpandedPlatform] = useState(null);
  const [creds, setCreds] = useState({});
  const [connecting, setConnecting] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await apiFetch("/adapters/credentials-guide");
        setGuide(data.adapters || {});
      } catch (err) {
        console.error("Failed to load credentials guide:", err);
      } finally {
        setLoadingGuide(false);
      }
    })();
  }, []);

  const connectedIds = new Set(connectedPlatforms.map((c) => c.platform_id));

  const handleConnect = async (platformId) => {
    setConnecting(true);
    try {
      await onConnect(platformId, creds);
      setCreds({});
      setExpandedPlatform(null);
    } finally {
      setConnecting(false);
    }
  };

  const handleFieldChange = (key, value) => {
    setCreds((prev) => ({ ...prev, [key]: value }));
  };

  const toggleExpand = (pid) => {
    if (expandedPlatform === pid) {
      setExpandedPlatform(null);
      setCreds({});
    } else {
      setExpandedPlatform(pid);
      setCreds({});
    }
  };

  if (loadingGuide) return <LoadingState text="Loading credentials guide..." />;

  const adapterEntries = guide ? Object.entries(guide) : [];
  const connectedAdapters = adapterEntries.filter(([pid]) => connectedIds.has(pid));
  const availableAdapters = adapterEntries.filter(([pid]) => !connectedIds.has(pid));
  const filteredAvailable = searchTerm
    ? availableAdapters.filter(([, a]) => a.platform_name.toLowerCase().includes(searchTerm.toLowerCase()))
    : availableAdapters;

  return (
    <div data-testid="platform-connections-tab">
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-2">
          <div>
            <h2 className="text-lg font-semibold text-white">API Credentials Manager</h2>
            <p className="text-gray-400 text-sm mt-1">Connect your accounts to enable auto-push delivery. Each platform requires specific API credentials.</p>
          </div>
          <a href="/docs/API_CREDENTIALS_GUIDE.md" target="_blank" rel="noreferrer"
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-xs text-gray-300 hover:text-white hover:border-gray-600 transition-colors whitespace-nowrap"
            data-testid="full-guide-link">
            <FileText className="w-3.5 h-3.5" /> Full Setup Guide
          </a>
        </div>

        {/* Status bar */}
        <div className="flex items-center gap-4 mt-4 p-3 bg-gray-800/40 rounded-lg border border-gray-700/40">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-xs text-gray-400">Connected: <span className="text-white font-medium">{connectedAdapters.length}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-gray-500" />
            <span className="text-xs text-gray-400">Available: <span className="text-white font-medium">{availableAdapters.length}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-xs text-gray-400">Live Adapters: <span className="text-white font-medium">{adapterEntries.length}</span></span>
          </div>
        </div>
      </div>

      {/* Connected Platforms */}
      {connectedAdapters.length > 0 && (
        <div className="mb-10">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Connected Platforms ({connectedAdapters.length})
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            {connectedAdapters.map(([pid, adapter]) => {
              const colors = PLATFORM_COLORS[pid] || DEFAULT_COLOR;
              return (
                <div key={pid} className={`bg-gray-800/60 border ${colors.border} rounded-xl p-5 transition-all`} data-testid={`connected-${pid}`}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-9 h-9 rounded-lg ${colors.bg} flex items-center justify-center`}>
                        <Zap className={`w-4 h-4 ${colors.accent}`} />
                      </div>
                      <div>
                        <span className="text-white font-medium text-sm">{adapter.platform_name}</span>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          <span className="text-[11px] text-emerald-400">Connected</span>
                        </div>
                      </div>
                    </div>
                    <button onClick={() => onDisconnect(pid)}
                      className="px-3 py-1.5 bg-red-500/10 text-red-400 rounded-lg text-xs hover:bg-red-500/20 transition-colors border border-red-500/20"
                      data-testid={`disconnect-${pid}`}>
                      Disconnect
                    </button>
                  </div>
                  <div className="text-[11px] text-gray-500">
                    Fields: {adapter.fields.map((f) => f.label).join(", ")}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Available Platforms */}
      <div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Plus className="w-4 h-4 text-purple-400" />
            Available Platforms ({availableAdapters.length})
          </h3>
          {availableAdapters.length > 3 && (
            <div className="relative w-full sm:w-56">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500" />
              <input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Filter platforms..."
                data-testid="platform-search-input"
                className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-white text-xs focus:border-purple-500 focus:outline-none" />
            </div>
          )}
        </div>

        <div className="space-y-3">
          {filteredAvailable.map(([pid, adapter]) => {
            const colors = PLATFORM_COLORS[pid] || DEFAULT_COLOR;
            const isExpanded = expandedPlatform === pid;
            const allFilled = adapter.fields.every((f) => creds[f.key]?.trim());

            return (
              <div key={pid} className={`bg-gray-800/60 border ${isExpanded ? colors.border : "border-gray-700/50"} rounded-xl transition-all`} data-testid={`available-${pid}`}>
                {/* Platform header */}
                <button onClick={() => toggleExpand(pid)} className="w-full flex items-center justify-between p-5 text-left" data-testid={`expand-${pid}`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-lg ${colors.bg} flex items-center justify-center`}>
                      <Zap className={`w-4 h-4 ${colors.accent}`} />
                    </div>
                    <div>
                      <span className="text-white font-medium text-sm">{adapter.platform_name}</span>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-[11px] text-gray-500">{adapter.fields.length} credential{adapter.fields.length > 1 ? "s" : ""} required</span>
                        <span className="text-[11px] text-gray-600">|</span>
                        <span className="text-[11px] text-gray-500">{adapter.cost}</span>
                      </div>
                    </div>
                  </div>
                  {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                </button>

                {/* Expanded credential form */}
                {isExpanded && (
                  <div className="px-5 pb-5 border-t border-gray-700/50 pt-4 space-y-5" data-testid={`form-${pid}`}>
                    {/* Setup instructions */}
                    <div className="bg-gray-900/60 rounded-lg p-3 border border-gray-700/30">
                      <p className="text-xs text-gray-400 mb-2 font-medium">Quick Setup</p>
                      <p className="text-xs text-gray-300 mb-3">{adapter.setup_summary}</p>
                      <a href={adapter.developer_portal} target="_blank" rel="noreferrer"
                        className={`inline-flex items-center gap-1.5 text-xs ${colors.accent} hover:underline`}
                        data-testid={`portal-link-${pid}`}>
                        <Globe className="w-3 h-3" /> {adapter.developer_portal_label}
                        <ArrowRight className="w-3 h-3" />
                      </a>
                    </div>

                    {/* Credential fields */}
                    <div className="space-y-3">
                      {adapter.fields.map((field) => (
                        <CredentialField
                          key={field.key}
                          field={field}
                          value={creds[field.key]}
                          onChange={handleFieldChange}
                        />
                      ))}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-between pt-2">
                      <button onClick={() => { setExpandedPlatform(null); setCreds({}); }}
                        className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg text-xs hover:bg-gray-600 transition-colors"
                        data-testid={`cancel-${pid}`}>
                        Cancel
                      </button>
                      <button onClick={() => handleConnect(pid)} disabled={!allFilled || connecting}
                        className={`px-5 py-2 rounded-lg text-xs font-medium transition-colors flex items-center gap-2 ${allFilled && !connecting ? "bg-purple-600 text-white hover:bg-purple-700" : "bg-gray-700 text-gray-500 cursor-not-allowed"}`}
                        data-testid={`confirm-connect-${pid}`}>
                        {connecting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Link2 className="w-3.5 h-3.5" />}
                        {connecting ? "Connecting..." : "Connect"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {filteredAvailable.length === 0 && searchTerm && (
            <div className="text-center py-8 text-gray-500 text-sm">No platforms match "{searchTerm}"</div>
          )}
          {filteredAvailable.length === 0 && !searchTerm && (
            <div className="text-center py-8 text-gray-500 text-sm flex flex-col items-center gap-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
              <p className="text-white font-medium">All platforms connected!</p>
              <p>All {adapterEntries.length} live adapter platforms are connected.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────
// TEMPLATE ICON HELPER
// ──────────────────────────────────────────────
const TEMPLATE_ICON_MAP = { radio: Radio, music: Music, share: Share2, video: Video, film: Film, mic: Mic, layers: Layers, camera: Camera, monitor: Monitor, hexagon: Hexagon, star: Star, globe: Globe, shield: Shield };
function TemplateIcon({ name, className }) {
  const Icon = TEMPLATE_ICON_MAP[name] || Layers;
  return <Icon className={className} />;
}

// ──────────────────────────────────────────────
// TEMPLATES MANAGEMENT TAB
// ──────────────────────────────────────────────
function TemplatesTab({ templates, loading, platforms, onCreateTemplate, onUpdateTemplate, onDeleteTemplate, onRefresh }) {
  const [showCreate, setShowCreate] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ name: "", description: "", icon: "layers", platform_ids: [] });
  const [expandedCategories, setExpandedCategories] = useState({});

  const system = templates.filter((t) => t.is_system);
  const custom = templates.filter((t) => !t.is_system);

  const allPlatformsList = platforms ? Object.entries(platforms.categories || {}).flatMap(([catId, catData]) =>
    Object.entries(catData.platforms || {}).map(([pid, p]) => ({ ...p, id: pid, category: catId, categoryLabel: catData.label }))
  ) : [];

  const grouped = {};
  allPlatformsList.forEach((p) => {
    if (!grouped[p.category]) grouped[p.category] = { label: p.categoryLabel, platforms: [] };
    grouped[p.category].platforms.push(p);
  });

  const togglePlatformInForm = (pid) => {
    setForm((prev) => ({
      ...prev,
      platform_ids: prev.platform_ids.includes(pid) ? prev.platform_ids.filter((x) => x !== pid) : [...prev.platform_ids, pid],
    }));
  };

  const startEdit = (tpl) => {
    setForm({ name: tpl.name, description: tpl.description || "", icon: tpl.icon || "layers", platform_ids: [...(tpl.platform_ids || [])] });
    setEditingId(tpl.id);
    setShowCreate(true);
  };

  const handleSave = async () => {
    if (!form.name.trim()) return;
    if (editingId) {
      await onUpdateTemplate(editingId, form);
    } else {
      await onCreateTemplate(form);
    }
    setShowCreate(false);
    setEditingId(null);
    setForm({ name: "", description: "", icon: "layers", platform_ids: [] });
  };

  const cancelForm = () => {
    setShowCreate(false);
    setEditingId(null);
    setForm({ name: "", description: "", icon: "layers", platform_ids: [] });
  };

  const iconOptions = ["radio", "music", "share", "video", "film", "mic", "layers"];

  if (loading) return <LoadingState text="Loading templates..." />;

  return (
    <div data-testid="templates-tab">
      <div className="flex justify-between items-center mb-6">
        <div>
          <p className="text-gray-400 text-sm">Pre-configured platform sets for one-click distribution. {system.length} system + {custom.length} custom templates.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={onRefresh} className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 text-gray-400" data-testid="refresh-templates-btn"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={() => { cancelForm(); setShowCreate(true); }} data-testid="create-template-btn"
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium">
            <Plus className="w-4 h-4" /> New Template
          </button>
        </div>
      </div>

      {/* Create / Edit Form */}
      {showCreate && (
        <div className="bg-gray-800/80 border border-gray-700/50 rounded-xl p-6 mb-6" data-testid="template-form">
          <h3 className="text-lg font-semibold text-white mb-4">{editingId ? "Edit Template" : "Create New Template"}</h3>
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Template Name *</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="template-name-input"
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" placeholder="e.g. My Go-To Platforms" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Icon</label>
              <div className="flex gap-2">
                {iconOptions.map((ico) => (
                  <button key={ico} type="button" onClick={() => setForm({ ...form, icon: ico })} data-testid={`icon-${ico}`}
                    className={`p-2 rounded-lg border transition-colors ${form.icon === ico ? "border-purple-500 bg-purple-500/10" : "border-gray-700 hover:border-gray-600"}`}>
                    <TemplateIcon name={ico} className={`w-4 h-4 ${form.icon === ico ? "text-purple-400" : "text-gray-500"}`} />
                  </button>
                ))}
              </div>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} data-testid="template-desc-input"
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-purple-500 focus:outline-none" placeholder="What is this template for?" />
            </div>
          </div>

          <label className="block text-sm text-gray-400 mb-2">Select Platforms ({form.platform_ids.length} selected)</label>
          <div className="space-y-2 max-h-64 overflow-y-auto mb-4 border border-gray-700/50 rounded-lg p-3">
            {Object.entries(grouped).map(([catId, catData]) => (
              <div key={catId}>
                <button onClick={() => setExpandedCategories((p) => ({ ...p, [catId]: !p[catId] }))} className="w-full flex items-center justify-between p-2 bg-gray-900/50 rounded hover:bg-gray-900/80 text-sm" data-testid={`tpl-cat-${catId}`}>
                  <span className="text-gray-300 font-medium">{catData.label}</span>
                  {expandedCategories[catId] ? <ChevronDown className="w-3.5 h-3.5 text-gray-500" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-500" />}
                </button>
                {expandedCategories[catId] && (
                  <div className="grid sm:grid-cols-3 gap-1.5 pl-2 pt-1.5 pb-2">
                    {catData.platforms.map((p) => {
                      const sel = form.platform_ids.includes(p.id);
                      return (
                        <button key={p.id} onClick={() => togglePlatformInForm(p.id)} data-testid={`tpl-plat-${p.id}`}
                          className={`text-left px-2 py-1.5 rounded text-xs border transition-colors ${sel ? "border-purple-500 bg-purple-500/10 text-white" : "border-gray-700/50 text-gray-400 hover:text-white"}`}>
                          {sel && <Check className="w-3 h-3 inline mr-1 text-purple-400" />}{p.name}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button onClick={handleSave} disabled={!form.name.trim() || form.platform_ids.length === 0} data-testid="save-template-btn"
              className="flex items-center gap-2 px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium disabled:opacity-50">
              <Check className="w-4 h-4" /> {editingId ? "Update Template" : "Create Template"}
            </button>
            <button onClick={cancelForm} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm" data-testid="cancel-template-btn">Cancel</button>
          </div>
        </div>
      )}

      {/* System Templates */}
      <h3 className="text-white font-semibold mb-3 flex items-center gap-2"><Zap className="w-4 h-4 text-yellow-400" /> System Templates</h3>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-8">
        {system.map((tpl) => (
          <div key={tpl.id} className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-4 hover:border-purple-500/30 transition-colors" data-testid={`system-tpl-${tpl.id}`}>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-9 h-9 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center">
                <TemplateIcon name={tpl.icon} className="w-4.5 h-4.5 text-yellow-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-white font-medium text-sm">{tpl.name}</h4>
                <p className="text-gray-500 text-xs">{tpl.platform_count} platforms</p>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 bg-yellow-500/10 text-yellow-400 rounded">System</span>
            </div>
            <p className="text-gray-400 text-xs mb-3">{tpl.description}</p>
            <div className="flex flex-wrap gap-1">
              {(tpl.platform_ids || []).slice(0, 5).map((pid) => (
                <span key={pid} className="text-[10px] px-1.5 py-0.5 bg-gray-700/50 text-gray-400 rounded">{ALL_HUB_PLATFORMS_MAP[pid] || pid}</span>
              ))}
              {(tpl.platform_ids || []).length > 5 && <span className="text-[10px] px-1.5 py-0.5 bg-gray-700/50 text-gray-500 rounded">+{tpl.platform_ids.length - 5} more</span>}
            </div>
          </div>
        ))}
      </div>

      {/* Custom Templates */}
      <h3 className="text-white font-semibold mb-3 flex items-center gap-2"><Layers className="w-4 h-4 text-purple-400" /> Your Custom Templates</h3>
      {custom.length === 0 ? (
        <EmptyState icon={Layers} text="No custom templates yet" subtext="Create your own platform combos for one-click distribution" />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {custom.map((tpl) => (
            <div key={tpl.id} className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-4 group" data-testid={`custom-tpl-${tpl.id}`}>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-9 h-9 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                  <TemplateIcon name={tpl.icon} className="w-4.5 h-4.5 text-purple-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-white font-medium text-sm">{tpl.name}</h4>
                  <p className="text-gray-500 text-xs">{tpl.platform_count} platforms</p>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => startEdit(tpl)} className="p-1 text-gray-400 hover:text-white" data-testid={`edit-tpl-${tpl.id}`}><Edit3 className="w-3.5 h-3.5" /></button>
                  <button onClick={() => onDeleteTemplate(tpl.id)} className="p-1 text-gray-400 hover:text-red-400" data-testid={`delete-tpl-${tpl.id}`}><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
              {tpl.description && <p className="text-gray-400 text-xs mb-3">{tpl.description}</p>}
              <div className="flex flex-wrap gap-1">
                {(tpl.platform_ids || []).slice(0, 5).map((pid) => (
                  <span key={pid} className="text-[10px] px-1.5 py-0.5 bg-gray-700/50 text-gray-400 rounded">{ALL_HUB_PLATFORMS_MAP[pid] || pid}</span>
                ))}
                {(tpl.platform_ids || []).length > 5 && <span className="text-[10px] px-1.5 py-0.5 bg-gray-700/50 text-gray-500 rounded">+{tpl.platform_ids.length - 5} more</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────
// UTILITY COMPONENTS
// ──────────────────────────────────────────────
function LoadingState({ text }) {
  return (
    <div className="flex items-center justify-center py-16">
      <Loader2 className="w-6 h-6 text-purple-400 animate-spin mr-3" />
      <span className="text-gray-400">{text}</span>
    </div>
  );
}

function EmptyState({ icon: Icon, text, subtext }) {
  return (
    <div className="text-center py-16">
      <Icon className="w-12 h-12 text-gray-600 mx-auto mb-3" />
      <p className="text-gray-400 font-medium">{text}</p>
      {subtext && <p className="text-gray-500 text-sm mt-1">{subtext}</p>}
    </div>
  );
}

// ──────────────────────────────────────────────
// MAIN PAGE
// ──────────────────────────────────────────────
export default function DistributionHubPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [stats, setStats] = useState(null);
  const [content, setContent] = useState([]);
  const [deliveries, setDeliveries] = useState([]);
  const [platforms, setPlatforms] = useState(null);
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState({ stats: true, content: true, deliveries: true, platforms: true, connections: true, templates: true });
  const [distributing, setDistributing] = useState(false);
  const [activeBatchId, setActiveBatchId] = useState(null);

  // Extract user ID from JWT for WebSocket connection
  const userId = React.useMemo(() => {
    try {
      const token = getToken();
      if (!token) return null;
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.user_id || payload.sub || payload.id || null;
    } catch { return null; }
  }, []);

  const load = useCallback(async (key, path, setter) => {
    setLoading((prev) => ({ ...prev, [key]: true }));
    try {
      const data = await apiFetch(path);
      setter(data);
    } catch (err) {
      console.error(`Error loading ${key}:`, err);
    } finally {
      setLoading((prev) => ({ ...prev, [key]: false }));
    }
  }, []);

  useEffect(() => {
    load("stats", "/stats", setStats);
    load("content", "/content", (d) => setContent(d.content || []));
    load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || []));
    load("platforms", "/platforms", (d) => {
      setPlatforms(d);
      // Populate platform name map for template display
      Object.entries(d?.categories || {}).forEach(([, catData]) => {
        Object.entries(catData.platforms || {}).forEach(([pid, p]) => {
          ALL_HUB_PLATFORMS_MAP[pid] = p.name;
        });
      });
    });
    load("connections", "/platforms/connected", (d) => setConnectedPlatforms(d.connected_platforms || []));
    load("templates", "/templates", (d) => setTemplates(d.templates || []));
  }, [load]);

  const refreshAll = () => {
    load("stats", "/stats", setStats);
    load("content", "/content", (d) => setContent(d.content || []));
    load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || []));
    load("connections", "/platforms/connected", (d) => setConnectedPlatforms(d.connected_platforms || []));
    load("templates", "/templates", (d) => setTemplates(d.templates || []));
  };

  const handleAddContent = async () => {
    load("content", "/content", (d) => setContent(d.content || []));
    load("stats", "/stats", setStats);
  };

  const handleDistribute = async (contentId, platformIds) => {
    setDistributing(true);
    try {
      const result = await apiFetch("/distribute", {
        method: "POST",
        body: JSON.stringify({ content_id: contentId, platform_ids: platformIds }),
      });
      const batchId = result.batch_id;
      setActiveBatchId(batchId);
      alert(`Distribution initiated!\n\nBatch: ${batchId?.slice(0, 8)}...\nAPI Push: ${result.api_push_count} platforms\nExport Packages: ${result.export_package_count} platforms\nTotal: ${result.deliveries?.length || 0} deliveries\n\nDelivery engine is processing in the background.`);
      refreshAll();
      setActiveTab("tracking");
    } catch (err) {
      alert(`Distribution failed: ${err.message}`);
    } finally {
      setDistributing(false);
    }
  };

  const handleMarkDelivered = async (deliveryId) => {
    try {
      await apiFetch(`/deliveries/${deliveryId}/status`, {
        method: "PUT",
        body: JSON.stringify({ status: "delivered", response_data: { marked_manually: true } }),
      });
      load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || []));
      load("stats", "/stats", setStats);
    } catch (err) {
      alert(`Failed: ${err.message}`);
    }
  };

  const handleExport = async (deliveryId) => {
    try {
      const result = await apiFetch(`/deliveries/${deliveryId}/export`, { method: "POST" });
      const pkg = result.package;
      alert(`Export Package Ready!\n\nPlatform: ${pkg.platform}\nContent: ${pkg.content_title}\nSource of Truth: ${pkg.source_of_truth}\n\nInstructions: ${pkg.delivery_instructions}`);
      load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || []));
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    }
  };

  const handleRetryDelivery = async (deliveryId) => {
    try {
      await apiFetch(`/deliveries/${deliveryId}/retry`, { method: "POST" });
      setTimeout(() => load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || [])), 2000);
    } catch (err) {
      alert(`Retry failed: ${err.message}`);
    }
  };

  const handleUpdateMetadata = async (contentId, metadata) => {
    try {
      await apiFetch(`/content/${contentId}/metadata`, {
        method: "PUT",
        body: JSON.stringify(metadata),
      });
      load("content", "/content", (d) => setContent(d.content || []));
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleConnectPlatform = async (platformId, credentials) => {
    try {
      await apiFetch("/platforms/connect", {
        method: "POST",
        body: JSON.stringify({ platform_id: platformId, credentials }),
      });
      load("connections", "/platforms/connected", (d) => setConnectedPlatforms(d.connected_platforms || []));
    } catch (err) {
      alert(`Connection failed: ${err.message}`);
    }
  };

  const handleDisconnectPlatform = async (platformId) => {
    try {
      await apiFetch(`/platforms/${platformId}/disconnect`, { method: "DELETE" });
      load("connections", "/platforms/connected", (d) => setConnectedPlatforms(d.connected_platforms || []));
    } catch (err) {
      alert(`Disconnect failed: ${err.message}`);
    }
  };

  const handleCreateTemplate = async (data) => {
    try {
      await apiFetch("/templates", { method: "POST", body: JSON.stringify(data) });
      load("templates", "/templates", (d) => setTemplates(d.templates || []));
    } catch (err) {
      alert(`Create failed: ${err.message}`);
    }
  };

  const handleUpdateTemplate = async (templateId, data) => {
    try {
      await apiFetch(`/templates/${templateId}`, { method: "PUT", body: JSON.stringify(data) });
      load("templates", "/templates", (d) => setTemplates(d.templates || []));
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm("Delete this template?")) return;
    try {
      await apiFetch(`/templates/${templateId}`, { method: "DELETE" });
      load("templates", "/templates", (d) => setTemplates(d.templates || []));
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950" data-testid="distribution-hub-page">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white flex items-center gap-3" data-testid="hub-title">
                <Globe className="w-7 h-7 text-purple-400" />
                Distribution Hub
              </h1>
              <p className="text-gray-400 mt-1 text-sm">Your central command for content distribution — the source of truth for all deliveries</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500">{platforms?.total_platforms || 0} platforms available</span>
              <button onClick={refreshAll} className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 text-gray-400" data-testid="hub-refresh-btn">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-1 mt-6 overflow-x-auto pb-1 -mb-px">
            {TABS.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button key={tab.id} onClick={() => setActiveTab(tab.id)} data-testid={`tab-${tab.id}`}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-sm font-medium whitespace-nowrap transition-colors border-b-2 ${isActive ? "bg-gray-950 text-white border-purple-500" : "text-gray-400 hover:text-white border-transparent hover:bg-gray-800/50"}`}>
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === "dashboard" && <HubDashboard stats={stats} loading={loading.stats} />}
        {activeTab === "content" && <ContentLibrary content={content} loading={loading.content} onRefresh={() => load("content", "/content", (d) => setContent(d.content || []))} onAddContent={handleAddContent} />}
        {activeTab === "distribute" && <DistributeTab content={content} platforms={platforms} onDistribute={handleDistribute} distributing={distributing} templates={templates} />}
        {activeTab === "templates" && <TemplatesTab templates={templates} loading={loading.templates} platforms={platforms} onCreateTemplate={handleCreateTemplate} onUpdateTemplate={handleUpdateTemplate} onDeleteTemplate={handleDeleteTemplate} onRefresh={() => load("templates", "/templates", (d) => setTemplates(d.templates || []))} />}
        {activeTab === "tracking" && <DeliveryTracking deliveries={deliveries} loading={loading.deliveries} onRefresh={() => load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || []))} onMarkDelivered={handleMarkDelivered} onExport={handleExport} onRetry={handleRetryDelivery} activeBatchId={activeBatchId} userId={userId} />}
        {activeTab === "rights" && <RightsMetadataTab content={content} onUpdateMetadata={handleUpdateMetadata} />}
        {activeTab === "connections" && <PlatformConnectionsTab connectedPlatforms={connectedPlatforms} onConnect={handleConnectPlatform} onDisconnect={handleDisconnectPlatform} />}
      </div>
    </div>
  );
}
