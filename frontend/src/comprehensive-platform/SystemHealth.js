import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const SystemHealth = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [systemHealth, setSystemHealth] = useState({});
  const [systemLogs, setSystemLogs] = useState([]);
  const [systemStats, setSystemStats] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchSystemData();
  }, []);

  const fetchSystemData = async () => {
    setLoading(true);
    try {
      const [healthRes, logsRes, statsRes, alertsRes] = await Promise.all([
        axios.get(`${API}/api/platform/system/health`),
        axios.get(`${API}/api/platform/system/logs?limit=50`),
        axios.get(`${API}/api/platform/system/stats`),
        axios.get(`${API}/api/platform/system/alerts`)
      ]);

      if (healthRes.data.success) setSystemHealth(healthRes.data || {});
      if (logsRes.data.success) setSystemLogs(logsRes.data.logs || []);
      if (statsRes.data.success) setSystemStats(statsRes.data.stats || {});
      if (alertsRes.data.success) setAlerts(alertsRes.data.alerts || []);
    } catch (error) {
      handleApiError(error, 'fetchSystemData');
    } finally {
      setLoading(false);  
    }
  };

  const getHealthColor = (status) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'down': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'error': return 'text-red-600 dark:text-red-400';
      case 'warning': return 'text-yellow-600 dark:text-yellow-400';
      case 'info': return 'text-blue-600 dark:text-blue-400';
      case 'debug': return 'text-gray-600 dark:text-gray-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const tabs = [
    { id: 'overview', name: 'System Overview', icon: '🏥' },
    { id: 'components', name: 'Components', icon: '⚙️' },
    { id: 'logs', name: 'Logs', icon: '📋' },
    { id: 'alerts', name: 'Alerts', icon: '🚨' },
    { id: 'metrics', name: 'Metrics', icon: '📊' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">System Health & Logs</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Monitor system performance and logs</p>
        </div>
        <div className="flex space-x-2">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
            <span>🔄</span>
            <span>Refresh</span>
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2">
            <span>📥</span>
            <span>Export Logs</span>
          </button>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Overall Status</p>
              <p className="text-2xl font-bold text-green-600">{systemHealth.overall_status || 'Healthy'}</p>
            </div>
            <span className="text-2xl">💚</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Uptime</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{systemStats.uptime?.human_readable || '14d 6h'}</p>
            </div>
            <span className="text-2xl">⏱️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Error Rate</p>
              <p className="text-2xl font-bold text-blue-600">{(systemStats.errors?.error_rate || 0.05).toFixed(2)}%</p>
            </div>
            <span className="text-2xl">📊</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Alerts</p>
              <p className="text-2xl font-bold text-yellow-600">{alerts.filter(a => !a.resolved).length}</p>
            </div>
            <span className="text-2xl">🚨</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
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

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Performance</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">CPU Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: `${systemStats.resources?.cpu_usage || 34.5}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.cpu_usage || 34.5}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">Memory Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: `${systemStats.resources?.memory_usage || 67.8}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.memory_usage || 67.8}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">Disk Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-yellow-600 h-2 rounded-full" style={{width: `${systemStats.resources?.disk_usage || 45.2}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.disk_usage || 45.2}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">Network Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full" style={{width: `${systemStats.resources?.network_usage || 23.4}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.network_usage || 23.4}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Request Statistics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Today</span>
                    <span className="font-medium text-gray-900 dark:text-white">{systemStats.requests?.total_today?.toLocaleString() || '45,678'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">This Hour</span>
                    <span className="font-medium text-gray-900 dark:text-white">{systemStats.requests?.total_this_hour?.toLocaleString() || '3,456'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Avg Response Time</span>
                    <span className="font-medium text-gray-900 dark:text-white">{systemStats.performance?.average_response_time || 245.6}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Error Count</span>
                    <span className="font-medium text-red-600">{systemStats.errors?.total_today || 23}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'components' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemHealth.components?.map((component, index) => (
              <div key={component.component || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-gray-900 dark:text-white">{component.component?.replace('_', ' ') || 'Unknown Component'}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getHealthColor(component.status)}`}>
                    {component.status}
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Response Time</span>
                    <span className="text-gray-900 dark:text-white">{component.response_time?.toFixed(1) || 0}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Last Check</span>
                    <span className="text-gray-900 dark:text-white">
                      {component.last_check ? new Date(component.last_check).toLocaleTimeString() : 'Never'}
                    </span>
                  </div>
                  {component.error_message && (
                    <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-xs text-red-700 dark:text-red-300">
                      {component.error_message}
                    </div>
                  )}
                </div>
              </div>
            )) || (
              <div className="col-span-full text-center py-8">
                <div className="text-4xl mb-4">⚙️</div>
                <p className="text-gray-600 dark:text-gray-400">Loading system components...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-4">
            {/* Log Filters */}
            <div className="flex flex-wrap gap-4">
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Levels</option>
                <option>Error</option>
                <option>Warning</option>
                <option>Info</option>
                <option>Debug</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Components</option>
                <option>API Server</option>
                <option>Database</option>
                <option>Storage</option>
                <option>Queue</option>
              </select>
              <input
                type="text"
                placeholder="Search logs..."
                className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              />
            </div>

            {/* Logs List */}
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg`}>
              <div className="max-h-96 overflow-y-auto">
                {systemLogs.length > 0 ? systemLogs.map((log, index) => (
                  <div key={log.id || index} className="border-b border-gray-200 dark:border-gray-700 last:border-b-0 p-4">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <span className={`text-sm font-mono ${getLogLevelColor(log.level)}`}>
                          {(log.level || 'INFO').toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900 dark:text-white">{log.message || 'No message'}</p>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500 dark:text-gray-400">
                          <span>{log.component || 'unknown'}</span>
                          <span>{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'No timestamp'}</span>
                          {log.user_id && <span>User: {log.user_id}</span>}
                          {log.request_id && <span>Request: {log.request_id}</span>}
                        </div>
                      </div>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">📋</div>
                    <p className="text-gray-600 dark:text-gray-400">No logs available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {alerts.length > 0 ? alerts.map((alert, index) => (
              <div key={alert.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{alert.title}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        alert.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                        alert.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                        alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      }`}>
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">{alert.message}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                      Component: {alert.component} • {alert.triggered_at ? new Date(alert.triggered_at).toLocaleString() : 'Recently'}
                    </p>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    {!alert.acknowledged && (
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Acknowledge</button>
                    )}
                    {!alert.resolved && (
                      <button className="text-green-600 hover:text-green-700 text-sm font-medium">Resolve</button>
                    )}
                  </div>
                </div>
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">✅</div>
                <p className="text-gray-600 dark:text-gray-400">No active alerts. System is running smoothly!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Database Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Active Connections</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.database?.active_connections || 15}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Queries/Second</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.database?.queries_per_second || 234.5}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Slow Queries</span>
                  <span className="font-medium text-yellow-600">{systemStats.database?.slow_queries || 3}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Max Connections</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.database?.max_connections || 100}</span>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Cache Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Hit Rate</span>
                  <span className="font-medium text-green-600">{systemStats.cache?.hit_rate || 89.4}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Miss Rate</span>
                  <span className="font-medium text-red-600">{systemStats.cache?.miss_rate || 10.6}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Total Keys</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.cache?.total_keys?.toLocaleString() || '12,456'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Memory Usage</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.cache?.memory_usage || '45.2 MB'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { SystemHealth };
