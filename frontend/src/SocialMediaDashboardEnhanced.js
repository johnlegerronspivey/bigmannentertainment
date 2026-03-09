import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Search, Globe, Music, Radio, Tv, Film, Shield, Link, Headphones, Image, Volume2, Camera, Users, FileText, Database, Video, Mic, ChevronDown, ChevronUp, Check, X, Plus, Settings, BarChart3, Send, RefreshCw, Trash2, Eye, EyeOff, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_META = {
  social_media: { label: 'Social Media', Icon: Globe, color: 'from-blue-500 to-indigo-600' },
  music_streaming: { label: 'Music Streaming', Icon: Music, color: 'from-emerald-500 to-teal-600' },
  podcast: { label: 'Podcasts', Icon: Mic, color: 'from-orange-500 to-amber-600' },
  radio: { label: 'Radio & Broadcasting', Icon: Radio, color: 'from-rose-500 to-pink-600' },
  video_streaming: { label: 'TV & Video Streaming', Icon: Tv, color: 'from-purple-500 to-violet-600' },
  live_streaming: { label: 'Live Streaming', Icon: Video, color: 'from-red-500 to-rose-600' },
  video_platform: { label: 'Video Platforms', Icon: Film, color: 'from-sky-500 to-cyan-600' },
  rights_organization: { label: 'Rights Organizations', Icon: Shield, color: 'from-yellow-500 to-amber-600' },
  blockchain: { label: 'Blockchain', Icon: Link, color: 'from-slate-500 to-zinc-600' },
  web3_music: { label: 'Web3 Music', Icon: Headphones, color: 'from-fuchsia-500 to-pink-600' },
  nft_marketplace: { label: 'NFT Marketplace', Icon: Image, color: 'from-violet-500 to-purple-600' },
  audio_social: { label: 'Audio Social', Icon: Volume2, color: 'from-teal-500 to-emerald-600' },
  model_agency: { label: 'Model Agencies', Icon: Camera, color: 'from-pink-500 to-rose-600' },
  model_platform: { label: 'Model Platforms', Icon: Users, color: 'from-indigo-500 to-blue-600' },
  music_licensing: { label: 'Music Licensing', Icon: FileText, color: 'from-amber-500 to-yellow-600' },
  music_data_exchange: { label: 'Music Data Exchange', Icon: Database, color: 'from-cyan-500 to-sky-600' },
};

const getToken = () => localStorage.getItem('token');
const authHeaders = () => ({ headers: { Authorization: `Bearer ${getToken()}` } });

/* ─── Credential Modal ────────────────────────────────────────────── */
const CredentialModal = ({ platform, onClose, onSaved }) => {
  const fields = platform?.credentials_required || [];
  const [values, setValues] = useState(() => Object.fromEntries(fields.map(f => [f, ''])));
  const [displayName, setDisplayName] = useState('');
  const [showValues, setShowValues] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    const empty = fields.filter(f => !values[f]);
    if (empty.length > 0) { setError(`Missing: ${empty.join(', ')}`); return; }
    setSaving(true);
    setError('');
    try {
      await axios.post(
        `${BACKEND_URL}/api/social/credentials/${platform.platform_id}`,
        { credentials: values, display_name: displayName },
        authHeaders(),
      );
      onSaved();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save');
    } finally { setSaving(false); }
  };

  if (!platform) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-[#1a1d2e] rounded-2xl border border-white/10 w-full max-w-lg mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h3 className="text-lg font-semibold text-white" data-testid="credential-modal-title">{platform.name}</h3>
            <p className="text-sm text-gray-400 mt-0.5">Enter your API credentials</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg transition" data-testid="credential-modal-close"><X size={18} className="text-gray-400" /></button>
        </div>
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Display Name (optional)</label>
            <input value={displayName} onChange={e => setDisplayName(e.target.value)} placeholder="@yourhandle" className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" data-testid="credential-display-name" />
          </div>
          {fields.map(field => (
            <div key={field}>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">{field.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</label>
              <div className="relative">
                <input
                  type={showValues[field] ? 'text' : 'password'}
                  value={values[field]}
                  onChange={e => setValues(v => ({ ...v, [field]: e.target.value }))}
                  placeholder={`Enter ${field.replace(/_/g, ' ')}`}
                  className="w-full px-3 py-2.5 pr-10 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  data-testid={`credential-field-${field}`}
                />
                <button onClick={() => setShowValues(s => ({ ...s, [field]: !s[field] }))} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">
                  {showValues[field] ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>
          ))}
          {error && <p className="text-red-400 text-sm">{error}</p>}
        </div>
        <div className="flex gap-3 p-6 border-t border-white/10">
          <button onClick={onClose} className="flex-1 px-4 py-2.5 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition text-sm" data-testid="credential-cancel-btn">Cancel</button>
          <button onClick={handleSave} disabled={saving} className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2" data-testid="credential-save-btn">
            {saving ? <><Loader2 size={14} className="animate-spin" /> Saving...</> : <><Check size={14} /> Connect</>}
          </button>
        </div>
      </div>
    </div>
  );
};

