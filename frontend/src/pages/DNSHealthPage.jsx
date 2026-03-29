import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Search, Activity, Clock, Plus, Trash2, RefreshCw, CheckCircle, AlertTriangle, XCircle, Info, Globe, Shield, Mail, Server } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const RECORD_TYPE_OPTIONS = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV", "CAA"];

function HealthBadge({ status }) {
  const map = {
    pass: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    warn: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    fail: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
    info: { icon: Info, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  };
  const s = map[status] || map.info;
  const Icon = s.icon;
  return (
    <span data-testid={`health-badge-${status}`} className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${s.bg} ${s.color}`}>
      <Icon size={12} /> {status}
    </span>
  );
}

function ScoreRing({ score }) {
  const color = score >= 80 ? '#34d399' : score >= 50 ? '#fbbf24' : '#f87171';
  const circumference = 2 * Math.PI * 42;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div data-testid="health-score-ring" className="relative w-28 h-28 mx-auto">
      <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="8" />
        <circle cx="50" cy="50" r="42" fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" className="transition-all duration-700" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{score}</span>
        <span className="text-[10px] text-slate-400 uppercase tracking-wider">Score</span>
      </div>
    </div>
  );
}

export default function DNSHealthPage() {
  const [domain, setDomain] = useState('');
  const [selectedTypes, setSelectedTypes] = useState(["A", "AAAA", "MX", "NS", "TXT", "CNAME"]);
  const [lookupResults, setLookupResults] = useState(null);
  const [healthResult, setHealthResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [monitors, setMonitors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [healthLoading, setHealthLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('lookup');
  const [addMonitorDomain, setAddMonitorDomain] = useState('');
  const [addingMonitor, setAddingMonitor] = useState(false);
  const [refreshingId, setRefreshingId] = useState(null);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/dns/history?limit=15`, { headers });
      if (res.ok) { const d = await res.json(); setHistory(d.history || []); }
    } catch (e) { console.error(e); }
  }, []);

  const fetchMonitors = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/dns/monitors`, { headers });
      if (res.ok) { const d = await res.json(); setMonitors(d.monitors || []); }
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { fetchHistory(); fetchMonitors(); }, [fetchHistory, fetchMonitors]);

  const handleLookup = async (e) => {
    e.preventDefault();
    if (!domain.trim()) return;
    setLoading(true);
    setLookupResults(null);
    try {
      const res = await fetch(`${API}/api/dns/lookup`, {
        method: 'POST', headers,
        body: JSON.stringify({ domain: domain.trim(), record_types: selectedTypes }),
      });
      if (res.ok) {
        const d = await res.json();
        setLookupResults(d);
        fetchHistory();
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const handleHealthCheck = async (e) => {
    e.preventDefault();
    if (!domain.trim()) return;
    setHealthLoading(true);
    setHealthResult(null);
    try {
      const res = await fetch(`${API}/api/dns/health/${encodeURIComponent(domain.trim())}`, { headers });
      if (res.ok) setHealthResult(await res.json());
    } catch (e) { console.error(e); }
    setHealthLoading(false);
  };

  const toggleType = (t) => {
    setSelectedTypes(prev => prev.includes(t) ? prev.filter(x => x !== t) : [...prev, t]);
  };

  const handleAddMonitor = async () => {
    if (!addMonitorDomain.trim()) return;
    setAddingMonitor(true);
    try {
      const res = await fetch(`${API}/api/dns/monitors`, {
        method: 'POST', headers,
        body: JSON.stringify({ domain: addMonitorDomain.trim() }),
      });
      if (res.ok) { setAddMonitorDomain(''); fetchMonitors(); }
    } catch (e) { console.error(e); }
    setAddingMonitor(false);
  };

  const handleDeleteMonitor = async (monitorId) => {
    try {
      await fetch(`${API}/api/dns/monitors/${monitorId}`, { method: 'DELETE', headers });
      fetchMonitors();
    } catch (e) { console.error(e); }
  };

  const handleRefreshMonitor = async (monitorId) => {
    setRefreshingId(monitorId);
    try {
      await fetch(`${API}/api/dns/monitors/${monitorId}/refresh`, { method: 'POST', headers });
      fetchMonitors();
    } catch (e) { console.error(e); }
    setRefreshingId(null);
  };

  const checkIcons = {
    a_record: Globe,
    ipv6: Globe,
    nameservers: Server,
    mail: Mail,
    spf: Shield,
    dmarc: Shield,
    soa: Server,
    http: Activity,
    https: Activity,
  };

  return (
    <div data-testid="dns-health-page" className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">DNS Health Checker</h1>
        <p className="text-sm text-slate-400 mt-1">Lookup DNS records, run health checks, and monitor your domains</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-900 rounded-lg p-1 w-fit" data-testid="dns-tabs">
        {[
          { id: 'lookup', label: 'DNS Lookup', icon: Search },
          { id: 'health', label: 'Health Check', icon: Activity },
          { id: 'monitors', label: 'Monitors', icon: Globe },
          { id: 'history', label: 'History', icon: Clock },
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button key={tab.id} data-testid={`dns-tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}>
              <Icon size={14} /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Domain Input (shared between lookup and health) */}
      {(activeTab === 'lookup' || activeTab === 'health') && (
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="pt-6">
            <form onSubmit={activeTab === 'lookup' ? handleLookup : handleHealthCheck}
              className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1">
                <input data-testid="dns-domain-input" type="text" value={domain}
                  onChange={e => setDomain(e.target.value)}
                  placeholder="Enter domain (e.g. google.com)"
                  className="w-full px-4 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-violet-500 transition-colors" />
              </div>
              <button data-testid="dns-submit-btn" type="submit"
                disabled={loading || healthLoading || !domain.trim()}
                className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-sm font-medium transition-colors whitespace-nowrap">
                {(loading || healthLoading)
                  ? <><RefreshCw size={14} className="animate-spin" /> Checking...</>
                  : activeTab === 'lookup'
                    ? <><Search size={14} /> Lookup DNS</>
                    : <><Activity size={14} /> Run Health Check</>
                }
              </button>
            </form>

            {/* Record type selector for lookup tab */}
            {activeTab === 'lookup' && (
              <div className="mt-4 flex flex-wrap gap-2" data-testid="dns-type-selector">
                {RECORD_TYPE_OPTIONS.map(t => (
                  <button key={t} data-testid={`dns-type-${t}`}
                    onClick={() => toggleType(t)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      selectedTypes.includes(t)
                        ? 'bg-violet-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                    }`}>
                    {t}
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Lookup Results */}
      {activeTab === 'lookup' && lookupResults && (
        <div className="space-y-4" data-testid="dns-lookup-results">
          <h2 className="text-lg font-semibold text-white">Results for {lookupResults.domain}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(lookupResults.results).map(([type, data]) => (
              <Card key={type} className="bg-slate-900 border-slate-800">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between text-sm">
                    <span className="font-mono text-violet-400">{type}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      data.status === 'ok' ? 'bg-emerald-500/10 text-emerald-400'
                        : data.status === 'no_answer' ? 'bg-slate-500/10 text-slate-400'
                        : 'bg-red-500/10 text-red-400'
                    }`}>
                      {data.status === 'ok' ? `${data.count} record(s)` : data.status}
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {data.records && data.records.length > 0 ? (
                    <div className="space-y-1">
                      {data.records.map((r, i) => (
                        <div key={i} className="text-xs font-mono text-slate-300 bg-slate-800/50 px-3 py-1.5 rounded break-all">
                          {type === 'MX' ? `${r.priority} ${r.value}` :
                           type === 'SOA' ? `${r.mname} ${r.rname} (serial: ${r.serial})` :
                           type === 'SRV' ? `${r.priority} ${r.weight} ${r.port} ${r.target}` :
                           type === 'CAA' ? `${r.flags} ${r.tag} "${r.value}"` :
                           r.value}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">{data.error || 'No records'}</p>
                  )}
                  <div className="flex justify-between mt-2 text-[10px] text-slate-500">
                    {data.ttl != null && <span>TTL: {data.ttl}s</span>}
                    <span>{data.response_time_ms}ms</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Health Check Results */}
      {activeTab === 'health' && healthResult && (
        <div className="space-y-4" data-testid="dns-health-results">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <Card className="bg-slate-900 border-slate-800 lg:col-span-1">
              <CardHeader><CardTitle className="text-sm text-slate-300">Overall Health</CardTitle></CardHeader>
              <CardContent>
                <ScoreRing score={healthResult.health_score} />
                <p className="text-center text-xs text-slate-400 mt-3">{healthResult.domain}</p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800 lg:col-span-2">
              <CardHeader><CardTitle className="text-sm text-slate-300">Check Details</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(healthResult.checks).map(([key, check]) => {
                    const Icon = checkIcons[key] || Activity;
                    return (
                      <div key={key} data-testid={`health-check-${key}`}
                        className="flex items-center gap-3 p-2.5 rounded-lg bg-slate-800/50">
                        <Icon size={16} className="text-slate-400 shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-medium text-white capitalize">{key.replace(/_/g, ' ')}</span>
                            <HealthBadge status={check.status} />
                          </div>
                          <p className="text-[11px] text-slate-400 mt-0.5 truncate">{check.detail}</p>
                        </div>
                        {check.response_time_ms != null && (
                          <span className="text-[10px] text-slate-500 shrink-0">{check.response_time_ms}ms</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Monitors Tab */}
      {activeTab === 'monitors' && (
        <div className="space-y-4" data-testid="dns-monitors-section">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-sm text-slate-300">Add Domain to Monitor</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-3">
                <input data-testid="monitor-domain-input" type="text" value={addMonitorDomain}
                  onChange={e => setAddMonitorDomain(e.target.value)}
                  placeholder="e.g. bigmannentertainment.com"
                  className="flex-1 px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-violet-500" />
                <button data-testid="add-monitor-btn" onClick={handleAddMonitor}
                  disabled={addingMonitor || !addMonitorDomain.trim()}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium transition-colors">
                  <Plus size={14} /> Add
                </button>
              </div>
            </CardContent>
          </Card>

          {monitors.length === 0 ? (
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="py-12 text-center">
                <Globe size={40} className="mx-auto text-slate-600 mb-3" />
                <p className="text-sm text-slate-400">No monitored domains yet.</p>
                <p className="text-xs text-slate-500 mt-1">Add a domain above to start monitoring its DNS health.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {monitors.map(m => (
                <Card key={m.monitor_id} data-testid={`monitor-card-${m.monitor_id}`}
                  className="bg-slate-900 border-slate-800">
                  <CardContent className="pt-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-sm font-semibold text-white">{m.domain}</h3>
                        {m.last_checked
                          ? <p className="text-[10px] text-slate-500 mt-0.5">Last checked: {new Date(m.last_checked).toLocaleString()}</p>
                          : <p className="text-[10px] text-slate-500 mt-0.5">Never checked</p>}
                      </div>
                      <div className="flex items-center gap-1">
                        <button data-testid={`refresh-monitor-${m.monitor_id}`}
                          onClick={() => handleRefreshMonitor(m.monitor_id)}
                          disabled={refreshingId === m.monitor_id}
                          className="p-1.5 rounded-md hover:bg-slate-800 transition-colors disabled:opacity-50">
                          <RefreshCw size={14} className={`text-slate-400 ${refreshingId === m.monitor_id ? 'animate-spin' : ''}`} />
                        </button>
                        <button data-testid={`delete-monitor-${m.monitor_id}`}
                          onClick={() => handleDeleteMonitor(m.monitor_id)}
                          className="p-1.5 rounded-md hover:bg-red-900/30 transition-colors">
                          <Trash2 size={14} className="text-red-400" />
                        </button>
                      </div>
                    </div>
                    {m.last_health_score != null && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs text-slate-400">Health Score</span>
                          <span className={`text-xs font-bold ${
                            m.last_health_score >= 80 ? 'text-emerald-400' :
                            m.last_health_score >= 50 ? 'text-amber-400' : 'text-red-400'
                          }`}>{m.last_health_score}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full transition-all duration-500 ${
                            m.last_health_score >= 80 ? 'bg-emerald-500' :
                            m.last_health_score >= 50 ? 'bg-amber-500' : 'bg-red-500'
                          }`} style={{ width: `${m.last_health_score}%` }} />
                        </div>
                      </div>
                    )}
                    {m.last_checks && (
                      <div className="mt-3 flex flex-wrap gap-1">
                        {Object.entries(m.last_checks).map(([k, v]) => (
                          <span key={k} className={`text-[10px] px-1.5 py-0.5 rounded ${
                            v.status === 'pass' ? 'bg-emerald-500/10 text-emerald-400' :
                            v.status === 'warn' ? 'bg-amber-500/10 text-amber-400' :
                            v.status === 'fail' ? 'bg-red-500/10 text-red-400' :
                            'bg-blue-500/10 text-blue-400'
                          }`}>{k.replace(/_/g, ' ')}</span>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <Card className="bg-slate-900 border-slate-800" data-testid="dns-history-section">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm text-slate-300">Recent Lookups</CardTitle>
            <button data-testid="refresh-history-btn" onClick={fetchHistory}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors">
              <RefreshCw size={12} /> Refresh
            </button>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <div className="py-8 text-center">
                <Clock size={32} className="mx-auto text-slate-600 mb-2" />
                <p className="text-sm text-slate-400">No lookups yet.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-500 border-b border-slate-800">
                      <th className="text-left py-2 px-2">Domain</th>
                      <th className="text-left py-2 px-2">Types</th>
                      <th className="text-left py-2 px-2">Results</th>
                      <th className="text-left py-2 px-2">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((h, i) => (
                      <tr key={h.lookup_id || i} className="border-b border-slate-800/50 text-slate-300 hover:bg-slate-800/30">
                        <td className="py-2 px-2 font-mono text-violet-400">{h.domain}</td>
                        <td className="py-2 px-2">
                          <div className="flex flex-wrap gap-1">
                            {h.record_types?.map(t => (
                              <span key={t} className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px]">{t}</span>
                            ))}
                          </div>
                        </td>
                        <td className="py-2 px-2">
                          <div className="flex flex-wrap gap-1">
                            {h.result_summary && Object.entries(h.result_summary).map(([rt, s]) => (
                              <span key={rt} className={`px-1.5 py-0.5 rounded text-[10px] ${
                                s.status === 'ok' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-700 text-slate-400'
                              }`}>{rt}: {s.count}</span>
                            ))}
                          </div>
                        </td>
                        <td className="py-2 px-2 text-slate-500 whitespace-nowrap">
                          {h.created_at ? new Date(h.created_at).toLocaleString() : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
