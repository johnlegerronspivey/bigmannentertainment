import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Sponsorship Dashboard - Main hub for users
export const SponsorshipDashboard = () => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchUserDeals();
    fetchUserStats();
  }, []);

  const fetchUserDeals = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/deals`);
      setDeals(response.data.deals);
    } catch (error) {
      console.error('Error fetching deals:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserStats = async () => {
    try {
      // Calculate user stats from deals
      const activeDeals = deals.filter(deal => deal.status === 'active').length;
      const totalEarnings = deals.reduce((sum, deal) => sum + (deal.base_fee || 0), 0);
      
      setStats({
        totalDeals: deals.length,
        activeDeals,
        totalEarnings,
        avgDealValue: totalEarnings / Math.max(deals.length, 1)
      });
    } catch (error) {
      console.error('Error calculating stats:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-800',
      'pending': 'bg-yellow-100 text-yellow-800',
      'active': 'bg-green-100 text-green-800',
      'paused': 'bg-orange-100 text-orange-800',
      'completed': 'bg-blue-100 text-blue-800',
      'cancelled': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading sponsorship dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Sponsorship Dashboard</h1>
          <p className="text-gray-600">Manage your sponsorship deals and track your earnings</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Deals</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalDeals || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Deals</p>
                <p className="text-2xl font-bold text-gray-900">{stats.activeDeals || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Earnings</p>
                <p className="text-2xl font-bold text-gray-900">${(stats.totalEarnings || 0).toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg Deal Value</p>
                <p className="text-2xl font-bold text-gray-900">${(stats.avgDealValue || 0).toFixed(2)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Deals */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Recent Sponsorship Deals</h2>
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors">
                View All Deals
              </button>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            {deals.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No sponsorship deals</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by creating your first sponsorship deal.</p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deal Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sponsor</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Base Fee</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {deals.slice(0, 5).map((deal) => (
                    <tr key={deal.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{deal.deal_name}</div>
                        <div className="text-sm text-gray-500">{deal.deal_type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{deal.sponsor?.company_name || 'Unknown'}</div>
                        <div className="text-sm text-gray-500">{deal.sponsor?.brand_name || ''}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${(deal.base_fee || 0).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(deal.status)}`}>
                          {deal.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-purple-600 hover:text-purple-900 mr-3">View</button>
                        <button className="text-blue-600 hover:text-blue-900">Edit</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

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

// Performance Metrics Recorder
export const MetricsRecorder = ({ dealId, onMetricRecorded }) => {
  const [formData, setFormData] = useState({
    metric_type: 'views',
    metric_value: '',
    platform: '',
    source: 'organic'
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const metricTypes = [
    { value: 'views', label: 'Views' },
    { value: 'downloads', label: 'Downloads' },
    { value: 'streams', label: 'Streams' },
    { value: 'engagement', label: 'Engagement' },
    { value: 'clicks', label: 'Clicks' },
    { value: 'conversions', label: 'Conversions' },
    { value: 'revenue', label: 'Revenue' },
    { value: 'shares', label: 'Shares' },
    { value: 'comments', label: 'Comments' },
    { value: 'likes', label: 'Likes' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(false);

    try {
      const metricData = {
        deal_id: dealId,
        metric_type: formData.metric_type,
        metric_value: parseFloat(formData.metric_value),
        platform: formData.platform || null,
        source: formData.source,
        measurement_date: new Date().toISOString().split('T')[0]
      };

      await axios.post(`${API}/sponsorship/metrics`, metricData);
      
      setSuccess(true);
      setFormData({
        metric_type: 'views',
        metric_value: '',
        platform: '',
        source: 'organic'
      });
      
      if (onMetricRecorded) {
        onMetricRecorded();
      }

      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      console.error('Error recording metric:', error);
      alert('Failed to record metric. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Record Performance Metric</h3>
      
      {success && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          ✅ Performance metric recorded successfully!
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Metric Type *
            </label>
            <select
              value={formData.metric_type}
              onChange={(e) => setFormData({ ...formData, metric_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            >
              {metricTypes.map((type) => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Metric Value *
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.metric_value}
              onChange={(e) => setFormData({ ...formData, metric_value: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter numeric value"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Platform
            </label>
            <input
              type="text"
              value={formData.platform}
              onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="e.g., Instagram, YouTube, Spotify"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source
            </label>
            <select
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="organic">Organic</option>
              <option value="sponsored">Sponsored</option>
              <option value="viral">Viral</option>
              <option value="paid">Paid</option>
              <option value="referral">Referral</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Recording...' : 'Record Metric'}
        </button>
      </form>
    </div>
  );
};

// Admin Sponsorship Overview
export const AdminSponsorshipOverview = () => {
  const [overview, setOverview] = useState({});
  const [sponsors, setSponsors] = useState([]);
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
    fetchSponsors();
    fetchRecentDeals();
  }, []);

  const fetchOverview = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/admin/overview`);
      setOverview(response.data);
    } catch (error) {
      console.error('Error fetching overview:', error);
    }
  };

  const fetchSponsors = async () => {
    try {
      const response = await axios.get(`${API}/sponsorship/sponsors?limit=10`);
      setSponsors(response.data.sponsors);
    } catch (error) {
      console.error('Error fetching sponsors:', error);
    }
  };

  const fetchRecentDeals = async () => {
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
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading sponsorship overview...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Sponsorship Management</h1>
          <p className="text-gray-600">Overview of all sponsorship activities and performance</p>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Sponsors</p>
                <p className="text-2xl font-bold text-gray-900">{overview.overview?.total_sponsors || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Deals</p>
                <p className="text-2xl font-bold text-gray-900">{overview.overview?.active_deals || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Payouts</p>
                <p className="text-2xl font-bold text-gray-900">${(overview.overview?.total_payouts || 0).toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg Deal Value</p>
                <p className="text-2xl font-bold text-gray-900">${(overview.overview?.average_deal_value || 0).toFixed(2)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Sponsors */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Top Sponsors</h2>
            </div>
            <div className="p-6">
              {sponsors.length === 0 ? (
                <p className="text-gray-500">No sponsors found.</p>
              ) : (
                <div className="space-y-4">
                  {sponsors.slice(0, 5).map((sponsor) => (
                    <div key={sponsor.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{sponsor.company_name}</p>
                        <p className="text-sm text-gray-500">{sponsor.industry}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">{sponsor.tier}</p>
                        <p className="text-sm text-gray-500">${(sponsor.total_spent || 0).toFixed(2)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Deals */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Recent Deals</h2>
            </div>
            <div className="p-6">
              {deals.length === 0 ? (
                <p className="text-gray-500">No recent deals found.</p>
              ) : (
                <div className="space-y-4">
                  {deals.slice(0, 5).map((deal) => (
                    <div key={deal.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{deal.deal_name}</p>
                        <p className="text-sm text-gray-500">{deal.creator?.full_name}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">${(deal.base_fee || 0).toFixed(2)}</p>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          deal.status === 'active' ? 'bg-green-100 text-green-800' : 
                          deal.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {deal.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};