/* ─── Platform Card ───────────────────────────────────────────────── */
const PlatformCard = ({ conn, onConnect, onDisconnect }) => {
  const meta = CATEGORY_META[conn.type] || CATEGORY_META.social_media;
  const Icon = meta.Icon;
  return (
    <div className={`group relative bg-[#1a1d2e] rounded-xl border transition-all duration-200 hover:shadow-lg hover:shadow-blue-500/5 ${conn.connected ? 'border-emerald-500/30' : 'border-white/5 hover:border-white/15'}`} data-testid={`platform-card-${conn.platform_id}`}>
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${meta.color} flex items-center justify-center`}>
              <Icon size={16} className="text-white" />
            </div>
            <div className="min-w-0">
              <h4 className="text-sm font-semibold text-white truncate">{conn.name}</h4>
              {conn.display_name && <p className="text-xs text-gray-400 truncate">{conn.display_name}</p>}
            </div>
          </div>
          {conn.connected ? (
            <span className="shrink-0 flex items-center gap-1 px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-[10px] font-medium" data-testid={`status-connected-${conn.platform_id}`}>
              <Check size={10} /> Live
            </span>
          ) : (
            <span className="shrink-0 px-2 py-1 bg-white/5 text-gray-500 rounded-full text-[10px] font-medium" data-testid={`status-disconnected-${conn.platform_id}`}>
              Offline
            </span>
          )}
        </div>
        <p className="text-xs text-gray-500 mb-3 line-clamp-2 leading-relaxed">{conn.description}</p>
        <div className="flex gap-1.5 flex-wrap mb-3">
          {conn.supported_formats?.map(f => (
            <span key={f} className="px-1.5 py-0.5 bg-white/5 text-gray-400 rounded text-[10px]">{f}</span>
          ))}
        </div>
        {conn.connected ? (
          <button onClick={() => onDisconnect(conn.platform_id)} className="w-full px-3 py-2 border border-red-500/20 text-red-400 rounded-lg hover:bg-red-500/10 transition text-xs font-medium flex items-center justify-center gap-1.5" data-testid={`disconnect-btn-${conn.platform_id}`}>
            <Trash2 size={12} /> Disconnect
          </button>
        ) : (
          <button onClick={() => onConnect(conn)} className="w-full px-3 py-2 bg-blue-600/90 hover:bg-blue-600 text-white rounded-lg transition text-xs font-medium flex items-center justify-center gap-1.5" data-testid={`connect-btn-${conn.platform_id}`}>
            <Plus size={12} /> Connect
          </button>
        )}
      </div>
    </div>
  );
};

/* ─── Category Section ────────────────────────────────────────────── */
const CategorySection = ({ type, platforms, onConnect, onDisconnect, defaultOpen }) => {
  const [open, setOpen] = useState(defaultOpen);
  const meta = CATEGORY_META[type] || { label: type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()), Icon: Globe, color: 'from-gray-500 to-gray-600' };
  const connectedCount = platforms.filter(p => p.connected).length;
  const Icon = meta.Icon;

  return (
    <div className="mb-4" data-testid={`category-${type}`}>
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between p-3 bg-[#151827] rounded-xl hover:bg-[#1a1d30] transition group">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${meta.color} flex items-center justify-center`}>
            <Icon size={14} className="text-white" />
          </div>
          <span className="text-sm font-semibold text-white">{meta.label}</span>
          <span className="text-xs text-gray-500">({platforms.length})</span>
          {connectedCount > 0 && <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-[10px] font-medium rounded-full">{connectedCount} live</span>}
        </div>
        {open ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
      </button>
      {open && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 mt-3 pl-2">
          {platforms.map(p => <PlatformCard key={p.platform_id} conn={p} onConnect={onConnect} onDisconnect={onDisconnect} />)}
        </div>
      )}
    </div>
  );
};

