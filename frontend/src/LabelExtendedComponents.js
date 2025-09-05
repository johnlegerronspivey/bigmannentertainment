import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Get API URL from environment
const API = process.env.REACT_APP_BACKEND_URL;

// ===== PROJECT MANAGEMENT COMPONENT =====

const ProjectManagement = () => {
  const [projects, setProjects] = useState([]);
  const [studios, setStudios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    artist_id: ''
  });

  useEffect(() => {
    fetchProjects();
    fetchStudios();
  }, [filters]);

  const fetchProjects = async () => {
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.artist_id) params.artist_id = filters.artist_id;

      const response = await axios.get(`${API}/label/projects`, { params });
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudios = async () => {
    try {
      const response = await axios.get(`${API}/label/studios/available`);
      setStudios(response.data);
    } catch (error) {
      console.error('Error fetching studios:', error);
    }
  };

  const createProject = async (projectData) => {
    try {
      await axios.post(`${API}/label/projects`, projectData);
      setShowAddModal(false);
      fetchProjects();
    } catch (error) {
      console.error('Error creating project:', error);
      alert('Error creating project');
    }
  };

  const updateProjectStatus = async (projectId, status, notes) => {
    try {
      await axios.put(`${API}/label/projects/${projectId}/status`, {
        status,
        notes
      });
      fetchProjects();
    } catch (error) {
      console.error('Error updating project status:', error);
      alert('Error updating project status');
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">🎧 Recording Projects & Studio Management</h2>
        <div className="flex space-x-4">
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            + New Project
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.status}
            onChange={(e) => setFilters({...filters, status: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Status</option>
            <option value="planning">Planning</option>
            <option value="pre_production">Pre-Production</option>
            <option value="recording">Recording</option>
            <option value="mixing">Mixing</option>
            <option value="mastering">Mastering</option>
            <option value="completed">Completed</option>
          </select>
          
          <input
            type="text"
            placeholder="Filter by artist ID..."
            value={filters.artist_id}
            onChange={(e) => setFilters({...filters, artist_id: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            onClick={() => setFilters({status: '', artist_id: ''})}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {projects.map((project) => (
          <ProjectCard 
            key={project.id} 
            project={project} 
            onStatusUpdate={updateProjectStatus}
            onSelect={() => setSelectedProject(project)}
          />
        ))}
      </div>

      {/* Studios Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">🏢 Available Studios</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {studios.map((studio) => (
            <StudioCard key={studio.id} studio={studio} />
          ))}
        </div>
      </div>

      {/* Add Project Modal */}
      {showAddModal && (
        <AddProjectModal 
          onClose={() => setShowAddModal(false)}
          onSave={createProject}
        />
      )}

      {/* Project Details Modal */}
      {selectedProject && (
        <ProjectDetailsModal 
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
          onUpdate={fetchProjects}
        />
      )}
    </div>
  );
};

const ProjectCard = ({ project, onStatusUpdate, onSelect }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'planning': return 'bg-gray-100 text-gray-800';
      case 'pre_production': return 'bg-yellow-100 text-yellow-800';
      case 'recording': return 'bg-blue-100 text-blue-800';
      case 'mixing': return 'bg-purple-100 text-purple-800';
      case 'mastering': return 'bg-indigo-100 text-indigo-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getProgressPercentage = (status) => {
    switch (status) {
      case 'planning': return 10;
      case 'pre_production': return 25;
      case 'recording': return 50;
      case 'mixing': return 75;
      case 'mastering': return 90;
      case 'completed': return 100;
      default: return 0;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" onClick={onSelect}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-bold text-lg">{project.title}</h3>
          <p className="text-gray-600 text-sm">{project.project_type}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
          {project.status.replace('_', ' ')}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span>Progress</span>
          <span>{getProgressPercentage(project.status)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getProgressPercentage(project.status)}%` }}
          ></div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Budget:</span>
          <span>${(project.budget || 0).toLocaleString()}</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Spent:</span>
          <span className="text-red-600">${(project.spent || 0).toLocaleString()}</span>
        </div>
        
        {project.expected_completion && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Due:</span>
            <span>{new Date(project.expected_completion).toLocaleDateString()}</span>
          </div>
        )}
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Tracks:</span>
          <span>{project.completed_tracks || 0} / {project.total_tracks || 0}</span>
        </div>
      </div>
    </div>
  );
};

const StudioCard = ({ studio }) => (
  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
    <h4 className="font-medium mb-2">{studio.name}</h4>
    <p className="text-sm text-gray-600 mb-2">{studio.location?.city}, {studio.location?.state}</p>
    <div className="flex justify-between items-center">
      <span className="text-sm font-medium">${studio.daily_rate}/day</span>
      {studio.rating && (
        <span className="text-sm text-yellow-600">⭐ {studio.rating}/5</span>
      )}
    </div>
  </div>
);

// ===== MARKETING MANAGEMENT COMPONENT =====

const MarketingManagement = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [pressReleases, setPressReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('campaigns');
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    if (activeTab === 'campaigns') {
      fetchCampaigns();
    } else if (activeTab === 'press') {
      fetchPressReleases();
    }
  }, [activeTab]);

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get(`${API}/label/marketing/campaigns`);
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPressReleases = async () => {
    try {
      // Mock data for press releases
      setPressReleases([]);
    } catch (error) {
      console.error('Error fetching press releases:', error);
    }
  };

  const createCampaign = async (campaignData) => {
    try {
      await axios.post(`${API}/label/marketing/campaigns`, campaignData);
      setShowAddModal(false);
      fetchCampaigns();
    } catch (error) {
      console.error('Error creating campaign:', error);
      alert('Error creating campaign');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">📢 Marketing & Promotion</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          + New Campaign
        </button>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['campaigns', 'press', 'social', 'analytics'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeTab === tab 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.replace('_', ' ')}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {loading && (
          <div className="flex justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}

        {activeTab === 'campaigns' && !loading && (
          <CampaignManagement campaigns={campaigns} onUpdate={fetchCampaigns} />
        )}

        {activeTab === 'press' && (
          <PressManagement pressReleases={pressReleases} />
        )}

        {activeTab === 'social' && (
          <SocialMediaManagement />
        )}

        {activeTab === 'analytics' && (
          <MarketingAnalytics />
        )}
      </div>

      {/* Add Campaign Modal */}
      {showAddModal && (
        <AddCampaignModal 
          onClose={() => setShowAddModal(false)}
          onSave={createCampaign}
        />
      )}
    </div>
  );
};

const CampaignManagement = ({ campaigns, onUpdate }) => (
  <div>
    <h3 className="text-lg font-bold mb-4">🎯 Active Campaigns</h3>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {campaigns.map((campaign) => (
        <CampaignCard key={campaign.id} campaign={campaign} />
      ))}
    </div>
    
    {campaigns.length === 0 && (
      <div className="text-center py-8 text-gray-500">
        No campaigns found. Create your first marketing campaign to get started.
      </div>
    )}
  </div>
);

const CampaignCard = ({ campaign }) => (
  <div className="border border-gray-200 rounded-lg p-4">
    <div className="flex justify-between items-start mb-3">
      <h4 className="font-medium">{campaign.name}</h4>
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        campaign.status === 'active' ? 'bg-green-100 text-green-800' :
        campaign.status === 'planning' ? 'bg-yellow-100 text-yellow-800' :
        'bg-gray-100 text-gray-800'
      }`}>
        {campaign.status}
      </span>
    </div>
    
    <p className="text-sm text-gray-600 mb-2">Type: {campaign.campaign_type.replace('_', ' ')}</p>
    
    <div className="space-y-1 text-sm">
      <div className="flex justify-between">
        <span>Budget:</span>
        <span>${(campaign.total_budget || 0).toLocaleString()}</span>
      </div>
      <div className="flex justify-between">
        <span>Spent:</span>
        <span className="text-red-600">${(campaign.spent || 0).toLocaleString()}</span>
      </div>
      <div className="flex justify-between">
        <span>Duration:</span>
        <span>
          {new Date(campaign.start_date).toLocaleDateString()} - 
          {new Date(campaign.end_date).toLocaleDateString()}
        </span>
      </div>
    </div>
    
    {campaign.reach && (
      <div className="mt-3 p-2 bg-gray-50 rounded">
        <div className="text-sm">
          <div className="flex justify-between">
            <span>Reach:</span>
            <span>{campaign.reach.toLocaleString()}</span>
          </div>
          {campaign.engagement_rate && (
            <div className="flex justify-between">
              <span>Engagement:</span>
              <span>{campaign.engagement_rate}%</span>
            </div>
          )}
        </div>
      </div>
    )}
  </div>
);

// ===== FINANCIAL MANAGEMENT COMPONENT =====

const FinancialManagement = () => {
  const [transactions, setTransactions] = useState([]);
  const [royaltyStatements, setRoyaltyStatements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('transactions');
  const [showAddModal, setShowAddModal] = useState(false);
  const [financialSummary, setFinancialSummary] = useState(null);

  useEffect(() => {
    if (activeTab === 'transactions') {
      fetchTransactions();
    } else if (activeTab === 'royalties') {
      fetchRoyaltyStatements();
    }
    fetchFinancialSummary();
  }, [activeTab]);

  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API}/label/finance/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoyaltyStatements = async () => {
    try {
      const response = await axios.get(`${API}/label/finance/royalty-statements`);
      setRoyaltyStatements(response.data);
    } catch (error) {
      console.error('Error fetching royalty statements:', error);
    }
  };

  const fetchFinancialSummary = async () => {
    // Mock financial summary
    setFinancialSummary({
      total_revenue: 150000,
      total_expenses: 85000,
      net_profit: 65000,
      outstanding_royalties: 25000,
      recoupment_balance: 45000
    });
  };

  const createTransaction = async (transactionData) => {
    try {
      await axios.post(`${API}/label/finance/transactions`, transactionData);
      setShowAddModal(false);
      fetchTransactions();
    } catch (error) {
      console.error('Error creating transaction:', error);
      alert('Error creating transaction');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">💰 Financial Management</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          + Add Transaction
        </button>
      </div>

      {/* Financial Summary */}
      {financialSummary && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-green-800">Total Revenue</h3>
            <p className="text-2xl font-bold text-green-900">${financialSummary.total_revenue.toLocaleString()}</p>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-red-800">Total Expenses</h3>
            <p className="text-2xl font-bold text-red-900">${financialSummary.total_expenses.toLocaleString()}</p>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-800">Net Profit</h3>
            <p className="text-2xl font-bold text-blue-900">${financialSummary.net_profit.toLocaleString()}</p>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-yellow-800">Outstanding Royalties</h3>
            <p className="text-2xl font-bold text-yellow-900">${financialSummary.outstanding_royalties.toLocaleString()}</p>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-purple-800">Recoupment Balance</h3>
            <p className="text-2xl font-bold text-purple-900">${financialSummary.recoupment_balance.toLocaleString()}</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['transactions', 'royalties', 'budgets', 'reports'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeTab === tab 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {loading && (
          <div className="flex justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}

        {activeTab === 'transactions' && !loading && (
          <TransactionManagement transactions={transactions} />
        )}

        {activeTab === 'royalties' && (
          <RoyaltyManagement royaltyStatements={royaltyStatements} />
        )}

        {activeTab === 'budgets' && (
          <BudgetManagement />
        )}

        {activeTab === 'reports' && (
          <FinancialReports />
        )}
      </div>

      {/* Add Transaction Modal */}
      {showAddModal && (
        <AddTransactionModal 
          onClose={() => setShowAddModal(false)}
          onSave={createTransaction}
        />
      )}
    </div>
  );
};

const TransactionManagement = ({ transactions }) => (
  <div>
    <h3 className="text-lg font-bold mb-4">💳 Recent Transactions</h3>
    
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {transactions.map((transaction) => (
            <tr key={transaction.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {new Date(transaction.transaction_date).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  transaction.transaction_type === 'revenue' ? 'bg-green-100 text-green-800' :
                  transaction.transaction_type === 'expense' ? 'bg-red-100 text-red-800' :
                  transaction.transaction_type === 'advance' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {transaction.transaction_type}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">{transaction.description}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <span className={
                  transaction.transaction_type === 'revenue' ? 'text-green-600' :
                  transaction.transaction_type === 'expense' ? 'text-red-600' :
                  'text-gray-900'
                }>
                  ${transaction.amount.toLocaleString()}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  transaction.status === 'paid' ? 'bg-green-100 text-green-800' :
                  transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {transaction.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    
    {transactions.length === 0 && (
      <div className="text-center py-8 text-gray-500">
        No transactions found. Add your first financial transaction to get started.
      </div>
    )}
  </div>
);

// Royalty Management Component
const RoyaltyManagement = ({ royaltyStatements }) => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h3 className="text-xl font-bold">Royalty Management</h3>
      <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Generate Statement
      </button>
    </div>

    {royaltyStatements && royaltyStatements.length > 0 ? (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {royaltyStatements.map((statement) => (
          <div key={statement.id} className="bg-white p-4 rounded-lg border shadow-sm">
            <h4 className="font-semibold">{statement.artist}</h4>
            <p className="text-gray-600">{statement.period}</p>
            <div className="mt-2">
              <p className="text-sm">Amount: <span className="font-semibold">${statement.amount}</span></p>
              <p className="text-sm">Status: 
                <span className={`ml-1 px-2 py-1 rounded text-xs ${
                  statement.status === 'paid' ? 'bg-green-100 text-green-800' : 
                  statement.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                  'bg-red-100 text-red-800'
                }`}>
                  {statement.status}
                </span>
              </p>
            </div>
            <button className="mt-3 w-full bg-gray-100 text-gray-800 px-3 py-1 rounded text-sm hover:bg-gray-200">
              View Details
            </button>
          </div>
        ))}
      </div>
    ) : (
      <div className="text-center py-8 text-gray-500">
        <p>No royalty statements available.</p>
        <p className="text-sm mt-2">Royalty statements will appear here once artists are signed and releases are distributed.</p>
      </div>
    )}
  </div>
);

// Social Media Management Component
const SocialMediaManagement = () => {
  const [socialPosts, setSocialPosts] = useState([]);
  const [platforms, setPlatforms] = useState([
    { name: 'Instagram', followers: 15432, engagement: '3.2%', posts: 143 },
    { name: 'TikTok', followers: 8921, engagement: '5.1%', posts: 89 },
    { name: 'Twitter/X', followers: 5643, engagement: '2.1%', posts: 267 },
    { name: 'YouTube', followers: 12850, engagement: '4.3%', posts: 45 },
    { name: 'Facebook', followers: 9876, engagement: '1.8%', posts: 156 }
  ]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold">📱 Social Media Management</h3>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          Create Post
        </button>
      </div>

      {/* Platform Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {platforms.map((platform) => (
          <div key={platform.name} className="bg-white border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium">{platform.name}</h4>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Active
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Followers:</span>
                <span className="font-medium">{platform.followers.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span>Engagement:</span>
                <span className="font-medium text-green-600">{platform.engagement}</span>
              </div>
              <div className="flex justify-between">
                <span>Posts:</span>
                <span className="font-medium">{platform.posts}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Content Calendar */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-medium mb-4">📅 Content Calendar</h4>
        <div className="text-center py-8 text-gray-500">
          <p>Content calendar integration coming soon</p>
          <p className="text-sm">Schedule and manage posts across all platforms</p>
        </div>
      </div>
    </div>
  );
};

// Press Management Component  
const PressManagement = ({ pressReleases }) => {
  const [mediaContacts, setMediaContacts] = useState([
    { id: 1, name: 'Music Weekly', contact: 'editor@musicweekly.com', type: 'Magazine' },
    { id: 2, name: 'Billboard', contact: 'news@billboard.com', type: 'Industry Publication' },
    { id: 3, name: 'Rolling Stone', contact: 'submissions@rollingstone.com', type: 'Magazine' },
    { id: 4, name: 'Pitchfork', contact: 'tips@pitchfork.com', type: 'Online Publication' }
  ]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold">📰 Press & Media Relations</h3>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
          Create Press Release
        </button>
      </div>

      {/* Press Releases Section */}
      <div className="bg-white border rounded-lg p-6 mb-6">
        <h4 className="font-medium mb-4">Recent Press Releases</h4>
        {pressReleases && pressReleases.length > 0 ? (
          <div className="space-y-4">
            {pressReleases.map((release) => (
              <div key={release.id} className="border-l-4 border-green-500 pl-4">
                <h5 className="font-medium">{release.title}</h5>
                <p className="text-sm text-gray-600 mt-1">{release.summary}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span>Published: {new Date(release.published_date).toLocaleDateString()}</span>
                  <span>Status: {release.status}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No press releases yet</p>
            <p className="text-sm">Create your first press release to announce new releases</p>
          </div>
        )}
      </div>

      {/* Media Contacts */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-medium mb-4">Media Contacts</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Publication</th>
                <th className="text-left py-2">Contact</th>
                <th className="text-left py-2">Type</th>
                <th className="text-left py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mediaContacts.map((contact) => (
                <tr key={contact.id} className="border-b">
                  <td className="py-2 font-medium">{contact.name}</td>
                  <td className="py-2 text-blue-600">{contact.contact}</td>
                  <td className="py-2">
                    <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                      {contact.type}
                    </span>
                  </td>
                  <td className="py-2">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">
                      Contact
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Marketing Analytics Component
const MarketingAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState({
    totalReach: 125430,
    engagement: 3420,
    conversions: 245,
    roi: 312
  });

  const [campaignPerformance, setCampaignPerformance] = useState([
    { name: 'Summer Release Campaign', impressions: 45230, clicks: 1205, ctr: '2.7%', cost: 1200 },
    { name: 'Social Media Push', impressions: 32100, clicks: 892, ctr: '2.8%', cost: 800 },
    { name: 'Press Release Distribution', impressions: 15600, clicks: 423, ctr: '2.7%', cost: 300 }
  ]);

  return (
    <div>
      <h3 className="text-lg font-bold mb-6">📊 Marketing Analytics</h3>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Reach</p>
              <p className="text-2xl font-bold text-blue-600">{analyticsData.totalReach.toLocaleString()}</p>
            </div>
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              👁️
            </div>
          </div>
        </div>

        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Engagement</p>
              <p className="text-2xl font-bold text-green-600">{analyticsData.engagement.toLocaleString()}</p>
            </div>
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              💬
            </div>
          </div>
        </div>

        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Conversions</p>
              <p className="text-2xl font-bold text-purple-600">{analyticsData.conversions.toLocaleString()}</p>
            </div>
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              🎯
            </div>
          </div>
        </div>

        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">ROI %</p>
              <p className="text-2xl font-bold text-orange-600">{analyticsData.roi}%</p>
            </div>
            <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
              📈
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Performance */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-medium mb-4">Campaign Performance</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Campaign</th>
                <th className="text-left py-2">Impressions</th>
                <th className="text-left py-2">Clicks</th>
                <th className="text-left py-2">CTR</th>
                <th className="text-left py-2">Cost</th>
              </tr>
            </thead>
            <tbody>
              {campaignPerformance.map((campaign, index) => (
                <tr key={index} className="border-b">
                  <td className="py-2 font-medium">{campaign.name}</td>
                  <td className="py-2">{campaign.impressions.toLocaleString()}</td>
                  <td className="py-2">{campaign.clicks.toLocaleString()}</td>
                  <td className="py-2">{campaign.ctr}</td>
                  <td className="py-2">${campaign.cost.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Export all components
export { 
  ProjectManagement,
  MarketingManagement,
  FinancialManagement,
  ProjectCard,
  CampaignCard,
  TransactionManagement,
  RoyaltyManagement,
  SocialMediaManagement,
  PressManagement,
  MarketingAnalytics
};