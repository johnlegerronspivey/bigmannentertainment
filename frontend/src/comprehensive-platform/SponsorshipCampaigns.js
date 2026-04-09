import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API, handleApiError } from './utils';

const SponsorshipCampaigns = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [campaigns, setCampaigns] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('campaigns');

  useEffect(() => { fetchSponsorshipData(); }, []);

  const fetchSponsorshipData = async () => {
    setLoading(true);
    try {
      const [campaignsRes, opportunitiesRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/api/platform/sponsorship/campaigns?user_id=user_123`),
        axios.get(`${API}/api/platform/sponsorship/opportunities?user_id=user_123`),
        axios.get(`${API}/api/platform/sponsorship/analytics?user_id=user_123`)
      ]);
      if (campaignsRes.data.success) setCampaigns(campaignsRes.data.campaigns || []);
      if (opportunitiesRes.data.success) setOpportunities(opportunitiesRes.data.opportunities || []);
      if (analyticsRes.data.success) setAnalytics(analyticsRes.data.analytics || {});
    } catch (error) { handleApiError(error, 'fetchSponsorshipData'); } finally { setLoading(false); }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'completed': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'paused': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'cancelled': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'campaigns', name: 'My Campaigns', icon: '🎯' },
    { id: 'opportunities', name: 'Opportunities', icon: '💼' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
    { id: 'create', name: 'Create Campaign', icon: '➕' }
  ];

  return (
    <div data-testid="sponsorship-campaigns" className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Sponsorship & Campaigns</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Manage sponsorship deals and marketing campaigns</p>
        </div>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2">
          <span>🚀</span><span>Launch Campaign</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between"><div><p className="text-sm text-gray-600 dark:text-gray-400">Total Campaigns</p><p data-testid="sponsorship-total-campaigns" className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.overview?.total_campaigns || '0'}</p></div><span className="text-2xl">🎯</span></div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between"><div><p className="text-sm text-gray-600 dark:text-gray-400">Active Campaigns</p><p className="text-2xl font-bold text-green-600">{analytics.overview?.active_campaigns || '0'}</p></div><span className="text-2xl">🟢</span></div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between"><div><p className="text-sm text-gray-600 dark:text-gray-400">Total Spend</p><p className="text-2xl font-bold text-blue-600">${analytics.overview?.total_spent?.toLocaleString() || '0'}</p></div><span className="text-2xl">💰</span></div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between"><div><p className="text-sm text-gray-600 dark:text-gray-400">ROI</p><p className="text-2xl font-bold text-purple-600">{analytics.overview?.roi || '0'}%</p></div><span className="text-2xl">📈</span></div>
        </div>
      </div>

      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id ? 'border-purple-500 text-purple-600 dark:text-purple-400' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'}`}>
              <span>{tab.icon}</span><span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="space-y-4">
        {activeTab === 'campaigns' && (
          <div className="space-y-4">
            {campaigns.length > 0 ? campaigns.map((campaign, index) => (
              <div key={campaign.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{campaign.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(campaign.status)}`}>{campaign.status}</span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{campaign.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Brand: {campaign.brand_name}</span>
                      <span>Type: {campaign.campaign_type?.replace('_', ' ')}</span>
                      <span>Budget: ${campaign.budget_total?.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View</button>
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">Edit</button>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div><p className="text-sm text-gray-600 dark:text-gray-400">Budget Used</p><div className="flex items-center space-x-2 mt-1"><div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2"><div className="bg-purple-600 h-2 rounded-full" style={{width: `${((campaign.budget_spent || 0) / (campaign.budget_total || 1)) * 100}%`}}></div></div><span className="text-sm font-medium text-gray-900 dark:text-white">${(campaign.budget_spent || 0).toLocaleString()}</span></div></div>
                  <div><p className="text-sm text-gray-600 dark:text-gray-400">Start Date</p><p className="font-medium text-gray-900 dark:text-white">{campaign.start_date ? new Date(campaign.start_date).toLocaleDateString() : 'N/A'}</p></div>
                  <div><p className="text-sm text-gray-600 dark:text-gray-400">End Date</p><p className="font-medium text-gray-900 dark:text-white">{campaign.end_date ? new Date(campaign.end_date).toLocaleDateString() : 'N/A'}</p></div>
                  <div><p className="text-sm text-gray-600 dark:text-gray-400">Platforms</p><p className="font-medium text-gray-900 dark:text-white">{campaign.targeting?.platforms?.length || 0} platforms</p></div>
                </div>
              </div>
            )) : (<div className="text-center py-8"><div className="text-4xl mb-4">🎯</div><p className="text-gray-600 dark:text-gray-400">No campaigns found. Create your first campaign!</p></div>)}
          </div>
        )}

        {activeTab === 'opportunities' && (
          <div className="space-y-4">
            {opportunities.length > 0 ? opportunities.map((opportunity, index) => (
              <div key={opportunity.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{opportunity.title}</h3>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs rounded-full">{opportunity.industry}</span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{opportunity.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Brand: {opportunity.brand_name}</span>
                      <span>Budget: ${opportunity.budget_range?.min?.toLocaleString()} - ${opportunity.budget_range?.max?.toLocaleString()}</span>
                      <span>Deadline: {new Date(opportunity.deadline).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 ml-4">Apply</button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div><p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Requirements</p><div className="space-y-1">{opportunity.requirements?.map((req, idx) => (<p key={idx} className="text-sm text-gray-600 dark:text-gray-400">• {req}</p>))}</div></div>
                  <div><p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Contact</p><div className="space-y-1"><p className="text-sm text-gray-600 dark:text-gray-400">Email: {opportunity.contact_info?.email}</p>{opportunity.contact_info?.phone && (<p className="text-sm text-gray-600 dark:text-gray-400">Phone: {opportunity.contact_info.phone}</p>)}</div></div>
                </div>
              </div>
            )) : (<div className="text-center py-8"><div className="text-4xl mb-4">💼</div><p className="text-gray-600 dark:text-gray-400">No opportunities available at the moment.</p></div>)}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Campaigns</h3>
              <div className="space-y-4">{analytics.top_performing_campaigns?.slice(0, 5).map((campaign, index) => (<div key={campaign.id || index} className="flex justify-between items-center"><div><p className="font-medium text-gray-900 dark:text-white">{campaign.title}</p><p className="text-sm text-gray-600 dark:text-gray-400">{campaign.impressions?.toLocaleString() || 0} impressions</p></div><div className="text-right"><p className="font-semibold text-green-600">{campaign.roi}% ROI</p><p className="text-sm text-gray-600 dark:text-gray-400">{campaign.engagement_rate}% engagement</p></div></div>))}</div>
            </div>
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Performance</h3>
              <div className="space-y-4">{analytics.by_platform && Object.entries(analytics.by_platform).map(([platform, data]) => (<div key={platform} className="flex justify-between items-center"><div><p className="font-medium text-gray-900 dark:text-white capitalize">{platform}</p><p className="text-sm text-gray-600 dark:text-gray-400">{data.campaigns} campaigns</p></div><div className="text-right"><p className="font-semibold text-blue-600">{data.engagement_rate}% engagement</p><p className="text-sm text-gray-600 dark:text-gray-400">${data.cost_per_impression} CPI</p></div></div>))}</div>
            </div>
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6 lg:col-span-2`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">ROI Trends (Monthly)</h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">{analytics.monthly_trends?.map((month, index) => (<div key={month.month || index} className="text-center"><p className="text-sm text-gray-600 dark:text-gray-400">{month.month}</p><p className="text-lg font-semibold text-gray-900 dark:text-white">{month.roi}%</p><p className="text-xs text-gray-500 dark:text-gray-500">${month.spend?.toLocaleString()}</p></div>))}</div>
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Create New Campaign</h3>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Campaign Name</label><input type="text" placeholder="Enter campaign name..." className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} /></div>
                <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Brand Name</label><input type="text" placeholder="Enter brand name..." className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} /></div>
              </div>
              <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label><textarea rows={3} placeholder="Describe your campaign..." className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} /></div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Campaign Type</label><select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}><option>Brand Sponsorship</option><option>Product Placement</option><option>Influencer Campaign</option><option>Content Partnership</option><option>Event Sponsorship</option></select></div>
                <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Budget ($)</label><input type="number" placeholder="0" className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} /></div>
                <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Budget Type</label><select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}><option>Fixed</option><option>Performance Based</option><option>Hybrid</option></select></div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Start Date</label><input type="date" className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} /></div>
                <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">End Date</label><input type="date" className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} /></div>
              </div>
              <div><label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Target Platforms</label><div className="grid grid-cols-2 md:grid-cols-4 gap-3">{['Instagram', 'TikTok', 'YouTube', 'Facebook', 'Twitter', 'LinkedIn', 'Snapchat', 'Pinterest'].map((platform) => (<label key={platform} className="flex items-center space-x-2"><input type="checkbox" className="rounded" /><span className="text-sm text-gray-700 dark:text-gray-300">{platform}</span></label>))}</div></div>
              <div className="flex space-x-4">
                <button className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700">Create Campaign</button>
                <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">Save as Draft</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export { SponsorshipCampaigns };
