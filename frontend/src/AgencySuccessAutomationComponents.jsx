import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

// =========================
// Utility Functions
// =========================

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// =========================
// Stat Card Component
// =========================

const StatCard = ({ title, value, subtitle, icon, color = 'blue', trend }) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    pink: 'bg-pink-500',
    indigo: 'bg-indigo-500'
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 ${colorClasses[color]} rounded-lg flex items-center justify-center text-white text-2xl`}>
          {icon}
        </div>
        {trend && (
          <span className={`text-sm ${trend > 0 ? 'text-green-400' : trend < 0 ? 'text-red-400' : 'text-slate-400'}`}>
            {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-slate-400 text-sm">{title}</div>
      {subtitle && <div className="text-slate-500 text-xs mt-1">{subtitle}</div>}
    </div>
  );
};

// =========================
// Onboarding Tab
// =========================

const OnboardingTab = ({ agencyId }) => {
  const [workflows, setWorkflows] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTalent, setNewTalent] = useState({ talent_name: '', talent_email: '' });

  const fetchData = useCallback(async () => {
    try {
      const [workflowsRes, statsRes] = await Promise.all([
        fetch(`${API}/api/agency-automation/onboarding?agency_id=${agencyId}`),
        fetch(`${API}/api/agency-automation/onboarding/stats?agency_id=${agencyId}`)
      ]);
      
      const workflowsData = await workflowsRes.json();
      const statsData = await statsRes.json();
      
      setWorkflows(Array.isArray(workflowsData) ? workflowsData : []);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching onboarding data:', error);
      toast.error('Failed to load onboarding data');
    } finally {
      setLoading(false);
    }
  }, [agencyId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateOnboarding = async () => {
    if (!newTalent.talent_name || !newTalent.talent_email) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const response = await fetch(`${API}/api/agency-automation/onboarding`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          talent_id: `talent-${Date.now()}`,
          talent_name: newTalent.talent_name,
          talent_email: newTalent.talent_email,
          agency_id: agencyId
        })
      });

      if (response.ok) {
        toast.success('Onboarding workflow created successfully!');
        setShowCreateModal(false);
        setNewTalent({ talent_name: '', talent_email: '' });
        fetchData();
      } else {
        toast.error('Failed to create onboarding workflow');
      }
    } catch (error) {
      console.error('Error creating onboarding:', error);
      toast.error('Failed to create onboarding workflow');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'not_started': 'bg-slate-500',
      'in_progress': 'bg-blue-500',
      'pending_review': 'bg-yellow-500',
      'approved': 'bg-green-500',
      'completed': 'bg-green-600',
      'rejected': 'bg-red-500'
    };
    return colors[status] || 'bg-slate-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Workflows" 
          value={stats?.total_workflows || 0} 
          icon="📋"
          color="blue"
        />
        <StatCard 
          title="In Progress" 
          value={stats?.in_progress || 0} 
          icon="🔄"
          color="orange"
        />
        <StatCard 
          title="Pending Review" 
          value={stats?.pending_review || 0} 
          icon="⏳"
          color="yellow"
        />
        <StatCard 
          title="Completed This Month" 
          value={stats?.completed_this_month || 0} 
          subtitle={`Avg: ${stats?.average_completion_days || 0} days`}
          icon="✅"
          color="green"
        />
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-white">Onboarding Workflows</h3>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          data-testid="create-onboarding-btn"
        >
          <span>+</span> New Onboarding
        </button>
      </div>

      {/* Workflows List */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-900">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Talent</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Status</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Progress</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Due Date</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {workflows.length > 0 ? workflows.map((workflow) => (
                <tr key={workflow.id} className="hover:bg-slate-750" data-testid={`onboarding-row-${workflow.id}`}>
                  <td className="px-6 py-4">
                    <div className="text-white font-medium">{workflow.talent_name}</div>
                    <div className="text-slate-400 text-sm">{workflow.talent_email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium text-white ${getStatusColor(workflow.status)}`}>
                      {workflow.status?.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-purple-500 rounded-full transition-all"
                          style={{ width: `${workflow.progress_percentage || 0}%` }}
                        />
                      </div>
                      <span className="text-slate-300 text-sm">{Math.round(workflow.progress_percentage || 0)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">{formatDate(workflow.due_date)}</td>
                  <td className="px-6 py-4">
                    <button className="text-purple-400 hover:text-purple-300 text-sm">
                      View Details
                    </button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-slate-400">
                    No onboarding workflows found. Create one to get started!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-700">
            <h3 className="text-xl font-semibold text-white mb-4">Start New Onboarding</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Talent Name *</label>
                <input
                  type="text"
                  value={newTalent.talent_name}
                  onChange={(e) => setNewTalent({ ...newTalent, talent_name: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Enter talent name"
                  data-testid="talent-name-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email Address *</label>
                <input
                  type="email"
                  value={newTalent.talent_email}
                  onChange={(e) => setNewTalent({ ...newTalent, talent_email: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Enter email address"
                  data-testid="talent-email-input"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateOnboarding}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                data-testid="submit-onboarding-btn"
              >
                Create Workflow
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// =========================
// KPI Dashboard Tab
// =========================

const KPIDashboardTab = ({ agencyId }) => {
  const [kpis, setKpis] = useState(null);
  const [period, setPeriod] = useState('month');
  const [loading, setLoading] = useState(true);

  const fetchKPIs = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/agency-automation/kpis?agency_id=${agencyId}&period=${period}`);
      const data = await response.json();
      setKpis(data);
    } catch (error) {
      console.error('Error fetching KPIs:', error);
      toast.error('Failed to load KPI data');
    } finally {
      setLoading(false);
    }
  }, [agencyId, period]);

  useEffect(() => {
    fetchKPIs();
  }, [fetchKPIs]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-white">Agency KPIs</h3>
        <div className="flex gap-2">
          {['month', 'quarter', 'year'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                period === p
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
              data-testid={`period-${p}-btn`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Revenue KPIs */}
      <div>
        <h4 className="text-lg font-medium text-white mb-4">💰 Revenue Performance</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Revenue"
            value={formatCurrency(kpis?.total_revenue || 0)}
            subtitle={`Target: ${formatCurrency(kpis?.revenue_target || 0)}`}
            icon="$"
            color="green"
          />
          <StatCard
            title="Revenue Achievement"
            value={`${Math.round(kpis?.revenue_achievement || 0)}%`}
            icon="📊"
            color="blue"
          />
          <StatCard
            title="Gross Margin"
            value={`${Math.round(kpis?.gross_margin || 0)}%`}
            icon="📈"
            color="purple"
          />
          <StatCard
            title="Avg Booking Value"
            value={formatCurrency(kpis?.average_booking_value || 0)}
            icon="💎"
            color="indigo"
          />
        </div>
      </div>

      {/* Booking KPIs */}
      <div>
        <h4 className="text-lg font-medium text-white mb-4">📅 Booking Metrics</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Bookings"
            value={kpis?.total_bookings || 0}
            subtitle={`Target: ${kpis?.booking_target || 0}`}
            icon="📋"
            color="blue"
          />
          <StatCard
            title="Conversion Rate"
            value={`${Math.round(kpis?.booking_conversion_rate || 0)}%`}
            icon="🎯"
            color="green"
          />
          <StatCard
            title="Active Talent"
            value={kpis?.active_talent || 0}
            icon="👥"
            color="purple"
          />
          <StatCard
            title="Utilization Rate"
            value={`${Math.round(kpis?.talent_utilization_rate || 0)}%`}
            icon="⚡"
            color="orange"
          />
        </div>
      </div>

      {/* Client KPIs */}
      <div>
        <h4 className="text-lg font-medium text-white mb-4">🤝 Client Metrics</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Active Clients"
            value={kpis?.active_clients || 0}
            icon="🏢"
            color="blue"
          />
          <StatCard
            title="New Clients"
            value={kpis?.new_clients_this_period || 0}
            icon="✨"
            color="green"
          />
          <StatCard
            title="Retention Rate"
            value={`${Math.round(kpis?.client_retention_rate || 0)}%`}
            icon="🔄"
            color="purple"
          />
          <StatCard
            title="Avg Client Spend"
            value={formatCurrency(kpis?.average_client_spend || 0)}
            icon="💳"
            color="indigo"
          />
        </div>
      </div>

      {/* Top Performers */}
      {kpis?.top_talents?.length > 0 && (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-medium text-white mb-4">🏆 Top Performers</h4>
          <div className="space-y-3">
            {kpis.top_talents.map((talent, index) => (
              <div key={talent.talent_id} className="flex items-center justify-between p-3 bg-slate-750 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-slate-400' : 'bg-amber-700'
                  } text-white`}>
                    {index + 1}
                  </div>
                  <div>
                    <div className="text-white font-medium">{talent.name}</div>
                    <div className="text-slate-400 text-sm">{talent.bookings} bookings</div>
                  </div>
                </div>
                <div className="text-green-400 font-semibold">{formatCurrency(talent.revenue)}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// =========================
// Contract Management Tab
// =========================

const ContractTab = ({ agencyId }) => {
  const [contracts, setContracts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newContract, setNewContract] = useState({
    title: '',
    contract_type: 'non_exclusive',
    party_name: '',
    party_email: ''
  });

  const fetchData = useCallback(async () => {
    try {
      const [contractsRes, statsRes] = await Promise.all([
        fetch(`${API}/api/agency-automation/contracts?agency_id=${agencyId}`),
        fetch(`${API}/api/agency-automation/contracts/stats?agency_id=${agencyId}`)
      ]);
      
      const contractsData = await contractsRes.json();
      const statsData = await statsRes.json();
      
      setContracts(Array.isArray(contractsData) ? contractsData : []);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching contracts:', error);
      toast.error('Failed to load contract data');
    } finally {
      setLoading(false);
    }
  }, [agencyId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateContract = async () => {
    if (!newContract.title || !newContract.party_name) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const response = await fetch(`${API}/api/agency-automation/contracts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contract_type: newContract.contract_type,
          title: newContract.title,
          agency_id: agencyId,
          created_by: 'current-user',
          parties: [{
            party_id: `party-${Date.now()}`,
            party_type: 'talent',
            name: newContract.party_name,
            email: newContract.party_email,
            role: 'signer'
          }],
          terms: {
            compensation: { amount: 0, type: 'negotiable' }
          }
        })
      });

      if (response.ok) {
        toast.success('Contract created successfully!');
        setShowCreateModal(false);
        setNewContract({ title: '', contract_type: 'non_exclusive', party_name: '', party_email: '' });
        fetchData();
      } else {
        toast.error('Failed to create contract');
      }
    } catch (error) {
      console.error('Error creating contract:', error);
      toast.error('Failed to create contract');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-slate-500',
      'pending_review': 'bg-yellow-500',
      'pending_signature': 'bg-blue-500',
      'active': 'bg-green-500',
      'expired': 'bg-red-500',
      'terminated': 'bg-red-600',
      'completed': 'bg-green-600'
    };
    return colors[status] || 'bg-slate-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Contracts" 
          value={stats?.total_contracts || 0} 
          icon="📄"
          color="blue"
        />
        <StatCard 
          title="Active Contracts" 
          value={stats?.active_contracts || 0} 
          icon="✅"
          color="green"
        />
        <StatCard 
          title="Pending Signature" 
          value={stats?.pending_signature || 0} 
          icon="✍️"
          color="orange"
        />
        <StatCard 
          title="Contract Value" 
          value={formatCurrency(stats?.total_contract_value || 0)} 
          subtitle={`${stats?.expiring_soon || 0} expiring soon`}
          icon="💰"
          color="purple"
        />
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-white">Contracts</h3>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          data-testid="create-contract-btn"
        >
          <span>+</span> New Contract
        </button>
      </div>

      {/* Contracts List */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-900">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Contract</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Type</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Status</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Value</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">End Date</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {contracts.length > 0 ? contracts.map((contract) => (
                <tr key={contract.id} className="hover:bg-slate-750" data-testid={`contract-row-${contract.id}`}>
                  <td className="px-6 py-4">
                    <div className="text-white font-medium">{contract.title}</div>
                    <div className="text-slate-400 text-sm">{contract.contract_number}</div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">
                    {contract.contract_type?.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium text-white ${getStatusColor(contract.status)}`}>
                      {contract.status?.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-green-400">{formatCurrency(contract.total_value || 0)}</td>
                  <td className="px-6 py-4 text-slate-300">{formatDate(contract.end_date)}</td>
                  <td className="px-6 py-4">
                    <button className="text-purple-400 hover:text-purple-300 text-sm">
                      View
                    </button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-400">
                    No contracts found. Create one to get started!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-700">
            <h3 className="text-xl font-semibold text-white mb-4">Create New Contract</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Contract Title *</label>
                <input
                  type="text"
                  value={newContract.title}
                  onChange={(e) => setNewContract({ ...newContract, title: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Enter contract title"
                  data-testid="contract-title-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Contract Type</label>
                <select
                  value={newContract.contract_type}
                  onChange={(e) => setNewContract({ ...newContract, contract_type: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  data-testid="contract-type-select"
                >
                  <option value="exclusive_representation">Exclusive Representation</option>
                  <option value="non_exclusive">Non-Exclusive</option>
                  <option value="booking_agreement">Booking Agreement</option>
                  <option value="release_form">Release Form</option>
                  <option value="nda">NDA</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Party Name *</label>
                <input
                  type="text"
                  value={newContract.party_name}
                  onChange={(e) => setNewContract({ ...newContract, party_name: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Enter party name"
                  data-testid="party-name-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Party Email</label>
                <input
                  type="email"
                  value={newContract.party_email}
                  onChange={(e) => setNewContract({ ...newContract, party_email: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Enter party email"
                  data-testid="party-email-input"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateContract}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                data-testid="submit-contract-btn"
              >
                Create Contract
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// =========================
// Booking Tab
// =========================

const BookingTab = ({ agencyId }) => {
  const [bookings, setBookings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newBooking, setNewBooking] = useState({
    title: '',
    booking_type: 'photoshoot',
    talent_name: '',
    client_name: '',
    rate: 500,
    start_date: '',
    start_time: '09:00',
    end_time: '17:00'
  });

  const fetchData = useCallback(async () => {
    try {
      const [bookingsRes, statsRes] = await Promise.all([
        fetch(`${API}/api/agency-automation/bookings?agency_id=${agencyId}`),
        fetch(`${API}/api/agency-automation/bookings/stats?agency_id=${agencyId}`)
      ]);
      
      const bookingsData = await bookingsRes.json();
      const statsData = await statsRes.json();
      
      setBookings(Array.isArray(bookingsData) ? bookingsData : []);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching bookings:', error);
      toast.error('Failed to load booking data');
    } finally {
      setLoading(false);
    }
  }, [agencyId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreateBooking = async () => {
    if (!newBooking.title || !newBooking.talent_name || !newBooking.client_name || !newBooking.start_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    const startDateTime = new Date(`${newBooking.start_date}T${newBooking.start_time}`);
    const endDateTime = new Date(`${newBooking.start_date}T${newBooking.end_time}`);

    try {
      const response = await fetch(`${API}/api/agency-automation/bookings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          booking_type: newBooking.booking_type,
          agency_id: agencyId,
          talent_id: `talent-${Date.now()}`,
          talent_name: newBooking.talent_name,
          client_id: `client-${Date.now()}`,
          client_name: newBooking.client_name,
          title: newBooking.title,
          start_datetime: startDateTime.toISOString(),
          end_datetime: endDateTime.toISOString(),
          rate: parseFloat(newBooking.rate),
          rate_type: 'daily'
        })
      });

      if (response.ok) {
        toast.success('Booking created successfully!');
        setShowCreateModal(false);
        setNewBooking({
          title: '',
          booking_type: 'photoshoot',
          talent_name: '',
          client_name: '',
          rate: 500,
          start_date: '',
          start_time: '09:00',
          end_time: '17:00'
        });
        fetchData();
      } else {
        toast.error('Failed to create booking');
      }
    } catch (error) {
      console.error('Error creating booking:', error);
      toast.error('Failed to create booking');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'inquiry': 'bg-slate-500',
      'pending_confirmation': 'bg-yellow-500',
      'confirmed': 'bg-blue-500',
      'in_progress': 'bg-purple-500',
      'completed': 'bg-green-500',
      'cancelled': 'bg-red-500',
      'no_show': 'bg-red-600'
    };
    return colors[status] || 'bg-slate-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Bookings" 
          value={stats?.total_bookings || 0} 
          icon="📅"
          color="blue"
        />
        <StatCard 
          title="Confirmed" 
          value={stats?.confirmed_bookings || 0} 
          icon="✅"
          color="green"
        />
        <StatCard 
          title="Pending" 
          value={stats?.pending_bookings || 0} 
          icon="⏳"
          color="orange"
        />
        <StatCard 
          title="Revenue This Month" 
          value={formatCurrency(stats?.total_revenue_this_month || 0)} 
          subtitle={`Avg: ${formatCurrency(stats?.average_booking_value || 0)}`}
          icon="💰"
          color="purple"
        />
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-white">Bookings</h3>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
          data-testid="create-booking-btn"
        >
          <span>+</span> New Booking
        </button>
      </div>

      {/* Bookings List */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-900">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Booking</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Talent</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Client</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Status</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Date</th>
                <th className="px-6 py-4 text-left text-sm font-medium text-slate-300">Fee</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {bookings.length > 0 ? bookings.map((booking) => (
                <tr key={booking.id} className="hover:bg-slate-750" data-testid={`booking-row-${booking.id}`}>
                  <td className="px-6 py-4">
                    <div className="text-white font-medium">{booking.title}</div>
                    <div className="text-slate-400 text-sm">{booking.booking_type?.replace('_', ' ')}</div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">{booking.talent_name}</td>
                  <td className="px-6 py-4 text-slate-300">{booking.client_name}</td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium text-white ${getStatusColor(booking.status)}`}>
                      {booking.status?.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-300">{formatDateTime(booking.start_datetime)}</td>
                  <td className="px-6 py-4 text-green-400">{formatCurrency(booking.total_fee || 0)}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="6" className="px-6 py-8 text-center text-slate-400">
                    No bookings found. Create one to get started!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 w-full max-w-lg border border-slate-700">
            <h3 className="text-xl font-semibold text-white mb-4">Create New Booking</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-slate-300 mb-2">Booking Title *</label>
                <input
                  type="text"
                  value={newBooking.title}
                  onChange={(e) => setNewBooking({ ...newBooking, title: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="e.g., Vogue Cover Shoot"
                  data-testid="booking-title-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Booking Type</label>
                <select
                  value={newBooking.booking_type}
                  onChange={(e) => setNewBooking({ ...newBooking, booking_type: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  data-testid="booking-type-select"
                >
                  <option value="photoshoot">Photoshoot</option>
                  <option value="runway">Runway</option>
                  <option value="commercial">Commercial</option>
                  <option value="editorial">Editorial</option>
                  <option value="fitting">Fitting</option>
                  <option value="casting">Casting</option>
                  <option value="event">Event</option>
                  <option value="video">Video</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Rate ($)</label>
                <input
                  type="number"
                  value={newBooking.rate}
                  onChange={(e) => setNewBooking({ ...newBooking, rate: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  data-testid="booking-rate-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Talent Name *</label>
                <input
                  type="text"
                  value={newBooking.talent_name}
                  onChange={(e) => setNewBooking({ ...newBooking, talent_name: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Enter talent name"
                  data-testid="booking-talent-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Client Name *</label>
                <input
                  type="text"
                  value={newBooking.client_name}
                  onChange={(e) => setNewBooking({ ...newBooking, client_name: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  placeholder="Enter client name"
                  data-testid="booking-client-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Date *</label>
                <input
                  type="date"
                  value={newBooking.start_date}
                  onChange={(e) => setNewBooking({ ...newBooking, start_date: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  data-testid="booking-date-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Start Time</label>
                <input
                  type="time"
                  value={newBooking.start_time}
                  onChange={(e) => setNewBooking({ ...newBooking, start_time: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">End Time</label>
                <input
                  type="time"
                  value={newBooking.end_time}
                  onChange={(e) => setNewBooking({ ...newBooking, end_time: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateBooking}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                data-testid="submit-booking-btn"
              >
                Create Booking
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// =========================
// Revenue Forecast Tab
// =========================

const RevenueForecastTab = ({ agencyId }) => {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('monthly');

  const fetchForecast = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/agency-automation/forecast?agency_id=${agencyId}&forecast_period=${period}`);
      const data = await response.json();
      setForecast(data);
    } catch (error) {
      console.error('Error fetching forecast:', error);
      toast.error('Failed to load forecast data');
    } finally {
      setLoading(false);
    }
  }, [agencyId, period]);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-white">Revenue Forecast</h3>
        <div className="flex gap-2">
          {['monthly', 'quarterly', 'yearly'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                period === p
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
              data-testid={`forecast-period-${p}-btn`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Forecast Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-xl p-6">
          <div className="text-green-100 text-sm mb-2">Predicted Revenue</div>
          <div className="text-4xl font-bold text-white mb-2">
            {formatCurrency(forecast?.predicted_revenue || 0)}
          </div>
          <div className="text-green-200 text-sm">
            Confidence: {Math.round((forecast?.confidence_level || 0) * 100)}%
          </div>
        </div>
        
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Lower Bound</div>
          <div className="text-3xl font-bold text-red-400 mb-2">
            {formatCurrency(forecast?.lower_bound || 0)}
          </div>
          <div className="text-slate-500 text-sm">Conservative estimate</div>
        </div>
        
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Upper Bound</div>
          <div className="text-3xl font-bold text-green-400 mb-2">
            {formatCurrency(forecast?.upper_bound || 0)}
          </div>
          <div className="text-slate-500 text-sm">Optimistic estimate</div>
        </div>
      </div>

      {/* Breakdown by Type */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-medium text-white mb-4">📊 Revenue by Booking Type</h4>
          <div className="space-y-3">
            {Object.entries(forecast?.by_booking_type || {}).map(([type, value]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                  <span className="text-slate-300 capitalize">{type.replace('_', ' ')}</span>
                </div>
                <span className="text-white font-medium">{formatCurrency(value)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-medium text-white mb-4">🎯 Forecast Factors</h4>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Seasonal Factor</span>
              <span className={`font-medium ${forecast?.seasonal_factor >= 1 ? 'text-green-400' : 'text-red-400'}`}>
                {(forecast?.seasonal_factor || 1).toFixed(2)}x
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Growth Factor</span>
              <span className={`font-medium ${forecast?.growth_factor >= 1 ? 'text-green-400' : 'text-red-400'}`}>
                {(forecast?.growth_factor || 1).toFixed(2)}x
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Model Type</span>
              <span className="text-purple-400 capitalize">{forecast?.model_type || 'Statistical'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Model Accuracy</span>
              <span className="text-white">{Math.round(forecast?.model_accuracy || 0)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Assumptions & Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-medium text-white mb-4">📋 Assumptions</h4>
          <ul className="space-y-2">
            {(forecast?.assumptions || []).map((assumption, index) => (
              <li key={index} className="text-slate-300 text-sm flex items-start gap-2">
                <span className="text-blue-400 mt-1">•</span>
                {assumption}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-medium text-white mb-4">⚠️ Risks</h4>
          <ul className="space-y-2">
            {(forecast?.risks || []).map((risk, index) => (
              <li key={index} className="text-slate-300 text-sm flex items-start gap-2">
                <span className="text-red-400 mt-1">•</span>
                {risk}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h4 className="text-lg font-medium text-white mb-4">🚀 Opportunities</h4>
          <ul className="space-y-2">
            {(forecast?.opportunities || []).map((opportunity, index) => (
              <li key={index} className="text-slate-300 text-sm flex items-start gap-2">
                <span className="text-green-400 mt-1">•</span>
                {opportunity}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

// =========================
// Main Dashboard Component
// =========================

const AgencySuccessAutomationDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Using a default agency ID for demo purposes
  const agencyId = 'agency-default';

  const fetchDashboard = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/agency-automation/dashboard?agency_id=${agencyId}`);
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, [agencyId]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'onboarding', label: 'Onboarding', icon: '👤' },
    { id: 'kpis', label: 'KPIs', icon: '📈' },
    { id: 'contracts', label: 'Contracts', icon: '📄' },
    { id: 'bookings', label: 'Bookings', icon: '📅' },
    { id: 'forecast', label: 'Forecast', icon: '🔮' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900" data-testid="agency-automation-dashboard">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-2">🚀 Agency Success Automation</h1>
          <p className="text-purple-200">
            Automated workflows, KPI tracking, contract management, and revenue forecasting
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-slate-900 border-b border-slate-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 text-sm font-medium whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'text-purple-400 border-b-2 border-purple-400'
                    : 'text-slate-400 hover:text-slate-300'
                }`}
                data-testid={`tab-${tab.id}`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
              </div>
            ) : (
              <>
                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <StatCard
                    title="Active Onboardings"
                    value={dashboard?.onboarding_stats?.in_progress || 0}
                    subtitle={`${dashboard?.onboarding_stats?.overdue_count || 0} overdue`}
                    icon="👤"
                    color="blue"
                  />
                  <StatCard
                    title="Active Contracts"
                    value={dashboard?.contract_stats?.active_contracts || 0}
                    subtitle={`${dashboard?.contract_stats?.expiring_soon || 0} expiring soon`}
                    icon="📄"
                    color="green"
                  />
                  <StatCard
                    title="Confirmed Bookings"
                    value={dashboard?.booking_stats?.confirmed_bookings || 0}
                    subtitle={`${dashboard?.booking_stats?.pending_bookings || 0} pending`}
                    icon="📅"
                    color="purple"
                  />
                  <StatCard
                    title="Monthly Revenue"
                    value={formatCurrency(dashboard?.booking_stats?.total_revenue_this_month || 0)}
                    icon="💰"
                    color="orange"
                  />
                </div>

                {/* Revenue Forecast Preview */}
                {dashboard?.revenue_forecast && (
                  <div className="bg-gradient-to-r from-green-600/20 to-emerald-600/20 rounded-xl p-6 border border-green-500/30">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-1">Revenue Forecast</h3>
                        <p className="text-slate-400 text-sm">Next period prediction</p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-green-400">
                          {formatCurrency(dashboard.revenue_forecast.predicted_revenue)}
                        </div>
                        <div className="text-sm text-slate-400">
                          Confidence: {Math.round(dashboard.revenue_forecast.confidence_level * 100)}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Recent Alerts */}
                {dashboard?.recent_alerts?.length > 0 && (
                  <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">🔔 Recent Alerts</h3>
                    <div className="space-y-3">
                      {dashboard.recent_alerts.slice(0, 5).map((alert) => (
                        <div key={alert.id} className="flex items-start gap-4 p-3 bg-slate-750 rounded-lg">
                          <div className={`w-2 h-2 rounded-full mt-2 ${
                            alert.severity === 'critical' ? 'bg-red-500' :
                            alert.severity === 'high' ? 'bg-orange-500' :
                            alert.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                          }`}></div>
                          <div className="flex-1">
                            <div className="text-white font-medium">{alert.title}</div>
                            <div className="text-slate-400 text-sm">{alert.message}</div>
                          </div>
                          <div className="text-slate-500 text-xs">
                            {formatDateTime(alert.created_at)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Upcoming Deadlines */}
                {dashboard?.upcoming_deadlines?.length > 0 && (
                  <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4">📆 Upcoming Deadlines</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {dashboard.upcoming_deadlines.slice(0, 6).map((deadline, index) => (
                        <div key={index} className="flex items-center gap-4 p-3 bg-slate-750 rounded-lg">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            deadline.type === 'booking' ? 'bg-blue-500/20 text-blue-400' :
                            deadline.type === 'contract_expiry' ? 'bg-orange-500/20 text-orange-400' :
                            'bg-purple-500/20 text-purple-400'
                          }`}>
                            {deadline.type === 'booking' ? '📅' : '📄'}
                          </div>
                          <div className="flex-1">
                            <div className="text-white font-medium text-sm">{deadline.title}</div>
                            <div className="text-slate-400 text-xs">{formatDateTime(deadline.date)}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'onboarding' && <OnboardingTab agencyId={agencyId} />}
        {activeTab === 'kpis' && <KPIDashboardTab agencyId={agencyId} />}
        {activeTab === 'contracts' && <ContractTab agencyId={agencyId} />}
        {activeTab === 'bookings' && <BookingTab agencyId={agencyId} />}
        {activeTab === 'forecast' && <RevenueForecastTab agencyId={agencyId} />}
      </div>
    </div>
  );
};

export default AgencySuccessAutomationDashboard;
