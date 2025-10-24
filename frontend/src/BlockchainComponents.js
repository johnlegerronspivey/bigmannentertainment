import React, { useState, useEffect } from 'react';

// Get API URL from environment
const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// ===== BLOCKCHAIN INTEGRATION DASHBOARD =====

export const BlockchainIntegrationDashboard = () => {
  const [integrationStatus, setIntegrationStatus] = useState(null);
  const [activeStep, setActiveStep] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [executingStep, setExecutingStep] = useState(null);

  useEffect(() => {
    fetchIntegrationStatus();
  }, []);

  const fetchIntegrationStatus = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/blockchain/status`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setIntegrationStatus(data.blockchain_integration_status);
        setError('');
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
        localStorage.removeItem('token');
      } else if (response.status === 404) {
        setError('Backend API not accessible. Please ensure the preview servers are active or test locally at http://localhost:3000');
      } else if (response.status === 403) {
        setError('Admin access required. Please log in with admin credentials.');
      } else {
        setError(`Failed to load blockchain integration status (Status: ${response.status})`);
      }
    } catch (error) {
      console.error('Blockchain status fetch error:', error);
      setError('Error connecting to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const executeStep = async (stepNumber) => {
    try {
      setExecutingStep(stepNumber);
      setError('');
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/blockchain/integrate/step-${stepNumber}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`Step ${stepNumber} completed:`, data);
        await fetchIntegrationStatus(); // Refresh status
      } else {
        const errorData = await response.json();
        setError(`Step ${stepNumber} failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error(`Step ${stepNumber} execution error:`, error);
      setError(`Step ${stepNumber} execution failed: ${error.message}`);
    } finally {
      setExecutingStep(null);
    }
  };

  const executeCompleteIntegration = async () => {
    try {
      setExecutingStep('complete');
      setError('');
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/blockchain/integrate/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Complete integration:', data);
        await fetchIntegrationStatus(); // Refresh status
      } else {
        const errorData = await response.json();
        setError(`Complete integration failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Complete integration error:', error);
      setError(`Complete integration failed: ${error.message}`);
    } finally {
      setExecutingStep(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg shadow-md">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-lg font-medium text-red-800 mb-2">
                    Failed to Load Blockchain Integration Status
                  </h3>
                  <p className="text-red-700 mb-4">{error}</p>
                  
                  {error.includes('404') || error.includes('not accessible') ? (
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-4">
                      <p className="text-sm text-yellow-800 font-semibold mb-2">⚠️ Backend API Not Accessible</p>
                      <p className="text-sm text-yellow-700 mb-3">
                        The preview environment's routing is not initialized. This is a platform infrastructure issue.
                      </p>
                      <div className="space-y-2 text-sm text-yellow-800">
                        <p>✅ <strong>Option 1:</strong> Click "Wake up servers" button (if visible)</p>
                        <p>✅ <strong>Option 2:</strong> Test locally: <code className="bg-yellow-100 px-2 py-1 rounded">http://localhost:3000</code></p>
                        <p>✅ <strong>Option 3:</strong> Deploy your app for stable access</p>
                      </div>
                    </div>
                  ) : null}
                  
                  <div className="flex gap-3">
                    <button
                      onClick={fetchIntegrationStatus}
                      className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      🔄 Retry
                    </button>
                    <button
                      onClick={() => window.location.href = '/'}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      ← Back to Home
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Additional Help Section */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-800 mb-2">💡 Need Help?</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Check your internet connection</li>
                <li>• Ensure you're logged in with admin credentials</li>
                <li>• Try refreshing the page</li>
                <li>• Contact support if the issue persists</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">⛓️ Blockchain Integration</h1>
          <p className="text-xl text-gray-600">
            Complete ULN blockchain integration with smart contracts and DAO governance
          </p>
        </div>

        {/* Integration Status Overview */}
        {integrationStatus && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">🎯 Integration Status</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {integrationStatus.total_labels_registered}
                </div>
                <div className="text-gray-600">Labels Registered</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {integrationStatus.smart_contracts_deployed}
                </div>
                <div className="text-gray-600">Smart Contracts</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {integrationStatus.dao_governance_active ? 'Active' : 'Inactive'}
                </div>
                <div className="text-gray-600">DAO Governance</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600">
                  {integrationStatus.blockchain_network}
                </div>
                <div className="text-gray-600">Network</div>
              </div>
            </div>

            {/* Overall Status */}
            <div className="flex items-center justify-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-green-600 mr-2">✅</div>
              <div className="text-green-800 font-medium">
                Status: {integrationStatus.overall_status.replace('_', ' ').toUpperCase()}
              </div>
            </div>
          </div>
        )}

        {/* Integration Steps */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Step 1: Label Discovery & Registration */}
          <IntegrationStepCard
            stepNumber={1}
            title="Label Discovery & Registration"
            description="Scan database for all existing label entities and register them on blockchain"
            status={integrationStatus?.step_1_discovery || "pending"}
            onExecute={() => executeStep(1)}
            executing={executingStep === 1}
            features={[
              "Global Label ID assignment",
              "Metadata validation",
              "Blockchain address generation"
            ]}
          />

          {/* Step 2: Smart Contract Binding */}
          <IntegrationStepCard
            stepNumber={2}
            title="Smart Contract Binding"
            description="Generate rights split contracts and governance rules for each label"
            status={integrationStatus?.step_2_contracts || "pending"}
            onExecute={() => executeStep(2)}
            executing={executingStep === 2}
            features={[
              "Rights split contracts",
              "DAO governance contracts",
              "Royalty distribution contracts"
            ]}
          />

          {/* Step 3: Metadata & Content Sync */}
          <IntegrationStepCard
            stepNumber={3}
            title="Metadata & Content Sync"
            description="Sync all releases and content with federated metadata across labels"
            status={integrationStatus?.step_3_sync || "pending"}
            onExecute={() => executeStep(3)}
            executing={executingStep === 3}
            features={[
              "Cross-label metadata sync",
              "Role-based access controls",
              "Content federation"
            ]}
          />

          {/* Step 4: Royalty Engine Integration */}
          <IntegrationStepCard
            stepNumber={4}
            title="Royalty Engine Integration"
            description="Modify royalty engine for multi-label splits and blockchain payouts"
            status={integrationStatus?.step_4_royalty || "pending"}
            onExecute={() => executeStep(4)}
            executing={executingStep === 4}
            features={[
              "Multi-label royalty splits",
              "Blockchain-based payouts",
              "Dispute mechanisms"
            ]}
          />

          {/* Step 5: Governance & Compliance Hooks */}
          <IntegrationStepCard
            stepNumber={5}
            title="Governance & Compliance Hooks"
            description="Connect DAO voting portals and jurisdiction compliance engines"
            status={integrationStatus?.step_5_governance || "pending"}
            onExecute={() => executeStep(5)}
            executing={executingStep === 5}
            features={[
              "DAO voting portals",
              "Jurisdiction engines",
              "Audit trail federation"
            ]}
          />

          {/* Step 6: Dashboard Activation */}
          <IntegrationStepCard
            stepNumber={6}
            title="Dashboard Activation"
            description="Enable Connected Labels view across Creator, Admin, and Investor dashboards"
            status={integrationStatus?.step_6_dashboards || "pending"}
            onExecute={() => executeStep(6)}
            executing={executingStep === 6}
            features={[
              "Creator Portal integration",
              "Admin Panel configuration",
              "Investor Dashboard activation"
            ]}
          />
        </div>

        {/* Complete Integration Button */}
        <div className="bg-white rounded-lg shadow-lg p-6 text-center">
          <h3 className="text-xl font-bold mb-4">🚀 Complete Integration</h3>
          <p className="text-gray-600 mb-6">
            Execute all 6 steps of the blockchain integration plan in sequence
          </p>
          
          <button
            onClick={executeCompleteIntegration}
            disabled={executingStep === 'complete'}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-8 py-3 rounded-lg font-medium transition-colors"
          >
            {executingStep === 'complete' ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Executing Complete Integration...
              </div>
            ) : (
              'Execute Complete Blockchain Integration'
            )}
          </button>
        </div>

        {/* Available Features */}
        {integrationStatus?.available_features && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4">🌐 Available Blockchain Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {integrationStatus.available_features.map((feature, index) => (
                <div key={index} className="flex items-center p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-green-600 mr-2">✅</div>
                  <div className="text-green-800 text-sm">{feature}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ===== INTEGRATION STEP CARD COMPONENT =====

const IntegrationStepCard = ({ 
  stepNumber, 
  title, 
  description, 
  status, 
  onExecute, 
  executing, 
  features 
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'pending': return '⏳';
      case 'failed': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">
            Step {stepNumber}: {title}
          </h3>
          <p className="text-gray-600 mt-1">{description}</p>
        </div>
        
        <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getStatusColor(status)}`}>
          {getStatusIcon(status)} {status}
        </div>
      </div>

      {/* Features */}
      <div className="mb-4">
        <h4 className="font-medium text-gray-700 mb-2">Key Features:</h4>
        <ul className="space-y-1">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center text-sm text-gray-600">
              <div className="w-2 h-2 bg-purple-400 rounded-full mr-2"></div>
              {feature}
            </li>
          ))}
        </ul>
      </div>

      {/* Execute Button */}
      <button
        onClick={onExecute}
        disabled={executing || status === 'completed'}
        className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors"
      >
        {executing ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Executing Step {stepNumber}...
          </div>
        ) : status === 'completed' ? (
          `✅ Step ${stepNumber} Completed`
        ) : (
          `Execute Step ${stepNumber}`
        )}
      </button>
    </div>
  );
};