/* ─── Main Dashboard ──────────────────────────────────────────────── */
const SocialMediaDashboardEnhanced = () => {
  const [connections, setConnections] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('connections');
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [modalPlatform, setModalPlatform] = useState(null);
  const [newPost, setNewPost] = useState({ provider: '', content: '', mediaUrls: [] });
  const [posting, setPosting] = useState(false);
  const [connectingAll, setConnectingAll] = useState(false);

  const fetchConnections = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/api/social/connections`, authHeaders());
      setConnections(res.data.connections || []);
    } catch { setConnections([]); }
  }, []);

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/api/social/metrics/dashboard`, authHeaders());
      setDashboardData(res.data);
    } catch { setDashboardData({ platforms: [], total_followers: 0, total_posts: 0, avg_engagement: 0, connected_count: 0, total_platforms: 0 }); }
  }, []);

  const fetchPosts = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/api/social/posts`, authHeaders());
      setPosts(res.data.posts || []);
    } catch { setPosts([]); }
  }, []);

  useEffect(() => {
    Promise.all([fetchConnections(), fetchDashboard(), fetchPosts()]).finally(() => setLoading(false));
  }, [fetchConnections, fetchDashboard, fetchPosts]);

  const handleDisconnect = async (platformId) => {
    if (!window.confirm('Disconnect this platform?')) return;
    try {
      await axios.post(`${BACKEND_URL}/api/social/disconnect/${platformId}`, {}, authHeaders());
      fetchConnections();
      fetchDashboard();
    } catch (err) { alert(err.response?.data?.detail || 'Failed to disconnect'); }
  };

  const handleConnectAll = async () => {
    if (!window.confirm('Connect all 120 platforms? You can add specific credentials later.')) return;
    setConnectingAll(true);
    try {
      const allIds = connections.filter(c => !c.connected).map(c => c.platform_id);
      await axios.post(`${BACKEND_URL}/api/social/bulk-connect`, { platform_ids: allIds }, authHeaders());
      await fetchConnections();
      await fetchDashboard();
    } catch (err) { alert(err.response?.data?.detail || 'Failed'); }
    finally { setConnectingAll(false); }
  };

  const handlePost = async (e) => {
    e.preventDefault();
    setPosting(true);
    try {
      await axios.post(`${BACKEND_URL}/api/social/post`, { provider: newPost.provider, content: newPost.content, media_urls: newPost.mediaUrls }, authHeaders());
      setNewPost({ provider: '', content: '', mediaUrls: [] });
      fetchPosts();
      setActiveTab('posts');
    } catch (err) { alert(err.response?.data?.detail || 'Failed to post'); }
    finally { setPosting(false); }
  };

  /* ── Filters ── */
  const filtered = connections.filter(c => {
    if (search && !c.name.toLowerCase().includes(search.toLowerCase()) && !c.platform_id.includes(search.toLowerCase())) return false;
    if (filterType !== 'all' && c.type !== filterType) return false;
    if (filterStatus === 'connected' && !c.connected) return false;
    if (filterStatus === 'disconnected' && c.connected) return false;
    return true;
  });

  const grouped = {};
  filtered.forEach(c => { (grouped[c.type] = grouped[c.type] || []).push(c); });

  const connectedPlatforms = connections.filter(c => c.connected);
  const totalConnected = connectedPlatforms.length;
  const totalPlatforms = connections.length;
  const categories = [...new Set(connections.map(c => c.type))];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f1119] flex items-center justify-center">
        <Loader2 className="animate-spin text-blue-500" size={40} />
      </div>
    );
  }

  const tabs = [
    { id: 'connections', label: 'Platforms', Icon: Settings, count: totalPlatforms },
    { id: 'overview', label: 'Overview', Icon: BarChart3, count: totalConnected },
    { id: 'post', label: 'Create Post', Icon: Send },
    { id: 'posts', label: 'Posts', Icon: FileText, count: posts.length },
  ];

  return (
    <div className="min-h-screen bg-[#0f1119]" data-testid="social-media-dashboard">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 py-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight" data-testid="dashboard-title">Platform Connections</h1>
            <p className="text-sm text-gray-400 mt-1">{totalConnected} of {totalPlatforms} platforms connected</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => { fetchConnections(); fetchDashboard(); }} className="px-3 py-2 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition text-sm flex items-center gap-1.5" data-testid="refresh-btn">
              <RefreshCw size={14} /> Refresh
            </button>
            <button onClick={handleConnectAll} disabled={connectingAll} className="px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition text-sm font-medium flex items-center gap-1.5 disabled:opacity-50" data-testid="connect-all-btn">
              {connectingAll ? <><Loader2 size={14} className="animate-spin" /> Connecting...</> : <><Plus size={14} /> Connect All</>}
            </button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
            <p className="text-xs text-gray-500 mb-1">Total Platforms</p>
            <p className="text-2xl font-bold text-white" data-testid="stat-total">{totalPlatforms}</p>
          </div>
          <div className="bg-[#1a1d2e] rounded-xl p-4 border border-emerald-500/20">
            <p className="text-xs text-emerald-400 mb-1">Connected</p>
            <p className="text-2xl font-bold text-emerald-400" data-testid="stat-connected">{totalConnected}</p>
          </div>
          <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
            <p className="text-xs text-gray-500 mb-1">Categories</p>
            <p className="text-2xl font-bold text-white" data-testid="stat-categories">{categories.length}</p>
          </div>
          <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
            <p className="text-xs text-gray-500 mb-1">Posts</p>
            <p className="text-2xl font-bold text-white" data-testid="stat-posts">{posts.length}</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-1 bg-[#151827] rounded-xl mb-6 overflow-x-auto" data-testid="tab-bar">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} className={`flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition ${activeTab === t.id ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-400 hover:text-white hover:bg-white/5'}`} data-testid={`tab-${t.id}`}>
              <t.Icon size={14} /> {t.label}
              {t.count !== undefined && <span className={`ml-1 text-[10px] px-1.5 py-0.5 rounded-full ${activeTab === t.id ? 'bg-white/20' : 'bg-white/5'}`}>{t.count}</span>}
            </button>
          ))}
        </div>

        {/* ── Connections Tab ── */}
        {activeTab === 'connections' && (
          <div>
            <div className="flex flex-col sm:flex-row gap-3 mb-5">
              <div className="relative flex-1">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search platforms..." className="w-full pl-9 pr-3 py-2.5 bg-[#1a1d2e] border border-white/10 rounded-lg text-sm text-white placeholder:text-gray-500 focus:ring-2 focus:ring-blue-500 outline-none" data-testid="search-platforms" />
              </div>
              <select value={filterType} onChange={e => setFilterType(e.target.value)} className="px-3 py-2.5 bg-[#1a1d2e] border border-white/10 rounded-lg text-sm text-white outline-none" data-testid="filter-type">
                <option value="all">All Categories</option>
                {categories.map(c => <option key={c} value={c}>{(CATEGORY_META[c]?.label) || c}</option>)}
              </select>
              <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="px-3 py-2.5 bg-[#1a1d2e] border border-white/10 rounded-lg text-sm text-white outline-none" data-testid="filter-status">
                <option value="all">All Status</option>
                <option value="connected">Connected</option>
                <option value="disconnected">Disconnected</option>
              </select>
            </div>
            {Object.keys(grouped).length === 0 ? (
              <div className="text-center py-20 text-gray-500"><p>No platforms match your filters.</p></div>
            ) : (
              Object.entries(grouped).map(([type, platforms]) => (
                <CategorySection key={type} type={type} platforms={platforms} onConnect={p => setModalPlatform(p)} onDisconnect={handleDisconnect} defaultOpen={type === 'social_media'} />
              ))
            )}
          </div>
        )}

        {/* ── Overview Tab ── */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {totalConnected === 0 ? (
              <div className="bg-[#1a1d2e] rounded-xl p-12 text-center border border-white/5">
                <Globe size={48} className="mx-auto text-gray-600 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">No Platforms Connected</h3>
                <p className="text-sm text-gray-400 mb-4">Connect your platforms to see analytics</p>
                <button onClick={() => setActiveTab('connections')} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">Connect Platforms</button>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-blue-600/20 to-indigo-600/20 rounded-xl p-6 border border-blue-500/20">
                    <p className="text-xs text-blue-300 mb-1">Connected Platforms</p>
                    <p className="text-3xl font-bold text-white">{totalConnected}</p>
                  </div>
                  <div className="bg-gradient-to-br from-emerald-600/20 to-teal-600/20 rounded-xl p-6 border border-emerald-500/20">
                    <p className="text-xs text-emerald-300 mb-1">Platform Categories</p>
                    <p className="text-3xl font-bold text-white">{new Set(connectedPlatforms.map(p => p.type)).size}</p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-600/20 to-violet-600/20 rounded-xl p-6 border border-purple-500/20">
                    <p className="text-xs text-purple-300 mb-1">Total Posts</p>
                    <p className="text-3xl font-bold text-white">{posts.length}</p>
                  </div>
                </div>
                <div className="bg-[#1a1d2e] rounded-xl border border-white/5 overflow-hidden">
                  <div className="p-4 border-b border-white/5">
                    <h3 className="text-sm font-semibold text-white">Connected Platforms</h3>
                  </div>
                  <div className="divide-y divide-white/5 max-h-[400px] overflow-y-auto">
                    {connectedPlatforms.map(c => {
                      const meta = CATEGORY_META[c.type] || CATEGORY_META.social_media;
                      const Icon = meta.Icon;
                      return (
                        <div key={c.platform_id} className="flex items-center justify-between px-4 py-3 hover:bg-white/[.02]">
                          <div className="flex items-center gap-3">
                            <div className={`w-7 h-7 rounded-md bg-gradient-to-br ${meta.color} flex items-center justify-center`}><Icon size={12} className="text-white" /></div>
                            <div>
                              <p className="text-sm text-white font-medium">{c.name}</p>
                              <p className="text-xs text-gray-500">{c.type.replace(/_/g, ' ')}</p>
                            </div>
                          </div>
                          <span className="flex items-center gap-1 text-emerald-400 text-xs"><Check size={12} /> Connected</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ── Create Post Tab ── */}
        {activeTab === 'post' && (
          <div className="max-w-2xl mx-auto">
            {connectedPlatforms.length === 0 ? (
              <div className="bg-[#1a1d2e] rounded-xl p-12 text-center border border-white/5">
                <Send size={48} className="mx-auto text-gray-600 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">No Connected Platforms</h3>
                <p className="text-sm text-gray-400 mb-4">Connect a platform first to post content</p>
                <button onClick={() => setActiveTab('connections')} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">Connect Platforms</button>
              </div>
            ) : (
              <form onSubmit={handlePost} className="bg-[#1a1d2e] rounded-xl border border-white/5 p-6 space-y-5">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5">Platform</label>
                  <select value={newPost.provider} onChange={e => setNewPost(p => ({ ...p, provider: e.target.value }))} required className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white outline-none" data-testid="post-platform-select">
                    <option value="">Select platform...</option>
                    {connectedPlatforms.map(c => <option key={c.platform_id} value={c.platform_id}>{c.name}{c.display_name ? ` (${c.display_name})` : ''}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5">Content</label>
                  <textarea value={newPost.content} onChange={e => setNewPost(p => ({ ...p, content: e.target.value }))} rows={5} required maxLength={500} placeholder="What's on your mind?" className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white outline-none resize-none" data-testid="post-content-input" />
                  <p className="text-right text-xs text-gray-500 mt-1">{newPost.content.length}/500</p>
                </div>
                <button type="submit" disabled={posting || !newPost.provider || !newPost.content} className="w-full px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition disabled:opacity-40 flex items-center justify-center gap-2" data-testid="post-submit-btn">
                  {posting ? <><Loader2 size={14} className="animate-spin" /> Posting...</> : <><Send size={14} /> Post</>}
                </button>
              </form>
            )}
          </div>
        )}

        {/* ── Posts Tab ── */}
        {activeTab === 'posts' && (
          <div className="space-y-3">
            {posts.length === 0 ? (
              <div className="bg-[#1a1d2e] rounded-xl p-12 text-center border border-white/5">
                <FileText size={48} className="mx-auto text-gray-600 mb-4" />
                <p className="text-gray-400 text-sm">No posts yet</p>
              </div>
            ) : posts.map(post => (
              <div key={post.id} className="bg-[#1a1d2e] rounded-xl border border-white/5 p-4" data-testid={`post-${post.id}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {post.platforms?.map(p => <span key={p} className="text-xs bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded">{p}</span>)}
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded ${post.status === 'posted' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-yellow-500/10 text-yellow-400'}`}>{post.status}</span>
                </div>
                <p className="text-sm text-white mb-2">{post.content}</p>
                <p className="text-xs text-gray-500">{post.posted_at ? new Date(post.posted_at).toLocaleString() : ''}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Credential Modal */}
      {modalPlatform && (
        <CredentialModal platform={modalPlatform} onClose={() => setModalPlatform(null)} onSaved={() => { setModalPlatform(null); fetchConnections(); fetchDashboard(); }} />
      )}
    </div>
  );
};

export default SocialMediaDashboardEnhanced;
