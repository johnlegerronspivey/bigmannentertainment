import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

const FederatedContentList = ({ content }) => {
  if (content.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">No federated content found</div>
        <p className="text-gray-400 mt-2">Start sharing content across labels to see it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold mb-4">📁 Federated Content</h3>
      {content.map((item, index) => (
        <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium">Content ID: {item.content_id}</h4>
              <p className="text-sm text-gray-600">Primary Label: {item.primary_label_id}</p>
              <p className="text-sm text-gray-500">
                Shared with: {item.licensing_labels?.length || 0} labels
              </p>
              <p className="text-sm text-gray-500">
                Access Level: {item.access_level}
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Active
              </span>
            </div>
          </div>

          {item.rights_splits && Object.keys(item.rights_splits).length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <h5 className="text-sm font-medium text-gray-700 mb-2">Rights Distribution:</h5>
              <div className="flex flex-wrap gap-2">
                {Object.entries(item.rights_splits).map(([labelId, percentage]) => (
                  <span key={labelId} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {labelId}: {percentage}%
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

const MetadataSync = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🔄 Metadata Synchronization</h3>
    <p className="text-gray-600">Sync metadata across all connected labels</p>
    
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <span className="text-blue-600 text-xl">ℹ️</span>
        </div>
        <div className="ml-3">
          <h4 className="text-sm font-medium text-blue-900">Automatic Metadata Sync</h4>
          <p className="text-sm text-blue-700">
            Metadata is automatically synchronized across all labels with federated access when changes are made.
          </p>
        </div>
      </div>
    </div>

    <div className="space-y-3">
      <div className="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
        <div>
          <div className="font-medium">Content Metadata</div>
          <div className="text-sm text-gray-600">Title, artist, genre, duration</div>
        </div>
        <div className="text-green-600 font-medium">✓ Sync Active</div>
      </div>

      <div className="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
        <div>
          <div className="font-medium">Rights Information</div>
          <div className="text-sm text-gray-600">Ownership, splits, restrictions</div>
        </div>
        <div className="text-green-600 font-medium">✓ Sync Active</div>
      </div>

      <div className="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
        <div>
          <div className="font-medium">Revenue Data</div>
          <div className="text-sm text-gray-600">Streams, plays, earnings</div>
        </div>
        <div className="text-green-600 font-medium">✓ Sync Active</div>
      </div>
    </div>
  </div>
);

const PermissionsManagement = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">🔐 Role-Based Permissions</h3>
    <p className="text-gray-600">Manage access levels and permissions for federated content</p>
    
    <div className="space-y-3">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Read Only Access</h4>
        <p className="text-sm text-gray-600 mb-3">View content and basic metadata only</p>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">View Metadata</span>
          <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">View Usage Stats</span>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Edit Metadata</h4>
        <p className="text-sm text-gray-600 mb-3">Modify non-rights metadata</p>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Edit Title/Artist</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Update Genre</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Add Description</span>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Full Access</h4>
        <p className="text-sm text-gray-600 mb-3">Complete control including rights management</p>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Edit Rights</span>
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Change Splits</span>
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Manage Distribution</span>
        </div>
      </div>
    </div>
  </div>
);

const UsageAttribution = () => (
  <div className="space-y-4">
    <h3 className="text-lg font-bold">📊 Usage Attribution</h3>
    <p className="text-gray-600">Track streams, views, and revenue attribution by label</p>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Streams by Label</h4>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm">Label A</span>
            <span className="font-medium">1,234,567</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label B</span>
            <span className="font-medium">987,654</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label C</span>
            <span className="font-medium">456,789</span>
          </div>
        </div>
      </div>

      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Revenue Attribution</h4>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm">Label A</span>
            <span className="font-medium">$12,345</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label B</span>
            <span className="font-medium">$9,876</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm">Label C</span>
            <span className="font-medium">$4,567</span>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const CreateContentSharingModal = ({ onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    content_id: '',
    target_labels: [],
    access_level: 'read_only',
    proposed_rights_splits: {},
    usage_restrictions: [],
    expiry_date: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/uln/content/federated-access`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content_id: formData.content_id,
          requesting_label_id: 'current-label-id',
          target_labels: formData.target_labels,
          access_level: formData.access_level,
          proposed_rights_splits: formData.proposed_rights_splits,
          usage_restrictions: formData.usage_restrictions,
          expiry_date: formData.expiry_date ? new Date(formData.expiry_date).toISOString() : null
        })
      });

      if (response.ok) {
        onCreated();
        onClose();
      }
    } catch (error) {
      console.error('Error creating content sharing:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
        <h3 className="text-xl font-bold mb-4">Share Content Across Labels</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content ID</label>
            <input
              type="text"
              required
              value={formData.content_id}
              onChange={(e) => setFormData({...formData, content_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter content identifier"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Labels</label>
            <input
              type="text"
              value={formData.target_labels.join(', ')}
              onChange={(e) => setFormData({
                ...formData, 
                target_labels: e.target.value.split(',').map(id => id.trim()).filter(id => id)
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter label IDs (comma-separated)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Access Level</label>
            <select
              value={formData.access_level}
              onChange={(e) => setFormData({...formData, access_level: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="read_only">Read Only</option>
              <option value="edit_metadata">Edit Metadata</option>
              <option value="full_access">Full Access</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date (Optional)</label>
            <input
              type="date"
              value={formData.expiry_date}
              onChange={(e) => setFormData({...formData, expiry_date: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Create Sharing Agreement
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export const CrossLabelContentSharing = () => {
  const [activeSection, setActiveSection] = useState('federated');
  const [federatedContent, setFederatedContent] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchFederatedContent = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const currentLabelId = 'current-label-id';
      
      const response = await fetch(`${API}/api/uln/content/federated/${currentLabelId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFederatedContent(data.federated_content || []);
      }
    } catch (error) {
      console.error('Error fetching federated content:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeSection === 'federated') {
      fetchFederatedContent();
    }
  }, [activeSection]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">🔗 Cross-Label Content Sharing</h2>
          <p className="text-gray-600">Federated access and metadata sync across labels</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          + Share Content
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['federated', 'metadata', 'permissions', 'usage'].map((section) => (
            <button
              key={section}
              onClick={() => setActiveSection(section)}
              className={`capitalize py-2 px-4 rounded-md font-medium transition-colors ${
                activeSection === section 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {section.replace('_', ' ')}
            </button>
          ))}
        </nav>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        {loading && (
          <div className="flex justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}

        {activeSection === 'federated' && !loading && (
          <FederatedContentList content={federatedContent} />
        )}

        {activeSection === 'metadata' && (
          <MetadataSync />
        )}

        {activeSection === 'permissions' && (
          <PermissionsManagement />
        )}

        {activeSection === 'usage' && (
          <UsageAttribution />
        )}
      </div>

      {showCreateModal && (
        <CreateContentSharingModal 
          onClose={() => setShowCreateModal(false)}
          onCreated={fetchFederatedContent}
        />
      )}
    </div>
  );
};
