import React, { useState, useEffect, useCallback } from 'react';
import { Shield, CheckCircle, AlertTriangle, Lock, Building2, Hash, FileText, Loader2, RefreshCw, ChevronRight } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return { 'Content-Type': 'application/json', ...(token ? { 'Authorization': `Bearer ${token}` } : {}) };
};

const IDENTIFIER_META = {
  gs1_company_prefix: { label: 'GS1 Company Prefix', placeholder: 'e.g. 08600043402', hint: '7-11 digit numeric prefix assigned by GS1', icon: Hash },
  gln: { label: 'Global Location Number (GLN)', placeholder: 'e.g. 0860004340201', hint: '13-digit identifier with Modulo-10 check digit', icon: Building2 },
  ein: { label: 'EIN (Employer Identification Number)', placeholder: 'e.g. 27-0658077', hint: '9-digit US federal tax ID (XX-XXXXXXX)', icon: FileText },
  duns: { label: 'DUNS Number', placeholder: 'e.g. 123456789', hint: '9-digit Dun & Bradstreet identifier', icon: Hash },
  business_registration_number: { label: 'Business Registration Number', placeholder: 'e.g. BME-2024-001', hint: 'State/federal business filing ID', icon: FileText },
  business_entity: { label: 'Business Entity Name', placeholder: 'e.g. Big Mann Entertainment', hint: 'Legal business name', icon: Building2 },
  business_owner: { label: 'Business Owner', placeholder: 'e.g. John LeGerron Spivey', hint: 'Registered business owner', icon: Shield },
  business_type: { label: 'Business Type', placeholder: 'e.g. Sole Proprietorship', hint: 'LLC, Corporation, Sole Proprietorship, etc.', icon: FileText },
};

const BUSINESS_TYPES = ['Sole Proprietorship', 'LLC', 'Corporation', 'S-Corporation', 'Partnership', 'Non-Profit'];

