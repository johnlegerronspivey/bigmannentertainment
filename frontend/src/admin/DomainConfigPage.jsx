import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Globe, Shield, Mail, Server, CheckCircle, XCircle, Copy, RefreshCw, Zap, Trash2, Plus, Database } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function StatusBadge({ status }) {
  const map = {
    healthy: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', label: 'Verified' },
    Success: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', label: 'Verified' },
    configured: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', label: 'Active' },
    connected: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', label: 'Connected' },
    Pending: { bg: 'bg-amber-500/10', text: 'text-amber-400', label: 'Pending' },
    Failed: { bg: 'bg-red-500/10', text: 'text-red-400', label: 'Failed' },
    NotStarted: { bg: 'bg-slate-500/10', text: 'text-slate-400', label: 'Not Started' },
    not_configured: { bg: 'bg-slate-500/10', text: 'text-slate-400', label: 'Not Configured' },
    unavailable: { bg: 'bg-slate-500/10', text: 'text-slate-400', label: 'Unavailable' },
    error: { bg: 'bg-red-500/10', text: 'text-red-400', label: 'Error' },
  };
  const s = map[status] || map.NotStarted;
  return (
    <span data-testid={`status-badge-${status}`} className={`px-2.5 py-1 rounded-full text-xs font-medium ${s.bg} ${s.text}`}>
      {s.label}
    </span>
  );
}

function CopyButton({ value }) {
  const [copied, setCopied] = useState(false);
  const handle = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button data-testid="copy-dns-value" onClick={handle} className="p-1 rounded hover:bg-slate-700 transition-colors" title="Copy">
      {copied ? <CheckCircle size={14} className="text-emerald-400" /> : <Copy size={14} className="text-slate-400" />}
    </button>
  );
}

