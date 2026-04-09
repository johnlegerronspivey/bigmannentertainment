import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const ComplianceCenter = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [complianceStatus, setComplianceStatus] = useState({});
  const [complianceAlerts, setComplianceAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    setLoading(true);
    try {
      const [statusRes, alertsRes] = await Promise.all([
        axios.get(`${API}/api/platform/compliance/status?user_id=user_123`),
        axios.get(`${API}/api/platform/compliance/alerts?user_id=user_123`)
      ]);

      if (statusRes.data.success) setComplianceStatus(statusRes.data.overall_compliance || {});
      if (alertsRes.data.success) setComplianceAlerts(alertsRes.data.alerts || []);
    } catch (error) {
      handleApiError(error, 'fetchComplianceData');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '🛡️' },
    { id: 'alerts', name: 'Alerts', icon: '⚠️' },
    { id: 'rights', name: 'Rights Management', icon: '📜' },
    { id: 'reports', name: 'Reports', icon: '📊' }
  ];

  return (
    <div data-testid="compliance-center" className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Compliance Center</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Regulatory compliance and rights management</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
          <span>🔍</span>
          <span>Run Compliance Check</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Compliance Score</p>
              <p data-testid="compliance-score" className="text-2xl font-bold text-gray-900 dark:text-white">{complianceStatus.score || '0'}%</p>
            </div>
            <span className="text-2xl">🛡️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Compliant Assets</p>
              <p className="text-2xl font-bold text-green-600">{complianceStatus.compliant_assets || '0'}</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Needs Attention</p>
              <p className="text-2xl font-bold text-yellow-600">{complianceStatus.needs_attention || '0'}</p>
            </div>
            <span className="text-2xl">⚠️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Non-Compliant</p>
              <p className="text-2xl font-bold text-red-600">{complianceStatus.non_compliant || '0'}</p>
            </div>
            <span className="text-2xl">❌</span>
          </div>
        </div>
      </div>

      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id ? 'border-blue-500 text-blue-600 dark:text-blue-400' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}>
              <span>{tab.icon}</span><span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="space-y-4">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance by Type</h3>
              <div className="space-y-4">
                {[
                  { type: 'Copyright', score: 95.2, status: 'compliant' },
                  { type: 'GDPR', score: 78.9, status: 'needs_attention' },
                  { type: 'Territorial Rights', score: 92.1, status: 'compliant' },
                  { type: 'Age Rating', score: 88.7, status: 'compliant' }
                ].map((item, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{item.type}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{item.score}%</span>
                      <span className={`w-3 h-3 rounded-full ${item.status === 'compliant' ? 'bg-green-500' : item.status === 'needs_attention' ? 'bg-yellow-500' : 'bg-red-500'}`}></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance by Territory</h3>
              <div className="space-y-4">
                {[
                  { territory: 'United States', score: 92.3, assets: 567 },
                  { territory: 'European Union', score: 76.8, assets: 234 },
                  { territory: 'United Kingdom', score: 89.4, assets: 189 },
                  { territory: 'Canada', score: 94.1, assets: 156 },
                  { territory: 'Australia', score: 91.7, assets: 102 }
                ].map((item, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <div>
                      <p className="text-gray-900 dark:text-white font-medium">{item.territory}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{item.assets} assets</p>
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">{item.score}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {complianceAlerts.length > 0 ? complianceAlerts.map((alert, index) => (
              <div key={alert.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{alert.title}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(alert.risk_level)}`}>{alert.risk_level}</span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">{alert.message}</p>
                    {alert.territory && (<p className="text-sm text-gray-500 dark:text-gray-500 mt-1">Territory: {alert.territory}</p>)}
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Review</button>
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">Resolve</button>
                  </div>
                </div>
                {alert.deadline && (
                  <div className="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-600">
                    <span className="text-sm text-gray-600 dark:text-gray-400">Deadline: {new Date(alert.deadline).toLocaleDateString()}</span>
                    <span className={`text-sm font-medium ${new Date(alert.deadline) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) ? 'text-red-600' : 'text-gray-600 dark:text-gray-400'}`}>
                      {Math.ceil((new Date(alert.deadline) - new Date()) / (1000 * 60 * 60 * 24))} days remaining
                    </span>
                  </div>
                )}
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">✅</div>
                <p className="text-gray-600 dark:text-gray-400">No compliance alerts. Great job!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'rights' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Rights Information</h3>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Add Rights Info</button>
              </div>
              <div className="space-y-4">
                {[
                  { asset: 'Summer Vibes Instrumental', owner: 'Big Mann Entertainment', year: 2024, territories: ['US', 'CA', 'UK', 'EU', 'AU'], restrictions: ['No sync without license', 'Attribution required'] },
                  { asset: 'Midnight Dreams', owner: 'Big Mann Entertainment', year: 2024, territories: ['US', 'CA', 'UK'], restrictions: ['Commercial use only'] }
                ].map((rights, index) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">{rights.asset}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">© {rights.year} {rights.owner}</p>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">✏️</button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Territories</p>
                        <div className="flex flex-wrap gap-1">
                          {rights.territories.map((territory) => (
                            <span key={territory} className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 text-xs rounded">{territory}</span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Restrictions</p>
                        <div className="space-y-1">
                          {rights.restrictions.map((restriction, idx) => (
                            <p key={idx} className="text-xs text-gray-600 dark:text-gray-400">• {restriction}</p>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Generate Compliance Report</h3>
                <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">Generate Report</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date Range</label>
                  <div className="space-y-2">
                    <input type="date" className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} />
                    <input type="date" className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Compliance Types</label>
                  <div className="space-y-2">
                    {['Copyright', 'GDPR', 'Territorial Rights', 'Age Rating'].map((type) => (
                      <label key={type} className="flex items-center space-x-2">
                        <input type="checkbox" className="rounded" defaultChecked />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Reports</h3>
              <div className="space-y-4">
                {[
                  { name: 'Q4 Compliance Report', date: '2024-01-15', status: 'completed', type: 'PDF' },
                  { name: 'GDPR Audit Report', date: '2024-01-10', status: 'completed', type: 'PDF' },
                  { name: 'Rights Review Report', date: '2024-01-05', status: 'processing', type: 'PDF' }
                ].map((report, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{report.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{report.date} • {report.type}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${report.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'}`}>{report.status}</span>
                      {report.status === 'completed' && (<button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Download</button>)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { ComplianceCenter };
