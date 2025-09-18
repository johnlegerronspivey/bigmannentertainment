import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Main Content Removal Dashboard
const ContentRemovalDashboard = () => {
  const [activeTab, setActiveTab] = useState('requests');
  const [userRole, setUserRole] = useState('creator');

  useEffect(() => {
    // Get user role from token or API
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUserRole(payload.role || 'creator');
      } catch (e) {
        console.error('Failed to parse token:', e);
      }
    }
  }, []);

  const tabs = [
    { id: 'requests', label: 'My Requests', icon: '📋' },
    { id: 'create', label: 'New Request', icon: '➕' },
    ...(userRole === 'admin' || userRole === 'super_admin' ? [
      { id: 'admin', label: 'Admin Panel', icon: '⚙️' },
      { id: 'analytics', label: 'Analytics', icon: '📊' }
    ] : []),
    { id: 'dao', label: 'DAO Governance', icon: '🗳️' },
    { id: 'platforms', label: 'Platforms', icon: '🌐' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Content Removal Management</h1>
          <p className="text-gray-600">Manage content takedown requests across all distribution platforms</p>
        </div>

        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
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
        <div className="bg-white rounded-lg shadow-sm min-h-96">
          {activeTab === 'requests' && <RemovalRequestsList />}
          {activeTab === 'create' && <CreateRemovalRequest />}
          {activeTab === 'admin' && (userRole === 'admin' || userRole === 'super_admin') && <AdminPanel />}
          {activeTab === 'analytics' && (userRole === 'admin' || userRole === 'super_admin') && <AnalyticsDashboard />}
          {activeTab === 'dao' && <DAOGovernance />}
          {activeTab === 'platforms' && <SupportedPlatforms />}
        </div>
      </div>
    </div>
  );
};

