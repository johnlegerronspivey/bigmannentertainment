import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Workflow Integration Dashboard
export const WorkflowIntegrationDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/workflow-integration/dashboard/workflows`);
      setDashboardData(response.data.dashboard);
      setError('');
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500"></div>
          <p className="mt-4 text-gray-600">Loading Workflow Integration Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Workflow Integration Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Manage your content workflows across 120+ platforms and social media strategies
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: '📊' },
              { id: 'content-workflow', name: 'Content Workflow', icon: '🎯' },
              { id: 'social-strategy', name: 'Social Media Strategy', icon: '🚀' },
              { id: 'platforms', name: 'Platform Integration', icon: '🌐' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
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
        {activeTab === 'overview' && (
          <OverviewTab dashboardData={dashboardData} onRefresh={fetchDashboardData} />
        )}
        {activeTab === 'content-workflow' && (
          <ContentWorkflowTab />
        )}
        {activeTab === 'social-strategy' && (
          <SocialStrategyTab />
        )}
        {activeTab === 'platforms' && (
          <PlatformIntegrationTab />
        )}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ dashboardData, onRefresh }) => {
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    fetchHealthData();
  }, []);

  const fetchHealthData = async () => {
    try {
      const response = await axios.get(`${API}/workflow-integration/health`);
      setHealthData(response.data);
    } catch (error) {
      console.error('Error fetching health data:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* System Health */}
      {healthData && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className={`text-2xl font-bold ${healthData.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                {healthData.status === 'healthy' ? '✅' : '❌'}
              </div>
              <p className="text-sm text-gray-600">Overall Status</p>
              <p className="font-medium">{healthData.status}</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {healthData.platform_integration?.total_platforms || 0}
              </div>
              <p className="text-sm text-gray-600">Total Platforms</p>
              <p className="font-medium">Content Workflow</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {healthData.platform_integration?.social_media_platforms || 0}
              </div>
              <p className="text-sm text-gray-600">Social Media</p>
              <p className="font-medium">Strategy Platforms</p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                  <span className="text-blue-600 font-semibold">🎯</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Content Workflows</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.content_workflow_stats?.total_workflows || 0}
                </p>
              </div>
            </div>
            <div className="mt-2">
              <p className="text-sm text-gray-600">
                {dashboardData.content_workflow_stats?.active_workflows || 0} active
              </p>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center">
                  <span className="text-purple-600 font-semibold">🚀</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Social Strategies</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.social_strategy_stats?.total_strategies || 0}
                </p>
              </div>
            </div>
            <div className="mt-2">
              <p className="text-sm text-gray-600">
                {dashboardData.social_strategy_stats?.active_strategies || 0} active
              </p>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
                  <span className="text-green-600 font-semibold">🌐</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Platforms Used</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.content_workflow_stats?.total_platforms_used || 0}
                </p>
              </div>
            </div>
            <div className="mt-2">
              <p className="text-sm text-gray-600">Content distribution</p>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center">
                  <span className="text-yellow-600 font-semibold">📱</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Social Platforms</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {dashboardData.social_strategy_stats?.total_social_platforms_used || 0}
                </p>
              </div>
            </div>
            <div className="mt-2">
              <p className="text-sm text-gray-600">Strategy campaigns</p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activities */}
      {dashboardData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Content Workflows */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Content Workflows</h3>
            {dashboardData.recent_content_workflows?.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.recent_content_workflows.map((workflow, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{workflow.content_title || `Workflow ${workflow.workflow_id?.slice(0, 8)}`}</p>
                      <p className="text-sm text-gray-600">
                        Status: <span className="capitalize">{workflow.status}</span> • 
                        {workflow.target_platforms?.length || 0} platforms
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-purple-600">
                        {workflow.progress_percentage || 0}%
                      </p>
                      <p className="text-xs text-gray-500">
                        {workflow.created_at ? new Date(workflow.created_at).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No content workflows yet</p>
            )}
          </div>

          {/* Recent Social Strategies */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Social Media Strategies</h3>
            {dashboardData.recent_social_strategies?.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.recent_social_strategies.map((strategy, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{strategy.strategy_name}</p>
                      <p className="text-sm text-gray-600">
                        Status: <span className="capitalize">{strategy.strategy_status}</span> • 
                        {strategy.target_platforms?.length || 0} platforms
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-blue-600">
                        {strategy.progress_percentage || 0}%
                      </p>
                      <p className="text-xs text-gray-500">
                        {strategy.created_at ? new Date(strategy.created_at).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No social media strategies yet</p>
            )}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => window.location.href = '/upload'}
            className="flex items-center justify-center px-4 py-3 border border-purple-300 rounded-md text-purple-700 bg-purple-50 hover:bg-purple-100 transition-colors"
          >
            <span className="mr-2">📤</span>
            Upload Content
          </button>
          <button
            onClick={onRefresh}
            className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md text-gray-700 bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <span className="mr-2">🔄</span>
            Refresh Dashboard
          </button>
          <button
            onClick={() => window.location.href = '/platforms'}
            className="flex items-center justify-center px-4 py-3 border border-blue-300 rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
          >
            <span className="mr-2">🌐</span>
            View All Platforms
          </button>
        </div>
      </div>
    </div>
  );
};

// Content Workflow Tab Component
const ContentWorkflowTab = () => {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    content_id: '',
    target_platforms: [],
    quality_profile: 'standard',
    custom_settings: ''
  });

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      // This would fetch user's workflows - for now we'll show empty state
      setWorkflows([]);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkflow = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('content_id', newWorkflow.content_id);
      formData.append('quality_profile', newWorkflow.quality_profile);
      if (newWorkflow.custom_settings) {
        formData.append('custom_settings', newWorkflow.custom_settings);
      }

      const response = await axios.post(`${API}/workflow-integration/content-workflow`, formData);
      
      if (response.data.success) {
        alert('Content workflow created successfully!');
        setShowCreateForm(false);
        setNewWorkflow({
          content_id: '',
          target_platforms: [],
          quality_profile: 'standard',
          custom_settings: ''
        });
        fetchWorkflows();
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
      alert('Failed to create workflow: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Content Workflows</h2>
          <p className="text-gray-600">Manage content distribution across all 120+ platforms</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md font-medium"
        >
          Create New Workflow
        </button>
      </div>

      {/* Create Workflow Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create Content Workflow</h3>
            <form onSubmit={handleCreateWorkflow} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content ID
                </label>
                <input
                  type="text"
                  required
                  value={newWorkflow.content_id}
                  onChange={(e) => setNewWorkflow({...newWorkflow, content_id: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter content ID"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quality Profile
                </label>
                <select
                  value={newWorkflow.quality_profile}
                  onChange={(e) => setNewWorkflow({...newWorkflow, quality_profile: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="standard">Standard</option>
                  <option value="premium">Premium</option>
                  <option value="broadcast">Broadcast</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Custom Settings (JSON)
                </label>
                <textarea
                  value={newWorkflow.custom_settings}
                  onChange={(e) => setNewWorkflow({...newWorkflow, custom_settings: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows="3"
                  placeholder='{"setting": "value"}'
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                >
                  Create Workflow
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Workflows List */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Workflows</h3>
        {workflows.length > 0 ? (
          <div className="space-y-4">
            {workflows.map((workflow, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900">{workflow.content_title}</h4>
                    <p className="text-sm text-gray-600">
                      Status: {workflow.status} | Progress: {workflow.progress_percentage}%
                    </p>
                    <p className="text-sm text-gray-600">
                      Platforms: {workflow.target_platforms?.length || 0}
                    </p>
                  </div>
                  <button className="text-purple-600 hover:text-purple-800 text-sm">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🎯</div>
            <p className="text-gray-500 mb-4">No content workflows yet</p>
            <p className="text-sm text-gray-400">
              Create your first workflow to distribute content across all platforms
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Social Strategy Tab Component
const SocialStrategyTab = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newStrategy, setNewStrategy] = useState({
    strategy_name: '',
    campaign_objective: 'brand_awareness',
    campaign_duration_days: 30,
    budget_per_platform: 100
  });

  const handleCreateStrategy = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('strategy_name', newStrategy.strategy_name);
      formData.append('campaign_objective', newStrategy.campaign_objective);
      formData.append('campaign_duration_days', newStrategy.campaign_duration_days);
      formData.append('budget_per_platform', newStrategy.budget_per_platform);

      const response = await axios.post(`${API}/workflow-integration/social-media-strategy`, formData);
      
      if (response.data.success) {
        alert('Social media strategy created successfully!');
        setShowCreateForm(false);
        setNewStrategy({
          strategy_name: '',
          campaign_objective: 'brand_awareness',
          campaign_duration_days: 30,
          budget_per_platform: 100
        });
      }
    } catch (error) {
      console.error('Error creating strategy:', error);
      alert('Failed to create strategy: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Social Media Strategies</h2>
          <p className="text-gray-600">Advanced social media campaigns (Phases 5-10) across 21 platforms</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md font-medium"
        >
          Create New Strategy
        </button>
      </div>

      {/* Create Strategy Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create Social Media Strategy</h3>
            <form onSubmit={handleCreateStrategy} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Strategy Name
                </label>
                <input
                  type="text"
                  required
                  value={newStrategy.strategy_name}
                  onChange={(e) => setNewStrategy({...newStrategy, strategy_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter strategy name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Campaign Objective
                </label>
                <select
                  value={newStrategy.campaign_objective}
                  onChange={(e) => setNewStrategy({...newStrategy, campaign_objective: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="brand_awareness">Brand Awareness</option>
                  <option value="engagement">Engagement</option>
                  <option value="traffic">Traffic</option>
                  <option value="conversions">Conversions</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Campaign Duration (Days)
                </label>
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={newStrategy.campaign_duration_days}
                  onChange={(e) => setNewStrategy({...newStrategy, campaign_duration_days: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget per Platform ($)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={newStrategy.budget_per_platform}
                  onChange={(e) => setNewStrategy({...newStrategy, budget_per_platform: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                >
                  Create Strategy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Strategies List */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Strategies</h3>
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🚀</div>
          <p className="text-gray-500 mb-4">No social media strategies yet</p>
          <p className="text-sm text-gray-400">
            Create your first strategy to launch campaigns across social platforms
          </p>
        </div>
      </div>
    </div>
  );
};

// Platform Integration Tab Component
const PlatformIntegrationTab = () => {
  const [platformData, setPlatformData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlatformData();
  }, []);

  const fetchPlatformData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/workflow-integration/platforms/overview`);
      setPlatformData(response.data.overview);
    } catch (error) {
      console.error('Error fetching platform data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading platform data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Platform Integration</h2>
        <p className="text-gray-600">Overview of all integrated platforms and their capabilities</p>
      </div>

      {/* Platform Stats */}
      {platformData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {platformData.total_platforms}
            </div>
            <p className="text-gray-600">Total Platforms</p>
            <p className="text-sm text-gray-500">Content distribution</p>
          </div>
          
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {platformData.social_media_platforms}
            </div>
            <p className="text-gray-600">Social Media</p>
            <p className="text-sm text-gray-500">Strategy campaigns</p>
          </div>
          
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {platformData.content_workflow_platforms}
            </div>
            <p className="text-gray-600">Workflow Enabled</p>
            <p className="text-sm text-gray-500">Full automation</p>
          </div>
        </div>
      )}

      {/* Platform Categories */}
      {platformData && platformData.platform_categories && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Categories</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(platformData.platform_categories).map(([category, count]) => (
              <div key={category} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-gray-900 capitalize">
                    {category.replace(/_/g, ' ')}
                  </span>
                  <span className="text-lg font-bold text-purple-600">{count}</span>
                </div>
                <p className="text-sm text-gray-500 mt-1">platforms</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Platform Management Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Management</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => window.location.href = '/platforms'}
            className="flex items-center justify-center px-4 py-3 border border-blue-300 rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
          >
            <span className="mr-2">🌐</span>
            View All Platforms
          </button>
          <button
            onClick={() => window.location.href = '/distribute'}
            className="flex items-center justify-center px-4 py-3 border border-purple-300 rounded-md text-purple-700 bg-purple-50 hover:bg-purple-100 transition-colors"
          >
            <span className="mr-2">🚀</span>
            Start Distribution
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkflowIntegrationDashboard;