import React, { useState, useEffect } from 'react';

// Get API URL from environment
const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// ===== ENHANCED EDIT LABEL MODAL WITH PHASE 2 IMPROVEMENTS =====

export const EnhancedEditLabelModal = ({ label, onClose, onUpdate }) => {
  const [formData, setFormData] = useState({
    name: label.name || '',
    legal_name: '',
    genres: (label.genre_focus || []).join(', '),
    integration: label.integration_type || '',
    label_type: label.label_type || '',
    status: label.status || 'active',
    owner: '',
    headquarters: '',
    tax_status: 'corporation',
    jurisdiction: label.territory || 'US',
    social_media_handles: {
      instagram: '',
      twitter: '',
      facebook: '',
      youtube: ''
    }
  });
  
  const [initialFormData, setInitialFormData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [showAuditTrail, setShowAuditTrail] = useState(false);
  const [auditTrail, setAuditTrail] = useState([]);
  const [activeTab, setActiveTab] = useState('basic'); // basic, social, advanced

  // Fetch complete label details
  useEffect(() => {
    const fetchLabelDetails = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API}/api/uln/labels/${label.global_id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.label) {
            const labelData = data.label;
            
            // Get owner from associated_entities
            const ownerEntity = labelData.associated_entities?.find(
              e => e.entity_type === 'owner' || e.role === 'Owner'
            );
            
            const updatedFormData = {
              name: labelData.metadata_profile?.name || label.name,
              legal_name: labelData.metadata_profile?.legal_name || '',
              genres: (labelData.metadata_profile?.genre_specialization || label.genre_focus || []).join(', '),
              integration: labelData.integration_type || '',
              label_type: labelData.label_type || '',
              status: labelData.status || 'active',
              owner: ownerEntity?.name || '',
              headquarters: labelData.metadata_profile?.headquarters || '',
              tax_status: labelData.metadata_profile?.tax_status || 'corporation',
              jurisdiction: labelData.metadata_profile?.jurisdiction || label.territory || 'US',
              social_media_handles: labelData.metadata_profile?.social_media_handles || {
                instagram: '',
                twitter: '',
                facebook: '',
                youtube: ''
              }
            };
            
            setFormData(updatedFormData);
            setInitialFormData(JSON.parse(JSON.stringify(updatedFormData)));
          }
        }
      } catch (error) {
        console.error('Error fetching label details:', error);
      }
    };
    
    fetchLabelDetails();
  }, [label.global_id]);

  // Fetch audit trail
  useEffect(() => {
    if (showAuditTrail) {
      fetchAuditTrail();
    }
  }, [showAuditTrail]);

  const fetchAuditTrail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/uln/audit/trail?resource_id=${label.global_id}&limit=10`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAuditTrail(data.audit_entries || []);
        }
      }
    } catch (error) {
      console.error('Error fetching audit trail:', error);
    }
  };

  // Detect unsaved changes
  useEffect(() => {
    if (initialFormData) {
      const hasChanges = JSON.stringify(formData) !== JSON.stringify(initialFormData);
      setHasUnsavedChanges(hasChanges);
    }
  }, [formData, initialFormData]);

  // Field-level validation
  const validateField = (name, value) => {
    let errorMessage = '';
    
    switch (name) {
      case 'name':
        if (!value || value.trim().length === 0) {
          errorMessage = 'Label name is required';
        } else if (value.length < 2) {
          errorMessage = 'Label name must be at least 2 characters';
        } else if (value.length > 100) {
          errorMessage = 'Label name must be less than 100 characters';
        }
        break;
      case 'legal_name':
        if (value && value.length > 150) {
          errorMessage = 'Legal name must be less than 150 characters';
        }
        break;
      case 'genres':
        if (value) {
          const genreArray = value.split(',').map(g => g.trim()).filter(g => g);
          if (genreArray.length > 10) {
            errorMessage = 'Maximum 10 genres allowed';
          }
        }
        break;
      default:
        break;
    }
    
    setFieldErrors(prev => ({
      ...prev,
      [name]: errorMessage
    }));
    
    return errorMessage === '';
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({...prev, [name]: value}));
    validateField(name, value);
  };

  const handleSocialMediaChange = (platform, value) => {
    setFormData(prev => ({
      ...prev,
      social_media_handles: {
        ...prev.social_media_handles,
        [platform]: value
      }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate all fields
    const isNameValid = validateField('name', formData.name);
    const isLegalNameValid = validateField('legal_name', formData.legal_name);
    const isGenresValid = validateField('genres', formData.genres);
    
    if (!isNameValid || !isLegalNameValid || !isGenresValid) {
      setError('Please fix validation errors before submitting');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      
      // Prepare update data with only changed fields
      const updateData = {};
      
      if (formData.name !== initialFormData.name) {
        updateData.name = formData.name;
      }
      if (formData.legal_name !== initialFormData.legal_name) {
        updateData.legal_name = formData.legal_name;
      }
      if (formData.genres !== initialFormData.genres) {
        updateData.genres = formData.genres.split(',').map(g => g.trim()).filter(g => g);
      }
      if (formData.integration !== initialFormData.integration) {
        updateData.integration = formData.integration;
      }
      if (formData.label_type !== initialFormData.label_type) {
        updateData.label_type = formData.label_type;
      }
      if (formData.status !== initialFormData.status) {
        updateData.status = formData.status;
      }
      if (formData.owner !== initialFormData.owner) {
        updateData.owner = formData.owner;
      }
      if (formData.headquarters !== initialFormData.headquarters) {
        updateData.headquarters = formData.headquarters;
      }
      if (formData.tax_status !== initialFormData.tax_status) {
        updateData.tax_status = formData.tax_status;
      }
      if (formData.jurisdiction !== initialFormData.jurisdiction) {
        updateData.jurisdiction = formData.jurisdiction;
      }
      if (JSON.stringify(formData.social_media_handles) !== JSON.stringify(initialFormData.social_media_handles)) {
        updateData.social_media_handles = formData.social_media_handles;
      }

      if (Object.keys(updateData).length === 0) {
        setError('No changes to save');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/uln/labels/${label.global_id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setSuccess('✅ Label updated successfully!');
        setHasUnsavedChanges(false);
        // Show toast notification
        showToast('Label updated successfully!', 'success');
        setTimeout(() => {
          onUpdate();
        }, 1500);
      } else {
        setError(data.error || data.detail || 'Failed to update label');
        showToast(data.error || 'Failed to update label', 'error');
      }
    } catch (error) {
      console.error('Error updating label:', error);
      setError('Network error. Please try again.');
      showToast('Network error. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (hasUnsavedChanges) {
      const confirmClose = window.confirm('You have unsaved changes. Are you sure you want to close?');
      if (!confirmClose) return;
    }
    onClose();
  };

  // Toast notification helper
  const showToast = (message, type) => {
    // This could be replaced with a proper toast library
    console.log(`[${type.toUpperCase()}] ${message}`);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-purple-600 text-white px-6 py-4 rounded-t-lg flex justify-between items-center sticky top-0 z-10">
          <div>
            <h2 className="text-xl font-bold">✏️ Edit Label</h2>
            {hasUnsavedChanges && (
              <p className="text-xs text-yellow-200 mt-1">⚠️ You have unsaved changes</p>
            )}
          </div>
          <button 
            onClick={handleClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
            title="Close"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="bg-gray-100 px-6 py-3 flex space-x-4 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('basic')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'basic' ? 'bg-purple-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-200'
            }`}
          >
            📋 Basic Info
          </button>
          <button
            onClick={() => setActiveTab('social')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'social' ? 'bg-purple-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-200'
            }`}
          >
            📱 Social Media
          </button>
          <button
            onClick={() => setActiveTab('advanced')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'advanced' ? 'bg-purple-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-200'
            }`}
          >
            ⚙️ Advanced
          </button>
          <button
            onClick={() => setShowAuditTrail(!showAuditTrail)}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              showAuditTrail ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-200'
            }`}
          >
            📜 History
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Basic Info Tab */}
          {activeTab === 'basic' && (
            <div className="space-y-4">
              {/* Label Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Label Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                    fieldErrors.name 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:ring-purple-500'
                  }`}
                  placeholder="Enter label name"
                  required
                />
                {fieldErrors.name && (
                  <p className="text-xs text-red-500 mt-1">❌ {fieldErrors.name}</p>
                )}
              </div>

              {/* Legal Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Legal Name
                </label>
                <input
                  type="text"
                  name="legal_name"
                  value={formData.legal_name}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                    fieldErrors.legal_name 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:ring-purple-500'
                  }`}
                  placeholder="Enter legal name"
                />
                {fieldErrors.legal_name && (
                  <p className="text-xs text-red-500 mt-1">❌ {fieldErrors.legal_name}</p>
                )}
              </div>

              {/* Two-column layout for Label Type and Status */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Label Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Label Type
                  </label>
                  <select
                    name="label_type"
                    value={formData.label_type}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="major">Major Label</option>
                    <option value="independent">Independent Label</option>
                    <option value="distribution">Distribution Label</option>
                    <option value="publishing">Publishing Label</option>
                    <option value="management">Management Label</option>
                  </select>
                </div>

                {/* Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="pending">Pending</option>
                    <option value="suspended">Suspended</option>
                  </select>
                </div>
              </div>

              {/* Genres */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Music Genres
                </label>
                <input
                  type="text"
                  name="genres"
                  value={formData.genres}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                    fieldErrors.genres 
                      ? 'border-red-500 focus:ring-red-500' 
                      : 'border-gray-300 focus:ring-purple-500'
                  }`}
                  placeholder="e.g., Hip-Hop, R&B, Rap (comma-separated)"
                />
                <p className="text-xs text-gray-500 mt-1">Separate multiple genres with commas (max 10)</p>
                {fieldErrors.genres && (
                  <p className="text-xs text-red-500 mt-1">❌ {fieldErrors.genres}</p>
                )}
              </div>

              {/* Two-column layout for Integration and Jurisdiction */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Integration Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Integration Type
                  </label>
                  <select
                    name="integration"
                    value={formData.integration}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="full_integration">Full Integration</option>
                    <option value="api_partner">API Partner</option>
                    <option value="distribution_only">Distribution Only</option>
                    <option value="metadata_sync">Metadata Sync</option>
                    <option value="content_sharing">Content Sharing</option>
                  </select>
                </div>

                {/* Jurisdiction */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Territory/Jurisdiction
                  </label>
                  <select
                    name="jurisdiction"
                    value={formData.jurisdiction}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="US">United States</option>
                    <option value="UK">United Kingdom</option>
                    <option value="EU">European Union</option>
                    <option value="CA">Canada</option>
                    <option value="AU">Australia</option>
                    <option value="JP">Japan</option>
                    <option value="GLOBAL">Global</option>
                  </select>
                </div>
              </div>

              {/* Owner */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Owner
                </label>
                <input
                  type="text"
                  name="owner"
                  value={formData.owner}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter owner name"
                />
              </div>

              {/* Two-column layout for Headquarters and Tax Status */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Headquarters */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Headquarters
                  </label>
                  <input
                    type="text"
                    name="headquarters"
                    value={formData.headquarters}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="Enter headquarters location"
                  />
                </div>

                {/* Tax Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tax Status
                  </label>
                  <select
                    name="tax_status"
                    value={formData.tax_status}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="corporation">Corporation</option>
                    <option value="llc">LLC</option>
                    <option value="partnership">Partnership</option>
                    <option value="sole_proprietorship">Sole Proprietorship</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Social Media Tab */}
          {activeTab === 'social' && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800">
                  📱 Connect your social media accounts to enhance your label's presence in the network.
                </p>
              </div>

              {/* Instagram */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Instagram Handle
                </label>
                <div className="flex items-center">
                  <span className="inline-flex items-center px-3 py-2 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-l-md">
                    @
                  </span>
                  <input
                    type="text"
                    value={formData.social_media_handles.instagram}
                    onChange={(e) => handleSocialMediaChange('instagram', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-r-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="instagram_username"
                  />
                </div>
              </div>

              {/* Twitter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Twitter/X Handle
                </label>
                <div className="flex items-center">
                  <span className="inline-flex items-center px-3 py-2 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-l-md">
                    @
                  </span>
                  <input
                    type="text"
                    value={formData.social_media_handles.twitter}
                    onChange={(e) => handleSocialMediaChange('twitter', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-r-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="twitter_username"
                  />
                </div>
              </div>

              {/* Facebook */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Facebook Page
                </label>
                <div className="flex items-center">
                  <span className="inline-flex items-center px-3 py-2 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-l-md">
                    facebook.com/
                  </span>
                  <input
                    type="text"
                    value={formData.social_media_handles.facebook}
                    onChange={(e) => handleSocialMediaChange('facebook', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-r-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="page_name"
                  />
                </div>
              </div>

              {/* YouTube */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  YouTube Channel
                </label>
                <div className="flex items-center">
                  <span className="inline-flex items-center px-3 py-2 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-l-md">
                    youtube.com/@
                  </span>
                  <input
                    type="text"
                    value={formData.social_media_handles.youtube}
                    onChange={(e) => handleSocialMediaChange('youtube', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-r-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="channel_name"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Advanced Tab */}
          {activeTab === 'advanced' && (
            <div className="space-y-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-yellow-800">
                  ⚙️ Advanced settings for label configuration. Use with caution.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Label Information</h4>
                  <div className="text-sm space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Global ID:</span>
                      <span className="font-mono text-xs">{label.global_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="capitalize">{formData.label_type || label.label_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        formData.status === 'active' ? 'bg-green-100 text-green-800' : 
                        formData.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {formData.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Network Stats</h4>
                  <div className="text-sm space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Content:</span>
                      <span>{label.content_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Shared:</span>
                      <span>{label.shared_content_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Monthly Revenue:</span>
                      <span>${(label.monthly_revenue || 0).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Features</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <span>{label.blockchain_enabled ? '✅' : '❌'}</span>
                    <span>Blockchain Enabled</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>{label.dao_affiliated ? '✅' : '❌'}</span>
                    <span>DAO Affiliated</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>{label.compliance_status === 'verified' ? '✅' : '❌'}</span>
                    <span>Compliance Verified</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span>{label.verification_status === 'verified' ? '✅' : '❌'}</span>
                    <span>Identity Verified</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Audit Trail Panel */}
          {showAuditTrail && (
            <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
              <h3 className="font-medium text-gray-900 mb-3 flex items-center">
                <span className="mr-2">📜</span>
                Edit History (Last 10 Changes)
              </h3>
              {auditTrail.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">No edit history available</p>
              ) : (
                <div className="space-y-2">
                  {auditTrail.map((entry, index) => (
                    <div key={index} className="bg-white rounded border border-gray-200 p-3 text-sm">
                      <div className="flex items-start justify-between mb-1">
                        <span className="font-medium text-gray-900">{entry.action_description}</span>
                        <span className="text-xs text-gray-500">
                          {new Date(entry.timestamp).toLocaleString()}
                        </span>
                      </div>
                      {entry.changes_made && Object.keys(entry.changes_made).length > 0 && (
                        <div className="mt-2 text-xs text-gray-600">
                          <span className="font-medium">Changed fields:</span>{' '}
                          {Object.keys(entry.changes_made).join(', ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              ❌ {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="mt-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}

          {/* Footer Actions */}
          <div className="mt-6 flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              disabled={loading || !hasUnsavedChanges || Object.values(fieldErrors).some(err => err !== '')}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <span>💾</span>
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
