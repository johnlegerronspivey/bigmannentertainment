import React, { useState, useEffect } from 'react';

// Get API URL from environment
const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

// ===== MAIN LABEL DASHBOARD =====

export const LabelDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState({
    start: new Date().toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchDashboardData();
  }, [dateRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/label/dashboard`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        setError('');
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
        localStorage.removeItem('accessToken');
      } else {
        setError('Failed to load label dashboard data');
      }
    } catch (error) {
      console.error('Label dashboard fetch error:', error);
      setError('Error connecting to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🎵 Big Mann Entertainment - Label Dashboard</h1>
          
          {/* Date Range Selector */}
          <div className="flex space-x-4">
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <nav className="flex space-x-8 px-6 py-4">
            {['overview', 'artists', 'ar', 'projects', 'marketing', 'finance'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`capitalize font-medium py-2 px-4 rounded-md transition-colors ${
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

        {/* Dashboard Content */}
        {dashboardData && (
          <>
            {activeTab === 'overview' && (
              <LabelOverview data={dashboardData} />
            )}
            {activeTab === 'artists' && (
              <ArtistManagement />
            )}
            {activeTab === 'ar' && (
              <ARManagement />
            )}
            {activeTab === 'projects' && (
              <ProjectManagement />
            )}
            {activeTab === 'marketing' && (
              <MarketingManagement />
            )}
            {activeTab === 'finance' && (
              <FinancialManagement />
            )}
          </>
        )}
      </div>
    </div>
  );
};

// ===== LABEL OVERVIEW COMPONENT =====

const LabelOverview = ({ data }) => {
  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard 
          title="Total Artists" 
          value={data.total_artists} 
          icon="👥" 
          color="bg-blue-500"
        />
        <MetricCard 
          title="Active Projects" 
          value={data.active_projects} 
          icon="🎧" 
          color="bg-green-500"
        />
        <MetricCard 
          title="Total Revenue" 
          value={`$${(data.total_revenue || 0).toLocaleString()}`} 
          icon="💰" 
          color="bg-yellow-500"
        />
        <MetricCard 
          title="Total Streams" 
          value={(data.total_streams || 0).toLocaleString()} 
          icon="📈" 
          color="bg-purple-500"
        />
      </div>

      {/* Top Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">🌟 Top Performing Artists</h3>
          <div className="space-y-4">
            {(data.top_artists || []).map((artist, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium">{artist.stage_name}</div>
                  <div className="text-sm text-gray-600">{artist.streams?.toLocaleString()} streams</div>
                </div>
                <div className="text-green-600 font-bold">
                  ${artist.revenue?.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">📊 Revenue Breakdown</h3>
          <div className="space-y-3">
            {Object.entries(data.revenue_breakdown || {}).map(([source, amount]) => (
              <div key={source} className="flex justify-between items-center">
                <span className="capitalize">{source.replace('_', ' ')}</span>
                <span className="font-medium">${amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* A&R Metrics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4">🎯 A&R Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{data.demos_received || 0}</div>
            <div className="text-gray-600">Demos Received</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{data.artists_signed || 0}</div>
            <div className="text-gray-600">Artists Signed</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{(data.conversion_rate || 0).toFixed(1)}%</div>
            <div className="text-gray-600">Conversion Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, icon, color }) => (
  <div className="bg-white rounded-lg shadow-lg p-6">
    <div className="flex items-center">
      <div className={`${color} p-3 rounded-full text-white text-2xl`}>
        {icon}
      </div>
      <div className="ml-4">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  </div>
);

// ===== ARTIST MANAGEMENT COMPONENT =====

const ArtistManagement = () => {
  const [artists, setArtists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedArtist, setSelectedArtist] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    genre: ''
  });

  useEffect(() => {
    fetchArtists();
  }, [filters]);

  const fetchArtists = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) return;

      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.genre) params.append('genre', filters.genre);

      const response = await fetch(`${API}/api/label/artists?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setArtists(data);
      }
    } catch (error) {
      console.error('Error fetching artists:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddArtist = async (artistData) => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${API}/api/label/artists`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(artistData)
      });
      
      if (response.ok) {
        setShowAddModal(false);
        fetchArtists();
      }
    } catch (error) {
      console.error('Error adding artist:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">👥 Artist Roster</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          + Add Artist
        </button>
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
            <option value="active">Active</option>
            <option value="development">Development</option>
            <option value="released">Released</option>
            <option value="inactive">Inactive</option>
          </select>
          
          <input
            type="text"
            placeholder="Filter by genre..."
            value={filters.genre}
            onChange={(e) => setFilters({...filters, genre: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />

          <button
            onClick={() => setFilters({status: '', genre: ''})}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Artists List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {artists.map((artist) => (
          <ArtistCard 
            key={artist.id} 
            artist={artist} 
            onSelect={() => setSelectedArtist(artist)}
          />
        ))}
      </div>

      {/* Add Artist Modal */}
      {showAddModal && (
        <AddArtistModal 
          onClose={() => setShowAddModal(false)}
          onSave={handleAddArtist}
        />
      )}

      {/* Artist Details Modal */}
      {selectedArtist && (
        <ArtistDetailsModal 
          artist={selectedArtist}
          onClose={() => setSelectedArtist(null)}
          onUpdate={fetchArtists}
        />
      )}
    </div>
  );
};

