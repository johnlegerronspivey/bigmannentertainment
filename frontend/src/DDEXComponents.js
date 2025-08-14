import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// DDEX ERN (Electronic Release Notification) Creator
export const DDEXERNCreator = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    artist_name: '',
    label_name: 'Big Mann Entertainment',
    release_date: '',
    release_type: 'Single',
    territories: 'Worldwide'
  });
  const [audioFile, setAudioFile] = useState(null);
  const [coverImage, setCoverImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!audioFile) {
      setMessage('Please select an audio file');
      return;
    }

    setLoading(true);
    setMessage('');

    const submitData = new FormData();
    Object.keys(formData).forEach(key => {
      submitData.append(key, formData[key]);
    });
    submitData.append('audio_file', audioFile);
    if (coverImage) {
      submitData.append('cover_image', coverImage);
    }

    try {
      const response = await axios.post(`${API}/ddex/ern/create`, submitData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMessage('ERN message created successfully!');
      setFormData({
        title: '',
        artist_name: '',
        label_name: 'Big Mann Entertainment',
        release_date: '',
        release_type: 'Single',
        territories: 'Worldwide'
      });
      setAudioFile(null);
      setCoverImage(null);
      
      // Reset file inputs
      const fileInputs = document.querySelectorAll('input[type="file"]');
      fileInputs.forEach(input => input.value = '');
      
      if (onSuccess) onSuccess(response.data);
      
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to create ERN message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6">Create ERN (Electronic Release Notification)</h2>
      <p className="text-gray-600 mb-6">
        Generate DDEX-compliant XML for digital music distribution to streaming platforms like Spotify, Apple Music, Amazon Music, etc.
      </p>
      
      {message && (
        <div className={`mb-6 p-4 rounded-md ${
          message.includes('successfully') 
            ? 'bg-green-100 border border-green-400 text-green-700'
            : 'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Track Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Artist Name *
            </label>
            <input
              type="text"
              value={formData.artist_name}
              onChange={(e) => setFormData({ ...formData, artist_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Label Name *
            </label>
            <input
              type="text"
              value={formData.label_name}
              onChange={(e) => setFormData({ ...formData, label_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Release Date *
            </label>
            <input
              type="date"
              value={formData.release_date}
              onChange={(e) => setFormData({ ...formData, release_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Release Type
            </label>
            <select
              value={formData.release_type}
              onChange={(e) => setFormData({ ...formData, release_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="Single">Single</option>
              <option value="Album">Album</option>
              <option value="EP">EP</option>
              <option value="Compilation">Compilation</option>
              <option value="Live">Live</option>
              <option value="Remix">Remix</option>
              <option value="Soundtrack">Soundtrack</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Territory
            </label>
            <select
              value={formData.territories}
              onChange={(e) => setFormData({ ...formData, territories: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="Worldwide">Worldwide</option>
              <option value="US">United States</option>
              <option value="CA">Canada</option>
              <option value="GB">United Kingdom</option>
              <option value="DE">Germany</option>
              <option value="FR">France</option>
              <option value="JP">Japan</option>
              <option value="AU">Australia</option>
            </select>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Audio File *
          </label>
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setAudioFile(e.target.files[0])}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          />
          <p className="text-sm text-gray-500 mt-1">Supported formats: MP3, WAV, FLAC, AAC</p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cover Image (Optional)
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setCoverImage(e.target.files[0])}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <p className="text-sm text-gray-500 mt-1">Recommended: 3000x3000px, JPEG/PNG</p>
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Creating ERN Message...' : 'Create ERN Message'}
        </button>
      </form>
    </div>
  );
};

// DDEX CWR (Common Works Registration) Creator  
export const DDEXCWRCreator = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    composer_name: '',
    lyricist_name: '',
    publisher_name: '',
    performing_rights_org: 'ASCAP',
    duration: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    const submitData = new FormData();
    Object.keys(formData).forEach(key => {
      if (formData[key]) {
        submitData.append(key, formData[key]);
      }
    });

    try {
      const response = await axios.post(`${API}/ddex/cwr/register-work`, submitData);
      
      setMessage('Musical work registered successfully!');
      setFormData({
        title: '',
        composer_name: '',
        lyricist_name: '',
        publisher_name: '',
        performing_rights_org: 'ASCAP',
        duration: ''
      });
      
      if (onSuccess) onSuccess(response.data);
      
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to register musical work');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6">Register Musical Work (CWR)</h2>
      <p className="text-gray-600 mb-6">
        Register your musical compositions with Performance Rights Organizations (PROs) like ASCAP, BMI, and SESAC.
      </p>
      
      {message && (
        <div className={`mb-6 p-4 rounded-md ${
          message.includes('successfully') 
            ? 'bg-green-100 border border-green-400 text-green-700'
            : 'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Work Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Composer Name *
            </label>
            <input
              type="text"
              value={formData.composer_name}
              onChange={(e) => setFormData({ ...formData, composer_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lyricist Name (Optional)
            </label>
            <input
              type="text"
              value={formData.lyricist_name}
              onChange={(e) => setFormData({ ...formData, lyricist_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Publisher Name (Optional)
            </label>
            <input
              type="text"
              value={formData.publisher_name}
              onChange={(e) => setFormData({ ...formData, publisher_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Performance Rights Organization *
            </label>
            <select
              value={formData.performing_rights_org}
              onChange={(e) => setFormData({ ...formData, performing_rights_org: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            >
              <option value="ASCAP">ASCAP</option>
              <option value="BMI">BMI</option>
              <option value="SESAC">SESAC</option>
              <option value="GMR">GMR (Global Music Rights)</option>
              <option value="SOCAN">SOCAN (Canada)</option>
              <option value="PRS">PRS for Music (UK)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration (Optional)
            </label>
            <input
              type="text"
              value={formData.duration}
              onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="PT3M30S (3 minutes 30 seconds)"
            />
            <p className="text-sm text-gray-500 mt-1">ISO 8601 duration format (e.g., PT3M30S)</p>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50"
        >
          {loading ? 'Registering Work...' : 'Register Musical Work'}
        </button>
      </form>
    </div>
  );
};

// DDEX Message List
export const DDEXMessageList = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchMessages();
  }, [filter]);

  const fetchMessages = async () => {
    try {
      const params = new URLSearchParams();
      if (filter) params.append('message_type', filter);
      
      const response = await axios.get(`${API}/ddex/messages?${params}`);
      setMessages(response.data.messages);
    } catch (error) {
      console.error('Error fetching DDEX messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadXML = async (messageId, filename) => {
    try {
      const response = await axios.get(`${API}/ddex/messages/${messageId}/xml`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/xml' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading XML:', error);
      alert('Failed to download XML file');
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
        <p className="text-center mt-4 text-gray-600">Loading DDEX messages...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">DDEX Messages</h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">All Messages</option>
          <option value="ERN">ERN Messages</option>
          <option value="CWR">CWR Registrations</option>
        </select>
      </div>
      
      {messages.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📄</div>
          <p className="text-gray-600">No DDEX messages found. Create your first ERN or CWR message above.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    message.message_type === 'ERN' 
                      ? 'bg-purple-100 text-purple-600' 
                      : 'bg-orange-100 text-orange-600'
                  }`}>
                    {message.message_type}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    message.status === 'Created' || message.status === 'Registered'
                      ? 'bg-green-100 text-green-600'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {message.status}
                  </span>
                </div>
                <button
                  onClick={() => downloadXML(message.id, message.xml_filename)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
                >
                  Download XML
                </button>
              </div>
              
              <h3 className="text-lg font-semibold mb-2">{message.title}</h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                {message.message_type === 'ERN' ? (
                  <>
                    <div>
                      <span className="font-medium">Artist:</span><br />
                      {message.artist_name}
                    </div>
                    <div>
                      <span className="font-medium">Label:</span><br />
                      {message.label_name}
                    </div>
                    <div>
                      <span className="font-medium">ISRC:</span><br />
                      <span className="font-mono text-xs">{message.isrc}</span>
                    </div>
                    <div>
                      <span className="font-medium">Catalog:</span><br />
                      <span className="font-mono text-xs">{message.catalog_number}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div>
                      <span className="font-medium">Composer:</span><br />
                      {message.composer_name}
                    </div>
                    <div>
                      <span className="font-medium">PRO:</span><br />
                      {message.performing_rights_org}
                    </div>
                    <div>
                      <span className="font-medium">ISWC:</span><br />
                      <span className="font-mono text-xs">{message.iswc}</span>
                    </div>
                    <div>
                      <span className="font-medium">Work ID:</span><br />
                      <span className="font-mono text-xs">{message.work_id}</span>
                    </div>
                  </>
                )}
              </div>
              
              <div className="mt-3 text-xs text-gray-500">
                Created: {new Date(message.created_at).toLocaleString()}
                {message.message_id && (
                  <span className="ml-4">Message ID: {message.message_id || message.registration_id}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// DDEX Identifier Generator
export const DDEXIdentifierGenerator = () => {
  const [identifierType, setIdentifierType] = useState('isrc');
  const [count, setCount] = useState(1);
  const [identifiers, setIdentifiers] = useState([]);
  const [loading, setLoading] = useState(false);

  const generateIdentifiers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/ddex/identifiers/generate`, {
        params: { identifier_type: identifierType, count }
      });
      setIdentifiers(response.data.identifiers);
    } catch (error) {
      console.error('Error generating identifiers:', error);
      alert('Failed to generate identifiers');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (identifier) => {
    navigator.clipboard.writeText(identifier);
    // You could add a toast notification here
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-6">Generate Music Industry Identifiers</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Identifier Type
          </label>
          <select
            value={identifierType}
            onChange={(e) => setIdentifierType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="isrc">ISRC (International Standard Recording Code)</option>
            <option value="iswc">ISWC (International Standard Musical Work Code)</option>
            <option value="catalog_number">Catalog Number</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Count (1-10)
          </label>
          <input
            type="number"
            min="1"
            max="10"
            value={count}
            onChange={(e) => setCount(parseInt(e.target.value) || 1)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
        
        <div className="flex items-end">
          <button
            onClick={generateIdentifiers}
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-md transition-colors disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>
      
      {identifiers.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Generated Identifiers</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {identifiers.map((identifier, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-mono text-sm">{identifier}</span>
                <button
                  onClick={() => copyToClipboard(identifier)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm transition-colors"
                >
                  Copy
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-800 mb-2">What are these identifiers?</h4>
            <div className="text-sm text-blue-700">
              {identifierType === 'isrc' && (
                <p><strong>ISRC:</strong> Unique identifier for sound recordings. Required for digital distribution to streaming platforms and radio.</p>
              )}
              {identifierType === 'iswc' && (
                <p><strong>ISWC:</strong> Unique identifier for musical compositions/works. Used by PROs for royalty collection and distribution.</p>
              )}
              {identifierType === 'catalog_number' && (
                <p><strong>Catalog Number:</strong> Label-specific identifier for releases. Used for internal tracking and distribution coordination.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// DDEX Admin Dashboard (for admins only)
export const DDEXAdminDashboard = () => {
  const [statistics, setStatistics] = useState({});
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatistics();
    fetchAllMessages();
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${API}/ddex/admin/statistics`);
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching DDEX statistics:', error);
    }
  };

  const fetchAllMessages = async () => {
    try {
      const response = await axios.get(`${API}/ddex/admin/messages?limit=20`);
      setMessages(response.data.messages);
    } catch (error) {
      console.error('Error fetching DDEX messages:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
        <p className="text-center mt-4 text-gray-600">Loading DDEX statistics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Messages</p>
              <p className="text-3xl font-bold text-purple-600">{statistics.total_messages || 0}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">ERN Messages</p>
              <p className="text-3xl font-bold text-blue-600">{statistics.ern_messages || 0}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">CWR Registrations</p>
              <p className="text-3xl font-bold text-orange-600">{statistics.cwr_registrations || 0}</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Recent Activity</p>
              <p className="text-3xl font-bold text-green-600">{statistics.recent_activity?.total_30_days || 0}</p>
              <p className="text-xs text-gray-500">Last 30 days</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Messages */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Recent DDEX Messages</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {messages.map((message) => (
                <tr key={message.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      message.message_type === 'ERN' 
                        ? 'bg-purple-100 text-purple-800' 
                        : 'bg-orange-100 text-orange-800'
                    }`}>
                      {message.message_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {message.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {message.user?.full_name || message.user?.email || 'Unknown'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      (message.status === 'Created' || message.status === 'Registered') 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {message.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(message.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};