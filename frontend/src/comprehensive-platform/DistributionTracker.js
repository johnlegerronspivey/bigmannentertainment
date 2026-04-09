import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const DistributionTracker = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [distributionJobs, setDistributionJobs] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('jobs');

  useEffect(() => {
    fetchDistributionData();
  }, []);

  const fetchDistributionData = async () => {
    setLoading(true);
    try {
      const [jobsRes, platformsRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/api/platform/distribution/jobs?user_id=user_123`),
        axios.get(`${API}/api/platform/distribution/platforms`),
        axios.get(`${API}/api/platform/distribution/analytics?user_id=user_123`)
      ]);

      if (jobsRes.data.success) setDistributionJobs(jobsRes.data.jobs || []);
      if (platformsRes.data.success) setPlatforms(platformsRes.data.platforms || []);
      if (analyticsRes.data.success) setAnalytics(analyticsRes.data.analytics || {});
    } catch (error) {
      handleApiError(error, 'fetchDistributionData');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'processing': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'jobs', name: 'Distribution Jobs', icon: '📤' },
    { id: 'platforms', name: 'Platforms', icon: '🌐' },
    { id: 'gs1', name: 'GS1 Digital Links', icon: '🔗' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
    { id: 'create', name: 'Create Job', icon: '➕' }
  ];

  return (
    <div data-testid="distribution-tracker" className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Distribution Tracker</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Monitor content distribution across all platforms</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
          <span>🚀</span>
          <span>Quick Distribute</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Jobs</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.total_jobs || '0'}</p>
            </div>
            <span className="text-2xl">📤</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Jobs</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.active_jobs || '0'}</p>
            </div>
            <span className="text-2xl">🔄</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">{analytics.success_rate || '0'}%</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Avg. Delivery Time</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.average_delivery_time || '0'}h</p>
            </div>
            <span className="text-2xl">⏱️</span>
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
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
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
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Status</option>
                <option>Active</option>
                <option>Completed</option>
                <option>Failed</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Platforms</option>
                <option>Spotify</option>
                <option>Apple Music</option>
                <option>YouTube</option>
              </select>
            </div>

            <div className="space-y-4">
              {distributionJobs.length > 0 ? distributionJobs.map((job, index) => (
                <div key={job.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{job.asset_title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Distributing to {job.platforms?.length || job.total_platforms || 0} platforms
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Progress</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div className="bg-blue-600 h-2 rounded-full" style={{width: `${job.progress || 0}%`}}></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{job.progress || 0}%</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Successful</p>
                      <p className="text-lg font-semibold text-green-600">{job.successful_deliveries || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
                      <p className="text-lg font-semibold text-red-600">{job.failed_deliveries || 0}</p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Started: {job.submitted_at ? new Date(job.submitted_at).toLocaleDateString() : 'N/A'}
                    </div>
                    <div className="flex space-x-2">
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View Details</button>
                      {job.status === 'failed' && (
                        <button className="text-green-600 hover:text-green-700 text-sm font-medium">Retry</button>
                      )}
                    </div>
                  </div>
                </div>
              )) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📤</div>
                  <p className="text-gray-600 dark:text-gray-400">No distribution jobs found. Create your first distribution job!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'platforms' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.length > 0 ? platforms.map((platform, index) => (
              <div key={platform.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-gray-900 dark:text-white">{platform.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    platform.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                    'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                  }`}>
                    {platform.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{platform.category}</p>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  <p>Max file size: {platform.max_file_size ? `${Math.round(platform.max_file_size / 1024 / 1024)}MB` : 'N/A'}</p>
                  <p>Delivery time: {platform.delivery_time_estimate || 'N/A'}</p>
                </div>
              </div>
            )) : (
              <div className="col-span-full text-center py-8">
                <div className="text-4xl mb-4">🌐</div>
                <p className="text-gray-600 dark:text-gray-400">Loading platforms...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'gs1' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <span className="mr-2">🔗</span>
                GS1 Digital Links for Distribution
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Generate GS1 Digital Links and QR codes for your assets to enable direct-to-consumer engagement and licensing integration.
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className={`${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'} border rounded-lg p-4`}>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Digital Link Benefits</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-center"><span className="mr-2">✅</span>Direct consumer engagement</li>
                    <li className="flex items-center"><span className="mr-2">✅</span>Royalty tracking integration</li>
                    <li className="flex items-center"><span className="mr-2">✅</span>Global interoperability</li>
                    <li className="flex items-center"><span className="mr-2">✅</span>Compliance with GS1 standards</li>
                  </ul>
                </div>
                
                <div className={`${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'} border rounded-lg p-4`}>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Distribution Integration</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-center"><span className="mr-2">🎵</span>Music metadata with ISRC</li>
                    <li className="flex items-center"><span className="mr-2">🎬</span>Video content with ISAN</li>
                    <li className="flex items-center"><span className="mr-2">🖼️</span>Image assets with licensing</li>
                    <li className="flex items-center"><span className="mr-2">👕</span>Merchandise tracking</li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 text-center">
                <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
                  🚀 Access Full GS1 Registry
                </button>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Available in Content Manager → GS1 Registry tab
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Performance</h3>
              <div className="space-y-3">
                {analytics.platform_performance && Object.entries(analytics.platform_performance).map(([platform, data]) => (
                  <div key={platform} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{platform}</span>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{data.success_rate}%</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{data.avg_delivery_time}h avg</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Daily Distribution</h3>
              <div className="space-y-3">
                {analytics.daily_stats && Object.entries(analytics.daily_stats).map(([day, count]) => (
                  <div key={day} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{day}</span>
                    <span className="font-medium text-gray-900 dark:text-white">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Create Distribution Job</h3>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Content</label>
                <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                  <option>Choose content to distribute...</option>
                  <option>Summer Vibes Instrumental</option>
                  <option>Brand Logo Animation</option>
                  <option>Artist Portrait</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Platforms</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {['Music Data Exchange (MDE)', 'Mechanical Licensing Collective (MLC)', 'Spotify', 'Apple Music', 'YouTube', 'Instagram', 'TikTok', 'Facebook', 'Amazon Music', 'Tidal', 'Pandora'].map((platform) => (
                    <label key={platform} className="flex items-center space-x-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{platform}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Priority</label>
                <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                  <option>Normal</option>
                  <option>High</option>
                  <option>Urgent</option>
                </select>
              </div>

              <div className="flex space-x-4">
                <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
                  Create Distribution Job
                </button>
                <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
                  Save as Draft
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { DistributionTracker };
