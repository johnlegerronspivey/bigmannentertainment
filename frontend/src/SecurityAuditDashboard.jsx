import React, { useState, useEffect, useCallback, useRef } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SEVERITY_COLORS = {
  critical: { bg: 'bg-red-900/30', border: 'border-red-500', text: 'text-red-400', badge: 'bg-red-500/20 text-red-300', dot: '#f87171' },
  high: { bg: 'bg-orange-900/30', border: 'border-orange-500', text: 'text-orange-400', badge: 'bg-orange-500/20 text-orange-300', dot: '#fb923c' },
  moderate: { bg: 'bg-yellow-900/30', border: 'border-yellow-500', text: 'text-yellow-400', badge: 'bg-yellow-500/20 text-yellow-300', dot: '#facc15' },
  low: { bg: 'bg-blue-900/30', border: 'border-blue-500', text: 'text-blue-400', badge: 'bg-blue-500/20 text-blue-300', dot: '#60a5fa' },
};

const GRADE_COLORS = { A: 'text-emerald-400', B: 'text-green-400', C: 'text-yellow-400', D: 'text-orange-400', F: 'text-red-400' };

/* ─── Small Components ─────────────────────────────────────── */

function SecurityScoreRing({ score, grade }) {
  const r = 54, c = 2 * Math.PI * r, off = c - (score / 100) * c;
  const color = score >= 90 ? '#34d399' : score >= 75 ? '#4ade80' : score >= 60 ? '#facc15' : score >= 40 ? '#fb923c' : '#f87171';
  return (
    <div className="flex flex-col items-center" data-testid="security-score-ring">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={r} fill="none" stroke="#1e293b" strokeWidth="10" />
        <circle cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={off}
          style={{ transition: 'stroke-dashoffset 1s ease', transform: 'rotate(-90deg)', transformOrigin: '70px 70px' }} />
        <text x="70" y="62" textAnchor="middle" fill="white" fontSize="28" fontWeight="bold">{score}</text>
        <text x="70" y="84" textAnchor="middle" fill="#94a3b8" fontSize="13">/ 100</text>
      </svg>
      <span className={`text-2xl font-bold mt-1 ${GRADE_COLORS[grade] || 'text-gray-400'}`} data-testid="security-grade">Grade {grade}</span>
    </div>
  );
}

function SeverityBar({ label, count, total, color }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div className="flex items-center gap-3 text-sm" data-testid={`severity-bar-${label}`}>
      <span className={`w-20 font-medium capitalize ${color.text}`}>{label}</span>
      <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, backgroundColor: color.dot }} />
      </div>
      <span className="w-8 text-right text-slate-300 font-mono">{count}</span>
    </div>
  );
}

