import React, { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SEVERITY_COLORS = {
  critical: { bg: 'bg-red-900/30', border: 'border-red-500', text: 'text-red-400', badge: 'bg-red-500/20 text-red-300' },
  high: { bg: 'bg-orange-900/30', border: 'border-orange-500', text: 'text-orange-400', badge: 'bg-orange-500/20 text-orange-300' },
  moderate: { bg: 'bg-yellow-900/30', border: 'border-yellow-500', text: 'text-yellow-400', badge: 'bg-yellow-500/20 text-yellow-300' },
  low: { bg: 'bg-blue-900/30', border: 'border-blue-500', text: 'text-blue-400', badge: 'bg-blue-500/20 text-blue-300' },
};

const GRADE_COLORS = {
  A: 'text-emerald-400', B: 'text-green-400', C: 'text-yellow-400', D: 'text-orange-400', F: 'text-red-400',
};

function SecurityScoreRing({ score, grade }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const strokeColor = score >= 90 ? '#34d399' : score >= 75 ? '#4ade80' : score >= 60 ? '#facc15' : score >= 40 ? '#fb923c' : '#f87171';

  return (
    <div className="flex flex-col items-center" data-testid="security-score-ring">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#1e293b" strokeWidth="10" />
        <circle
          cx="70" cy="70" r={radius} fill="none"
          stroke={strokeColor} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1s ease', transform: 'rotate(-90deg)', transformOrigin: '70px 70px' }}
        />
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
        <div className={`h-full rounded-full transition-all duration-700`} style={{ width: `${pct}%`, backgroundColor: color.text.includes('red') ? '#f87171' : color.text.includes('orange') ? '#fb923c' : color.text.includes('yellow') ? '#facc15' : '#60a5fa' }} />
      </div>
      <span className="w-8 text-right text-slate-300 font-mono">{count}</span>
    </div>
  );
}

function VulnCard({ vuln, stack }) {
  const [expanded, setExpanded] = useState(false);
  const colors = SEVERITY_COLORS[vuln.severity] || SEVERITY_COLORS.low;

  return (
    <div className={`border rounded-lg p-4 ${colors.bg} ${colors.border} border-opacity-30 transition-all duration-200`} data-testid={`vuln-card-${vuln.module}`}>
      <div className="flex items-start justify-between cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${colors.badge}`}>{vuln.severity}</span>
            <span className="text-white font-semibold truncate">{vuln.module}</span>
            <span className="px-2 py-0.5 rounded bg-slate-700 text-slate-300 text-xs">{stack}</span>
          </div>
          <p className="text-slate-300 text-sm mt-1 truncate">{vuln.title || vuln.description}</p>
        </div>
        <svg className={`w-5 h-5 text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </div>
      {expanded && (
        <div className="mt-3 pt-3 border-t border-slate-600/50 space-y-2 text-sm">
          {vuln.vulnerable_versions && <div><span className="text-slate-400">Vulnerable:</span> <span className="text-red-300 font-mono">{vuln.vulnerable_versions}</span></div>}
          {vuln.patched_versions && <div><span className="text-slate-400">Patched:</span> <span className="text-green-300 font-mono">{vuln.patched_versions}</span></div>}
          {vuln.installed_version && <div><span className="text-slate-400">Installed:</span> <span className="text-slate-300 font-mono">{vuln.installed_version}</span></div>}
          {vuln.fix_versions?.length > 0 && <div><span className="text-slate-400">Fix versions:</span> <span className="text-green-300 font-mono">{vuln.fix_versions.join(', ')}</span></div>}
          {vuln.recommendation && <div><span className="text-slate-400">Recommendation:</span> <span className="text-slate-200">{vuln.recommendation}</span></div>}
          {vuln.url && <a href={vuln.url} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300 underline inline-block">View Advisory</a>}
        </div>
      )}
    </div>
  );
}

function HistoryRow({ record }) {
  const gradeColor = GRADE_COLORS[record.grade] || 'text-gray-400';
  const sb = record.severity_breakdown || {};
  return (
    <tr className="border-b border-slate-700/50 hover:bg-slate-800/40 transition-colors" data-testid="audit-history-row">
      <td className="py-3 px-4 text-sm text-slate-300">{new Date(record.timestamp).toLocaleString()}</td>
      <td className="py-3 px-4"><span className={`font-bold text-lg ${gradeColor}`}>{record.grade}</span></td>
      <td className="py-3 px-4 text-sm font-mono text-white">{record.security_score}</td>
      <td className="py-3 px-4 text-sm font-mono text-slate-300">{record.total_vulnerabilities}</td>
      <td className="py-3 px-4 text-sm">
        {sb.critical > 0 && <span className="text-red-400 mr-2">C:{sb.critical}</span>}
        {sb.high > 0 && <span className="text-orange-400 mr-2">H:{sb.high}</span>}
        {sb.moderate > 0 && <span className="text-yellow-400 mr-2">M:{sb.moderate}</span>}
        {sb.low > 0 && <span className="text-blue-400 mr-2">L:{sb.low}</span>}
        {record.total_vulnerabilities === 0 && <span className="text-emerald-400">Clean</span>}
      </td>
      <td className="py-3 px-4 text-sm text-slate-400">{record.total_dependencies || '-'}</td>
    </tr>
  );
}

export default function SecurityAuditDashboard() {
  const [auditData, setAuditData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [sevFilter, setSevFilter] = useState('all');

  const fetchAudit = useCallback(async (force = false) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/security/audit?force=${force}`);
      const data = await res.json();
      setAuditData(data);
    } catch (e) {
      console.error('Audit fetch failed:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/security/audit/history?limit=20`);
      const data = await res.json();
      setHistory(data);
    } catch (e) {
      console.error('History fetch failed:', e);
    }
  }, []);

  useEffect(() => {
    fetchAudit(false);
    fetchHistory();
  }, [fetchAudit, fetchHistory]);

  const allVulns = auditData ? [
    ...(auditData.frontend?.vulnerabilities || []).map(v => ({ ...v, stack: 'Frontend' })),
    ...(auditData.backend?.vulnerabilities || []).map(v => ({ ...v, stack: 'Backend' })),
  ] : [];

  const filteredVulns = sevFilter === 'all' ? allVulns : allVulns.filter(v => v.severity === sevFilter);
  const sb = auditData?.severity_breakdown || {};

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'vulnerabilities', label: `Vulnerabilities (${auditData?.total_vulnerabilities || 0})` },
    { id: 'history', label: 'History' },
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
              <h1 className="text-xl font-bold tracking-tight">Security Audit Monitor</h1>
              <p className="text-slate-400 text-sm">Dependency vulnerability scanner</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {auditData?.cached && <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded" data-testid="cache-indicator">Cached ({auditData.cache_age_seconds}s ago)</span>}
            <button
              onClick={() => { fetchAudit(true); }}
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
              data-testid="run-audit-btn"
            >
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
        <div className="flex gap-1 mb-6 bg-slate-800/50 p-1 rounded-lg w-fit" data-testid="audit-tabs">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === t.id ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700/50'}`}
              data-testid={`tab-${t.id}`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Loading state */}
        {loading && !auditData && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <svg className="w-12 h-12 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
            <p className="text-slate-400">Running security audit... This may take a minute.</p>
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && auditData && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Score Card */}
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 flex flex-col items-center" data-testid="score-card">
                <SecurityScoreRing score={auditData.security_score} grade={auditData.grade} />
                <p className="text-slate-400 text-sm mt-3">Security Score</p>
              </div>

              {/* Stats */}
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div data-testid="stat-deps">
                    <p className="text-2xl font-bold text-white">{auditData.total_dependencies?.toLocaleString()}</p>
                    <p className="text-xs text-slate-400">Dependencies</p>
                  </div>
                  <div data-testid="stat-vulns">
                    <p className={`text-2xl font-bold ${auditData.total_vulnerabilities === 0 ? 'text-emerald-400' : 'text-red-400'}`}>{auditData.total_vulnerabilities}</p>
                    <p className="text-xs text-slate-400">Vulnerabilities</p>
                  </div>
                  <div data-testid="stat-frontend">
                    <p className="text-2xl font-bold text-cyan-400">{auditData.frontend?.vulnerabilities?.length || 0}</p>
                    <p className="text-xs text-slate-400">Frontend Issues</p>
                  </div>
                  <div data-testid="stat-backend">
                    <p className="text-2xl font-bold text-amber-400">{auditData.backend?.vulnerabilities?.length || 0}</p>
                    <p className="text-xs text-slate-400">Backend Issues</p>
                  </div>
                </div>
              </div>

              {/* Severity Breakdown */}
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">By Severity</h3>
                <div className="space-y-3">
                  <SeverityBar label="critical" count={sb.critical || 0} total={auditData.total_vulnerabilities || 1} color={SEVERITY_COLORS.critical} />
                  <SeverityBar label="high" count={sb.high || 0} total={auditData.total_vulnerabilities || 1} color={SEVERITY_COLORS.high} />
                  <SeverityBar label="moderate" count={sb.moderate || 0} total={auditData.total_vulnerabilities || 1} color={SEVERITY_COLORS.moderate} />
                  <SeverityBar label="low" count={sb.low || 0} total={auditData.total_vulnerabilities || 1} color={SEVERITY_COLORS.low} />
                </div>
              </div>
            </div>

            {/* Status Banner */}
            {auditData.total_vulnerabilities === 0 ? (
              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-5 flex items-center gap-4" data-testid="status-banner-clean">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                </div>
                <div>
                  <h3 className="text-emerald-300 font-semibold text-lg">All Clear</h3>
                  <p className="text-emerald-400/70 text-sm">No known vulnerabilities found across {auditData.total_dependencies?.toLocaleString()} dependencies.</p>
                </div>
              </div>
            ) : (
              <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-5 flex items-center gap-4" data-testid="status-banner-issues">
                <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
                </div>
                <div>
                  <h3 className="text-amber-300 font-semibold text-lg">{auditData.total_vulnerabilities} Vulnerabilities Found</h3>
                  <p className="text-amber-400/70 text-sm">
                    {sb.critical > 0 && `${sb.critical} critical, `}{sb.high > 0 && `${sb.high} high, `}{sb.moderate > 0 && `${sb.moderate} moderate, `}{sb.low > 0 && `${sb.low} low`}
                  </p>
                </div>
              </div>
            )}

            {/* Timestamp */}
            <p className="text-xs text-slate-500 text-center" data-testid="audit-timestamp">
              Last scanned: {new Date(auditData.timestamp).toLocaleString()}
              {auditData.cached && ` (cached ${auditData.cache_age_seconds}s ago)`}
            </p>
          </div>
        )}

        {/* Vulnerabilities Tab */}
        {activeTab === 'vulnerabilities' && auditData && (
          <div className="space-y-4">
            {/* Severity Filter */}
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
                <p className="text-sm">All dependencies are up to date and secure.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredVulns.map((v, i) => <VulnCard key={`${v.module}-${v.title}-${i}`} vuln={v} stack={v.stack} />)}
              </div>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Audit History</h3>
              <button onClick={fetchHistory} className="text-sm text-indigo-400 hover:text-indigo-300" data-testid="refresh-history-btn">Refresh</button>
            </div>
            {history.length === 0 ? (
              <p className="text-slate-500 text-center py-12">No audit history yet. Run your first audit above.</p>
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
                      <th className="py-3 px-4 font-medium">Deps</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((r, i) => <HistoryRow key={i} record={r} />)}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
