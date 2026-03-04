import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const LibraryPage = () => {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMedia();
    // eslint-disable-next-line
  }, []);

  async function loadMedia() {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please login.');
        setLoading(false);
        return;
      }

      let response;
      try {
        response = await axios.get(`${API}/media/library`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (firstError) {
        console.log('Library endpoint failed, trying user-media endpoint...');
        try {
          response = await axios.get(`${API}/media`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        } catch (secondError) {
          console.log('Media endpoint failed, trying list endpoint...');
          response = await axios.get(`${API}/media/list`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        }
      }

      let mediaItems = [];
      if (response.data?.media_items) {
        mediaItems = response.data.media_items;
      } else if (response.data?.media) {
        mediaItems = response.data.media;
      } else if (Array.isArray(response.data)) {
        mediaItems = response.data;
      } else if (response.data?.data) {
        mediaItems = response.data.data;
      }

      console.log('Loaded media items:', mediaItems);
      setMedia(mediaItems || []);
    } catch (error) {
      console.error('Error loading media:', error);
      
      if (error.response?.status === 401) {
        setError('Authentication expired. Please login again.');
      } else if (error.response?.status === 404) {
        setError('Media service not available. This may be temporary.');
      } else {
        setError(`Failed to load media: ${error.response?.data?.detail || error.message}`);
      }
    }
    setLoading(false);
  }

  const filteredMedia = media.filter(item => {
    if (filter === 'all') return true;
    return item.content_type === filter;
  });

  const deleteMedia = async (mediaId) => {
    if (!window.confirm('Are you sure you want to delete this media?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/media/${mediaId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setMedia(prev => prev.filter(item => item.id !== mediaId));
      alert('Media deleted successfully!');
    } catch (error) {
      console.error('Delete error:', error);
      alert(`Failed to delete media: ${error.response?.data?.detail || error.message}`);
    }
  };

  const viewMedia = (item) => {
    window.open(`${API}/media/${item.id}/view`, '_blank');
  };

  const refreshMedia = () => {
    loadMedia();
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your media library...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="text-red-600 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Media</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-x-4">
            <button 
              onClick={refreshMedia}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Retry
            </button>
            <Link to="/upload" className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
              Upload New Content
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Media Library</h1>
          <p className="text-gray-600">{media.length} files in your library</p>
        </div>
        <div className="space-x-3">
          <button
            onClick={refreshMedia}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
          >
            Refresh
          </button>
          <Link
            to="/upload"
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
          >
            Upload Content
          </Link>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
          {[
            { key: 'all', label: 'All Files', count: media.length },
            { key: 'audio', label: 'Audio', count: media.filter(m => m.content_type === 'audio').length },
            { key: 'video', label: 'Video', count: media.filter(m => m.content_type === 'video').length },
            { key: 'image', label: 'Images', count: media.filter(m => m.content_type === 'image').length }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === tab.key 
                  ? 'bg-white text-purple-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>
      </div>

      {filteredMedia.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredMedia.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow border overflow-hidden">
              {/* Media Preview */}
              <div className="aspect-video bg-gray-100 flex items-center justify-center">
                {item.content_type === 'image' ? (
                  <img 
                    src={`${API}/media/${item.id}/download`}
                    alt={item.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className={`w-full h-full flex items-center justify-center text-6xl ${item.content_type === 'image' ? 'hidden' : ''}`}>
                  {item.content_type === 'audio' ? '🎵' :
                   item.content_type === 'video' ? '🎥' : '📄'}
                </div>
              </div>

              {/* Media Info */}
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1 truncate">{item.title}</h3>
                <p className="text-sm text-gray-500 mb-2">
                  {item.content_type} • {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Unknown date'}
                </p>
                
                {item.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{item.description}</p>
                )}

                {/* Actions */}
                <div className="flex space-x-2">
                  <button
                    onClick={() => viewMedia(item)}
                    className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded text-sm text-center"
                  >
                    View
                  </button>
                  <Link
                    to={`/distribute?media=${item.id}&title=${encodeURIComponent(item.title)}`}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-sm text-center"
                  >
                    Distribute
                  </Link>
                  <button
                    onClick={() => deleteMedia(item.id)}
                    className="px-3 py-2 text-red-600 hover:text-red-800 border border-red-200 hover:border-red-300 rounded text-sm"
                  >
                    🗑️
                  </button>
                </div>

                {/* Status */}
                <div className="mt-3 flex justify-between items-center text-xs">
                  <span className={`px-2 py-1 rounded ${
                    item.is_approved ? 'bg-green-100 text-green-800' : 
                    item.approval_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {item.is_approved ? 'Approved' : 
                     item.approval_status === 'pending' ? 'Pending' : 'Draft'}
                  </span>
                  {item.download_count > 0 && (
                    <span className="text-gray-500">{item.download_count} downloads</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m4 0H3a1 1 0 00-1 1v13a1 1 0 001 1h18a1 1 0 001-1V5a1 1 0 00-1-1z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No {filter === 'all' ? '' : filter} files found</h3>
          <p className="text-gray-600 mb-4">
            {filter === 'all' 
              ? 'Your uploaded content will appear here.' 
              : `No ${filter} files in your library.`}
          </p>
          <Link 
            to="/upload" 
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 inline-block"
          >
            Upload Your First {filter === 'all' ? 'Content' : filter.charAt(0).toUpperCase() + filter.slice(1)}
          </Link>
        </div>
      )}
    </div>
  );
};

export default LibraryPage;
