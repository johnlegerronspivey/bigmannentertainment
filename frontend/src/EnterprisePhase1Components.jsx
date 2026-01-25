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
// ZERO-TRUST COMPLIANCE COMPONENTS
// ============================================

// Release Verification Component
export const ReleaseVerificationForm = ({ onVerify }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    release_id: '',
    model_name: '',
    photographer_name: '',
    brand_name: '',
    location: '',
    has_model_consent: false,
    has_photographer_consent: false,
    has_brand_clearance: false,
    has_location_clearance: false,
    is_minor: false,
    has_guardian_consent: false,
    usage_scope: 'commercial',
    duration_days: 365,
    territories: 'worldwide'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const releaseId = formData.release_id || `release-${Date.now()}`;
      const response = await fetch(`${API}/enterprise/compliance/verify-release/${releaseId}?actor_id=current-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setResult(data);
      onVerify?.(data);
      toast.success(`Release verification: ${data.status}`);
    } catch (error) {
      toast.error('Failed to verify release');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'failed': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="release-verification-form">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">📝</span> Release Verification
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Release ID (optional)</label>
            <input
              type="text"
              value={formData.release_id}
              onChange={(e) => setFormData({...formData, release_id: e.target.value})}
              placeholder="Auto-generated if empty"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="release-id-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Model Name *</label>
            <input
              type="text"
              value={formData.model_name}
              onChange={(e) => setFormData({...formData, model_name: e.target.value})}
              placeholder="e.g., Jane Doe"
              required
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="model-name-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Photographer Name</label>
            <input
              type="text"
              value={formData.photographer_name}
              onChange={(e) => setFormData({...formData, photographer_name: e.target.value})}
              placeholder="e.g., John Smith"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="photographer-name-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Brand Name</label>
            <input
              type="text"
              value={formData.brand_name}
              onChange={(e) => setFormData({...formData, brand_name: e.target.value})}
              placeholder="e.g., Fashion Brand Co"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="brand-name-input"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.has_model_consent}
              onChange={(e) => setFormData({...formData, has_model_consent: e.target.checked})}
              className="rounded border-slate-500"
            />
            Model Consent
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.has_photographer_consent}
              onChange={(e) => setFormData({...formData, has_photographer_consent: e.target.checked})}
              className="rounded border-slate-500"
            />
            Photographer Consent
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.has_brand_clearance}
              onChange={(e) => setFormData({...formData, has_brand_clearance: e.target.checked})}
              className="rounded border-slate-500"
            />
            Brand Clearance
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.has_location_clearance}
              onChange={(e) => setFormData({...formData, has_location_clearance: e.target.checked})}
              className="rounded border-slate-500"
            />
            Location Clearance
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.is_minor}
              onChange={(e) => setFormData({...formData, is_minor: e.target.checked})}
              className="rounded border-slate-500"
            />
            Minor (Under 18)
          </label>
          {formData.is_minor && (
            <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.has_guardian_consent}
                onChange={(e) => setFormData({...formData, has_guardian_consent: e.target.checked})}
                className="rounded border-slate-500"
              />
              Guardian Consent
            </label>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Usage Scope</label>
            <select
              value={formData.usage_scope}
              onChange={(e) => setFormData({...formData, usage_scope: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            >
              <option value="commercial">Commercial</option>
              <option value="editorial">Editorial</option>
              <option value="personal">Personal</option>
              <option value="advertising">Advertising</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Duration (Days)</label>
            <input
              type="number"
              value={formData.duration_days}
              onChange={(e) => setFormData({...formData, duration_days: parseInt(e.target.value)})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Territories</label>
            <input
              type="text"
              value={formData.territories}
              onChange={(e) => setFormData({...formData, territories: e.target.value})}
              placeholder="e.g., worldwide, USA, EU"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg disabled:opacity-50 font-medium"
          data-testid="verify-release-btn"
        >
          {loading ? 'Verifying...' : 'Verify Release'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-4 rounded-lg border ${getStatusColor(result.status)}`} data-testid="verification-result">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-bold text-lg">Status: {result.status?.toUpperCase()}</h4>
              <p className="text-sm opacity-80">Release ID: {result.release_id}</p>
            </div>
            <span className="text-xs opacity-60">{new Date(result.verification_date).toLocaleString()}</span>
          </div>
          
          <div className="grid grid-cols-2 gap-2 mt-3 text-sm">
            <div>Model Consent: {result.model_consent ? '✅' : '❌'}</div>
            <div>Photographer: {result.photographer_consent ? '✅' : '❌'}</div>
            <div>Brand Clearance: {result.brand_clearance ? '✅' : '❌'}</div>
            <div>Location: {result.location_clearance ? '✅' : '❌'}</div>
          </div>

          {result.issues?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-current/20">
              <p className="font-medium text-sm">Issues Found:</p>
              <ul className="text-sm list-disc list-inside opacity-80">
                {result.issues.map((issue, i) => <li key={i}>{issue}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Identity Verification Component
export const IdentityVerificationForm = ({ onVerify }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    user_id: '',
    full_name: '',
    id_type: 'passport',
    id_number: '',
    date_of_birth: '',
    has_id_document: false,
    has_selfie: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const userId = formData.user_id || `user-${Date.now()}`;
      const response = await fetch(`${API}/enterprise/compliance/verify-identity/${userId}?actor_id=current-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          full_name: formData.full_name,
          id_type: formData.id_type,
          id_number: formData.id_number,
          date_of_birth: formData.date_of_birth,
          id_document: formData.has_id_document,
          selfie: formData.has_selfie
        })
      });
      const data = await response.json();
      setResult(data);
      onVerify?.(data);
      toast.success(`Identity verification: ${data.verification_status}`);
    } catch (error) {
      toast.error('Failed to verify identity');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'failed': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'requires_resubmission': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="identity-verification-form">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">🪪</span> Identity Verification
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">User ID (optional)</label>
            <input
              type="text"
              value={formData.user_id}
              onChange={(e) => setFormData({...formData, user_id: e.target.value})}
              placeholder="Auto-generated if empty"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="user-id-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Full Name *</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              placeholder="Legal name as on ID"
              required
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="full-name-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">ID Type</label>
            <select
              value={formData.id_type}
              onChange={(e) => setFormData({...formData, id_type: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            >
              <option value="passport">Passport</option>
              <option value="drivers_license">Drivers License</option>
              <option value="national_id">National ID</option>
              <option value="state_id">State ID</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">ID Number</label>
            <input
              type="text"
              value={formData.id_number}
              onChange={(e) => setFormData({...formData, id_number: e.target.value})}
              placeholder="Document number"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="id-number-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Date of Birth *</label>
            <input
              type="date"
              value={formData.date_of_birth}
              onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
              required
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="dob-input"
            />
          </div>
        </div>

        <div className="flex gap-6">
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.has_id_document}
              onChange={(e) => setFormData({...formData, has_id_document: e.target.checked})}
              className="rounded border-slate-500"
            />
            ID Document Uploaded
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.has_selfie}
              onChange={(e) => setFormData({...formData, has_selfie: e.target.checked})}
              className="rounded border-slate-500"
            />
            Selfie Verification
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg disabled:opacity-50 font-medium"
          data-testid="verify-identity-btn"
        >
          {loading ? 'Verifying...' : 'Verify Identity'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-4 rounded-lg border ${getStatusColor(result.verification_status)}`} data-testid="identity-result">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-bold text-lg">Status: {result.verification_status?.toUpperCase()}</h4>
              <p className="text-sm opacity-80">User ID: {result.user_id}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-2 mt-3 text-sm">
            <div>Age Verified: {result.age_verified ? '✅' : '❌'}</div>
            <div>DOB Verified: {result.date_of_birth_verified ? '✅' : '❌'}</div>
            <div>Is Minor: {result.is_minor ? '⚠️ Yes' : 'No'}</div>
            {result.is_minor && <div>Guardian Consent: {result.guardian_consent_if_minor ? '✅' : '❌'}</div>}
          </div>

          {result.expiry_date && (
            <p className="text-xs opacity-60 mt-2">
              Expires: {new Date(result.expiry_date).toLocaleDateString()}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

// Fraud Detection Component
export const FraudDetectionPanel = ({ onDetect }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    upload_id: '',
    file_name: '',
    file_hash: '',
    file_size: 0,
    uploader_id: '',
    upload_source: 'web',
    metadata: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const uploadId = formData.upload_id || `upload-${Date.now()}`;
      const response = await fetch(`${API}/enterprise/compliance/detect-fraud/${uploadId}?actor_id=current-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          file_name: formData.file_name,
          file_hash: formData.file_hash,
          file_size: formData.file_size,
          uploader_id: formData.uploader_id,
          upload_source: formData.upload_source,
          metadata: formData.metadata
        })
      });
      const data = await response.json();
      setResult(data);
      onDetect?.(data);
      toast.success(`Fraud detection complete: ${data.risk_level} risk`);
    } catch (error) {
      toast.error('Failed to run fraud detection');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-600/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-600/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-600/20 text-blue-400 border-blue-500/30';
      default: return 'bg-green-600/20 text-green-400 border-green-500/30';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="fraud-detection-panel">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">🔍</span> Fraud Detection
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Upload ID (optional)</label>
            <input
              type="text"
              value={formData.upload_id}
              onChange={(e) => setFormData({...formData, upload_id: e.target.value})}
              placeholder="Auto-generated if empty"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="upload-id-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">File Name *</label>
            <input
              type="text"
              value={formData.file_name}
              onChange={(e) => setFormData({...formData, file_name: e.target.value})}
              placeholder="e.g., photo_001.jpg"
              required
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="file-name-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">File Hash (SHA256)</label>
            <input
              type="text"
              value={formData.file_hash}
              onChange={(e) => setFormData({...formData, file_hash: e.target.value})}
              placeholder="For duplicate detection"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">File Size (bytes)</label>
            <input
              type="number"
              value={formData.file_size}
              onChange={(e) => setFormData({...formData, file_size: parseInt(e.target.value) || 0})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Uploader ID</label>
            <input
              type="text"
              value={formData.uploader_id}
              onChange={(e) => setFormData({...formData, uploader_id: e.target.value})}
              placeholder="User who uploaded"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Upload Source</label>
            <select
              value={formData.upload_source}
              onChange={(e) => setFormData({...formData, upload_source: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            >
              <option value="web">Web Upload</option>
              <option value="mobile">Mobile App</option>
              <option value="api">API Integration</option>
              <option value="bulk">Bulk Import</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-1">Additional Metadata (JSON)</label>
          <textarea
            value={formData.metadata}
            onChange={(e) => setFormData({...formData, metadata: e.target.value})}
            placeholder='{"camera": "Canon EOS", "location": "NYC"}'
            rows={2}
            className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white text-sm"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-lg disabled:opacity-50 font-medium"
          data-testid="detect-fraud-btn"
        >
          {loading ? 'Analyzing...' : 'Run Fraud Detection'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-4 rounded-lg border ${getRiskColor(result.risk_level)}`} data-testid="fraud-result">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-bold text-lg">Risk Level: {result.risk_level?.toUpperCase()}</h4>
              <p className="text-sm opacity-80">Upload ID: {result.upload_id}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-2 mt-3 text-sm">
            <div>Duplicate: {result.is_duplicate ? `⚠️ Yes (${result.duplicate_of})` : '✅ No'}</div>
            <div>AI Generated: {result.ai_generated_probability}%</div>
            <div>Similarity Score: {result.similarity_score}%</div>
            <div>Metadata Tampered: {result.metadata_tampering_detected ? '⚠️ Yes' : '✅ No'}</div>
          </div>

          {result.copyright_match && (
            <p className="text-sm mt-2 text-yellow-400">Copyright Match: {result.copyright_match}</p>
          )}

          {result.flags?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-current/20">
              <p className="font-medium text-sm">Flags:</p>
              <ul className="text-sm list-disc list-inside opacity-80">
                {result.flags.map((flag, i) => <li key={i}>{flag}</li>)}
              </ul>
            </div>
          )}

          {result.recommended_action && (
            <p className="mt-2 text-sm font-medium">Recommended: {result.recommended_action}</p>
          )}
        </div>
      )}
    </div>
  );
};

// Privacy Compliance Check Component
export const PrivacyComplianceChecker = ({ onCheck }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    entity_id: '',
    entity_type: 'user',
    entity_name: '',
    data_types: [],
    has_consent: false,
    supports_erasure: false,
    supports_portability: false,
    regions: []
  });

  const regionOptions = [
    { value: 'EU', label: 'European Union (GDPR)' },
    { value: 'US-CA', label: 'California (CCPA)' },
    { value: 'Brazil', label: 'Brazil (LGPD)' },
    { value: 'Canada', label: 'Canada (PIPEDA)' },
    { value: 'Japan', label: 'Japan (APPI)' },
    { value: 'UK', label: 'United Kingdom (UK GDPR)' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const entityId = formData.entity_id || `entity-${Date.now()}`;
      const regionsParam = formData.regions.join(',');
      const response = await fetch(`${API}/enterprise/compliance/check-privacy/${entityId}?actor_id=current-user&entity_type=${formData.entity_type}&regions=${regionsParam}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: formData.entity_name,
          data_types: formData.data_types,
          consent_collected: formData.has_consent,
          right_to_erasure_supported: formData.supports_erasure,
          data_portability_supported: formData.supports_portability
        })
      });
      const data = await response.json();
      setResult(data);
      onCheck?.(data);
      toast.success(`Privacy compliance: ${data.status}`);
    } catch (error) {
      toast.error('Failed to check privacy compliance');
    } finally {
      setLoading(false);
    }
  };

  const toggleRegion = (region) => {
    setFormData(prev => ({
      ...prev,
      regions: prev.regions.includes(region)
        ? prev.regions.filter(r => r !== region)
        : [...prev.regions, region]
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'compliant': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'non_compliant': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'pending_review': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'requires_action': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="privacy-compliance-checker">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">🌍</span> Privacy Compliance Check
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Entity ID (optional)</label>
            <input
              type="text"
              value={formData.entity_id}
              onChange={(e) => setFormData({...formData, entity_id: e.target.value})}
              placeholder="Auto-generated if empty"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="entity-id-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Entity Type</label>
            <select
              value={formData.entity_type}
              onChange={(e) => setFormData({...formData, entity_type: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            >
              <option value="user">User</option>
              <option value="model">Model/Talent</option>
              <option value="agency">Agency</option>
              <option value="campaign">Campaign</option>
              <option value="asset">Asset</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Entity Name *</label>
            <input
              type="text"
              value={formData.entity_name}
              onChange={(e) => setFormData({...formData, entity_name: e.target.value})}
              placeholder="Name or identifier"
              required
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="entity-name-input"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-2">Applicable Regions</label>
          <div className="flex flex-wrap gap-2">
            {regionOptions.map(region => (
              <button
                key={region.value}
                type="button"
                onClick={() => toggleRegion(region.value)}
                className={`px-3 py-1.5 rounded text-sm transition-colors ${
                  formData.regions.includes(region.value)
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {region.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.has_consent}
              onChange={(e) => setFormData({...formData, has_consent: e.target.checked})}
              className="rounded border-slate-500"
            />
            Consent Collected
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.supports_erasure}
              onChange={(e) => setFormData({...formData, supports_erasure: e.target.checked})}
              className="rounded border-slate-500"
            />
            Right to Erasure
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.supports_portability}
              onChange={(e) => setFormData({...formData, supports_portability: e.target.checked})}
              className="rounded border-slate-500"
            />
            Data Portability
          </label>
        </div>

        <button
          type="submit"
          disabled={loading || formData.regions.length === 0}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-lg disabled:opacity-50 font-medium"
          data-testid="check-privacy-btn"
        >
          {loading ? 'Checking...' : 'Check Privacy Compliance'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-4 rounded-lg border ${getStatusColor(result.status)}`} data-testid="privacy-result">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-bold text-lg">Status: {result.status?.toUpperCase().replace('_', ' ')}</h4>
              <p className="text-sm opacity-80">Entity: {result.entity_type} - {result.entity_id}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-3 text-sm">
            <div>GDPR: {result.gdpr_compliant ? '✅' : '❌'}</div>
            <div>CCPA: {result.ccpa_compliant ? '✅' : '❌'}</div>
            <div>COPPA: {result.coppa_compliant ? '✅' : '❌'}</div>
            <div>Data Retention: {result.data_retention_compliant ? '✅' : '❌'}</div>
            <div>Consent: {result.consent_collected ? '✅' : '❌'}</div>
            <div>Erasure: {result.right_to_erasure_supported ? '✅' : '❌'}</div>
          </div>

          {result.issues?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-current/20">
              <p className="font-medium text-sm">Issues:</p>
              <ul className="text-sm list-disc list-inside opacity-80">
                {result.issues.map((issue, i) => <li key={i}>{issue}</li>)}
              </ul>
            </div>
          )}

          {result.remediation_steps?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-current/20">
              <p className="font-medium text-sm text-green-400">Remediation Steps:</p>
              <ol className="text-sm list-decimal list-inside opacity-80">
                {result.remediation_steps.map((step, i) => <li key={i}>{step}</li>)}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Usage Rights Validation Component
export const UsageRightsValidator = ({ onValidate }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    asset_id: '',
    asset_name: '',
    requested_use: 'commercial',
    requested_territory: 'worldwide',
    requested_duration: 365,
    is_exclusive: false,
    intended_platform: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const assetId = formData.asset_id || `asset-${Date.now()}`;
      const response = await fetch(`${API}/enterprise/compliance/validate-usage-rights/${assetId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          requested_use: {
            use_type: formData.requested_use,
            territory: formData.requested_territory,
            duration_days: formData.requested_duration,
            exclusive: formData.is_exclusive,
            platform: formData.intended_platform,
            asset_name: formData.asset_name
          },
          actor_id: 'current-user'
        })
      });
      const data = await response.json();
      setResult(data);
      onValidate?.(data);
      toast.success(`Usage rights: ${data.status}`);
    } catch (error) {
      toast.error('Failed to validate usage rights');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'compliant': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'non_compliant': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'pending_review': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'requires_action': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6" data-testid="usage-rights-validator">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className="text-2xl">⚖️</span> Usage Rights Validation
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Asset ID (optional)</label>
            <input
              type="text"
              value={formData.asset_id}
              onChange={(e) => setFormData({...formData, asset_id: e.target.value})}
              placeholder="Auto-generated if empty"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="asset-id-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Asset Name *</label>
            <input
              type="text"
              value={formData.asset_name}
              onChange={(e) => setFormData({...formData, asset_name: e.target.value})}
              placeholder="e.g., Summer Campaign Photo Set"
              required
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              data-testid="asset-name-input"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Requested Use</label>
            <select
              value={formData.requested_use}
              onChange={(e) => setFormData({...formData, requested_use: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            >
              <option value="commercial">Commercial</option>
              <option value="editorial">Editorial</option>
              <option value="advertising">Advertising</option>
              <option value="social_media">Social Media</option>
              <option value="broadcast">Broadcast/TV</option>
              <option value="print">Print</option>
              <option value="digital">Digital Only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Territory</label>
            <select
              value={formData.requested_territory}
              onChange={(e) => setFormData({...formData, requested_territory: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            >
              <option value="worldwide">Worldwide</option>
              <option value="north_america">North America</option>
              <option value="europe">Europe</option>
              <option value="asia_pacific">Asia Pacific</option>
              <option value="usa_only">USA Only</option>
              <option value="uk_only">UK Only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Duration (Days)</label>
            <input
              type="number"
              value={formData.requested_duration}
              onChange={(e) => setFormData({...formData, requested_duration: parseInt(e.target.value) || 0})}
              min="1"
              max="3650"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Intended Platform</label>
            <input
              type="text"
              value={formData.intended_platform}
              onChange={(e) => setFormData({...formData, intended_platform: e.target.value})}
              placeholder="e.g., Instagram, Website, Billboard"
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
            />
          </div>
        </div>

        <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={formData.is_exclusive}
            onChange={(e) => setFormData({...formData, is_exclusive: e.target.checked})}
            className="rounded border-slate-500"
          />
          Request Exclusive Rights
        </label>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-3 rounded-lg disabled:opacity-50 font-medium"
          data-testid="validate-rights-btn"
        >
          {loading ? 'Validating...' : 'Validate Usage Rights'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-4 rounded-lg border ${getStatusColor(result.status)}`} data-testid="rights-result">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-bold text-lg">Status: {result.status?.toUpperCase().replace('_', ' ')}</h4>
              <p className="text-sm opacity-80">Asset ID: {result.asset_id}</p>
            </div>
          </div>
          
          <div className="mt-3">
            {result.allowed_uses?.length > 0 && (
              <div className="mb-2">
                <span className="text-sm font-medium text-green-400">Allowed Uses: </span>
                <span className="text-sm">{result.allowed_uses.join(', ')}</span>
              </div>
            )}
            {result.restricted_uses?.length > 0 && (
              <div className="mb-2">
                <span className="text-sm font-medium text-red-400">Restricted: </span>
                <span className="text-sm">{result.restricted_uses.join(', ')}</span>
              </div>
            )}
            {result.territories?.length > 0 && (
              <div className="mb-2">
                <span className="text-sm font-medium">Territories: </span>
                <span className="text-sm">{result.territories.join(', ')}</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2 mt-3 text-sm">
            <div>Exclusivity: {result.exclusivity ? '✅ Yes' : 'No'}</div>
            <div>Duration: {result.duration_days} days</div>
            <div>Auto-renewal: {result.auto_renewal ? '✅' : '❌'}</div>
            {result.renewal_price > 0 && <div>Renewal: ${result.renewal_price}</div>}
          </div>

          {result.end_date && (
            <p className="text-xs opacity-60 mt-2">
              Valid until: {new Date(result.end_date).toLocaleDateString()}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

// Compliance Dashboard - Main Component that combines all
export const ZeroTrustComplianceDashboard = () => {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'release', label: 'Release Verification', icon: '📝' },
    { id: 'identity', label: 'Identity Verification', icon: '🪪' },
    { id: 'usage', label: 'Usage Rights', icon: '⚖️' },
    { id: 'fraud', label: 'Fraud Detection', icon: '🔍' },
    { id: 'privacy', label: 'Privacy Compliance', icon: '🌍' },
    { id: 'audit', label: 'Audit Trail', icon: '📋' },
    { id: 'licenses', label: 'License Expiry', icon: '⏰' }
  ];

  return (
    <div className="space-y-6" data-testid="zero-trust-compliance-dashboard">
      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 p-2 bg-slate-800/50 rounded-lg">
        {sections.map(section => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              activeSection === section.id
                ? 'bg-purple-600 text-white'
                : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
            }`}
            data-testid={`tab-${section.id}`}
          >
            <span>{section.icon}</span>
            <span className="hidden sm:inline">{section.label}</span>
          </button>
        ))}
      </div>

      {/* Content Sections */}
      {activeSection === 'overview' && (
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-600/20 to-green-800/20 rounded-lg p-6 border border-green-500/20">
            <h4 className="text-green-400 font-medium mb-2">Verified Releases</h4>
            <p className="text-3xl font-bold text-white">-</p>
            <p className="text-sm text-slate-400 mt-1">This month</p>
          </div>
          <div className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 rounded-lg p-6 border border-blue-500/20">
            <h4 className="text-blue-400 font-medium mb-2">Identity Verified</h4>
            <p className="text-3xl font-bold text-white">-</p>
            <p className="text-sm text-slate-400 mt-1">Active users</p>
          </div>
          <div className="bg-gradient-to-br from-orange-600/20 to-orange-800/20 rounded-lg p-6 border border-orange-500/20">
            <h4 className="text-orange-400 font-medium mb-2">Fraud Alerts</h4>
            <p className="text-3xl font-bold text-white">-</p>
            <p className="text-sm text-slate-400 mt-1">Pending review</p>
          </div>
          <div className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 rounded-lg p-6 border border-purple-500/20">
            <h4 className="text-purple-400 font-medium mb-2">Compliance Rate</h4>
            <p className="text-3xl font-bold text-white">-</p>
            <p className="text-sm text-slate-400 mt-1">GDPR/CCPA</p>
          </div>
        </div>
      )}

      {activeSection === 'release' && <ReleaseVerificationForm />}
      {activeSection === 'identity' && <IdentityVerificationForm />}
      {activeSection === 'usage' && <UsageRightsValidator />}
      {activeSection === 'fraud' && <FraudDetectionPanel />}
      {activeSection === 'privacy' && <PrivacyComplianceChecker />}
      {activeSection === 'audit' && <ComplianceAuditTrail />}
      {activeSection === 'licenses' && <LicenseExpiryTracker />}
    </div>
  );
};

// ============================================
// COMPLIANCE COMPONENTS (Legacy)
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
            <ZeroTrustComplianceDashboard />
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