function VulnCard({ vuln, stack }) {
  const [open, setOpen] = useState(false);
  const colors = SEVERITY_COLORS[vuln.severity] || SEVERITY_COLORS.low;
  return (
    <div className={`border rounded-lg p-4 ${colors.bg} ${colors.border} border-opacity-30 transition-all`} data-testid={`vuln-card-${vuln.module}`}>
      <div className="flex items-start justify-between cursor-pointer" onClick={() => setOpen(!open)}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${colors.badge}`}>{vuln.severity}</span>
            <span className="text-white font-semibold truncate">{vuln.module}</span>
            <span className="px-2 py-0.5 rounded bg-slate-700 text-slate-300 text-xs">{stack}</span>
          </div>
          <p className="text-slate-300 text-sm mt-1 truncate">{vuln.title || vuln.description}</p>
        </div>
        <svg className={`w-5 h-5 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </div>
      {open && (
        <div className="mt-3 pt-3 border-t border-slate-600/50 space-y-2 text-sm">
          {vuln.vulnerable_versions && <div><span className="text-slate-400">Vulnerable:</span> <span className="text-red-300 font-mono">{vuln.vulnerable_versions}</span></div>}
          {vuln.patched_versions && <div><span className="text-slate-400">Patched:</span> <span className="text-green-300 font-mono">{vuln.patched_versions}</span></div>}
          {vuln.installed_version && <div><span className="text-slate-400">Installed:</span> <span className="text-slate-300 font-mono">{vuln.installed_version}</span></div>}
          {vuln.fix_versions?.length > 0 && <div><span className="text-slate-400">Fix:</span> <span className="text-green-300 font-mono">{vuln.fix_versions.join(', ')}</span></div>}
          {vuln.recommendation && <div><span className="text-slate-400">Fix:</span> <span className="text-slate-200">{vuln.recommendation}</span></div>}
          {vuln.url && <a href={vuln.url} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline inline-block">View Advisory</a>}
        </div>
      )}
    </div>
  );
}

/* ─── Trend Chart (pure SVG) ───────────────────────────────── */

function TrendChart({ data }) {
  if (!data || data.length < 2) return <p className="text-slate-500 text-sm text-center py-8">Need at least 2 scans for trend data. Run more audits.</p>;

  const w = 700, h = 180, px = 40, py = 20;
  const scores = data.map(d => d.security_score);
  const vulns = data.map(d => d.total_vulnerabilities);
  const minS = Math.min(...scores, 0), maxS = Math.max(...scores, 100);
  const maxV = Math.max(...vulns, 1);

  const pts = (arr, max, min = 0) => arr.map((v, i) => {
    const x = px + (i / (arr.length - 1)) * (w - 2 * px);
    const y = py + (1 - (v - min) / (max - min || 1)) * (h - 2 * py);
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5" data-testid="trend-chart">
      <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Security Score Trend</h3>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ maxHeight: 200 }}>
        {/* Grid */}
        {[0, 25, 50, 75, 100].map(v => {
          const y = py + (1 - v / 100) * (h - 2 * py);
          return <g key={v}><line x1={px} y1={y} x2={w - px} y2={y} stroke="#334155" strokeWidth="0.5" /><text x={px - 6} y={y + 4} fill="#64748b" fontSize="10" textAnchor="end">{v}</text></g>;
        })}
        {/* Score line */}
        <polyline points={pts(scores, maxS, minS)} fill="none" stroke="#34d399" strokeWidth="2.5" strokeLinejoin="round" />
        {scores.map((s, i) => {
          const x = px + (i / (scores.length - 1)) * (w - 2 * px);
          const y = py + (1 - (s - minS) / (maxS - minS || 1)) * (h - 2 * py);
          return <circle key={i} cx={x} cy={y} r="3.5" fill="#34d399" />;
        })}
        {/* Vuln line */}
        <polyline points={pts(vulns, maxV)} fill="none" stroke="#f87171" strokeWidth="2" strokeDasharray="4 3" strokeLinejoin="round" />
        {/* Legend */}
        <circle cx={w - 180} cy={12} r="4" fill="#34d399" /><text x={w - 172} y={16} fill="#94a3b8" fontSize="10">Score</text>
        <line x1={w - 110} y1={12} x2={w - 90} y2={12} stroke="#f87171" strokeWidth="2" strokeDasharray="4 3" /><text x={w - 86} y={16} fill="#94a3b8" fontSize="10">Vulns</text>
      </svg>
      {/* X-axis labels */}
      <div className="flex justify-between px-10 mt-1">
        {data.length <= 10 ? data.map((d, i) => (
          <span key={i} className="text-[10px] text-slate-500">{new Date(d.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>
        )) : [0, Math.floor(data.length / 2), data.length - 1].map(i => (
          <span key={i} className="text-[10px] text-slate-500">{new Date(data[i].timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>
        ))}
      </div>
    </div>
  );
}

/* ─── Alert Card ───────────────────────────────────────────── */

function AlertCard({ alert, onDismiss }) {
  const colors = SEVERITY_COLORS[alert.severity] || SEVERITY_COLORS.low;
  return (
    <div className={`border rounded-lg p-4 ${colors.bg} ${colors.border} border-opacity-30 flex items-start gap-3 ${!alert.read ? 'ring-1 ring-indigo-500/30' : ''}`} data-testid={`alert-card-${alert.module}`}>
      <div className={`w-2 h-2 mt-2 rounded-full flex-shrink-0 ${!alert.read ? 'bg-indigo-400' : 'bg-slate-600'}`} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${colors.badge}`}>{alert.severity}</span>
          <span className="text-white font-semibold text-sm">{alert.module}</span>
          <span className="px-2 py-0.5 rounded bg-slate-700 text-slate-300 text-xs">{alert.stack}</span>
        </div>
        <p className="text-slate-200 text-sm mt-1">{alert.title}</p>
        {alert.description && <p className="text-slate-400 text-xs mt-1">{alert.description}</p>}
        <p className="text-slate-500 text-xs mt-2">{new Date(alert.timestamp).toLocaleString()}</p>
      </div>
      <button onClick={() => onDismiss(alert.timestamp)} className="text-slate-500 hover:text-slate-300 transition-colors p-1" title="Dismiss" data-testid="dismiss-alert-btn">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
    </div>
  );
}

/* ─── Monitor Config Panel ─────────────────────────────────── */

function MonitorPanel({ config, onUpdate, onScanNow, scanning, onTestEmail, testingEmail }) {
  if (!config) return null;
  const toggle = (key) => onUpdate({ [key]: !config[key] });

  return (
    <div className="space-y-6" data-testid="monitor-panel">
      {/* Status card */}
      <div className={`rounded-xl p-5 border ${config.enabled ? 'bg-emerald-900/15 border-emerald-500/30' : 'bg-slate-800/50 border-slate-700/50'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${config.enabled ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
            <div>
              <h3 className="font-semibold text-white">{config.enabled ? 'Monitor Active' : 'Monitor Inactive'}</h3>
              <p className="text-sm text-slate-400">{config.enabled ? `Scanning every ${config.interval_hours}h` : 'Enable to start automated scanning'}</p>
            </div>
          </div>
          <button onClick={() => toggle('enabled')}
            className={`relative w-14 h-7 rounded-full transition-colors ${config.enabled ? 'bg-emerald-600' : 'bg-slate-600'}`}
            data-testid="monitor-toggle">
            <span className={`absolute top-0.5 left-0.5 w-6 h-6 bg-white rounded-full transition-transform shadow ${config.enabled ? 'translate-x-7' : ''}`} />
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 text-center">
          <p className="text-2xl font-bold text-white">{config.total_scans || 0}</p>
          <p className="text-xs text-slate-400 mt-1">Total Scans</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 text-center">
          <p className="text-sm font-mono text-slate-300">{config.last_scan ? new Date(config.last_scan).toLocaleString() : 'Never'}</p>
          <p className="text-xs text-slate-400 mt-1">Last Scan</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 text-center">
          <p className="text-sm font-mono text-slate-300">{config.next_scan ? new Date(config.next_scan).toLocaleString() : 'N/A'}</p>
          <p className="text-xs text-slate-400 mt-1">Next Scan</p>
        </div>
      </div>

      {/* Email notifications */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
          Email Notifications
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <span className="font-medium text-white">Send email on new CVEs</span>
            <p className="text-xs text-slate-400 mt-0.5">Get notified via email when vulnerabilities match your severity filters</p>
          </div>
          <button onClick={() => toggle('email_notifications')}
            className={`relative w-11 h-6 rounded-full transition-colors ${config.email_notifications ? 'bg-indigo-600' : 'bg-slate-600'}`}
            data-testid="toggle-email-notifications">
            <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform shadow ${config.email_notifications ? 'translate-x-5' : ''}`} />
          </button>
        </div>
        {config.email_notifications && (
          <div className="space-y-3 pt-2">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Recipient Email</label>
              <div className="flex gap-2">
                <input type="email" value={config.alert_email || ''}
                  onChange={(e) => onUpdate({ alert_email: e.target.value })}
                  className="flex-1 bg-slate-700/50 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  placeholder="your@email.com"
                  data-testid="alert-email-input" />
                <button onClick={onTestEmail} disabled={testingEmail || !config.alert_email}
                  className="px-4 py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
                  data-testid="send-test-email-btn">
                  {testingEmail ? 'Sending...' : 'Test Email'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Scan interval */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Scan Interval</h3>
        <div className="flex gap-2 flex-wrap">
          {[1, 6, 12, 24, 48, 168].map(h => (
            <button key={h}
              onClick={() => onUpdate({ interval_hours: h })}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${config.interval_hours === h ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-400 hover:text-white'}`}
              data-testid={`interval-${h}`}>
              {h < 24 ? `${h}h` : h === 24 ? '1d' : h === 48 ? '2d' : '1w'}
            </button>
          ))}
        </div>
      </div>

      {/* Alert severity filters */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Alert When Found</h3>
        <div className="space-y-3">
          {[
            { key: 'alert_on_critical', label: 'Critical', color: 'text-red-400' },
            { key: 'alert_on_high', label: 'High', color: 'text-orange-400' },
            { key: 'alert_on_moderate', label: 'Moderate', color: 'text-yellow-400' },
            { key: 'alert_on_low', label: 'Low', color: 'text-blue-400' },
          ].map(({ key, label, color }) => (
            <div key={key} className="flex items-center justify-between">
              <span className={`font-medium ${color}`}>{label} vulnerabilities</span>
              <button onClick={() => toggle(key)}
                className={`relative w-11 h-6 rounded-full transition-colors ${config[key] ? 'bg-indigo-600' : 'bg-slate-600'}`}
                data-testid={`toggle-${key}`}>
                <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform shadow ${config[key] ? 'translate-x-5' : ''}`} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Manual scan button */}
      <button onClick={onScanNow} disabled={scanning}
        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl text-sm font-semibold transition-colors flex items-center justify-center gap-2"
        data-testid="scan-now-btn">
        {scanning ? (
          <><svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg> Scanning...</>
        ) : 'Scan Now & Generate Alerts'}
      </button>
    </div>
  );
}

/* ─── History Table ────────────────────────────────────────── */

function HistoryRow({ record }) {
  const gc = GRADE_COLORS[record.grade] || 'text-gray-400';
  const sb = record.severity_breakdown || {};
  return (
    <tr className="border-b border-slate-700/50 hover:bg-slate-800/40 transition-colors" data-testid="audit-history-row">
      <td className="py-3 px-4 text-sm text-slate-300">{new Date(record.timestamp).toLocaleString()}</td>
      <td className="py-3 px-4"><span className={`font-bold text-lg ${gc}`}>{record.grade}</span></td>
      <td className="py-3 px-4 text-sm font-mono text-white">{record.security_score}</td>
      <td className="py-3 px-4 text-sm font-mono text-slate-300">{record.total_vulnerabilities}</td>
      <td className="py-3 px-4 text-sm">
        {sb.critical > 0 && <span className="text-red-400 mr-2">C:{sb.critical}</span>}
        {sb.high > 0 && <span className="text-orange-400 mr-2">H:{sb.high}</span>}
        {sb.moderate > 0 && <span className="text-yellow-400 mr-2">M:{sb.moderate}</span>}
        {sb.low > 0 && <span className="text-blue-400 mr-2">L:{sb.low}</span>}
        {record.total_vulnerabilities === 0 && <span className="text-emerald-400">Clean</span>}
      </td>
      <td className="py-3 px-4 text-sm text-slate-400">{record.is_scheduled ? 'Auto' : 'Manual'}</td>
    </tr>
  );
}

/* ─── Main Dashboard ───────────────────────────────────────── */

export default function SecurityAuditDashboard() {
  const [auditData, setAuditData] = useState(null);
  const [history, setHistory] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [alertCount, setAlertCount] = useState({ unread: 0, total: 0 });
  const [monitorConfig, setMonitorConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [sevFilter, setSevFilter] = useState('all');
  const pollRef = useRef(null);

  const apiFetch = useCallback(async (path, opts) => {
    try {
      const res = await fetch(`${API_URL}${path}`, opts);
      if (!res.ok) throw new Error(res.statusText);
      return await res.json();
    } catch (e) { console.error(`Fetch ${path} failed:`, e); return null; }
  }, []);

  const fetchAudit = useCallback(async (force = false) => {
    setLoading(true);
    const data = await apiFetch(`/api/security/audit?force=${force}`);
    if (data) setAuditData(data);
    setLoading(false);
  }, [apiFetch]);

  const fetchHistory = useCallback(async () => {
    const data = await apiFetch('/api/security/audit/history?limit=30');
    if (data) setHistory(data);
  }, [apiFetch]);

  const fetchTrend = useCallback(async () => {
    const data = await apiFetch('/api/security/audit/trend?days=90');
    if (data) setTrendData(data);
  }, [apiFetch]);

  const fetchAlerts = useCallback(async () => {
    const [list, count] = await Promise.all([
      apiFetch('/api/security/alerts?limit=50'),
      apiFetch('/api/security/alerts/count'),
    ]);
    if (list) setAlerts(list);
    if (count) setAlertCount(count);
  }, [apiFetch]);

  const fetchConfig = useCallback(async () => {
    const data = await apiFetch('/api/security/monitor/config');
    if (data) setMonitorConfig(data);
  }, [apiFetch]);

  useEffect(() => {
    fetchAudit(false);
    fetchHistory();
    fetchTrend();
    fetchAlerts();
    fetchConfig();
    // Poll alert count every 60s
    pollRef.current = setInterval(() => apiFetch('/api/security/alerts/count').then(c => c && setAlertCount(c)), 60000);
    return () => clearInterval(pollRef.current);
  }, [fetchAudit, fetchHistory, fetchTrend, fetchAlerts, fetchConfig, apiFetch]);

  const handleUpdateConfig = async (updates) => {
    const data = await apiFetch('/api/security/monitor/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (data) setMonitorConfig(data);
  };

  const handleScanNow = async () => {
    setScanning(true);
    const data = await apiFetch('/api/security/monitor/scan-now', { method: 'POST' });
    if (data?.scan) { setAuditData(data.scan); setMonitorConfig(data.config); }
    await Promise.all([fetchAlerts(), fetchHistory(), fetchTrend()]);
    setScanning(false);
  };

  const handleTestEmail = async () => {
    setTestingEmail(true);
    const data = await apiFetch('/api/security/email/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient: monitorConfig?.alert_email || '' }),
    });
    setTestingEmail(false);
    if (data?.sent) {
      alert('Test email sent successfully! Check your inbox.');
    } else {
      alert(`Failed to send test email: ${data?.error || 'Unknown error'}`);
    }
  };

  const handleDismissAlert = async (timestamp) => {
    await apiFetch('/api/security/alerts/dismiss', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_ids: [timestamp] }),
    });
    fetchAlerts();
  };

  const handleMarkAllRead = async () => {
    await apiFetch('/api/security/alerts/read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    fetchAlerts();
  };

  const handleDismissAll = async () => {
    await apiFetch('/api/security/alerts/dismiss', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    fetchAlerts();
  };

  const allVulns = auditData ? [
    ...(auditData.frontend?.vulnerabilities || []).map(v => ({ ...v, stack: 'Frontend' })),
    ...(auditData.backend?.vulnerabilities || []).map(v => ({ ...v, stack: 'Backend' })),
  ] : [];
  const filteredVulns = sevFilter === 'all' ? allVulns : allVulns.filter(v => v.severity === sevFilter);
  const sb = auditData?.severity_breakdown || {};

  const tabs = [
    { id: 'overview', label: 'Overview', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'vulnerabilities', label: `Vulns (${auditData?.total_vulnerabilities || 0})`, icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z' },
    { id: 'monitoring', label: 'Monitoring', icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z' },
    { id: 'alerts', label: 'Alerts', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9', badge: alertCount.unread },
    { id: 'history', label: 'History', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white" data-testid="security-audit-dashboard">
      {/* Header */}
      <div className="border-b border-slate-700/50 bg-slate-900/60 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">CVE Monitor</h1>
              <p className="text-slate-400 text-sm">Automated dependency vulnerability scanner</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {monitorConfig?.enabled && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-900/30 px-2.5 py-1 rounded-full" data-testid="monitor-active-badge">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Auto-scan ON
              </span>
            )}
            {auditData?.cached && <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded" data-testid="cache-indicator">Cached ({auditData.cache_age_seconds}s)</span>}
            <button onClick={() => fetchAudit(true)} disabled={loading}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
              data-testid="run-audit-btn">
              {loading ? (
                <><svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg> Scanning...</>
              ) : (
                <><svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg> Run Audit</>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-slate-800/50 p-1 rounded-lg w-fit overflow-x-auto" data-testid="audit-tabs">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap relative ${activeTab === t.id ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700/50'}`}
              data-testid={`tab-${t.id}`}>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={t.icon} /></svg>
              {t.label}
              {t.badge > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center" data-testid="alert-badge">{t.badge > 9 ? '9+' : t.badge}</span>
              )}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && !auditData && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <svg className="w-12 h-12 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
            <p className="text-slate-400">Running security audit...</p>
          </div>
        )}

        {/* ── Overview Tab ── */}
        {activeTab === 'overview' && auditData && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center" data-testid="score-card">
                <SecurityScoreRing score={auditData.security_score} grade={auditData.grade} />
                <p className="text-slate-400 text-sm mt-3">Security Score</p>
              </div>
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div data-testid="stat-deps"><p className="text-2xl font-bold text-white">{auditData.total_dependencies?.toLocaleString()}</p><p className="text-xs text-slate-400">Dependencies</p></div>
                  <div data-testid="stat-vulns"><p className={`text-2xl font-bold ${auditData.total_vulnerabilities === 0 ? 'text-emerald-400' : 'text-red-400'}`}>{auditData.total_vulnerabilities}</p><p className="text-xs text-slate-400">Vulnerabilities</p></div>
                  <div data-testid="stat-frontend"><p className="text-2xl font-bold text-cyan-400">{auditData.frontend?.vulnerabilities?.length || 0}</p><p className="text-xs text-slate-400">Frontend</p></div>
                  <div data-testid="stat-backend"><p className="text-2xl font-bold text-amber-400">{auditData.backend?.vulnerabilities?.length || 0}</p><p className="text-xs text-slate-400">Backend</p></div>
                </div>
              </div>
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">By Severity</h3>
                <div className="space-y-3">
                  {['critical', 'high', 'moderate', 'low'].map(s => (
                    <SeverityBar key={s} label={s} count={sb[s] || 0} total={auditData.total_vulnerabilities || 1} color={SEVERITY_COLORS[s]} />
                  ))}
                </div>
              </div>
            </div>

            {/* Status banner */}
            {auditData.total_vulnerabilities === 0 ? (
              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-5 flex items-center gap-4" data-testid="status-banner-clean">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                </div>
                <div><h3 className="text-emerald-300 font-semibold text-lg">All Clear</h3><p className="text-emerald-400/70 text-sm">No known vulnerabilities across {auditData.total_dependencies?.toLocaleString()} dependencies.</p></div>
              </div>
            ) : (
              <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-5 flex items-center gap-4" data-testid="status-banner-issues">
                <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                </div>
                <div><h3 className="text-amber-300 font-semibold text-lg">{auditData.total_vulnerabilities} Vulnerabilities Found</h3><p className="text-amber-400/70 text-sm">{sb.critical > 0 && `${sb.critical} critical, `}{sb.high > 0 && `${sb.high} high, `}{sb.moderate > 0 && `${sb.moderate} moderate, `}{sb.low > 0 && `${sb.low} low`}</p></div>
              </div>
            )}

            {/* Trend chart */}
            <TrendChart data={trendData} />

            <p className="text-xs text-slate-500 text-center" data-testid="audit-timestamp">
              Last scanned: {new Date(auditData.timestamp).toLocaleString()}
              {auditData.cached && ` (cached ${auditData.cache_age_seconds}s ago)`}
            </p>
          </div>
        )}

        {/* ── Vulnerabilities Tab ── */}
        {activeTab === 'vulnerabilities' && auditData && (
          <div className="space-y-4">
            <div className="flex gap-2 flex-wrap" data-testid="severity-filter">
              {['all', 'critical', 'high', 'moderate', 'low'].map(s => (
                <button key={s} onClick={() => setSevFilter(s)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all capitalize ${sevFilter === s ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                  data-testid={`filter-${s}`}>
                  {s} {s !== 'all' && `(${sb[s] || 0})`}
                </button>
              ))}
            </div>
            {filteredVulns.length === 0 ? (
              <div className="text-center py-16 text-slate-500" data-testid="no-vulns-message">
                <svg className="w-16 h-16 mx-auto mb-4 text-emerald-500/30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                <p className="text-lg font-medium text-slate-300">No vulnerabilities found</p>
                <p className="text-sm">All dependencies are secure.</p>
              </div>
            ) : (
              <div className="space-y-3">{filteredVulns.map((v, i) => <VulnCard key={`${v.module}-${v.title}-${i}`} vuln={v} stack={v.stack} />)}</div>
            )}
          </div>
        )}

        {/* ── Monitoring Tab ── */}
        {activeTab === 'monitoring' && (
          <MonitorPanel config={monitorConfig} onUpdate={handleUpdateConfig} onScanNow={handleScanNow} scanning={scanning} />
        )}

        {/* ── Alerts Tab ── */}
        {activeTab === 'alerts' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                Alerts
                {alertCount.unread > 0 && <span className="px-2 py-0.5 text-xs bg-red-500 text-white rounded-full">{alertCount.unread} unread</span>}
              </h3>
              <div className="flex gap-2">
                <button onClick={handleMarkAllRead} className="text-sm text-indigo-400 hover:text-indigo-300 px-3 py-1 rounded-lg hover:bg-slate-800 transition-colors" data-testid="mark-all-read-btn">Mark all read</button>
                <button onClick={handleDismissAll} className="text-sm text-red-400 hover:text-red-300 px-3 py-1 rounded-lg hover:bg-slate-800 transition-colors" data-testid="dismiss-all-btn">Dismiss all</button>
              </div>
            </div>
            {alerts.length === 0 ? (
              <div className="text-center py-16 text-slate-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
                <p className="text-lg font-medium text-slate-300">No alerts</p>
                <p className="text-sm">Enable monitoring and run a scan to generate alerts.</p>
              </div>
            ) : (
              <div className="space-y-3">{alerts.map((a, i) => <AlertCard key={`${a.timestamp}-${i}`} alert={a} onDismiss={handleDismissAlert} />)}</div>
            )}
          </div>
        )}

        {/* ── History Tab ── */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Audit History</h3>
              <button onClick={fetchHistory} className="text-sm text-indigo-400 hover:text-indigo-300" data-testid="refresh-history-btn">Refresh</button>
            </div>
            {history.length === 0 ? (
              <p className="text-slate-500 text-center py-12">No audit history yet.</p>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-slate-700/50">
                <table className="w-full" data-testid="history-table">
                  <thead className="bg-slate-800/80">
                    <tr className="text-left text-sm text-slate-400">
                      <th className="py-3 px-4 font-medium">Timestamp</th>
                      <th className="py-3 px-4 font-medium">Grade</th>
                      <th className="py-3 px-4 font-medium">Score</th>
                      <th className="py-3 px-4 font-medium">Vulns</th>
                      <th className="py-3 px-4 font-medium">Breakdown</th>
                      <th className="py-3 px-4 font-medium">Type</th>
                    </tr>
                  </thead>
                  <tbody>{history.map((r, i) => <HistoryRow key={i} record={r} />)}</tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
