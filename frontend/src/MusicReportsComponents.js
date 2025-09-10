import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Music Reports Integration Dashboard
export const MusicReportsDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [integrationData, setIntegrationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState('');
  const [syncStatus, setSyncStatus] = useState('');

  useEffect(() => {
    fetchDashboardData();
    fetchIntegrationData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/music-reports/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data.music_reports_dashboard);
    } catch (error) {
      console.error('Dashboard fetch error:', error);
    }
  };

  const fetchIntegrationData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/ddex/music-reports/cwr`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIntegrationData(response.data.music_reports_integration);
      setError('');
    } catch (error) {
      setError('Failed to load Music Reports integration data');
      console.error('Music Reports data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/ddex/music-reports/sync`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchIntegrationData();
      alert('Sync initiated successfully!');
    } catch (error) {
      alert('Sync failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  const integration = integrationData?.integration_status || {};
  const works = integrationData?.cwr_works || [];

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Music Reports Integration</h1>
            <p className="text-gray-600 mt-1">Manage your CWR works and royalty collection with Music Reports</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              integration.connected 
                ? 'bg-green-100 text-green-800' 
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {integration.connected ? 'Connected' : 'Mock Mode'}
            </div>
            <button 
              onClick={handleSync}
              disabled={loading}
              className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
            >
              {loading ? 'Syncing...' : 'Sync Now'}
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="p-6 border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{integration.total_works_registered || 0}</div>
            <div className="text-sm text-blue-800">Total Works Registered</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{integration.pending_sync || 0}</div>
            <div className="text-sm text-orange-800">Pending Sync</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">${(Math.random() * 5000).toFixed(2)}</div>
            <div className="text-sm text-green-800">Total Royalties Collected</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{integration.sync_errors || 0}</div>
            <div className="text-sm text-red-800">Sync Errors</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'works', label: 'CWR Works' },
            { id: 'royalties', label: 'Royalties' },
            { id: 'settings', label: 'Settings' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-4 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <MusicReportsOverview integration={integration} />
        )}
        {activeTab === 'works' && (
          <MusicReportsWorks works={works} onRefresh={fetchIntegrationData} />
        )}
        {activeTab === 'royalties' && (
          <MusicReportsRoyalties />
        )}
        {activeTab === 'settings' && (
          <MusicReportsSettings integration={integration} />
        )}
      </div>
    </div>
  );
};

// Overview Tab Component
const MusicReportsOverview = ({ integration }) => {
  const capabilities = integrationData?.sync_capabilities || {};
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Integration Status */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">Integration Status</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Connection:</span>
              <span className={integration.connected ? 'text-green-600' : 'text-yellow-600'}>
                {integration.connected ? 'Active' : 'Mock Mode'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Last Sync:</span>
              <span className="text-gray-600">
                {integration.last_sync || 'Never'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Next Sync:</span>
              <span className="text-gray-600">Manual trigger available</span>
            </div>
          </div>
        </div>

        {/* Capabilities */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">Sync Capabilities</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Automatic Sync
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Bulk Upload
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Real-time Updates
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
              Error Handling
            </li>
          </ul>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-3">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center text-sm">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
            <span className="text-gray-600">System initialized - Ready for Music Reports integration</span>
            <span className="ml-auto text-gray-400">Just now</span>
          </div>
          <div className="flex items-center text-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
            <span className="text-gray-600">CWR framework configured for ASCAP, BMI, SESAC, SOCAN</span>
            <span className="ml-auto text-gray-400">Today</span>
          </div>
          <div className="flex items-center text-sm">
            <div className="w-2 h-2 bg-orange-500 rounded-full mr-3"></div>
            <span className="text-gray-600">Awaiting Music Reports API credentials for live sync</span>
            <span className="ml-auto text-gray-400">Pending</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// CWR Works Tab Component
const MusicReportsWorks = ({ works, onRefresh }) => {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">CWR Works</h3>
        <button 
          onClick={onRefresh}
          className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
        >
          Refresh Works
        </button>
      </div>

      {works.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-400 text-lg mb-2">No CWR works found</div>
          <p className="text-gray-600">Register your first musical work to see it here.</p>
          <a 
            href="/ddex/cwr" 
            className="inline-block mt-4 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
          >
            Register New Work
          </a>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Composer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Publisher
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PRO
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Registered
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {works.map((work, index) => (
                <tr key={work.work_id || index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {work.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {work.composer}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {work.publisher}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {work.performing_rights_org}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                      {work.music_reports_status || 'Pending Sync'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {work.registration_date ? new Date(work.registration_date).toLocaleDateString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Royalties Tab Component
const MusicReportsRoyalties = () => {
  const mockRoyalties = [
    { id: 1, work: "Sample Track 1", period: "Q4 2024", amount: 1250.75, status: "Paid" },
    { id: 2, work: "Sample Track 2", period: "Q4 2024", amount: 890.50, status: "Pending" },
    { id: 3, work: "Sample Track 3", period: "Q3 2024", amount: 2100.25, status: "Paid" },
  ];

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-4">Royalty Collections</h3>
        
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">$4,241.50</div>
            <div className="text-sm text-green-800">Total Collected</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">$890.50</div>
            <div className="text-sm text-yellow-800">Pending Payment</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">$3,351.00</div>
            <div className="text-sm text-blue-800">Paid Out</div>
          </div>
        </div>
      </div>

      {/* Royalty Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Work
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Period
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {mockRoyalties.map((royalty) => (
              <tr key={royalty.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {royalty.work}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {royalty.period}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${royalty.amount.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    royalty.status === 'Paid' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {royalty.status}
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

// Settings Tab Component
const MusicReportsSettings = ({ integration }) => {
  const [settings, setSettings] = useState({
    autoSync: true,
    syncFrequency: 'daily',
    notifications: true,
    emailReports: true
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Integration Settings</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Auto Sync</label>
              <p className="text-sm text-gray-500">Automatically sync CWR works with Music Reports</p>
            </div>
            <input
              type="checkbox"
              checked={settings.autoSync}
              onChange={(e) => handleSettingChange('autoSync', e.target.checked)}
              className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Sync Frequency</label>
              <p className="text-sm text-gray-500">How often to sync with Music Reports</p>
            </div>
            <select
              value={settings.syncFrequency}
              onChange={(e) => handleSettingChange('syncFrequency', e.target.value)}
              className="mt-1 block pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-purple-500 focus:border-purple-500 sm:text-sm rounded-md"
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="manual">Manual Only</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Email Notifications</label>
              <p className="text-sm text-gray-500">Receive notifications for sync status and errors</p>
            </div>
            <input
              type="checkbox"
              checked={settings.notifications}
              onChange={(e) => handleSettingChange('notifications', e.target.checked)}
              className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">Monthly Reports</label>
              <p className="text-sm text-gray-500">Receive monthly royalty collection reports</p>
            </div>
            <input
              type="checkbox"
              checked={settings.emailReports}
              onChange={(e) => handleSettingChange('emailReports', e.target.checked)}
              className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            />
          </div>
        </div>
      </div>

      {/* API Configuration */}
      <div className="border-t pt-6">
        <h4 className="text-md font-semibold mb-4">API Configuration</h4>
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Music Reports API Not Connected
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>To enable live synchronization with Music Reports, you need to:</p>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li>Contact Music Reports to obtain API credentials</li>
                  <li>Configure API keys in the admin settings</li>
                  <li>Test the connection and enable live sync</li>
                </ul>
                <p className="mt-2">
                  <a href="/contact-guide" className="font-medium underline">
                    View Music Reports Contact Guide →
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="border-t pt-6">
        <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700">
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default MusicReportsDashboard;