const StatusBadge = ({ compliant }) => (
  <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${compliant ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-500/15 text-amber-400'}`} data-testid="compliance-badge">
    {compliant ? <CheckCircle size={13} /> : <AlertTriangle size={13} />}
    {compliant ? 'Fully Compliant' : 'Incomplete'}
  </span>
);

export default function BusinessIdentifiersPage() {
  const [labels, setLabels] = useState([]);
  const [selectedLabel, setSelectedLabel] = useState(null);
  const [identifiers, setIdentifiers] = useState(null);
  const [protectedData, setProtectedData] = useState(null);
  const [compliance, setCompliance] = useState(null);
  const [form, setForm] = useState({});
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isProtected, setIsProtected] = useState(false);
  const [validating, setValidating] = useState({});

  // Fetch user's labels
  useEffect(() => {
    const loadLabels = async () => {
      try {
        const res = await fetch(`${API}/api/uln/me/labels`, { headers: getAuthHeaders() });
        if (res.ok) {
          const data = await res.json();
          const list = data.labels || [];
          setLabels(list);
          if (list.length > 0) setSelectedLabel(list[0]);
        }
      } catch (e) { console.error(e); }
      setLoading(false);
    };
    loadLabels();
    // Also fetch protected identifiers
    fetch(`${API}/api/gs1-identifiers/protected-owner`, { headers: getAuthHeaders() })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setProtectedData(d); })
      .catch(() => {});
  }, []);

  // Load identifiers when label changes
  const loadIdentifiers = useCallback(async (labelId) => {
    if (!labelId) return;
    setLoading(true);
    try {
      const [idRes, compRes] = await Promise.all([
        fetch(`${API}/api/gs1-identifiers/labels/${labelId}`, { headers: getAuthHeaders() }),
        fetch(`${API}/api/gs1-identifiers/labels/${labelId}/compliance`, { headers: getAuthHeaders() }),
      ]);
      const idData = idRes.ok ? await idRes.json() : {};
      const compData = compRes.ok ? await compRes.json() : {};

      setIdentifiers(idData.identifiers);
      setIsProtected(idData.is_protected || false);
      setCompliance(compData);

      if (idData.identifiers) {
        const { label_id, owner_user_id, created_at, created_by, updated_at, updated_by, _id, ...clean } = idData.identifiers;
        setForm(clean);
      } else {
        setForm({ gs1_company_prefix: '', gln: '', ein: '', duns: '', business_registration_number: '', business_entity: '', business_owner: '', business_type: '' });
      }
      setErrors({});
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (selectedLabel?.label_id) loadIdentifiers(selectedLabel.label_id);
  }, [selectedLabel, loadIdentifiers]);

  // Inline validation
  const validateField = async (field, value) => {
    if (!value.trim()) {
      setErrors(e => ({ ...e, [field]: `${IDENTIFIER_META[field]?.label || field} is required` }));
      return;
    }
    const validatable = ['gtin', 'gln', 'gs1_company_prefix', 'ein', 'duns', 'business_registration_number'];
    if (!validatable.includes(field)) {
      setErrors(e => { const c = { ...e }; delete c[field]; return c; });
      return;
    }
    setValidating(v => ({ ...v, [field]: true }));
    try {
      const res = await fetch(`${API}/api/gs1-identifiers/validate`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ identifier_type: field, value }),
      });
      const data = await res.json();
      if (data.valid) {
        setErrors(e => { const c = { ...e }; delete c[field]; return c; });
      } else {
        setErrors(e => ({ ...e, [field]: data.error }));
      }
    } catch {
      // skip
    }
    setValidating(v => ({ ...v, [field]: false }));
  };

  // Save identifiers
  const handleSave = async () => {
    if (!selectedLabel?.label_id) return;
    setSaving(true);
    setErrors({});
    try {
      const res = await fetch(`${API}/api/gs1-identifiers/labels/${selectedLabel.label_id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (res.ok && data.success) {
        loadIdentifiers(selectedLabel.label_id);
      } else {
        if (data.detail?.validation_errors) {
          setErrors(data.detail.validation_errors);
        } else {
          setErrors({ _general: typeof data.detail === 'string' ? data.detail : 'Failed to save identifiers' });
        }
      }
    } catch (e) {
      setErrors({ _general: 'Network error saving identifiers' });
    }
    setSaving(false);
  };

  if (loading && labels.length === 0) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center" data-testid="identifiers-loading">
        <Loader2 className="animate-spin text-purple-400" size={32} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white pt-20 pb-16 px-4" data-testid="business-identifiers-page">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Business & GS1 Identifiers</h1>
            <p className="text-slate-400 text-sm mt-1">Mandatory identifiers for all labels — format validated with GS1 check-digit verification</p>
          </div>
          {compliance && <StatusBadge compliant={compliance.compliant} />}
        </div>

        {/* Label Selector */}
        {labels.length > 1 && (
          <div className="flex flex-wrap gap-2" data-testid="label-selector">
            {labels.map(l => (
              <button
                key={l.label_id}
                onClick={() => setSelectedLabel(l)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedLabel?.label_id === l.label_id ? 'bg-purple-600 text-white' : 'bg-white/[.06] text-slate-300 hover:bg-white/10'}`}
                data-testid={`label-tab-${l.label_id}`}
              >
                {l.label_name || l.label_id}
              </button>
            ))}
          </div>
        )}

        {/* Protected Owner Banner */}
        {isProtected && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-start gap-3" data-testid="protected-banner">
            <Lock className="text-amber-400 mt-0.5 shrink-0" size={20} />
            <div>
              <p className="text-amber-300 font-semibold text-sm">Immutable Ownership Protection Active</p>
              <p className="text-amber-200/70 text-xs mt-0.5">
                These identifiers are permanently locked for {protectedData?.protected_owner || 'the protected owner'} / {protectedData?.protected_business || 'protected business'}. They cannot be modified.
              </p>
            </div>
          </div>
        )}

        {/* Compliance Summary */}
        {compliance && !compliance.compliant && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4" data-testid="compliance-alert">
            <p className="text-red-300 font-semibold text-sm flex items-center gap-2"><AlertTriangle size={16} /> Identifier Compliance Issues</p>
            {compliance.missing_identifiers?.length > 0 && (
              <p className="text-red-200/70 text-xs mt-1">Missing: {compliance.missing_identifiers.map(f => IDENTIFIER_META[f]?.label || f).join(', ')}</p>
            )}
            {Object.keys(compliance.invalid_identifiers || {}).length > 0 && (
              <p className="text-red-200/70 text-xs mt-1">Invalid: {Object.entries(compliance.invalid_identifiers).map(([f, e]) => `${IDENTIFIER_META[f]?.label || f}: ${e}`).join('; ')}</p>
            )}
          </div>
        )}

        {errors._general && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-red-300 text-sm" data-testid="general-error">
            {errors._general}
          </div>
        )}

        {/* Identifier Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5" data-testid="identifiers-form">
          {Object.entries(IDENTIFIER_META).map(([field, meta]) => {
            const Icon = meta.icon;
            const value = form[field] || '';
            const error = errors[field];
            const isFieldProtected = isProtected;
            const isFieldValidating = validating[field];

            if (field === 'business_type') {
              return (
                <div key={field} className="space-y-1.5">
                  <label className="flex items-center gap-1.5 text-sm font-medium text-slate-300">
                    <Icon size={14} className="text-purple-400" />
                    {meta.label}
                    {isFieldProtected && <Lock size={12} className="text-amber-400 ml-1" />}
                  </label>
                  <select
                    value={value}
                    disabled={isFieldProtected}
                    onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                    className={`w-full bg-white/[.06] border rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition ${error ? 'border-red-500/50' : 'border-white/10'} ${isFieldProtected ? 'opacity-60 cursor-not-allowed' : ''}`}
                    data-testid={`field-${field}`}
                  >
                    <option value="">Select type...</option>
                    {BUSINESS_TYPES.map(bt => <option key={bt} value={bt}>{bt}</option>)}
                  </select>
                  <p className="text-[11px] text-slate-500">{meta.hint}</p>
                  {error && <p className="text-[11px] text-red-400" data-testid={`error-${field}`}>{error}</p>}
                </div>
              );
            }

            return (
              <div key={field} className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-sm font-medium text-slate-300">
                  <Icon size={14} className="text-purple-400" />
                  {meta.label}
                  <span className="text-red-400 text-[10px] ml-0.5">*</span>
                  {isFieldProtected && <Lock size={12} className="text-amber-400 ml-1" />}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={value}
                    disabled={isFieldProtected}
                    placeholder={meta.placeholder}
                    onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                    onBlur={() => validateField(field, value)}
                    className={`w-full bg-white/[.06] border rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition ${error ? 'border-red-500/50' : 'border-white/10'} ${isFieldProtected ? 'opacity-60 cursor-not-allowed' : ''}`}
                    data-testid={`field-${field}`}
                  />
                  {isFieldValidating && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <Loader2 size={14} className="animate-spin text-purple-400" />
                    </div>
                  )}
                  {!isFieldValidating && value && !error && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <CheckCircle size={14} className="text-emerald-400" />
                    </div>
                  )}
                </div>
                <p className="text-[11px] text-slate-500">{meta.hint}</p>
                {error && <p className="text-[11px] text-red-400" data-testid={`error-${field}`}>{error}</p>}
              </div>
            );
          })}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4 pt-2">
          {!isProtected && (
            <button
              onClick={handleSave}
              disabled={saving || Object.keys(errors).filter(k => k !== '_general').length > 0}
              className="px-6 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg transition-all flex items-center gap-2"
              data-testid="save-identifiers-btn"
            >
              {saving ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle size={16} />}
              {saving ? 'Saving...' : 'Save Identifiers'}
            </button>
          )}
          <button
            onClick={() => selectedLabel?.label_id && loadIdentifiers(selectedLabel.label_id)}
            className="px-4 py-2.5 bg-white/[.06] hover:bg-white/10 text-slate-300 text-sm font-medium rounded-lg transition-all flex items-center gap-2"
            data-testid="refresh-identifiers-btn"
          >
            <RefreshCw size={14} /> Refresh
          </button>
        </div>

        {/* GS1 Standards Info */}
        <div className="bg-white/[.04] border border-white/10 rounded-2xl p-6 mt-4" data-testid="gs1-standards-info">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <Shield size={18} className="text-purple-400" /> GS1 Standards Compliance
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            {[
              { name: 'GTIN', desc: 'Global Trade Item Number (8/12/13/14 digits)', standard: 'GS1-128' },
              { name: 'GLN', desc: 'Global Location Number (13 digits)', standard: 'GS1 GLN' },
              { name: 'GS1 Prefix', desc: 'Company Prefix (7-11 digits)', standard: 'GS1 Registration' },
              { name: 'ISRC', desc: 'ISO 3901 Recording Code', standard: 'CC-XXX-YY-NNNNN' },
              { name: 'UPC', desc: 'Universal Product Code (12 digits)', standard: 'GTIN-12' },
              { name: 'EIN', desc: 'Employer Identification Number', standard: 'XX-XXXXXXX' },
            ].map(s => (
              <div key={s.name} className="bg-white/[.03] rounded-xl p-3">
                <p className="text-white font-medium flex items-center gap-1.5">
                  <ChevronRight size={12} className="text-purple-400" /> {s.name}
                </p>
                <p className="text-slate-400 text-xs mt-0.5">{s.desc}</p>
                <p className="text-purple-300 text-[10px] mt-0.5">Format: {s.standard}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
