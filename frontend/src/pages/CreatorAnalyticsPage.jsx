import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../utils/apiClient";
import { BarChart3, Eye, Download, Heart, Users, TrendingUp, DollarSign, FileAudio, FileVideo, Image, MessageCircle } from "lucide-react";

function CreatorAnalyticsPage() {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [contentPerf, setContentPerf] = useState([]);
  const [audience, setAudience] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");

  useEffect(() => {
    loadAll();
  }, []);

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
    } catch {
      // Partial load ok
    } finally {
      setLoading(false);
    }
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

  return (
    <div className="min-h-screen bg-gray-950 text-white" data-testid="analytics-page">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold" data-testid="analytics-page-title">Creator Analytics</h1>
          <p className="text-gray-400 mt-1">Insights into your content performance and audience</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-800 pb-2" data-testid="analytics-tabs">
          {["overview", "content", "audience", "revenue"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`pb-2 px-1 text-sm font-medium capitalize transition-colors ${tab === t ? "text-purple-400 border-b-2 border-purple-400" : "text-gray-500 hover:text-gray-300"}`}
              data-testid={`tab-${t}`}
            >
              {t}
            </button>
          ))}
        </div>

        {tab === "overview" && overview && (
          <div data-testid="overview-section">
            {/* Stat Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard icon={<BarChart3 className="w-5 h-5 text-purple-400" />} label="Total Content" value={overview.total_content} />
              <StatCard icon={<Eye className="w-5 h-5 text-blue-400" />} label="Total Views" value={overview.engagement?.total_views || 0} />
              <StatCard icon={<Download className="w-5 h-5 text-green-400" />} label="Downloads" value={overview.engagement?.total_downloads || 0} />
              <StatCard icon={<Heart className="w-5 h-5 text-pink-400" />} label="Likes" value={overview.engagement?.total_likes || 0} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Content by Type */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="content-by-type-card">
                <h3 className="font-semibold text-sm text-gray-300 mb-4">Content by Type</h3>
                <div className="space-y-3">
                  {Object.entries(overview.content_by_type || {}).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {typeIcon(type)}
                        <span className="text-sm capitalize">{type}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${type === "audio" ? "bg-green-500" : type === "video" ? "bg-blue-500" : "bg-pink-500"}`}
                            style={{ width: `${overview.total_content ? (count / overview.total_content) * 100 : 0}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-400 w-8 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Stats */}
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="quick-stats-card">
                <h3 className="font-semibold text-sm text-gray-300 mb-4">Quick Stats</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between py-2 border-b border-gray-800">
                    <span className="text-sm text-gray-400 flex items-center gap-2"><Users className="w-4 h-4" /> Followers</span>
                    <span className="font-medium">{overview.profile_stats?.total_followers || 0}</span>
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-gray-800">
                    <span className="text-sm text-gray-400 flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Streams</span>
                    <span className="font-medium">{overview.profile_stats?.total_streams || 0}</span>
                  </div>
                  <div className="flex items-center justify-between py-2 border-b border-gray-800">
                    <span className="text-sm text-gray-400 flex items-center gap-2"><DollarSign className="w-4 h-4" /> Earnings</span>
                    <span className="font-medium">${(overview.profile_stats?.total_earnings || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex items-center justify-between py-2">
                    <span className="text-sm text-gray-400 flex items-center gap-2"><MessageCircle className="w-4 h-4" /> Conversations</span>
                    <span className="font-medium">{overview.total_conversations || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

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
                        <td className="px-4 py-3">
                          <span className="flex items-center gap-1.5 capitalize">{typeIcon(item.content_type)} {item.content_type}</span>
                        </td>
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

        {tab === "audience" && audience && (
          <div data-testid="audience-section">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <StatCard icon={<Users className="w-5 h-5 text-purple-400" />} label="Total Followers" value={audience.total_followers || 0} />
            </div>

            {/* Growth Chart (simplified bar representation) */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6" data-testid="follower-growth-card">
              <h3 className="font-semibold text-sm text-gray-300 mb-4">Follower Growth (Last 7 Days)</h3>
              <div className="flex items-end gap-2 h-32">
                {(audience.growth || []).map((d, i) => {
                  const max = Math.max(...(audience.growth || []).map((g) => g.new_followers), 1);
                  const height = (d.new_followers / max) * 100;
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                      <span className="text-xs text-gray-500">{d.new_followers}</span>
                      <div className="w-full bg-purple-600/30 rounded-t" style={{ height: `${Math.max(height, 4)}%` }}>
                        <div className="w-full h-full bg-purple-500 rounded-t" />
                      </div>
                      <span className="text-[10px] text-gray-600">{d.date.slice(5)}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Top Content */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="top-content-card">
              <h3 className="font-semibold text-sm text-gray-300 mb-4">Top Performing Content</h3>
              <div className="space-y-3">
                {(audience.top_content || []).map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-gray-800/50">
                    <div className="flex items-center gap-2">
                      {typeIcon(item.content_type)}
                      <span className="text-sm">{item.title}</span>
                    </div>
                    <span className="text-sm text-gray-400">{item.stats?.views || 0} views</span>
                  </div>
                ))}
                {(audience.top_content || []).length === 0 && <p className="text-gray-500 text-sm">No public content yet</p>}
              </div>
            </div>
          </div>
        )}

        {tab === "revenue" && revenue && (
          <div data-testid="revenue-section">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <StatCard icon={<DollarSign className="w-5 h-5 text-green-400" />} label="Total Earnings" value={`$${(revenue.total_earnings || 0).toFixed(2)}`} />
            </div>

            {/* Monthly Revenue */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6" data-testid="monthly-revenue-card">
              <h3 className="font-semibold text-sm text-gray-300 mb-4">Monthly Revenue (Last 6 Months)</h3>
              <div className="flex items-end gap-3 h-40">
                {(revenue.monthly_revenue || []).map((m, i) => {
                  const max = Math.max(...(revenue.monthly_revenue || []).map((r) => r.amount), 1);
                  const height = (m.amount / max) * 100;
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1">
                      <span className="text-xs text-gray-500">${m.amount.toFixed(0)}</span>
                      <div className="w-full rounded-t" style={{ height: `${Math.max(height, 4)}%`, background: "linear-gradient(to top, #22c55e40, #22c55e)" }} />
                      <span className="text-[10px] text-gray-600">{m.month.slice(5)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

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
