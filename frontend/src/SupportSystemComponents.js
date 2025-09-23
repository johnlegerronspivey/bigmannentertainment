import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main Support System Dashboard
export const SupportSystemDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState(null);
  const [userDashboard, setUserDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSystemData();
  }, []);

  const fetchSystemData = async () => {
    try {
      setLoading(true);
      
      // Fetch system health
      const healthResponse = await axios.get(`${API}/support/health`);
      setSystemHealth(healthResponse.data);
      
      // Fetch user dashboard (requires auth)
      try {
        const dashboardResponse = await axios.get(`${API}/support/dashboard`);
        setUserDashboard(dashboardResponse.data);
      } catch (authError) {
        console.log('Dashboard requires authentication - user not logged in');
      }
      
      setError('');
    } catch (error) {
      console.error('Error fetching system data:', error);
      setError('Failed to load support system data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">Loading Support System...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Support Center</h1>
          <p className="mt-2 text-gray-600">
            Multi-tiered support system with live chat, ticketing, DAO arbitration & knowledge base
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'dashboard', name: 'Dashboard', icon: '📊' },
              { id: 'tickets', name: 'Support Tickets', icon: '🎫' },
              { id: 'chat', name: 'Live Chat', icon: '💬' },
              { id: 'knowledge', name: 'Knowledge Base', icon: '📚' },
              { id: 'dao', name: 'DAO Arbitration', icon: '⚖️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'dashboard' && (
          <SupportDashboardTab 
            systemHealth={systemHealth} 
            userDashboard={userDashboard}
            onRefresh={fetchSystemData}
          />
        )}
        {activeTab === 'tickets' && <TicketingTab />}
        {activeTab === 'chat' && <LiveChatTab />}
        {activeTab === 'knowledge' && <KnowledgeBaseTab />}
        {activeTab === 'dao' && <DAOArbitrationTab />}
      </div>
    </div>
  );
};

