import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://creative-ledger.preview.emergentagent.com';

// Global error handler utility
const handleApiError = (error, context) => {
  console.error(`Error in ${context}:`, error);
  
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    return;
  }
  
  if (error.response?.status === 403) {
    console.error('Access forbidden - insufficient permissions');
    return;
  }
  
  if (error.response?.status >= 500) {
    console.error('Server error - please try again later');
    return;
  }
  
  console.error('API Error:', error.response?.data?.message || error.message || 'Unknown error');
};

// Safe API response handler
const handleApiResponse = (response, successCallback, errorMessage = 'API call failed') => {
  if (response?.data?.success) {
    if (successCallback) successCallback(response.data);
    return true;
  } else {
    console.error(errorMessage, response?.data?.message || 'Unknown error');
    return false;
  }
};

// PHASE 5: Advanced Content Scheduling & Publishing Automation
const AdvancedSchedulingTab = () => {
  const [schedulingRules, setSchedulingRules] = useState([]);
  const [contentQueues, setContentQueues] = useState([]);
  const [newRule, setNewRule] = useState({
    name: '',
    platforms: [],
    content_types: [],
    optimal_times: {},
    frequency: 'daily',
    auto_optimize: true
  });
  const [loading, setLoading] = useState(false);

  const platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'tiktok', 'youtube'];
  const contentTypes = ['image', 'video', 'text', 'carousel', 'story'];
  const daysOfWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  const createSchedulingRule = async () => {
    if (!newRule.name.trim()) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No authentication token found');
        return;
      }
      
      const response = await axios.post(
        `${API}/api/social-media-advanced/scheduling/rules`,
        newRule,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response?.data?.success) {
        setSchedulingRules([...schedulingRules, { ...newRule, id: response.data.rule_id }]);
        setNewRule({
          name: '',
          platforms: [],
          content_types: [],
          optimal_times: {},
          frequency: 'daily',
          auto_optimize: true
        });
      } else {
        console.error('Failed to create scheduling rule:', response?.data?.message || 'Unknown error');
      }
    } catch (error) {
      console.error('Failed to create scheduling rule:', error);
      if (error.response?.status === 401) {
        // Handle authentication error
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  const optimizePostingTimes = async (platform) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No authentication token found');
        return;
      }
      
      const response = await axios.get(
        `${API}/api/social-media-advanced/scheduling/optimize-times/${platform}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response?.data?.success) {
        alert(`Optimal times for ${platform}: ${JSON.stringify(response.data.optimal_times, null, 2)}`);
      } else {
        console.error('Failed to optimize posting times:', response?.data?.message || 'Unknown error');
      }
    } catch (error) {
      console.error('Failed to optimize posting times:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">🤖 Advanced Content Scheduling</h3>
        
        {/* Create New Scheduling Rule */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Create Scheduling Rule</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Rule Name"
              value={newRule.name}
              onChange={(e) => setNewRule({...newRule, name: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <select
              value={newRule.frequency}
              onChange={(e) => setNewRule({...newRule, frequency: e.target.value})}
              className="border rounded-lg px-3 py-2"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          
          {/* Platform Selection */}
          <div className="mt-4">
            <label className="block text-sm font-medium mb-2">Platforms</label>
            <div className="flex flex-wrap gap-2">
              {platforms.map(platform => (
                <label key={platform} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newRule.platforms.includes(platform)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setNewRule({...newRule, platforms: [...newRule.platforms, platform]});
                      } else {
                        setNewRule({...newRule, platforms: newRule.platforms.filter(p => p !== platform)});
                      }
                    }}
                  />
                  <span className="text-sm capitalize">{platform}</span>
                </label>
              ))}
            </div>
          </div>
          
          {/* Content Types */}
          <div className="mt-4">
            <label className="block text-sm font-medium mb-2">Content Types</label>
            <div className="flex flex-wrap gap-2">
              {contentTypes.map(type => (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newRule.content_types.includes(type)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setNewRule({...newRule, content_types: [...newRule.content_types, type]});
                      } else {
                        setNewRule({...newRule, content_types: newRule.content_types.filter(t => t !== type)});
                      }
                    }}
                  />
                  <span className="text-sm capitalize">{type}</span>
                </label>
              ))}
            </div>
          </div>
          
          <button
            onClick={createSchedulingRule}
            disabled={loading || !newRule.name.trim()}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Rule'}
          </button>
        </div>

        {/* AI Optimization Tools */}
        <div className="border-t pt-6">
          <h4 className="font-medium mb-3">AI Posting Time Optimization</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {platforms.map(platform => (
              <button
                key={platform}
                onClick={() => optimizePostingTimes(platform)}
                className="bg-green-100 text-green-800 px-3 py-2 rounded-lg hover:bg-green-200 text-sm"
              >
                Optimize {platform}
              </button>
            ))}
          </div>
        </div>

        {/* Existing Rules */}
        <div className="mt-6">
          <h4 className="font-medium mb-3">Active Scheduling Rules ({schedulingRules.length})</h4>
          <div className="space-y-2">
            {schedulingRules.map((rule, index) => (
              <div key={index} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex justify-between items-start">
                  <div>
                    <h5 className="font-medium">{rule.name}</h5>
                    <p className="text-sm text-gray-600">
                      Platforms: {rule.platforms.join(', ')} | Frequency: {rule.frequency}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${rule.auto_optimize ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {rule.auto_optimize ? 'Auto-Optimized' : 'Manual'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// PHASE 6: Real-time Analytics & Performance Optimization
const RealTimeAnalyticsTab = () => {
  const [realTimeMetrics, setRealTimeMetrics] = useState({});
  const [performanceReports, setPerformanceReports] = useState([]);
  const [abTests, setAbTests] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [timeWindow, setTimeWindow] = useState(3600);

  const platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'tiktok', 'youtube'];

  const fetchRealTimeMetrics = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        handleApiError({ response: { status: 401 } }, 'fetchRealTimeMetrics');
        return;
      }
      
      const platformParam = selectedPlatform !== 'all' ? `platform=${selectedPlatform}&` : '';
      const response = await axios.get(
        `${API}/api/social-media-advanced/analytics/real-time?${platformParam}time_window=${timeWindow}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      handleApiResponse(response, (data) => {
        setRealTimeMetrics(data);
      }, 'Failed to fetch real-time metrics');
    } catch (error) {
      handleApiError(error, 'fetchRealTimeMetrics');
    }
  };

  const generateReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const endDate = new Date();
      const startDate = new Date(endDate.getTime() - (30 * 24 * 60 * 60 * 1000)); // 30 days ago
      
      const response = await axios.post(
        `${API}/api/social-media-advanced/analytics/generate-report`,
        {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString(),
          platforms: platforms
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setPerformanceReports([response.data.report, ...performanceReports]);
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
    }
  };

  const createABTest = async (contentVariants) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/analytics/ab-test`,
        {
          content_variants: contentVariants,
          platforms: platforms.slice(0, 3), // Test on first 3 platforms
          duration_hours: 24
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setAbTests([...abTests, {
          id: response.data.test_id,
          variants: contentVariants,
          status: 'active',
          created_at: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Failed to create A/B test:', error);
    }
  };

  useEffect(() => {
    fetchRealTimeMetrics();
    const interval = setInterval(fetchRealTimeMetrics, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [selectedPlatform, timeWindow]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">📊 Real-time Analytics & Performance</h3>
        
        {/* Controls */}
        <div className="flex space-x-4 mb-6">
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="border rounded-lg px-3 py-2"
          >
            <option value="all">All Platforms</option>
            {platforms.map(platform => (
              <option key={platform} value={platform}>{platform}</option>
            ))}
          </select>
          
          <select
            value={timeWindow}
            onChange={(e) => setTimeWindow(parseInt(e.target.value))}
            className="border rounded-lg px-3 py-2"
          >
            <option value={3600}>Last Hour</option>
            <option value={21600}>Last 6 Hours</option>
            <option value={86400}>Last 24 Hours</option>
          </select>
          
          <button
            onClick={generateReport}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Generate Report
          </button>
        </div>

        {/* Real-time Metrics Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-800">Total Engagement</h4>
            <p className="text-2xl font-bold text-blue-900">
              {realTimeMetrics.summary?.total_engagement?.toLocaleString() || '0'}
            </p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-medium text-green-800">Total Reach</h4>
            <p className="text-2xl font-bold text-green-900">
              {realTimeMetrics.summary?.total_reach?.toLocaleString() || '0'}
            </p>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-medium text-purple-800">Impressions</h4>
            <p className="text-2xl font-bold text-purple-900">
              {realTimeMetrics.summary?.total_impressions?.toLocaleString() || '0'}
            </p>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg">
            <h4 className="font-medium text-orange-800">Metrics Tracked</h4>
            <p className="text-2xl font-bold text-orange-900">
              {realTimeMetrics.summary?.total_metrics || '0'}
            </p>
          </div>
        </div>

        {/* A/B Testing Section */}
        <div className="border-t pt-6">
          <h4 className="font-medium mb-3">A/B Testing</h4>
          <div className="mb-4">
            <button
              onClick={() => createABTest(['Content Variant A', 'Content Variant B'])}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Create A/B Test
            </button>
          </div>
          
          <div className="space-y-2">
            {abTests.map(test => (
              <div key={test.id} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex justify-between items-center">
                  <div>
                    <h5 className="font-medium">A/B Test: {test.variants.join(' vs ')}</h5>
                    <p className="text-sm text-gray-600">Created: {new Date(test.created_at).toLocaleString()}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${test.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {test.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// PHASE 7: Audience Engagement & Community Management
const CommunityManagementTab = () => {
  const [unifiedInbox, setUnifiedInbox] = useState([]);
  const [autoResponseRules, setAutoResponseRules] = useState([]);
  const [newRule, setNewRule] = useState({
    name: '',
    triggers: [],
    response_template: '',
    platforms: [],
    is_active: true
  });
  const [inboxFilter, setInboxFilter] = useState('all');

  const platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'tiktok', 'youtube'];
  const engagementTypes = ['comment', 'mention', 'direct_message', 'reply', 'review'];

  const fetchUnifiedInbox = async () => {
    try {
      const token = localStorage.getItem('token');
      const statusParam = inboxFilter !== 'all' ? `status=${inboxFilter}` : '';
      const response = await axios.get(
        `${API}/api/social-media-advanced/engagement/unified-inbox?${statusParam}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setUnifiedInbox(response.data.engagements || []);
      }
    } catch (error) {
      console.error('Failed to fetch unified inbox:', error);
    }
  };

  const createAutoResponseRule = async () => {
    if (!newRule.name.trim() || !newRule.response_template.trim()) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/engagement/auto-response-rule`,
        newRule,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setAutoResponseRules([...autoResponseRules, { ...newRule, id: response.data.rule_id }]);
        setNewRule({
          name: '',
          triggers: [],
          response_template: '',
          platforms: [],
          is_active: true
        });
      }
    } catch (error) {
      console.error('Failed to create auto-response rule:', error);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-green-600 bg-green-50';
    }
  };

  useEffect(() => {
    fetchUnifiedInbox();
  }, [inboxFilter]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">💬 Community Management & Engagement</h3>
        
        {/* Unified Inbox */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-medium">Unified Inbox</h4>
            <select
              value={inboxFilter}
              onChange={(e) => setInboxFilter(e.target.value)}
              className="border rounded-lg px-3 py-2"
            >
              <option value="all">All Engagements</option>
              <option value="unread">Unread</option>
              <option value="high">High Priority</option>
              <option value="responded">Responded</option>
            </select>
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {unifiedInbox.length > 0 ? unifiedInbox.map((engagement, index) => (
              <div key={index} className="border rounded-lg p-3 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium capitalize">{engagement.platform}</span>
                    <span className="text-sm text-gray-500">•</span>
                    <span className="text-sm capitalize">{engagement.engagement_type}</span>
                  </div>
                  <div className="flex space-x-2">
                    <span className={`px-2 py-1 rounded text-xs ${getSentimentColor(engagement.sentiment)}`}>
                      {engagement.sentiment}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(engagement.priority)}`}>
                      {engagement.priority}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-700 mb-2">{engagement.content}</p>
                <div className="flex justify-between items-center text-xs text-gray-500">
                  <span>From: {engagement.from_user}</span>
                  <span>{new Date(engagement.timestamp).toLocaleString()}</span>
                </div>
              </div>
            )) : (
              <div className="text-center py-8 text-gray-500">
                <p>No engagements found</p>
              </div>
            )}
          </div>
        </div>

        {/* Auto-Response Rules */}
        <div className="border-t pt-6">
          <h4 className="font-medium mb-4">Auto-Response Rules</h4>
          
          <div className="mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Rule Name"
                value={newRule.name}
                onChange={(e) => setNewRule({...newRule, name: e.target.value})}
                className="border rounded-lg px-3 py-2"
              />
              
              <input
                type="text"
                placeholder="Trigger Keywords (comma-separated)"
                onChange={(e) => setNewRule({...newRule, triggers: e.target.value.split(',').map(t => t.trim())})}
                className="border rounded-lg px-3 py-2"
              />
            </div>
            
            <textarea
              placeholder="Response Template (use {user} for username, {platform} for platform)"
              value={newRule.response_template}
              onChange={(e) => setNewRule({...newRule, response_template: e.target.value})}
              className="w-full border rounded-lg px-3 py-2 mt-2"
              rows="3"
            />
            
            <div className="mt-2">
              <label className="block text-sm font-medium mb-2">Platforms</label>
              <div className="flex flex-wrap gap-2">
                {platforms.map(platform => (
                  <label key={platform} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={newRule.platforms.includes(platform)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setNewRule({...newRule, platforms: [...newRule.platforms, platform]});
                        } else {
                          setNewRule({...newRule, platforms: newRule.platforms.filter(p => p !== platform)});
                        }
                      }}
                    />
                    <span className="text-sm capitalize">{platform}</span>
                  </label>
                ))}
              </div>
            </div>
            
            <button
              onClick={createAutoResponseRule}
              disabled={!newRule.name.trim() || !newRule.response_template.trim()}
              className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Create Rule
            </button>
          </div>

          <div className="space-y-2">
            {autoResponseRules.map((rule, index) => (
              <div key={index} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex justify-between items-start">
                  <div>
                    <h5 className="font-medium">{rule.name}</h5>
                    <p className="text-sm text-gray-600">Triggers: {rule.triggers.join(', ')}</p>
                    <p className="text-sm text-gray-700 mt-1">{rule.response_template}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${rule.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {rule.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// PHASE 8: Cross-platform Campaign Orchestration
const CampaignOrchestrationTab = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [newCampaign, setNewCampaign] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    platforms: [],
    budget_total: 0,
    goals: {},
    status: 'draft'
  });
  const [contentAdaptations, setContentAdaptations] = useState({});

  const platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'tiktok', 'youtube'];
  const goalTypes = ['reach', 'engagement', 'conversions', 'brand_awareness'];

  const createCampaign = async () => {
    if (!newCampaign.name.trim() || newCampaign.platforms.length === 0) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/campaigns/create`,
        newCampaign,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setCampaigns([...campaigns, { ...newCampaign, id: response.data.campaign_id }]);
        setNewCampaign({
          name: '',
          description: '',
          start_date: '',
          end_date: '',
          platforms: [],
          budget_total: 0,
          goals: {},
          status: 'draft'
        });
      }
    } catch (error) {
      console.error('Failed to create campaign:', error);
    }
  };

  const adaptContent = async (campaignId, contentId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/campaigns/${campaignId}/adapt-content`,
        {
          content_id: contentId,
          platforms: platforms
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setContentAdaptations({
          ...contentAdaptations,
          [campaignId]: response.data.adaptations
        });
      }
    } catch (error) {
      console.error('Failed to adapt content:', error);
    }
  };

  const optimizeBudget = async (campaignId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/campaigns/${campaignId}/optimize-budget`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        alert(`Budget optimized for campaign ${campaignId}: ${JSON.stringify(response.data.optimized_allocation, null, 2)}`);
      }
    } catch (error) {
      console.error('Failed to optimize budget:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">🎯 Cross-platform Campaign Orchestration</h3>
        
        {/* Create New Campaign */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Create New Campaign</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Campaign Name"
              value={newCampaign.name}
              onChange={(e) => setNewCampaign({...newCampaign, name: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="number"
              placeholder="Total Budget ($)"
              value={newCampaign.budget_total}
              onChange={(e) => setNewCampaign({...newCampaign, budget_total: parseFloat(e.target.value) || 0})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="date"
              placeholder="Start Date"
              value={newCampaign.start_date}
              onChange={(e) => setNewCampaign({...newCampaign, start_date: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="date"
              placeholder="End Date"
              value={newCampaign.end_date}
              onChange={(e) => setNewCampaign({...newCampaign, end_date: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
          </div>
          
          <textarea
            placeholder="Campaign Description"
            value={newCampaign.description}
            onChange={(e) => setNewCampaign({...newCampaign, description: e.target.value})}
            className="w-full border rounded-lg px-3 py-2 mt-2"
            rows="3"
          />
          
          {/* Platform Selection */}
          <div className="mt-4">
            <label className="block text-sm font-medium mb-2">Target Platforms</label>
            <div className="flex flex-wrap gap-2">
              {platforms.map(platform => (
                <label key={platform} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={newCampaign.platforms.includes(platform)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setNewCampaign({...newCampaign, platforms: [...newCampaign.platforms, platform]});
                      } else {
                        setNewCampaign({...newCampaign, platforms: newCampaign.platforms.filter(p => p !== platform)});
                      }
                    }}
                  />
                  <span className="text-sm capitalize">{platform}</span>
                </label>
              ))}
            </div>
          </div>
          
          <button
            onClick={createCampaign}
            disabled={!newCampaign.name.trim() || newCampaign.platforms.length === 0}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Create Campaign
          </button>
        </div>

        {/* Campaign Management */}
        <div className="border-t pt-6">
          <h4 className="font-medium mb-4">Active Campaigns ({campaigns.length})</h4>
          <div className="space-y-4">
            {campaigns.map((campaign, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h5 className="font-medium text-lg">{campaign.name}</h5>
                    <p className="text-sm text-gray-600">{campaign.description}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Budget: ${campaign.budget_total.toLocaleString()} | 
                      Platforms: {campaign.platforms.join(', ')}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${campaign.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {campaign.status}
                  </span>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => adaptContent(campaign.id, `content_${index}`)}
                    className="bg-purple-100 text-purple-800 px-3 py-1 rounded text-sm hover:bg-purple-200"
                  >
                    Adapt Content
                  </button>
                  
                  <button
                    onClick={() => optimizeBudget(campaign.id)}
                    className="bg-orange-100 text-orange-800 px-3 py-1 rounded text-sm hover:bg-orange-200"
                  >
                    Optimize Budget
                  </button>
                </div>
                
                {/* Show Content Adaptations */}
                {contentAdaptations[campaign.id] && (
                  <div className="mt-3 pt-3 border-t">
                    <h6 className="text-sm font-medium mb-2">Content Adaptations:</h6>
                    <div className="space-y-1">
                      {Object.entries(contentAdaptations[campaign.id]).map(([platform, content]) => (
                        <div key={platform} className="text-xs bg-gray-50 p-2 rounded">
                          <strong className="capitalize">{platform}:</strong> {content}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// PHASE 9: Influencer & Partnership Management
const InfluencerManagementTab = () => {
  const [influencers, setInfluencers] = useState([]);
  const [partnerships, setPartnerships] = useState([]);
  const [searchCriteria, setSearchCriteria] = useState({
    categories: [],
    min_followers: '',
    min_engagement_rate: ''
  });

  const categories = ['fitness', 'lifestyle', 'tech', 'fashion', 'food', 'travel', 'beauty', 'business'];
  const partnershipTypes = ['sponsored_post', 'collaboration', 'brand_ambassador'];

  const discoverInfluencers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/influencers/discover`,
        searchCriteria,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setInfluencers(response.data.influencers || []);
      }
    } catch (error) {
      console.error('Failed to discover influencers:', error);
    }
  };

  const createPartnership = async (influencerId, type) => {
    try {
      const token = localStorage.getItem('token');
      const partnership = {
        influencer_id: influencerId,
        campaign_id: 'campaign_001',
        partnership_type: type,
        deliverables: ['1 Instagram post', '3 stories'],
        compensation: { amount: 1000, currency: 'USD' },
        contract_terms: {},
        start_date: new Date().toISOString(),
        end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
      };
      
      const response = await axios.post(
        `${API}/api/social-media-advanced/partnerships/create`,
        partnership,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setPartnerships([...partnerships, { ...partnership, id: response.data.partnership_id }]);
      }
    } catch (error) {
      console.error('Failed to create partnership:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">🤝 Influencer & Partnership Management</h3>
        
        {/* Influencer Discovery */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Discover Influencers</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <input
              type="number"
              placeholder="Min Followers"
              value={searchCriteria.min_followers}
              onChange={(e) => setSearchCriteria({...searchCriteria, min_followers: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <input
              type="number"
              placeholder="Min Engagement Rate (%)"
              value={searchCriteria.min_engagement_rate}
              onChange={(e) => setSearchCriteria({...searchCriteria, min_engagement_rate: e.target.value})}
              className="border rounded-lg px-3 py-2"
            />
            
            <button
              onClick={discoverInfluencers}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Search Influencers
            </button>
          </div>
          
          {/* Categories */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Categories</label>
            <div className="flex flex-wrap gap-2">
              {categories.map(category => (
                <label key={category} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={searchCriteria.categories.includes(category)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSearchCriteria({...searchCriteria, categories: [...searchCriteria.categories, category]});
                      } else {
                        setSearchCriteria({...searchCriteria, categories: searchCriteria.categories.filter(c => c !== category)});
                      }
                    }}
                  />
                  <span className="text-sm capitalize">{category}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Discovered Influencers */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Discovered Influencers ({influencers.length})</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {influencers.map((influencer, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h5 className="font-medium">{influencer.name}</h5>
                  <div className="flex space-x-1">
                    {partnershipTypes.map(type => (
                      <button
                        key={type}
                        onClick={() => createPartnership(influencer.id, type)}
                        className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs hover:bg-green-200"
                      >
                        {type.replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="text-sm text-gray-600 space-y-1">
                  <p>Categories: {influencer.categories?.join(', ') || 'N/A'}</p>
                  <p>Followers: {Object.values(influencer.follower_counts || {}).reduce((a, b) => a + b, 0).toLocaleString()}</p>
                  <p>Avg Engagement: {Object.values(influencer.engagement_rates || {}).reduce((a, b) => a + b, 0).toFixed(1)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Partnerships */}
        <div className="border-t pt-6">
          <h4 className="font-medium mb-4">Active Partnerships ({partnerships.length})</h4>
          <div className="space-y-3">
            {partnerships.map((partnership, index) => (
              <div key={index} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex justify-between items-start">
                  <div>
                    <h5 className="font-medium">Partnership #{partnership.id}</h5>
                    <p className="text-sm text-gray-600">
                      Type: {partnership.partnership_type.replace('_', ' ')} | 
                      Compensation: ${partnership.compensation.amount}
                    </p>
                    <p className="text-sm text-gray-500">
                      Deliverables: {partnership.deliverables.join(', ')}
                    </p>
                  </div>
                  <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">
                    {partnership.status || 'pending'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// PHASE 10: AI-Powered Content Optimization & Predictive Analytics
const AIOptimizationTab = () => {
  const [contentRecommendations, setContentRecommendations] = useState([]);
  const [trendPredictions, setTrendPredictions] = useState([]);
  const [executiveDashboard, setExecutiveDashboard] = useState({});
  const [contentToOptimize, setContentToOptimize] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('twitter');
  const [optimizedContent, setOptimizedContent] = useState({});

  const platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'tiktok', 'youtube'];
  const trendCategories = ['technology', 'entertainment', 'business', 'lifestyle', 'sports'];

  const generateRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/ai/content-recommendations`,
        { platforms: platforms },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setContentRecommendations(response.data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to generate recommendations:', error);
    }
  };

  const predictTrends = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/ai/predict-trends`,
        { categories: trendCategories },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setTrendPredictions(response.data.predictions || []);
      }
    } catch (error) {
      console.error('Failed to predict trends:', error);
    }
  };

  const optimizeContent = async () => {
    if (!contentToOptimize.trim()) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-media-advanced/ai/optimize-content`,
        {
          content: contentToOptimize,
          target_platform: selectedPlatform
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setOptimizedContent(response.data.optimizations);
      }
    } catch (error) {
      console.error('Failed to optimize content:', error);
    }
  };

  const fetchExecutiveDashboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/social-media-advanced/ai/executive-dashboard`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setExecutiveDashboard(response.data.dashboard);
      }
    } catch (error) {
      console.error('Failed to fetch executive dashboard:', error);
    }
  };

  useEffect(() => {
    fetchExecutiveDashboard();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">🤖 AI-Powered Optimization & Analytics</h3>
        
        {/* Executive Dashboard Summary */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Executive Dashboard</h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h5 className="font-medium text-blue-800">Active Campaigns</h5>
              <p className="text-2xl font-bold text-blue-900">
                {executiveDashboard?.summary?.active_campaigns || 0}
              </p>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h5 className="font-medium text-green-800">Monthly Engagement</h5>
              <p className="text-2xl font-bold text-green-900">
                {executiveDashboard?.summary?.total_monthly_engagement?.toLocaleString() || '0'}
              </p>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <h5 className="font-medium text-purple-800">Growth Rate</h5>
              <p className="text-2xl font-bold text-purple-900">
                {(executiveDashboard?.summary?.predicted_growth_rate * 100)?.toFixed(1) || 0}%
              </p>
            </div>
            
            <div className="bg-orange-50 p-4 rounded-lg">
              <h5 className="font-medium text-orange-800">ROI Trend</h5>
              <p className="text-2xl font-bold text-orange-900">
                {executiveDashboard?.summary?.roi_trend || 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* AI Tools */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Content Recommendations */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-medium">Content Recommendations</h4>
              <button
                onClick={generateRecommendations}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
              >
                Generate
              </button>
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {contentRecommendations.map((rec, index) => (
                <div key={index} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-sm font-medium capitalize">{rec.platform}</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {(rec.confidence_score * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{rec.recommendation_text}</p>
                  <div className="text-xs text-gray-500">
                    Predicted: {rec.predicted_performance?.engagement_rate}% engagement
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Trend Predictions */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-medium">Trend Predictions</h4>
              <button
                onClick={predictTrends}
                className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700"
              >
                Predict
              </button>
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {trendPredictions.map((trend, index) => (
                <div key={index} className="border rounded-lg p-3 bg-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="text-sm font-medium">{trend.trend_topic}</h5>
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      {(trend.opportunity_score * 100).toFixed(0)}% opportunity
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mb-1">
                    Peak: {new Date(trend.predicted_peak).toLocaleDateString()}
                  </p>
                  <p className="text-xs text-gray-500">
                    Actions: {trend.recommended_actions?.join(', ')}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Content Optimization Tool */}
        <div className="border-t pt-6 mt-6">
          <h4 className="font-medium mb-3">Content Optimization</h4>
          <div className="space-y-4">
            <div className="flex space-x-4">
              <textarea
                placeholder="Enter content to optimize..."
                value={contentToOptimize}
                onChange={(e) => setContentToOptimize(e.target.value)}
                className="flex-1 border rounded-lg px-3 py-2"
                rows="3"
              />
              
              <div className="space-y-2">
                <select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                  className="border rounded-lg px-3 py-2 w-full"
                >
                  {platforms.map(platform => (
                    <option key={platform} value={platform}>{platform}</option>
                  ))}
                </select>
                
                <button
                  onClick={optimizeContent}
                  disabled={!contentToOptimize.trim()}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  Optimize
                </button>
              </div>
            </div>
            
            {/* Optimized Content Results */}
            {Object.keys(optimizedContent).length > 0 && (
              <div className="border rounded-lg p-4 bg-green-50">
                <h5 className="font-medium mb-2">Optimization Results for {selectedPlatform}:</h5>
                <div className="space-y-2 text-sm">
                  {Object.entries(optimizedContent).map(([key, value]) => (
                    <div key={key}>
                      <strong className="text-green-800 capitalize">{key.replace('_', ' ')}:</strong>
                      <span className="ml-2 text-gray-700">
                        {Array.isArray(value) ? value.join(', ') : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Key Insights */}
        {executiveDashboard?.key_insights && (
          <div className="border-t pt-6 mt-6">
            <h4 className="font-medium mb-3">Key Insights</h4>
            <div className="space-y-2">
              {executiveDashboard.key_insights.map((insight, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <span className="text-blue-600">💡</span>
                  <p className="text-sm text-gray-700">{insight}</p>
                </div>
              ))}
            </div>
            
            <h4 className="font-medium mb-3 mt-4">Action Items</h4>
            <div className="space-y-2">
              {executiveDashboard.action_items?.map((action, index) => (
                <div key={index} className="flex items-start space-x-2">
                  <span className="text-green-600">✅</span>
                  <p className="text-sm text-gray-700">{action}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Main Component for Phases 5-10
export const SocialMediaPhases5To10Dashboard = () => {
  const [activeTab, setActiveTab] = useState('scheduling');
  const [systemStatus, setSystemStatus] = useState({});

  const tabs = [
    { id: 'scheduling', name: 'Advanced Scheduling', icon: '🤖', component: AdvancedSchedulingTab },
    { id: 'analytics', name: 'Real-time Analytics', icon: '📊', component: RealTimeAnalyticsTab },
    { id: 'community', name: 'Community Management', icon: '💬', component: CommunityManagementTab },
    { id: 'campaigns', name: 'Campaign Orchestration', icon: '🎯', component: CampaignOrchestrationTab },
    { id: 'influencers', name: 'Influencer Management', icon: '🤝', component: InfluencerManagementTab },
    { id: 'ai', name: 'AI Optimization', icon: '🤖', component: AIOptimizationTab }
  ];

  const fetchSystemStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/social-media-advanced/status/comprehensive`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setSystemStatus(response.data.status);
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || AdvancedSchedulingTab;

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Social Media Strategy: Phases 5-10</h1>
        <p className="text-gray-600">Advanced automation, analytics, and AI-powered optimization</p>
      </div>

      {/* System Status Overview */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">System Status Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
          {Object.entries(systemStatus).map(([phase, data]) => (
            <div key={phase} className="text-center">
              <div className="font-medium capitalize">{phase.replace('phase_', 'Phase ').replace('_', ' ')}</div>
              <div className="text-xs text-gray-500 mt-1">
                {typeof data === 'object' ? Object.values(data).reduce((a, b) => a + b, 0) : 0} items
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Active Tab Content */}
      <ActiveComponent />
    </div>
  );
};

export default SocialMediaPhases5To10Dashboard;