// ===== BLOCKCHAIN CONTRACTS VIEWER =====

export const BlockchainContractsViewer = () => {
  const [selectedLabel, setSelectedLabel] = useState('');
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchContracts = async (labelId) => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/blockchain/contracts/${labelId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setContracts(data.contracts?.smart_contracts || []);
      } else {
        setError('Failed to load contracts');
      }
    } catch (error) {
      console.error('Contracts fetch error:', error);
      setError('Error loading contracts');
    } finally {
      setLoading(false);
    }
  };

  const handleLabelSelect = (labelId) => {
    setSelectedLabel(labelId);
    if (labelId) {
      fetchContracts(labelId);
    } else {
      setContracts([]);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">📋 Smart Contracts Viewer</h2>
      
      {/* Label Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Label to View Contracts:
        </label>
        <select
          value={selectedLabel}
          onChange={(e) => handleLabelSelect(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">Choose a label...</option>
          <option value="BM-LBL-ATLANTIC">Atlantic Records</option>
          <option value="BM-LBL-COLUMBIA">Columbia Records</option>
          <option value="BM-LBL-DEFIJAM">Def Jam Recordings</option>
          <option value="BM-LBL-SUBPOP">Sub Pop Records</option>
          <option value="BM-LBL-MATADOR">Matador Records</option>
        </select>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
      )}

      {/* Contracts Display */}
      {contracts.length > 0 && (
        <div className="space-y-4">
          {contracts.map((contract, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-bold text-lg capitalize">
                    {contract.contract_type.replace('_', ' ')} Contract
                  </h3>
                  <p className="text-gray-600">
                    Address: <code className="bg-gray-100 px-2 py-1 rounded">{contract.contract_address}</code>
                  </p>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                  {contract.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Deployed:</div>
                  <div className="font-medium">{new Date(contract.deployed_at).toLocaleDateString()}</div>
                </div>
                
                <div>
                  <div className="text-sm text-gray-600">Network:</div>
                  <div className="font-medium">{contract.blockchain_network || 'goerli'}</div>
                </div>
              </div>

              {/* Contract-specific details */}
              {contract.governance_rules && (
                <div className="mt-3 p-3 bg-gray-50 rounded">
                  <div className="text-sm font-medium text-gray-700 mb-2">Governance Rules:</div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>Voting Threshold: {(contract.governance_rules.voting_threshold * 100)}%</div>
                    <div>Quorum Requirement: {(contract.governance_rules.quorum_requirement * 100)}%</div>
                    <div>Voting Period: {contract.governance_rules.voting_period_days} days</div>
                  </div>
                </div>
              )}

              {contract.dao_voting_weight && (
                <div className="mt-3 p-3 bg-blue-50 rounded">
                  <div className="text-sm font-medium text-blue-700">
                    DAO Voting Weight: {contract.dao_voting_weight}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedLabel && contracts.length === 0 && !loading && !error && (
        <div className="text-center py-8 text-gray-500">
          No contracts found for selected label
        </div>
      )}
    </div>
  );
};

// ===== BLOCKCHAIN AUDIT TRAIL =====

export const BlockchainAuditTrail = () => {
  const [auditEntries, setAuditEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAuditTrail();
  }, []);

  const fetchAuditTrail = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/blockchain/audit-trail`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAuditEntries(data.audit_trail || []);
      } else {
        setError('Failed to load audit trail');
      }
    } catch (error) {
      console.error('Audit trail fetch error:', error);
      setError('Error loading audit trail');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">🔍 Blockchain Audit Trail</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {auditEntries.map((entry, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-bold">{entry.action_type.replace('_', ' ').toUpperCase()}</h3>
                <p className="text-sm text-gray-600">
                  by {entry.actor_id} ({entry.actor_type})
                </p>
              </div>
              <div className="text-xs text-gray-500">
                {new Date(entry.timestamp).toLocaleString()}
              </div>
            </div>

            <div className="text-sm text-gray-700 mb-2">
              Network: <span className="font-medium">{entry.blockchain_network}</span>
            </div>

            <div className="text-xs text-gray-500 mb-2">
              Hash: <code className="bg-gray-100 px-1 rounded">{entry.audit_hash}</code>
            </div>

            {entry.details && (
              <div className="mt-3 p-3 bg-gray-50 rounded">
                <div className="text-xs font-medium text-gray-700 mb-1">Details:</div>
                <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                  {JSON.stringify(entry.details, null, 2)}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>

      {auditEntries.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          No audit trail entries found
        </div>
      )}
    </div>
  );
};

export default BlockchainIntegrationDashboard;