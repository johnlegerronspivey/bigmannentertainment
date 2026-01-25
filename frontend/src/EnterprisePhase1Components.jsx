import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// ============================================
// TALENT INTELLIGENCE COMPONENTS
// ============================================

export const TalentScoreAnalyzer = ({ modelId, modelData, onAnalysis }) => {
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState(null);

  const analyzeScore = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/talent/analyze-score/${modelId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(modelData)
      });
      const data = await response.json();
      setScore(data);
      onAnalysis?.(data);
      toast.success('Talent analysis complete');
    } catch (error) {
      toast.error('Failed to analyze talent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="talent-score-analyzer">
      <h3 className="text-xl font-bold text-white mb-4">AI Talent Analysis</h3>
      
      <button
        onClick={analyzeScore}
        disabled={loading}
        className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
        data-testid="analyze-talent-btn"
      >
        {loading ? 'Analyzing...' : 'Analyze Talent Score'}
      </button>

      {score && (
        <div className="mt-6 space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <ScoreCard label="Overall Score" value={score.overall_score} />
            <ScoreCard label="Commercial Value" value={score.commercial_value} />
            <ScoreCard label="Market Demand" value={score.market_demand} />
            <ScoreCard label="Booking Potential" value={score.booking_potential} />
          </div>
          
          {score.trending_categories?.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-slate-400 mb-2">Trending Categories</h4>
              <div className="flex flex-wrap gap-2">
                {score.trending_categories.map((cat, i) => (
                  <span key={i} className="bg-purple-600/30 text-purple-300 px-3 py-1 rounded-full text-sm">
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          <div className="bg-slate-700/50 rounded-lg p-4 mt-4">
            <p className="text-slate-300">
              <span className="font-medium text-purple-400">Predicted Bookings (30d):</span>{' '}
              {score.predicted_bookings_30d}
            </p>
            <p className="text-slate-300 mt-1">
              <span className="font-medium text-purple-400">Recommended Rate Adjustment:</span>{' '}
              {(score.recommended_rate_adjustment * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

const ScoreCard = ({ label, value }) => (
  <div className="bg-slate-700/50 rounded-lg p-4 text-center">
    <div className="text-2xl font-bold text-white">{value?.toFixed(0) || 0}</div>
    <div className="text-xs text-slate-400 mt-1">{label}</div>
  </div>
);

export const MarketTrendsWidget = () => {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrends();
  }, []);

  const fetchTrends = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/talent/market-trends?category=modeling`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setTrends(data);
    } catch (error) {
      console.error('Failed to fetch trends');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="animate-pulse bg-slate-800 rounded-lg h-64" />;

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="market-trends-widget">
      <h3 className="text-xl font-bold text-white mb-4">Market Trends</h3>
      <div className="space-y-3">
        {trends.map((trend, i) => (
          <div key={i} className="bg-slate-700/50 rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium text-white">{trend.trend_name}</h4>
                <p className="text-sm text-slate-400">{trend.category}</p>
              </div>
              <span className={`text-sm font-medium ${trend.growth_rate > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {trend.growth_rate > 0 ? '+' : ''}{(trend.growth_rate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="mt-2 flex flex-wrap gap-1">
              {trend.affected_regions?.map((region, j) => (
                <span key={j} className="text-xs bg-slate-600 text-slate-300 px-2 py-0.5 rounded">
                  {region}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================
// EXECUTIVE DASHBOARD COMPONENTS
// ============================================

export const ExecutiveSummaryDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [timeRange, setTimeRange] = useState('month');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, [timeRange]);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/executive/summary?time_range=${timeRange}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error('Failed to fetch summary');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <ExecutiveSkeleton />;

  return (
    <div className="space-y-6" data-testid="executive-summary-dashboard">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Executive Command Center</h2>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
          data-testid="time-range-select"
        >
          <option value="day">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
          <option value="year">This Year</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard 
          label="Total Revenue" 
          value={`$${(summary?.total_revenue || 0).toLocaleString()}`}
          change={summary?.revenue_change}
        />
        <KPICard 
          label="Active Agencies" 
          value={summary?.active_agencies || 0}
        />
        <KPICard 
          label="Active Models" 
          value={summary?.active_models || 0}
        />
        <KPICard 
          label="Total Bookings" 
          value={summary?.total_bookings || 0}
        />
      </div>

      {/* Platform Health */}
      <div className="bg-slate-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Platform Health</h3>
          <span className={`text-2xl font-bold ${
            summary?.platform_health_score >= 80 ? 'text-green-400' :
            summary?.platform_health_score >= 60 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {summary?.platform_health_score || 0}/100
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all ${
              summary?.platform_health_score >= 80 ? 'bg-green-500' :
              summary?.platform_health_score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${summary?.platform_health_score || 0}%` }}
          />
        </div>
      </div>

      {/* AI Insights */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Key Insights</h3>
          <ul className="space-y-2">
            {summary?.key_insights?.map((insight, i) => (
              <li key={i} className="flex items-start gap-2 text-slate-300">
                <span className="text-purple-400 mt-1">•</span>
                {insight}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="bg-slate-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Action Items</h3>
          <ul className="space-y-2">
            {summary?.action_items?.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-slate-300">
                <span className="text-yellow-400 mt-1">→</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

const KPICard = ({ label, value, change }) => (
  <div className="bg-slate-800 rounded-lg p-4">
    <div className="text-sm text-slate-400 mb-1">{label}</div>
    <div className="text-2xl font-bold text-white">{value}</div>
    {change !== undefined && (
      <div className={`text-sm mt-1 ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
        {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(1)}%
      </div>
    )}
  </div>
);

const ExecutiveSkeleton = () => (
  <div className="space-y-6 animate-pulse">
    <div className="h-10 bg-slate-800 rounded w-64" />
    <div className="grid grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-24 bg-slate-800 rounded-lg" />
      ))}
    </div>
    <div className="h-32 bg-slate-800 rounded-lg" />
  </div>
);

export const AgencyRankingsTable = () => {
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRankings();
  }, []);

  const fetchRankings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/executive/agency-rankings?limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setRankings(data);
    } catch (error) {
      console.error('Failed to fetch rankings');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="animate-pulse bg-slate-800 rounded-lg h-64" />;

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="agency-rankings-table">
      <h3 className="text-xl font-bold text-white mb-4">Agency Rankings</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-slate-400 text-sm border-b border-slate-700">
              <th className="pb-3 pr-4">Rank</th>
              <th className="pb-3 pr-4">Agency</th>
              <th className="pb-3 pr-4">Score</th>
              <th className="pb-3 pr-4">Revenue</th>
              <th className="pb-3 pr-4">Models</th>
              <th className="pb-3">Trend</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((agency) => (
              <tr key={agency.agency_id} className="border-b border-slate-700/50">
                <td className="py-3 pr-4">
                  <span className={`font-bold ${
                    agency.rank <= 3 ? 'text-yellow-400' : 'text-slate-400'
                  }`}>
                    #{agency.rank}
                  </span>
                </td>
                <td className="py-3 pr-4 text-white">{agency.agency_name}</td>
                <td className="py-3 pr-4 text-purple-400 font-medium">{agency.performance_score.toFixed(0)}</td>
                <td className="py-3 pr-4 text-slate-300">${agency.revenue_contribution.toLocaleString()}</td>
                <td className="py-3 pr-4 text-slate-300">{agency.active_models}</td>
                <td className="py-3">
                  <span className={`px-2 py-1 rounded text-xs ${
                    agency.growth_trend === 'growing' ? 'bg-green-500/20 text-green-400' :
                    agency.growth_trend === 'declining' ? 'bg-red-500/20 text-red-400' :
                    'bg-slate-600/50 text-slate-400'
                  }`}>
                    {agency.growth_trend}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export const FraudRiskMonitor = () => {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRisks();
  }, []);

  const fetchRisks = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/executive/fraud-risks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setRisks(data);
    } catch (error) {
      console.error('Failed to fetch risks');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="animate-pulse bg-slate-800 rounded-lg h-48" />;

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="fraud-risk-monitor">
      <h3 className="text-xl font-bold text-white mb-4">Fraud Risk Monitor</h3>
      {risks.length === 0 ? (
        <div className="text-center py-8 text-slate-400">
          <span className="text-4xl mb-2">✓</span>
          <p>No fraud risks detected</p>
        </div>
      ) : (
        <div className="space-y-3">
          {risks.map((risk, i) => (
            <div key={i} className={`rounded-lg p-4 border-l-4 ${
              risk.risk_level === 'critical' ? 'bg-red-500/10 border-red-500' :
              risk.risk_level === 'high' ? 'bg-orange-500/10 border-orange-500' :
              risk.risk_level === 'medium' ? 'bg-yellow-500/10 border-yellow-500' :
              'bg-slate-700/50 border-slate-600'
            }`}>
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium text-white">{risk.risk_type}</h4>
                  <p className="text-sm text-slate-400 mt-1">{risk.description}</p>
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded ${
                  risk.risk_level === 'critical' ? 'bg-red-500 text-white' :
                  risk.risk_level === 'high' ? 'bg-orange-500 text-white' :
                  'bg-slate-600 text-slate-300'
                }`}>
                  {risk.risk_level.toUpperCase()}
                </span>
              </div>
              <p className="text-sm text-purple-400 mt-2">
                Recommended: {risk.recommended_action}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// COMPLIANCE COMPONENTS
// ============================================

export const ComplianceAuditTrail = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [complianceOnly, setComplianceOnly] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, [complianceOnly]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${API}/enterprise/compliance/audit-trail?compliance_only=${complianceOnly}&limit=50`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error('Failed to fetch audit logs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="compliance-audit-trail">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-white">Compliance Audit Trail</h3>
        <label className="flex items-center gap-2 text-sm text-slate-400">
          <input
            type="checkbox"
            checked={complianceOnly}
            onChange={(e) => setComplianceOnly(e.target.checked)}
            className="rounded"
          />
          Compliance events only
        </label>
      </div>

      {loading ? (
        <div className="animate-pulse space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-slate-700 rounded" />
          ))}
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={i} className="bg-slate-700/50 rounded-lg p-3 flex justify-between items-start">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">{log.action_type}</span>
                  {log.compliance_relevant && (
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                      Compliance
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-400">
                  {log.entity_type}: {log.entity_id}
                </p>
              </div>
              <span className="text-xs text-slate-500">
                {new Date(log.timestamp).toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const LicenseExpiryTracker = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchExpiringLicenses();
  }, []);

  const fetchExpiringLicenses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/compliance/expiring-licenses?days_ahead=30`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setNotifications(data);
    } catch (error) {
      console.error('Failed to fetch expiring licenses');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="animate-pulse bg-slate-800 rounded-lg h-48" />;

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="license-expiry-tracker">
      <h3 className="text-xl font-bold text-white mb-4">License Expiry Tracker</h3>
      {notifications.length === 0 ? (
        <p className="text-slate-400 text-center py-8">No licenses expiring in the next 30 days</p>
      ) : (
        <div className="space-y-3">
          {notifications.map((notif, i) => (
            <div key={i} className={`rounded-lg p-4 ${
              notif.notification_type === 'expired' ? 'bg-red-500/10 border border-red-500/30' :
              notif.notification_type === 'urgent' ? 'bg-orange-500/10 border border-orange-500/30' :
              'bg-slate-700/50'
            }`}>
              <div className="flex justify-between">
                <span className="text-white font-medium">License #{notif.license_id.slice(0, 8)}</span>
                <span className={`text-sm ${
                  notif.days_until_expiry <= 0 ? 'text-red-400' :
                  notif.days_until_expiry <= 7 ? 'text-orange-400' : 'text-slate-400'
                }`}>
                  {notif.days_until_expiry <= 0 ? 'Expired' : `${notif.days_until_expiry} days left`}
                </span>
              </div>
              <div className="mt-2 flex justify-between items-center">
                <span className="text-sm text-slate-400">
                  Renewal: ${notif.renewal_price}
                </span>
                {notif.auto_renewal_enabled && (
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded">
                    Auto-renewal
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// AGENCY WORKSPACE COMPONENTS
// ============================================

export const AgencyWorkspaceDashboard = ({ agencyId }) => {
  const [workspace, setWorkspace] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (agencyId) {
      fetchWorkspace();
      fetchInsights();
    }
  }, [agencyId]);

  const fetchWorkspace = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/workspace/${agencyId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setWorkspace(data);
      }
    } catch (error) {
      console.error('Failed to fetch workspace');
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/workspace/${agencyId}/ai-insights`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setInsights(data);
      }
    } catch (error) {
      console.error('Failed to fetch insights');
    }
  };

  if (loading) return <div className="animate-pulse bg-slate-800 rounded-lg h-96" />;

  if (!workspace) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 text-center">
        <p className="text-slate-400 mb-4">No workspace found for this agency</p>
        <CreateWorkspaceButton agencyId={agencyId} onCreated={fetchWorkspace} />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="agency-workspace-dashboard">
      {/* Header with Branding */}
      <div 
        className="rounded-lg p-6" 
        style={{ backgroundColor: workspace.branding?.primary_color || '#6366f1' }}
      >
        <h2 className="text-2xl font-bold text-white">{workspace.agency_name}</h2>
        {workspace.branding?.tagline && (
          <p className="text-white/80 mt-1">{workspace.branding.tagline}</p>
        )}
      </div>

      {/* Quick Stats */}
      {insights?.metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Active Models" value={insights.metrics.active_models} />
          <StatCard label="Bookings (30d)" value={insights.metrics.bookings_30d} />
          <StatCard label="Revenue (30d)" value={`$${insights.metrics.revenue_30d?.toLocaleString() || 0}`} />
          <StatCard label="Avg Booking" value={`$${insights.metrics.avg_booking_value?.toFixed(0) || 0}`} />
        </div>
      )}

      {/* AI Insights */}
      {insights && (
        <div className="bg-slate-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">AI Insights</h3>
          <p className="text-slate-300 mb-4">{insights.performance_summary}</p>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-purple-400 mb-2">Opportunities</h4>
              <ul className="space-y-1">
                {insights.opportunities?.map((opp, i) => (
                  <li key={i} className="text-sm text-slate-300">• {opp}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-yellow-400 mb-2">Recommended Actions</h4>
              <ul className="space-y-1">
                {insights.recommended_actions?.map((action, i) => (
                  <li key={i} className="text-sm text-slate-300">→ {action}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Talent Pipeline Preview */}
      {workspace.pipelines?.[0] && (
        <TalentPipelineWidget pipeline={workspace.pipelines[0]} />
      )}
    </div>
  );
};

const StatCard = ({ label, value }) => (
  <div className="bg-slate-800 rounded-lg p-4">
    <div className="text-sm text-slate-400">{label}</div>
    <div className="text-xl font-bold text-white mt-1">{value}</div>
  </div>
);

const CreateWorkspaceButton = ({ agencyId, onCreated }) => {
  const [loading, setLoading] = useState(false);

  const createWorkspace = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/workspace/create/${agencyId}?agency_name=My Agency`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        toast.success('Workspace created!');
        onCreated();
      }
    } catch (error) {
      toast.error('Failed to create workspace');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={createWorkspace}
      disabled={loading}
      className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
    >
      {loading ? 'Creating...' : 'Create Workspace'}
    </button>
  );
};

const TalentPipelineWidget = ({ pipeline }) => {
  const stageCounts = {};
  pipeline.entries?.forEach(entry => {
    stageCounts[entry.stage] = (stageCounts[entry.stage] || 0) + 1;
  });

  const stages = ['scouting', 'contacted', 'interviewing', 'contracted', 'active'];

  return (
    <div className="bg-slate-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Talent Pipeline</h3>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {stages.map(stage => (
          <div key={stage} className="flex-1 min-w-24 bg-slate-700/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-white">{stageCounts[stage] || 0}</div>
            <div className="text-xs text-slate-400 capitalize mt-1">{stage}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const CastingSuggestionGenerator = ({ agencyId }) => {
  const [requirements, setRequirements] = useState({
    campaign_name: '',
    category: '',
    budget: '',
    requirements: ''
  });
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateSuggestions = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/enterprise/workspace/${agencyId}/casting-suggestions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requirements)
      });
      const data = await response.json();
      setSuggestions(data);
      toast.success('Casting suggestions generated!');
    } catch (error) {
      toast.error('Failed to generate suggestions');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="casting-suggestion-generator">
      <h3 className="text-xl font-bold text-white mb-4">AI Casting Suggestions</h3>
      
      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <input
          type="text"
          placeholder="Campaign Name"
          value={requirements.campaign_name}
          onChange={(e) => setRequirements({...requirements, campaign_name: e.target.value})}
          className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
        />
        <input
          type="text"
          placeholder="Category (e.g., Fashion, Beauty)"
          value={requirements.category}
          onChange={(e) => setRequirements({...requirements, category: e.target.value})}
          className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
        />
        <input
          type="text"
          placeholder="Budget"
          value={requirements.budget}
          onChange={(e) => setRequirements({...requirements, budget: e.target.value})}
          className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
        />
        <input
          type="text"
          placeholder="Special Requirements"
          value={requirements.requirements}
          onChange={(e) => setRequirements({...requirements, requirements: e.target.value})}
          className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
        />
      </div>
      
      <button
        onClick={generateSuggestions}
        disabled={loading || !requirements.campaign_name}
        className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg disabled:opacity-50"
      >
        {loading ? 'Generating...' : 'Generate Suggestions'}
      </button>

      {suggestions && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-white">Suggested Talent</h4>
            <span className="text-sm text-slate-400">
              Confidence: {suggestions.confidence_score}%
            </span>
          </div>
          
          <div className="space-y-3">
            {suggestions.suggested_talents?.map((talent, i) => (
              <div key={i} className="bg-slate-700/50 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h5 className="font-medium text-white">{talent.talent_name}</h5>
                    <p className="text-sm text-slate-400 mt-1">
                      Match Score: {talent.match_score}%
                    </p>
                  </div>
                </div>
                {talent.match_reasons?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {talent.match_reasons.map((reason, j) => (
                      <span key={j} className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded">
                        {reason}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {suggestions.ai_reasoning && (
            <div className="mt-4 bg-slate-700/30 rounded-lg p-4">
              <h5 className="text-sm font-medium text-slate-400 mb-2">AI Reasoning</h5>
              <p className="text-sm text-slate-300">{suggestions.ai_reasoning}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================
// MAIN ENTERPRISE DASHBOARD PAGE
// ============================================

export const EnterprisePhase1Dashboard = () => {
  const [activeTab, setActiveTab] = useState('executive');

  const tabs = [
    { id: 'executive', label: 'Executive Dashboard', icon: '📊' },
    { id: 'intelligence', label: 'Talent Intelligence', icon: '🧠' },
    { id: 'compliance', label: 'Compliance', icon: '🔐' },
    { id: 'workspace', label: 'Agency Workspace', icon: '🏢' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">Enterprise Command Center</h1>
          <p className="text-slate-400 mt-2">AI-Powered Talent Intelligence Platform</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
              data-testid={`tab-${tab.id}`}
            >
              <span>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {activeTab === 'executive' && (
            <>
              <ExecutiveSummaryDashboard />
              <div className="grid md:grid-cols-2 gap-6">
                <AgencyRankingsTable />
                <FraudRiskMonitor />
              </div>
            </>
          )}

          {activeTab === 'intelligence' && (
            <>
              <MarketTrendsWidget />
              <TalentScoreAnalyzer 
                modelId="demo-model-1"
                modelData={{ name: "Demo Model", categories: ["Fashion", "Commercial"] }}
              />
            </>
          )}

          {activeTab === 'compliance' && (
            <div className="grid md:grid-cols-2 gap-6">
              <ComplianceAuditTrail />
              <LicenseExpiryTracker />
            </div>
          )}

          {activeTab === 'workspace' && (
            <>
              <AgencyWorkspaceDashboard agencyId="demo-agency" />
              <CastingSuggestionGenerator agencyId="demo-agency" />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnterprisePhase1Dashboard;
