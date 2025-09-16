import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  MapPin, 
  Target, 
  DollarSign, 
  Users, 
  Clock,
  Play,
  Pause,
  Save,
  Plus,
  Edit,
  Trash2,
  Eye,
  Settings,
  Upload,
  Image as ImageIcon,
  Video,
  Globe,
  Zap,
  BarChart3,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

// AWS Amplify imports
import { API, Auth, Storage } from 'aws-amplify';

const CampaignManager = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('active');

  // Campaign form state
  const [campaignForm, setCampaignForm] = useState({
    name: '',
    description: '',
    budget: '',
    startDate: '',
    endDate: '',
    targetAudience: {
      demographics: {},
      geotargeting: [],
      interests: []
    },
    creativeAssets: [],
    triggers: [],
    platforms: []
  });

  // Available platforms
  const doohPlatforms = [
    { id: 'vistar', name: 'Vistar Media', type: 'DSP', regions: ['US', 'CA'] },
    { id: 'hivestack', name: 'Hivestack', type: 'SSP', regions: ['Global'] },
    { id: 'broadsign', name: 'Broadsign', type: 'CMS', regions: ['Global'] },
    { id: 'tradedesk', name: 'The Trade Desk', type: 'DSP', regions: ['US', 'EU'] },
    { id: 'viooh', name: 'VIOOH', type: 'Marketplace', regions: ['UK', 'EU'] }
  ];

  // Campaign status options
  const campaignStatuses = {
    draft: { label: 'Draft', color: 'gray', icon: Edit },
    active: { label: 'Active', color: 'green', icon: Play },
    paused: { label: 'Paused', color: 'yellow', icon: Pause },
    completed: { label: 'Completed', color: 'blue', icon: CheckCircle },
    cancelled: { label: 'Cancelled', color: 'red', icon: XCircle }
  };

  useEffect(() => {
    loadCurrentUser();
    loadCampaigns();
  }, []);

  const loadCurrentUser = async () => {
    try {
      const user = await Auth.currentAuthenticatedUser();
      setCurrentUser(user);
    } catch (error) {
      console.error('Error loading user:', error);
    }
  };

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const response = await API.get('doohapi', '/campaigns', {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });
      setCampaigns(response.campaigns || []);
    } catch (error) {
      console.error('Error loading campaigns:', error);
      // Mock data for demonstration
      setCampaigns([
        {
          id: 'camp_001',
          name: 'Summer Music Festival 2025',
          description: 'Promote upcoming summer music festival across major cities',
          status: 'active',
          budget: 25000,
          spent: 18750,
          startDate: '2025-01-15',
          endDate: '2025-02-15',
          impressions: 2450000,
          clicks: 8330,
          conversions: 847,
          platforms: ['vistar', 'hivestack'],
          createdBy: 'artist_user_001',
          createdAt: '2025-01-10T10:00:00Z'
        },
        {
          id: 'camp_002',
          name: 'New Artist Launch',
          description: 'Launch campaign for emerging artist debut album',
          status: 'paused',
          budget: 15000,
          spent: 8200,
          startDate: '2025-01-10',
          endDate: '2025-01-31',
          impressions: 1230000,
          clicks: 4560,
          conversions: 445,
          platforms: ['broadsign', 'viooh'],
          createdBy: 'sponsor_user_002',
          createdAt: '2025-01-08T14:30:00Z'
        }
      ]);
    }
    setLoading(false);
  };

  const createCampaign = async () => {
    setLoading(true);
    try {
      const campaignData = {
        ...campaignForm,
        createdBy: currentUser?.username,
        createdAt: new Date().toISOString(),
        status: 'draft'
      };

      const response = await API.post('doohapi', '/campaigns', {
        body: campaignData,
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setCampaigns([...campaigns, response.campaign]);
      setShowCreateModal(false);
      setCampaignForm({
        name: '',
        description: '',
        budget: '',
        startDate: '',
        endDate: '',
        targetAudience: { demographics: {}, geotargeting: [], interests: [] },
        creativeAssets: [],
        triggers: [],
        platforms: []
      });
    } catch (error) {
      console.error('Error creating campaign:', error);
    }
    setLoading(false);
  };

  const updateCampaignStatus = async (campaignId, newStatus) => {
    try {
      await API.put('doohapi', `/campaigns/${campaignId}/status`, {
        body: { status: newStatus },
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setCampaigns(campaigns.map(camp => 
        camp.id === campaignId ? { ...camp, status: newStatus } : camp
      ));
    } catch (error) {
      console.error('Error updating campaign status:', error);
    }
  };

  const deleteCampaign = async (campaignId) => {
    if (!window.confirm('Are you sure you want to delete this campaign?')) return;

    try {
      await API.del('doohapi', `/campaigns/${campaignId}`, {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setCampaigns(campaigns.filter(camp => camp.id !== campaignId));
    } catch (error) {
      console.error('Error deleting campaign:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getStatusConfig = (status) => campaignStatuses[status] || campaignStatuses.draft;

  const filteredCampaigns = campaigns.filter(campaign => 
    activeTab === 'all' || campaign.status === activeTab
  );

  const renderCampaignCard = (campaign) => {
    const statusConfig = getStatusConfig(campaign.status);
    const StatusIcon = statusConfig.icon;
    const ctr = campaign.clicks > 0 ? ((campaign.clicks / campaign.impressions) * 100).toFixed(2) : 0;
    const budgetUsed = (campaign.spent / campaign.budget) * 100;

    return (
      <div key={campaign.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center space-x-3">
            <StatusIcon className={`w-5 h-5 text-${statusConfig.color}-500`} />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
              <p className="text-sm text-gray-600">{campaign.description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-xs font-medium bg-${statusConfig.color}-100 text-${statusConfig.color}-800`}>
              {statusConfig.label}
            </span>
            <div className="flex space-x-1">
              <button 
                onClick={() => setSelectedCampaign(campaign)}
                className="p-2 text-gray-400 hover:text-blue-600 rounded"
              >
                <Eye className="w-4 h-4" />
              </button>
              <button className="p-2 text-gray-400 hover:text-green-600 rounded">
                <Edit className="w-4 h-4" />
              </button>
              <button 
                onClick={() => deleteCampaign(campaign.id)}
                className="p-2 text-gray-400 hover:text-red-600 rounded"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500">Budget</p>
            <p className="text-sm font-medium">{formatCurrency(campaign.budget)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Spent</p>
            <p className="text-sm font-medium">{formatCurrency(campaign.spent)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Impressions</p>
            <p className="text-sm font-medium">{formatNumber(campaign.impressions)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">CTR</p>
            <p className="text-sm font-medium">{ctr}%</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Budget Progress</span>
            <span>{budgetUsed.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${budgetUsed > 90 ? 'bg-red-500' : budgetUsed > 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
              style={{ width: `${Math.min(budgetUsed, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Globe className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">{campaign.platforms.length} platforms</span>
            </div>
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                {new Date(campaign.startDate).toLocaleDateString()} - {new Date(campaign.endDate).toLocaleDateString()}
              </span>
            </div>
          </div>
          <div className="flex space-x-2">
            {campaign.status === 'active' && (
              <button 
                onClick={() => updateCampaignStatus(campaign.id, 'paused')}
                className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded text-xs hover:bg-yellow-200"
              >
                Pause
              </button>
            )}
            {campaign.status === 'paused' && (
              <button 
                onClick={() => updateCampaignStatus(campaign.id, 'active')}
                className="px-3 py-1 bg-green-100 text-green-800 rounded text-xs hover:bg-green-200"
              >
                Resume
              </button>
            )}
            {campaign.status === 'draft' && (
              <button 
                onClick={() => updateCampaignStatus(campaign.id, 'active')}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-xs hover:bg-blue-200"
              >
                Launch
              </button>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderCreateModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Create New Campaign</h2>
          <button 
            onClick={() => setShowCreateModal(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Name</label>
              <input
                type="text"
                value={campaignForm.name}
                onChange={(e) => setCampaignForm({...campaignForm, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter campaign name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={campaignForm.description}
                onChange={(e) => setCampaignForm({...campaignForm, description: e.target.value})}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe your campaign goals"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Budget (USD)</label>
              <input
                type="number"
                value={campaignForm.budget}
                onChange={(e) => setCampaignForm({...campaignForm, budget: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="10000"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input
                  type="date"
                  value={campaignForm.startDate}
                  onChange={(e) => setCampaignForm({...campaignForm, startDate: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input
                  type="date"
                  value={campaignForm.endDate}
                  onChange={(e) => setCampaignForm({...campaignForm, endDate: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Platform Selection */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Platform Selection</h3>
            <div className="space-y-2">
              {doohPlatforms.map(platform => (
                <label key={platform.id} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={campaignForm.platforms.includes(platform.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setCampaignForm({
                          ...campaignForm, 
                          platforms: [...campaignForm.platforms, platform.id]
                        });
                      } else {
                        setCampaignForm({
                          ...campaignForm, 
                          platforms: campaignForm.platforms.filter(p => p !== platform.id)
                        });
                      }
                    }}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{platform.name}</div>
                    <div className="text-sm text-gray-500">{platform.type} • {platform.regions.join(', ')}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4 mt-8">
          <button 
            onClick={() => setShowCreateModal(false)}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button 
            onClick={createCampaign}
            disabled={loading || !campaignForm.name || !campaignForm.budget}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>}
            <span>Create Campaign</span>
          </button>
        </div>
      </div>
    </div>
  );

  if (loading && campaigns.length === 0) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campaign Manager</h1>
          <p className="text-gray-600 mt-1">Create and manage your DOOH advertising campaigns</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>New Campaign</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'all', name: 'All Campaigns', count: campaigns.length },
            { id: 'active', name: 'Active', count: campaigns.filter(c => c.status === 'active').length },
            { id: 'paused', name: 'Paused', count: campaigns.filter(c => c.status === 'paused').length },
            { id: 'draft', name: 'Draft', count: campaigns.filter(c => c.status === 'draft').length },
            { id: 'completed', name: 'Completed', count: campaigns.filter(c => c.status === 'completed').length }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name} ({tab.count})
            </button>
          ))}
        </nav>
      </div>

      {/* Campaign Grid */}
      <div className="grid gap-6">
        {filteredCampaigns.length > 0 ? (
          filteredCampaigns.map(renderCampaignCard)
        ) : (
          <div className="text-center py-12">
            <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns found</h3>
            <p className="text-gray-600 mb-4">
              {activeTab === 'all' 
                ? "You haven't created any campaigns yet." 
                : `No ${activeTab} campaigns found.`
              }
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              <span>Create Your First Campaign</span>
            </button>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && renderCreateModal()}

      {/* Campaign Detail Modal */}
      {selectedCampaign && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">{selectedCampaign.name}</h2>
              <button 
                onClick={() => setSelectedCampaign(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            {/* Campaign details would go here */}
            <div className="space-y-4">
              <p className="text-gray-600">{selectedCampaign.description}</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Total Budget</p>
                  <p className="text-xl font-semibold">{formatCurrency(selectedCampaign.budget)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Amount Spent</p>
                  <p className="text-xl font-semibold">{formatCurrency(selectedCampaign.spent)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Impressions</p>
                  <p className="text-xl font-semibold">{formatNumber(selectedCampaign.impressions)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Conversions</p>
                  <p className="text-xl font-semibold">{selectedCampaign.conversions}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignManager;