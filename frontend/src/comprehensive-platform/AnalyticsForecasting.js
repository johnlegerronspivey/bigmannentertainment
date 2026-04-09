import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const AnalyticsForecasting = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [roiAnalysis, setRoiAnalysis] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('performance');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const [performanceRes, roiRes] = await Promise.all([
        axios.get(`${API}/api/platform/analytics/performance?user_id=user_123`),
        axios.get(`${API}/api/platform/analytics/roi?user_id=user_123`)
      ]);

      if (performanceRes.data.success) setPerformanceMetrics(performanceRes.data.performance_metrics || {});
      if (roiRes.data.success) setRoiAnalysis(roiRes.data.roi_analysis || {});
    } catch (error) {
      handleApiError(error, 'fetchAnalyticsData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'performance', name: 'Performance', icon: '📊' },
    { id: 'forecasting', name: 'Forecasting', icon: '🔮' },
    { id: 'roi', name: 'ROI Analysis', icon: '💹' },
    { id: 'trends', name: 'Trends', icon: '📈' }
  ];

  return (
    <div data-testid="analytics-forecasting" className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics & Forecasting</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Advanced analytics and revenue forecasting</p>
        </div>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2">
          <span>📊</span>
          <span>Generate Report</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Streams</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{performanceMetrics.total_streams?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">🎵</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Engagement Rate</p>
              <p className="text-2xl font-bold text-blue-600">{performanceMetrics.engagement_rate ?? 0}%</p>
            </div>
            <span className="text-2xl">👍</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Views</p>
              <p className="text-2xl font-bold text-green-600">{performanceMetrics.total_views?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">👁️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Downloads</p>
              <p className="text-2xl font-bold text-purple-600">{performanceMetrics.total_downloads?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">⬇️</span>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="space-y-4">
        {activeTab === 'performance' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Assets</h3>
              <div className="space-y-4">
                {performanceMetrics.top_performing_assets?.slice(0, 5).map((asset, index) => (
                  <div key={asset.id || index} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{asset.title}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{asset.events?.toLocaleString() || asset.streams?.toLocaleString() || 0} events</p>
                    </div>
                    <p className="font-semibold text-green-600">${(asset.revenue || 0).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Performance</h3>
              <div className="space-y-4">
                {performanceMetrics.top_platforms?.slice(0, 5).map((platform, index) => (
                  <div key={platform.name || index} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{platform.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{platform.events?.toLocaleString() || platform.streams?.toLocaleString() || 0} events</p>
                    </div>
                    <p className="font-semibold text-blue-600">{platform.engagement_rate || 0}% engagement</p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6 lg:col-span-2`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Audience Demographics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Age Groups</h4>
                  <div className="space-y-2">
                    {performanceMetrics.audience_demographics?.age_groups && Object.entries(performanceMetrics.audience_demographics.age_groups).map(([age, percentage]) => (
                      <div key={age} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{age}</span>
                        <span className="font-medium text-gray-900 dark:text-white">{percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Gender</h4>
                  <div className="space-y-2">
                    {performanceMetrics.audience_demographics?.gender && Object.entries(performanceMetrics.audience_demographics.gender).map(([gender, percentage]) => (
                      <div key={gender} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400 capitalize">{gender}</span>
                        <span className="font-medium text-gray-900 dark:text-white">{percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Top Countries</h4>
                  <div className="space-y-2">
                    {performanceMetrics.audience_demographics?.top_countries?.slice(0, 5).map((country, index) => (
                      <div key={country.country || index} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{country.country}</span>
                        <span className="font-medium text-gray-900 dark:text-white">{country.percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'forecasting' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Revenue Forecast</h3>
                <div className="flex space-x-2">
                  <select className={`px-3 py-2 border rounded-lg text-sm ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                    <option>Next 12 Months</option>
                    <option>Next 6 Months</option>
                    <option>Next Quarter</option>
                  </select>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 text-sm">Generate Forecast</button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">$425K</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Predicted Revenue (12M)</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">+28%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Expected Growth</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">92%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Confidence Level</p>
                </div>
              </div>

              <div className="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <div className="text-4xl mb-4">📈</div>
                <p className="text-gray-600 dark:text-gray-400">Forecast chart would appear here</p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">Interactive revenue projection visualization</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Growth Opportunities</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <p className="font-medium text-green-900 dark:text-green-100">TikTok Expansion</p>
                    <p className="text-sm text-green-700 dark:text-green-300">+45% potential revenue increase</p>
                  </div>
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <p className="font-medium text-blue-900 dark:text-blue-100">International Markets</p>
                    <p className="text-sm text-blue-700 dark:text-blue-300">+32% potential from EU/Asia</p>
                  </div>
                  <div className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                    <p className="font-medium text-purple-900 dark:text-purple-100">Podcast Platforms</p>
                    <p className="text-sm text-purple-700 dark:text-purple-300">+28% untapped revenue</p>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Risk Factors</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <p className="font-medium text-yellow-900 dark:text-yellow-100">Platform Algorithm Changes</p>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">Medium risk to organic reach</p>
                  </div>
                  <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="font-medium text-red-900 dark:text-red-100">Market Saturation</p>
                    <p className="text-sm text-red-700 dark:text-red-300">High competition in key genres</p>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <p className="font-medium text-gray-900 dark:text-gray-100">Economic Factors</p>
                    <p className="text-sm text-gray-700 dark:text-gray-300">Low risk to entertainment spending</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'roi' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Overall ROI</h3>
              <div className="text-center py-6">
                <p className="text-4xl font-bold text-green-600 mb-2">{roiAnalysis.roi_percentage ?? 0}%</p>
                <p className="text-gray-600 dark:text-gray-400">Return on Investment</p>
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Total Investment</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${roiAnalysis.total_investment?.toLocaleString() || '0'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Total Revenue</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${roiAnalysis.total_revenue?.toLocaleString() || '0'}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">ROI by Platform</h3>
              <div className="space-y-3">
                {roiAnalysis.by_platform && Object.entries(roiAnalysis.by_platform).map(([platform, data]) => (
                  <div key={platform} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{platform}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Investment: ${data.investment?.toLocaleString() || 0}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-green-600">{data.roi?.toFixed(1) || 0}%</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">${data.revenue?.toLocaleString() || 0}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6 lg:col-span-2`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">ROI Trends (Monthly)</h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                {roiAnalysis.monthly_trend?.map((month, index) => (
                  <div key={month.month || index} className="text-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400">{month.month}</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">{month.roi}%</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-green-800 to-green-600' : 'bg-gradient-to-r from-green-500 to-green-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Revenue Trend</h4>
                <p className="text-2xl font-bold">📈 +18.4%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-blue-800 to-blue-600' : 'bg-gradient-to-r from-blue-500 to-blue-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Engagement Trend</h4>
                <p className="text-2xl font-bold">📊 +12.7%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-purple-800 to-purple-600' : 'bg-gradient-to-r from-purple-500 to-purple-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Audience Growth</h4>
                <p className="text-2xl font-bold">👥 +8.9%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-orange-800 to-orange-600' : 'bg-gradient-to-r from-orange-500 to-orange-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Content Performance</h4>
                <p className="text-2xl font-bold">🎯 +15.2%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Market Insights</h3>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">🎵 Audio Content Dominance</h4>
                  <p className="text-sm text-blue-700 dark:text-blue-300">Audio content shows 34% better performance on weekends and during evening hours (6-10 PM).</p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">📈 Q4 Revenue Spike</h4>
                  <p className="text-sm text-green-700 dark:text-green-300">Historical data shows Q4 typically brings 28% increase in streaming revenue due to holiday listening patterns.</p>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                  <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-2">🌟 Social Media Engagement</h4>
                  <p className="text-sm text-purple-700 dark:text-purple-300">TikTok campaigns show highest engagement rates at 9.8%, significantly outperforming other platforms.</p>
                </div>
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">🎭 Genre Performance</h4>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">Hip-hop and electronic genres show strongest revenue growth, while pop maintains highest overall volume.</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { AnalyticsForecasting };
