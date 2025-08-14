import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sponsorship Deal Creator
export const SponsorshipDealCreator = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    deal_name: '',
    sponsor_id: '',
    description: '',
    deal_type: 'content_sponsorship',
    base_fee: 0,
    currency: 'USD',
    payment_schedule: 'monthly',
    start_date: '',
    end_date: '',
    brand_integration_level: 'light',
    auto_renewal: false
  });
  const [sponsors, setSponsors] = useState([]);
  const [bonusRules, setBonusRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSponsors();
  }, []);

  const fetchSponsors = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/sponsors`);
      setSponsors(response.data.sponsors);
    } catch (error) {
      console.error('Error fetching sponsors:', error);
    }
  };

  const addBonusRule = () => {
    const newRule = {
      id: Date.now().toString(),
      name: '',
      bonus_type: 'performance',
      metric_type: 'views',
      rate: 0,
      threshold: 0,
      cap: 1000
    };
    setBonusRules([...bonusRules, newRule]);
  };

  const updateBonusRule = (ruleId, field, value) => {
    setBonusRules(rules => 
      rules.map(rule => 
        rule.id === ruleId ? { ...rule, [field]: value } : rule
      )
    );
  };

  const removeBonusRule = (ruleId) => {
    setBonusRules(rules => rules.filter(rule => rule.id !== ruleId));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const dealData = {
        ...formData,
        base_fee: parseFloat(formData.base_fee),
        start_date: formData.start_date,
        end_date: formData.end_date,
        bonus_rules: bonusRules.map(rule => ({
          ...rule,
          rate: parseFloat(rule.rate || 0),
          threshold: parseFloat(rule.threshold || 0),
          cap: parseFloat(rule.cap || 0),
          base_amount: parseFloat(rule.base_amount || 0)
        })),
        requirements: [],
        deliverables: [],
        content_ids: [],
        content_types: ['audio', 'video'],
        target_platforms: [],
        target_demographics: {},
        placement_requirements: {},
        kpi_targets: {}
      };

      const response = await axios.post(`${API}/sponsorship/deals`, dealData);
      
      setMessage('Sponsorship deal created successfully!');
      setFormData({
        deal_name: '',
        sponsor_id: '',
        description: '',
        deal_type: 'content_sponsorship',
        base_fee: 0,
        currency: 'USD',
        payment_schedule: 'monthly',
        start_date: '',
        end_date: '',
        brand_integration_level: 'light',
        auto_renewal: false
      });
      setBonusRules([]);
      
      if (onSuccess) onSuccess(response.data);
      
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to create sponsorship deal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6">Create Sponsorship Deal</h2>
      <p className="text-gray-600 mb-6">
        Set up a new sponsorship agreement with performance-based bonus structures.
      </p>
      
      {message && (
        <div className={`mb-6 p-4 rounded-md ${
          message.includes('successfully') 
            ? 'bg-green-100 border border-green-400 text-green-700'
            : 'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Deal Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deal Name *
            </label>
            <input
              type="text"
              value={formData.deal_name}
              onChange={(e) => setFormData({ ...formData, deal_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sponsor *
            </label>
            <select
              value={formData.sponsor_id}
              onChange={(e) => setFormData({ ...formData, sponsor_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            >
              <option value="">Select a sponsor</option>
              {sponsors.map((sponsor) => (
                <option key={sponsor.id} value={sponsor.id}>
                  {sponsor.company_name} ({sponsor.tier})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 h-24"
          />
        </div>

        {/* Deal Terms */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deal Type
            </label>
            <select
              value={formData.deal_type}
              onChange={(e) => setFormData({ ...formData, deal_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="content_sponsorship">Content Sponsorship</option>
              <option value="banner_ads">Banner Ads</option>
              <option value="platform_sponsorship">Platform Sponsorship</option>
              <option value="performance_bonus">Performance Bonus</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Base Fee ($)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.base_fee}
              onChange={(e) => setFormData({ ...formData, base_fee: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payment Schedule
            </label>
            <select
              value={formData.payment_schedule}
              onChange={(e) => setFormData({ ...formData, payment_schedule: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="milestone">Milestone-based</option>
            </select>
          </div>
        </div>

        {/* Timeline */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date *
            </label>
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date *
            </label>
            <input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
        </div>

        {/* Bonus Rules Section */}
        <div className="border-t pt-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Bonus Structure</h3>
            <button
              type="button"
              onClick={addBonusRule}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors text-sm"
            >
              Add Bonus Rule
            </button>
          </div>

          {bonusRules.map((rule) => (
            <div key={rule.id} className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-start mb-4">
                <h4 className="font-medium">Bonus Rule</h4>
                <button
                  type="button"
                  onClick={() => removeBonusRule(rule.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Remove
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rule Name
                  </label>
                  <input
                    type="text"
                    value={rule.name}
                    onChange={(e) => updateBonusRule(rule.id, 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                    placeholder="e.g., Views Bonus"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bonus Type
                  </label>
                  <select
                    value={rule.bonus_type}
                    onChange={(e) => updateBonusRule(rule.id, 'bonus_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  >
                    <option value="performance">Performance</option>
                    <option value="milestone">Milestone</option>
                    <option value="fixed">Fixed</option>
                    <option value="tiered">Tiered</option>
                    <option value="revenue_share">Revenue Share</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Metric Type
                  </label>
                  <select
                    value={rule.metric_type}
                    onChange={(e) => updateBonusRule(rule.id, 'metric_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  >
                    <option value="views">Views</option>
                    <option value="downloads">Downloads</option>
                    <option value="streams">Streams</option>
                    <option value="engagement">Engagement</option>
                    <option value="clicks">Clicks</option>
                    <option value="conversions">Conversions</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rate/Amount ($)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={rule.rate}
                    onChange={(e) => updateBonusRule(rule.id, 'rate', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                    placeholder="0.001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Threshold
                  </label>
                  <input
                    type="number"
                    value={rule.threshold}
                    onChange={(e) => updateBonusRule(rule.id, 'threshold', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                    placeholder="1000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cap ($)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={rule.cap}
                    onChange={(e) => updateBonusRule(rule.id, 'cap', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                    placeholder="1000"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Creating Deal...' : 'Create Sponsorship Deal'}
        </button>
      </form>
    </div>
  );
};

// Sponsorship Deals List
export const SponsorshipDealsList = () => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchDeals();
  }, [filter]);

  const fetchDeals = async () => {
    try {
      const params = new URLSearchParams();
      if (filter) params.append('status', filter);
      
      const response = await axios.get(`${API}/sponsorship/deals?${params}`);
      setDeals(response.data.deals);
    } catch (error) {
      console.error('Error fetching deals:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-600';
      case 'pending': return 'bg-yellow-100 text-yellow-600';
      case 'completed': return 'bg-blue-100 text-blue-600';
      case 'cancelled': return 'bg-red-100 text-red-600';
      case 'paused': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
        <p className="text-center mt-4 text-gray-600">Loading sponsorship deals...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">My Sponsorship Deals</h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="pending">Pending</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      {deals.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">🤝</div>
          <p className="text-gray-600">No sponsorship deals found. Create your first deal above.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {deals.map((deal) => (
            <div key={deal.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">{deal.deal_name}</h3>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(deal.status)}`}>
                  {deal.status.toUpperCase()}
                </span>
              </div>
              
              <div className="text-sm text-gray-600 mb-3">
                <p><strong>Sponsor:</strong> {deal.sponsor?.company_name || 'Unknown'}</p>
                <p><strong>Type:</strong> {deal.deal_type.replace('_', ' ')}</p>
                <p><strong>Base Fee:</strong> ${deal.base_fee}</p>
              </div>

              <div className="text-xs text-gray-500 mb-3">
                <p>Start: {new Date(deal.start_date).toLocaleDateString()}</p>
                <p>End: {new Date(deal.end_date).toLocaleDateString()}</p>
              </div>

              <div className="flex justify-between items-center">
                <div className="text-sm">
                  <span className="font-medium">{deal.bonus_rules?.length || 0}</span> bonus rules
                </div>
                <button className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm transition-colors">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Performance Metrics Tracker
export const PerformanceTracker = ({ dealId }) => {
  const [metrics, setMetrics] = useState({});
  const [newMetric, setNewMetric] = useState({
    metric_type: 'views',
    metric_value: '',
    platform: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (dealId) {
      fetchMetrics();
    }
  }, [dealId]);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/deals/${dealId}/metrics`);
      setMetrics(response.data.metrics_by_type);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const recordMetric = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const metricData = {
        deal_id: dealId,
        metric_type: newMetric.metric_type,
        metric_value: parseFloat(newMetric.metric_value),
        platform: newMetric.platform || null,
        measurement_date: new Date().toISOString().split('T')[0]
      };

      await axios.post(`${API}/sponsorship/metrics`, metricData);
      
      setMessage('Performance metric recorded successfully!');
      setNewMetric({
        metric_type: 'views',
        metric_value: '',
        platform: ''
      });
      
      fetchMetrics(); // Refresh metrics
      
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to record metric');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6">Performance Tracking</h2>
      
      {/* Record New Metric */}
      <div className="border-b pb-6 mb-6">
        <h3 className="text-lg font-medium mb-4">Record New Metric</h3>
        
        {message && (
          <div className={`mb-4 p-3 rounded-md text-sm ${
            message.includes('successfully') 
              ? 'bg-green-100 border border-green-400 text-green-700'
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}>
            {message}
          </div>
        )}
        
        <form onSubmit={recordMetric} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Metric Type
            </label>
            <select
              value={newMetric.metric_type}
              onChange={(e) => setNewMetric({ ...newMetric, metric_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
            >
              <option value="views">Views</option>
              <option value="downloads">Downloads</option>
              <option value="streams">Streams</option>
              <option value="engagement">Engagement</option>
              <option value="clicks">Clicks</option>
              <option value="conversions">Conversions</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Value
            </label>
            <input
              type="number"
              value={newMetric.metric_value}
              onChange={(e) => setNewMetric({ ...newMetric, metric_value: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Platform (Optional)
            </label>
            <input
              type="text"
              value={newMetric.platform}
              onChange={(e) => setNewMetric({ ...newMetric, platform: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
              placeholder="e.g., Instagram"
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md transition-colors disabled:opacity-50 text-sm"
            >
              {loading ? 'Recording...' : 'Record'}
            </button>
          </div>
        </form>
      </div>

      {/* Metrics Display */}
      <div>
        <h3 className="text-lg font-medium mb-4">Recent Performance</h3>
        {Object.keys(metrics).length === 0 ? (
          <p className="text-gray-500">No metrics recorded yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(metrics).map(([metricType, metricData]) => {
              const totalValue = metricData.reduce((sum, m) => sum + m.metric_value, 0);
              const latestValue = metricData[metricData.length - 1]?.metric_value || 0;
              
              return (
                <div key={metricType} className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium capitalize mb-2">{metricType}</h4>
                  <div className="text-2xl font-bold text-purple-600 mb-1">
                    {totalValue.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">
                    Latest: {latestValue.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {metricData.length} data points
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

// Bonus Calculator and Display
export const BonusCalculator = ({ dealId }) => {
  const [bonuses, setBonuses] = useState([]);
  const [calculationPeriod, setCalculationPeriod] = useState({
    start_date: '',
    end_date: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (dealId) {
      fetchBonuses();
    }
  }, [dealId]);

  const fetchBonuses = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/deals/${dealId}/bonuses`);
      setBonuses(response.data.calculations);
    } catch (error) {
      console.error('Error fetching bonuses:', error);
    }
  };

  const calculateBonuses = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post(`${API}/sponsorship/deals/${dealId}/calculate-bonuses`, {
        period_start: calculationPeriod.start_date,
        period_end: calculationPeriod.end_date
      });
      
      setMessage(`Bonuses calculated successfully! Total: $${response.data.total_bonus_amount.toFixed(2)}`);
      fetchBonuses(); // Refresh bonus list
      
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to calculate bonuses');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6">Bonus Calculator</h2>
      
      {/* Calculate New Bonuses */}
      <div className="border-b pb-6 mb-6">
        <h3 className="text-lg font-medium mb-4">Calculate Period Bonuses</h3>
        
        {message && (
          <div className={`mb-4 p-3 rounded-md text-sm ${
            message.includes('successfully') 
              ? 'bg-green-100 border border-green-400 text-green-700'
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}>
            {message}
          </div>
        )}
        
        <form onSubmit={calculateBonuses} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Period Start
            </label>
            <input
              type="date"
              value={calculationPeriod.start_date}
              onChange={(e) => setCalculationPeriod({ ...calculationPeriod, start_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Period End
            </label>
            <input
              type="date"
              value={calculationPeriod.end_date}
              onChange={(e) => setCalculationPeriod({ ...calculationPeriod, end_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
              required
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors disabled:opacity-50 text-sm"
            >
              {loading ? 'Calculating...' : 'Calculate Bonuses'}
            </button>
          </div>
        </form>
      </div>

      {/* Bonus History */}
      <div>
        <h3 className="text-lg font-medium mb-4">Bonus History</h3>
        {bonuses.length === 0 ? (
          <p className="text-gray-500">No bonuses calculated yet.</p>
        ) : (
          <div className="space-y-4">
            {bonuses.map((bonus) => (
              <div key={bonus.id} className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="font-medium">
                      ${bonus.bonus_amount?.toFixed(2) || '0.00'}
                    </div>
                    <div className="text-sm text-gray-600">
                      {new Date(bonus.period_start).toLocaleDateString()} - {new Date(bonus.period_end).toLocaleDateString()}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    bonus.is_approved 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-yellow-100 text-yellow-600'
                  }`}>
                    {bonus.is_approved ? 'Approved' : 'Pending'}
                  </span>
                </div>
                
                <div className="text-sm text-gray-500">
                  Method: {bonus.calculation_method}
                  {bonus.threshold_met === false && (
                    <span className="ml-2 text-red-500">• Threshold not met</span>
                  )}
                  {bonus.cap_applied && (
                    <span className="ml-2 text-orange-500">• Cap applied</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Admin Sponsorship Overview
export const SponsorshipAdminDashboard = () => {
  const [overview, setOverview] = useState({});
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
    fetchAllDeals();
  }, []);

  const fetchOverview = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/admin/overview`);
      setOverview(response.data);
    } catch (error) {
      console.error('Error fetching overview:', error);
    }
  };

  const fetchAllDeals = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/admin/deals?limit=10`);
      setDeals(response.data.deals);
    } catch (error) {
      console.error('Error fetching deals:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
        <p className="text-center mt-4 text-gray-600">Loading sponsorship overview...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Sponsors</p>
              <p className="text-3xl font-bold text-purple-600">{overview.overview?.total_sponsors || 0}</p>
              <p className="text-sm text-green-600">{overview.overview?.active_sponsors || 0} active</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Deals</p>
              <p className="text-3xl font-bold text-blue-600">{overview.overview?.total_deals || 0}</p>
              <p className="text-sm text-green-600">{overview.overview?.active_deals || 0} active</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Payouts</p>
              <p className="text-3xl font-bold text-green-600">${overview.overview?.total_payouts?.toFixed(2) || '0.00'}</p>
              <p className="text-sm text-gray-500">All time</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Avg Deal Value</p>
              <p className="text-3xl font-bold text-orange-600">${overview.overview?.average_deal_value?.toFixed(2) || '0.00'}</p>
              <p className="text-sm text-gray-500">Per deal</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Deals */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Sponsorship Deals</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deal</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sponsor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Creator</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {deals.map((deal) => (
                <tr key={deal.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {deal.deal_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {deal.sponsor?.company_name || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {deal.creator?.full_name || deal.creator?.email || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${deal.base_fee}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      deal.status === 'active' ? 'bg-green-100 text-green-800' :
                      deal.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      deal.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {deal.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(deal.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};