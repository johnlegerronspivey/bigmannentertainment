import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Globe, Shield, Mail, Server, CheckCircle, XCircle, Clock, Copy, ExternalLink, RefreshCw } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function StatusBadge({ status }) {
  const map = {
    healthy: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', label: 'Verified' },
    Success: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', label: 'Verified' },
    configured: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', label: 'Active' },
    Pending: { bg: 'bg-amber-500/10', text: 'text-amber-400', label: 'Pending' },
    NotStarted: { bg: 'bg-slate-500/10', text: 'text-slate-400', label: 'Not Started' },
    not_configured: { bg: 'bg-slate-500/10', text: 'text-slate-400', label: 'Not Configured' },
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
    <button data-testid="copy-dns-value" onClick={handle} className="p-1 rounded hover:bg-slate-700 transition-colors">
      {copied ? <CheckCircle size={14} className="text-emerald-400" /> : <Copy size={14} className="text-slate-400" />}
    </button>
  );
}

export default function DomainConfigPage() {
  const [domainStatus, setDomainStatus] = useState(null);
  const [dnsGuide, setDnsGuide] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState(null);

  const token = localStorage.getItem('token');

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, guideRes] = await Promise.all([
        fetch(`${API}/api/aws/domain/status`),
        fetch(`${API}/api/aws/domain/dns-guide`),
      ]);
      if (statusRes.ok) setDomainStatus(await statusRes.json());
      if (guideRes.ok) setDnsGuide(await guideRes.json());
    } catch (e) {
      console.error('Failed to fetch domain status', e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  const initVerification = async () => {
    setVerifying(true);
    setVerifyResult(null);
    try {
      const res = await fetch(`${API}/api/aws/domain/ses/verify`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      const data = await res.json();
      if (res.ok) {
        setVerifyResult(data);
      } else {
        setVerifyResult({ error: data.detail || 'Verification failed' });
      }
    } catch (e) {
      setVerifyResult({ error: e.message });
    }
    setVerifying(false);
  };

  if (loading) {
    return (
      <div data-testid="domain-config-loading" className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="animate-spin text-violet-400" size={32} />
      </div>
    );
  }

  return (
    <div data-testid="domain-config-page" className="space-y-6 max-w-5xl mx-auto p-4 sm:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Domain Configuration</h1>
          <p className="text-sm text-slate-400 mt-1">bigmannentertainment.com</p>
        </div>
        <button
          data-testid="refresh-domain-status"
          onClick={fetchStatus}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition-colors"
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Service Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              <Shield size={16} className="text-emerald-400" /> Security Headers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StatusBadge status="configured" />
            <p className="text-xs text-slate-500 mt-2">HSTS, CSP, XSS Protection active</p>
          </CardContent>
        </Card>
      </div>

      {/* SES Verification Section */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Mail size={18} className="text-violet-400" /> Email Domain Verification
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400">
            Verify <strong className="text-white">bigmannentertainment.com</strong> with Amazon SES to send emails from your domain.
          </p>
          <button
            data-testid="start-ses-verification"
            onClick={initVerification}
            disabled={verifying}
            className="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 text-white text-sm font-medium transition-colors"
          >
            {verifying ? 'Verifying...' : 'Start Domain Verification'}
          </button>

          {verifyResult && !verifyResult.error && (
            <div data-testid="verification-result" className="mt-4 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 text-sm">
                <CheckCircle size={16} /> Verification initiated
              </div>
              <p className="text-xs text-slate-400">Add these DNS records to your domain registrar:</p>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-500 border-b border-slate-800">
                      <th className="text-left py-2 px-2">Type</th>
                      <th className="text-left py-2 px-2">Name</th>
                      <th className="text-left py-2 px-2">Value</th>
                      <th className="text-left py-2 px-2">Purpose</th>
                      <th className="py-2 px-2"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {verifyResult.dns_records_to_add?.map((r, i) => (
                      <tr key={i} className="border-b border-slate-800/50 text-slate-300">
                        <td className="py-2 px-2 font-mono text-violet-400">{r.type}</td>
                        <td className="py-2 px-2 font-mono break-all max-w-[200px]">{r.name}</td>
                        <td className="py-2 px-2 font-mono break-all max-w-[300px]">{r.value}</td>
                        <td className="py-2 px-2 text-slate-500">{r.purpose}</td>
                        <td className="py-2 px-2"><CopyButton value={r.value} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {verifyResult?.error && (
            <div data-testid="verification-error" className="flex items-center gap-2 text-red-400 text-sm mt-2">
              <XCircle size={16} /> {verifyResult.error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* DNS Records Guide */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Globe size={18} className="text-blue-400" /> Required DNS Records
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-400 mb-4">
            Configure these DNS records at your domain registrar to connect all services.
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
                  <th className="py-2 px-2"></th>
                </tr>
              </thead>
              <tbody>
                {dnsGuide?.required_records?.map((r, i) => (
                  <tr key={i} className="border-b border-slate-800/50 text-slate-300">
                    <td className="py-2 px-2">
                      {r.priority === 'required' ? (
                        <span className="text-red-400 font-medium">Required</span>
                      ) : r.priority === 'recommended' ? (
                        <span className="text-amber-400 font-medium">Recommended</span>
                      ) : (
                        <span className="text-slate-500">Optional</span>
                      )}
                    </td>
                    <td className="py-2 px-2 font-mono text-violet-400">{r.type}</td>
                    <td className="py-2 px-2 font-mono break-all max-w-[180px]">{r.name}</td>
                    <td className="py-2 px-2 font-mono break-all max-w-[280px]">{r.value}</td>
                    <td className="py-2 px-2 text-slate-500">{r.purpose}</td>
                    <td className="py-2 px-2"><CopyButton value={r.value} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {dnsGuide?.instructions && (
            <div className="mt-6 space-y-2">
              <h3 className="text-sm font-medium text-white">Setup Steps</h3>
              <ol className="list-decimal list-inside space-y-1 text-xs text-slate-400">
                {Object.values(dnsGuide.instructions).map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Security Headers Status */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Shield size={18} className="text-emerald-400" /> Security Headers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {[
              { header: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains; preload', active: true },
              { header: 'X-Content-Type-Options', value: 'nosniff', active: true },
              { header: 'X-Frame-Options', value: 'DENY', active: true },
              { header: 'X-XSS-Protection', value: '1; mode=block', active: true },
              { header: 'Referrer-Policy', value: 'strict-origin-when-cross-origin', active: true },
              { header: 'Permissions-Policy', value: 'camera=(), microphone=(self)', active: true },
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
