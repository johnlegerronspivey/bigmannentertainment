import React, { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Building2, Package, BarChart3, Scale, FileText, DollarSign, ShieldCheck, RefreshCw, Loader2, AlertCircle, ChevronDown, ChevronUp, Download, Plus, X, Gavel, TriangleAlert } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

/* ─── Governance Dashboard Widget ─── */
const DISPUTE_STATUS_STYLES = {
  open: 'bg-blue-500/20 text-blue-300',
  under_review: 'bg-yellow-500/20 text-yellow-300',
  resolved: 'bg-emerald-500/20 text-emerald-300',
  escalated: 'bg-red-500/20 text-red-300',
  closed: 'bg-slate-500/20 text-slate-400',
};

const PRIORITY_DOT = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-blue-500',
  low: 'bg-slate-400',
};

const RULE_TYPE_COLORS = {
  voting: 'bg-indigo-500/20 text-indigo-300',
  content_approval: 'bg-emerald-500/20 text-emerald-300',
  financial: 'bg-amber-500/20 text-amber-300',
  distribution: 'bg-cyan-500/20 text-cyan-300',
  membership: 'bg-rose-500/20 text-rose-300',
};

const GovernanceWidget = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/gs1/governance-overview`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState text="Loading governance data..." />;
  if (!data) return null;

  const { governance, disputes } = data;
  const openCount = disputes.open_disputes + disputes.under_review + disputes.escalated_disputes;

  return (
    <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6" data-testid="governance-widget">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Gavel size={18} className="text-purple-400" /> Governance & Disputes
        </h3>
        {openCount > 0 && (
          <span className="text-xs font-medium bg-red-500/20 text-red-300 px-2.5 py-1 rounded-full" data-testid="governance-open-badge">
            {openCount} open
          </span>
        )}
      </div>

      {/* Top Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        <div className="bg-white/[.04] rounded-xl px-4 py-3 text-center">
          <div className="text-xl font-bold text-purple-400">{governance.active_rules}</div>
          <div className="text-slate-500 text-[11px] mt-0.5">Active Rules</div>
        </div>
        <div className="bg-white/[.04] rounded-xl px-4 py-3 text-center">
          <div className="text-xl font-bold text-white">{governance.total_rules}</div>
          <div className="text-slate-500 text-[11px] mt-0.5">Total Rules</div>
        </div>
        <div className="bg-white/[.04] rounded-xl px-4 py-3 text-center">
          <div className="text-xl font-bold text-amber-400">{disputes.open_disputes}</div>
          <div className="text-slate-500 text-[11px] mt-0.5">Open Disputes</div>
        </div>
        <div className="bg-white/[.04] rounded-xl px-4 py-3 text-center">
          <div className="text-xl font-bold text-emerald-400">{disputes.resolved_disputes + disputes.closed_disputes}</div>
          <div className="text-slate-500 text-[11px] mt-0.5">Resolved / Closed</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Left — Rules by Type + Disputes by Priority */}
        <div className="space-y-4">
          {/* Rules by Type */}
          {Object.keys(governance.rules_by_type).length > 0 && (
            <div>
              <span className="text-slate-400 text-xs uppercase tracking-wider">Rules by Type</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {Object.entries(governance.rules_by_type).map(([type, count]) => (
                  <span key={type} className={`px-2.5 py-1 rounded-lg text-xs font-medium ${RULE_TYPE_COLORS[type] || 'bg-slate-500/20 text-slate-300'}`}>
                    {type.replace(/_/g, ' ')} ({count})
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Disputes by Priority */}
          {Object.keys(disputes.disputes_by_priority).length > 0 && (
            <div>
              <span className="text-slate-400 text-xs uppercase tracking-wider">Disputes by Priority</span>
              <div className="space-y-1.5 mt-2">
                {['critical', 'high', 'medium', 'low'].map(pri => {
                  const count = disputes.disputes_by_priority[pri];
                  if (!count) return null;
                  return (
                    <div key={pri} className="flex items-center gap-2 text-sm">
                      <span className={`w-2 h-2 rounded-full ${PRIORITY_DOT[pri]}`} />
                      <span className="text-slate-300 capitalize">{pri}</span>
                      <span className="ml-auto text-white font-mono text-xs">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Dispute Status Breakdown */}
          <div>
            <span className="text-slate-400 text-xs uppercase tracking-wider">Dispute Status</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {[
                { key: 'open_disputes', label: 'Open' },
                { key: 'under_review', label: 'Under Review' },
                { key: 'escalated_disputes', label: 'Escalated' },
                { key: 'resolved_disputes', label: 'Resolved' },
                { key: 'closed_disputes', label: 'Closed' },
              ].map(s => {
                const count = disputes[s.key];
                if (!count) return null;
                const statusKey = s.key.replace('_disputes', '');
                return (
                  <span key={s.key} className={`px-2.5 py-1 rounded-lg text-xs font-medium ${DISPUTE_STATUS_STYLES[statusKey] || DISPUTE_STATUS_STYLES[s.key.replace('_disputes', '')] || 'bg-slate-500/20 text-slate-300'}`}>
                    {s.label}: {count}
                  </span>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right — Recent Disputes */}
        <div>
          <span className="text-slate-400 text-xs uppercase tracking-wider">Recent Disputes</span>
          {disputes.recent_disputes.length > 0 ? (
            <div className="space-y-2 mt-2">
              {disputes.recent_disputes.map(d => (
                <div key={d.dispute_id} className="bg-white/[.03] border border-white/5 rounded-lg px-3.5 py-2.5 flex items-start gap-3 hover:bg-white/[.05] transition" data-testid={`recent-dispute-${d.dispute_id}`}>
                  <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${PRIORITY_DOT[d.priority] || 'bg-slate-400'}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white truncate">{d.title}</div>
                    <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500">
                      <span>{d.dispute_type?.replace(/_/g, ' ')}</span>
                      <span className="text-slate-600">|</span>
                      <span>{d.label_id}</span>
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium shrink-0 ${DISPUTE_STATUS_STYLES[d.status] || 'bg-slate-500/20 text-slate-400'}`}>
                    {d.status?.replace(/_/g, ' ')}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm mt-2">No recent disputes.</p>
          )}
        </div>
      </div>
    </div>
  );
};

