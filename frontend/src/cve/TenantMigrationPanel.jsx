import React, { useState, useEffect, useCallback } from "react";
import { Database, ArrowRight, CheckCircle2, AlertTriangle, RefreshCw, Server } from "lucide-react";
import { TENANT_API, fetcher } from "./shared";

export const TenantMigrationPanel = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [migrating, setMigrating] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedTenant, setSelectedTenant] = useState("");

  const fetchAnalysis = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetcher(`${TENANT_API}/migration-analysis`);
      setAnalysis(data);
      if (data.available_tenants?.length > 0 && !selectedTenant) {
        const defaultTenant = data.available_tenants.find(t => t.slug === "default");
        setSelectedTenant(defaultTenant?.id || data.available_tenants[0].id);
      }
    } catch (e) {
      console.error("Migration analysis failed:", e);
    }
    setLoading(false);
  }, [selectedTenant]);

  useEffect(() => { fetchAnalysis(); }, [fetchAnalysis]);

  const handleMigrate = async () => {
    if (!selectedTenant) return;
    if (!window.confirm("This will assign a tenant_id to all legacy documents. Proceed?")) return;
    setMigrating(true);
    setResult(null);
    try {
      const data = await fetcher(`${TENANT_API}/migrate-data`, {
        method: "POST",
        body: JSON.stringify({ target_tenant_id: selectedTenant }),
      });
      setResult(data);
      fetchAnalysis();
    } catch (e) {
      setResult({ success: false, error: e.message });
    }
    setMigrating(false);
  };

  if (loading) {
    return (
      <div data-testid="migration-loading" className="text-slate-400 text-center py-12">
        <RefreshCw className="w-5 h-5 animate-spin inline mr-2" />Analyzing collections...
      </div>
    );
  }

  if (!analysis) return null;

  const collections = Object.entries(analysis.collections || {});
  const collectionsWithLegacy = collections.filter(([, v]) => v.legacy_docs > 0);

  return (
    <div data-testid="tenant-migration-panel" className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" /> Tenant Data Migration
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Assign tenant ownership to legacy documents missing a tenant_id
          </p>
        </div>
        <button data-testid="refresh-analysis-btn" onClick={fetchAnalysis} className="flex items-center gap-2 text-slate-400 hover:text-white text-sm transition-colors">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div data-testid="total-docs-card" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <div className="text-slate-400 text-sm mb-1">Total Documents</div>
          <div className="text-2xl font-bold text-white">{analysis.total_documents}</div>
        </div>
        <div data-testid="legacy-docs-card" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <div className="text-slate-400 text-sm mb-1">Legacy (No Tenant)</div>
          <div className={`text-2xl font-bold ${analysis.total_legacy_documents > 0 ? "text-amber-400" : "text-emerald-400"}`}>
            {analysis.total_legacy_documents}
          </div>
        </div>
        <div data-testid="migration-status-card" className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
          <div className="text-slate-400 text-sm mb-1">Migration Status</div>
          {analysis.migration_needed ? (
            <div className="flex items-center gap-2 text-amber-400 text-lg font-bold">
              <AlertTriangle className="w-5 h-5" /> Needed
            </div>
          ) : (
            <div className="flex items-center gap-2 text-emerald-400 text-lg font-bold">
              <CheckCircle2 className="w-5 h-5" /> Complete
            </div>
          )}
        </div>
      </div>

      {/* Collection Breakdown Table */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-700/50">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Server className="w-4 h-4 text-slate-400" /> Collection Breakdown
          </h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700/40">
              <th className="text-left px-4 py-2.5 text-slate-400 font-medium">Collection</th>
              <th className="text-right px-4 py-2.5 text-slate-400 font-medium">Total</th>
              <th className="text-right px-4 py-2.5 text-slate-400 font-medium">Legacy</th>
              <th className="text-right px-4 py-2.5 text-slate-400 font-medium">Migrated</th>
              <th className="text-center px-4 py-2.5 text-slate-400 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {collections.map(([name, data]) => (
              <tr key={name} data-testid={`collection-row-${name}`} className="border-b border-slate-700/20 hover:bg-slate-700/10">
                <td className="px-4 py-2.5 text-slate-300 font-mono text-xs">{name}</td>
                <td className="px-4 py-2.5 text-right text-white">{data.total}</td>
                <td className={`px-4 py-2.5 text-right ${data.legacy_docs > 0 ? "text-amber-400 font-medium" : "text-slate-500"}`}>
                  {data.legacy_docs}
                </td>
                <td className="px-4 py-2.5 text-right text-emerald-400">{data.already_migrated}</td>
                <td className="px-4 py-2.5 text-center">
                  {data.legacy_docs === 0 ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-emerald-500/20 text-emerald-300">
                      <CheckCircle2 className="w-3 h-3" /> Done
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-amber-500/20 text-amber-300">
                      <AlertTriangle className="w-3 h-3" /> Pending
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Migration Action */}
      {analysis.migration_needed && (
        <div data-testid="migration-action-section" className="bg-slate-800/60 border border-amber-500/30 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-white">Run Migration</h3>
          <p className="text-xs text-slate-400">
            {collectionsWithLegacy.length} collection(s) have legacy documents.
            Select a target tenant to assign ownership to all unassigned documents.
          </p>
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <label className="text-xs text-slate-400">Target Tenant:</label>
              <select
                data-testid="target-tenant-select"
                value={selectedTenant}
                onChange={(e) => setSelectedTenant(e.target.value)}
                className="bg-slate-700 border border-slate-600 text-white text-sm rounded-lg px-3 py-1.5 focus:ring-cyan-500 focus:border-cyan-500"
              >
                {analysis.available_tenants?.map((t) => (
                  <option key={t.id} value={t.id}>{t.name} ({t.plan})</option>
                ))}
              </select>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 hidden sm:block" />
            <button
              data-testid="run-migration-btn"
              onClick={handleMigrate}
              disabled={migrating || !selectedTenant}
              className="flex items-center gap-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              {migrating ? (
                <><RefreshCw className="w-4 h-4 animate-spin" /> Migrating...</>
              ) : (
                <><Database className="w-4 h-4" /> Run Migration</>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Migration Result */}
      {result && (
        <div data-testid="migration-result" className={`rounded-xl p-5 border ${result.success ? "bg-emerald-900/20 border-emerald-500/30" : "bg-red-900/20 border-red-500/30"}`}>
          {result.success ? (
            <>
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-semibold text-emerald-300">Migration Successful</h3>
              </div>
              <p className="text-xs text-slate-300 mb-3">
                Migrated <span className="font-bold text-white">{result.total_migrated}</span> documents
                to tenant <span className="font-bold text-white">{result.target_tenant?.name}</span>
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {Object.entries(result.collections || {}).filter(([, v]) => v.migrated > 0).map(([name, data]) => (
                  <div key={name} className="bg-slate-800/40 rounded-lg px-3 py-2 text-xs">
                    <div className="text-slate-400 font-mono truncate">{name}</div>
                    <div className="text-emerald-300 font-bold">{data.migrated} migrated</div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <span className="text-red-300 text-sm">Migration failed: {result.error}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
