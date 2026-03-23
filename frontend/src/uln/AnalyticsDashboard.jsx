import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { RefreshCw, TrendingUp, Globe, Music, BarChart3, Users, PieChart } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const getToken = () => localStorage.getItem('token');

const api = async (path) => {
  const res = await fetch(`${API}/api/uln-enhanced${path}`, {
    headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
  });
  return res.json();
};

const COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1', '#14b8a6'];

export const AnalyticsDashboard = () => {
  const [performance, setPerformance] = useState([]);
  const [trends, setTrends] = useState([]);
  const [genres, setGenres] = useState([]);
  const [territories, setTerritories] = useState([]);
  const [sharing, setSharing] = useState(null);
  const [dao, setDao] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activePanel, setActivePanel] = useState('performance');

  const refresh = useCallback(async () => {
    setLoading(true);
    const [p, t, g, tr, s, d] = await Promise.all([
      api('/analytics/cross-label-performance'),
      api('/analytics/revenue-trends?months=12'),
      api('/analytics/genre-breakdown'),
      api('/analytics/territory-breakdown'),
      api('/analytics/content-sharing'),
      api('/analytics/dao'),
    ]);
    setPerformance(p.labels || []);
    setTrends(t.trends || []);
    setGenres(g.genres || []);
    setTerritories(tr.territories || []);
    setSharing(s);
    setDao(d);
    setLoading(false);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const maxRevenue = Math.max(...trends.map((t) => t.revenue), 1);

  if (loading) return <div className="flex justify-center py-16"><RefreshCw className="w-8 h-8 animate-spin text-cyan-500" /></div>;

  const panels = [
    { id: 'performance', label: 'Cross-Label', icon: <Users className="w-4 h-4" /> },
    { id: 'revenue', label: 'Revenue', icon: <TrendingUp className="w-4 h-4" /> },
    { id: 'genres', label: 'Genres', icon: <Music className="w-4 h-4" /> },
    { id: 'territories', label: 'Territories', icon: <Globe className="w-4 h-4" /> },
    { id: 'sharing', label: 'Content Sharing', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'dao', label: 'DAO', icon: <PieChart className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-6" data-testid="analytics-dashboard">
      {/* Sub-nav */}
      <div className="flex flex-wrap gap-2">
        {panels.map((p) => (
          <Button key={p.id} variant={activePanel === p.id ? 'default' : 'outline'} size="sm"
            onClick={() => setActivePanel(p.id)}
            className={activePanel === p.id ? 'bg-cyan-600 hover:bg-cyan-700 text-white' : 'border-slate-600 text-slate-300 hover:bg-slate-700'}>
            {p.icon}<span className="ml-1.5">{p.label}</span>
          </Button>
        ))}
        <Button variant="outline" size="sm" onClick={refresh} className="ml-auto border-slate-600 text-slate-300 hover:bg-slate-700">
          <RefreshCw className="w-4 h-4" />
        </Button>
      </div>

      {/* Cross-label performance */}
      {activePanel === 'performance' && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Cross-Label Performance Ranking</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-slate-300">
                <thead className="text-xs text-slate-500 border-b border-slate-700">
                  <tr>
                    <th className="px-3 py-2 text-left">#</th>
                    <th className="px-3 py-2 text-left">Label</th>
                    <th className="px-3 py-2 text-left">Type</th>
                    <th className="px-3 py-2 text-left">Territory</th>
                    <th className="px-3 py-2 text-right">Royalties</th>
                    <th className="px-3 py-2 text-right">Shared</th>
                    <th className="px-3 py-2 text-center">Blockchain</th>
                  </tr>
                </thead>
                <tbody>
                  {performance.slice(0, 25).map((l, i) => (
                    <tr key={l.label_id} className="border-b border-slate-700/50 hover:bg-slate-700/40">
                      <td className="px-3 py-2 text-slate-500">{i + 1}</td>
                      <td className="px-3 py-2 font-medium text-white">{l.name}</td>
                      <td className="px-3 py-2"><span className={`text-xs px-2 py-0.5 rounded ${l.label_type === 'major' ? 'bg-violet-900/40 text-violet-400' : 'bg-cyan-900/40 text-cyan-400'}`}>{l.label_type}</span></td>
                      <td className="px-3 py-2">{l.territory}</td>
                      <td className="px-3 py-2 text-right font-mono">${l.total_royalties.toLocaleString()}</td>
                      <td className="px-3 py-2 text-right">{l.shared_content}</td>
                      <td className="px-3 py-2 text-center">{l.blockchain_enabled ? <span className="text-emerald-400">Active</span> : <span className="text-slate-500">-</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Revenue trends */}
      {activePanel === 'revenue' && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Monthly Revenue Trends (12mo)</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-end gap-1 h-64">
              {trends.map((t, i) => (
                <div key={t.month} className="flex-1 flex flex-col items-center justify-end h-full">
                  <div className="w-full rounded-t" style={{ height: `${(t.revenue / maxRevenue) * 100}%`, background: `linear-gradient(180deg, ${COLORS[i % COLORS.length]}, ${COLORS[i % COLORS.length]}88)` }} title={`$${t.revenue.toLocaleString()}`} />
                  <span className="text-[10px] text-slate-500 mt-1 rotate-[-45deg] origin-top-left">{t.month}</span>
                </div>
              ))}
            </div>
            <div className="mt-6 grid grid-cols-3 gap-4 text-center">
              <div><p className="text-xs text-slate-500">Total Revenue</p><p className="text-lg font-bold text-white">${trends.reduce((s, t) => s + t.revenue, 0).toLocaleString()}</p></div>
              <div><p className="text-xs text-slate-500">Avg Monthly</p><p className="text-lg font-bold text-white">${Math.round(trends.reduce((s, t) => s + t.revenue, 0) / (trends.length || 1)).toLocaleString()}</p></div>
              <div><p className="text-xs text-slate-500">Total Txns</p><p className="text-lg font-bold text-white">{trends.reduce((s, t) => s + t.transactions, 0).toLocaleString()}</p></div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Genre breakdown */}
      {activePanel === 'genres' && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Genre Distribution</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {genres.map((g, i) => {
                const maxCount = Math.max(...genres.map((x) => x.label_count), 1);
                return (
                  <div key={g.genre} className="flex items-center gap-3">
                    <span className="w-28 text-sm text-slate-300 truncate">{g.genre}</span>
                    <div className="flex-1 bg-slate-700 rounded-full h-5 overflow-hidden">
                      <div className="h-full rounded-full transition-all" style={{ width: `${(g.label_count / maxCount) * 100}%`, backgroundColor: COLORS[i % COLORS.length] }} />
                    </div>
                    <span className="text-sm text-slate-400 w-8 text-right">{g.label_count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Territory */}
      {activePanel === 'territories' && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white text-base">Territory Distribution</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {territories.map((t, i) => (
                <div key={t.territory} className="p-4 rounded-lg bg-slate-700/50 text-center">
                  <p className="text-2xl font-bold" style={{ color: COLORS[i % COLORS.length] }}>{t.label_count}</p>
                  <p className="text-sm text-slate-400">{t.territory}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Content sharing */}
      {activePanel === 'sharing' && sharing && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-slate-800 border-slate-700"><CardContent className="p-4 text-center"><p className="text-3xl font-bold text-cyan-400">{sharing.total_shared_content}</p><p className="text-sm text-slate-400">Total Shared Items</p></CardContent></Card>
            <Card className="bg-slate-800 border-slate-700"><CardContent className="p-4 text-center"><p className="text-3xl font-bold text-violet-400">{Object.keys(sharing.by_access_level || {}).length}</p><p className="text-sm text-slate-400">Access Levels</p></CardContent></Card>
            <Card className="bg-slate-800 border-slate-700"><CardContent className="p-4 text-center"><p className="text-3xl font-bold text-emerald-400">{(sharing.top_sharers || []).length}</p><p className="text-sm text-slate-400">Active Sharers</p></CardContent></Card>
          </div>
          {(sharing.top_sharers || []).length > 0 && (
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader><CardTitle className="text-white text-base">Top Content Sharers</CardTitle></CardHeader>
              <CardContent>
                {sharing.top_sharers.map((s, i) => (
                  <div key={s.label_id} className="flex items-center gap-3 py-2 border-b border-slate-700/50 last:border-0">
                    <span className="text-slate-500 w-6">{i + 1}</span>
                    <span className="text-white flex-1">{s.name}</span>
                    <span className="text-cyan-400 font-mono">{s.shared_count} items</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* DAO analytics */}
      {activePanel === 'dao' && dao && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-base">Proposals by Status</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(dao.by_status || {}).map(([k, v]) => (
                <div key={k} className="flex justify-between items-center py-2 border-b border-slate-700/50">
                  <span className="text-slate-300 capitalize">{k}</span>
                  <span className="text-white font-bold">{v}</span>
                </div>
              ))}
              {Object.keys(dao.by_status || {}).length === 0 && <p className="text-slate-500 text-sm">No proposals yet</p>}
            </CardContent>
          </Card>
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-base">Proposals by Type</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(dao.by_type || {}).map(([k, v]) => (
                <div key={k} className="flex justify-between items-center py-2 border-b border-slate-700/50">
                  <span className="text-slate-300">{k.replace(/_/g, ' ')}</span>
                  <span className="text-white font-bold">{v}</span>
                </div>
              ))}
              {Object.keys(dao.by_type || {}).length === 0 && <p className="text-slate-500 text-sm">No proposals yet</p>}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
