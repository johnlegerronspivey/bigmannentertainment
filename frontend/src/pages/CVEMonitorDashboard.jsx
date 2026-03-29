import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Shield, AlertTriangle, Eye, EyeOff, Plus, Trash2, RefreshCw, Bell, Search, Activity, CheckCircle, XCircle, Clock, ChevronDown, ChevronUp, ExternalLink, Filter } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api/cve-monitor`;

const SEV_STYLE = {
  critical: { bg: 'bg-red-500/15', text: 'text-red-400', border: 'border-red-500/30', dot: 'bg-red-500' },
  high: { bg: 'bg-orange-500/15', text: 'text-orange-400', border: 'border-orange-500/30', dot: 'bg-orange-500' },
  medium: { bg: 'bg-amber-500/15', text: 'text-amber-400', border: 'border-amber-500/30', dot: 'bg-amber-500' },
  low: { bg: 'bg-blue-500/15', text: 'text-blue-400', border: 'border-blue-500/30', dot: 'bg-blue-500' },
  info: { bg: 'bg-slate-500/15', text: 'text-slate-400', border: 'border-slate-500/30', dot: 'bg-slate-500' },
};

function SeverityBadge({ severity }) {
  const s = SEV_STYLE[severity] || SEV_STYLE.info;
  return (
    <span data-testid={`severity-badge-${severity}`} className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold uppercase tracking-wide ${s.bg} ${s.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {severity}
    </span>
  );
}

function StatCard({ label, value, icon: Icon, color = 'text-cyan-400', bgColor = 'bg-cyan-500/10' }) {
  return (
    <Card className="bg-slate-800/60 border-slate-700/50">
      <CardContent className="p-4 flex items-center gap-4">
        <div className={`p-2.5 rounded-xl ${bgColor}`}>
          <Icon className={`w-5 h-5 ${color}`} />
        </div>
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          <p className="text-xs text-slate-400 mt-0.5">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function TrendBar({ data }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map(d => d.count), 1);
  return (
    <div data-testid="trend-bar" className="flex items-end gap-1 h-16">
      {data.map((d, i) => (
        <div key={i} className="flex-1 flex flex-col items-center gap-1">
          <div
            className="w-full bg-cyan-500/40 rounded-t-sm transition-all duration-300 min-h-[2px]"
            style={{ height: `${Math.max((d.count / max) * 100, 5)}%` }}
            title={`${d.date}: ${d.count} CVEs`}
          />
          <span className="text-[9px] text-slate-500">{d.date.slice(5)}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Overview Tab ─────────────────────────────────────────────
function OverviewTab({ stats, loading, onRefreshFeed }) {
  if (loading) return <div className="text-center py-16 text-slate-400">Loading stats...</div>;
  if (!stats) return <div className="text-center py-16 text-slate-400">No stats available. Try refreshing the feed.</div>;

  return (
    <div data-testid="overview-tab" className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Feed Entries" value={stats.total_feed_entries || 0} icon={Activity} />
        <StatCard label="Active Watches" value={stats.active_watches || 0} icon={Eye} color="text-emerald-400" bgColor="bg-emerald-500/10" />
        <StatCard label="Total Alerts" value={stats.total_alerts || 0} icon={Bell} color="text-amber-400" bgColor="bg-amber-500/10" />
        <StatCard label="New Alerts" value={stats.new_alerts || 0} icon={AlertTriangle} color="text-red-400" bgColor="bg-red-500/10" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-slate-800/60 border-slate-700/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-300">Severity Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2.5">
              {Object.entries(stats.severity_breakdown || {}).map(([sev, count]) => {
                const s = SEV_STYLE[sev] || SEV_STYLE.info;
                const total = Object.values(stats.severity_breakdown || {}).reduce((a, b) => a + b, 1);
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={sev} className="flex items-center gap-3">
                    <span className={`w-16 text-xs font-medium uppercase ${s.text}`}>{sev}</span>
                    <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${s.dot}`} style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-xs text-slate-400 w-8 text-right">{count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/60 border-slate-700/50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-slate-300">7-Day Trend</CardTitle>
              <button
                data-testid="refresh-feed-btn"
                onClick={onRefreshFeed}
                className="flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                <RefreshCw size={12} /> Refresh Feed
              </button>
            </div>
          </CardHeader>
          <CardContent>
            <TrendBar data={stats.daily_trend} />
            {stats.last_refresh && (
              <p className="text-[10px] text-slate-500 mt-3">
                Last refresh: {new Date(stats.last_refresh.timestamp).toLocaleString()} ({stats.last_refresh.results_count} results)
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ─── Feed Tab ─────────────────────────────────────────────────
function FeedTab({ onRefreshFeed, refreshing }) {
  const [feed, setFeed] = useState([]);
  const [feedTotal, setFeedTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sevFilter, setSevFilter] = useState('');
  const [expanded, setExpanded] = useState(null);

  const fetchFeed = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (sevFilter) params.set('severity', sevFilter);
      params.set('limit', '50');
      const res = await fetch(`${API}/feed?${params}`);
      const data = await res.json();
      setFeed(data.items || []);
      setFeedTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [search, sevFilter]);

  useEffect(() => { fetchFeed(); }, [fetchFeed]);

  return (
    <div data-testid="feed-tab" className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            data-testid="feed-search"
            type="text"
            placeholder="Search CVE ID or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
        <select
          data-testid="feed-severity-filter"
          value={sevFilter}
          onChange={(e) => setSevFilter(e.target.value)}
          className="px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <button
          data-testid="refresh-nvd-btn"
          onClick={onRefreshFeed}
          disabled={refreshing}
          className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Fetching...' : 'Fetch from NVD'}
        </button>
      </div>

      <p className="text-xs text-slate-500">{feedTotal} entries in feed</p>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading feed...</div>
      ) : feed.length === 0 ? (
        <div className="text-center py-12 text-slate-500">No CVEs in feed. Click &quot;Fetch from NVD&quot; to pull latest vulnerabilities.</div>
      ) : (
        <div className="space-y-2">
          {feed.map((item) => (
            <div key={item.cve_id} className="bg-slate-800/60 border border-slate-700/50 rounded-lg overflow-hidden">
              <button
                data-testid={`feed-item-${item.cve_id}`}
                onClick={() => setExpanded(expanded === item.cve_id ? null : item.cve_id)}
                className="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-slate-700/30 transition-colors"
              >
                <SeverityBadge severity={item.severity} />
                <span className="text-sm font-mono text-cyan-300 whitespace-nowrap">{item.cve_id}</span>
                <span className="text-sm text-slate-300 truncate flex-1">{item.description?.slice(0, 100)}</span>
                {item.cvss_score > 0 && (
                  <span className="text-xs font-semibold text-slate-400 bg-slate-700 px-2 py-0.5 rounded">CVSS {item.cvss_score}</span>
                )}
                <span className="text-xs text-slate-500 whitespace-nowrap">{item.published?.slice(0, 10)}</span>
                {expanded === item.cve_id ? <ChevronUp size={16} className="text-slate-400" /> : <ChevronDown size={16} className="text-slate-400" />}
              </button>
              {expanded === item.cve_id && (
                <div className="px-4 pb-4 border-t border-slate-700/50 pt-3 space-y-3">
                  <p className="text-sm text-slate-300 leading-relaxed">{item.description}</p>
                  {item.cwe_ids?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {item.cwe_ids.map((cwe) => (
                        <span key={cwe} className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">{cwe}</span>
                      ))}
                    </div>
                  )}
                  {item.affected_products?.length > 0 && (
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Affected Products:</p>
                      <div className="flex flex-wrap gap-1.5">
                        {item.affected_products.map((p) => (
                          <span key={p} className="text-xs bg-purple-500/15 text-purple-300 px-2 py-0.5 rounded">{p}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {item.references?.length > 0 && (
                    <div>
                      <p className="text-xs text-slate-500 mb-1">References:</p>
                      {item.references.filter(Boolean).map((ref, i) => (
                        <a key={i} href={ref} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 truncate">
                          <ExternalLink size={10} /> {ref}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Watches Tab ──────────────────────────────────────────────
function WatchesTab() {
  const [watches, setWatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: '', keyword: '', watch_type: 'keyword', severity_filter: 'all' });
  const [refreshingId, setRefreshingId] = useState(null);

  const fetchWatches = useCallback(async () => {
    try {
      const res = await fetch(`${API}/watches`);
      const data = await res.json();
      setWatches(data || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchWatches(); }, [fetchWatches]);

  const addWatch = async () => {
    if (!form.name || !form.keyword) return;
    try {
      await fetch(`${API}/watches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      setForm({ name: '', keyword: '', watch_type: 'keyword', severity_filter: 'all' });
      setShowAdd(false);
      fetchWatches();
    } catch (e) { console.error(e); }
  };

  const toggleWatch = async (id) => {
    await fetch(`${API}/watches/${id}/toggle`, { method: 'PUT' });
    fetchWatches();
  };

  const deleteWatch = async (id) => {
    await fetch(`${API}/watches/${id}`, { method: 'DELETE' });
    fetchWatches();
  };

  const refreshWatch = async (id) => {
    setRefreshingId(id);
    try {
      await fetch(`${API}/watches/${id}/refresh`, { method: 'POST' });
      fetchWatches();
    } catch (e) { console.error(e); }
    setRefreshingId(null);
  };

  return (
    <div data-testid="watches-tab" className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-300">{watches.length} Watch Rules</h3>
        <button
          data-testid="add-watch-btn"
          onClick={() => setShowAdd(!showAdd)}
          className="flex items-center gap-1.5 bg-cyan-600 hover:bg-cyan-700 text-white px-3 py-2 rounded-lg text-sm transition-colors"
        >
          <Plus size={14} /> Add Watch
        </button>
      </div>

      {showAdd && (
        <Card className="bg-slate-800/80 border-cyan-500/30">
          <CardContent className="p-4 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                data-testid="watch-name-input"
                placeholder="Watch Name (e.g., React Vulnerabilities)"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <input
                data-testid="watch-keyword-input"
                placeholder="Keyword (e.g., react, python, openssl)"
                value={form.keyword}
                onChange={(e) => setForm({ ...form, keyword: e.target.value })}
                className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
              <select
                data-testid="watch-type-select"
                value={form.watch_type}
                onChange={(e) => setForm({ ...form, watch_type: e.target.value })}
                className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="keyword">Keyword</option>
                <option value="package">Package</option>
                <option value="vendor">Vendor</option>
              </select>
              <select
                data-testid="watch-severity-select"
                value={form.severity_filter}
                onChange={(e) => setForm({ ...form, severity_filter: e.target.value })}
                className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical+</option>
                <option value="high">High+</option>
                <option value="medium">Medium+</option>
              </select>
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowAdd(false)} className="px-3 py-1.5 text-sm text-slate-400 hover:text-white">Cancel</button>
              <button
                data-testid="save-watch-btn"
                onClick={addWatch}
                className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm"
              >
                Save Watch
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading watches...</div>
      ) : watches.length === 0 ? (
        <div className="text-center py-12 text-slate-500">No watch rules yet. Add one to start monitoring.</div>
      ) : (
        <div className="space-y-2">
          {watches.map((w) => (
            <div key={w.id} data-testid={`watch-item-${w.id}`} className={`flex items-center gap-3 px-4 py-3 rounded-lg border transition-colors ${w.enabled ? 'bg-slate-800/60 border-slate-700/50' : 'bg-slate-900/40 border-slate-800/50 opacity-60'}`}>
              <button data-testid={`toggle-watch-${w.id}`} onClick={() => toggleWatch(w.id)} className="shrink-0">
                {w.enabled ? <Eye size={18} className="text-emerald-400" /> : <EyeOff size={18} className="text-slate-500" />}
              </button>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white truncate">{w.name}</span>
                  <span className="text-xs bg-slate-700 text-slate-400 px-1.5 py-0.5 rounded">{w.watch_type}</span>
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="text-xs text-cyan-400 font-mono">{w.keyword}</span>
                  <span className="text-xs text-slate-500">Sev: {w.severity_filter}</span>
                  {w.alerts_count > 0 && (
                    <span className="text-xs bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded">{w.alerts_count} alerts</span>
                  )}
                </div>
              </div>
              {w.last_checked && <span className="text-[10px] text-slate-500 hidden sm:block">{new Date(w.last_checked).toLocaleString()}</span>}
              <button
                data-testid={`refresh-watch-${w.id}`}
                onClick={() => refreshWatch(w.id)}
                disabled={refreshingId === w.id}
                className="p-1.5 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <RefreshCw size={14} className={`text-slate-400 ${refreshingId === w.id ? 'animate-spin' : ''}`} />
              </button>
              <button
                data-testid={`delete-watch-${w.id}`}
                onClick={() => deleteWatch(w.id)}
                className="p-1.5 hover:bg-red-500/20 rounded-lg transition-colors"
              >
                <Trash2 size={14} className="text-slate-400 hover:text-red-400" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Alerts Tab ───────────────────────────────────────────────
function AlertsTab() {
  const [alerts, setAlerts] = useState([]);
  const [newCount, setNewCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  const fetchAlerts = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter) params.set('status', statusFilter);
      params.set('limit', '50');
      const res = await fetch(`${API}/alerts?${params}`);
      const data = await res.json();
      setAlerts(data.items || []);
      setNewCount(data.new_count || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [statusFilter]);

  useEffect(() => { fetchAlerts(); }, [fetchAlerts]);

  const acknowledgeAlert = async (id) => {
    await fetch(`${API}/alerts/${id}/acknowledge`, { method: 'PUT' });
    fetchAlerts();
  };

  const dismissAlert = async (id) => {
    await fetch(`${API}/alerts/${id}/dismiss`, { method: 'PUT' });
    fetchAlerts();
  };

  const acknowledgeAll = async () => {
    await fetch(`${API}/alerts/acknowledge-all`, { method: 'POST' });
    fetchAlerts();
  };

  const STATUS_ICON = {
    new: { icon: AlertTriangle, color: 'text-red-400' },
    acknowledged: { icon: CheckCircle, color: 'text-amber-400' },
    dismissed: { icon: XCircle, color: 'text-slate-500' },
  };

  return (
    <div data-testid="alerts-tab" className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-medium text-slate-300">Alerts</h3>
          {newCount > 0 && <span className="bg-red-500/20 text-red-400 text-xs font-semibold px-2 py-0.5 rounded-full">{newCount} new</span>}
        </div>
        <div className="flex items-center gap-2">
          <select
            data-testid="alert-status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="dismissed">Dismissed</option>
          </select>
          {newCount > 0 && (
            <button
              data-testid="acknowledge-all-btn"
              onClick={acknowledgeAll}
              className="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm"
            >
              Ack All
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading alerts...</div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-12 text-slate-500">No alerts yet. Alerts are generated when watched keywords match new CVEs.</div>
      ) : (
        <div className="space-y-2">
          {alerts.map((alert) => {
            const si = STATUS_ICON[alert.status] || STATUS_ICON.new;
            const StatusIcon = si.icon;
            return (
              <div key={alert.id} data-testid={`alert-item-${alert.id}`} className="flex items-start gap-3 px-4 py-3 bg-slate-800/60 border border-slate-700/50 rounded-lg">
                <StatusIcon size={18} className={`mt-0.5 shrink-0 ${si.color}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-mono text-cyan-300">{alert.cve_id}</span>
                    <SeverityBadge severity={alert.severity} />
                    {alert.cvss_score > 0 && <span className="text-xs text-slate-400 bg-slate-700 px-1.5 py-0.5 rounded">CVSS {alert.cvss_score}</span>}
                  </div>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">{alert.description}</p>
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className="text-[10px] text-slate-500">Watch: {alert.watch_name || alert.keyword}</span>
                    <span className="text-[10px] text-slate-500">{new Date(alert.created_at).toLocaleString()}</span>
                  </div>
                </div>
                {alert.status === 'new' && (
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      data-testid={`ack-alert-${alert.id}`}
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="p-1.5 hover:bg-amber-500/20 rounded-lg transition-colors"
                      title="Acknowledge"
                    >
                      <CheckCircle size={14} className="text-amber-400" />
                    </button>
                    <button
                      data-testid={`dismiss-alert-${alert.id}`}
                      onClick={() => dismissAlert(alert.id)}
                      className="p-1.5 hover:bg-red-500/20 rounded-lg transition-colors"
                      title="Dismiss"
                    >
                      <XCircle size={14} className="text-slate-400" />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── Main Dashboard ───────────────────────────────────────────
const TABS = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'feed', label: 'CVE Feed', icon: Shield },
  { id: 'watches', label: 'Watch Rules', icon: Eye },
  { id: 'alerts', label: 'Alerts', icon: Bell },
];

export default function CVEMonitorDashboard() {
  const [tab, setTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [newAlerts, setNewAlerts] = useState(0);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${API}/stats`);
      const data = await res.json();
      setStats(data);
      setNewAlerts(data.new_alerts || 0);
    } catch (e) { console.error(e); }
    setStatsLoading(false);
  }, []);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  const handleRefreshFeed = async () => {
    setRefreshing(true);
    try {
      await fetch(`${API}/feed/refresh`, { method: 'POST' });
      await fetchStats();
    } catch (e) { console.error(e); }
    setRefreshing(false);
  };

  return (
    <div data-testid="cve-monitor-dashboard" className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800/60 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-500/10 rounded-xl">
                <Shield className="w-7 h-7 text-red-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">CVE Monitor</h1>
                <p className="text-xs text-slate-400">Automated vulnerability tracking from NVD feeds</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {newAlerts > 0 && (
                <button
                  data-testid="alert-badge-header"
                  onClick={() => setTab('alerts')}
                  className="flex items-center gap-1.5 bg-red-500/20 text-red-400 px-3 py-1.5 rounded-lg text-xs font-semibold"
                >
                  <Bell size={14} /> {newAlerts} New Alert{newAlerts !== 1 ? 's' : ''}
                </button>
              )}
              <button
                data-testid="header-refresh-btn"
                onClick={handleRefreshFeed}
                disabled={refreshing}
                className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Fetching...' : 'Refresh Feed'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800/60 bg-slate-900/40">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1 overflow-x-auto py-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                data-testid={`monitor-tab-${t.id}`}
                onClick={() => setTab(t.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm transition-all whitespace-nowrap ${
                  tab === t.id
                    ? 'bg-cyan-500/10 text-cyan-400 font-medium shadow-lg shadow-cyan-500/5'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <t.icon className="w-4 h-4" />
                {t.label}
                {t.id === 'alerts' && newAlerts > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-xs">{newAlerts}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {tab === 'overview' && <OverviewTab stats={stats} loading={statsLoading} onRefreshFeed={handleRefreshFeed} />}
        {tab === 'feed' && <FeedTab onRefreshFeed={handleRefreshFeed} refreshing={refreshing} />}
        {tab === 'watches' && <WatchesTab />}
        {tab === 'alerts' && <AlertsTab />}
      </div>
    </div>
  );
}
