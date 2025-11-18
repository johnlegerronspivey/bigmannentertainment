import React, { useState, useEffect } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

const AWSOrganizationsComponent = () => {
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [stateChanges, setStateChanges] = useState([]);
  const [selectedState, setSelectedState] = useState('ALL');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [error, setError] = useState(null);
  const [serviceHealth, setServiceHealth] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const stateInfo = {
    'PENDING_ACTIVATION': {
      label: 'Pending Activation',
      color: 'bg-yellow-100 text-yellow-800',
      badgeColor: 'bg-yellow-500',
      icon: '⏳',
      description: 'Account created but not yet activated'
    },
    'ACTIVE': {
      label: 'Active',
      color: 'bg-green-100 text-green-800',
      badgeColor: 'bg-green-500',
      icon: '✓',
      description: 'Account operational and ready'
    },
    'SUSPENDED': {
      label: 'Suspended',
      color: 'bg-red-100 text-red-800',
      badgeColor: 'bg-red-500',
      icon: '⚠',
      description: 'Account under AWS suspension'
    },
    'PENDING_CLOSURE': {
      label: 'Pending Closure',
      color: 'bg-orange-100 text-orange-800',
      badgeColor: 'bg-orange-500',
      icon: '🔒',
      description: 'Account closure in progress'
    },
    'CLOSED': {
      label: 'Closed',
      color: 'bg-gray-100 text-gray-800',
      badgeColor: 'bg-gray-500',
      icon: '✖',
      description: 'Account in 90-day reinstatement window'
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedState, selectedSeverity]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check service health
      const healthRes = await fetch(`${BACKEND_URL}/api/aws-organizations/health`);
      const healthData = await healthRes.json();
      setServiceHealth(healthData);

      if (healthData.status !== 'healthy') {
        setError(healthData.message);
        setLoading(false);
        return;
      }

      // Load accounts
      let accountsUrl = `${BACKEND_URL}/api/aws-organizations/accounts`;
      const params = new URLSearchParams();
      if (selectedState !== 'ALL') params.append('state', selectedState);
      if (selectedSeverity !== 'ALL') params.append('severity', selectedSeverity);
      if (params.toString()) accountsUrl += `?${params.toString()}`;

      const accountsRes = await fetch(accountsUrl);
      const accountsData = await accountsRes.json();
      setAccounts(accountsData);

      // Load summary
      const summaryRes = await fetch(`${BACKEND_URL}/api/aws-organizations/summary`);
      const summaryData = await summaryRes.json();
      setSummary(summaryData);

      // Load recent state changes
      const changesRes = await fetch(`${BACKEND_URL}/api/aws-organizations/state-changes?limit=50`);
      const changesData = await changesRes.json();
      setStateChanges(changesData);

      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const monitorStateChanges = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${BACKEND_URL}/api/aws-organizations/monitor`, {
        method: 'POST'
      });
      const changes = await res.json();
      
      if (changes.length > 0) {
        alert(`Detected ${changes.length} account state change(s)!`);
        loadData();
      } else {
        alert('No state changes detected since last check.');
      }
    } catch (err) {
      alert(`Error monitoring changes: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getSeverityBadge = (state) => {
    if (state === 'SUSPENDED' || state === 'CLOSED') return 'CRITICAL';
    if (state === 'PENDING_CLOSURE') return 'WARNING';
    return 'NORMAL';
  };

  if (loading && !summary) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading AWS Organizations data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                AWS Organizations Management
              </h1>
              <p className="text-gray-600">
                Account lifecycle monitoring using new State field (Sept 2025 update)
              </p>
            </div>
            <div className="flex items-center gap-4">
              {serviceHealth && (
                <div className={`px-4 py-2 rounded-lg ${
                  serviceHealth.status === 'healthy' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  <span className="font-semibold">
                    {serviceHealth.status === 'healthy' ? '● Online' : '● Offline'}
                  </span>
                </div>
              )}
              <button
                onClick={loadData}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Refreshing...' : '🔄 Refresh'}
              </button>
            </div>
          </div>

          {/* Deprecation Notice */}
          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <h3 className="font-semibold text-yellow-800 mb-1">Migration Notice</h3>
                <p className="text-sm text-yellow-700">
                  The old <code className="bg-yellow-100 px-1 rounded">Status</code> field is deprecated. 
                  This dashboard uses the new <code className="bg-yellow-100 px-1 rounded">State</code> field 
                  (introduced Sept 2025). Full deprecation: <strong>September 9, 2026</strong>.
                </p>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <span className="text-red-600 text-xl mr-3">✖</span>
              <div>
                <h3 className="font-semibold text-red-800 mb-1">Service Error</h3>
                <p className="text-sm text-red-700">{error}</p>
                <p className="text-xs text-red-600 mt-2">
                  Please check AWS credentials and Organizations access.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Accounts</div>
              <div className="text-3xl font-bold text-gray-900">{summary.total_accounts}</div>
            </div>
            <div className="bg-green-50 rounded-lg shadow p-6">
              <div className="text-sm text-green-600 mb-1">Active</div>
              <div className="text-3xl font-bold text-green-700">{summary.active_accounts}</div>
            </div>
            <div className="bg-yellow-50 rounded-lg shadow p-6">
              <div className="text-sm text-yellow-600 mb-1">Pending Activation</div>
              <div className="text-3xl font-bold text-yellow-700">{summary.pending_activation}</div>
            </div>
            <div className="bg-orange-50 rounded-lg shadow p-6">
              <div className="text-sm text-orange-600 mb-1">Warning</div>
              <div className="text-3xl font-bold text-orange-700">{summary.warning_accounts}</div>
            </div>
            <div className="bg-red-50 rounded-lg shadow p-6">
              <div className="text-sm text-red-600 mb-1">Critical</div>
              <div className="text-3xl font-bold text-red-700">{summary.critical_accounts}</div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex gap-4">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 border-b-2 font-medium ${
                activeTab === 'overview'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('accounts')}
              className={`px-4 py-2 border-b-2 font-medium ${
                activeTab === 'accounts'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Accounts ({accounts.length})
            </button>
            <button
              onClick={() => setActiveTab('changes')}
              className={`px-4 py-2 border-b-2 font-medium ${
                activeTab === 'changes'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              State Changes ({stateChanges.length})
            </button>
            <button
              onClick={() => setActiveTab('monitor')}
              className={`px-4 py-2 border-b-2 font-medium ${
                activeTab === 'monitor'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Monitoring
            </button>
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && summary && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-6">Account State Distribution</h2>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {Object.entries(stateInfo).map(([state, info]) => (
                <div key={state} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl">{info.icon}</span>
                    <span className="text-2xl font-bold">
                      {summary.accounts_by_state[state] || 0}
                    </span>
                  </div>
                  <div className="text-sm font-semibold mb-1">{info.label}</div>
                  <div className="text-xs text-gray-600">{info.description}</div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold mb-2">Organization Info</h3>
              <div className="text-sm text-gray-600">
                <div>Organization ID: <code className="bg-gray-100 px-2 py-1 rounded">{summary.organization_id}</code></div>
                <div className="mt-1">Last Updated: {formatDate(summary.last_updated)}</div>
              </div>
            </div>
          </div>
        )}

        {/* Accounts Tab */}
        {activeTab === 'accounts' && (
          <div className="bg-white rounded-lg shadow">
            {/* Filters */}
            <div className="p-6 border-b bg-gray-50">
              <div className="flex gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filter by State
                  </label>
                  <select
                    value={selectedState}
                    onChange={(e) => setSelectedState(e.target.value)}
                    className="border border-gray-300 rounded-lg px-4 py-2"
                  >
                    <option value="ALL">All States</option>
                    {Object.entries(stateInfo).map(([state, info]) => (
                      <option key={state} value={state}>{info.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filter by Severity
                  </label>
                  <select
                    value={selectedSeverity}
                    onChange={(e) => setSelectedSeverity(e.target.value)}
                    className="border border-gray-300 rounded-lg px-4 py-2"
                  >
                    <option value="ALL">All Severities</option>
                    <option value="normal">Normal</option>
                    <option value="warning">Warning</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Accounts List */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">State</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">OU</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {accounts.map((account) => {
                    const info = stateInfo[account.state];
                    const severity = getSeverityBadge(account.state);
                    return (
                      <tr key={account.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900">{account.name}</div>
                          <div className="text-sm text-gray-600">{account.email}</div>
                          <div className="text-xs text-gray-500 font-mono">{account.id}</div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${info.color}`}>
                            {info.icon} {info.label}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex px-2 py-1 rounded text-xs font-semibold ${
                            severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                            severity === 'WARNING' ? 'bg-orange-100 text-orange-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {severity}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {account.parent_ou_name || 'N/A'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {formatDate(account.joined_timestamp)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* State Changes Tab */}
        {activeTab === 'changes' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h2 className="text-xl font-bold mb-4">Recent State Changes</h2>
              <div className="space-y-4">
                {stateChanges.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No state changes recorded yet
                  </div>
                ) : (
                  stateChanges.map((change) => (
                    <div key={change.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-semibold text-gray-900">{change.account_name}</span>
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${
                              change.severity === 'critical' ? 'bg-red-100 text-red-800' :
                              change.severity === 'warning' ? 'bg-orange-100 text-orange-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {change.severity.toUpperCase()}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 mb-1">
                            {change.account_email}
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            {change.previous_state && (
                              <span className={`px-2 py-1 rounded ${stateInfo[change.previous_state]?.color || 'bg-gray-100'}`}>
                                {stateInfo[change.previous_state]?.label || change.previous_state}
                              </span>
                            )}
                            {change.previous_state && <span>→</span>}
                            <span className={`px-2 py-1 rounded ${stateInfo[change.new_state]?.color}`}>
                              {stateInfo[change.new_state]?.label}
                            </span>
                          </div>
                        </div>
                        <div className="text-sm text-gray-500 text-right">
                          {formatDate(change.detected_at)}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Monitoring Tab */}
        {activeTab === 'monitor' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">State Monitoring</h2>
            <p className="text-gray-600 mb-6">
              Monitor account state changes in real-time. This will compare current states
              with the last recorded states and detect any changes.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Fetches current account states from AWS Organizations</li>
                <li>• Compares with last known states in database</li>
                <li>• Records any state transitions</li>
                <li>• Alerts on critical state changes (SUSPENDED, CLOSED)</li>
              </ul>
            </div>

            <button
              onClick={monitorStateChanges}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
            >
              {loading ? 'Checking for changes...' : '🔍 Check for State Changes'}
            </button>

            <div className="mt-6 pt-6 border-t">
              <h3 className="font-semibold mb-3">Monitored States (Critical/Warning)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {['SUSPENDED', 'PENDING_CLOSURE', 'CLOSED'].map((state) => {
                  const info = stateInfo[state];
                  return (
                    <div key={state} className="border rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xl">{info.icon}</span>
                        <span className="font-semibold">{info.label}</span>
                      </div>
                      <div className="text-sm text-gray-600">{info.description}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AWSOrganizationsComponent;
