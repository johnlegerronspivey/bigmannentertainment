import React, { useState, useEffect, useCallback } from "react";
import { api } from "../utils/apiClient";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  DollarSign, TrendingUp, BarChart3, Music, Plus, RefreshCw,
  ArrowUpRight, ArrowDownRight, ChevronDown, X, Filter, Layers
} from "lucide-react";
import { toast } from "sonner";

const SOURCE_COLORS = {
  streaming: "#8b5cf6",
  ad_revenue: "#f59e0b",
  sync_licensing: "#10b981",
  other: "#6b7280",
};

const PLATFORM_ICONS = {
  spotify: "#1DB954",
  apple_music: "#FC3C44",
  youtube: "#FF0000",
  youtube_music: "#FF0000",
  tidal: "#000000",
  amazon_music: "#00A8E1",
  soundcloud: "#FF5500",
  tiktok: "#25F4EE",
  instagram: "#E4405F",
  deezer: "#FEAA2D",
};

function MiniBarChart({ data, height = 80 }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map((d) => d.amount), 1);
  const barW = Math.max(100 / data.length - 1, 4);
  return (
    <div data-testid="revenue-trend-chart" className="flex items-end gap-[2px]" style={{ height }}>
      {data.map((d, i) => {
        const h = Math.max((d.amount / max) * height, 2);
        return (
          <div key={i} className="group relative flex flex-col items-center" style={{ width: `${barW}%` }}>
            <div
              className="w-full rounded-t bg-purple-500/80 hover:bg-purple-400 transition-colors"
              style={{ height: h }}
            />
            <div className="absolute -top-8 hidden group-hover:block bg-slate-800 text-white text-[10px] px-2 py-0.5 rounded whitespace-nowrap z-10 border border-slate-600">
              {d.month}: ${d.amount.toLocaleString()}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function SourcePie({ sources }) {
  if (!sources || sources.length === 0) return null;
  const total = sources.reduce((s, x) => s + x.total, 0) || 1;
  let cum = 0;
  const segments = sources.map((s) => {
    const pct = (s.total / total) * 100;
    const start = cum;
    cum += pct;
    return { ...s, pct, start };
  });
  return (
    <div data-testid="revenue-source-pie" className="flex items-center gap-6">
      <svg viewBox="0 0 36 36" className="w-24 h-24">
        {segments.map((seg, i) => {
          const color = SOURCE_COLORS[seg.source] || SOURCE_COLORS.other;
          return (
            <circle
              key={i}
              r="15.9"
              cx="18"
              cy="18"
              fill="none"
              stroke={color}
              strokeWidth="5"
              strokeDasharray={`${seg.pct} ${100 - seg.pct}`}
              strokeDashoffset={-seg.start}
              className="transition-all duration-500"
            />
          );
        })}
      </svg>
      <div className="flex flex-col gap-1.5">
        {segments.map((seg, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span
              className="w-3 h-3 rounded-sm"
              style={{ background: SOURCE_COLORS[seg.source] || SOURCE_COLORS.other }}
            />
            <span className="text-slate-300 capitalize">{seg.source.replace(/_/g, " ")}</span>
            <span className="text-slate-400 ml-auto">{seg.pct.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function RevenueTrackingPage() {
  const [overview, setOverview] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [txTotal, setTxTotal] = useState(0);
  const [platformDetail, setPlatformDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [txLoading, setTxLoading] = useState(false);
  const [tab, setTab] = useState("overview");
  const [filterPlatform, setFilterPlatform] = useState("");
  const [filterSource, setFilterSource] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [addForm, setAddForm] = useState({
    platform_id: "spotify",
    platform_name: "Spotify",
    content_id: "",
    content_title: "",
    source: "streaming",
    amount: "",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const PLATFORM_OPTIONS = [
    { id: "spotify", name: "Spotify" },
    { id: "apple_music", name: "Apple Music" },
    { id: "youtube", name: "YouTube" },
    { id: "youtube_music", name: "YouTube Music" },
    { id: "tidal", name: "TIDAL" },
    { id: "amazon_music", name: "Amazon Music" },
    { id: "soundcloud", name: "SoundCloud" },
    { id: "tiktok", name: "TikTok" },
    { id: "instagram", name: "Instagram" },
    { id: "deezer", name: "Deezer" },
  ];
  const SOURCE_OPTIONS = ["streaming", "ad_revenue", "sync_licensing", "other"];

  const loadOverview = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get("/revenue/overview");
      setOverview(data);
    } catch (e) {
      toast.error("Failed to load revenue overview");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTransactions = useCallback(async () => {
    setTxLoading(true);
    try {
      let q = "/revenue/transactions?limit=50";
      if (filterPlatform) q += `&platform_id=${filterPlatform}`;
      if (filterSource) q += `&source=${filterSource}`;
      const data = await api.get(q);
      setTransactions(data.transactions || []);
      setTxTotal(data.total || 0);
    } catch {
      toast.error("Failed to load transactions");
    } finally {
      setTxLoading(false);
    }
  }, [filterPlatform, filterSource]);

  const loadPlatformDetail = async (pid) => {
    try {
      const data = await api.get(`/revenue/platform/${pid}`);
      setPlatformDetail(data);
    } catch {
      toast.error("Failed to load platform detail");
    }
  };

  useEffect(() => {
    loadOverview();
  }, [loadOverview]);

  useEffect(() => {
    if (tab === "transactions") loadTransactions();
  }, [tab, loadTransactions]);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!addForm.amount || isNaN(addForm.amount) || Number(addForm.amount) <= 0) {
      toast.error("Enter a valid amount");
      return;
    }
    setSubmitting(true);
    try {
      await api.post("/revenue/record", {
        ...addForm,
        amount: parseFloat(addForm.amount),
      });
      toast.success("Revenue recorded");
      setShowAddForm(false);
      setAddForm({ platform_id: "spotify", platform_name: "Spotify", content_id: "", content_title: "", source: "streaming", amount: "", description: "" });
      loadOverview();
      if (tab === "transactions") loadTransactions();
    } catch {
      toast.error("Failed to record revenue");
    } finally {
      setSubmitting(false);
    }
  };

  const prevMonth = overview?.monthly_trend?.length >= 2
    ? overview.monthly_trend[overview.monthly_trend.length - 2].amount
    : 0;
  const currMonth = overview?.monthly_trend?.length >= 1
    ? overview.monthly_trend[overview.monthly_trend.length - 1].amount
    : 0;
  const monthChange = prevMonth > 0 ? ((currMonth - prevMonth) / prevMonth) * 100 : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" />
      </div>
    );
  }

  return (
    <div data-testid="revenue-tracking-page" className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
          <div>
            <h1 data-testid="revenue-page-title" className="text-3xl sm:text-4xl font-bold tracking-tight">
              Revenue Tracking
            </h1>
            <p className="text-slate-400 mt-1 text-sm">
              {overview?.period || "Last 12 months"} &middot; {overview?.total_transactions || 0} transactions
            </p>
          </div>
          <div className="flex gap-2">
            <button
              data-testid="revenue-refresh-btn"
              onClick={loadOverview}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm border border-slate-700 transition-colors"
            >
              <RefreshCw size={14} /> Refresh
            </button>
            <button
              data-testid="revenue-add-btn"
              onClick={() => setShowAddForm(!showAddForm)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-sm font-medium transition-colors"
            >
              <Plus size={14} /> Record Revenue
            </button>
          </div>
        </div>

        {/* Add Revenue Form */}
        {showAddForm && (
          <Card className="bg-slate-900 border-slate-700 mb-6">
            <CardHeader className="pb-3 flex flex-row items-center justify-between">
              <CardTitle className="text-lg text-white">Record New Revenue</CardTitle>
              <button onClick={() => setShowAddForm(false)} className="text-slate-400 hover:text-white">
                <X size={18} />
              </button>
            </CardHeader>
            <CardContent>
              <form data-testid="revenue-add-form" onSubmit={handleAdd} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Platform</label>
                  <select
                    data-testid="revenue-form-platform"
                    value={addForm.platform_id}
                    onChange={(e) => {
                      const opt = PLATFORM_OPTIONS.find((p) => p.id === e.target.value);
                      setAddForm({ ...addForm, platform_id: e.target.value, platform_name: opt?.name || e.target.value });
                    }}
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white"
                  >
                    {PLATFORM_OPTIONS.map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Source</label>
                  <select
                    data-testid="revenue-form-source"
                    value={addForm.source}
                    onChange={(e) => setAddForm({ ...addForm, source: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white"
                  >
                    {SOURCE_OPTIONS.map((s) => (
                      <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Amount (USD)</label>
                  <input
                    data-testid="revenue-form-amount"
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={addForm.amount}
                    onChange={(e) => setAddForm({ ...addForm, amount: e.target.value })}
                    placeholder="0.00"
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Content Title</label>
                  <input
                    data-testid="revenue-form-content-title"
                    type="text"
                    value={addForm.content_title}
                    onChange={(e) => setAddForm({ ...addForm, content_title: e.target.value })}
                    placeholder="e.g. Summer Vibes"
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Description</label>
                  <input
                    data-testid="revenue-form-description"
                    type="text"
                    value={addForm.description}
                    onChange={(e) => setAddForm({ ...addForm, description: e.target.value })}
                    placeholder="Optional note"
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm text-white"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    data-testid="revenue-form-submit"
                    type="submit"
                    disabled={submitting}
                    className="w-full px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-sm font-medium disabled:opacity-50 transition-colors"
                  >
                    {submitting ? "Saving..." : "Save"}
                  </button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-slate-900 p-1 rounded-lg w-fit border border-slate-700">
          {[
            { id: "overview", label: "Overview", icon: BarChart3 },
            { id: "platforms", label: "Platforms", icon: Layers },
            { id: "transactions", label: "Transactions", icon: DollarSign },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              data-testid={`revenue-tab-${id}`}
              onClick={() => setTab(id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                tab === id ? "bg-purple-600 text-white" : "text-slate-400 hover:text-white hover:bg-slate-800"
              }`}
            >
              <Icon size={14} /> {label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {tab === "overview" && overview && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-slate-900 border-slate-700">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">Total Revenue</span>
                    <DollarSign size={16} className="text-purple-400" />
                  </div>
                  <p data-testid="revenue-total" className="text-2xl font-bold text-white">
                    ${overview.total_revenue?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </p>
                  <span className="text-xs text-slate-500">{overview.currency}</span>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-700">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">This Month</span>
                    <TrendingUp size={16} className="text-emerald-400" />
                  </div>
                  <p data-testid="revenue-this-month" className="text-2xl font-bold text-white">
                    ${currMonth?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </p>
                  <span className={`text-xs flex items-center gap-0.5 ${monthChange >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {monthChange >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                    {Math.abs(monthChange).toFixed(1)}% vs last month
                  </span>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-700">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">Platforms</span>
                    <Layers size={16} className="text-amber-400" />
                  </div>
                  <p data-testid="revenue-platform-count" className="text-2xl font-bold text-white">
                    {overview.by_platform?.length || 0}
                  </p>
                  <span className="text-xs text-slate-500">Active platforms</span>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-700">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-slate-400 uppercase tracking-wider">Transactions</span>
                    <BarChart3 size={16} className="text-cyan-400" />
                  </div>
                  <p data-testid="revenue-tx-count" className="text-2xl font-bold text-white">
                    {overview.total_transactions}
                  </p>
                  <span className="text-xs text-slate-500">{overview.period}</span>
                </CardContent>
              </Card>
            </div>

            {/* Monthly Trend + Source Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-900 border-slate-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base text-white">Monthly Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <MiniBarChart data={overview.monthly_trend} height={120} />
                  <div className="flex justify-between mt-2 text-[10px] text-slate-500">
                    {overview.monthly_trend?.map((d, i) =>
                      i % 2 === 0 ? <span key={i}>{d.month.slice(5)}</span> : <span key={i} />
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-900 border-slate-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base text-white">Revenue by Source</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-center">
                  <SourcePie sources={overview.by_source} />
                </CardContent>
              </Card>
            </div>

            {/* Top Earning Content */}
            {overview.top_earning_content?.length > 0 && (
              <Card className="bg-slate-900 border-slate-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base text-white flex items-center gap-2">
                    <Music size={16} className="text-purple-400" /> Top Earning Content
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {overview.top_earning_content.map((c, i) => {
                      const pct = overview.total_revenue > 0 ? (c.total / overview.total_revenue) * 100 : 0;
                      return (
                        <div key={i} data-testid={`top-content-${i}`} className="flex items-center gap-3">
                          <span className="text-xs text-slate-500 w-5 text-right">{i + 1}</span>
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm text-white">{c.title}</span>
                              <span className="text-sm font-medium text-purple-300">${c.total.toLocaleString()}</span>
                            </div>
                            <div className="h-1 rounded-full bg-slate-800 overflow-hidden">
                              <div
                                className="h-full rounded-full bg-purple-500 transition-all duration-500"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Platforms Tab */}
        {tab === "platforms" && overview && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {overview.by_platform?.map((p) => (
                <Card
                  key={p.platform_id}
                  data-testid={`platform-card-${p.platform_id}`}
                  className="bg-slate-900 border-slate-700 hover:border-purple-500/40 transition-colors cursor-pointer"
                  onClick={() => loadPlatformDetail(p.platform_id)}
                >
                  <CardContent className="p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ background: PLATFORM_ICONS[p.platform_id] || "#8b5cf6" }}
                      />
                      <span className="text-sm font-medium text-white">{p.platform_name}</span>
                    </div>
                    <p className="text-xl font-bold text-white mb-1">
                      ${p.total.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">{p.count} transactions</span>
                      <span className="text-purple-400">{p.percentage}%</span>
                    </div>
                    <div className="mt-2 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-purple-500 transition-all duration-500"
                        style={{ width: `${p.percentage}%` }}
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Platform Detail Modal */}
            {platformDetail && (
              <Card className="bg-slate-900 border-purple-500/30">
                <CardHeader className="pb-2 flex flex-row items-center justify-between">
                  <CardTitle className="text-base text-white">
                    {platformDetail.platform_id} — Detail
                  </CardTitle>
                  <button
                    data-testid="close-platform-detail"
                    onClick={() => setPlatformDetail(null)}
                    className="text-slate-400 hover:text-white"
                  >
                    <X size={16} />
                  </button>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-slate-400">Total Revenue</p>
                      <p className="text-lg font-bold text-white">${platformDetail.total_revenue?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400">Transactions</p>
                      <p className="text-lg font-bold text-white">{platformDetail.transaction_count}</p>
                    </div>
                    {Object.entries(platformDetail.by_source || {}).map(([src, amt]) => (
                      <div key={src}>
                        <p className="text-xs text-slate-400 capitalize">{src.replace(/_/g, " ")}</p>
                        <p className="text-lg font-bold text-white">${amt.toLocaleString()}</p>
                      </div>
                    ))}
                  </div>
                  {platformDetail.recent_transactions?.length > 0 && (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-slate-700 text-slate-400 text-xs">
                            <th className="text-left py-2 pr-4">Date</th>
                            <th className="text-left py-2 pr-4">Content</th>
                            <th className="text-left py-2 pr-4">Source</th>
                            <th className="text-right py-2">Amount</th>
                          </tr>
                        </thead>
                        <tbody>
                          {platformDetail.recent_transactions.slice(0, 10).map((tx, i) => (
                            <tr key={i} className="border-b border-slate-800 text-slate-300">
                              <td className="py-2 pr-4 text-xs">{tx.date?.slice(0, 10)}</td>
                              <td className="py-2 pr-4">{tx.content_title || "—"}</td>
                              <td className="py-2 pr-4 capitalize">{tx.source?.replace(/_/g, " ")}</td>
                              <td className="py-2 text-right font-medium text-white">${tx.amount?.toFixed(2)}</td>
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
        )}

        {/* Transactions Tab */}
        {tab === "transactions" && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-wrap gap-3 items-center">
              <div className="flex items-center gap-1.5 text-xs text-slate-400">
                <Filter size={12} /> Filters:
              </div>
              <select
                data-testid="tx-filter-platform"
                value={filterPlatform}
                onChange={(e) => setFilterPlatform(e.target.value)}
                className="bg-slate-800 border border-slate-600 rounded px-3 py-1.5 text-sm text-white"
              >
                <option value="">All Platforms</option>
                {PLATFORM_OPTIONS.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
              <select
                data-testid="tx-filter-source"
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
                className="bg-slate-800 border border-slate-600 rounded px-3 py-1.5 text-sm text-white"
              >
                <option value="">All Sources</option>
                {SOURCE_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
                ))}
              </select>
              <span className="text-xs text-slate-500 ml-auto">{txTotal} total</span>
            </div>

            {/* Transactions Table */}
            <Card className="bg-slate-900 border-slate-700 overflow-hidden">
              <CardContent className="p-0">
                {txLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-purple-500" />
                  </div>
                ) : transactions.length === 0 ? (
                  <div className="text-center py-12 text-slate-400 text-sm">
                    No transactions found. Record your first revenue entry above.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table data-testid="revenue-transactions-table" className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-700 bg-slate-800/50 text-slate-400 text-xs uppercase tracking-wider">
                          <th className="text-left py-3 px-4">Date</th>
                          <th className="text-left py-3 px-4">Platform</th>
                          <th className="text-left py-3 px-4">Content</th>
                          <th className="text-left py-3 px-4">Source</th>
                          <th className="text-right py-3 px-4">Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {transactions.map((tx, i) => (
                          <tr key={i} data-testid={`tx-row-${i}`} className="border-b border-slate-800 hover:bg-slate-800/40 text-slate-300">
                            <td className="py-3 px-4 text-xs">{tx.date?.slice(0, 10)}</td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                <div
                                  className="w-2.5 h-2.5 rounded-full"
                                  style={{ background: PLATFORM_ICONS[tx.platform_id] || "#8b5cf6" }}
                                />
                                {tx.platform_name}
                              </div>
                            </td>
                            <td className="py-3 px-4">{tx.content_title || "—"}</td>
                            <td className="py-3 px-4 capitalize">{tx.source?.replace(/_/g, " ")}</td>
                            <td className="py-3 px-4 text-right font-medium text-white">${tx.amount?.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
