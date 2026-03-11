import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { Send, Upload, Package, Shield, Radio, Film, Music, Image, Video, ChevronDown, ChevronRight, Check, X, RefreshCw, Search, Download, Globe, Zap, BarChart3, FileText, Link2, Clock, CheckCircle2, AlertCircle, Loader2, ArrowRight } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

const TABS = [
  { id: "dashboard", label: "Hub Dashboard", icon: BarChart3 },
  { id: "content", label: "Content Library", icon: FileText },
  { id: "distribute", label: "Distribute", icon: Send },
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
function DistributeTab({ content, platforms, onDistribute, distributing }) {
  const [selectedContent, setSelectedContent] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [search, setSearch] = useState("");

  const toggleCategory = (catId) => setExpandedCategories((prev) => ({ ...prev, [catId]: !prev[catId] }));
  const togglePlatform = (pid) => setSelectedPlatforms((prev) => prev.includes(pid) ? prev.filter((x) => x !== pid) : [...prev, pid]);

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
function DeliveryTracking({ deliveries, loading, onRefresh, onMarkDelivered, onExport }) {
  const [statusFilter, setStatusFilter] = useState("all");
  const filtered = statusFilter === "all" ? deliveries : deliveries.filter((d) => d.status === statusFilter);

  return (
    <div data-testid="delivery-tracking">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex gap-2 flex-wrap">
          {["all", "queued", "delivering", "delivered", "export_ready", "failed"].map((s) => (
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
                  <p className="text-xs text-gray-500 mt-1">{d.platform_category} | Batch: {d.batch_id?.slice(0, 8)}...</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${STATUS_STYLES[d.status] || STATUS_STYLES.draft}`}>
                    {d.status?.replace("_", " ")}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${d.delivery_method === "api_push" ? "bg-green-500/10 text-green-400" : "bg-cyan-500/10 text-cyan-400"}`}>
                    {d.delivery_method === "api_push" ? "Auto" : "Export"}
                  </span>
                  {d.status === "export_ready" && (
                    <button onClick={() => onExport(d.id)} className="px-2 py-1 bg-cyan-600/20 text-cyan-400 rounded text-xs hover:bg-cyan-600/30" data-testid={`export-${d.id}`}>
                      <Download className="w-3 h-3 inline mr-1" />Export
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
function PlatformConnectionsTab({ connectedPlatforms, platforms, onConnect, onDisconnect }) {
  const [showConnect, setShowConnect] = useState(null);
  const [creds, setCreds] = useState({});

  const connectedIds = new Set(connectedPlatforms.map((c) => c.platform_id));

  const handleConnect = async (platformId) => {
    await onConnect(platformId, creds);
    setCreds({});
    setShowConnect(null);
  };

  const allPlatformsList = platforms ? Object.entries(platforms.categories || {}).flatMap(([catId, catData]) =>
    Object.entries(catData.platforms || {}).filter(([pid, p]) => p.method === "api_push").map(([pid, p]) => ({ ...p, id: pid, categoryLabel: catData.label }))
  ) : [];

  return (
    <div data-testid="platform-connections-tab">
      <p className="text-gray-400 text-sm mb-6">Connect your accounts for auto-push delivery. Platforms without connections will use export packages.</p>

      {connectedPlatforms.length > 0 && (
        <div className="mb-8">
          <h3 className="text-white font-semibold mb-3">Connected Platforms ({connectedPlatforms.length})</h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {connectedPlatforms.map((c) => (
              <div key={c.platform_id} className="bg-gray-800/60 border border-emerald-500/20 rounded-xl p-4" data-testid={`connected-${c.platform_id}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span className="text-white font-medium text-sm">{c.platform_name}</span>
                  </div>
                  <button onClick={() => onDisconnect(c.platform_id)} className="text-red-400 hover:text-red-300 text-xs" data-testid={`disconnect-${c.platform_id}`}>Disconnect</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <h3 className="text-white font-semibold mb-3">Available for Connection</h3>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {allPlatformsList.filter((p) => !connectedIds.has(p.id)).map((p) => (
          <div key={p.id} className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-4" data-testid={`available-${p.id}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-300 font-medium text-sm">{p.name}</span>
              <span className="text-[10px] text-gray-500">{p.categoryLabel}</span>
            </div>
            {showConnect === p.id ? (
              <div className="mt-2 space-y-2">
                <input value={creds.api_key || ""} onChange={(e) => setCreds({ ...creds, api_key: e.target.value })} placeholder="API Key / Token"
                  data-testid={`cred-input-${p.id}`}
                  className="w-full bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:border-purple-500 focus:outline-none" />
                <div className="flex gap-2">
                  <button onClick={() => handleConnect(p.id)} className="px-3 py-1 bg-purple-600 text-white rounded text-xs hover:bg-purple-700" data-testid={`confirm-connect-${p.id}`}>Connect</button>
                  <button onClick={() => setShowConnect(null)} className="px-3 py-1 bg-gray-700 text-gray-300 rounded text-xs hover:bg-gray-600">Cancel</button>
                </div>
              </div>
            ) : (
              <button onClick={() => setShowConnect(p.id)} className="mt-1 text-xs text-purple-400 hover:text-purple-300" data-testid={`start-connect-${p.id}`}>Connect Account</button>
            )}
          </div>
        ))}
      </div>
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
  const [loading, setLoading] = useState({ stats: true, content: true, deliveries: true, platforms: true, connections: true });
  const [distributing, setDistributing] = useState(false);

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
    load("platforms", "/platforms", setPlatforms);
    load("connections", "/platforms/connected", (d) => setConnectedPlatforms(d.connected_platforms || []));
  }, [load]);

  const refreshAll = () => {
    load("stats", "/stats", setStats);
    load("content", "/content", (d) => setContent(d.content || []));
    load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || []));
    load("connections", "/platforms/connected", (d) => setConnectedPlatforms(d.connected_platforms || []));
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
      alert(`Distribution initiated!\n\nBatch: ${result.batch_id?.slice(0, 8)}...\nAPI Push: ${result.api_push_count} platforms\nExport Packages: ${result.export_package_count} platforms\nTotal: ${result.deliveries?.length || 0} deliveries`);
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
        {activeTab === "distribute" && <DistributeTab content={content} platforms={platforms} onDistribute={handleDistribute} distributing={distributing} />}
        {activeTab === "tracking" && <DeliveryTracking deliveries={deliveries} loading={loading.deliveries} onRefresh={() => load("deliveries", "/deliveries", (d) => setDeliveries(d.deliveries || []))} onMarkDelivered={handleMarkDelivered} onExport={handleExport} />}
        {activeTab === "rights" && <RightsMetadataTab content={content} onUpdateMetadata={handleUpdateMetadata} />}
        {activeTab === "connections" && <PlatformConnectionsTab connectedPlatforms={connectedPlatforms} platforms={platforms} onConnect={handleConnectPlatform} onDisconnect={handleDisconnectPlatform} />}
      </div>
    </div>
  );
}