// Support Dashboard Tab
const SupportDashboardTab = ({ systemHealth, userDashboard, onRefresh }) => {
  return (
    <div className="space-y-6">
      {/* System Status Cards */}
      {systemHealth && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white shadow rounded-lg p-4 text-center">
            <div className={`text-2xl mb-2 ${systemHealth.live_chat_active ? 'text-green-600' : 'text-red-600'}`}>
              💬
            </div>
            <p className="font-medium text-gray-900">Live Chat</p>
            <p className="text-sm text-gray-600">
              {systemHealth.live_chat_active ? 'Active' : 'Inactive'}
            </p>
            <p className="text-xs text-gray-500">{systemHealth.total_active_chats} active</p>
          </div>

          <div className="bg-white shadow rounded-lg p-4 text-center">
            <div className={`text-2xl mb-2 ${systemHealth.ticketing_system_active ? 'text-green-600' : 'text-red-600'}`}>
              🎫
            </div>
            <p className="font-medium text-gray-900">Ticketing</p>
            <p className="text-sm text-gray-600">
              {systemHealth.ticketing_system_active ? 'Active' : 'Inactive'}
            </p>
            <p className="text-xs text-gray-500">{systemHealth.total_active_tickets} open</p>
          </div>

          <div className="bg-white shadow rounded-lg p-4 text-center">
            <div className={`text-2xl mb-2 ${systemHealth.dao_integration_active ? 'text-green-600' : 'text-red-600'}`}>
              ⚖️
            </div>
            <p className="font-medium text-gray-900">DAO System</p>
            <p className="text-sm text-gray-600">
              {systemHealth.dao_integration_active ? 'Active' : 'Inactive'}
            </p>
            <p className="text-xs text-gray-500">{systemHealth.total_active_disputes} disputes</p>
          </div>

          <div className="bg-white shadow rounded-lg p-4 text-center">
            <div className={`text-2xl mb-2 ${systemHealth.knowledge_base_active ? 'text-green-600' : 'text-red-600'}`}>
              📚
            </div>
            <p className="font-medium text-gray-900">Knowledge Base</p>
            <p className="text-sm text-gray-600">
              {systemHealth.knowledge_base_active ? 'Active' : 'Inactive'}
            </p>
            <p className="text-xs text-gray-500">{systemHealth.total_kb_articles} articles</p>
          </div>

          <div className="bg-white shadow rounded-lg p-4 text-center">
            <div className={`text-2xl mb-2 ${systemHealth.ai_automation_active ? 'text-green-600' : 'text-red-600'}`}>
              🤖
            </div>
            <p className="font-medium text-gray-900">AI Automation</p>
            <p className="text-sm text-gray-600">
              {systemHealth.ai_automation_active ? 'Active' : 'Inactive'}
            </p>
            <p className="text-xs text-gray-500">Auto-tagging</p>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {systemHealth && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Performance</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {systemHealth.avg_ticket_resolution_time_hours}h
              </div>
              <p className="text-sm text-gray-600">Avg Resolution Time</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {systemHealth.avg_chat_response_time_minutes}m
              </div>
              <p className="text-sm text-gray-600">Avg Chat Response</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {systemHealth.system_uptime_percentage}%
              </div>
              <p className="text-sm text-gray-600">System Uptime</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {systemHealth.user_satisfaction_score}/5
              </div>
              <p className="text-sm text-gray-600">User Satisfaction</p>
            </div>
          </div>
        </div>
      )}

      {/* User Dashboard (if authenticated) */}
      {userDashboard && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Your Tickets */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Support Activity</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">Total Tickets</p>
                  <p className="text-sm text-gray-600">{userDashboard.total_tickets} created</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-600">{userDashboard.total_tickets}</p>
                </div>
              </div>
              
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">Open Issues</p>
                  <p className="text-sm text-gray-600">Pending resolution</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-orange-600">{userDashboard.open_tickets}</p>
                </div>
              </div>

              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">Resolved</p>
                  <p className="text-sm text-gray-600">Successfully completed</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">{userDashboard.resolved_tickets}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            {userDashboard.recent_tickets?.length > 0 ? (
              <div className="space-y-3">
                {userDashboard.recent_tickets.slice(0, 3).map((ticket, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                    <p className="font-medium text-gray-900 text-sm">
                      {ticket.title || 'Support Ticket'}
                    </p>
                    <p className="text-xs text-gray-600">
                      Status: <span className="capitalize">{ticket.status}</span> • 
                      {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No recent activity</p>
            )}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <button className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors">
            <span className="text-2xl mb-2">🎫</span>
            <span className="font-medium">Create Ticket</span>
          </button>
          
          <button className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors">
            <span className="text-2xl mb-2">💬</span>
            <span className="font-medium">Start Chat</span>
          </button>
          
          <button className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors">
            <span className="text-2xl mb-2">📚</span>
            <span className="font-medium">Browse Docs</span>
          </button>
          
          <button 
            onClick={onRefresh}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl mb-2">🔄</span>
            <span className="font-medium">Refresh</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// Enhanced Ticketing System Tab with AI Features
const TicketingTab = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [aiSuggestions, setAiSuggestions] = useState(null);
  const [analyzingTicket, setAnalyzingTicket] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showTicketDetails, setShowTicketDetails] = useState(false);
  const [newTicket, setNewTicket] = useState({
    title: '',
    description: '',
    category: 'technical_support',
    priority: 'medium',
    asset_id: '',
    user_contact_email: ''
  });

  const ticketCategories = [
    { value: 'technical_support', label: 'Technical Support', icon: '🔧' },
    { value: 'licensing_dispute', label: 'Licensing Dispute', icon: '⚖️' },
    { value: 'royalty_issue', label: 'Royalty Issue', icon: '💰' },
    { value: 'platform_bug', label: 'Platform Bug', icon: '🐛' },
    { value: 'content_removal', label: 'Content Removal', icon: '🗑️' },
    { value: 'payment_issue', label: 'Payment Issue', icon: '💳' },
    { value: 'account_access', label: 'Account Access', icon: '🔐' },
    { value: 'general_inquiry', label: 'General Inquiry', icon: '❓' }
  ];

  const ticketPriorities = [
    { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
    { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' }
  ];

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      if (filterStatus) params.append('status', filterStatus);
      
      const response = await axios.get(`${API}/support/tickets?${params}`);
      setTickets(response.data.tickets || []);
    } catch (error) {
      console.error('Error fetching tickets:', error);
      // Handle non-authenticated state gracefully
      if (error.response?.status === 401) {
        setTickets([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [searchQuery, filterStatus]);

  // AI-powered ticket analysis
  const analyzeTicketContent = async () => {
    if (!newTicket.title || !newTicket.description) return;
    
    setAnalyzingTicket(true);
    try {
      const response = await axios.get(`${API}/support/ai/faq-suggestions`, {
        params: {
          query: `${newTicket.title} ${newTicket.description}`,
          context: `Category: ${newTicket.category}, Priority: ${newTicket.priority}`,
          limit: 3
        }
      });
      
      if (response.data.suggestions) {
        setAiSuggestions(response.data.suggestions);
      }
    } catch (error) {
      console.error('Error analyzing ticket:', error);
    } finally {
      setAnalyzingTicket(false);
    }
  };

  // Debounced analysis trigger
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (newTicket.title || newTicket.description) {
        analyzeTicketContent();
      }
    }, 2000);
    
    return () => clearTimeout(timeoutId);
  }, [newTicket.title, newTicket.description]);

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await axios.post(`${API}/support/tickets`, newTicket);
      if (response.data) {
        setShowCreateForm(false);
        setNewTicket({
          title: '',
          description: '',
          category: 'technical_support',
          priority: 'medium',
          asset_id: '',
          user_contact_email: ''
        });
        setAiSuggestions(null);
        fetchTickets();
        
        // Show success with AI insights
        const ticket = response.data;
        alert(`Support ticket created successfully! ${
          ticket.ai_tags ? `AI detected topics: ${ticket.ai_tags.join(', ')}` : ''
        }`);
      }
    } catch (error) {
      console.error('Error creating ticket:', error);
      alert('Failed to create ticket: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const viewTicketDetails = async (ticket) => {
    setSelectedTicket(ticket);
    setShowTicketDetails(true);
    
    // Fetch AI analysis for the ticket if available
    if (ticket.ticket_id) {
      try {
        const response = await axios.get(`${API}/support/ai/analysis/ticket/${ticket.ticket_id}`);
        setSelectedTicket(prev => ({...prev, ai_analysis: response.data}));
      } catch (error) {
        console.log('No AI analysis available for this ticket');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Support Tickets</h2>
          <p className="text-gray-600">Manage your support requests and track their progress</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium"
        >
          Create New Ticket
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Search tickets..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status Filter</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={fetchTickets}
              className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 border border-gray-300 rounded-md font-medium"
            >
              Search
            </button>
          </div>
        </div>
      </div>

      {/* Create Ticket Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Create Support Ticket</h3>
            <form onSubmit={handleCreateTicket} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  required
                  value={newTicket.title}
                  onChange={(e) => setNewTicket({...newTicket, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of your issue"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description *
                </label>
                <textarea
                  required
                  rows="4"
                  value={newTicket.description}
                  onChange={(e) => setNewTicket({...newTicket, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Detailed description of your issue"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    value={newTicket.category}
                    onChange={(e) => setNewTicket({...newTicket, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {ticketCategories.map(cat => (
                      <option key={cat.value} value={cat.value}>{cat.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={newTicket.priority}
                    onChange={(e) => setNewTicket({...newTicket, priority: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {ticketPriorities.map(pri => (
                      <option key={pri.value} value={pri.value}>{pri.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Asset ID (Optional)
                  </label>
                  <input
                    type="text"
                    value={newTicket.asset_id}
                    onChange={(e) => setNewTicket({...newTicket, asset_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Related asset or content ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Contact Email (Optional)
                  </label>
                  <input
                    type="email"
                    value={newTicket.user_contact_email}
                    onChange={(e) => setNewTicket({...newTicket, user_contact_email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Alternative contact email"
                  />
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Create Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Tickets List */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Tickets</h3>
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading tickets...</p>
          </div>
        ) : tickets.length > 0 ? (
          <div className="space-y-4">
            {tickets.map((ticket, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{ticket.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{ticket.description}</p>
                    <div className="flex items-center space-x-4 mt-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        ticket.status === 'open' ? 'bg-green-100 text-green-800' :
                        ticket.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                        ticket.status === 'resolved' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {ticket.status?.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        ticket.priority === 'critical' ? 'bg-red-100 text-red-800' :
                        ticket.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                        ticket.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {ticket.priority?.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        {ticket.category?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-sm text-gray-500">
                      {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                    <button className="text-blue-600 hover:text-blue-800 text-sm mt-1">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🎫</div>
            <p className="text-gray-500 mb-4">No support tickets yet</p>
            <p className="text-sm text-gray-400">
              Create your first ticket to get help from our support team
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Live Chat Tab with WebSocket integration
const LiveChatTab = () => {
  const [chatSessions, setChatSessions] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [websocket, setWebsocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [isTyping, setIsTyping] = useState(false);
  const [otherTyping, setOtherTyping] = useState(new Set());
  const [agentStatus, setAgentStatus] = useState('offline');
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  useEffect(() => {
    return () => {
      if (websocket) {
        websocket.close();
      }
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [websocket]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const connectWebSocket = (sessionId, userId = 'user123', userType = 'customer') => {
    try {
      const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/api/support/ws/chat/${sessionId}?user_id=${userId}&user_type=${userType}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setConnectionStatus('connected');
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      ws.onclose = () => {
        setConnectionStatus('disconnected');
        console.log('WebSocket disconnected');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };

      setWebsocket(ws);
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'new_message':
        setMessages(prev => [...prev, data.message]);
        break;
      case 'message_history':
        setMessages(prev => [...prev, data.message]);
        break;
      case 'typing_indicator':
        if (data.is_typing) {
          setOtherTyping(prev => new Set([...prev, data.user_id]));
        } else {
          setOtherTyping(prev => {
            const newSet = new Set(prev);
            newSet.delete(data.user_id);
            return newSet;
          });
        }
        break;
      case 'agent_assigned':
        setAgentStatus('online');
        setMessages(prev => [...prev, {
          message_id: 'system_' + Date.now(),
          sender_type: 'system',
          content: `${data.agent_name || 'An agent'} has joined the chat`,
          timestamp: data.timestamp
        }]);
        break;
      case 'agent_unavailable':
        setAgentStatus('offline');
        setMessages(prev => [...prev, {
          message_id: 'system_' + Date.now(),
          sender_type: 'system', 
          content: data.message,
          timestamp: data.timestamp
        }]);
        break;
      case 'escalation_alert':
        // Handle escalation notifications
        break;
      case 'heartbeat':
        // Respond to heartbeat
        if (websocket) {
          websocket.send(JSON.stringify({ type: 'pong' }));
        }
        break;
    }
  };

  const startNewChat = async () => {
    try {
      setLoading(true);
      const chatRequest = {
        initial_message: "Hello, I need assistance with my account.",
        category: "technical_support",
        priority: "medium"
      };
      
      const response = await axios.post(`${API}/support/chat/sessions`, chatRequest);
      if (response.data) {
        const newSession = response.data;
        setChatSessions([newSession, ...chatSessions]);
        setActiveChatId(newSession.session_id);
        setMessages([]);
        
        // Connect WebSocket for real-time chat
        connectWebSocket(newSession.session_id);
      }
    } catch (error) {
      console.error('Error starting chat:', error);
      alert('Failed to start chat: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !websocket || connectionStatus !== 'connected') {
      return;
    }

    // Stop typing indicator
    if (isTyping) {
      websocket.send(JSON.stringify({
        type: 'typing_indicator',
        is_typing: false
      }));
      setIsTyping(false);
    }

    // Send message
    websocket.send(JSON.stringify({
      type: 'chat_message',
      content: newMessage.trim()
    }));

    setNewMessage('');
  };

  const handleTyping = () => {
    if (!websocket || connectionStatus !== 'connected') return;

    if (!isTyping) {
      setIsTyping(true);
      websocket.send(JSON.stringify({
        type: 'typing_indicator',
        is_typing: true
      }));
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      if (websocket && isTyping) {
        websocket.send(JSON.stringify({
          type: 'typing_indicator',
          is_typing: false
        }));
        setIsTyping(false);
      }
    }, 2000);
  };

  const switchToSession = (sessionId) => {
    // Close current WebSocket
    if (websocket) {
      websocket.close();
    }

    setActiveChatId(sessionId);
    setMessages([]);
    setOtherTyping(new Set());

    // Connect to new session
    connectWebSocket(sessionId);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Live Chat Support</h2>
          <p className="text-gray-600">Get instant help from our support team with real-time messaging</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              connectionStatus === 'connected' ? 'bg-green-500' : 
              connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-600 capitalize">{connectionStatus}</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${agentStatus === 'online' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            <span className="text-sm text-gray-600">Agent {agentStatus}</span>
          </div>
        </div>
      </div>

      {/* Enhanced Chat Interface */}
      <div className="bg-white shadow rounded-lg overflow-hidden" style={{height: '700px'}}>
        <div className="flex h-full">
          {/* Chat Sessions Sidebar */}
          <div className="w-1/3 border-r border-gray-200 bg-gray-50">
            <div className="p-4 border-b border-gray-200">
              <button
                onClick={startNewChat}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Starting...
                  </>
                ) : (
                  <>
                    <span className="mr-2">💬</span>
                    Start New Chat
                  </>
                )}
              </button>
            </div>
            
            <div className="p-4 max-h-full overflow-y-auto">
              {chatSessions.length > 0 ? (
                <div className="space-y-2">
                  {chatSessions.map((session, index) => (
                    <div
                      key={session.session_id || index}
                      onClick={() => switchToSession(session.session_id)}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        activeChatId === session.session_id 
                          ? 'bg-blue-100 border-blue-500 border shadow-sm' 
                          : 'bg-white hover:bg-gray-100 hover:shadow-sm'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-sm">Chat Session</p>
                          <p className="text-xs text-gray-600">
                            {session.status ? `Status: ${session.status}` : 'Active'} •{' '}
                            {session.started_at ? new Date(session.started_at).toLocaleTimeString() : 'Now'}
                          </p>
                        </div>
                        {activeChatId === session.session_id && connectionStatus === 'connected' && (
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">💬</div>
                  <p className="text-gray-500 text-sm">No active chats</p>
                  <p className="text-gray-400 text-xs mt-2">Click "Start New Chat" to begin</p>
                </div>
              )}
            </div>
          </div>

          {/* Enhanced Chat Messages Area */}
          <div className="flex-1 flex flex-col">
            {activeChatId ? (
              <>
                {/* Chat Header */}
                <div className="border-b border-gray-200 p-4 bg-white">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold text-gray-900">Chat Session</h3>
                      <p className="text-sm text-gray-500">
                        {agentStatus === 'online' ? 'Agent available' : 'Waiting for agent...'}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span className={connectionStatus === 'connected' ? 'text-green-600' : 'text-red-600'}>
                        ● {connectionStatus}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
                  {messages.length > 0 ? (
                    <div className="space-y-4">
                      {messages.map((msg, index) => (
                        <div
                          key={msg.message_id || index}
                          className={`flex ${
                            msg.sender_type === 'customer' || msg.sender_type === 'user_message' 
                              ? 'justify-end' 
                              : 'justify-start'
                          }`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow-sm ${
                              msg.sender_type === 'customer' || msg.sender_type === 'user_message'
                                ? 'bg-blue-600 text-white'
                                : msg.sender_type === 'agent' || msg.sender_type === 'agent_message'
                                ? 'bg-white text-gray-800 border border-gray-200'
                                : msg.sender_type === 'system'
                                ? 'bg-yellow-50 text-yellow-800 border border-yellow-200'
                                : 'bg-purple-50 text-purple-800 border border-purple-200'
                            }`}
                          >
                            <p className="text-sm">{msg.content}</p>
                            <div className="flex justify-between items-center mt-1">
                              <p className="text-xs opacity-75">
                                {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : 'Now'}
                              </p>
                              {msg.ai_sentiment && (
                                <span className={`text-xs px-1 py-0.5 rounded ${
                                  msg.ai_sentiment === 'positive' ? 'bg-green-100 text-green-600' :
                                  msg.ai_sentiment === 'negative' ? 'bg-red-100 text-red-600' :
                                  'bg-gray-100 text-gray-600'
                                }`}>
                                  {msg.ai_sentiment}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {/* Typing Indicators */}
                      {otherTyping.size > 0 && (
                        <div className="flex justify-start">
                          <div className="bg-white border border-gray-200 px-4 py-2 rounded-lg shadow-sm">
                            <div className="flex items-center space-x-2">
                              <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                              </div>
                              <span className="text-xs text-gray-500">Agent is typing...</span>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      <div ref={messagesEndRef} />
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="text-4xl mb-4">👋</div>
                      <p className="text-gray-500">Start the conversation...</p>
                      <p className="text-gray-400 text-sm mt-2">Your messages will appear here</p>
                    </div>
                  )}
                </div>

                {/* Enhanced Message Input */}
                <div className="border-t border-gray-200 p-4 bg-white">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => {
                        setNewMessage(e.target.value);
                        handleTyping();
                      }}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder={connectionStatus === 'connected' ? "Type your message..." : "Connecting..."}
                      disabled={connectionStatus !== 'connected'}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          sendMessage();
                        }
                      }}
                    />
                    <button 
                      onClick={sendMessage}
                      disabled={!newMessage.trim() || connectionStatus !== 'connected'}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-md font-medium transition-colors"
                    >
                      Send
                    </button>
                  </div>
                  {connectionStatus !== 'connected' && (
                    <p className="text-xs text-gray-500 mt-2">
                      {connectionStatus === 'connecting' ? 'Connecting to chat...' : 'Chat disconnected. Please refresh to reconnect.'}
                    </p>
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <div className="text-6xl mb-4">💬</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Welcome to Live Chat</h3>
                  <p className="text-gray-500 mb-4">Select a chat or start a new conversation to begin</p>
                  <button
                    onClick={startNewChat}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-md font-medium"
                  >
                    {loading ? 'Starting...' : 'Start New Chat'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Knowledge Base Tab
const KnowledgeBaseTab = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      
      const response = await axios.get(`${API}/support/knowledge-base/articles?${params}`);
      setArticles(response.data.articles || []);
    } catch (error) {
      console.error('Error fetching articles:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, [searchQuery]);

  const viewArticle = async (articleId) => {
    try {
      const response = await axios.get(`${API}/support/knowledge-base/articles/${articleId}`);
      setSelectedArticle(response.data);
    } catch (error) {
      console.error('Error fetching article:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Knowledge Base</h2>
        <p className="text-gray-600">Self-service documentation, guides, and tutorials</p>
      </div>

      {/* Search */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex space-x-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Search knowledge base..."
          />
          <button
            onClick={fetchArticles}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
          >
            Search
          </button>
        </div>
      </div>

      {/* Article View or List */}
      {selectedArticle ? (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{selectedArticle.title}</h3>
              <div className="flex items-center space-x-4 mt-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {selectedArticle.article_type?.replace('_', ' ').toUpperCase()}
                </span>
                <span className="text-sm text-gray-500">
                  Views: {selectedArticle.view_count}
                </span>
                <span className="text-sm text-gray-500">
                  👍 {selectedArticle.helpful_votes}
                </span>
              </div>
            </div>
            <button
              onClick={() => setSelectedArticle(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap">{selectedArticle.content}</div>
          </div>
          
          {selectedArticle.tags?.length > 0 && (
            <div className="mt-6 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Tags:</p>
              <div className="flex flex-wrap gap-2">
                {selectedArticle.tags.map((tag, index) => (
                  <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Articles</h3>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading articles...</p>
            </div>
          ) : articles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {articles.map((article, index) => (
                <div
                  key={index}
                  onClick={() => viewArticle(article.article_id)}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
                >
                  <h4 className="font-medium text-gray-900 mb-2">{article.title}</h4>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-3">
                    {article.ai_summary || article.content?.substring(0, 150) + '...'}
                  </p>
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <span>{article.article_type?.replace('_', ' ')}</span>
                    <span>👍 {article.helpful_votes}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">📚</div>
              <p className="text-gray-500 mb-4">No articles found</p>
              <p className="text-sm text-gray-400">
                Try searching with different keywords
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// DAO Arbitration Tab
const DAOArbitrationTab = () => {
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const fetchDisputes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/support/dao/disputes`);
      setDisputes(response.data || []);
    } catch (error) {
      console.error('Error fetching disputes:', error);
      if (error.response?.status === 401) {
        setDisputes([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDisputes();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">DAO Arbitration</h2>
          <p className="text-gray-600">Smart contract disputes and community-governed resolution</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium"
        >
          Create Dispute
        </button>
      </div>

      {/* DAO Integration Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">DAO Integration Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">✅</div>
            <p className="font-medium text-gray-900">DAO Connected</p>
            <p className="text-sm text-gray-600">Smart contracts active</p>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">7</div>
            <p className="font-medium text-gray-900">Voting Period</p>
            <p className="text-sm text-gray-600">Days for resolution</p>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">60%</div>
            <p className="font-medium text-gray-900">Approval Threshold</p>
            <p className="text-sm text-gray-600">Required for resolution</p>
          </div>
        </div>
      </div>

      {/* Disputes List */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Disputes</h3>
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading disputes...</p>
          </div>
        ) : disputes.length > 0 ? (
          <div className="space-y-4">
            {disputes.map((dispute, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900">{dispute.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{dispute.description}</p>
                    <div className="flex items-center space-x-4 mt-3">
                      <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-medium">
                        {dispute.dispute_type?.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        Created: {dispute.created_at ? new Date(dispute.created_at).toLocaleDateString() : 'N/A'}
                      </span>
                      {dispute.voting_ends_at && (
                        <span className="text-xs text-gray-500">
                          Voting ends: {new Date(dispute.voting_ends_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <button className="text-blue-600 hover:text-blue-800 text-sm">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">⚖️</div>
            <p className="text-gray-500 mb-4">No disputes submitted</p>
            <p className="text-sm text-gray-400">
              Create a dispute for community arbitration
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SupportSystemDashboard;