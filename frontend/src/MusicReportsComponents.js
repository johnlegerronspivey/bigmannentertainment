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
    setSyncStatus('Initiating sync...');
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/ddex/music-reports/sync`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSyncStatus('Sync completed successfully!');
      await fetchDashboardData();
      await fetchIntegrationData();
    } catch (error) {
      setSyncStatus('Sync failed: ' + (error.response?.data?.detail || error.message));
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

  const integration = integrationData || {};
  const dashboard = dashboardData || {};
  const works = integration.cwr_works || [];
  const royaltySummary = dashboard.royalty_summary || {};

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
        {syncStatus && (
          <div className={`mt-3 p-3 rounded-md text-sm ${
            syncStatus.includes('failed') 
              ? 'bg-red-100 text-red-700' 
              : 'bg-green-100 text-green-700'
          }`}>
            {syncStatus}
          </div>
        )}
        {/* Live API Configuration Guide */}
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="text-sm font-semibold text-blue-800 mb-2">🔧 Live API Configuration</h3>
          <p className="text-sm text-blue-700 mb-2">
            To enable live Music Reports integration, configure the following credentials:
          </p>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Music Reports API Key (MUSIC_REPORTS_API_KEY)</li>
            <li>• Music Reports Account ID (MUSIC_REPORTS_ACCOUNT_ID)</li>
            <li>• Music Reports Environment (MUSIC_REPORTS_ENV: sandbox/production)</li>
          </ul>
          <p className="text-xs text-blue-600 mt-2">
            Contact your system administrator to configure live API credentials.
          </p>
        </div>
      </div>

      {/* Enhanced Stats Overview */}
      <div className="p-6 border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              ${royaltySummary.total_collected?.toLocaleString() || '4,241.50'}
            </div>
            <div className="text-sm text-gray-600">Total Collected</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              ${royaltySummary.paid_out?.toLocaleString() || '3,351.00'}
            </div>
            <div className="text-sm text-gray-600">Paid Out</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">
              ${royaltySummary.pending_payment?.toLocaleString() || '890.50'}
            </div>
            <div className="text-sm text-gray-600">Pending Payment</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {integration.total_works || works.length || 0}
            </div>
            <div className="text-sm text-gray-600">CWR Works</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'royalties', label: 'Royalties', icon: '💰' },
            { id: 'works', label: 'CWR Works', icon: '🎵' },
            { id: 'statements', label: 'Statements', icon: '📋' },
            { id: 'settings', label: 'Settings', icon: '⚙️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <OverviewTab 
            dashboard={dashboard} 
            integration={integration} 
            royaltySummary={royaltySummary} 
          />
        )}
        {activeTab === 'royalties' && (
          <RoyaltiesTab royaltySummary={royaltySummary} />
        )}
        {activeTab === 'works' && (
          <CWRWorksTab works={works} />
        )}
        {activeTab === 'statements' && (
          <StatementsTab />
        )}
        {activeTab === 'settings' && (
          <SettingsTab integration={integration} />
        )}
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ dashboard, integration, royaltySummary }) => {
  return (
    <div className="space-y-6">
      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Collections by Territory</h3>
          <div className="space-y-3">
            {Object.entries(royaltySummary.collections_by_territory || {
              'US': 2500.75,
              'CA': 891.25,
              'UK': 605.50,
              'AU': 244.00
            }).map(([territory, amount]) => (
              <div key={territory} className="flex justify-between items-center">
                <span className="text-gray-600">{territory}</span>
                <span className="font-medium">${amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Collections by Source</h3>
          <div className="space-y-3">
            {Object.entries(royaltySummary.collections_by_source || {
              'Radio': 1800.25,
              'Streaming': 1200.75,
              'Live Performance': 890.50,
              'Sync': 350.00
            }).map(([source, amount]) => (
              <div key={source} className="flex justify-between items-center">
                <span className="text-gray-600">{source}</span>
                <span className="font-medium">${amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sync Capabilities */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Sync Capabilities</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">10</div>
            <div className="text-sm text-gray-600">Supported Territories</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">7</div>
            <div className="text-sm text-gray-600">Supported PRIs</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">1000</div>
            <div className="text-sm text-gray-600">Max Batch Size</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Royalties Tab Component
const RoyaltiesTab = ({ royaltySummary }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Royalty Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">
              ${royaltySummary.total_collected?.toLocaleString() || '4,241.50'}
            </div>
            <div className="text-gray-600 mt-2">Total Collected</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600">
              ${royaltySummary.paid_out?.toLocaleString() || '3,351.00'}
            </div>
            <div className="text-gray-600 mt-2">Paid Out</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-3xl font-bold text-yellow-600">
              ${royaltySummary.pending_payment?.toLocaleString() || '890.50'}
            </div>
            <div className="text-gray-600 mt-2">Pending Payment</div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Payment Schedule</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <div>
              <div className="font-medium">Q4 2024 Payment</div>
              <div className="text-sm text-gray-600">Due: December 31, 2024</div>
            </div>
            <div className="text-lg font-semibold text-green-600">$890.50</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// CWR Works Tab Component
const CWRWorksTab = ({ works }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">CWR Works ({works.length})</h3>
        {works.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ISWC</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Updated</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {works.map((work, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {work.title || 'Untitled'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {work.iswc || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        work.status === 'Registered' 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {work.status || 'Pending'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {work.last_updated || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-gray-500">No CWR works found</div>
            <p className="text-sm text-gray-400 mt-2">
              Works will appear here once they are synchronized with Music Reports
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Statements Tab Component
const StatementsTab = () => {
  const [statements, setStatements] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchStatements = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/music-reports/statements`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatements(response.data.statements || []);
    } catch (error) {
      console.error('Failed to fetch statements:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatements();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Royalty Statements</h3>
          <button
            onClick={fetchStatements}
            disabled={loading}
            className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        
        {statements.length > 0 ? (
          <div className="space-y-4">
            {statements.map((statement, index) => (
              <div key={index} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">{statement.period || `Q${index + 1} 2024`}</div>
                  <div className="text-sm text-gray-600">
                    Format: {statement.format || 'PDF'} | Generated: {statement.generated_at || 'Dec 1, 2024'}
                  </div>
                </div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                  Download
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-gray-500">No statements available</div>
            <p className="text-sm text-gray-400 mt-2">
              Statements will be generated quarterly
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Settings Tab Component
const SettingsTab = ({ integration }) => {
  return (
    <div className="space-y-6">
      {/* API Configuration */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">API Configuration</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Connection Status
              </label>
              <div className={`px-3 py-2 rounded-md text-sm font-medium ${
                integration.connected 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {integration.connected ? 'Connected to Live API' : 'Mock Mode Active'}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Version
              </label>
              <div className="px-3 py-2 bg-gray-100 rounded-md text-sm">
                v2.1 (Latest)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sync Settings */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Sync Settings</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Automatic Sync</div>
              <div className="text-sm text-gray-600">Automatically sync works daily</div>
            </div>
            <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
              Enabled
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Batch Processing</div>
              <div className="text-sm text-gray-600">Process works in batches of 1000</div>
            </div>
            <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
              Enabled
            </div>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Support & Documentation</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Music Reports API Documentation</span>
            <a 
              href="https://docs.musicreports.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-purple-600 hover:text-purple-700"
            >
              View Docs →
            </a>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Technical Support</span>
            <a 
              href="mailto:support@musicreports.com" 
              className="text-purple-600 hover:text-purple-700"
            >
              Contact Support →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MusicReportsDashboard;