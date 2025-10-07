import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://uln-label-editor.preview.emergentagent.com';

// Main Social Media Strategy Dashboard
export const SocialMediaStrategyDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRealTimeData();
    const interval = setInterval(fetchRealTimeData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRealTimeData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/social-strategy/monitoring/real-time`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRealTimeData(response.data.monitoring);
    } catch (error) {
      console.error('Error fetching real-time data:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'intelligence', name: 'Platform Intelligence', icon: '🧠' },
    { id: 'campaigns', name: 'Campaigns', icon: '🚀' },
    { id: 'workflow', name: 'Workflow', icon: '⚡' },
    { id: 'analytics', name: 'Analytics', icon: '📈' }
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Social Media Strategy Center</h1>
        <p className="text-gray-600">Comprehensive social media management and optimization platform</p>
      </div>

      {/* Real-time Alert Bar */}
      {realTimeData?.alerts && realTimeData.alerts.length > 0 && (
        <div className="mb-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-xl mr-2">🚨</span>
              <span className="font-semibold">Active Alerts: {realTimeData.alerts.length}</span>
            </div>
            <div className="text-sm">
              Latest: {realTimeData.alerts[0]?.message}
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && <OverviewTab realTimeData={realTimeData} />}
        {activeTab === 'intelligence' && <PlatformIntelligenceTab />}
        {activeTab === 'campaigns' && <CrossPromotionTab />}
        {activeTab === 'workflow' && <WorkflowManagementTab />}
        {activeTab === 'analytics' && <AnalyticsTab />}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ realTimeData }) => {
  const [comprehensiveReport, setComprehensiveReport] = useState(null);
  const [aiRecommendations, setAiRecommendations] = useState(null);

  useEffect(() => {
    fetchComprehensiveReport();
    fetchAiRecommendations();
  }, []);

  const fetchComprehensiveReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/social-strategy/strategy/comprehensive-report`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setComprehensiveReport(response.data.report);
    } catch (error) {
      console.error('Error fetching comprehensive report:', error);
    }
  };

  const fetchAiRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/social-strategy/strategy/ai-recommendations`, {
        user_goals: { primary_objective: 'growth', target_audience: 'young_adults' },
        current_performance: { engagement_rate: 3.2, reach: 50000 }
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAiRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching AI recommendations:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Real-time Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="text-green-600 text-2xl mr-3">📈</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Active Campaigns</p>
              <p className="text-2xl font-semibold text-gray-900">{realTimeData?.current_campaigns || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
          <div className="flex items-center">
            <div className="text-blue-600 text-2xl mr-3">💬</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Real-time Engagement</p>
              <p className="text-2xl font-semibold text-gray-900">
                {realTimeData?.real_time_engagement?.likes_per_minute || 0}/min
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-purple-500">
          <div className="flex items-center">
            <div className="text-purple-600 text-2xl mr-3">🎯</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Active Posts</p>
              <p className="text-2xl font-semibold text-gray-900">{realTimeData?.active_posts || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-orange-500">
          <div className="flex items-center">
            <div className="text-orange-600 text-2xl mr-3">🔥</div>
            <div>
              <p className="text-sm font-medium text-gray-600">Trending Content</p>
              <p className="text-2xl font-semibold text-gray-900">
                {realTimeData?.trending_content?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Overview */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Performance Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {comprehensiveReport.executive_summary.total_reach.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Total Reach</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {comprehensiveReport.executive_summary.average_engagement_rate}%
              </div>
              <div className="text-sm text-gray-600">Avg Engagement Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {comprehensiveReport.executive_summary.roi}%
              </div>
              <div className="text-sm text-gray-600">ROI</div>
            </div>
          </div>
        </div>
      )}

      {/* AI Recommendations */}
      {aiRecommendations && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI-Powered Recommendations</h3>
          <div className="space-y-4">
            {aiRecommendations.priority_actions?.slice(0, 3).map((action, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-semibold text-gray-900">{action.action}</h4>
                <p className="text-gray-600 text-sm">{action.reason}</p>
                <div className="flex items-center mt-2 space-x-4">
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                    {action.expected_impact}
                  </span>
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {action.timeline}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Platform Status */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔧 Platform Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {realTimeData?.platform_status && Object.entries(realTimeData.platform_status).map(([platform, status]) => (
            <div key={platform} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium capitalize">{platform}</span>
                <span className={`w-3 h-3 rounded-full ${
                  status.status === 'optimal' ? 'bg-green-500' : 
                  status.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`}></span>
              </div>
              <div className="text-sm text-gray-600">
                <div>API: {status.api_health}</div>
                <div>Posting: {status.posting_enabled ? '✅' : '❌'}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Platform Intelligence Tab Component
const PlatformIntelligenceTab = () => {
  const [platforms, setPlatforms] = useState({});
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [contentRecommendations, setContentRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlatformIntelligence();
  }, []);

  const fetchPlatformIntelligence = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/social-strategy/platform-intelligence`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPlatforms(response.data.platforms);
    } catch (error) {
      console.error('Error fetching platform intelligence:', error);
    } finally {
      setLoading(false);
    }
  };

  const getContentRecommendations = async (contentType) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/social-strategy/content-recommendations`, {
        content_type: contentType,
        monetization_priority: false
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setContentRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching content recommendations:', error);
    }
  };

  if (loading) {
    return <div className="text-center">Loading platform intelligence...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Content Type Analyzer */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Content Recommendations</h3>
        <div className="flex flex-wrap gap-2 mb-4">
          {['audio', 'video', 'image', 'short_form', 'music'].map((type) => (
            <button
              key={type}
              onClick={() => getContentRecommendations(type)}
              className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors capitalize"
            >
              {type.replace('_', ' ')}
            </button>
          ))}
        </div>

        {contentRecommendations && (
          <div className="border-t pt-4">
            <h4 className="font-semibold mb-2">Recommended Platforms:</h4>
            <div className="flex flex-wrap gap-2 mb-4">
              {contentRecommendations.recommended_platforms.map((platform) => (
                <span
                  key={platform}
                  className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm capitalize"
                >
                  {platform.replace('_', ' ')}
                </span>
              ))}
            </div>
            <div className="text-sm text-gray-600">
              <strong>Optimization Score:</strong> {(contentRecommendations.optimization_score * 100).toFixed(1)}%
            </div>
          </div>
        )}
      </div>

      {/* Platform Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(platforms).map(([platformId, platform]) => (
          <div
            key={platformId}
            className={`bg-white p-6 rounded-lg shadow cursor-pointer transition-all ${
              selectedPlatform === platformId ? 'ring-2 ring-purple-500' : 'hover:shadow-lg'
            }`}
            onClick={() => setSelectedPlatform(selectedPlatform === platformId ? null : platformId)}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold capitalize">{platformId.replace('_', ' ')}</h3>
              <div className="text-2xl">
                {platformId === 'instagram' && '📸'}
                {platformId === 'tiktok' && '🎵'}
                {platformId === 'youtube' && '📺'}
                {platformId === 'twitter' && '🐦'}
                {platformId === 'linkedin' && '💼'}
                {platformId === 'spotify' && '🎶'}
                {platformId === 'threads' && '🧵'}
                {platformId === 'tumblr' && '📝'}
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div>
                <strong>Primary Content:</strong> {platform.primary_content_types?.join(', ')}
              </div>
              <div>
                <strong>Audience:</strong> {platform.audience_demographics?.age_range}
              </div>
              <div>
                <strong>Best Engagement:</strong> {platform.engagement_metrics?.best_content_type}
              </div>
            </div>

            {selectedPlatform === platformId && (
              <div className="mt-4 pt-4 border-t space-y-3">
                <div>
                  <strong className="text-purple-600">Capabilities:</strong>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {platform.capabilities?.map((capability) => (
                      <span
                        key={capability}
                        className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs"
                      >
                        {capability.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <strong className="text-blue-600">Optimal Posting Times:</strong>
                  <div className="text-xs mt-1">
                    {platform.optimal_posting_schedule?.weekdays?.join(', ')}
                  </div>
                </div>

                <div>
                  <strong className="text-green-600">Monetization Options:</strong>
                  <div className="text-xs mt-1">
                    {platform.monetization_options?.join(', ')}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Optimization Rules */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Content Optimization Rules</h3>
        <div className="space-y-4">
          <div className="border-l-4 border-green-500 pl-4">
            <h4 className="font-semibold">Short-Form Video Content</h4>
            <p className="text-gray-600 text-sm">
              Recommended for TikTok, Instagram Reels, YouTube Shorts. Keep under 60 seconds with strong opening hook.
            </p>
            <div className="mt-2 text-xs text-green-600">
              Best posting times: 15:00-18:00, 20:00-23:00
            </div>
          </div>

          <div className="border-l-4 border-blue-500 pl-4">
            <h4 className="font-semibold">Music Content</h4>
            <p className="text-gray-600 text-sm">
              High-quality audio for Spotify, Apple Music, with cross-promotion on TikTok and Instagram.
            </p>
            <div className="mt-2 text-xs text-blue-600">
              Release strategy: Friday for streaming, promotional content throughout week
            </div>
          </div>

          <div className="border-l-4 border-purple-500 pl-4">
            <h4 className="font-semibold">Professional Content</h4>
            <p className="text-gray-600 text-sm">
              LinkedIn-focused with industry insights, business-appropriate timing and messaging.
            </p>
            <div className="mt-2 text-xs text-purple-600">
              Best posting times: 08:00-10:00, 17:00-18:00 (weekdays only)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Cross-Promotion Tab Component
const CrossPromotionTab = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [newCampaign, setNewCampaign] = useState({
    content_id: '',
    content_type: 'video',
    objective: 'awareness',
    target_platforms: [],
    routing_strategy: 'staggered',
    budget: 1000
  });
  const [loading, setLoading] = useState(false);

  const createCampaign = async () => {
    if (!newCampaign.content_id || newCampaign.target_platforms.length === 0) {
      alert('Please fill in content ID and select at least one platform');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/social-strategy/cross-promotion/campaign`, newCampaign, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setCampaigns([...campaigns, response.data.campaign]);
        setNewCampaign({
          content_id: '',
          content_type: 'video',
          objective: 'awareness',
          target_platforms: [],
          routing_strategy: 'staggered',
          budget: 1000
        });
        alert('Campaign created successfully!');
      }
    } catch (error) {
      console.error('Error creating campaign:', error);
      alert('Error creating campaign');
    } finally {
      setLoading(false);
    }
  };

  const executeCampaign = async (campaignId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/api/social-strategy/cross-promotion/execute/${campaignId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        alert('Campaign execution started!');
      }
    } catch (error) {
      console.error('Error executing campaign:', error);
      alert('Error executing campaign');
    }
  };

  const platformOptions = [
    'instagram', 'tiktok', 'youtube', 'twitter', 'facebook', 
    'linkedin', 'spotify', 'threads', 'tumblr'
  ];

  return (
    <div className="space-y-6">
      {/* Create New Campaign */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Create Cross-Promotion Campaign</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content ID</label>
            <input
              type="text"
              value={newCampaign.content_id}
              onChange={(e) => setNewCampaign({...newCampaign, content_id: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter content ID"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
            <select
              value={newCampaign.content_type}
              onChange={(e) => setNewCampaign({...newCampaign, content_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="video">Video</option>
              <option value="audio">Audio</option>
              <option value="image">Image</option>
              <option value="short_form">Short Form</option>
              <option value="music">Music</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Objective</label>
            <select
              value={newCampaign.objective}
              onChange={(e) => setNewCampaign({...newCampaign, objective: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="awareness">Brand Awareness</option>
              <option value="engagement">Engagement</option>
              <option value="traffic">Drive Traffic</option>
              <option value="conversions">Conversions</option>
              <option value="monetization">Monetization</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Routing Strategy</label>
            <select
              value={newCampaign.routing_strategy}
              onChange={(e) => setNewCampaign({...newCampaign, routing_strategy: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="simultaneous">Simultaneous</option>
              <option value="sequential">Sequential</option>
              <option value="staggered">Staggered</option>
              <option value="performance_based">Performance Based</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Target Platforms</label>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
            {platformOptions.map((platform) => (
              <label key={platform} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={newCampaign.target_platforms.includes(platform)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setNewCampaign({
                        ...newCampaign,
                        target_platforms: [...newCampaign.target_platforms, platform]
                      });
                    } else {
                      setNewCampaign({
                        ...newCampaign,
                        target_platforms: newCampaign.target_platforms.filter(p => p !== platform)
                      });
                    }
                  }}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm capitalize">{platform}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Budget ($)</label>
          <input
            type="number"
            value={newCampaign.budget}
            onChange={(e) => setNewCampaign({...newCampaign, budget: parseInt(e.target.value)})}
            className="w-full md:w-1/3 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            min="0"
          />
        </div>

        <button
          onClick={createCampaign}
          disabled={loading}
          className="mt-4 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating...' : 'Create Campaign'}
        </button>
      </div>

      {/* Campaign List */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 Active Campaigns</h3>
        
        {campaigns.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No campaigns created yet. Create your first campaign above!</p>
        ) : (
          <div className="space-y-4">
            {campaigns.map((campaign) => (
              <div key={campaign.campaign_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">Campaign {campaign.campaign_id}</h4>
                  <span className={`px-2 py-1 rounded text-xs ${
                    campaign.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {campaign.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <strong>Objective:</strong> {campaign.objective}
                  </div>
                  <div>
                    <strong>Platforms:</strong> {campaign.target_platforms.length}
                  </div>
                  <div>
                    <strong>Strategy:</strong> {campaign.routing_strategy}
                  </div>
                </div>

                <div className="mt-3 flex space-x-2">
                  <button
                    onClick={() => executeCampaign(campaign.campaign_id)}
                    className="bg-blue-600 text-white px-4 py-1 rounded text-sm hover:bg-blue-700"
                  >
                    Execute
                  </button>
                  <button className="bg-gray-600 text-white px-4 py-1 rounded text-sm hover:bg-gray-700">
                    Monitor
                  </button>
                  <button className="bg-green-600 text-white px-4 py-1 rounded text-sm hover:bg-green-700">
                    Report
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Smart Routing Insights */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Smart Routing Insights</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold mb-2">Performance-Based Routing</h4>
            <p className="text-gray-600 text-sm mb-3">
              Automatically optimize budget allocation based on real-time performance data.
            </p>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span>TikTok Performance:</span>
                <span className="text-green-600 font-semibold">+340% above average</span>
              </div>
              <div className="flex justify-between">
                <span>Instagram Performance:</span>
                <span className="text-blue-600 font-semibold">+180% above average</span>
              </div>
              <div className="flex justify-between">
                <span>YouTube Performance:</span>
                <span className="text-yellow-600 font-semibold">-15% below average</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Cross-Platform Synergy</h4>
            <p className="text-gray-600 text-sm mb-3">
              Best performing platform combinations for cross-promotion.
            </p>
            <div className="space-y-2 text-xs">
              <div className="bg-green-50 p-2 rounded">
                <strong>TikTok → Instagram:</strong> 67% engagement boost
              </div>
              <div className="bg-blue-50 p-2 rounded">
                <strong>YouTube → Twitter:</strong> 45% traffic increase
              </div>
              <div className="bg-purple-50 p-2 rounded">
                <strong>Spotify → TikTok:</strong> 89% music discovery
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Workflow Management Tab Component
const WorkflowManagementTab = () => {
  const [projects, setProjects] = useState([]);
  const [templates, setTemplates] = useState({});
  const [newProject, setNewProject] = useState({
    title: '',
    description: '',
    objective: '',
    target_platforms: [],
    template_id: '',
    budget: 5000
  });
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDashboard, setProjectDashboard] = useState(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/social-strategy/workflow/templates`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTemplates(response.data.templates);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const createProject = async () => {
    if (!newProject.title || !newProject.description || newProject.target_platforms.length === 0) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/social-strategy/workflow/project`, newProject, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        setProjects([...projects, response.data.project]);
        setNewProject({
          title: '',
          description: '',
          objective: '',
          target_platforms: [],
          template_id: '',
          budget: 5000
        });
        alert('Project created successfully!');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Error creating project');
    }
  };

  const viewProjectDashboard = async (projectId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/social-strategy/workflow/project/${projectId}/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjectDashboard(response.data.dashboard);
      setSelectedProject(projectId);
    } catch (error) {
      console.error('Error fetching project dashboard:', error);
    }
  };

  const workflowPhases = [
    { id: 'audience_mapping', name: 'Audience Mapping', icon: '🎯' },
    { id: 'content_planning', name: 'Content Planning', icon: '📋' },
    { id: 'asset_creation', name: 'Asset Creation', icon: '🎨' },
    { id: 'approval_workflow', name: 'Approval Workflow', icon: '✅' },
    { id: 'scheduling', name: 'Scheduling', icon: '📅' },
    { id: 'engagement', name: 'Engagement', icon: '💬' },
    { id: 'monitoring', name: 'Monitoring', icon: '📊' },
    { id: 'reporting', name: 'Reporting', icon: '📈' },
    { id: 'optimization', name: 'Optimization', icon: '⚡' },
    { id: 'repurposing', name: 'Repurposing', icon: '🔄' }
  ];

  return (
    <div className="space-y-6">
      {/* Create New Project */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📝 Create Workflow Project</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project Title</label>
            <input
              type="text"
              value={newProject.title}
              onChange={(e) => setNewProject({...newProject, title: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter project title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Template</label>
            <select
              value={newProject.template_id}
              onChange={(e) => setNewProject({...newProject, template_id: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Select Template</option>
              {Object.entries(templates).map(([id, template]) => (
                <option key={id} value={id}>{template.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            value={newProject.description}
            onChange={(e) => setNewProject({...newProject, description: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 h-20"
            placeholder="Describe your project objectives and goals"
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Objective</label>
          <input
            type="text"
            value={newProject.objective}
            onChange={(e) => setNewProject({...newProject, objective: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="e.g., Increase brand awareness, Launch new product"
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Target Platforms</label>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
            {['instagram', 'tiktok', 'youtube', 'twitter', 'facebook', 'linkedin', 'spotify'].map((platform) => (
              <label key={platform} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={newProject.target_platforms.includes(platform)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setNewProject({
                        ...newProject,
                        target_platforms: [...newProject.target_platforms, platform]
                      });
                    } else {
                      setNewProject({
                        ...newProject,
                        target_platforms: newProject.target_platforms.filter(p => p !== platform)
                      });
                    }
                  }}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm capitalize">{platform}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Budget ($)</label>
          <input
            type="number"
            value={newProject.budget}
            onChange={(e) => setNewProject({...newProject, budget: parseInt(e.target.value)})}
            className="w-full md:w-1/3 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            min="0"
          />
        </div>

        <button
          onClick={createProject}
          className="mt-4 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700"
        >
          Create Project
        </button>
      </div>

      {/* Workflow Templates */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📚 Workflow Templates</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(templates).map(([id, template]) => (
            <div key={id} className="border rounded-lg p-4">
              <h4 className="font-semibold mb-2">{template.name}</h4>
              <p className="text-gray-600 text-sm mb-3">{template.description}</p>
              
              <div className="space-y-2 text-xs">
                <div>
                  <strong>Category:</strong> {template.category}
                </div>
                <div>
                  <strong>Timeline:</strong> {Object.values(template.default_timeline).reduce((sum, days) => sum + days, 0)} days
                </div>
                <div>
                  <strong>Budget:</strong> ${Object.values(template.budget_template).reduce((sum, amount) => sum + amount, 0).toLocaleString()}
                </div>
              </div>

              <button
                onClick={() => setNewProject({...newProject, template_id: id})}
                className="mt-3 w-full bg-blue-600 text-white py-1 rounded text-sm hover:bg-blue-700"
              >
                Use Template
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 10-Phase Workflow Overview */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 10-Phase Content Management System</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {workflowPhases.map((phase, index) => (
            <div key={phase.id} className="text-center">
              <div className="bg-purple-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
                <span className="text-xl">{phase.icon}</span>
              </div>
              <div className="text-sm font-medium">{phase.name}</div>
              <div className="text-xs text-gray-500">Phase {index + 1}</div>
            </div>
          ))}
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          <div>
            <h4 className="font-semibold mb-2">Phase Details:</h4>
            <ul className="space-y-1 text-gray-600">
              <li>• <strong>Audience Mapping:</strong> Define ICPs and platform preferences</li>
              <li>• <strong>Content Planning:</strong> Build calendar with themes and goals</li>
              <li>• <strong>Asset Creation:</strong> Produce media (video, audio, images, copy)</li>
              <li>• <strong>Approval Workflow:</strong> Route through legal, brand, partner checks</li>
              <li>• <strong>Scheduling:</strong> Automate posts across platforms</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-2">Advanced Phases:</h4>
            <ul className="space-y-1 text-gray-600">
              <li>• <strong>Engagement:</strong> Respond to comments, DMs, mentions</li>
              <li>• <strong>Monitoring:</strong> Track performance, sentiment, virality</li>
              <li>• <strong>Reporting:</strong> Generate insights and ROI metrics</li>
              <li>• <strong>Optimization:</strong> A/B test formats, timing, messaging</li>
              <li>• <strong>Repurposing:</strong> Reuse high-performing content</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Project Dashboard */}
      {projectDashboard && (
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">📊 Project Dashboard</h3>
            <button
              onClick={() => setSelectedProject(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {projectDashboard.project_overview.completion_percentage.toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600">Completion</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {projectDashboard.project_overview.days_active}
              </div>
              <div className="text-sm text-gray-600">Days Active</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                ${projectDashboard.budget_status.remaining.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Budget Remaining</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {projectDashboard.upcoming_deadlines.length}
              </div>
              <div className="text-sm text-gray-600">Upcoming Deadlines</div>
            </div>
          </div>

          {/* Phase Progress */}
          <div className="mb-6">
            <h4 className="font-semibold mb-3">Phase Progress</h4>
            <div className="space-y-2">
              {Object.entries(projectDashboard.phase_progress).map(([phase, progress]) => (
                <div key={phase} className="flex items-center justify-between p-2 border rounded">
                  <span className="capitalize font-medium">{phase.replace('_', ' ')}</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    progress.completed ? 'bg-green-100 text-green-800' :
                    progress.current ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {progress.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming Deadlines */}
          {projectDashboard.upcoming_deadlines.length > 0 && (
            <div>
              <h4 className="font-semibold mb-3">Upcoming Deadlines</h4>
              <div className="space-y-2">
                {projectDashboard.upcoming_deadlines.slice(0, 5).map((deadline, index) => (
                  <div key={index} className="flex items-center justify-between p-2 border rounded">
                    <div>
                      <div className="font-medium">{deadline.title}</div>
                      <div className="text-sm text-gray-600">{deadline.type}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm">{new Date(deadline.due_date).toLocaleDateString()}</div>
                      <span className={`px-2 py-1 rounded text-xs ${
                        deadline.priority === 'high' ? 'bg-red-100 text-red-800' :
                        deadline.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {deadline.priority}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Project List */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📁 Projects</h3>
        
        {projects.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No projects created yet. Create your first project above!</p>
        ) : (
          <div className="space-y-4">
            {projects.map((project) => (
              <div key={project.project_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">{project.title}</h4>
                  <span className={`px-2 py-1 rounded text-xs ${
                    project.status === 'completed' ? 'bg-green-100 text-green-800' :
                    project.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {project.status}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-3">{project.description}</p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-3">
                  <div>
                    <strong>Current Phase:</strong> {project.current_phase.replace('_', ' ')}
                  </div>
                  <div>
                    <strong>Platforms:</strong> {project.target_platforms.length}
                  </div>
                  <div>
                    <strong>Budget:</strong> ${project.budget.toLocaleString()}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => viewProjectDashboard(project.project_id)}
                    className="bg-blue-600 text-white px-4 py-1 rounded text-sm hover:bg-blue-700"
                  >
                    Dashboard
                  </button>
                  <button className="bg-green-600 text-white px-4 py-1 rounded text-sm hover:bg-green-700">
                    Advance Phase
                  </button>
                  <button className="bg-gray-600 text-white px-4 py-1 rounded text-sm hover:bg-gray-700">
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Analytics Tab Component
const AnalyticsTab = () => {
  const [comprehensiveReport, setComprehensiveReport] = useState(null);
  const [selectedDateRange, setSelectedDateRange] = useState('30d');
  const [platformAnalytics, setPlatformAnalytics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComprehensiveReport();
    fetchPlatformAnalytics();
  }, [selectedDateRange]);

  const fetchComprehensiveReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API}/api/social-strategy/strategy/comprehensive-report?date_range=${selectedDateRange}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setComprehensiveReport(response.data.report);
    } catch (error) {
      console.error('Error fetching comprehensive report:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPlatformAnalytics = async () => {
    const platforms = ['instagram', 'tiktok', 'youtube', 'twitter'];
    
    for (const platform of platforms) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API}/api/social-strategy/analytics/${platform}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setPlatformAnalytics(prev => ({
          ...prev,
          [platform]: response.data.analytics
        }));
      } catch (error) {
        console.error(`Error fetching ${platform} analytics:`, error);
      }
    }
  };

  if (loading) {
    return <div className="text-center">Loading analytics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Date Range Selector */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">📈 Analytics Dashboard</h3>
          <select
            value={selectedDateRange}
            onChange={(e) => setSelectedDateRange(e.target.value)}
            className="p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Executive Summary */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Executive Summary</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {comprehensiveReport.executive_summary.total_campaigns}
              </div>
              <div className="text-sm text-gray-600">Total Campaigns</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {comprehensiveReport.executive_summary.total_reach.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Total Reach</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {comprehensiveReport.executive_summary.average_engagement_rate}%
              </div>
              <div className="text-sm text-gray-600">Avg Engagement Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">
                {comprehensiveReport.executive_summary.conversion_rate}%
              </div>
              <div className="text-sm text-gray-600">Conversion Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">
                {comprehensiveReport.executive_summary.roi}%
              </div>
              <div className="text-sm text-gray-600">ROI</div>
            </div>
          </div>
        </div>
      )}

      {/* Platform Performance */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Platform Performance</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(comprehensiveReport.platform_performance).map(([platform, metrics]) => (
              <div key={platform} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold capitalize">{platform}</h4>
                  <div className="text-2xl">
                    {platform === 'instagram' && '📸'}
                    {platform === 'tiktok' && '🎵'}
                    {platform === 'youtube' && '📺'}
                    {platform === 'twitter' && '🐦'}
                  </div>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Reach:</span>
                    <span className="font-semibold">{metrics.reach.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Engagement Rate:</span>
                    <span className={`font-semibold ${metrics.engagement_rate > 4 ? 'text-green-600' : 'text-gray-600'}`}>
                      {metrics.engagement_rate}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Conversions:</span>
                    <span className="font-semibold">{metrics.conversions}</span>
                  </div>
                </div>

                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: `${Math.min(metrics.engagement_rate * 10, 100)}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">Engagement Performance</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Content Intelligence Insights */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🧠 Content Intelligence Insights</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3">Best Performing Content Types</h4>
              <div className="space-y-2">
                {comprehensiveReport.content_intelligence_insights.best_performing_content_types.map((type, index) => (
                  <div key={type} className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center text-xs font-semibold text-purple-700">
                      {index + 1}
                    </div>
                    <span className="capitalize">{type.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-3">Optimal Posting Times</h4>
              <div className="space-y-2 text-sm">
                {Object.entries(comprehensiveReport.content_intelligence_insights.optimal_posting_times).map(([platform, time]) => (
                  <div key={platform} className="flex justify-between">
                    <span className="capitalize">{platform}:</span>
                    <span className="font-semibold">{time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6">
            <h4 className="font-semibold mb-3">Hashtag Performance</h4>
            <div className="flex space-x-4">
              {Object.entries(comprehensiveReport.content_intelligence_insights.hashtag_performance).map(([type, score]) => (
                <div key={type} className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{score}</div>
                  <div className="text-sm text-gray-600 capitalize">{type}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Cross-Promotion Effectiveness */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔄 Cross-Promotion Effectiveness</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {comprehensiveReport.cross_promotion_effectiveness.campaigns_run}
              </div>
              <div className="text-sm text-gray-600">Campaigns Run</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {comprehensiveReport.cross_promotion_effectiveness.average_lift}
              </div>
              <div className="text-sm text-gray-600">Average Lift</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {comprehensiveReport.cross_promotion_effectiveness.best_platform_combinations.length}
              </div>
              <div className="text-sm text-gray-600">Top Combinations</div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Best Platform Combinations</h4>
            <div className="space-y-2">
              {comprehensiveReport.cross_promotion_effectiveness.best_platform_combinations.map((combo) => (
                <div key={combo} className="bg-green-50 p-3 rounded-lg">
                  <span className="font-semibold capitalize">{combo.replace('_', ' → ')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Workflow Efficiency */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Workflow Efficiency</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Object.entries(comprehensiveReport.workflow_efficiency).map(([metric, value]) => (
              <div key={metric} className="text-center">
                <div className="text-2xl font-bold text-orange-600">{value}</div>
                <div className="text-sm text-gray-600 capitalize">{metric.replace('_', ' ')}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Strategic Recommendations</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold mb-3 text-purple-600">Strategic</h4>
              <ul className="space-y-2 text-sm">
                {comprehensiveReport.recommendations.strategic.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-purple-600 mt-0.5">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-3 text-blue-600">Tactical</h4>
              <ul className="space-y-2 text-sm">
                {comprehensiveReport.recommendations.tactical.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-3 text-green-600">Budget</h4>
              <ul className="space-y-2 text-sm">
                {comprehensiveReport.recommendations.budget.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-green-600 mt-0.5">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Next Quarter Forecast */}
      {comprehensiveReport && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔮 Next Quarter Forecast</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {comprehensiveReport.next_quarter_forecast.projected_reach.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Projected Reach</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {comprehensiveReport.next_quarter_forecast.estimated_engagement_rate}%
              </div>
              <div className="text-sm text-gray-600">Est. Engagement Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {comprehensiveReport.next_quarter_forecast.predicted_conversions}
              </div>
              <div className="text-sm text-gray-600">Predicted Conversions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">
                {comprehensiveReport.next_quarter_forecast.expected_roi}%
              </div>
              <div className="text-sm text-gray-600">Expected ROI</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SocialMediaStrategyDashboard;