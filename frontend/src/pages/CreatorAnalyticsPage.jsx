import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../utils/apiClient";
import {
  BarChart3, Eye, Download, Heart, Users, TrendingUp, DollarSign,
  FileAudio, FileVideo, Image, MessageCircle, AlertTriangle, Clock,
  Globe, Zap, RefreshCw, ChevronDown, ChevronUp, X, MapPin,
  Smartphone, Monitor, Tablet, Tv, ArrowUpRight, ArrowDownRight
} from "lucide-react";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function CreatorAnalyticsPage() {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [contentPerf, setContentPerf] = useState([]);
  const [audience, setAudience] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");

  // New state for enhanced features
  const [anomalies, setAnomalies] = useState([]);
  const [demographics, setDemographics] = useState(null);
  const [bestTimes, setBestTimes] = useState(null);
  const [geoData, setGeoData] = useState(null);
  const [revenueOverview, setRevenueOverview] = useState(null);
  const [scanning, setScanning] = useState(false);

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    try {
      const [ov, cp, au, rv] = await Promise.all([
        api.get("/analytics/overview"),
        api.get("/analytics/content-performance"),
        api.get("/analytics/audience"),
        api.get("/analytics/revenue"),
      ]);
      setOverview(ov);
      setContentPerf(cp.items || []);
      setAudience(au);
      setRevenue(rv);

      // Load enhanced data in parallel
      Promise.all([
        api.get("/analytics/anomalies").then(d => setAnomalies(d.alerts || [])).catch(() => {}),
        api.get("/analytics/demographics").then(d => setDemographics(d)).catch(() => {}),
        api.get("/analytics/best-times").then(d => setBestTimes(d)).catch(() => {}),
        api.get("/analytics/geo").then(d => setGeoData(d)).catch(() => {}),
        api.get("/analytics/revenue/overview").then(d => setRevenueOverview(d)).catch(() => {}),
      ]);
    } catch { /* Partial load ok */ }
    finally { setLoading(false); }
  };

  const runScan = async () => {
    setScanning(true);
    try {
      const result = await api.post("/analytics/anomalies/scan");
      const alerts = await api.get("/analytics/anomalies");
      setAnomalies(alerts.alerts || []);
    } catch {}
    finally { setScanning(false); }
  };

  const dismissAnomaly = async (platformId, metric) => {
    try {
      await api.post("/analytics/anomalies/dismiss", { platform_id: platformId, metric });
      setAnomalies(prev => prev.filter(a => !(a.platform_id === platformId && a.metric === metric)));
    } catch {}
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500" />
      </div>
    );
  }

  const typeIcon = (type) => {
    if (type === "audio") return <FileAudio className="w-4 h-4 text-green-400" />;
    if (type === "video") return <FileVideo className="w-4 h-4 text-blue-400" />;
    return <Image className="w-4 h-4 text-pink-400" />;
  };

  const tabs = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "anomalies", label: "Anomaly Detection", icon: AlertTriangle },
    { id: "demographics", label: "Demographics", icon: Users },
    { id: "best_times", label: "Best Time to Post", icon: Clock },
    { id: "content", label: "Content", icon: Eye },
    { id: "revenue", label: "Revenue", icon: DollarSign },
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="analytics-page">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold" data-testid="analytics-page-title">Creator Analytics</h1>
            <p className="text-gray-400 mt-1">AI-powered insights into your content, audience, and revenue</p>
          </div>
          {anomalies.length > 0 && (
            <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-1.5" data-testid="anomaly-badge">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span className="text-amber-300 text-sm font-medium">{anomalies.length} anomal{anomalies.length === 1 ? "y" : "ies"} detected</span>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-8 border-b border-gray-800 pb-0 overflow-x-auto" data-testid="analytics-tabs">
          {tabs.map((t) => {
            const Icon = t.icon;
            return (
              <button key={t.id} onClick={() => setTab(t.id)}
                className={`flex items-center gap-2 pb-3 px-3 text-sm font-medium whitespace-nowrap transition-colors border-b-2 ${
                  tab === t.id ? "text-purple-400 border-purple-400" : "text-gray-500 hover:text-gray-300 border-transparent"
                }`}
                data-testid={`tab-${t.id}`}>
                <Icon className="w-4 h-4" />
                {t.label}
              </button>
            );
          })}
        </div>

        {/* OVERVIEW TAB */}
        {tab === "overview" && overview && (
          <div data-testid="overview-section">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard icon={<BarChart3 className="w-5 h-5 text-purple-400" />} label="Total Content" value={overview.total_content} />
              <StatCard icon={<Eye className="w-5 h-5 text-blue-400" />} label="Total Views" value={overview.engagement?.total_views || 0} />
              <StatCard icon={<Download className="w-5 h-5 text-green-400" />} label="Downloads" value={overview.engagement?.total_downloads || 0} />
              <StatCard icon={<Heart className="w-5 h-5 text-pink-400" />} label="Likes" value={overview.engagement?.total_likes || 0} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="content-by-type-card">
                <h3 className="font-semibold text-sm text-gray-300 mb-4">Content by Type</h3>
                <div className="space-y-3">
                  {Object.entries(overview.content_by_type || {}).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">{typeIcon(type)}<span className="text-sm capitalize">{type}</span></div>
                      <div className="flex items-center gap-3">
                        <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${type === "audio" ? "bg-green-500" : type === "video" ? "bg-blue-500" : "bg-pink-500"}`}
                            style={{ width: `${overview.total_content ? (count / overview.total_content) * 100 : 0}%` }} />
                        </div>
                        <span className="text-sm text-gray-400 w-8 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="quick-stats-card">
                <h3 className="font-semibold text-sm text-gray-300 mb-4">Quick Stats</h3>
                <div className="space-y-3">
                  {[
                    { icon: Users, label: "Followers", value: overview.profile_stats?.total_followers || 0 },
                    { icon: TrendingUp, label: "Streams", value: overview.profile_stats?.total_streams || 0 },
                    { icon: DollarSign, label: "Earnings", value: `$${(overview.profile_stats?.total_earnings || 0).toFixed(2)}` },
                    { icon: MessageCircle, label: "Conversations", value: overview.total_conversations || 0 },
                  ].map(({ icon: Icon, label, value }) => (
                    <div key={label} className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
                      <span className="text-sm text-gray-400 flex items-center gap-2"><Icon className="w-4 h-4" /> {label}</span>
                      <span className="font-medium">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ANOMALY DETECTION TAB */}
        {tab === "anomalies" && (
          <AnomalyDetectionPanel anomalies={anomalies} scanning={scanning} onScan={runScan} onDismiss={dismissAnomaly} />
        )}

        {/* DEMOGRAPHICS TAB */}
        {tab === "demographics" && (
          <DemographicsPanel demographics={demographics} geoData={geoData} />
        )}

        {/* BEST TIME TO POST TAB */}
        {tab === "best_times" && (
          <BestTimesPanel bestTimes={bestTimes} />
        )}

        {/* CONTENT TAB */}
        {tab === "content" && (
          <div data-testid="content-performance-section">
            <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-gray-800">
                <h3 className="font-semibold text-sm text-gray-300">Content Performance</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-gray-500 text-xs uppercase border-b border-gray-800">
                      <th className="text-left px-4 py-3">Title</th>
                      <th className="text-left px-4 py-3">Type</th>
                      <th className="text-right px-4 py-3">Views</th>
                      <th className="text-right px-4 py-3">Downloads</th>
                      <th className="text-right px-4 py-3">Likes</th>
                      <th className="text-left px-4 py-3">Visibility</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contentPerf.map((item, i) => (
                      <tr key={i} className="border-b border-gray-800/50 hover:bg-gray-800/30" data-testid="performance-row">
                        <td className="px-4 py-3 font-medium">{item.title}</td>
                        <td className="px-4 py-3"><span className="flex items-center gap-1.5 capitalize">{typeIcon(item.content_type)} {item.content_type}</span></td>
                        <td className="px-4 py-3 text-right">{item.stats?.views || 0}</td>
                        <td className="px-4 py-3 text-right">{item.stats?.downloads || 0}</td>
                        <td className="px-4 py-3 text-right">{item.stats?.likes || 0}</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${item.visibility === "public" ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}`}>
                            {item.visibility}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {contentPerf.length === 0 && (
                      <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-500">No content to analyze yet</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* REVENUE TAB */}
        {tab === "revenue" && (
          <RevenuePanel revenueOverview={revenueOverview} basicRevenue={revenue} />
        )}
      </div>
    </div>
  );
}

/* ─── ANOMALY DETECTION PANEL ─── */
function AnomalyDetectionPanel({ anomalies, scanning, onScan, onDismiss }) {
  return (
    <div data-testid="anomaly-section">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold">Anomaly Detection</h2>
          <p className="text-gray-400 text-sm mt-1">AI monitors your metrics for unusual spikes or drops</p>
        </div>
        <button onClick={onScan} disabled={scanning} data-testid="scan-anomalies-btn"
          className="flex items-center gap-2 px-4 py-2 bg-amber-600/20 border border-amber-500/30 rounded-lg text-amber-300 text-sm hover:bg-amber-600/30 disabled:opacity-50 transition-colors">
          {scanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
          {scanning ? "Scanning..." : "Run Scan"}
        </button>
      </div>

      {anomalies.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <Zap className="w-10 h-10 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 text-sm">No anomalies detected. Run a scan to analyze your metrics.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {anomalies.map((a, i) => (
            <div key={i} data-testid={`anomaly-alert-${i}`}
              className={`border rounded-xl p-4 ${a.severity === "critical" ? "bg-red-500/5 border-red-500/30" : "bg-amber-500/5 border-amber-500/30"}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${a.direction === "spike" ? "bg-red-500/10" : "bg-blue-500/10"}`}>
                    {a.direction === "spike" ? <ArrowUpRight className="w-5 h-5 text-red-400" /> : <ArrowDownRight className="w-5 h-5 text-blue-400" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-white font-medium capitalize">{a.platform_id.replace("_", " ")}</span>
                      <span className="text-gray-500">|</span>
                      <span className="text-gray-300 text-sm capitalize">{a.metric.replace("_", " ")}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${a.severity === "critical" ? "bg-red-500/10 text-red-400" : "bg-amber-500/10 text-amber-400"}`}>
                        {a.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400">
                      {a.direction === "spike" ? "Unusual increase" : "Unusual decrease"} of{" "}
                      <span className={`font-semibold ${a.direction === "spike" ? "text-red-300" : "text-blue-300"}`}>
                        {a.change_pct > 0 ? "+" : ""}{a.change_pct}%
                      </span>{" "}
                      detected. Current: {typeof a.current_value === "number" ? a.current_value.toLocaleString() : a.current_value}, baseline: {typeof a.baseline_mean === "number" ? a.baseline_mean.toLocaleString() : a.baseline_mean}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Z-score: {a.z_score} (threshold: 2.0)</p>
                  </div>
                </div>
                <button onClick={() => onDismiss(a.platform_id, a.metric)}
                  className="p-1.5 hover:bg-gray-800 rounded-lg text-gray-500 hover:text-gray-300 transition-colors" data-testid={`dismiss-anomaly-${i}`}>
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─── DEMOGRAPHICS PANEL ─── */
function DemographicsPanel({ demographics, geoData }) {
  if (!demographics) return <div className="text-gray-500 text-center py-12">Loading demographics...</div>;

  return (
    <div data-testid="demographics-section" className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={<Users className="w-5 h-5 text-purple-400" />} label="Total Followers" value={demographics.total_followers?.toLocaleString()} />
        <StatCard icon={<Globe className="w-5 h-5 text-cyan-400" />} label="Platforms" value={demographics.total_platforms} />
        <StatCard icon={<BarChart3 className="w-5 h-5 text-blue-400" />} label="Total Content" value={demographics.content_count} />
        <StatCard icon={<Eye className="w-5 h-5 text-green-400" />} label="Total Views" value={demographics.engagement_summary?.total_views?.toLocaleString() || 0} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Age Distribution */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="age-distribution">
          <h3 className="font-semibold text-sm text-gray-300 mb-4">Age Distribution</h3>
          <div className="space-y-3">
            {(demographics.age_groups || []).map((ag) => (
              <div key={ag.range} className="flex items-center gap-3">
                <span className="text-sm text-gray-400 w-12">{ag.range}</span>
                <div className="flex-1 h-6 bg-gray-800 rounded-lg overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-lg flex items-center justify-end pr-2 transition-all"
                    style={{ width: `${ag.percentage}%` }}>
                    {ag.percentage >= 10 && <span className="text-[10px] text-white font-medium">{ag.percentage}%</span>}
                  </div>
                </div>
                {ag.percentage < 10 && <span className="text-xs text-gray-500 w-10">{ag.percentage}%</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Gender Split */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="gender-split">
          <h3 className="font-semibold text-sm text-gray-300 mb-4">Gender Distribution</h3>
          <div className="flex gap-4 mb-6">
            {(demographics.gender_split || []).map((g) => (
              <div key={g.gender} className="flex-1 text-center">
                <div className="text-2xl font-bold text-white">{g.percentage}%</div>
                <div className="text-xs text-gray-500 mt-1">{g.gender}</div>
              </div>
            ))}
          </div>
          {/* Visual bar */}
          <div className="h-3 rounded-full overflow-hidden flex">
            {(demographics.gender_split || []).map((g, i) => (
              <div key={g.gender}
                className={`h-full ${i === 0 ? "bg-blue-500" : i === 1 ? "bg-pink-500" : "bg-purple-500"}`}
                style={{ width: `${g.percentage}%` }} />
            ))}
          </div>
          <div className="flex justify-between mt-2 text-[10px] text-gray-600">
            {(demographics.gender_split || []).map((g, i) => (
              <div key={g.gender} className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${i === 0 ? "bg-blue-500" : i === 1 ? "bg-pink-500" : "bg-purple-500"}`} />
                {g.gender}
              </div>
            ))}
          </div>
        </div>

        {/* Interest Categories */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="interests">
          <h3 className="font-semibold text-sm text-gray-300 mb-4">Top Interests</h3>
          <div className="space-y-3">
            {(demographics.interests || []).map((int_item) => (
              <div key={int_item.category} className="flex items-center justify-between">
                <span className="text-sm text-gray-300">{int_item.category}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${int_item.percentage}%` }} />
                  </div>
                  <span className="text-xs text-gray-500 w-12 text-right">{int_item.percentage}%</span>
                  <span className="text-[10px] text-gray-600 w-8">({int_item.affinity_index}x)</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Device Breakdown */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="devices">
          <h3 className="font-semibold text-sm text-gray-300 mb-4">Devices</h3>
          <div className="space-y-4">
            {(demographics.devices || []).map((d) => {
              const icons = { Mobile: Smartphone, Desktop: Monitor, Tablet: Tablet, "Smart TV": Tv };
              const Icon = icons[d.type] || Monitor;
              return (
                <div key={d.type} className="flex items-center gap-3">
                  <Icon className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300 w-20">{d.type}</span>
                  <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${d.percentage}%` }} />
                  </div>
                  <span className="text-xs text-gray-500 w-12 text-right">{d.percentage}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Geographic Distribution */}
      {geoData && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="geo-distribution">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-sm text-gray-300">Geographic Distribution</h3>
            <span className="text-xs text-gray-500">{geoData.total_countries} countries</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-xs text-gray-500 uppercase mb-3">By Country</h4>
              <div className="space-y-2">
                {(geoData.countries || []).slice(0, 10).map((c) => (
                  <div key={c.code} className="flex items-center gap-2">
                    <span className="text-sm w-32 text-gray-300">{c.name}</span>
                    <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${c.percentage}%` }} />
                    </div>
                    <span className="text-xs text-gray-500 w-12 text-right">{c.percentage}%</span>
                    <span className="text-xs text-gray-600 w-14 text-right">{c.listeners?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-xs text-gray-500 uppercase mb-3">Top US Cities</h4>
              <div className="space-y-2">
                {(geoData.top_cities_us || []).map((c, i) => (
                  <div key={c.city} className="flex items-center gap-2">
                    <span className="text-xs text-gray-600 w-5">{i + 1}</span>
                    <MapPin className="w-3 h-3 text-gray-500" />
                    <span className="text-sm text-gray-300 flex-1">{c.city}, {c.state}</span>
                    <span className="text-xs text-gray-500">{c.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── BEST TIME TO POST PANEL ─── */
function BestTimesPanel({ bestTimes }) {
  if (!bestTimes) return <div className="text-gray-500 text-center py-12">Loading posting time analysis...</div>;

  const heatmap = bestTimes.heatmap || [];

  return (
    <div data-testid="best-times-section" className="space-y-6">
      {/* Recommendations */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="posting-recommendations">
        <h3 className="font-semibold text-sm text-gray-300 mb-4">Recommended Posting Windows</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {(bestTimes.recommendations || []).map((r, i) => (
            <div key={i} className={`p-4 rounded-lg border ${
              r.label === "Peak" ? "bg-emerald-500/5 border-emerald-500/30" :
              r.label === "High" ? "bg-blue-500/5 border-blue-500/30" :
              "bg-gray-800/50 border-gray-700"
            }`} data-testid={`recommendation-${i}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium text-sm">{r.day}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  r.label === "Peak" ? "bg-emerald-500/10 text-emerald-400" :
                  r.label === "High" ? "bg-blue-500/10 text-blue-400" :
                  "bg-gray-700 text-gray-400"
                }`}>{r.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="text-gray-300 text-sm">{r.time_range} UTC</span>
              </div>
              <div className="mt-2 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${
                  r.label === "Peak" ? "bg-emerald-500" : r.label === "High" ? "bg-blue-500" : "bg-gray-600"
                }`} style={{ width: `${r.score}%` }} />
              </div>
              <span className="text-[10px] text-gray-600 mt-1 block">Engagement score: {r.score}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Heatmap */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="engagement-heatmap">
        <h3 className="font-semibold text-sm text-gray-300 mb-4">Engagement Heatmap (UTC)</h3>
        <div className="overflow-x-auto">
          <div className="min-w-[700px]">
            {/* Hour labels */}
            <div className="flex ml-12 mb-1">
              {[0, 3, 6, 9, 12, 15, 18, 21].map(h => (
                <span key={h} className="text-[10px] text-gray-600" style={{ width: `${100 / 8}%` }}>{h}:00</span>
              ))}
            </div>
            {/* Grid */}
            {heatmap.map((row, dayIdx) => (
              <div key={dayIdx} className="flex items-center gap-1 mb-0.5">
                <span className="text-xs text-gray-500 w-10">{DAYS[dayIdx]}</span>
                <div className="flex-1 flex gap-[1px]">
                  {row.map((val, hourIdx) => {
                    const intensity = Math.round(val * 255);
                    const bg = val >= 0.8 ? `rgba(16, 185, 129, ${val})` :
                              val >= 0.5 ? `rgba(59, 130, 246, ${val * 0.9})` :
                              val >= 0.2 ? `rgba(107, 114, 128, ${val * 0.7})` :
                              "rgba(31, 41, 55, 0.5)";
                    return (
                      <div key={hourIdx} className="flex-1 h-7 rounded-sm cursor-pointer hover:ring-1 hover:ring-white/30 transition-all"
                        style={{ backgroundColor: bg }}
                        title={`${DAYS[dayIdx]} ${hourIdx}:00 — Score: ${(val * 100).toFixed(0)}%`} />
                    );
                  })}
                </div>
              </div>
            ))}
            {/* Legend */}
            <div className="flex items-center justify-end gap-2 mt-3">
              <span className="text-[10px] text-gray-600">Low</span>
              <div className="flex gap-[1px]">
                {[0.1, 0.3, 0.5, 0.7, 0.9].map(v => (
                  <div key={v} className="w-5 h-3 rounded-sm" style={{
                    backgroundColor: v >= 0.8 ? `rgba(16, 185, 129, ${v})` :
                                    v >= 0.5 ? `rgba(59, 130, 246, ${v * 0.9})` :
                                    `rgba(107, 114, 128, ${v * 0.7})`
                  }} />
                ))}
              </div>
              <span className="text-[10px] text-gray-600">High</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── REVENUE PANEL ─── */
function RevenuePanel({ revenueOverview, basicRevenue }) {
  const data = revenueOverview;

  if (!data) return (
    <div data-testid="revenue-section">
      <StatCard icon={<DollarSign className="w-5 h-5 text-green-400" />} label="Total Earnings" value={`$${(basicRevenue?.total_earnings || 0).toFixed(2)}`} />
    </div>
  );

  return (
    <div data-testid="revenue-section" className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={<DollarSign className="w-5 h-5 text-emerald-400" />} label="Total Revenue" value={`$${data.total_revenue?.toLocaleString()}`} />
        <StatCard icon={<TrendingUp className="w-5 h-5 text-blue-400" />} label="Transactions" value={data.total_transactions} />
        <StatCard icon={<BarChart3 className="w-5 h-5 text-purple-400" />} label="Platforms" value={data.by_platform?.length || 0} />
        <StatCard icon={<DollarSign className="w-5 h-5 text-cyan-400" />} label="Period" value={data.period || "12 months"} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue by Platform */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="revenue-by-platform">
          <h3 className="font-semibold text-sm text-gray-300 mb-4">Revenue by Platform</h3>
          <div className="space-y-3">
            {(data.by_platform || []).slice(0, 10).map((p) => (
              <div key={p.platform_id} className="flex items-center gap-3">
                <span className="text-sm text-gray-300 w-28 truncate capitalize">{p.platform_name || p.platform_id}</span>
                <div className="flex-1 h-4 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full flex items-center justify-end pr-1 transition-all"
                    style={{ width: `${Math.min(p.percentage, 100)}%` }}>
                    {p.percentage >= 15 && <span className="text-[9px] text-white font-medium">${p.total}</span>}
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-16 text-right">${p.total}</span>
                <span className="text-[10px] text-gray-600 w-10 text-right">{p.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Revenue by Source */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="revenue-by-source">
          <h3 className="font-semibold text-sm text-gray-300 mb-4">Revenue by Source</h3>
          <div className="space-y-4">
            {(data.by_source || []).map((s) => {
              const colors = {
                streaming: "bg-green-500", ad_revenue: "bg-blue-500",
                sync_licensing: "bg-purple-500", downloads: "bg-cyan-500", other: "bg-gray-500"
              };
              return (
                <div key={s.source} className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${colors[s.source] || "bg-gray-500"}`} />
                  <span className="text-sm text-gray-300 capitalize flex-1">{s.source.replace("_", " ")}</span>
                  <span className="text-sm text-white font-medium">${s.total.toLocaleString()}</span>
                  <span className="text-xs text-gray-500 w-10">{s.percentage}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Monthly Trend */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="revenue-trend">
        <h3 className="font-semibold text-sm text-gray-300 mb-4">Monthly Revenue Trend</h3>
        <div className="flex items-end gap-2 h-48">
          {(data.monthly_trend || []).map((m, i) => {
            const max = Math.max(...(data.monthly_trend || []).map((r) => r.amount), 1);
            const height = (m.amount / max) * 100;
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-[10px] text-gray-500">${m.amount >= 1000 ? `${(m.amount / 1000).toFixed(1)}k` : m.amount.toFixed(0)}</span>
                <div className="w-full rounded-t transition-all hover:opacity-80 cursor-pointer"
                  style={{
                    height: `${Math.max(height, 3)}%`,
                    background: "linear-gradient(to top, rgba(16,185,129,0.3), rgba(16,185,129,0.8))",
                  }}
                  title={`${m.month}: $${m.amount.toFixed(2)}`} />
                <span className="text-[10px] text-gray-600">{m.month.slice(5)}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Top Earning Content */}
      {data.top_earning_content?.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="top-earning-content">
          <h3 className="font-semibold text-sm text-gray-300 mb-4">Top Earning Content</h3>
          <div className="space-y-2">
            {data.top_earning_content.map((c, i) => (
              <div key={c.content_id} className="flex items-center justify-between py-2 border-b border-gray-800/50 last:border-0">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-600 w-5">{i + 1}</span>
                  <span className="text-sm text-gray-300">{c.title}</span>
                </div>
                <span className="text-sm text-emerald-400 font-medium">${c.total.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── STAT CARD ─── */
function StatCard({ icon, label, value }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5" data-testid="stat-card">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="text-xs text-gray-500 uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}

export default CreatorAnalyticsPage;
