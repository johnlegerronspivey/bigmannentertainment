import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  BarChart3, 
  MapPin, 
  Target, 
  Zap, 
  Monitor,
  Globe,
  Calendar,
  DollarSign,
  TrendingUp,
  Eye,
  MousePointer,
  Users,
  Smartphone,
  Cloud,
  Sun,
  CloudRain,
  Snowflake,
  Activity,
  Settings,
  Download,
  Plus,
  Edit,
  Trash2,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Layers
} from 'lucide-react';

const PDOOHCampaignManager = () => {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [platforms, setPlatforms] = useState({});
  const [triggers, setTriggers] = useState([]);
  const [performance, setPerformance] = useState({});
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const BACKEND_URL = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  // Sample data for demonstration
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      // Load campaigns
      const sampleCampaigns = [
        {
          id: 'campaign_001',
          name: 'Summer Music Festival 2025',
          campaign_type: 'artist_promotion',
          status: 'active',
          budget_total: 25000,
          budget_spent: 18750,
          start_date: '2025-01-15T00:00:00Z',
          end_date: '2025-02-15T00:00:00Z',
          platforms: ['trade_desk', 'vistar_media', 'hivestack'],
          impressions: 2450000,
          ctr: 0.34,
          conversions: 847
        },
        {
          id: 'campaign_002',
          name: 'New Artist Spotlight',
          campaign_type: 'release_announcement',
          status: 'paused',
          budget_total: 15000,
          budget_spent: 8200,
          start_date: '2025-01-10T00:00:00Z',
          end_date: '2025-01-31T00:00:00Z',
          platforms: ['broadsign', 'viooh'],
          impressions: 1230000,
          ctr: 0.28,
          conversions: 445
        },
        {
          id: 'campaign_003',
          name: 'Concert Tour Promotion',
          campaign_type: 'event_promotion',
          status: 'draft',
          budget_total: 35000,
          budget_spent: 0,
          start_date: '2025-02-01T00:00:00Z',
          end_date: '2025-03-01T00:00:00Z',
          platforms: ['trade_desk', 'vistar_media', 'hivestack', 'broadsign'],
          impressions: 0,
          ctr: 0,
          conversions: 0
        }
      ];
      setCampaigns(sampleCampaigns);

      // Load platforms
      const samplePlatforms = {
        trade_desk: { name: 'The Trade Desk', features: ['dsp', 'audience_targeting'], bidding_model: 'rtb' },
        vistar_media: { name: 'Vistar Media', features: ['dsp', 'location_intelligence'], bidding_model: 'rtb' },
        hivestack: { name: 'Hivestack', features: ['ssp', 'exchange'], bidding_model: 'rtb' },
        broadsign: { name: 'Broadsign', features: ['header_bidder', 'programmatic'], bidding_model: 'cpm' },
        viooh: { name: 'VIOOH', features: ['inventory_management', 'audience_data'], bidding_model: 'programmatic_guaranteed' }
      };
      setPlatforms(samplePlatforms);

      // Load dashboard data
      const sampleDashboard = {
        campaign_overview: {
          total_campaigns: 3,
          active_campaigns: 1,
          paused_campaigns: 1,
          completed_campaigns: 0
        },
        budget_overview: {
          total_budget: 75000,
          total_spend: 26950,
          remaining_budget: 48050,
          budget_utilization: 35.9
        },
        performance_metrics: {
          total_impressions: 3680000,
          total_reach: 2840000,
          average_cpm: 7.32,
          average_ctr: 0.31,
          total_conversions: 1292
        },
        trigger_analytics: {
          total_trigger_evaluations: 1247,
          successful_triggers: 892,
          trigger_success_rate: 71.5,
          most_active_triggers: [
            { type: 'weather', count: 342 },
            { type: 'time_based', count: 287 },
            { type: 'sports', count: 156 },
            { type: 'events', count: 107 }
          ]
        }
      };
      setDashboardData(sampleDashboard);

    } catch (error) {
      console.error('Error loading data:', error);
    }
    setLoading(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Play className="w-4 h-4 text-green-500" />;
      case 'paused': return <Pause className="w-4 h-4 text-yellow-500" />;
      case 'draft': return <Edit className="w-4 h-4 text-gray-500" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-blue-500" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">pDOOH Campaign Dashboard</h2>
          <p className="text-gray-600">Programmatic Digital Out-of-Home advertising management</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>New Campaign</span>
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Campaigns</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardData.campaign_overview?.active_campaigns || 0}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-gray-600">
              Total: {dashboardData.campaign_overview?.total_campaigns || 0} campaigns
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Impressions</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatNumber(dashboardData.performance_metrics?.total_impressions || 0)}
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Eye className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-green-600">
              Avg CPM: ${dashboardData.performance_metrics?.average_cpm || 0}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Budget Spent</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatCurrency(dashboardData.budget_overview?.total_spend || 0)}
              </p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-gray-600">
              {dashboardData.budget_overview?.budget_utilization || 0}% utilization
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Conversions</p>
              <p className="text-3xl font-bold text-gray-900">
                {formatNumber(dashboardData.performance_metrics?.total_conversions || 0)}
              </p>
            </div>
            <div className="bg-orange-100 p-3 rounded-full">
              <Target className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-green-600">
              CTR: {dashboardData.performance_metrics?.average_ctr || 0}%
            </span>
          </div>
        </div>
      </div>

      {/* Trigger Analytics */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Real-Time Trigger Analytics</h3>
          <Zap className="w-5 h-5 text-yellow-500" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Trigger Success Rate</span>
              <span className="text-lg font-semibold text-green-600">
                {dashboardData.trigger_analytics?.trigger_success_rate || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${dashboardData.trigger_analytics?.trigger_success_rate || 0}%` }}
              ></div>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Most Active Triggers</h4>
            <div className="space-y-2">
              {dashboardData.trigger_analytics?.most_active_triggers?.map((trigger, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 capitalize">{trigger.type}</span>
                  <span className="text-sm font-medium text-gray-900">{trigger.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCampaigns = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Campaign Management</h2>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Create Campaign</span>
          </button>
        </div>
      </div>

      <div className="grid gap-6">
        {campaigns.map((campaign) => (
          <div key={campaign.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center space-x-3">
                {getStatusIcon(campaign.status)}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
                  <p className="text-sm text-gray-600 capitalize">{campaign.campaign_type.replace('_', ' ')}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(campaign.status)}`}>
                  {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                </span>
                <button
                  onClick={() => setSelectedCampaign(campaign)}
                  className="text-purple-600 hover:text-purple-800"
                >
                  <BarChart3 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-xs text-gray-500">Budget</p>
                <p className="text-sm font-medium">{formatCurrency(campaign.budget_total)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Spent</p>
                <p className="text-sm font-medium">{formatCurrency(campaign.budget_spent)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Impressions</p>
                <p className="text-sm font-medium">{formatNumber(campaign.impressions)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">CTR</p>
                <p className="text-sm font-medium">{campaign.ctr}%</p>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Monitor className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">{campaign.platforms.length} platforms</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-600">
                    {new Date(campaign.start_date).toLocaleDateString()} - {new Date(campaign.end_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="flex space-x-2">
                {campaign.status === 'active' && (
                  <button className="p-2 text-yellow-600 hover:bg-yellow-50 rounded">
                    <Pause className="w-4 h-4" />
                  </button>
                )}
                {campaign.status === 'paused' && (
                  <button className="p-2 text-green-600 hover:bg-green-50 rounded">
                    <Play className="w-4 h-4" />
                  </button>
                )}
                <button className="p-2 text-gray-600 hover:bg-gray-50 rounded">
                  <Edit className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-4">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Budget Progress</span>
                <span>{Math.round((campaign.budget_spent / campaign.budget_total) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-purple-600 h-2 rounded-full" 
                  style={{ width: `${Math.min((campaign.budget_spent / campaign.budget_total) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderPlatforms = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Platform Integration</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(platforms).map(([key, platform]) => (
          <div key={key} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Bidding Model</p>
                <p className="text-sm font-medium text-gray-900 capitalize">{platform.bidding_model.replace('_', ' ')}</p>
              </div>
              
              <div>
                <p className="text-sm text-gray-600">Features</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {platform.features.map((feature, index) => (
                    <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                      {feature.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <button className="w-full text-purple-600 hover:text-purple-800 text-sm font-medium">
                View Inventory
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTriggers = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Real-Time Triggers & DCO</h2>
        <button className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
          <Plus className="w-4 h-4" />
          <span>Create Trigger</span>
        </button>
      </div>

      {/* Weather Triggers */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Sun className="w-5 h-5 text-yellow-500" />
          <h3 className="text-lg font-semibold text-gray-900">Weather-Based Triggers</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Sun className="w-4 h-4 text-orange-500" />
              <span className="font-medium">Hot Weather</span>
            </div>
            <p className="text-sm text-gray-600">Temperature &gt; 25°C</p>
            <p className="text-xs text-green-600 mt-1">342 triggers this month</p>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <CloudRain className="w-4 h-4 text-blue-500" />
              <span className="font-medium">Rainy Day</span>
            </div>
            <p className="text-sm text-gray-600">Precipitation detected</p>
            <p className="text-xs text-green-600 mt-1">128 triggers this month</p>
          </div>
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Snowflake className="w-4 h-4 text-blue-300" />
              <span className="font-medium">Cold Weather</span>
            </div>
            <p className="text-sm text-gray-600">Temperature &lt; 5°C</p>
            <p className="text-xs text-green-600 mt-1">87 triggers this month</p>
          </div>
        </div>
      </div>

      {/* Sports & Events Triggers */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Activity className="w-5 h-5 text-green-500" />
          <h3 className="text-lg font-semibold text-gray-900">Sports & Events Triggers</h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="font-medium">Live Game: Lakers vs Warriors</span>
            </div>
            <span className="text-sm text-green-600">Active trigger</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="font-medium">Music Festival Tonight</span>
            </div>
            <span className="text-sm text-blue-600">Scheduled</span>
          </div>
        </div>
      </div>

      {/* Creative Variants */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Dynamic Creative Variants</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Available Variants</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 border rounded">
                <span className="text-sm">Default Creative</span>
                <span className="text-xs text-gray-500">Always active</span>
              </div>
              <div className="flex items-center justify-between p-2 border rounded">
                <span className="text-sm">Summer Theme</span>
                <span className="text-xs text-orange-500">Hot weather trigger</span>
              </div>
              <div className="flex items-center justify-between p-2 border rounded">
                <span className="text-sm">Rainy Day Indoor</span>
                <span className="text-xs text-blue-500">Rain trigger</span>
              </div>
              <div className="flex items-center justify-between p-2 border rounded">
                <span className="text-sm">Sports Excitement</span>
                <span className="text-xs text-green-500">Live sports trigger</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Optimization Performance</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Trigger Success Rate</span>
                <span className="text-sm font-medium text-green-600">71.5%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">CTR Improvement</span>
                <span className="text-sm font-medium text-green-600">+23%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Engagement Lift</span>
                <span className="text-sm font-medium text-green-600">+31%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Analytics & Attribution</h2>
      
      {/* Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Total Reach</h3>
            <Users className="w-5 h-5 text-blue-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">2.84M</p>
          <p className="text-sm text-green-600 mt-2">+15.2% vs last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Attribution Rate</h3>
            <Target className="w-5 h-5 text-purple-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">75.3%</p>
          <p className="text-sm text-green-600 mt-2">+5.1% vs last month</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Footfall Lift</h3>
            <MapPin className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">23.7%</p>
          <p className="text-sm text-green-600 mt-2">Above industry avg</p>
        </div>
      </div>

      {/* Attribution Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Attribution Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Conversion Types</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Streaming Plays</span>
                <span className="text-sm font-medium">234 (48%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Website Visits</span>
                <span className="text-sm font-medium">156 (32%)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">App Installs</span>
                <span className="text-sm font-medium">98 (20%)</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-3">Platform Performance</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Vistar Media</span>
                <span className="text-sm font-medium text-green-600">82.1%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Trade Desk</span>
                <span className="text-sm font-medium text-green-600">73.8%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Hivestack</span>
                <span className="text-sm font-medium text-green-600">69.2%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Export Reports</h3>
          <Download className="w-5 h-5 text-gray-400" />
        </div>
        <div className="flex space-x-4">
          <button className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
            <Download className="w-4 h-4" />
            <span>CSV Export</span>
          </button>
          <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            <Download className="w-4 h-4" />
            <span>PDF Report</span>
          </button>
          <button className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
            <Download className="w-4 h-4" />
            <span>JSON Data</span>
          </button>
        </div>
      </div>
    </div>
  );

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
    { id: 'campaigns', name: 'Campaigns', icon: Monitor },
    { id: 'platforms', name: 'Platforms', icon: Globe },
    { id: 'triggers', name: 'Triggers & DCO', icon: Zap },
    { id: 'analytics', name: 'Analytics', icon: TrendingUp }
  ];

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Tab Navigation */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' && renderDashboard()}
      {activeTab === 'campaigns' && renderCampaigns()}
      {activeTab === 'platforms' && renderPlatforms()}
      {activeTab === 'triggers' && renderTriggers()}
      {activeTab === 'analytics' && renderAnalytics()}

      {/* Create Campaign Modal Placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Create New pDOOH Campaign</h3>
              <button 
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <p className="text-gray-600 mb-4">Campaign creation form would go here...</p>
            <div className="flex justify-end space-x-3">
              <button 
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                Create Campaign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PDOOHCampaignManager;