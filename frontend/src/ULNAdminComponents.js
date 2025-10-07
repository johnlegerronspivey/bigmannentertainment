import React, { useState, useEffect } from 'react';

// Get API URL from environment
const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// ===== BULK LABEL EDITING COMPONENT =====

export const BulkLabelEditor = ({ labels, onClose, onUpdate }) => {
  const [selectedLabels, setSelectedLabels] = useState(labels.map(l => l.global_id));
  const [bulkAction, setBulkAction] = useState('');
  const [bulkValue, setBulkValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [progress, setProgress] = useState({ current: 0, total: 0 });

  const bulkActions = [
    { value: 'status', label: 'Change Status', options: ['active', 'inactive', 'pending', 'suspended'] },
    { value: 'integration', label: 'Change Integration', options: ['full_integration', 'api_partner', 'distribution_only', 'metadata_sync', 'content_sharing'] },
    { value: 'label_type', label: 'Change Label Type', options: ['major', 'independent', 'distribution', 'publishing', 'management'] },
    { value: 'jurisdiction', label: 'Change Territory', options: ['US', 'UK', 'EU', 'CA', 'AU', 'JP', 'GLOBAL'] },
  ];

  const toggleLabelSelection = (globalId) => {
    setSelectedLabels(prev => 
      prev.includes(globalId) 
        ? prev.filter(id => id !== globalId)
        : [...prev, globalId]
    );
  };

  const selectAll = () => {
    setSelectedLabels(labels.map(l => l.global_id));
  };

  const deselectAll = () => {
    setSelectedLabels([]);
  };

  const handleBulkUpdate = async () => {
    if (!bulkAction || !bulkValue) {
      setError('Please select both an action and a value');
      return;
    }

    if (selectedLabels.length === 0) {
      setError('Please select at least one label');
      return;
    }

    const confirm = window.confirm(
      `Are you sure you want to update ${selectedLabels.length} label(s)?\n\nAction: ${bulkAction}\nValue: ${bulkValue}`
    );

    if (!confirm) return;

    setLoading(true);
    setError('');
    setSuccess('');
    setProgress({ current: 0, total: selectedLabels.length });

    const token = localStorage.getItem('token');
    let successCount = 0;
    let failCount = 0;

    for (let i = 0; i < selectedLabels.length; i++) {
      const labelId = selectedLabels[i];
      setProgress({ current: i + 1, total: selectedLabels.length });

      try {
        const updateData = { [bulkAction]: bulkValue };

        const response = await fetch(`${API}/api/uln/labels/${labelId}`, {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updateData)
        });

        if (response.ok) {
          successCount++;
        } else {
          failCount++;
        }
      } catch (error) {
        console.error(`Error updating label ${labelId}:`, error);
        failCount++;
      }
    }

    setLoading(false);
    setSuccess(`✅ Bulk update complete! ${successCount} succeeded, ${failCount} failed.`);
    
    setTimeout(() => {
      onUpdate();
    }, 2000);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-purple-600 text-white px-6 py-4 rounded-t-lg flex justify-between items-center sticky top-0 z-10">
          <h2 className="text-xl font-bold">📦 Bulk Label Editor</h2>
          <button 
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Selection Controls */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-gray-900">
                Selected Labels: {selectedLabels.length} / {labels.length}
              </h3>
              <div className="space-x-2">
                <button
                  onClick={selectAll}
                  className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded"
                >
                  Select All
                </button>
                <button
                  onClick={deselectAll}
                  className="px-3 py-1 bg-gray-500 hover:bg-gray-600 text-white text-sm rounded"
                >
                  Deselect All
                </button>
              </div>
            </div>

            {/* Label List with Checkboxes */}
            <div className="max-h-60 overflow-y-auto space-y-2">
              {labels.map((label) => (
                <label
                  key={label.global_id}
                  className="flex items-center p-3 bg-white border border-gray-200 rounded hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedLabels.includes(label.global_id)}
                    onChange={() => toggleLabelSelection(label.global_id)}
                    className="mr-3 h-4 w-4 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{label.name}</div>
                    <div className="text-xs text-gray-500">
                      {label.label_type} • {label.status} • {label.territory}
                    </div>
                  </div>
                  <span className="text-xs text-gray-400 font-mono">
                    {label.global_id.slice(-8)}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Bulk Action Selection */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-4">Bulk Action</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Action Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Action
                </label>
                <select
                  value={bulkAction}
                  onChange={(e) => {
                    setBulkAction(e.target.value);
                    setBulkValue('');
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">-- Choose Action --</option>
                  {bulkActions.map((action) => (
                    <option key={action.value} value={action.value}>
                      {action.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Action Value */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Value
                </label>
                <select
                  value={bulkValue}
                  onChange={(e) => setBulkValue(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={!bulkAction}
                >
                  <option value="">-- Choose Value --</option>
                  {bulkAction && bulkActions.find(a => a.value === bulkAction)?.options.map((option) => (
                    <option key={option} value={option}>
                      {option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          {loading && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">
                  Updating labels...
                </span>
                <span className="text-sm text-blue-700">
                  {progress.current} / {progress.total}
                </span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(progress.current / progress.total) * 100}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              ❌ {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleBulkUpdate}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading || selectedLabels.length === 0 || !bulkAction || !bulkValue}
            >
              {loading ? 'Updating...' : `Update ${selectedLabels.length} Label(s)`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ===== ADVANCED SEARCH COMPONENT =====

export const AdvancedSearch = ({ onSearch, onClose }) => {
  const [searchCriteria, setSearchCriteria] = useState({
    name: '',
    label_type: '',
    status: '',
    territory: '',
    integration_type: '',
    genres: '',
    dao_affiliated: '',
    blockchain_enabled: '',
    compliance_status: '',
    verification_status: ''
  });

  const handleChange = (field, value) => {
    setSearchCriteria(prev => ({ ...prev, [field]: value }));
  };

  const handleSearch = () => {
    // Filter out empty criteria
    const activeCriteria = Object.fromEntries(
      Object.entries(searchCriteria).filter(([_, value]) => value !== '')
    );
    onSearch(activeCriteria);
  };

  const handleReset = () => {
    setSearchCriteria({
      name: '',
      label_type: '',
      status: '',
      territory: '',
      integration_type: '',
      genres: '',
      dao_affiliated: '',
      blockchain_enabled: '',
      compliance_status: '',
      verification_status: ''
    });
    onSearch({});
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-purple-600 text-white px-6 py-4 rounded-t-lg flex justify-between items-center sticky top-0 z-10">
          <h2 className="text-xl font-bold">🔍 Advanced Search</h2>
          <button 
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* Name Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Label Name
            </label>
            <input
              type="text"
              value={searchCriteria.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Search by name..."
            />
          </div>

          {/* Two-column layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Label Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Label Type
              </label>
              <select
                value={searchCriteria.label_type}
                onChange={(e) => handleChange('label_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Types</option>
                <option value="major">Major</option>
                <option value="independent">Independent</option>
                <option value="distribution">Distribution</option>
                <option value="publishing">Publishing</option>
                <option value="management">Management</option>
              </select>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={searchCriteria.status}
                onChange={(e) => handleChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>

            {/* Territory */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Territory
              </label>
              <select
                value={searchCriteria.territory}
                onChange={(e) => handleChange('territory', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Territories</option>
                <option value="US">United States</option>
                <option value="UK">United Kingdom</option>
                <option value="EU">European Union</option>
                <option value="CA">Canada</option>
                <option value="AU">Australia</option>
                <option value="JP">Japan</option>
                <option value="GLOBAL">Global</option>
              </select>
            </div>

            {/* Integration Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Integration Type
              </label>
              <select
                value={searchCriteria.integration_type}
                onChange={(e) => handleChange('integration_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Integrations</option>
                <option value="full_integration">Full Integration</option>
                <option value="api_partner">API Partner</option>
                <option value="distribution_only">Distribution Only</option>
                <option value="metadata_sync">Metadata Sync</option>
                <option value="content_sharing">Content Sharing</option>
              </select>
            </div>

            {/* DAO Affiliated */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                DAO Affiliated
              </label>
              <select
                value={searchCriteria.dao_affiliated}
                onChange={(e) => handleChange('dao_affiliated', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>

            {/* Blockchain Enabled */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Blockchain Enabled
              </label>
              <select
                value={searchCriteria.blockchain_enabled}
                onChange={(e) => handleChange('blockchain_enabled', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>

            {/* Compliance Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Compliance Status
              </label>
              <select
                value={searchCriteria.compliance_status}
                onChange={(e) => handleChange('compliance_status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All</option>
                <option value="verified">Verified</option>
                <option value="pending">Pending</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>

            {/* Verification Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Verification Status
              </label>
              <select
                value={searchCriteria.verification_status}
                onChange={(e) => handleChange('verification_status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All</option>
                <option value="verified">Verified</option>
                <option value="pending">Pending</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>

          {/* Genres */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Genres (comma-separated)
            </label>
            <input
              type="text"
              value={searchCriteria.genres}
              onChange={(e) => handleChange('genres', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="e.g., Hip-Hop, R&B, Pop"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
            >
              Reset Filters
            </button>
            <div className="space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSearch}
                className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                🔍 Search
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ===== LABEL DATA EXPORT COMPONENT =====

export const LabelDataExporter = ({ labels, onClose }) => {
  const [exportFormat, setExportFormat] = useState('json');
  const [includeFields, setIncludeFields] = useState({
    basic: true,
    metadata: true,
    social: true,
    stats: true
  });

  const handleExport = () => {
    let exportData = labels.map(label => {
      const data = {};
      
      if (includeFields.basic) {
        data.global_id = label.global_id;
        data.name = label.name;
        data.label_type = label.label_type;
        data.status = label.status;
        data.integration_type = label.integration_type;
      }
      
      if (includeFields.metadata) {
        data.territory = label.territory;
        data.genres = label.genre_focus;
      }
      
      if (includeFields.stats) {
        data.content_count = label.content_count;
        data.shared_content_count = label.shared_content_count;
        data.monthly_revenue = label.monthly_revenue;
      }
      
      return data;
    });

    let content, filename, mimeType;

    if (exportFormat === 'json') {
      content = JSON.stringify(exportData, null, 2);
      filename = 'uln_labels_export.json';
      mimeType = 'application/json';
    } else if (exportFormat === 'csv') {
      const headers = Object.keys(exportData[0] || {}).join(',');
      const rows = exportData.map(row => 
        Object.values(row).map(val => 
          typeof val === 'object' ? JSON.stringify(val) : val
        ).join(',')
      );
      content = [headers, ...rows].join('\n');
      filename = 'uln_labels_export.csv';
      mimeType = 'text/csv';
    }

    // Create download
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-md w-full">
        {/* Header */}
        <div className="bg-purple-600 text-white px-6 py-4 rounded-t-lg flex justify-between items-center">
          <h2 className="text-xl font-bold">📤 Export Label Data</h2>
          <button 
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-4">
          <p className="text-sm text-gray-600">
            Exporting {labels.length} label(s)
          </p>

          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Export Format
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="json"
                  checked={exportFormat === 'json'}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="mr-2"
                />
                <span>JSON (recommended)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="csv"
                  checked={exportFormat === 'csv'}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="mr-2"
                />
                <span>CSV (spreadsheet)</span>
              </label>
            </div>
          </div>

          {/* Field Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Include Fields
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeFields.basic}
                  onChange={(e) => setIncludeFields(prev => ({ ...prev, basic: e.target.checked }))}
                  className="mr-2"
                />
                <span>Basic Info (ID, Name, Type, Status)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeFields.metadata}
                  onChange={(e) => setIncludeFields(prev => ({ ...prev, metadata: e.target.checked }))}
                  className="mr-2"
                />
                <span>Metadata (Territory, Genres)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeFields.stats}
                  onChange={(e) => setIncludeFields(prev => ({ ...prev, stats: e.target.checked }))}
                  className="mr-2"
                />
                <span>Statistics (Content, Revenue)</span>
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleExport}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              📥 Download
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