const ArtistCard = ({ artist, onSelect }) => (
  <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" onClick={onSelect}>
    <div className="flex items-center mb-4">
      <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
        <span className="text-purple-600 font-bold text-lg">
          {artist.stage_name.charAt(0).toUpperCase()}
        </span>
      </div>
      <div className="ml-4">
        <h3 className="font-bold text-lg">{artist.stage_name}</h3>
        <p className="text-gray-600 text-sm">{artist.real_name}</p>
      </div>
    </div>
    
    <div className="space-y-2">
      <div className="flex justify-between">
        <span className="text-gray-600">Status:</span>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          artist.status === 'active' ? 'bg-green-100 text-green-800' :
          artist.status === 'development' ? 'bg-yellow-100 text-yellow-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {artist.status}
        </span>
      </div>
      
      {artist.genres && artist.genres.length > 0 && (
        <div className="flex justify-between">
          <span className="text-gray-600">Genres:</span>
          <span className="text-sm">{artist.genres.slice(0, 2).join(', ')}</span>
        </div>
      )}
      
      <div className="flex justify-between">
        <span className="text-gray-600">Signed:</span>
        <span className="text-sm">
          {artist.signed_date ? new Date(artist.signed_date).toLocaleDateString() : 'Not signed'}
        </span>
      </div>
    </div>
  </div>
);

// ===== A&R MANAGEMENT COMPONENT =====