export default function DomainConfigPage() {
  const [domainStatus, setDomainStatus] = useState(null);
  const [dnsGuide, setDnsGuide] = useState(null);
  const [r53Records, setR53Records] = useState([]);
  const [r53Zone, setR53Zone] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoConfiguring, setAutoConfiguring] = useState(false);
  const [autoConfigResult, setAutoConfigResult] = useState(null);
  const [showAddRecord, setShowAddRecord] = useState(false);
  const [newRecord, setNewRecord] = useState({ name: '', type: 'A', values: '', ttl: 300 });
  const [addingRecord, setAddingRecord] = useState(false);
  const [deletingRecord, setDeletingRecord] = useState(null);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, guideRes, recordsRes, zoneRes] = await Promise.all([
        fetch(`${API}/api/domain/status`),
        fetch(`${API}/api/domain/dns-guide`),
        fetch(`${API}/api/route53/records`),
        fetch(`${API}/api/route53/zone`),
      ]);
      if (statusRes.ok) setDomainStatus(await statusRes.json());
      if (guideRes.ok) setDnsGuide(await guideRes.json());
      if (recordsRes.ok) { const d = await recordsRes.json(); setR53Records(d.records || []); }
      if (zoneRes.ok) setR53Zone(await zoneRes.json());
    } catch (e) {
      console.error('Fetch failed', e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleAutoConfig = async () => {
    setAutoConfiguring(true);
    setAutoConfigResult(null);
    try {
      const res = await fetch(`${API}/api/route53/auto-configure`, { method: 'POST', headers });
      const data = await res.json();
      setAutoConfigResult(data);
      if (res.ok) fetchAll();
    } catch (e) {
      setAutoConfigResult({ status: 'error', message: e.message });
    }
    setAutoConfiguring(false);
  };

  const handleAddRecord = async () => {
    setAddingRecord(true);
    try {
      const values = newRecord.values.split(',').map(v => v.trim()).filter(Boolean);
      const res = await fetch(`${API}/api/route53/record`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ name: newRecord.name, type: newRecord.type, values, ttl: Number(newRecord.ttl) }),
      });
      if (res.ok) {
        setShowAddRecord(false);
        setNewRecord({ name: '', type: 'A', values: '', ttl: 300 });
        fetchAll();
      }
    } catch (e) {
      console.error(e);
    }
    setAddingRecord(false);
  };

  const handleDeleteRecord = async (record) => {
    if (!window.confirm(`Delete ${record.type} record for ${record.name}?`)) return;
    setDeletingRecord(record.name + record.type);
    try {
      await fetch(`${API}/api/route53/record`, {
        method: 'DELETE',
        headers,
        body: JSON.stringify({ name: record.name, type: record.type, values: record.values, ttl: record.ttl }),
      });
      fetchAll();
    } catch (e) {
      console.error(e);
    }
    setDeletingRecord(null);
  };

  if (loading) {
    return (
      <div data-testid="domain-config-loading" className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="animate-spin text-violet-400" size={32} />
      </div>
    );
  }

  const protectedTypes = ['NS', 'SOA'];

  return (
    <div data-testid="domain-config-page" className="space-y-6 max-w-5xl mx-auto p-4 sm:p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Domain Configuration</h1>
          <p className="text-sm text-slate-400 mt-1">bigmannentertainment.com</p>
        </div>
        <button data-testid="refresh-domain-status" onClick={fetchAll}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition-colors">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Service Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-slate-300">
              <Globe size={16} className="text-orange-400" /> Route53
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StatusBadge status={domainStatus?.route53?.status} />
            <p className="text-xs text-slate-500 mt-2">Zone: {r53Zone?.id || 'N/A'}</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-slate-300">
              <Mail size={16} className="text-violet-400" /> SES Email
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StatusBadge status={domainStatus?.ses?.status} />
            <p className="text-xs text-slate-500 mt-2">no-reply@bigmannentertainment.com</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-slate-300">
              <Server size={16} className="text-blue-400" /> CloudFront CDN
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StatusBadge status={domainStatus?.cloudfront?.status} />
            <p className="text-xs text-slate-500 mt-2">{domainStatus?.cloudfront?.domain || 'cdn.bigmannentertainment.com'}</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-slate-300">
              <Shield size={16} className="text-emerald-400" /> Security
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StatusBadge status="configured" />
            <p className="text-xs text-slate-500 mt-2">HSTS, CSP, XSS Protection</p>
          </CardContent>
        </Card>
      </div>

      {/* Route53 Auto-Configure */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Zap size={18} className="text-amber-400" /> Auto-Configure DNS Records
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400">
            Automatically create all required DNS records in Route53 — SPF, DMARC, DKIM, SES verification, MTA-STS, TLS reporting, WorkMail autodiscover, WWW/API/mail subdomains, MX, and CAA.
          </p>
          <button data-testid="auto-configure-dns" onClick={handleAutoConfig} disabled={autoConfiguring}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white text-sm font-medium transition-colors">
            {autoConfiguring ? <><RefreshCw size={14} className="animate-spin" /> Configuring...</> : <><Zap size={14} /> Auto-Configure All Records</>}
          </button>

          {autoConfigResult && autoConfigResult.results && (
            <div data-testid="auto-config-result" className="mt-4 space-y-2">
              <div className={`flex items-center gap-2 text-sm ${autoConfigResult.failed === 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                <CheckCircle size={16} /> {autoConfigResult.message}
              </div>
              <div className="space-y-1">
                {autoConfigResult.results.map((r, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    {r.status === 'ok'
                      ? <CheckCircle size={12} className="text-emerald-400 shrink-0" />
                      : <XCircle size={12} className="text-red-400 shrink-0" />}
                    <span className="text-slate-300">{r.record}</span>
                    {r.error && <span className="text-red-400 truncate">— {r.error}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Live Route53 Records */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Database size={18} className="text-orange-400" /> Route53 DNS Records
            <span className="text-xs font-normal text-slate-500 ml-2">{r53Records.length} records</span>
          </CardTitle>
          <button data-testid="add-record-btn" onClick={() => setShowAddRecord(!showAddRecord)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-xs font-medium transition-colors">
            <Plus size={12} /> Add Record
          </button>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Add Record Form */}
          {showAddRecord && (
            <div data-testid="add-record-form" className="p-4 rounded-lg bg-slate-800/70 border border-slate-700 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Name</label>
                  <input data-testid="record-name-input" value={newRecord.name} onChange={e => setNewRecord(p => ({ ...p, name: e.target.value }))}
                    placeholder="e.g. www.bigmannentertainment.com"
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500" />
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Type</label>
                  <select data-testid="record-type-select" value={newRecord.type} onChange={e => setNewRecord(p => ({ ...p, type: e.target.value }))}
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-violet-500">
                    {['A', 'AAAA', 'CNAME', 'TXT', 'MX', 'CAA', 'SRV', 'NAPTR', 'NS', 'PTR'].map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Values (comma-separated)</label>
                  <input data-testid="record-values-input" value={newRecord.values} onChange={e => setNewRecord(p => ({ ...p, values: e.target.value }))}
                    placeholder="e.g. 1.2.3.4"
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500" />
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">TTL</label>
                  <input data-testid="record-ttl-input" type="number" value={newRecord.ttl} onChange={e => setNewRecord(p => ({ ...p, ttl: e.target.value }))}
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-violet-500" />
                </div>
              </div>
              <div className="flex gap-2">
                <button data-testid="submit-record-btn" onClick={handleAddRecord} disabled={addingRecord}
                  className="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-xs font-medium transition-colors">
                  {addingRecord ? 'Adding...' : 'Add Record'}
                </button>
                <button onClick={() => setShowAddRecord(false)}
                  className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs transition-colors">
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Records Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800">
                  <th className="text-left py-2 px-2 w-16">Type</th>
                  <th className="text-left py-2 px-2">Name</th>
                  <th className="text-left py-2 px-2">Value</th>
                  <th className="text-left py-2 px-2 w-16">TTL</th>
                  <th className="py-2 px-2 w-16"></th>
                </tr>
              </thead>
              <tbody>
                {r53Records.map((r, i) => (
                  <tr key={i} className="border-b border-slate-800/50 text-slate-300 hover:bg-slate-800/30">
                    <td className="py-2 px-2 font-mono text-violet-400">{r.type}</td>
                    <td className="py-2 px-2 font-mono break-all max-w-[250px]">{r.name}</td>
                    <td className="py-2 px-2 font-mono break-all max-w-[350px]">
                      {r.values?.map((v, vi) => <div key={vi} className="truncate">{v}</div>)}
                    </td>
                    <td className="py-2 px-2 text-slate-500">{r.ttl}</td>
                    <td className="py-2 px-2">
                      <div className="flex items-center gap-1">
                        <CopyButton value={r.values?.join(', ') || ''} />
                        {!protectedTypes.includes(r.type) && (
                          <button data-testid={`delete-record-${i}`}
                            onClick={() => handleDeleteRecord(r)}
                            disabled={deletingRecord === r.name + r.type}
                            className="p-1 rounded hover:bg-red-900/30 transition-colors disabled:opacity-50"
                            title="Delete record">
                            <Trash2 size={14} className="text-red-400" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Name Servers */}
          {r53Zone?.name_servers && (
            <div className="mt-4 p-3 rounded-lg bg-slate-800/50">
              <h4 className="text-xs font-medium text-slate-400 mb-2">Name Servers</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                {r53Zone.name_servers.map((ns, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <span className="font-mono text-slate-300">{ns}</span>
                    <CopyButton value={ns} />
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Required DNS Guide */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Globe size={18} className="text-blue-400" /> DNS Configuration Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-400 mb-4">
            Reference of all recommended records. Use <strong className="text-amber-400">Auto-Configure</strong> above to create them automatically in Route53.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800">
                  <th className="text-left py-2 px-2">Priority</th>
                  <th className="text-left py-2 px-2">Type</th>
                  <th className="text-left py-2 px-2">Name</th>
                  <th className="text-left py-2 px-2">Value</th>
                  <th className="text-left py-2 px-2">Purpose</th>
                </tr>
              </thead>
              <tbody>
                {dnsGuide?.required_records?.map((r, i) => (
                  <tr key={i} className="border-b border-slate-800/50 text-slate-300">
                    <td className="py-2 px-2">
                      {r.priority === 'required' ? <span className="text-red-400 font-medium">Required</span>
                        : r.priority === 'recommended' ? <span className="text-amber-400 font-medium">Recommended</span>
                        : <span className="text-slate-500">Optional</span>}
                    </td>
                    <td className="py-2 px-2 font-mono text-violet-400">{r.type}</td>
                    <td className="py-2 px-2 font-mono break-all max-w-[180px]">{r.name}</td>
                    <td className="py-2 px-2 font-mono break-all max-w-[280px]">{r.value}</td>
                    <td className="py-2 px-2 text-slate-500">{r.purpose}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Security Headers */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Shield size={18} className="text-emerald-400" /> Security Headers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {[
              { header: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains; preload' },
              { header: 'X-Content-Type-Options', value: 'nosniff' },
              { header: 'X-Frame-Options', value: 'DENY' },
              { header: 'X-XSS-Protection', value: '1; mode=block' },
              { header: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
              { header: 'Permissions-Policy', value: 'camera=(), microphone=(self)' },
            ].map((h, i) => (
              <div key={i} className="flex items-start gap-2 p-3 rounded-lg bg-slate-800/50">
                <CheckCircle size={14} className="text-emerald-400 mt-0.5 shrink-0" />
                <div>
                  <p className="font-mono text-slate-300">{h.header}</p>
                  <p className="text-slate-500 mt-0.5">{h.value}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