/* ─── Overview Tab ─── */
const OverviewTab = () => {
  const [gs1Data, setGs1Data] = useState(null);
  const [licensingData, setLicensingData] = useState(null);
  const [compData, setCompData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [g, l, c] = await Promise.allSettled([
        fetch(`${API}/api/gs1/business-info`).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/licensing/dashboard`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/comprehensive-licensing/dashboard`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
      ]);
      if (g.status === 'fulfilled') setGs1Data(g.value);
      if (l.status === 'fulfilled') setLicensingData(l.value);
      if (c.status === 'fulfilled') setCompData(c.value?.comprehensive_licensing_dashboard);
      setLoading(false);
    };
    load();
  }, []);

  if (loading) return <LoadingState text="Loading overview..." />;

  const ov = licensingData?.licensing_overview;
  const fin = licensingData?.financial_summary;
  const gs1Info = gs1Data?.business_info;

  return (
    <div className="space-y-6" data-testid="overview-tab">
      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Platforms Licensed" value={ov?.total_platforms_licensed ?? compData?.licensing_overview?.total_platforms_licensed ?? 0} color="text-white" />
        <StatCard label="Active Licenses" value={ov?.active_licenses ?? compData?.licensing_overview?.active_agreements ?? 0} color="text-emerald-400" />
        <StatCard label="Compliance Rate" value={`${(ov?.licensing_compliance_rate ?? 100).toFixed(0)}%`} color="text-sky-400" />
        <StatCard label="GS1 Assets" value={gs1Info?.total_assets ?? 0} color="text-amber-400" />
      </div>

      {/* Two-Column */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Business Summary */}
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Building2 size={18} className="text-purple-400" /> Business Entity
          </h3>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Entity" value={gs1Data?.business_entity ?? licensingData?.business_info?.business_entity} />
            <InfoRow label="Owner" value={gs1Data?.business_owner ?? licensingData?.business_info?.business_owner} />
            <InfoRow label="Industry" value={gs1Data?.industry ?? licensingData?.business_info?.industry} />
            <InfoRow label="EIN" value={gs1Data?.ein ?? licensingData?.business_info?.ein} />
            <InfoRow label="GS1 Prefix" value={gs1Info?.company_prefix} />
            <InfoRow label="GLN" value={gs1Data?.business_info?.legal_entity_gln ?? '0860004340201'} />
            <InfoRow label="Certification" value={gs1Info?.certification_level} accent />
          </dl>
          <a href="/business-identifiers" className="mt-3 inline-flex items-center gap-1.5 text-xs text-purple-400 hover:text-purple-300 transition" data-testid="manage-identifiers-link">
            <ShieldCheck size={12} /> Manage GS1 & Business Identifiers
          </a>
        </div>

        {/* Financial Summary */}
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <DollarSign size={18} className="text-emerald-400" /> Financial Summary
          </h3>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Total Licensing Fees" value={`$${(fin?.total_licensing_fees ?? compData?.licensing_overview?.total_licensing_fees ?? 0).toLocaleString()}`} />
            <InfoRow label="Monthly Recurring" value={`$${(fin?.monthly_recurring_revenue ?? 0).toLocaleString()}`} />
            <InfoRow label="Comprehensive Agreements" value={compData?.licensing_overview?.total_comprehensive_agreements ?? 0} />
            <InfoRow label="Revenue Share Potential" value={fin?.revenue_share_potential ?? 'N/A'} />
          </dl>
        </div>
      </div>

      {/* Platform Categories */}
      {licensingData?.platform_categories && (
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <BarChart3 size={18} className="text-sky-400" /> Platform Categories
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {Object.entries(licensingData.platform_categories).map(([cat, count]) => (
              <div key={cat} className="bg-white/[.04] rounded-xl px-4 py-3 flex justify-between items-center">
                <span className="text-slate-300 text-sm capitalize">{cat.replace(/_/g, ' ')}</span>
                <span className="text-white font-semibold text-sm">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Governance Dashboard Widget */}
      <GovernanceWidget />
    </div>
  );
};

/* ─── GS1 & Business Info Tab ─── */
const GS1BusinessTab = () => {
  const [businessInfo, setBusinessInfo] = useState(null);
  const [compBizInfo, setCompBizInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      const [g, c] = await Promise.allSettled([
        fetch(`${API}/api/gs1/business-info`).then(r => r.ok ? r.json() : null),
        fetch(`${API}/api/comprehensive-licensing/business-information`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
      ]);
      if (g.status === 'fulfilled' && g.value) setBusinessInfo(g.value);
      else setError('Failed to load GS1 business info');
      if (c.status === 'fulfilled' && c.value) setCompBizInfo(c.value.business_information);
      setLoading(false);
    };
    load();
  }, []);

  if (loading) return <LoadingState text="Loading business information..." />;
  if (error && !businessInfo) return <ErrorState message={error} />;

  return (
    <div className="space-y-6" data-testid="gs1-business-tab">
      {/* Entity & GS1 Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Business Entity</h3>
          <dl className="space-y-3 text-sm">
            <InfoRow label="Business Entity" value={businessInfo?.business_entity} />
            <InfoRow label="Business Owner" value={businessInfo?.business_owner} />
            <InfoRow label="Industry" value={businessInfo?.industry} />
            <InfoRow label="Business Type" value={businessInfo?.business_type} />
            <InfoRow label="EIN" value={businessInfo?.ein} />
            <InfoRow label="TIN" value={businessInfo?.tin} />
          </dl>
        </div>

        {businessInfo?.business_info && (
          <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">GS1 Registry</h3>
            <dl className="space-y-3 text-sm">
              <InfoRow label="Company Prefix" value={businessInfo.business_info.company_prefix} />
              <InfoRow label="Legal Entity GLN" value={businessInfo.business_info.legal_entity_gln || 'N/A'} />
              <InfoRow label="Total Assets" value={businessInfo.business_info.total_assets} />
              <InfoRow label="Compliance Status" value={businessInfo.business_info.compliance_status} accent />
              <InfoRow label="Certification Level" value={businessInfo.business_info.certification_level} accent />
              <InfoRow label="Active Identifiers" value={businessInfo.business_info.active_identifiers} />
            </dl>
          </div>
        )}
      </div>

      {/* Capabilities */}
      {businessInfo?.capabilities && (
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">GS1 Capabilities</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <span className="text-slate-400 text-xs uppercase tracking-wider">Identifier Generation</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {businessInfo.capabilities.identifier_generation?.map((id, i) => (
                  <span key={i} className="bg-purple-500/20 text-purple-200 px-2.5 py-1 rounded-lg text-xs font-medium">{id}</span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-slate-400 text-xs uppercase tracking-wider">Features</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {businessInfo.capabilities.digital_links && <FeatureBadge label="Digital Links" />}
                {businessInfo.capabilities.qr_codes && <FeatureBadge label="QR Codes" />}
                {businessInfo.capabilities.analytics && <FeatureBadge label="Analytics" />}
                {businessInfo.capabilities.bulk_operations && <FeatureBadge label="Bulk Operations" />}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Comprehensive Licensing Business Info */}
      {compBizInfo && (
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Legal & Contact Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <span className="text-slate-400 text-xs uppercase tracking-wider">Legal Identifiers</span>
              <dl className="space-y-2 text-sm mt-2">
                <InfoRow label="GS1 Prefix" value={compBizInfo.company_prefix} />
                <InfoRow label="ISAN Prefix" value={compBizInfo.isan_prefix} />
                <InfoRow label="ISRC Prefix" value={compBizInfo.isrc_prefix} />
                <InfoRow label="Legal Entity GLN" value={compBizInfo.legal_entity_gln} />
              </dl>
            </div>
            <div>
              <span className="text-slate-400 text-xs uppercase tracking-wider">Contact</span>
              <dl className="space-y-2 text-sm mt-2">
                <InfoRow label="Email" value={compBizInfo.contact_email} />
                <InfoRow label="Phone" value={compBizInfo.contact_phone || '(334) 669-8638'} />
              </dl>
            </div>
            <div>
              <span className="text-slate-400 text-xs uppercase tracking-wider">Platform Integration</span>
              <dl className="space-y-2 text-sm mt-2">
                <InfoRow label="Platforms" value={compBizInfo.distribution_platform_ids?.length ?? 0} />
                <InfoRow label="Credentials" value={`${Object.keys(compBizInfo.platform_credentials || {}).length} configured`} />
                <InfoRow label="API Integrations" value={`${Object.keys(compBizInfo.api_configurations || {}).length} active`} />
              </dl>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ─── Products & Barcodes Tab ─── */
const ProductsBarcodesTab = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [newProduct, setNewProduct] = useState({ title: '', artist_name: '', label_name: '', release_date: '', genre: '', duration_seconds: '', isrc: '', catalog_number: '', distribution_format: 'Digital' });
  const [upcCode, setUpcCode] = useState('');
  const [formatType, setFormatType] = useState('PNG');
  const [barcodeData, setBarcodeData] = useState(null);
  const [barcodeLoading, setBarcodeLoading] = useState(false);

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/gs1/products`);
      if (res.ok) { const d = await res.json(); setProducts(d.products || []); setError(''); }
      else setError('Failed to load products');
    } catch { setError('Error loading products.'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const createProduct = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/gs1/products`, {
        method: 'POST', headers: getAuthHeaders(),
        body: JSON.stringify({ ...newProduct, release_date: new Date(newProduct.release_date).toISOString(), duration_seconds: newProduct.duration_seconds ? parseInt(newProduct.duration_seconds) : null })
      });
      if (res.ok) {
        const d = await res.json();
        alert(`Product created - UPC: ${d.product.upc}, GTIN: ${d.product.gtin}`);
        setShowForm(false);
        setNewProduct({ title: '', artist_name: '', label_name: '', release_date: '', genre: '', duration_seconds: '', isrc: '', catalog_number: '', distribution_format: 'Digital' });
        fetchProducts();
      } else { const e = await res.json(); setError(e.detail || 'Failed to create product'); }
    } catch { setError('Error creating product.'); }
    finally { setLoading(false); }
  };

  const generateBarcode = async () => {
    if (!upcCode || upcCode.length !== 12) { setError('UPC code must be exactly 12 digits'); return; }
    try {
      setBarcodeLoading(true); setError('');
      const res = await fetch(`${API}/api/gs1/barcode/generate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ upc_code: upcCode, format_type: formatType }) });
      if (res.ok) setBarcodeData(await res.json());
      else setError('Failed to generate barcode');
    } catch { setError('Error generating barcode.'); }
    finally { setBarcodeLoading(false); }
  };

  const downloadBarcode = () => {
    if (!barcodeData) return;
    const link = document.createElement('a');
    link.href = `data:${barcodeData.content_type};base64,${barcodeData.data}`;
    link.download = `barcode_${barcodeData.upc_code}.${formatType.toLowerCase()}`;
    link.click();
  };

  return (
    <div className="space-y-6" data-testid="products-barcodes-tab">
      {error && <ErrorBanner message={error} onDismiss={() => setError('')} />}

      {/* Products Section */}
      <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-white">UPC / GTIN Products</h3>
          <button onClick={() => setShowForm(!showForm)} className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all ${showForm ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30' : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30'}`} data-testid="create-product-btn">
            {showForm ? <><X size={14} /> Cancel</> : <><Plus size={14} /> Create Product</>}
          </button>
        </div>

        {showForm && (
          <div className="bg-white/[.04] rounded-xl p-5 mb-5 border border-white/5">
            <h4 className="text-white font-medium mb-4">New Music Product</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'title', label: 'Title *', type: 'text' },
                { key: 'artist_name', label: 'Artist *', type: 'text' },
                { key: 'label_name', label: 'Label *', type: 'text' },
                { key: 'release_date', label: 'Release Date *', type: 'date' },
                { key: 'genre', label: 'Genre', type: 'text' },
                { key: 'duration_seconds', label: 'Duration (sec)', type: 'number' },
                { key: 'isrc', label: 'ISRC', type: 'text', placeholder: 'USTEST2500001' },
                { key: 'catalog_number', label: 'Catalog #', type: 'text' },
              ].map(f => (
                <div key={f.key}>
                  <label className="block text-slate-400 text-xs mb-1.5">{f.label}</label>
                  <input type={f.type} value={newProduct[f.key]} onChange={e => setNewProduct(p => ({ ...p, [f.key]: e.target.value }))} placeholder={f.placeholder || ''} className="w-full bg-white/[.06] text-white border border-white/10 rounded-lg px-3 py-2 text-sm focus:border-purple-500 focus:outline-none transition" data-testid={`product-input-${f.key}`} />
                </div>
              ))}
            </div>
            <button onClick={createProduct} disabled={loading || !newProduct.title || !newProduct.artist_name || !newProduct.label_name || !newProduct.release_date} className="mt-4 bg-purple-600 hover:bg-purple-700 disabled:opacity-40 text-white font-medium py-2 px-5 rounded-xl text-sm transition" data-testid="submit-product-btn">
              {loading ? 'Creating...' : 'Create Product'}
            </button>
          </div>
        )}

        {loading && products.length === 0 ? (
          <LoadingState text="Loading products..." />
        ) : products.length === 0 ? (
          <p className="text-slate-400 text-sm text-center py-6">No products yet. Create your first music product.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm" data-testid="products-table">
              <thead>
                <tr className="border-b border-white/10">
                  {['UPC', 'GTIN', 'Title', 'Artist', 'Label', 'Release', 'Status'].map(h => (
                    <th key={h} className="text-left text-slate-400 py-2.5 px-2 text-xs uppercase tracking-wider font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {products.map((p, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/[.02] transition">
                    <td className="text-emerald-400 py-2.5 px-2 font-mono text-xs">{p.upc}</td>
                    <td className="text-sky-400 py-2.5 px-2 font-mono text-xs">{p.gtin}</td>
                    <td className="text-white py-2.5 px-2">{p.title}</td>
                    <td className="text-slate-300 py-2.5 px-2">{p.artist_name}</td>
                    <td className="text-slate-300 py-2.5 px-2">{p.label_name}</td>
                    <td className="text-slate-300 py-2.5 px-2">{new Date(p.release_date).toLocaleDateString()}</td>
                    <td className="py-2.5 px-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${p.gtin_status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-500/20 text-slate-400'}`}>{p.gtin_status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Barcode Generator */}
      <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Barcode Generator</h3>
        <div className="flex flex-col sm:flex-row gap-3">
          <input type="text" value={upcCode} onChange={e => setUpcCode(e.target.value.replace(/\D/g, '').slice(0, 12))} placeholder="Enter 12-digit UPC" maxLength={12} className="flex-1 bg-white/[.06] text-white border border-white/10 rounded-lg px-3 py-2 text-sm font-mono focus:border-purple-500 focus:outline-none transition" data-testid="barcode-upc-input" />
          <select value={formatType} onChange={e => setFormatType(e.target.value)} className="bg-white/[.06] text-white border border-white/10 rounded-lg px-3 py-2 text-sm" data-testid="barcode-format-select">
            <option value="PNG">PNG</option>
            <option value="JPEG">JPEG</option>
            <option value="SVG">SVG</option>
          </select>
          <button onClick={generateBarcode} disabled={barcodeLoading || !upcCode || upcCode.length !== 12} className="bg-sky-600 hover:bg-sky-700 disabled:opacity-40 text-white font-medium py-2 px-5 rounded-xl text-sm transition flex items-center gap-1.5" data-testid="generate-barcode-btn">
            {barcodeLoading ? <Loader2 size={14} className="animate-spin" /> : <BarChart3 size={14} />} Generate
          </button>
        </div>
        {barcodeData && (
          <div className="mt-5 bg-white/[.04] rounded-xl p-5 border border-white/5">
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <img src={`data:${barcodeData.content_type};base64,${barcodeData.data}`} alt={`Barcode ${barcodeData.upc_code}`} className="bg-white p-3 rounded-lg" />
              <div className="space-y-2 text-sm flex-1">
                <InfoRow label="UPC" value={barcodeData.upc_code} />
                <InfoRow label="Format" value={barcodeData.format_type} />
                <InfoRow label="Size" value={`${(barcodeData.size_bytes / 1024).toFixed(1)} KB`} />
              </div>
              <button onClick={downloadBarcode} className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 px-5 rounded-xl text-sm transition flex items-center gap-1.5" data-testid="download-barcode-btn">
                <Download size={14} /> Download
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/* ─── Platform Licensing Tab ─── */
const PlatformLicensingTab = () => {
  const [licenses, setLicenses] = useState([]);
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [initLoading, setInitLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (statusFilter) params.append('status', statusFilter);
    const [l, s] = await Promise.allSettled([
      fetch(`${API}/api/licensing/platforms?${params}`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/api/licensing/status`, { headers: getAuthHeaders() }).then(r => r.ok ? r.json() : null),
    ]);
    if (l.status === 'fulfilled' && l.value) setLicenses(l.value.licenses || []);
    if (s.status === 'fulfilled' && s.value) setStatusData(s.value);
    setLoading(false);
  }, [statusFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const initializeAll = async () => {
    try {
      setInitLoading(true);
      const res = await fetch(`${API}/api/licensing/initialize-all-platforms`, { method: 'POST', headers: getAuthHeaders() });
      if (res.ok) { const d = await res.json(); alert(`Licensed ${d.platforms_licensed} platforms!`); fetchData(); }
      else setError('Failed to initialize');
    } catch { setError('Error initializing.'); }
    finally { setInitLoading(false); }
  };

  const toggleLicense = async (platformId, currentStatus) => {
    const endpoint = currentStatus === 'active' ? 'deactivate' : 'activate';
    const body = currentStatus === 'active' ? { reason: prompt('Reason for deactivation:') || 'No reason' } : undefined;
    try {
      const res = await fetch(`${API}/api/licensing/platforms/${platformId}/${endpoint}`, { method: 'POST', headers: getAuthHeaders(), body: body ? JSON.stringify(body) : undefined });
      if (res.ok) fetchData();
      else alert(`Failed to ${endpoint} license`);
    } catch { alert(`Error ${endpoint}ing license`); }
  };

  if (loading) return <LoadingState text="Loading platform licenses..." />;

  return (
    <div className="space-y-6" data-testid="platform-licensing-tab">
      {error && <ErrorBanner message={error} onDismiss={() => setError('')} />}

      {/* Status Summary */}
      {statusData && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Platforms" value={statusData.total_platforms_licensed ?? 0} color="text-white" />
          <StatCard label="Active Licenses" value={statusData.active_licenses ?? 0} color="text-emerald-400" />
          <StatCard label="Health Score" value={`${statusData.licensing_health_score ?? 0}%`} color={statusData.licensing_health_score > 90 ? 'text-emerald-400' : 'text-amber-400'} />
          <StatCard label="Compliance" value={`${(statusData.compliance_rate ?? 0).toFixed(0)}%`} color="text-sky-400" />
        </div>
      )}

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="bg-white/[.06] text-white border border-white/10 rounded-lg px-3 py-2 text-sm" data-testid="license-status-filter">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="pending">Pending</option>
          <option value="expired">Expired</option>
          <option value="suspended">Suspended</option>
        </select>
        <button onClick={initializeAll} disabled={initLoading} className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white font-medium py-2 px-5 rounded-xl text-sm transition flex items-center gap-1.5" data-testid="license-all-btn">
          {initLoading ? <Loader2 size={14} className="animate-spin" /> : <Scale size={14} />} License All Platforms
        </button>
        <button onClick={fetchData} className="bg-white/[.06] hover:bg-white/10 text-white py-2 px-3 rounded-xl text-sm transition" data-testid="refresh-licenses-btn">
          <RefreshCw size={14} />
        </button>
      </div>

      {/* License Grid */}
      {licenses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {licenses.map(lic => (
            <div key={lic.platform_id} className="bg-white/[.06] border border-white/10 rounded-xl p-5 hover:border-white/20 transition">
              <div className="flex justify-between items-start mb-3">
                <h4 className="text-white font-medium text-sm">{lic.platform_name}</h4>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${lic.license_status === 'active' ? 'bg-emerald-500/20 text-emerald-300' : lic.license_status === 'pending' ? 'bg-amber-500/20 text-amber-300' : lic.license_status === 'expired' ? 'bg-red-500/20 text-red-300' : 'bg-slate-500/20 text-slate-400'}`}>{lic.license_status?.toUpperCase()}</span>
              </div>
              <dl className="space-y-1.5 text-xs text-slate-400 mb-3">
                <div className="flex justify-between"><span>Type</span><span className="text-slate-300">{lic.license_type}</span></div>
                <div className="flex justify-between"><span>Monthly Limit</span><span className="text-slate-300">{lic.monthly_limit} uploads</span></div>
                <div className="flex justify-between"><span>Revenue Share</span><span className="text-slate-300">{lic.revenue_share_percentage}%</span></div>
                <div className="flex justify-between"><span>Usage</span><span className="text-slate-300">{lic.usage_count || 0} uploads</span></div>
              </dl>
              <button onClick={() => toggleLicense(lic.platform_id, lic.license_status)} className={`w-full py-1.5 rounded-lg text-xs font-medium transition ${lic.license_status === 'active' ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30' : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30'}`} data-testid={`toggle-license-${lic.platform_id}`}>
                {lic.license_status === 'active' ? 'Deactivate' : 'Activate'}
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-slate-400 text-sm text-center py-8">No platform licenses found. Click "License All Platforms" to get started.</p>
      )}
    </div>
  );
};

/* ─── Compensation Tab ─── */
const CompensationTab = () => {
  const [subTab, setSubTab] = useState('rates');
  const [rates, setRates] = useState([]);
  const [compData, setCompData] = useState(null);
  const [dashData, setDashData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [periodDays, setPeriodDays] = useState(30);

  const loadRates = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/licensing/statutory-rates`, { headers: getAuthHeaders() });
      if (res.ok) { const d = await res.json(); setRates(d.rates || []); }
    } catch { setError('Error loading rates'); }
    finally { setLoading(false); }
  };

  const loadDailyComp = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/licensing/daily-compensation`, { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify({ date: selectedDate }) });
      if (res.ok) setCompData(await res.json());
    } catch { setError('Error loading compensation'); }
    finally { setLoading(false); }
  };

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/licensing/compensation-dashboard?period_days=${periodDays}`, { headers: getAuthHeaders() });
      if (res.ok) setDashData(await res.json());
    } catch { setError('Error loading analytics'); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadRates(); }, []);

  const subTabs = [
    { id: 'rates', label: 'Statutory Rates' },
    { id: 'daily', label: 'Daily Compensation' },
    { id: 'analytics', label: 'Compensation Analytics' },
  ];

  return (
    <div className="space-y-6" data-testid="compensation-tab">
      {error && <ErrorBanner message={error} onDismiss={() => setError('')} />}

      {/* Sub-tabs */}
      <div className="flex gap-2 flex-wrap">
        {subTabs.map(t => (
          <button key={t.id} onClick={() => { setSubTab(t.id); if (t.id === 'rates') loadRates(); if (t.id === 'daily') loadDailyComp(); if (t.id === 'analytics') loadDashboard(); }} className={`px-4 py-2 rounded-xl text-sm font-medium transition ${subTab === t.id ? 'bg-purple-600 text-white' : 'bg-white/[.06] text-slate-300 hover:bg-white/10'}`} data-testid={`comp-subtab-${t.id}`}>
            {t.label}
          </button>
        ))}
      </div>

      {loading && <LoadingState text="Loading..." />}

      {/* Statutory Rates */}
      {subTab === 'rates' && !loading && (
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Statutory Rates</h3>
          {rates.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    {['License Type', 'Rate Type', 'Current Rate', 'Per Unit', 'Effective Date', 'Source'].map(h => (
                      <th key={h} className="text-left text-slate-400 py-2.5 px-2 text-xs uppercase tracking-wider font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rates.map((r, i) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/[.02] transition">
                      <td className="text-white py-2.5 px-2">{r.license_type}</td>
                      <td className="text-slate-300 py-2.5 px-2">{r.rate_type}</td>
                      <td className="text-emerald-400 py-2.5 px-2 font-mono">{r.current_rate}</td>
                      <td className="text-slate-300 py-2.5 px-2">{r.per_unit}</td>
                      <td className="text-slate-300 py-2.5 px-2">{r.effective_date}</td>
                      <td className="text-slate-400 py-2.5 px-2 text-xs">{r.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <p className="text-slate-400 text-sm text-center py-6">No statutory rates data available.</p>}
        </div>
      )}

      {/* Daily Compensation */}
      {subTab === 'daily' && !loading && (
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Daily Compensation</h3>
          <div className="flex gap-3 mb-4">
            <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="bg-white/[.06] text-white border border-white/10 rounded-lg px-3 py-2 text-sm" data-testid="comp-date-input" />
            <button onClick={loadDailyComp} className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-5 rounded-xl text-sm transition" data-testid="calc-comp-btn">Calculate</button>
          </div>
          {compData && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard label="Total Streams" value={compData.total_streams?.toLocaleString() ?? 0} color="text-white" />
                <StatCard label="Total Compensation" value={`$${(compData.total_compensation ?? 0).toFixed(2)}`} color="text-emerald-400" />
                <StatCard label="Platforms" value={compData.platforms_count ?? 0} color="text-sky-400" />
                <StatCard label="Date" value={compData.date ?? selectedDate} color="text-slate-300" />
              </div>
              {compData.platform_breakdown && (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        {['Platform', 'Streams', 'Rate', 'Compensation'].map(h => (
                          <th key={h} className="text-left text-slate-400 py-2.5 px-2 text-xs uppercase tracking-wider font-medium">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {compData.platform_breakdown.map((p, i) => (
                        <tr key={i} className="border-b border-white/5">
                          <td className="text-white py-2.5 px-2">{p.platform}</td>
                          <td className="text-slate-300 py-2.5 px-2">{p.streams?.toLocaleString()}</td>
                          <td className="text-slate-300 py-2.5 px-2 font-mono">${p.rate?.toFixed(4)}</td>
                          <td className="text-emerald-400 py-2.5 px-2 font-mono">${p.compensation?.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Compensation Analytics */}
      {subTab === 'analytics' && !loading && (
        <div className="bg-white/[.06] border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Compensation Analytics</h3>
          <div className="flex gap-3 mb-4">
            <select value={periodDays} onChange={e => setPeriodDays(Number(e.target.value))} className="bg-white/[.06] text-white border border-white/10 rounded-lg px-3 py-2 text-sm" data-testid="analytics-period-select">
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
            <button onClick={loadDashboard} className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-5 rounded-xl text-sm transition" data-testid="load-analytics-btn">Load</button>
          </div>
          {dashData && (
            <div className="space-y-4">
              {dashData.period_summary && (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <StatCard label="Total Revenue" value={`$${(dashData.period_summary.total_revenue ?? 0).toFixed(2)}`} color="text-emerald-400" />
                  <StatCard label="Total Streams" value={(dashData.period_summary.total_streams ?? 0).toLocaleString()} color="text-white" />
                  <StatCard label="Avg Daily Revenue" value={`$${(dashData.period_summary.avg_daily_revenue ?? 0).toFixed(2)}`} color="text-sky-400" />
                  <StatCard label="Period" value={`${periodDays} days`} color="text-slate-300" />
                </div>
              )}
              {dashData.recent_payouts && dashData.recent_payouts.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10">
                        {['Date', 'Platform', 'Amount', 'Status'].map(h => (
                          <th key={h} className="text-left text-slate-400 py-2.5 px-2 text-xs uppercase tracking-wider font-medium">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {dashData.recent_payouts.map((p, i) => (
                        <tr key={i} className="border-b border-white/5">
                          <td className="text-slate-300 py-2.5 px-2">{p.date}</td>
                          <td className="text-white py-2.5 px-2">{p.platform}</td>
                          <td className="text-emerald-400 py-2.5 px-2 font-mono">${p.amount?.toFixed(2)}</td>
                          <td className="py-2.5 px-2"><span className={`px-2 py-0.5 rounded-full text-xs ${p.status === 'completed' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>{p.status}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/* ─── Agreements & Compliance Tab ─── */
const AgreementsComplianceTab = () => {
  const [subTab, setSubTab] = useState('agreements');
  const [agreements, setAgreements] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [compDocs, setCompDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedAgreement, setExpandedAgreement] = useState(null);

  const loadAgreements = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/comprehensive-licensing/license-agreements`, { headers: getAuthHeaders() });
      if (res.ok) { const d = await res.json(); setAgreements(d.agreements || []); }
    } catch { setError('Error loading agreements'); }
    finally { setLoading(false); }
  };

  const loadWorkflows = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/comprehensive-licensing/workflows`, { headers: getAuthHeaders() });
      if (res.ok) { const d = await res.json(); setWorkflows(d.workflows || []); }
    } catch { setError('Error loading workflows'); }
    finally { setLoading(false); }
  };

  const loadCompliance = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/comprehensive-licensing/compliance-documents`, { headers: getAuthHeaders() });
      if (res.ok) { const d = await res.json(); setCompDocs(d.compliance_documents || []); }
    } catch { setError('Error loading compliance'); }
    finally { setLoading(false); }
  };

  const generateLicenses = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/comprehensive-licensing/generate-all-platform-licenses`, { method: 'POST', headers: getAuthHeaders() });
      if (res.ok) { const d = await res.json(); alert(`Licensed ${d.platforms_licensed} platforms!`); loadAgreements(); }
    } catch { setError('Error generating licenses'); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadAgreements(); }, []);

  const subTabs = [
    { id: 'agreements', label: 'Agreements', onClick: loadAgreements },
    { id: 'workflows', label: 'Workflows', onClick: loadWorkflows },
    { id: 'compliance', label: 'Compliance Docs', onClick: loadCompliance },
  ];

  return (
    <div className="space-y-6" data-testid="agreements-compliance-tab">
      {error && <ErrorBanner message={error} onDismiss={() => setError('')} />}

      <div className="flex flex-wrap items-center gap-3">
        {subTabs.map(t => (
          <button key={t.id} onClick={() => { setSubTab(t.id); t.onClick(); }} className={`px-4 py-2 rounded-xl text-sm font-medium transition ${subTab === t.id ? 'bg-purple-600 text-white' : 'bg-white/[.06] text-slate-300 hover:bg-white/10'}`} data-testid={`ac-subtab-${t.id}`}>
            {t.label}
          </button>
        ))}
        <button onClick={generateLicenses} disabled={loading} className="ml-auto bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white font-medium py-2 px-5 rounded-xl text-sm transition flex items-center gap-1.5" data-testid="generate-licenses-btn">
          {loading ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />} Generate All Licenses
        </button>
      </div>

      {loading && <LoadingState text="Loading..." />}

      {/* Agreements */}
      {subTab === 'agreements' && !loading && (
        <div className="space-y-4">
          {agreements.length > 0 ? agreements.map((ag, i) => (
            <div key={i} className="bg-white/[.06] border border-white/10 rounded-xl p-5 hover:border-white/20 transition">
              <div className="flex justify-between items-center cursor-pointer" onClick={() => setExpandedAgreement(expandedAgreement === i ? null : i)}>
                <div className="flex items-center gap-3">
                  <h4 className="text-white font-medium text-sm">{ag.license_type?.replace(/_/g, ' ').toUpperCase()}</h4>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${ag.agreement_status === 'active' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>{ag.agreement_status?.toUpperCase()}</span>
                </div>
                <div className="flex items-center gap-3 text-slate-400 text-sm">
                  <span>{ag.total_platforms} platforms</span>
                  {expandedAgreement === i ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>
              </div>
              {expandedAgreement === i && (
                <div className="mt-4 pt-4 border-t border-white/5 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Details</span>
                    <dl className="space-y-1.5 mt-2">
                      <InfoRow label="Categories" value={ag.platform_categories?.length ?? 0} />
                      <InfoRow label="Duration" value={`${ag.license_duration_months} months`} />
                      <InfoRow label="Created" value={new Date(ag.created_at).toLocaleDateString()} />
                    </dl>
                  </div>
                  <div>
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Financial Terms</span>
                    <dl className="space-y-1.5 mt-2">
                      {ag.licensing_fees && Object.entries(ag.licensing_fees).map(([k, v]) => (
                        <InfoRow key={k} label={k.replace(/_/g, ' ')} value={`$${v?.toLocaleString()}`} />
                      ))}
                    </dl>
                  </div>
                  <div>
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Categories</span>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {ag.platform_categories?.map((c, ci) => (
                        <span key={ci} className="bg-purple-500/20 text-purple-200 px-2 py-0.5 rounded-lg text-xs">{c}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )) : (
            <p className="text-slate-400 text-sm text-center py-8">No agreements found. Click "Generate All Licenses" to create comprehensive agreements.</p>
          )}
        </div>
      )}

      {/* Workflows */}
      {subTab === 'workflows' && !loading && (
        <div className="space-y-4">
          {workflows.length > 0 ? workflows.map((wf, i) => (
            <div key={i} className="bg-white/[.06] border border-white/10 rounded-xl p-5">
              <div className="flex justify-between items-center mb-3">
                <h4 className="text-white font-medium text-sm">{wf.workflow_name}</h4>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300`}>{(wf.workflow_status || 'active').toUpperCase()}</span>
              </div>
              <div className="flex gap-6 text-xs text-slate-400 mb-3">
                <span>Steps: {wf.automation_steps?.length ?? 0}</span>
                <span>Triggers: {wf.trigger_conditions?.length ?? 0}</span>
                <span>Created: {new Date(wf.created_at).toLocaleDateString()}</span>
              </div>
              {wf.automation_steps?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {wf.automation_steps.slice(0, 5).map((s, si) => (
                    <span key={si} className={`px-2.5 py-1 rounded-lg text-xs ${s.auto_execute ? 'bg-sky-500/20 text-sky-300' : 'bg-slate-500/20 text-slate-400'}`}>
                      {s.step?.replace(/_/g, ' ')} {s.auto_execute ? '(Auto)' : '(Manual)'}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )) : (
            <p className="text-slate-400 text-sm text-center py-8">No workflows found. Workflows are created when you generate comprehensive licenses.</p>
          )}
        </div>
      )}

      {/* Compliance Docs */}
      {subTab === 'compliance' && !loading && (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4 mb-4">
            <StatCard label="Total Documents" value={compDocs.length} color="text-white" />
            <StatCard label="Pending Review" value={compDocs.filter(d => d.legal_review_status === 'pending').length} color="text-amber-400" />
            <StatCard label="Approved" value={compDocs.filter(d => d.legal_review_status === 'approved').length} color="text-emerald-400" />
          </div>
          {compDocs.length > 0 ? compDocs.map((doc, i) => (
            <div key={i} className="bg-white/[.06] border border-white/10 rounded-xl p-5">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-white font-medium text-sm">{doc.document_type?.replace(/_/g, ' ').toUpperCase()}</h4>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${doc.legal_review_status === 'approved' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}`}>{doc.legal_review_status?.toUpperCase()}</span>
              </div>
              <div className="flex gap-4 text-xs text-slate-400">
                <span>Platform: {doc.platform_id}</span>
                <span>Requirements: {doc.compliance_requirements?.length ?? 0}</span>
                <span>Created: {new Date(doc.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          )) : (
            <p className="text-slate-400 text-sm text-center py-8">No compliance documents found.</p>
          )}
        </div>
      )}
    </div>
  );
};

/* ─── Shared UI Components ─── */
const StatCard = ({ label, value, color = 'text-white' }) => (
  <div className="bg-white/[.06] border border-white/10 rounded-xl p-4 text-center">
    <div className={`text-2xl font-bold ${color} mb-1`}>{value}</div>
    <div className="text-slate-400 text-xs">{label}</div>
  </div>
);

const InfoRow = ({ label, value, accent }) => (
  <div className="flex justify-between items-center gap-2">
    <span className="text-slate-400">{label}</span>
    <span className={`font-medium text-right ${accent ? 'text-emerald-400' : 'text-white'}`}>{value ?? 'N/A'}</span>
  </div>
);

const FeatureBadge = ({ label }) => (
  <span className="bg-emerald-500/20 text-emerald-200 px-2.5 py-1 rounded-lg text-xs font-medium">{label}</span>
);

const LoadingState = ({ text }) => (
  <div className="flex items-center justify-center py-12 gap-2 text-slate-400">
    <Loader2 size={18} className="animate-spin" /> <span className="text-sm">{text}</span>
  </div>
);

const ErrorState = ({ message }) => (
  <div className="flex items-center justify-center py-12 gap-2 text-red-400">
    <AlertCircle size={18} /> <span className="text-sm">{message}</span>
  </div>
);

const ErrorBanner = ({ message, onDismiss }) => (
  <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-xl text-sm flex justify-between items-center">
    <span>{message}</span>
    <button onClick={onDismiss} className="text-red-400 hover:text-red-200"><X size={14} /></button>
  </div>
);

/* ─── Quick Actions Panel ─── */
const QuickActionsPanel = ({ onSwitchTab, onActionComplete }) => {
  const [summary, setSummary] = useState(null);
  const [actionLoading, setActionLoading] = useState('');

  useEffect(() => {
    fetch(`${API}/api/gs1/quick-actions/summary`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setSummary(d); })
      .catch(() => {});
  }, []);

  const runAction = async (key, url, method = 'POST') => {
    setActionLoading(key);
    try {
      const res = await fetch(`${API}${url}`, { method, headers: getAuthHeaders() });
      if (res.ok) {
        const data = await res.json();
        onActionComplete(key, data);
      } else {
        onActionComplete(key, null, 'Action failed');
      }
    } catch {
      onActionComplete(key, null, 'Network error');
    } finally {
      setActionLoading('');
    }
  };

  const actions = [
    {
      key: 'create-product',
      label: 'Create Product',
      desc: 'Register a new UPC/GTIN product',
      icon: <Plus size={18} />,
      badge: summary?.products_count,
      badgeLabel: 'products',
      color: 'from-emerald-600/20 to-emerald-500/5 border-emerald-500/20 hover:border-emerald-400/40',
      iconBg: 'bg-emerald-500/20 text-emerald-400',
      onClick: () => onSwitchTab('products'),
    },
    {
      key: 'generate-barcode',
      label: 'Generate Barcode',
      desc: 'Create UPC barcode images',
      icon: <BarChart3 size={18} />,
      badge: summary?.digital_links_count,
      badgeLabel: 'links',
      color: 'from-sky-600/20 to-sky-500/5 border-sky-500/20 hover:border-sky-400/40',
      iconBg: 'bg-sky-500/20 text-sky-400',
      onClick: () => onSwitchTab('products'),
    },
    {
      key: 'license-all',
      label: 'License All Platforms',
      desc: 'Activate licenses for all platforms',
      icon: <Scale size={18} />,
      badge: summary?.active_licenses,
      badgeLabel: 'active',
      color: 'from-purple-600/20 to-purple-500/5 border-purple-500/20 hover:border-purple-400/40',
      iconBg: 'bg-purple-500/20 text-purple-400',
      onClick: () => runAction('license-all', '/api/licensing/initialize-all-platforms'),
      isAction: true,
    },
    {
      key: 'compliance-check',
      label: 'Compliance Check',
      desc: 'Review pending compliance docs',
      icon: <ShieldCheck size={18} />,
      badge: summary?.pending_reviews,
      badgeLabel: 'pending',
      color: 'from-amber-600/20 to-amber-500/5 border-amber-500/20 hover:border-amber-400/40',
      iconBg: 'bg-amber-500/20 text-amber-400',
      onClick: () => onSwitchTab('agreements'),
    },
    {
      key: 'business-ids',
      label: 'Business Identifiers',
      desc: 'Manage mandatory GS1 & business IDs',
      icon: <Building2 size={18} />,
      badge: summary?.identifiers_count,
      badgeLabel: 'configured',
      color: 'from-rose-600/20 to-rose-500/5 border-rose-500/20 hover:border-rose-400/40',
      iconBg: 'bg-rose-500/20 text-rose-400',
      onClick: () => { window.location.href = '/business-identifiers'; },
      isNav: true,
    },
    {
      key: 'csv-import',
      label: 'CSV Catalog Import',
      desc: 'Bulk import catalog assets via CSV',
      icon: <Download size={18} className="rotate-180" />,
      color: 'from-teal-600/20 to-teal-500/5 border-teal-500/20 hover:border-teal-400/40',
      iconBg: 'bg-teal-500/20 text-teal-400',
      onClick: () => { window.location.href = '/catalog-import'; },
      isNav: true,
    },
    {
      key: 'gen-licenses',
      label: 'Generate Comprehensive',
      desc: 'Create all platform license agreements',
      icon: <FileText size={18} />,
      badge: summary?.compliance_docs,
      badgeLabel: 'docs',
      color: 'from-indigo-600/20 to-indigo-500/5 border-indigo-500/20 hover:border-indigo-400/40',
      iconBg: 'bg-indigo-500/20 text-indigo-400',
      onClick: () => runAction('gen-licenses', '/api/comprehensive-licensing/generate-all-platform-licenses'),
      isAction: true,
    },
    {
      key: 'view-rates',
      label: 'Statutory Rates',
      desc: 'View current compensation rates',
      icon: <DollarSign size={18} />,
      color: 'from-lime-600/20 to-lime-500/5 border-lime-500/20 hover:border-lime-400/40',
      iconBg: 'bg-lime-500/20 text-lime-400',
      onClick: () => onSwitchTab('compensation'),
    },
  ];

  return (
    <div className="mb-8" data-testid="quick-actions-panel">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
          <RefreshCw size={16} className="text-purple-400" />
          Quick Actions
        </h2>
        <span className="text-xs text-slate-500 uppercase tracking-wider">GS1 Hub Shortcuts</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {actions.map(a => (
          <button
            key={a.key}
            onClick={a.onClick}
            disabled={actionLoading === a.key}
            className={`group relative bg-gradient-to-br ${a.color} border rounded-xl p-4 text-left transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-60`}
            data-testid={`quick-action-${a.key}`}
          >
            {actionLoading === a.key && (
              <div className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-xl z-10">
                <Loader2 size={20} className="animate-spin text-white" />
              </div>
            )}
            <div className="flex items-start justify-between mb-2">
              <div className={`${a.iconBg} p-2 rounded-lg`}>
                {a.icon}
              </div>
              {a.badge !== undefined && a.badge !== null && (
                <span className="text-[10px] text-slate-400 font-mono bg-white/[.06] px-1.5 py-0.5 rounded-md">
                  {a.badge} {a.badgeLabel}
                </span>
              )}
            </div>
            <div className="text-sm font-medium text-white group-hover:text-white/90 leading-tight">{a.label}</div>
            <div className="text-[11px] text-slate-500 mt-0.5 leading-snug">{a.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

/* ─── Main Hub Page ─── */
export default function GS1LicensingHub() {
  const [activeTab, setActiveTab] = useState('overview');
  const [actionResult, setActionResult] = useState(null);

  const handleActionComplete = (key, data, error) => {
    if (error) {
      setActionResult({ type: 'error', message: error });
    } else if (key === 'license-all') {
      setActionResult({ type: 'success', message: `Licensed ${data?.platforms_licensed ?? 0} platforms successfully!` });
      setActiveTab('licensing');
    } else if (key === 'gen-licenses') {
      setActionResult({ type: 'success', message: `Generated ${data?.platforms_licensed ?? 0} comprehensive license agreements!` });
      setActiveTab('agreements');
    }
    setTimeout(() => setActionResult(null), 5000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a14] text-white" data-testid="gs1-licensing-hub">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            GS1 & Licensing Hub
          </h1>
          <p className="text-slate-400 mt-1 text-sm sm:text-base">
            Unified management for GS1 registry, platform licensing, compensation & compliance
          </p>
        </div>

        {/* Quick Actions Panel */}
        <QuickActionsPanel
          onSwitchTab={setActiveTab}
          onActionComplete={handleActionComplete}
        />

        {/* Action Result Banner */}
        {actionResult && (
          <div
            className={`mb-6 px-4 py-3 rounded-xl text-sm flex justify-between items-center transition-all ${
              actionResult.type === 'success'
                ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-300'
                : 'bg-red-500/10 border border-red-500/30 text-red-300'
            }`}
            data-testid="quick-action-result"
          >
            <span>{actionResult.message}</span>
            <button onClick={() => setActionResult(null)} className="ml-3 opacity-60 hover:opacity-100"><X size={14} /></button>
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-white/[.04] border border-white/10 rounded-xl p-1 flex flex-wrap gap-0.5 h-auto w-full justify-start mb-6">
            <TabsTrigger value="overview" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white text-slate-400 rounded-lg px-4 py-2 text-sm" data-testid="tab-overview">
              <BarChart3 size={14} className="mr-1.5" /> Overview
            </TabsTrigger>
            <TabsTrigger value="gs1-business" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white text-slate-400 rounded-lg px-4 py-2 text-sm" data-testid="tab-gs1-business">
              <Building2 size={14} className="mr-1.5" /> GS1 & Business
            </TabsTrigger>
            <TabsTrigger value="products" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white text-slate-400 rounded-lg px-4 py-2 text-sm" data-testid="tab-products">
              <Package size={14} className="mr-1.5" /> Products & Barcodes
            </TabsTrigger>
            <TabsTrigger value="licensing" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white text-slate-400 rounded-lg px-4 py-2 text-sm" data-testid="tab-licensing">
              <Scale size={14} className="mr-1.5" /> Platform Licensing
            </TabsTrigger>
            <TabsTrigger value="compensation" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white text-slate-400 rounded-lg px-4 py-2 text-sm" data-testid="tab-compensation">
              <DollarSign size={14} className="mr-1.5" /> Compensation
            </TabsTrigger>
            <TabsTrigger value="agreements" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white text-slate-400 rounded-lg px-4 py-2 text-sm" data-testid="tab-agreements">
              <FileText size={14} className="mr-1.5" /> Agreements & Compliance
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview"><OverviewTab /></TabsContent>
          <TabsContent value="gs1-business"><GS1BusinessTab /></TabsContent>
          <TabsContent value="products"><ProductsBarcodesTab /></TabsContent>
          <TabsContent value="licensing"><PlatformLicensingTab /></TabsContent>
          <TabsContent value="compensation"><CompensationTab /></TabsContent>
          <TabsContent value="agreements"><AgreementsComplianceTab /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