// Create New Removal Request Component
const CreateRemovalRequest = () => {
  const [formData, setFormData] = useState({
    content_id: '',
    reason: 'rights_revoked',
    urgency: 'medium',
    description: '',
    target_platforms: [],
    territory_scope: 'worldwide',
    effective_date: '',
    legal_notice_ref: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [platforms, setPlatforms] = useState([]);

  useEffect(() => {
    fetchSupportedPlatforms();
  }, []);

  const fetchSupportedPlatforms = async () => {
    try {
      const response = await axios.get(`${API}/api/content-removal/platforms`);
      setPlatforms(response.data.platforms);
    } catch (error) {
      console.error('Failed to fetch platforms:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      const requestData = {
        ...formData,
        effective_date: formData.effective_date ? new Date(formData.effective_date).toISOString() : null
      };

      const response = await axios.post(
        `${API}/api/content-removal/requests`,
        requestData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setMessage('Removal request created successfully!');
      setFormData({
        content_id: '',
        reason: 'rights_revoked',
        urgency: 'medium',
        description: '',
        target_platforms: [],
        territory_scope: 'worldwide',
        effective_date: '',
        legal_notice_ref: ''
      });
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create removal request');
    }

    setLoading(false);
  };

  const handlePlatformToggle = (platformId) => {
    setFormData(prev => ({
      ...prev,
      target_platforms: prev.target_platforms.includes(platformId)
        ? prev.target_platforms.filter(id => id !== platformId)
        : [...prev.target_platforms, platformId]
    }));
  };

  const reasons = [
    { value: 'rights_revoked', label: 'Rights Revoked' },
    { value: 'licensing_expired', label: 'Licensing Expired' },
    { value: 'copyright_dispute', label: 'Copyright Dispute' },
    { value: 'takedown_request', label: 'DMCA Takedown Request' },
    { value: 'compliance_violation', label: 'Compliance Violation' },
    { value: 'artist_request', label: 'Artist Request' },
    { value: 'admin_action', label: 'Administrative Action' }
  ];

  const urgencyLevels = [
    { value: 'low', label: 'Low Priority' },
    { value: 'medium', label: 'Medium Priority' },
    { value: 'high', label: 'High Priority' },
    { value: 'urgent', label: 'Urgent' },
    { value: 'legal', label: 'Legal (24h)' }
  ];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Removal Request</h2>

      {message && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {message}
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Content Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Content Information</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content ID *
              </label>
              <input
                type="text"
                required
                value={formData.content_id}
                onChange={(e) => setFormData({...formData, content_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter content/release ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Legal Notice Reference
              </label>
              <input
                type="text"
                value={formData.legal_notice_ref}
                onChange={(e) => setFormData({...formData, legal_notice_ref: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Legal notice or case reference"
              />
            </div>
          </div>
        </div>

        {/* Removal Details */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Removal Details</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reason for Removal *
              </label>
              <select
                required
                value={formData.reason}
                onChange={(e) => setFormData({...formData, reason: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {reasons.map(reason => (
                  <option key={reason.value} value={reason.value}>
                    {reason.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Urgency Level *
              </label>
              <select
                required
                value={formData.urgency}
                onChange={(e) => setFormData({...formData, urgency: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {urgencyLevels.map(level => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description *
            </label>
            <textarea
              required
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Provide detailed explanation for the removal request..."
            />
          </div>
        </div>

        {/* Scope and Timing */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Scope and Timing</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Territory Scope
              </label>
              <select
                value={formData.territory_scope}
                onChange={(e) => setFormData({...formData, territory_scope: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="worldwide">Worldwide</option>
                <option value="US">United States</option>
                <option value="EU">European Union</option>
                <option value="UK">United Kingdom</option>
                <option value="CA">Canada</option>
                <option value="AU">Australia</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Effective Date
              </label>
              <input
                type="datetime-local"
                value={formData.effective_date}
                onChange={(e) => setFormData({...formData, effective_date: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <p className="text-xs text-gray-500 mt-1">Leave empty for immediate removal</p>
            </div>
          </div>
        </div>

        {/* Platform Selection */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Target Platforms</h3>
          <p className="text-sm text-gray-600 mb-4">
            Select specific platforms or leave empty to remove from all platforms
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {platforms.map(platform => (
              <label key={platform.id} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.target_platforms.includes(platform.id)}
                  onChange={() => handlePlatformToggle(platform.id)}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">{platform.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50 flex items-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating Request...
              </>
            ) : (
              <>
                <span className="mr-2">🚨</span>
                Submit Removal Request
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

// Removal Requests List Component
const RemovalRequestsList = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const fetchRequests = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = filter !== 'all' ? { status: filter } : {};
      
      const response = await axios.get(`${API}/api/content-removal/requests`, {
        headers: { 'Authorization': `Bearer ${token}` },
        params
      });
      
      setRequests(response.data);
    } catch (error) {
      setError('Failed to fetch removal requests');
    }
    setLoading(false);
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      rejected: 'bg-gray-100 text-gray-800',
      disputed: 'bg-orange-100 text-orange-800'
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || colors.pending}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const getUrgencyBadge = (urgency) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-yellow-100 text-yellow-800',
      urgent: 'bg-orange-100 text-orange-800',
      legal: 'bg-red-100 text-red-800'
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[urgency] || colors.medium}`}>
        {urgency.toUpperCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <p className="mt-2 text-gray-600">Loading removal requests...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">My Removal Requests</h2>
        
        <div className="flex space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Requests</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="disputed">Disputed</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {requests.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No removal requests found</h3>
          <p className="text-gray-600">Create your first removal request to get started</p>
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map((request) => (
            <div key={request.id} className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-1">
                    {request.content_title || `Content ${request.content_id}`}
                  </h3>
                  <p className="text-sm text-gray-600">ID: {request.content_id}</p>
                </div>
                <div className="flex space-x-2">
                  {getStatusBadge(request.status)}
                  {getUrgencyBadge(request.urgency)}
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <span className="text-sm font-medium text-gray-700">Reason:</span>
                  <span className="ml-2 text-sm text-gray-600">
                    {request.reason.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Territory:</span>
                  <span className="ml-2 text-sm text-gray-600">{request.territory_scope}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Created:</span>
                  <span className="ml-2 text-sm text-gray-600">
                    {new Date(request.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Platforms:</span>
                  <span className="ml-2 text-sm text-gray-600">
                    {request.target_platforms.length > 0 
                      ? `${request.target_platforms.length} selected`
                      : 'All platforms'
                    }
                  </span>
                </div>
              </div>

              <div className="mb-4">
                <span className="text-sm font-medium text-gray-700">Description:</span>
                <p className="mt-1 text-sm text-gray-600">{request.description}</p>
              </div>

              {request.platform_results && request.platform_results.length > 0 && (
                <div className="mb-4">
                  <span className="text-sm font-medium text-gray-700 mb-2 block">Platform Status:</span>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {request.platform_results.map((result, index) => (
                      <div key={index} className="text-xs">
                        <span className="font-medium">{result.platform_name}:</span>
                        <span className={`ml-1 ${
                          result.status === 'completed' ? 'text-green-600' :
                          result.status === 'failed' ? 'text-red-600' :
                          result.status === 'processing' ? 'text-blue-600' :
                          'text-gray-600'
                        }`}>
                          {result.status === 'completed' ? '✅' :
                           result.status === 'failed' ? '❌' :
                           result.status === 'processing' ? '⏳' : '⏸️'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => window.open(`/content-removal/request/${request.id}`, '_blank')}
                  className="text-purple-600 hover:text-purple-800 text-sm font-medium"
                >
                  View Details →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Admin Panel Component
const AdminPanel = () => {
  const [pendingRequests, setPendingRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    fetchPendingRequests();
  }, []);

  const fetchPendingRequests = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/content-removal/requests`, {
        headers: { 'Authorization': `Bearer ${token}` },
        params: { status: 'pending' }
      });
      setPendingRequests(response.data);
    } catch (error) {
      console.error('Failed to fetch pending requests:', error);
    }
    setLoading(false);
  };

  const handleApprove = async (requestId, notes = '') => {
    setProcessingId(requestId);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      if (notes) formData.append('notes', notes);

      await axios.post(
        `${API}/api/content-removal/requests/${requestId}/approve`,
        formData,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      // Refresh list
      fetchPendingRequests();
    } catch (error) {
      console.error('Failed to approve request:', error);
    }
    setProcessingId(null);
  };

  const handleReject = async (requestId, reason) => {
    if (!reason.trim()) {
      alert('Please provide a rejection reason');
      return;
    }

    setProcessingId(requestId);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('reason', reason);

      await axios.post(
        `${API}/api/content-removal/requests/${requestId}/reject`,
        formData,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      // Refresh list
      fetchPendingRequests();
    } catch (error) {
      console.error('Failed to reject request:', error);
    }
    setProcessingId(null);
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <p className="mt-2 text-gray-600">Loading pending requests...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Admin Review Panel</h2>

      {pendingRequests.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">✅</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No pending requests</h3>
          <p className="text-gray-600">All removal requests have been reviewed</p>
        </div>
      ) : (
        <div className="space-y-6">
          {pendingRequests.map((request) => (
            <div key={request.id} className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-1">
                    {request.content_title || `Content ${request.content_id}`}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Requested by: {request.requested_by} • {new Date(request.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
                    PENDING REVIEW
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    request.urgency === 'legal' ? 'bg-red-100 text-red-800' :
                    request.urgency === 'urgent' ? 'bg-orange-100 text-orange-800' :
                    request.urgency === 'high' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {request.urgency.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <span className="text-sm font-medium text-gray-700">Reason:</span>
                  <span className="ml-2 text-sm text-gray-600">
                    {request.reason.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Territory:</span>
                  <span className="ml-2 text-sm text-gray-600">{request.territory_scope}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-700">Platforms:</span>
                  <span className="ml-2 text-sm text-gray-600">
                    {request.target_platforms.length > 0 
                      ? request.target_platforms.join(', ')
                      : 'All platforms'
                    }
                  </span>
                </div>
                {request.legal_notice_ref && (
                  <div>
                    <span className="text-sm font-medium text-gray-700">Legal Notice:</span>
                    <span className="ml-2 text-sm text-gray-600">{request.legal_notice_ref}</span>
                  </div>
                )}
              </div>

              <div className="mb-6">
                <span className="text-sm font-medium text-gray-700">Description:</span>
                <p className="mt-1 text-sm text-gray-600 bg-gray-50 p-3 rounded">
                  {request.description}
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    const reason = prompt('Please provide a reason for rejection:');
                    if (reason) handleReject(request.id, reason);
                  }}
                  disabled={processingId === request.id}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
                >
                  Reject
                </button>
                <button
                  onClick={() => {
                    const notes = prompt('Optional approval notes:');
                    handleApprove(request.id, notes || '');
                  }}
                  disabled={processingId === request.id}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-md disabled:opacity-50 flex items-center"
                >
                  {processingId === request.id ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    'Approve & Execute'
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Analytics Dashboard Component
const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30');

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const endDate = new Date();
      const startDate = new Date(endDate.getTime() - (parseInt(dateRange) * 24 * 60 * 60 * 1000));

      const response = await axios.get(`${API}/api/content-removal/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` },
        params: {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString()
        }
      });

      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <p className="mt-2 text-gray-600">Loading analytics...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Removal Analytics</h2>
        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </select>
      </div>

      {analytics && (
        <>
          {/* Overview Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-gray-900">{analytics.total_requests}</div>
              <div className="text-sm text-gray-600">Total Requests</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-green-600">{analytics.completed_requests}</div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-yellow-600">{analytics.pending_requests}</div>
              <div className="text-sm text-gray-600">Pending</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-2xl font-bold text-red-600">{analytics.disputed_requests}</div>
              <div className="text-sm text-gray-600">Disputed</div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Requests by Reason */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Requests by Reason</h3>
              <div className="space-y-3">
                {Object.entries(analytics.requests_by_reason).map(([reason, count]) => (
                  <div key={reason} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">
                      {reason.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Requests by Platform */}
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Requests by Platform</h3>
              <div className="space-y-3">
                {Object.entries(analytics.requests_by_platform).slice(0, 10).map(([platform, count]) => (
                  <div key={platform} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 capitalize">{platform}</span>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// DAO Governance Component
const DAOGovernance = () => {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    fetchDAOProposals();
  }, []);

  const fetchDAOProposals = async () => {
    try {
      const response = await axios.get(`${API}/api/content-removal/dao/proposals`);
      setProposals(response.data.proposals);
    } catch (error) {
      console.error('Failed to fetch DAO proposals:', error);
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">DAO Governance</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-md"
        >
          {showCreateForm ? 'Cancel' : 'Create Proposal'}
        </button>
      </div>

      {showCreateForm && <CreateDAOProposal onSuccess={fetchDAOProposals} />}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          <p className="mt-2 text-gray-600">Loading DAO proposals...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {proposals.map((proposal, index) => (
            <DAOProposalCard key={proposal.id || index} proposal={proposal} onVote={fetchDAOProposals} />
          ))}
        </div>
      )}
    </div>
  );
};

// Create DAO Proposal Component
const CreateDAOProposal = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    content_id: '',
    reason: '',
    description: '',
    voting_duration_hours: 72
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const data = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        data.append(key, value);
      });

      await axios.post(`${API}/api/content-removal/dao/propose-removal`, data, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      onSuccess();
      setFormData({
        content_id: '',
        reason: '',
        description: '',
        voting_duration_hours: 72
      });
    } catch (error) {
      console.error('Failed to create DAO proposal:', error);
    }
    setLoading(false);
  };

  return (
    <div className="bg-gray-50 p-4 rounded-lg mb-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Create DAO Removal Proposal</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content ID</label>
            <input
              type="text"
              required
              value={formData.content_id}
              onChange={(e) => setFormData({...formData, content_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Voting Duration (hours)</label>
            <select
              value={formData.voting_duration_hours}
              onChange={(e) => setFormData({...formData, voting_duration_hours: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value={24}>24 hours</option>
              <option value={48}>48 hours</option>
              <option value={72}>72 hours</option>
              <option value={168}>1 week</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
          <input
            type="text"
            required
            value={formData.reason}
            onChange={(e) => setFormData({...formData, reason: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Brief reason for removal"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            required
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Detailed description of why this content should be removed"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create Proposal'}
        </button>
      </form>
    </div>
  );
};

// DAO Proposal Card Component  
const DAOProposalCard = ({ proposal, onVote }) => {
  const [voting, setVoting] = useState(false);

  const handleVote = async (vote) => {
    setVoting(true);
    try {
      const token = localStorage.getItem('token');
      const data = new FormData();
      data.append('vote', vote);

      await axios.post(
        `${API}/api/content-removal/dao/proposals/${proposal.id}/vote`,
        data,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      onVote();
    } catch (error) {
      console.error('Failed to vote:', error);
      alert('Failed to submit vote');
    }
    setVoting(false);
  };

  const isVotingActive = new Date() < new Date(proposal.voting_deadline);
  const totalVotes = (proposal.votes_for || 0) + (proposal.votes_against || 0);
  const approvalRate = totalVotes > 0 ? ((proposal.votes_for || 0) / totalVotes * 100).toFixed(1) : 0;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Content: {proposal.content_id}</h3>
          <p className="text-sm text-gray-600">Proposed by: {proposal.proposed_by}</p>
        </div>
        <div className="flex space-x-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
            isVotingActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {isVotingActive ? 'VOTING ACTIVE' : 'VOTING CLOSED'}
          </span>
        </div>
      </div>

      <div className="mb-4">
        <span className="text-sm font-medium text-gray-700">Reason:</span>
        <span className="ml-2 text-sm text-gray-600">{proposal.reason}</span>
      </div>

      <div className="mb-4">
        <span className="text-sm font-medium text-gray-700">Description:</span>
        <p className="mt-1 text-sm text-gray-600">{proposal.description}</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-bold text-green-600">{proposal.votes_for || 0}</div>
          <div className="text-xs text-gray-600">Votes For</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-red-600">{proposal.votes_against || 0}</div>
          <div className="text-xs text-gray-600">Votes Against</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{approvalRate}%</div>
          <div className="text-xs text-gray-600">Approval Rate</div>
        </div>
      </div>

      {isVotingActive && (
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => handleVote('for')}
            disabled={voting}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50"
          >
            {voting ? 'Voting...' : 'Vote For'}
          </button>
          <button
            onClick={() => handleVote('against')}
            disabled={voting}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50"
          >
            {voting ? 'Voting...' : 'Vote Against'}
          </button>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500">
        Voting deadline: {new Date(proposal.voting_deadline).toLocaleString()}
      </div>
    </div>
  );
};

// Supported Platforms Component
const SupportedPlatforms = () => {
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      const response = await axios.get(`${API}/api/content-removal/platforms`);
      setPlatforms(response.data.platforms);
    } catch (error) {
      console.error('Failed to fetch platforms:', error);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <p className="mt-2 text-gray-600">Loading platforms...</p>
      </div>
    );
  }

  const platformsByType = platforms.reduce((acc, platform) => {
    if (!acc[platform.type]) acc[platform.type] = [];
    acc[platform.type].push(platform);
    return acc;
  }, {});

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Supported Platforms for Takedown</h2>
      
      <div className="mb-4">
        <div className="text-sm text-gray-600">
          <span className="font-medium">{platforms.length}</span> platforms support automated takedown
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(platformsByType).map(([type, typePlatforms]) => (
          <div key={type} className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} ({typePlatforms.length})
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {typePlatforms.map((platform) => (
                <div key={platform.id} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-900">{platform.name}</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      platform.takedown_method === 'ddex_ern' ? 'bg-blue-100 text-blue-800' :
                      platform.takedown_method === 'api_call' ? 'bg-green-100 text-green-800' :
                      platform.takedown_method === 'graph_api' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {platform.takedown_method?.replace('_', ' ').toUpperCase() || 'MANUAL'}
                    </span>
                  </div>
                  
                  <div className="text-xs text-gray-600">
                    <div>Method: {platform.takedown_method || 'Manual process'}</div>
                    {platform.takedown_method === 'ddex_ern' && (
                      <div className="mt-1 text-green-600">✓ Automated DDEX delivery</div>
                    )}
                    {platform.takedown_method === 'api_call' && (
                      <div className="mt-1 text-green-600">✓ Direct API integration</div>
                    )}
                    {platform.takedown_method === 'graph_api' && (
                      <div className="mt-1 text-green-600">✓ Facebook Graph API</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContentRemovalDashboard;