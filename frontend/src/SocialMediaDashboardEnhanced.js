import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Search, Globe, Music, Radio, Tv, Film, Shield, Link, Headphones, Image, Volume2, Camera, Users, FileText, Database, Video, Mic, ChevronDown, ChevronUp, Check, X, Plus, Settings, BarChart3, Send, RefreshCw, Trash2, Eye, EyeOff, Loader2, TrendingUp, TrendingDown, Activity, Heart, MessageCircle, Share2, Zap, ArrowUpRight, ArrowDownRight, Wifi, WifiOff, Signal } from 'lucide-react';

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
  const [mode, setMode] = useState(platform?.has_url_connect ? 'url' : 'api');
  const [profileUrl, setProfileUrl] = useState('');
  const [values, setValues] = useState(() => Object.fromEntries(fields.map(f => [f, ''])));
  const [displayName, setDisplayName] = useState('');
  const [showValues, setShowValues] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [urlResult, setUrlResult] = useState(null);
  const [showManualMetrics, setShowManualMetrics] = useState(false);
  const [manualMetrics, setManualMetrics] = useState({ followers: '', following: '', posts: '', engagement_rate: '' });

  const handleSaveUrl = async () => {
    if (!profileUrl.trim()) { setError('Please enter your profile URL'); return; }
    setSaving(true);
    setError('');
    try {
      const manual = showManualMetrics && manualMetrics.followers
        ? { followers: parseInt(manualMetrics.followers) || 0, following: parseInt(manualMetrics.following) || 0, posts: parseInt(manualMetrics.posts) || 0, engagement_rate: parseFloat(manualMetrics.engagement_rate) || 0 }
        : undefined;
      const res = await axios.post(
        `${BACKEND_URL}/api/social/connect-url`,
        { profile_url: profileUrl, display_name: displayName || undefined, platform_id: platform.platform_id, manual_metrics: manual },
        authHeaders(),
      );
      setUrlResult(res.data);
      // If auto-scrape returned no metrics and user hasn't entered manual yet, prompt them
      if (!res.data.metrics_available && !showManualMetrics) {
        setShowManualMetrics(true);
      }
      onSaved();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect with URL');
    } finally { setSaving(false); }
  };

  const handleSaveApi = async () => {
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
            <p className="text-sm text-gray-400 mt-0.5">Connect your account</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg transition" data-testid="credential-modal-close"><X size={18} className="text-gray-400" /></button>
        </div>

        {/* Mode Toggle */}
        {platform.has_url_connect && fields.length > 0 && (
          <div className="flex border-b border-white/10">
            <button onClick={() => { setMode('url'); setError(''); }} className={`flex-1 py-2.5 text-xs font-medium transition ${mode === 'url' ? 'text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/5' : 'text-gray-500 hover:text-gray-300'}`} data-testid="connect-mode-url">
              <Link size={12} className="inline mr-1.5" />Profile URL
            </button>
            <button onClick={() => { setMode('api'); setError(''); }} className={`flex-1 py-2.5 text-xs font-medium transition ${mode === 'api' ? 'text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/5' : 'text-gray-500 hover:text-gray-300'}`} data-testid="connect-mode-api">
              <Settings size={12} className="inline mr-1.5" />API Keys
            </button>
          </div>
        )}

        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          {/* URL Success Result */}
          {urlResult && (
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg" data-testid="url-connect-success">
              <p className="text-sm text-emerald-400 font-medium flex items-center gap-1.5"><Check size={14} /> Connected via URL</p>
              {urlResult.initial_metrics && (
                <div className="mt-2 space-y-1.5">
                  {(urlResult.initial_metrics.full_name || urlResult.initial_metrics.page_name) && (
                    <p className="text-xs text-white font-medium flex items-center gap-1.5">
                      {urlResult.initial_metrics.full_name || urlResult.initial_metrics.page_name}
                      {urlResult.initial_metrics.is_verified && <Check size={10} className="text-blue-400" />}
                      {urlResult.initial_metrics.category && <span className="text-gray-500 font-normal ml-1">· {urlResult.initial_metrics.category}</span>}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-3 text-xs text-gray-300">
                    <span data-testid="url-metric-followers">{formatNum(urlResult.initial_metrics.followers)} followers</span>
                    {urlResult.initial_metrics.following > 0 && <span data-testid="url-metric-following">{formatNum(urlResult.initial_metrics.following)} following</span>}
                    <span data-testid="url-metric-posts">{formatNum(urlResult.initial_metrics.posts)} posts</span>
                    <span data-testid="url-metric-engagement">{urlResult.initial_metrics.engagement_rate}% engagement</span>
                    {urlResult.initial_metrics.page_likes > 0 && <span data-testid="url-metric-page-likes">{formatNum(urlResult.initial_metrics.page_likes)} page likes</span>}
                  </div>
                  {urlResult.initial_metrics.bio && (
                    <p className="text-[11px] text-gray-400 mt-1 line-clamp-2" data-testid="url-metric-bio">{urlResult.initial_metrics.bio}</p>
                  )}
                  {(urlResult.initial_metrics.impressions > 0 || urlResult.initial_metrics.reach > 0) && (
                    <div className="flex gap-3 text-[10px] text-gray-500 mt-1">
                      {urlResult.initial_metrics.impressions > 0 && <span>~{formatNum(urlResult.initial_metrics.impressions)} est. impressions</span>}
                      {urlResult.initial_metrics.reach > 0 && <span>~{formatNum(urlResult.initial_metrics.reach)} est. reach</span>}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* URL Mode */}
          {mode === 'url' && !urlResult && (
            <>
              <div className="p-3 bg-cyan-500/5 border border-cyan-500/10 rounded-lg">
                <p className="text-xs text-cyan-300 mb-1 font-medium flex items-center gap-1"><Signal size={10} /> Quick Connect</p>
                <p className="text-[11px] text-gray-400 leading-relaxed">Paste your profile URL and we'll fetch your public metrics automatically. No API keys needed.</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1.5">Profile URL</label>
                <input
                  value={profileUrl}
                  onChange={e => setProfileUrl(e.target.value)}
                  placeholder={platform.url_example || `https://platform.com/yourprofile`}
                  className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent outline-none"
                  data-testid="credential-profile-url"
                />
                <p className="text-[10px] text-gray-500 mt-1">Example: {platform.url_example || 'https://platform.com/yourprofile'}</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-400 mb-1.5">Display Name (optional)</label>
                <input value={displayName} onChange={e => setDisplayName(e.target.value)} placeholder="@yourhandle" className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:ring-2 focus:ring-cyan-500 focus:border-transparent outline-none" data-testid="credential-display-name-url" />
              </div>
              {/* Manual Metrics Toggle */}
              <button
                type="button"
                onClick={() => setShowManualMetrics(!showManualMetrics)}
                className="flex items-center gap-1.5 text-[11px] text-gray-400 hover:text-cyan-400 transition"
                data-testid="toggle-manual-metrics"
              >
                {showManualMetrics ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                {showManualMetrics ? 'Hide manual metrics' : 'Add metrics manually (if auto-fetch fails)'}
              </button>
              {showManualMetrics && (
                <div className="space-y-2.5 p-3 bg-amber-500/5 border border-amber-500/10 rounded-lg" data-testid="manual-metrics-form">
                  <p className="text-[10px] text-amber-300/80 leading-relaxed">Some platforms block automated data fetching. Enter your public stats here as a fallback.</p>
                  <div className="grid grid-cols-2 gap-2.5">
                    <div>
                      <label className="block text-[10px] font-medium text-gray-400 mb-1">Followers</label>
                      <input type="number" min="0" value={manualMetrics.followers} onChange={e => setManualMetrics(m => ({ ...m, followers: e.target.value }))} placeholder="e.g. 10000" className="w-full px-2.5 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-xs focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none" data-testid="manual-followers" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-medium text-gray-400 mb-1">Following</label>
                      <input type="number" min="0" value={manualMetrics.following} onChange={e => setManualMetrics(m => ({ ...m, following: e.target.value }))} placeholder="e.g. 500" className="w-full px-2.5 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-xs focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none" data-testid="manual-following" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-medium text-gray-400 mb-1">Posts</label>
                      <input type="number" min="0" value={manualMetrics.posts} onChange={e => setManualMetrics(m => ({ ...m, posts: e.target.value }))} placeholder="e.g. 250" className="w-full px-2.5 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-xs focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none" data-testid="manual-posts" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-medium text-gray-400 mb-1">Engagement %</label>
                      <input type="number" min="0" max="100" step="0.1" value={manualMetrics.engagement_rate} onChange={e => setManualMetrics(m => ({ ...m, engagement_rate: e.target.value }))} placeholder="e.g. 3.5" className="w-full px-2.5 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-xs focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none" data-testid="manual-engagement" />
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* URL connected but no metrics — prompt manual entry */}
          {urlResult && !urlResult.metrics_available && !showManualMetrics && (
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg" data-testid="url-no-metrics-prompt">
              <p className="text-xs text-amber-400 font-medium">Connected, but auto-fetch couldn't retrieve metrics</p>
              <p className="text-[11px] text-gray-400 mt-1">{platform.name} blocks automated data retrieval. You can enter your metrics manually to track your performance.</p>
              <button
                onClick={() => { setShowManualMetrics(true); setUrlResult(null); }}
                className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 font-medium transition"
                data-testid="add-metrics-manually-btn"
              >
                + Add metrics manually
              </button>
            </div>
          )}

          {/* API Mode */}
          {mode === 'api' && (
            <>
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
            </>
          )}

          {error && <p className="text-red-400 text-sm" data-testid="credential-error">{error}</p>}
        </div>
        <div className="flex gap-3 p-6 border-t border-white/10">
          <button onClick={onClose} className="flex-1 px-4 py-2.5 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition text-sm" data-testid="credential-cancel-btn">{urlResult ? 'Done' : 'Cancel'}</button>
          {!urlResult && (
            <button onClick={mode === 'url' ? handleSaveUrl : handleSaveApi} disabled={saving} className={`flex-1 px-4 py-2.5 ${mode === 'url' ? 'bg-cyan-600 hover:bg-cyan-700' : 'bg-blue-600 hover:bg-blue-700'} text-white rounded-lg transition text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2`} data-testid="credential-save-btn">
              {saving ? <><Loader2 size={14} className="animate-spin" /> Connecting...</> : mode === 'url' ? <><Link size={14} /> Connect with URL</> : <><Check size={14} /> Connect</>}
            </button>
          )}
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
          <div className="flex flex-col items-end gap-1">
            {conn.connected ? (
              <span className="shrink-0 flex items-center gap-1 px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-[10px] font-medium" data-testid={`status-connected-${conn.platform_id}`}>
                <Check size={10} /> Live
              </span>
            ) : (
              <span className="shrink-0 px-2 py-1 bg-white/5 text-gray-500 rounded-full text-[10px] font-medium" data-testid={`status-disconnected-${conn.platform_id}`}>
                Offline
              </span>
            )}
            {conn.has_live_api && (
              <span className="flex items-center gap-0.5 px-1.5 py-0.5 bg-cyan-500/10 text-cyan-400 rounded text-[9px] font-medium" data-testid={`live-api-badge-${conn.platform_id}`}>
                <Signal size={8} /> API
              </span>
            )}
            {conn.has_url_connect && !conn.has_live_api && (
              <span className="flex items-center gap-0.5 px-1.5 py-0.5 bg-violet-500/10 text-violet-400 rounded text-[9px] font-medium" data-testid={`url-connect-badge-${conn.platform_id}`}>
                <Link size={8} /> URL
              </span>
            )}
            {conn.connection_method === 'url' && conn.profile_url && (
              <span className="flex items-center gap-0.5 px-1.5 py-0.5 bg-emerald-500/5 text-emerald-300/60 rounded text-[9px]" data-testid={`connected-via-url-${conn.platform_id}`}>
                <Link size={7} /> via URL
              </span>
            )}
          </div>
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

/* ─── Mini Sparkline ───────────────────────────────────────────────── */
const Sparkline = ({ data, color = '#3b82f6', height = 32 }) => {
  if (!data || data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 100;
  const points = data.map((v, i) => `${(i / (data.length - 1)) * w},${height - ((v - min) / range) * (height - 4) - 2}`).join(' ');
  return (
    <svg viewBox={`0 0 ${w} ${height}`} className="w-full" style={{ height }} preserveAspectRatio="none">
      <polyline fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" points={points} />
    </svg>
  );
};

/* ─── Format Number ───────────────────────────────────────────────── */
const formatNum = (n) => {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toString();
};

/* ─── Data Source Badge ───────────────────────────────────────────── */
const DataSourceBadge = ({ source }) => {
  const isLive = source === 'live';
  return (
    <span className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[9px] font-semibold tracking-wide ${isLive ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400/70 border border-amber-500/10'}`} data-testid={`data-source-${isLive ? 'live' : 'simulated'}`}>
      {isLive ? <Wifi size={8} /> : <WifiOff size={8} />}
      {isLive ? 'LIVE' : 'SIM'}
    </span>
  );
};

/* ─── Analytics Platform Row ──────────────────────────────────────── */
const AnalyticsPlatformRow = ({ platform }) => {
  const meta = CATEGORY_META[platform.type] || CATEGORY_META.social_media;
  const Icon = meta.Icon;
  const isGrowing = platform.growth_rate > 0;
  return (
    <div className="flex items-center gap-4 px-4 py-3 hover:bg-white/[.02] transition" data-testid={`analytics-row-${platform.platform_id}`}>
      <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${meta.color} flex items-center justify-center shrink-0`}>
        <Icon size={14} className="text-white" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <p className="text-sm text-white font-medium truncate">{platform.name}</p>
          <DataSourceBadge source={platform.data_source} />
        </div>
        <p className="text-[10px] text-gray-500">{platform.type.replace(/_/g, ' ')}</p>
      </div>
      <div className="text-right w-20">
        <p className="text-sm font-semibold text-white" data-testid={`row-followers-${platform.platform_id}`}>{formatNum(platform.followers)}</p>
        <p className="text-[10px] text-gray-500">followers</p>
      </div>
      <div className="text-right w-14">
        <p className="text-sm font-semibold text-gray-300" data-testid={`row-posts-${platform.platform_id}`}>{formatNum(platform.posts || 0)}</p>
        <p className="text-[10px] text-gray-500">posts</p>
      </div>
      <div className="text-right w-16">
        <p className="text-sm font-semibold text-cyan-400" data-testid={`row-engagement-${platform.platform_id}`}>{platform.engagement_rate}%</p>
        <p className="text-[10px] text-gray-500">engage</p>
      </div>
      <div className="w-20 hidden sm:block">
        <Sparkline data={platform.daily_followers} color={isGrowing ? '#10b981' : '#ef4444'} height={24} />
      </div>
      <div className={`flex items-center gap-0.5 text-xs font-medium w-16 justify-end ${isGrowing ? 'text-emerald-400' : 'text-red-400'}`}>
        {isGrowing ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
        {Math.abs(platform.growth_rate)}%
      </div>
    </div>
  );
};

/* ─── Category Metrics Card ───────────────────────────────────────── */
const CategoryMetricsCard = ({ cat }) => {
  const meta = CATEGORY_META[cat.type] || CATEGORY_META.social_media;
  const Icon = meta.Icon;
  return (
    <div className="bg-[#1a1d2e] rounded-xl border border-white/5 p-4 hover:border-white/10 transition" data-testid={`cat-metric-${cat.type}`}>
      <div className="flex items-center gap-2.5 mb-3">
        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${meta.color} flex items-center justify-center`}>
          <Icon size={14} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white">{cat.label}</p>
          <div className="flex items-center gap-1.5">
            <p className="text-[10px] text-gray-500">{cat.platform_count} platform{cat.platform_count !== 1 ? 's' : ''}</p>
            {cat.live_count > 0 && (
              <span className="flex items-center gap-0.5 text-[9px] text-emerald-400"><Wifi size={7} />{cat.live_count} live</span>
            )}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2">
        <div>
          <p className="text-lg font-bold text-white">{formatNum(cat.total_followers)}</p>
          <p className="text-[10px] text-gray-500">followers</p>
        </div>
        <div>
          <p className="text-lg font-bold text-cyan-400">{cat.avg_engagement}%</p>
          <p className="text-[10px] text-gray-500">avg engage</p>
        </div>
        <div>
          <p className={`text-lg font-bold ${cat.avg_growth >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>{cat.avg_growth >= 0 ? '+' : ''}{cat.avg_growth}%</p>
          <p className="text-[10px] text-gray-500">growth</p>
        </div>
      </div>
    </div>
  );
};

/* ─── Main Dashboard ──────────────────────────────────────────────── */
const SocialMediaDashboardEnhanced = () => {
  const [connections, setConnections] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [platformMetrics, setPlatformMetrics] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
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
    } catch { setDashboardData({ platforms: [], total_followers: 0, total_posts: 0, avg_engagement: 0, connected_count: 0, total_platforms: 0, total_likes: 0, total_comments: 0, total_shares: 0, total_impressions: 0, total_reach: 0 }); }
  }, []);

  const fetchPlatformMetrics = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/api/social/metrics/platforms`, authHeaders());
      setPlatformMetrics(res.data);
    } catch { setPlatformMetrics({ platforms: [], categories: [], total_connected: 0 }); }
  }, []);

  const fetchPosts = useCallback(async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/api/social/posts`, authHeaders());
      setPosts(res.data.posts || []);
    } catch { setPosts([]); }
  }, []);

  useEffect(() => {
    Promise.all([fetchConnections(), fetchDashboard(), fetchPlatformMetrics(), fetchPosts()]).finally(() => setLoading(false));
  }, [fetchConnections, fetchDashboard, fetchPlatformMetrics, fetchPosts]);

  const handleRefreshMetrics = async () => {
    setRefreshing(true);
    try {
      await axios.post(`${BACKEND_URL}/api/social/metrics/refresh`, {}, authHeaders());
      await Promise.all([fetchDashboard(), fetchPlatformMetrics()]);
    } catch {}
    finally { setRefreshing(false); }
  };

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
    { id: 'analytics', label: 'Analytics', Icon: Activity, count: totalConnected },
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
            <button onClick={() => { fetchConnections(); fetchDashboard(); fetchPlatformMetrics(); }} className="px-3 py-2 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition text-sm flex items-center gap-1.5" data-testid="refresh-btn">
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

        {/* ── Analytics Tab ── */}
        {activeTab === 'analytics' && (
          <div className="space-y-6" data-testid="analytics-tab">
            {totalConnected === 0 ? (
              <div className="bg-[#1a1d2e] rounded-xl p-12 text-center border border-white/5">
                <Activity size={48} className="mx-auto text-gray-600 mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">No Platforms Connected</h3>
                <p className="text-sm text-gray-400 mb-4">Connect platforms to view analytics and metrics</p>
                <button onClick={() => setActiveTab('connections')} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm" data-testid="analytics-connect-cta">Connect Platforms</button>
              </div>
            ) : (
              <>
                {/* Data source status bar */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3 flex-wrap">
                    <p className="text-sm text-gray-400">Metrics for <span className="text-white font-medium">{totalConnected}</span> platforms</p>
                    {(dashboardData?.live_count > 0 || platformMetrics?.live_count > 0) && (
                      <span className="flex items-center gap-1 px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full text-[10px] font-medium" data-testid="live-metrics-count">
                        <Wifi size={10} /> {dashboardData?.live_count || platformMetrics?.live_count || 0} Live
                      </span>
                    )}
                    {(dashboardData?.simulated_count > 0 || platformMetrics?.simulated_count > 0) && (
                      <span className="flex items-center gap-1 px-2 py-1 bg-amber-500/10 text-amber-400/70 rounded-full text-[10px] font-medium" data-testid="simulated-metrics-count">
                        <WifiOff size={10} /> {dashboardData?.simulated_count || platformMetrics?.simulated_count || 0} Simulated
                      </span>
                    )}
                  </div>
                  <button onClick={handleRefreshMetrics} disabled={refreshing} className="px-3 py-1.5 border border-white/10 text-gray-300 rounded-lg hover:bg-white/5 transition text-xs flex items-center gap-1.5 disabled:opacity-50" data-testid="refresh-metrics-btn">
                    <RefreshCw size={12} className={refreshing ? 'animate-spin' : ''} /> {refreshing ? 'Refreshing...' : 'Refresh Metrics'}
                  </button>
                </div>

                {/* Live API Info Banner */}
                <div className="bg-[#151827] rounded-xl p-4 border border-cyan-500/10" data-testid="live-api-info-banner">
                  <div className="flex items-start gap-3">
                    <Signal size={16} className="text-cyan-400 mt-0.5 shrink-0" />
                    <div>
                      <p className="text-xs font-medium text-cyan-300 mb-1">Live API Integration Active</p>
                      <p className="text-[11px] text-gray-400 leading-relaxed">
                        Platforms with valid API credentials show <span className="text-emerald-400 font-medium">LIVE</span> real-time data.
                        Others display <span className="text-amber-400/70 font-medium">SIM</span> estimated metrics.
                        Add real credentials to a platform to unlock live metrics.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Aggregate Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="aggregate-metrics">
                  <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Users size={14} className="text-blue-400" />
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider">Followers</p>
                    </div>
                    <p className="text-xl font-bold text-white" data-testid="metric-total-followers">{formatNum(dashboardData?.total_followers || 0)}</p>
                  </div>
                  <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Heart size={14} className="text-rose-400" />
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider">Likes</p>
                    </div>
                    <p className="text-xl font-bold text-white" data-testid="metric-total-likes">{formatNum(dashboardData?.total_likes || 0)}</p>
                  </div>
                  <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <MessageCircle size={14} className="text-amber-400" />
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider">Comments</p>
                    </div>
                    <p className="text-xl font-bold text-white" data-testid="metric-total-comments">{formatNum(dashboardData?.total_comments || 0)}</p>
                  </div>
                  <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Share2 size={14} className="text-emerald-400" />
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider">Shares</p>
                    </div>
                    <p className="text-xl font-bold text-white" data-testid="metric-total-shares">{formatNum(dashboardData?.total_shares || 0)}</p>
                  </div>
                  <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Zap size={14} className="text-cyan-400" />
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider">Impressions</p>
                    </div>
                    <p className="text-xl font-bold text-white" data-testid="metric-total-impressions">{formatNum(dashboardData?.total_impressions || 0)}</p>
                  </div>
                  <div className="bg-[#1a1d2e] rounded-xl p-4 border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Activity size={14} className="text-violet-400" />
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider">Avg Engagement</p>
                    </div>
                    <p className="text-xl font-bold text-white" data-testid="metric-avg-engagement">{dashboardData?.avg_engagement || 0}%</p>
                  </div>
                </div>

                {/* Category Breakdown */}
                {platformMetrics?.categories?.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-3">Category Breakdown</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="category-breakdown">
                      {platformMetrics.categories.map(cat => (
                        <CategoryMetricsCard key={cat.type} cat={cat} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Top Platforms Table */}
                <div className="bg-[#1a1d2e] rounded-xl border border-white/5 overflow-hidden">
                  <div className="flex items-center justify-between p-4 border-b border-white/5">
                    <h3 className="text-sm font-semibold text-white">Platform Performance</h3>
                    <p className="text-[10px] text-gray-500">{platformMetrics?.platforms?.length || 0} platforms</p>
                  </div>
                  {/* Table header */}
                  <div className="flex items-center gap-4 px-4 py-2 text-[10px] text-gray-500 uppercase tracking-wider border-b border-white/5 bg-white/[.01]">
                    <div className="w-8 shrink-0" />
                    <div className="flex-1">Platform</div>
                    <div className="text-right w-20">Followers</div>
                    <div className="text-right w-16">Engage</div>
                    <div className="w-20 hidden sm:block text-center">Trend</div>
                    <div className="text-right w-16">Growth</div>
                  </div>
                  <div className="max-h-[500px] overflow-y-auto divide-y divide-white/[.03]" data-testid="platform-performance-list">
                    {(platformMetrics?.platforms || []).map(p => (
                      <AnalyticsPlatformRow key={p.platform_id} platform={p} />
                    ))}
                  </div>
                  {/* Legend */}
                  <div className="flex items-center gap-4 px-4 py-2.5 border-t border-white/5 bg-white/[.01]">
                    <span className="flex items-center gap-1 text-[10px] text-gray-500"><Wifi size={8} className="text-emerald-400" /> LIVE = Real API data</span>
                    <span className="flex items-center gap-1 text-[10px] text-gray-500"><WifiOff size={8} className="text-amber-400/70" /> SIM = Simulated estimates</span>
                  </div>
                </div>
              </>
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
