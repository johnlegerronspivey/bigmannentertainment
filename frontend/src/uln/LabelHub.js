import React, { useState, useEffect } from 'react';
import { EnhancedEditLabelModal } from '../EnhancedULNComponents';
import { BulkLabelEditor, AdvancedSearch, LabelDataExporter } from '../ULNAdminComponents';

const API = process.env.REACT_APP_BACKEND_URL;

const LabelHubCard = ({ label, onEdit }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getVerificationIcon = (status) => {
    switch (status) {
      case 'verified': return '✅';
      case 'pending': return '⏳';
      case 'rejected': return '❌';
      default: return '❓';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow p-6 border-l-4 border-purple-500">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{label.name}</h3>
          <div className="flex items-center space-x-2 mt-1">
            <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
              label.label_type === 'major' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {label.label_type}
            </span>
            <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(label.status)}`}>
              {label.status}
            </span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className="text-2xl">
            {label.label_type === 'major' ? '🏢' : 
             label.label_type === 'independent' ? '🎵' :
             label.label_type === 'distribution' ? '📦' : '🎼'}
          </div>
          <button
            onClick={() => onEdit(label)}
            className="text-purple-600 hover:text-purple-800 transition-colors"
            title="Edit Label"
          >
            ✏️
          </button>
        </div>
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        <div className="flex items-center justify-between">
          <span className="font-medium">Territory:</span>
          <span>{label.territory}</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="font-medium">Integration:</span>
          <span className="capitalize">{label.integration_type.replace('_', ' ')}</span>
        </div>

        {label.genre_focus && label.genre_focus.length > 0 && (
          <div className="flex items-center justify-between">
            <span className="font-medium">Genres:</span>
            <span className="text-xs">{label.genre_focus.slice(0, 2).join(', ')}</span>
          </div>
        )}

        <div className="flex items-center justify-between">
          <span className="font-medium">Verification:</span>
          <span>{getVerificationIcon(label.verification_status)} {label.verification_status}</span>
        </div>
      </div>

      {/* Features */}
      <div className="mt-4 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          {label.blockchain_enabled && <span className="text-purple-600" title="Blockchain Enabled">⛓️</span>}
          {label.dao_affiliated && <span className="text-blue-600" title="DAO Affiliated">🗳️</span>}
          {label.compliance_status === 'verified' && <span className="text-green-600" title="Compliance Verified">✅</span>}
        </div>
        <div className="text-gray-500">
          ID: {label.global_id.slice(-8)}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center text-xs">
          <div>
            <div className="font-bold text-gray-900">{label.content_count || 0}</div>
            <div className="text-gray-500">Content</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">{label.shared_content_count || 0}</div>
            <div className="text-gray-500">Shared</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">${(label.monthly_revenue || 0).toLocaleString()}</div>
            <div className="text-gray-500">Monthly</div>
          </div>
        </div>
      </div>

      {/* Major Label Additional Info */}
      {label.label_type === 'major' && (
        <div className="mt-3 pt-3 border-t border-purple-200">
          <div className="flex items-center justify-between text-xs">
            <span className="text-purple-600 font-medium">🌟 Major Label Network</span>
            <span className="text-purple-500">Premium Tier</span>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Full ULN integration • Smart contracts • DAO governance
          </div>
        </div>
      )}

      {/* Independent Label Additional Info */}
      {label.label_type === 'independent' && (
        <div className="mt-3 pt-3 border-t border-blue-200">
          <div className="flex items-center justify-between text-xs">
            <span className="text-blue-600 font-medium">🎶 Independent Spirit</span>
            <span className="text-blue-500">API Partner</span>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            Creative freedom • Direct artist relationships • Innovation focus
          </div>
        </div>
      )}
    </div>
  );
};

const EditLabelModal = ({ label, onClose, onUpdate }) => {
  const [formData, setFormData] = useState({
    name: label.name || '',
    legal_name: label.metadata_profile?.legal_name || '',
    genres: (label.genre_focus || []).join(', '),
    integration: label.integration_type || '',
    owner: '',
    headquarters: label.metadata_profile?.headquarters || '',
    tax_status: label.metadata_profile?.tax_status || 'corporation'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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
            const ownerEntity = data.label.associated_entities?.find(
              e => e.entity_type === 'owner' || e.role === 'Owner'
            );
            if (ownerEntity) {
              setFormData(prev => ({...prev, owner: ownerEntity.name}));
            }
          }
        }
      } catch (error) {
        console.error('Error fetching label details:', error);
      }
    };
    fetchLabelDetails();
  }, [label.global_id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({...prev, [name]: value}));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      
      const updateData = {};
      
      if (formData.name !== label.name) {
        updateData.name = formData.name;
      }
      if (formData.legal_name) {
        updateData.legal_name = formData.legal_name;
      }
      if (formData.genres) {
        updateData.genres = formData.genres.split(',').map(g => g.trim()).filter(g => g);
      }
      if (formData.integration !== label.integration_type) {
        updateData.integration = formData.integration;
      }
      if (formData.owner) {
        updateData.owner = formData.owner;
      }
      if (formData.headquarters) {
        updateData.headquarters = formData.headquarters;
      }
      if (formData.tax_status) {
        updateData.tax_status = formData.tax_status;
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
        setTimeout(() => {
          onUpdate();
        }, 1500);
      } else {
        setError(data.error || data.detail || 'Failed to update label');
      }
    } catch (error) {
      console.error('Error updating label:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="bg-purple-600 text-white px-6 py-4 rounded-t-lg flex justify-between items-center">
          <h2 className="text-xl font-bold">✏️ Edit Label</h2>
          <button 
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Label Name</label>
            <input type="text" name="name" value={formData.name} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter label name" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Legal Name</label>
            <input type="text" name="legal_name" value={formData.legal_name} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter legal name" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Music Genres</label>
            <input type="text" name="genres" value={formData.genres} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="e.g., Hip-Hop, R&B, Rap (comma-separated)" />
            <p className="text-xs text-gray-500 mt-1">Separate multiple genres with commas</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Integration Type</label>
            <select name="integration" value={formData.integration} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
              <option value="full_integration">Full Integration</option>
              <option value="api_partner">API Partner</option>
              <option value="distribution_only">Distribution Only</option>
              <option value="metadata_sync">Metadata Sync</option>
              <option value="content_sharing">Content Sharing</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Owner</label>
            <input type="text" name="owner" value={formData.owner} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter owner name" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Headquarters</label>
            <input type="text" name="headquarters" value={formData.headquarters} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter headquarters location" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tax Status</label>
            <select name="tax_status" value={formData.tax_status} onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
              <option value="corporation">Corporation</option>
              <option value="llc">LLC</option>
              <option value="partnership">Partnership</option>
              <option value="sole_proprietorship">Sole Proprietorship</option>
            </select>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
          )}
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">{success}</div>
          )}

          <div className="flex space-x-3 pt-4">
            <button type="submit" disabled={loading}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? '⏳ Saving...' : '💾 Save Changes'}
            </button>
            <button type="button" onClick={onClose} disabled={loading}
              className="flex-1 bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export const LabelHub = () => {
  const [labelHubData, setLabelHubData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    territory: '',
    genre: '',
    dao_affiliated: null
  });
  const [initializationStatus, setInitializationStatus] = useState('');
  const [editingLabel, setEditingLabel] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showBulkEditor, setShowBulkEditor] = useState(false);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [showExporter, setShowExporter] = useState(false);
  const [selectedLabelsForBulk, setSelectedLabelsForBulk] = useState([]);

  useEffect(() => {
    fetchLabelHubData();
  }, [filters]);

  const fetchLabelHubData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const params = new URLSearchParams();
      if (filters.territory) params.append('territory', filters.territory);
      if (filters.genre) params.append('genre', filters.genre);
      if (filters.dao_affiliated !== null) params.append('dao_affiliated', filters.dao_affiliated);

      const response = await fetch(`${API}/api/uln/dashboard/label-hub?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLabelHubData(data.label_hub_entries || []);
        setError('');
      } else {
        setError('Failed to load label hub data');
      }
    } catch (error) {
      console.error('Error fetching label hub data:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const initializeMajorLabels = async () => {
    try {
      setLoading(true);
      setInitializationStatus('Initializing major labels...');
      
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/uln/initialize-major-labels`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setInitializationStatus(`✅ Success! ${data.message}`);
        if (data.statistics) {
          setInitializationStatus(
            `✅ Successfully initialized ${data.statistics.total_initialized} labels ` +
            `(${data.statistics.major_labels} major, ${data.statistics.independent_labels} independent)`
          );
        }
        
        setTimeout(() => {
          fetchLabelHubData();
          setInitializationStatus('');
        }, 3000);
        
      } else {
        setInitializationStatus(`❌ Error: ${data.error || 'Failed to initialize labels'}`);
        setTimeout(() => setInitializationStatus(''), 5000);
      }
    } catch (error) {
      console.error('Error initializing major labels:', error);
      setInitializationStatus('❌ Network error. Please try again.');
      setTimeout(() => setInitializationStatus(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleEditLabel = (label) => {
    setEditingLabel(label);
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setEditingLabel(null);
  };

  const handleLabelUpdated = () => {
    fetchLabelHubData();
    handleCloseEditModal();
  };

  if (loading) {
    return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold">🏢 Label Hub</h2>
          <p className="text-gray-600">Connected labels in the Unified Label Network</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={() => setShowAdvancedSearch(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-1"
          >
            <span>🔍</span>
            <span>Advanced Search</span>
          </button>
          <button 
            onClick={() => {
              setSelectedLabelsForBulk(labelHubData);
              setShowBulkEditor(true);
            }}
            disabled={labelHubData.length === 0}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-1"
          >
            <span>📦</span>
            <span>Bulk Edit</span>
          </button>
          <button 
            onClick={() => setShowExporter(true)}
            disabled={labelHubData.length === 0}
            className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-1"
          >
            <span>📤</span>
            <span>Export</span>
          </button>
          <button 
            onClick={initializeMajorLabels}
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-1"
          >
            <span>🏢</span>
            <span className="hidden sm:inline">Initialize Labels</span>
          </button>
          <button 
            onClick={() => window.location.href = '/uln/register'}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-1"
          >
            <span>+</span>
            <span>Register</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            value={filters.territory}
            onChange={(e) => setFilters({...filters, territory: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Territories</option>
            <option value="US">United States</option>
            <option value="UK">United Kingdom</option>
            <option value="EU">European Union</option>
            <option value="CA">Canada</option>
            <option value="AU">Australia</option>
            <option value="JP">Japan</option>
          </select>
          
          <input
            type="text"
            placeholder="Filter by genre..."
            value={filters.genre}
            onChange={(e) => setFilters({...filters, genre: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <select
            value={filters.dao_affiliated === null ? '' : filters.dao_affiliated.toString()}
            onChange={(e) => setFilters({...filters, dao_affiliated: e.target.value === '' ? null : e.target.value === 'true'})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Labels</option>
            <option value="true">DAO Affiliated</option>
            <option value="false">Non-DAO</option>
          </select>

          <button
            onClick={() => setFilters({territory: '', genre: '', dao_affiliated: null})}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
      )}

      {initializationStatus && (
        <div className={`px-4 py-3 rounded ${
          initializationStatus.includes('✅') 
            ? 'bg-green-100 border border-green-400 text-green-700' 
            : initializationStatus.includes('❌')
            ? 'bg-red-100 border border-red-400 text-red-700'
            : 'bg-blue-100 border border-blue-400 text-blue-700'
        }`}>
          {initializationStatus}
        </div>
      )}

      {/* Labels Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {labelHubData.map((label) => (
          <LabelHubCard key={label.global_id} label={label} onEdit={handleEditLabel} />
        ))}
      </div>

      {labelHubData.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No labels found matching your criteria</div>
          <p className="text-gray-400 mt-2">Try adjusting your filters or register a new label</p>
        </div>
      )}

      {showEditModal && editingLabel && (
        <EnhancedEditLabelModal
          label={editingLabel}
          onClose={handleCloseEditModal}
          onUpdate={handleLabelUpdated}
        />
      )}

      {showBulkEditor && (
        <BulkLabelEditor
          labels={selectedLabelsForBulk}
          onClose={() => setShowBulkEditor(false)}
          onUpdate={() => {
            fetchLabelHubData();
            setShowBulkEditor(false);
          }}
        />
      )}

      {showAdvancedSearch && (
        <AdvancedSearch
          onSearch={(criteria) => {
            console.log('Search criteria:', criteria);
            setFilters(prev => ({ ...prev, ...criteria }));
            setShowAdvancedSearch(false);
          }}
          onClose={() => setShowAdvancedSearch(false)}
        />
      )}

      {showExporter && (
        <LabelDataExporter
          labels={labelHubData}
          onClose={() => setShowExporter(false)}
        />
      )}
    </div>
  );
};