const ARManagement = () => {
  const [activeSection, setActiveSection] = useState('demos');
  const [demos, setDemos] = useState([]);
  const [industryContacts, setIndustryContacts] = useState([]);
  const [industryTrends, setIndustryTrends] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeSection === 'demos') {
      fetchDemos();
    } else if (activeSection === 'trends') {
      fetchIndustryTrends();
    }
  }, [activeSection]);

  const fetchDemos = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${API}/api/label/ar/demos`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDemos(data);
      }
    } catch (error) {
      console.error('Error fetching demos:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIndustryTrends = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${API}/api/label/ar/industry-trends`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setIndustryTrends(data);
      }
    } catch (error) {
      console.error('Error fetching trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchIndustryContacts = async (query, category = 'all') => {
    setLoading(true);
    try {
      const token = localStorage.getItem('accessToken');
      const params = new URLSearchParams({ query, category });
      const response = await fetch(`${API}/api/label/ar/industry-contacts?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setIndustryContacts(data);
      }
    } catch (error) {
      console.error('Error fetching contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">🎯 A&R Management</h2>
      </div>

      {/* Section Navigation */}
      <div className="bg-white rounded-lg shadow p-4">
        <nav className="flex space-x-6">
          {['demos', 'contacts', 'trends', 'scouts'].map((section) => (
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

      {/* Section Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {loading && (
          <div className="flex justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        )}

        {activeSection === 'demos' && !loading && (
          <DemoManagement demos={demos} onUpdate={fetchDemos} />
        )}

        {activeSection === 'contacts' && (
          <IndustryContacts contacts={industryContacts} onSearch={searchIndustryContacts} />
        )}

        {activeSection === 'trends' && !loading && industryTrends && (
          <IndustryTrends trends={industryTrends} />
        )}

        {activeSection === 'scouts' && (
          <TalentScouts />
        )}
      </div>
    </div>
  );
};

const DemoManagement = ({ demos, onUpdate }) => {
  const [selectedDemo, setSelectedDemo] = useState(null);

  const evaluateDemo = async (demoId, score, notes, status) => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(`${API}/api/label/ar/demos/${demoId}/evaluate`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          score,
          notes,
          status
        })
      });
      
      if (response.ok) {
        onUpdate();
        setSelectedDemo(null);
      }
    } catch (error) {
      console.error('Error evaluating demo:', error);
      alert('Error evaluating demo');
    }
  };

  return (
    <div>
      <h3 className="text-lg font-bold mb-4">📨 Demo Submissions</h3>
      
      <div className="space-y-4">
        {demos.map((demo) => (
          <div key={demo.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium">{demo.artist_name}</h4>
                <p className="text-sm text-gray-600">{demo.contact_email}</p>
                <p className="text-sm text-gray-500">Genre: {demo.genre}</p>
                <p className="text-sm text-gray-500">
                  Submitted: {new Date(demo.created_at).toLocaleDateString()}
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  demo.status === 'submitted' ? 'bg-blue-100 text-blue-800' :
                  demo.status === 'reviewing' ? 'bg-yellow-100 text-yellow-800' :
                  demo.status === 'shortlisted' ? 'bg-green-100 text-green-800' :
                  demo.status === 'rejected' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {demo.status}
                </span>
                
                <button
                  onClick={() => setSelectedDemo(demo)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm"
                >
                  Review
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedDemo && (
        <DemoEvaluationModal 
          demo={selectedDemo}
          onClose={() => setSelectedDemo(null)}
          onEvaluate={evaluateDemo}
        />
      )}
    </div>
  );
};

// ===== ADDITIONAL MODAL COMPONENTS =====

const AddArtistModal = ({ onClose, onSave }) => {
  const [formData, setFormData] = useState({
    stage_name: '',
    real_name: '',
    email: '',
    phone: '',
    genres: [],
    bio: '',
    social_media: {}
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
        <h3 className="text-xl font-bold mb-4">Add New Artist</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Stage Name *</label>
              <input
                type="text"
                required
                value={formData.stage_name}
                onChange={(e) => setFormData({...formData, stage_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Real Name</label>
              <input
                type="text"
                value={formData.real_name}
                onChange={(e) => setFormData({...formData, real_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Genres (comma-separated)</label>
            <input
              type="text"
              placeholder="e.g., pop, hip-hop, R&B"
              onChange={(e) => setFormData({
                ...formData, 
                genres: e.target.value.split(',').map(g => g.trim()).filter(g => g)
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
            <textarea
              rows="3"
              value={formData.bio}
              onChange={(e) => setFormData({...formData, bio: e.target.value})}
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
              Add Artist
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ===== LABEL DIRECTORY COMPONENT =====

const LabelDirectory = () => {
  const [labels, setLabels] = useState({ major_labels: [], independent_labels: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [selectedTerritory, setSelectedTerritory] = useState('');
  const [activeTab, setActiveTab] = useState('major');

  useEffect(() => {
    fetchLabels();
  }, []);

  const fetchLabels = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API}/api/industry/record-labels`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLabels(data);
        setError('');
      } else if (response.status === 401) {
        setError('Session expired. Please log in again.');
        localStorage.removeItem('accessToken');
      } else {
        setError('Failed to load record labels');
      }
    } catch (error) {
      console.error('Error fetching labels:', error);
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const filterLabels = (labelsList) => {
    return labelsList.filter(label => {
      const matchesSearch = label.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesGenre = !selectedGenre || (label.genre_focus && label.genre_focus.toLowerCase().includes(selectedGenre.toLowerCase()));
      const matchesTerritory = !selectedTerritory || label.territories.includes(selectedTerritory);
      return matchesSearch && matchesGenre && matchesTerritory;
    });
  };

  const getUniqueGenres = (labelsList) => {
    const genres = new Set();
    labelsList.forEach(label => {
      if (label.genre_focus) {
        genres.add(label.genre_focus);
      }
    });
    return Array.from(genres).sort();
  };

  const getUniqueTerritories = (labelsList) => {
    const territories = new Set();
    labelsList.forEach(label => {
      if (label.territories) {
        label.territories.forEach(territory => territories.add(territory));
      }
    });
    return Array.from(territories).sort();
  };

  const allLabels = [...labels.major_labels, ...labels.independent_labels];
  const uniqueGenres = getUniqueGenres(allLabels);
  const uniqueTerritories = getUniqueTerritories(allLabels);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-700 to-blue-800 rounded-lg p-6 text-white">
        <h2 className="text-3xl font-bold mb-2">🏢 Global Record Labels Directory</h2>
        <p className="text-lg opacity-90">
          Connected to {labels.major_labels?.length || 0} major labels and {labels.independent_labels?.length || 0} independent labels worldwide
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <input
              type="text"
              placeholder="Search labels..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <select
              value={selectedGenre}
              onChange={(e) => setSelectedGenre(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All Genres</option>
              {uniqueGenres.map(genre => (
                <option key={genre} value={genre}>{genre}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={selectedTerritory}
              onChange={(e) => setSelectedTerritory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All Territories</option>
              {uniqueTerritories.map(territory => (
                <option key={territory} value={territory}>{territory}</option>
              ))}
            </select>
          </div>
          <div>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedGenre('');
                setSelectedTerritory('');
              }}
              className="w-full bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('major')}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
              activeTab === 'major'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Major Labels ({filterLabels(labels.major_labels || []).length})
          </button>
          <button
            onClick={() => setActiveTab('independent')}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
              activeTab === 'independent'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Independent Labels ({filterLabels(labels.independent_labels || []).length})
          </button>
          <button
            onClick={() => setActiveTab('all')}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
              activeTab === 'all'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Labels ({filterLabels([...labels.major_labels || [], ...labels.independent_labels || []]).length})
          </button>
        </div>
      </div>

      {/* Labels Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {(() => {
          let labelsToShow = [];
          if (activeTab === 'major') {
            labelsToShow = filterLabels(labels.major_labels || []);
          } else if (activeTab === 'independent') {
            labelsToShow = filterLabels(labels.independent_labels || []);
          } else {
            labelsToShow = filterLabels([...labels.major_labels || [], ...labels.independent_labels || []]);
          }

          return labelsToShow.map((label, index) => (
            <LabelCard key={`${label.name}-${index}`} label={label} />
          ));
        })()}
      </div>

      {/* Summary Stats */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">📊 Directory Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{labels.major_labels?.length || 0}</div>
            <div className="text-gray-600">Major Labels</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{labels.independent_labels?.length || 0}</div>
            <div className="text-gray-600">Independent Labels</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{uniqueGenres.length}</div>
            <div className="text-gray-600">Genres Covered</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">{uniqueTerritories.length}</div>
            <div className="text-gray-600">Territories</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ===== LABEL CARD COMPONENT =====

const LabelCard = ({ label }) => {
  const isMajor = !label.genre_focus; // Major labels typically don't have specific genre focus
  const labelType = isMajor ? 'Major' : 'Independent';
  
  return (
    <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow p-6 border-l-4 border-purple-500">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{label.name}</h3>
          <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
            isMajor ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {labelType}
          </span>
        </div>
        <div className="text-2xl">
          {isMajor ? '🏢' : '🎵'}
        </div>
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        {label.founded && (
          <div className="flex items-center">
            <span className="font-medium">Founded:</span>
            <span className="ml-1">{label.founded}</span>
          </div>
        )}
        
        {label.headquarters && (
          <div className="flex items-center">
            <span className="font-medium">HQ:</span>
            <span className="ml-1">{label.headquarters}</span>
          </div>
        )}

        {label.parent && (
          <div className="flex items-center">
            <span className="font-medium">Parent:</span>
            <span className="ml-1">{label.parent}</span>
          </div>
        )}

        {label.genre_focus && (
          <div className="flex items-center">
            <span className="font-medium">Genre:</span>
            <span className="ml-1 bg-gray-100 px-2 py-1 rounded">{label.genre_focus}</span>
          </div>
        )}

        {label.territories && (
          <div className="flex items-start">
            <span className="font-medium">Territories:</span>
            <div className="ml-1 flex flex-wrap gap-1">
              {label.territories.map(territory => (
                <span key={territory} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                  {territory}
                </span>
              ))}
            </div>
          </div>
        )}

        {label.supported_formats && (
          <div className="flex items-start">
            <span className="font-medium">Formats:</span>
            <div className="ml-1 flex flex-wrap gap-1">
              {label.supported_formats.map(format => (
                <span key={format} className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">
                  {format.toUpperCase()}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 flex space-x-2">
        <button className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors">
          Connect
        </button>
        <button className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors">
          Details
        </button>
      </div>
    </div>
  );
};

// Export all components
export { 
  ArtistManagement, 
  ARManagement,
  LabelOverview,
  MetricCard,
  ArtistCard,
  AddArtistModal,
  LabelDirectory,
  LabelCard
};