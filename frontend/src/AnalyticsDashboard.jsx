import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  TrendingUp, 
  TrendingDown, 
  Eye, 
  MousePointer, 
  Users, 
  DollarSign,
  MapPin,
  Clock,
  Calendar,
  Download,
  Filter,
  RefreshCw,
  Target,
  Zap,
  Globe,
  Activity,
  AlertCircle,
  CheckCircle,
  Info
} from 'lucide-react';

// AWS Amplify imports
import { API, Auth } from 'aws-amplify';

const AnalyticsDashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedCampaign, setSelectedCampaign] = useState('all');
  const [selectedMetric, setSelectedMetric] = useState('impressions');
  const [loading, setLoading] = useState(false);
  const [campaigns, setCampaigns] = useState([]);
  const [realTimeData, setRealTimeData] = useState({});

  // Time range options
  const timeRanges = [
    { id: '24h', name: 'Last 24 Hours' },
    { id: '7d', name: 'Last 7 Days' },
    { id: '30d', name: 'Last 30 Days' },
    { id: '90d', name: 'Last 90 Days' },
    { id: 'custom', name: 'Custom Range' }
  ];

  // Available metrics for visualization
  const metrics = [
    { id: 'impressions', name: 'Impressions', icon: Eye, color: 'blue' },
    { id: 'clicks', name: 'Clicks', icon: MousePointer, color: 'green' },
    { id: 'reach', name: 'Reach', icon: Users, color: 'purple' },
    { id: 'spend', name: 'Spend', icon: DollarSign, color: 'red' },
    { id: 'ctr', name: 'CTR', icon: Target, color: 'yellow' },
    { id: 'footfall', name: 'Footfall', icon: MapPin, color: 'teal' }
  ];

  useEffect(() => {
    loadDashboardData();
    loadCampaigns();
    
    // Set up real-time data polling
    const interval = setInterval(loadRealTimeData, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, [selectedTimeRange, selectedCampaign]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const response = await API.get('doohapi', '/analytics/dashboard', {
        queryStringParameters: {
          timeRange: selectedTimeRange,
          campaign: selectedCampaign
        },
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });
      setDashboardData(response.data || {});
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // Mock data for demonstration
      setDashboardData({
        overview: {
          totalImpressions: 12450000,
          totalClicks: 42560,
          totalReach: 8950000,
          totalSpend: 156780,
          averageCTR: 0.34,
          totalFootfall: 234500,
          activeCampaigns: 8,
          activeTriggers: 15
        },
        trends: {
          impressions: [
            { date: '2025-01-09', value: 1850000 },
            { date: '2025-01-10', value: 1920000 },
            { date: '2025-01-11', value: 1780000 },
            { date: '2025-01-12', value: 2100000 },
            { date: '2025-01-13', value: 1950000 },
            { date: '2025-01-14', value: 2200000 },
            { date: '2025-01-15', value: 2250000 }
          ],
          clicks: [
            { date: '2025-01-09', value: 6300 },
            { date: '2025-01-10', value: 6720 },
            { date: '2025-01-11', value: 5940 },
            { date: '2025-01-12', value: 7140 },
            { date: '2025-01-13', value: 6630 },
            { date: '2025-01-14', value: 7480 },
            { date: '2025-01-15', value: 7650 }
          ]
        },
        platforms: [
          { name: 'Vistar Media', impressions: 3250000, spend: 45230, share: 26.1 },
          { name: 'Hivestack', impressions: 2890000, spend: 38940, share: 23.2 },
          { name: 'The Trade Desk', impressions: 2650000, spend: 41250, share: 21.3 },
          { name: 'Broadsign', impressions: 2100000, spend: 22180, share: 16.9 },
          { name: 'VIOOH', impressions: 1560000, spend: 9180, share: 12.5 }
        ],
        locations: [
          { city: 'New York', state: 'NY', impressions: 2450000, footfall: 45600, spend: 32100 },
          { city: 'Los Angeles', state: 'CA', impressions: 2120000, footfall: 38900, spend: 28740 },
          { city: 'Chicago', state: 'IL', impressions: 1890000, footfall: 32100, spend: 25200 },
          { city: 'Miami', state: 'FL', impressions: 1650000, footfall: 28700, spend: 22150 },
          { city: 'Atlanta', state: 'GA', impressions: 1480000, footfall: 24200, spend: 19800 }
        ],
        triggers: [
          { type: 'Weather', activations: 342, performance: '+23%' },
          { type: 'Time-based', activations: 287, performance: '+15%' },
          { type: 'Sports Events', activations: 156, performance: '+31%' },
          { type: 'Location', activations: 123, performance: '+18%' },
          { type: 'Custom', activations: 89, performance: '+12%' }
        ],
        attribution: {
          totalConversions: 8945,
          attributionRate: 74.2,
          conversionTypes: {
            websiteVisits: 3420,
            appDownloads: 2180,
            storeVisits: 1890,
            streamingPlays: 1455
          }
        }
      });
    }
    setLoading(false);
  };

  const loadCampaigns = async () => {
    try {
      const response = await API.get('doohapi', '/campaigns', {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });
      setCampaigns(response.campaigns || []);
    } catch (error) {
      console.error('Error loading campaigns:', error);
    }
  };

  const loadRealTimeData = async () => {
    try {
      const response = await API.get('doohapi', '/analytics/realtime', {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });
      setRealTimeData(response.data || {});
    } catch (error) {
      // Mock real-time data
      setRealTimeData({
        liveImpressions: Math.floor(Math.random() * 1000) + 2000,
        activeScreens: 1847,
        ongoingCampaigns: 8,
        triggerActivations: Math.floor(Math.random() * 10) + 5
      });
    }
  };

  const exportData = async (format) => {
    try {
      const response = await API.get('doohapi', `/analytics/export/${format}`, {
        queryStringParameters: {
          timeRange: selectedTimeRange,
          campaign: selectedCampaign
        },
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });
      
      // Handle download
      const blob = new Blob([response.data], { 
        type: format === 'csv' ? 'text/csv' : 'application/json' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_${selectedTimeRange}_${Date.now()}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const renderKPICard = (title, value, change, icon: Icon, color) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
      {change && (
        <div className="mt-4 flex items-center">
          {change.startsWith('+') ? (
            <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
          )}
          <span className={`text-sm font-medium ${
            change.startsWith('+') ? 'text-green-600' : 'text-red-600'
          }`}>
            {change} from last period
          </span>
        </div>
      )}
    </div>
  );

  const renderChart = () => {
    const selectedMetricData = dashboardData.trends?.[selectedMetric] || [];
    
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            {metrics.find(m => m.id === selectedMetric)?.name} Trend
          </h3>
          <div className="flex space-x-2">
            {metrics.map(metric => {
              const MetricIcon = metric.icon;
              return (
                <button
                  key={metric.id}
                  onClick={() => setSelectedMetric(metric.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium ${
                    selectedMetric === metric.id
                      ? `bg-${metric.color}-100 text-${metric.color}-800`
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <MetricIcon className="w-4 h-4" />
                  <span>{metric.name}</span>
                </button>
              );
            })}
          </div>
        </div>
        
        {/* Simple chart representation */}
        <div className="h-64 flex items-end space-x-2">
          {selectedMetricData.map((dataPoint, index) => {
            const maxValue = Math.max(...selectedMetricData.map(d => d.value));
            const height = (dataPoint.value / maxValue) * 100;
            return (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="bg-blue-500 rounded-t w-full transition-all hover:bg-blue-600"
                  style={{ height: `${height}%` }}
                  title={`${new Date(dataPoint.date).toLocaleDateString()}: ${formatNumber(dataPoint.value)}`}
                ></div>
                <span className="text-xs text-gray-500 mt-2">
                  {new Date(dataPoint.date).toLocaleDateString(undefined, { weekday: 'short' })}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (loading && !dashboardData.overview) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor your DOOH campaign performance and ROI</p>
        </div>
        
        <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-4 mt-4 md:mt-0">
          {/* Time Range Selector */}
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeRanges.map(range => (
              <option key={range.id} value={range.id}>{range.name}</option>
            ))}
          </select>

          {/* Campaign Filter */}
          <select
            value={selectedCampaign}
            onChange={(e) => setSelectedCampaign(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Campaigns</option>
            {campaigns.map(campaign => (
              <option key={campaign.id} value={campaign.id}>{campaign.name}</option>
            ))}
          </select>

          {/* Export Options */}
          <div className="flex space-x-2">
            <button
              onClick={() => exportData('csv')}
              className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Download className="w-4 h-4" />
              <span>CSV</span>
            </button>
            <button
              onClick={() => exportData('json')}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Download className="w-4 h-4" />
              <span>JSON</span>
            </button>
          </div>
        </div>
      </div>

      {/* Real-time Stats */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Live Performance</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{formatNumber(realTimeData.liveImpressions || 0)}</p>
            <p className="text-blue-100">Live Impressions</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{realTimeData.activeScreens || 0}</p>
            <p className="text-blue-100">Active Screens</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{realTimeData.ongoingCampaigns || 0}</p>
            <p className="text-blue-100">Live Campaigns</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-white">{realTimeData.triggerActivations || 0}</p>
            <p className="text-blue-100">Recent Triggers</p>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {renderKPICard(
          'Total Impressions',
          formatNumber(dashboardData.overview?.totalImpressions || 0),
          '+12.5%',
          Eye,
          'blue'
        )}
        {renderKPICard(
          'Total Clicks',
          formatNumber(dashboardData.overview?.totalClicks || 0),
          '+8.2%',
          MousePointer,
          'green'
        )}
        {renderKPICard(
          'Total Reach',
          formatNumber(dashboardData.overview?.totalReach || 0),
          '+15.3%',
          Users,
          'purple'
        )}
        {renderKPICard(
          'Total Spend',
          formatCurrency(dashboardData.overview?.totalSpend || 0),
          '+6.7%',
          DollarSign,
          'red'
        )}
      </div>

      {/* Chart */}
      <div className="mb-8">
        {renderChart()}
      </div>

      {/* Platform Performance & Location Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Platform Performance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Platform Performance</h3>
          <div className="space-y-4">
            {dashboardData.platforms?.map((platform, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                    <Globe className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{platform.name}</p>
                    <p className="text-sm text-gray-600">{formatNumber(platform.impressions)} impressions</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">{formatCurrency(platform.spend)}</p>
                  <p className="text-sm text-gray-600">{platform.share}% share</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Locations */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Top Performing Locations</h3>
          <div className="space-y-4">
            {dashboardData.locations?.map((location, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                    <MapPin className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{location.city}, {location.state}</p>
                    <p className="text-sm text-gray-600">{formatNumber(location.impressions)} impressions</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">{formatNumber(location.footfall)} footfall</p>
                  <p className="text-sm text-gray-600">{formatCurrency(location.spend)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trigger Performance & Attribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Trigger Performance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Trigger Performance</h3>
          <div className="space-y-4">
            {dashboardData.triggers?.map((trigger, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-yellow-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{trigger.type} Triggers</p>
                    <p className="text-sm text-gray-600">{trigger.activations} activations</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    trigger.performance.startsWith('+') 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {trigger.performance}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Attribution Analysis */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Attribution Analysis</h3>
          <div className="space-y-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">Attribution Rate</span>
                <span className="text-lg font-bold text-blue-900">
                  {dashboardData.attribution?.attributionRate}%
                </span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${dashboardData.attribution?.attributionRate}%` }}
                ></div>
              </div>
            </div>
            
            <div className="space-y-3">
              {Object.entries(dashboardData.attribution?.conversionTypes || {}).map(([type, count]) => (
                <div key={type} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 capitalize">
                    {type.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                  <span className="font-medium text-gray-900">{formatNumber(count)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;