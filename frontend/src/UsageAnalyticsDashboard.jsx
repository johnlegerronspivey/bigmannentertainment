import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import {
  BarChart3, Users, Activity, TrendingUp, Clock, Layers,
  RefreshCw, ChevronDown, Zap, PieChart, ArrowUpRight,
  ArrowDownRight, Minus, Eye
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const PERIODS = [
  { id: '1d', label: 'Today' },
  { id: '7d', label: '7 Days' },
  { id: '14d', label: '14 Days' },
  { id: '30d', label: '30 Days' },
  { id: '90d', label: '90 Days' }
];

const CATEGORY_COLORS = {
  creative_studio: '#8b5cf6',
  ai_tools: '#f59e0b',
  collaboration: '#10b981',
  projects: '#3b82f6',
  marketplace: '#ec4899',
  auth: '#6b7280',
  testing: '#14b8a6'
};

const CATEGORY_LABELS = {
  creative_studio: 'Creative Studio',
  ai_tools: 'AI Tools',
  collaboration: 'Collaboration',
  projects: 'Projects',
  marketplace: 'Marketplace',
  auth: 'Authentication',
  testing: 'Testing'
};

// ==================== Stat Card ====================
const StatCard = ({ label, value, icon: Icon, change, color }) => (
  <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4 hover:border-slate-600/60 transition-colors"
       data-testid={`stat-card-${label.toLowerCase().replace(/\s+/g, '-')}`}>
    <div className="flex items-center justify-between mb-3">
      <span className="text-gray-400 text-xs font-medium uppercase tracking-wide">{label}</span>
      <div className={`p-1.5 rounded-lg`} style={{ backgroundColor: `${color}20` }}>
        <Icon size={14} style={{ color }} />
      </div>
    </div>
    <div className="flex items-end gap-2">
      <span className="text-white text-2xl font-bold">{typeof value === 'number' ? value.toLocaleString() : value}</span>
      {change !== undefined && (
        <span className={`flex items-center text-xs font-medium mb-0.5 ${change > 0 ? 'text-emerald-400' : change < 0 ? 'text-red-400' : 'text-gray-500'}`}>
          {change > 0 ? <ArrowUpRight size={12} /> : change < 0 ? <ArrowDownRight size={12} /> : <Minus size={12} />}
          {Math.abs(change)}%
        </span>
      )}
    </div>
  </div>
);

// ==================== Mini Bar Chart ====================
const MiniBarChart = ({ data, maxVal, color }) => {
  if (!data || data.length === 0) return null;
  const max = maxVal || Math.max(...data.map(d => d.events || d.count || 0), 1);
  return (
    <div className="flex items-end gap-[2px] h-20">
      {data.map((d, i) => {
        const val = d.events || d.count || 0;
        const h = Math.max(2, (val / max) * 100);
        return (
          <div key={i} className="flex-1 flex flex-col items-center group relative">
            <div className="w-full rounded-t-sm transition-all hover:opacity-80"
                 style={{ height: `${h}%`, backgroundColor: color, minHeight: 2 }} />
            <div className="absolute -top-6 bg-slate-700 text-white text-[9px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-10">
              {d.date ? `${d.date}: ${val}` : val}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// ==================== Horizontal Bar ====================
const HBar = ({ label, value, maxVal, color }) => {
  const pct = maxVal > 0 ? (value / maxVal) * 100 : 0;
  return (
    <div className="flex items-center gap-2">
      <span className="text-gray-400 text-[11px] w-28 truncate" title={label}>{label}</span>
      <div className="flex-1 h-3 bg-slate-700/50 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500"
             style={{ width: `${Math.max(pct, 1)}%`, backgroundColor: color }} />
      </div>
      <span className="text-gray-300 text-[11px] w-10 text-right font-mono">{value}</span>
    </div>
  );
};

// ==================== Donut Chart ====================
const DonutChart = ({ data }) => {
  if (!data || Object.keys(data).length === 0) return null;
  const total = Object.values(data).reduce((a, b) => a + b, 0);
  if (total === 0) return null;

  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  let cumAngle = 0;

  const arcs = entries.map(([key, val]) => {
    const pct = val / total;
    const startAngle = cumAngle;
    cumAngle += pct * 360;
    const endAngle = cumAngle;
    const color = CATEGORY_COLORS[key] || '#6b7280';
    return { key, val, pct, startAngle, endAngle, color };
  });

  const polarToCartesian = (cx, cy, r, angle) => {
    const rad = ((angle - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  };

  const describeArc = (cx, cy, r, start, end) => {
    if (end - start >= 359.99) {
      const s = polarToCartesian(cx, cy, r, start);
      const m = polarToCartesian(cx, cy, r, start + 180);
      return `M ${s.x} ${s.y} A ${r} ${r} 0 1 1 ${m.x} ${m.y} A ${r} ${r} 0 1 1 ${s.x} ${s.y}`;
    }
    const s = polarToCartesian(cx, cy, r, start);
    const e = polarToCartesian(cx, cy, r, end);
    const large = end - start > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
  };

  return (
    <div className="flex items-center gap-4">
      <svg width="100" height="100" viewBox="0 0 100 100">
        {arcs.map((a, i) => (
          <path key={i} d={describeArc(50, 50, 38, a.startAngle, a.endAngle)}
                fill="none" stroke={a.color} strokeWidth="10" strokeLinecap="round" />
        ))}
        <text x="50" y="48" textAnchor="middle" fill="white" fontSize="16" fontWeight="bold">
          {total.toLocaleString()}
        </text>
        <text x="50" y="62" textAnchor="middle" fill="#94a3b8" fontSize="9">events</text>
      </svg>
      <div className="flex-1 space-y-1">
        {entries.slice(0, 6).map(([key, val]) => (
          <div key={key} className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: CATEGORY_COLORS[key] || '#6b7280' }} />
            <span className="text-gray-400 text-[10px] flex-1">{CATEGORY_LABELS[key] || key}</span>
            <span className="text-gray-300 text-[10px] font-mono">{val}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ==================== Feature Usage Card ====================
const FeatureUsageCard = ({ name, data }) => {
  const color = CATEGORY_COLORS[name] || '#6b7280';
  const maxCount = Math.max(...(data.events || []).map(e => e.count), 1);
  return (
    <div className="bg-slate-800/40 border border-slate-700/40 rounded-lg p-3 hover:border-slate-600/60 transition-colors"
         data-testid={`feature-card-${name}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
          <span className="text-white text-xs font-medium">{CATEGORY_LABELS[name] || name}</span>
        </div>
        <span className="text-gray-400 text-[10px] font-mono bg-slate-700/50 px-2 py-0.5 rounded">{data.total} total</span>
      </div>
      <div className="space-y-1.5">
        {(data.events || []).map((ev, i) => (
          <div key={i}>
            <div className="flex items-center justify-between mb-0.5">
              <span className="text-gray-400 text-[10px]">{ev.event_type?.replace(/_/g, ' ')}</span>
              <div className="flex items-center gap-2">
                <span className="text-gray-500 text-[9px] flex items-center gap-0.5"><Users size={9} />{ev.unique_users}</span>
                <span className="text-gray-300 text-[10px] font-mono">{ev.count}</span>
              </div>
            </div>
            <div className="h-1 bg-slate-700/50 rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${(ev.count / maxCount) * 100}%`, backgroundColor: color }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ==================== Main Dashboard ====================
const UsageAnalyticsDashboard = () => {
  const [period, setPeriod] = useState('7d');
  const [dashboard, setDashboard] = useState(null);
  const [features, setFeatures] = useState(null);
  const [realtime, setRealtime] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('overview');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [dashRes, featRes, rtRes] = await Promise.all([
        fetch(`${API}/api/analytics-tracking/dashboard?period=${period}`),
        fetch(`${API}/api/analytics-tracking/features?period=${period}`),
        fetch(`${API}/api/analytics-tracking/realtime`)
      ]);
      if (dashRes.ok) setDashboard(await dashRes.json());
      if (featRes.ok) setFeatures(await featRes.json());
      if (rtRes.ok) setRealtime(await rtRes.json());
    } catch (e) {
      toast.error('Failed to load analytics');
    }
    setLoading(false);
  }, [period]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const views = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'features', label: 'Features', icon: Layers },
    { id: 'trends', label: 'Trends', icon: TrendingUp },
    { id: 'realtime', label: 'Real-time', icon: Zap }
  ];

  return (
    <div className="min-h-screen bg-slate-900" data-testid="usage-analytics-dashboard">
      {/* Header */}
      <div className="border-b border-slate-700/50 bg-slate-900/90 backdrop-blur-lg sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-white text-xl font-bold flex items-center gap-2" data-testid="analytics-title">
                <BarChart3 size={20} className="text-cyan-400" /> Usage Analytics
              </h1>
              <p className="text-gray-500 text-xs mt-0.5">Track engagement, feature usage, and user activity</p>
            </div>
            <div className="flex items-center gap-3">
              {/* Period selector */}
              <div className="flex items-center bg-slate-800 rounded-lg border border-slate-700/50 p-0.5" data-testid="period-selector">
                {PERIODS.map(p => (
                  <button key={p.id} onClick={() => setPeriod(p.id)}
                          className={`text-[11px] px-3 py-1.5 rounded-md font-medium transition-colors
                            ${period === p.id ? 'bg-cyan-600 text-white' : 'text-gray-400 hover:text-white'}`}
                          data-testid={`period-${p.id}`}>
                    {p.label}
                  </button>
                ))}
              </div>
              <button onClick={fetchData}
                      className="p-2 rounded-lg bg-slate-800 border border-slate-700/50 text-gray-400 hover:text-white hover:border-slate-600 transition-colors"
                      data-testid="refresh-analytics-btn">
                <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>

          {/* View tabs */}
          <div className="flex gap-1 mt-3">
            {views.map(v => (
              <button key={v.id} onClick={() => setActiveView(v.id)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors
                        ${activeView === v.id ? 'bg-slate-700/70 text-white' : 'text-gray-500 hover:text-gray-300'}`}
                      data-testid={`view-tab-${v.id}`}>
                <v.icon size={13} />
                {v.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {loading && !dashboard ? (
          <div className="flex items-center justify-center py-20" data-testid="analytics-loading">
            <RefreshCw size={24} className="animate-spin text-cyan-400" />
          </div>
        ) : (
          <>
            {/* Sample data banner */}
            {dashboard?.sample_data && (
              <div className="mb-4 bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-2.5 flex items-center gap-2"
                   data-testid="sample-data-banner">
                <Eye size={14} className="text-amber-400" />
                <span className="text-amber-300 text-xs">Showing sample data for demo. Real events will appear as users interact with the platform.</span>
              </div>
            )}

            {/* Overview View */}
            {activeView === 'overview' && dashboard && (
              <div className="space-y-6" data-testid="overview-section">
                {/* Stat cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <StatCard label="Total Events" value={dashboard.total_events} icon={Activity} color="#06b6d4" change={12} />
                  <StatCard label="Active Users" value={dashboard.active_users} icon={Users} color="#8b5cf6" change={8} />
                  <StatCard label="Top Category" value={
                    Object.keys(dashboard.categories || {})[0]?.replace(/_/g, ' ') || 'N/A'
                  } icon={Layers} color="#f59e0b" />
                  <StatCard label="Events/Day" value={
                    dashboard.daily_trend?.length > 0
                      ? Math.round(dashboard.total_events / dashboard.daily_trend.length)
                      : 0
                  } icon={TrendingUp} color="#10b981" change={5} />
                </div>

                {/* Charts row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Daily trend */}
                  <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4" data-testid="daily-trend-chart">
                    <h3 className="text-white text-sm font-semibold mb-3 flex items-center gap-2">
                      <TrendingUp size={14} className="text-cyan-400" /> Daily Activity
                    </h3>
                    <MiniBarChart data={dashboard.daily_trend || []} color="#06b6d4" />
                    {dashboard.daily_trend?.length > 0 && (
                      <div className="flex justify-between mt-2">
                        <span className="text-gray-600 text-[9px]">{dashboard.daily_trend[0]?.date}</span>
                        <span className="text-gray-600 text-[9px]">{dashboard.daily_trend[dashboard.daily_trend.length - 1]?.date}</span>
                      </div>
                    )}
                  </div>

                  {/* Category donut */}
                  <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4" data-testid="category-breakdown">
                    <h3 className="text-white text-sm font-semibold mb-3 flex items-center gap-2">
                      <PieChart size={14} className="text-amber-400" /> Category Breakdown
                    </h3>
                    <DonutChart data={dashboard.categories} />
                  </div>
                </div>

                {/* Top events */}
                <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4" data-testid="top-events-section">
                  <h3 className="text-white text-sm font-semibold mb-3 flex items-center gap-2">
                    <BarChart3 size={14} className="text-emerald-400" /> Top Events
                  </h3>
                  <div className="space-y-2">
                    {(dashboard.top_events || []).map((e, i) => (
                      <HBar key={i} label={e.event?.replace(/_/g, ' ')} value={e.count}
                            maxVal={dashboard.top_events[0]?.count || 1}
                            color={i < 3 ? '#06b6d4' : i < 6 ? '#8b5cf6' : '#475569'} />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Features View */}
            {activeView === 'features' && features && (
              <div className="space-y-4" data-testid="features-section">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(features.features || {}).map(([name, data]) => (
                    <FeatureUsageCard key={name} name={name} data={data} />
                  ))}
                </div>
                {Object.keys(features.features || {}).length === 0 && (
                  <div className="text-center py-16 text-gray-500 text-sm">
                    No feature usage data for this period
                  </div>
                )}
              </div>
            )}

            {/* Trends View */}
            {activeView === 'trends' && dashboard && (
              <div className="space-y-6" data-testid="trends-section">
                {/* Full-width trend */}
                <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
                  <h3 className="text-white text-sm font-semibold mb-4 flex items-center gap-2">
                    <TrendingUp size={14} className="text-cyan-400" /> Event Trend — {PERIODS.find(p => p.id === period)?.label}
                  </h3>
                  <div className="h-32">
                    <MiniBarChart data={dashboard.daily_trend || []} color="#06b6d4" />
                  </div>
                  {dashboard.daily_trend?.length > 0 && (
                    <div className="flex justify-between mt-2">
                      <span className="text-gray-600 text-[9px]">{dashboard.daily_trend[0]?.date}</span>
                      <span className="text-gray-600 text-[9px]">{dashboard.daily_trend[dashboard.daily_trend.length - 1]?.date}</span>
                    </div>
                  )}
                </div>

                {/* Category trend bars */}
                <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
                  <h3 className="text-white text-sm font-semibold mb-4 flex items-center gap-2">
                    <Layers size={14} className="text-amber-400" /> Category Volume
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(dashboard.categories || {}).sort((a, b) => b[1] - a[1]).map(([cat, val]) => (
                      <HBar key={cat} label={CATEGORY_LABELS[cat] || cat}
                            value={val}
                            maxVal={Math.max(...Object.values(dashboard.categories || {}), 1)}
                            color={CATEGORY_COLORS[cat] || '#6b7280'} />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Real-time View */}
            {activeView === 'realtime' && (
              <div className="space-y-6" data-testid="realtime-section">
                <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-white text-sm font-semibold flex items-center gap-2">
                      <Zap size={14} className="text-emerald-400" /> Last Hour Activity
                    </h3>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                      <span className="text-emerald-400 text-[10px] font-medium">Live</span>
                    </div>
                  </div>
                  <div className="text-center py-8">
                    <span className="text-white text-5xl font-bold">{realtime?.last_hour_events || 0}</span>
                    <p className="text-gray-500 text-sm mt-2">events in the last hour</p>
                  </div>
                </div>

                {realtime?.top_events?.length > 0 && (
                  <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
                    <h3 className="text-white text-sm font-semibold mb-3">Recent Top Events</h3>
                    <div className="space-y-2">
                      {realtime.top_events.map((e, i) => (
                        <HBar key={i} label={e.event?.replace(/_/g, ' ')} value={e.count}
                              maxVal={realtime.top_events[0]?.count || 1} color="#10b981" />
                      ))}
                    </div>
                  </div>
                )}

                {(!realtime?.top_events || realtime.top_events.length === 0) && (
                  <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-8 text-center">
                    <Clock size={32} className="text-gray-600 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">No events in the last hour</p>
                    <p className="text-gray-600 text-xs mt-1">Events will appear here as users interact with the platform</p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default UsageAnalyticsDashboard;
