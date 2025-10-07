import React, { useState, useEffect } from 'react';
import axios from 'axios';
import QRCode from 'qrcode';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Component for Creating/Editing Profile
export const ProfileEditor = ({ user, onSave }) => {
  const [formData, setFormData] = useState({
    displayName: '',
    tagline: '',
    bio: '',
    location: '',
    avatarUrl: '',
    profilePublic: true,
    showEarnings: false,
    showDaoActivity: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (user) {
      fetchProfile();
    }
  }, [user]);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/profile/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.identity) {
        setFormData({
          displayName: response.data.identity.displayName || '',
          tagline: response.data.identity.tagline || '',
          bio: response.data.identity.bio || '',
          location: response.data.identity.location || '',
          avatarUrl: response.data.identity.avatarUrl || '',
          profilePublic: response.data.identity.profilePublic !== false,
          showEarnings: response.data.identity.showEarnings === true,
          showDaoActivity: response.data.identity.showDaoActivity !== false
        });
      }
    } catch (err) {
      console.log('No existing profile, creating new');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/profile/me`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSuccess(true);
      if (onSave) onSave();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl shadow-xl p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Edit Profile</h2>
      
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-500/20 border border-green-500 text-green-200 px-4 py-3 rounded mb-4">
          Profile updated successfully!
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Display Name</label>
          <input
            type="text"
            value={formData.displayName}
            onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Tagline</label>
          <input
            type="text"
            value={formData.tagline}
            onChange={(e) => setFormData({ ...formData, tagline: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            placeholder="Your creative tagline"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Bio</label>
          <textarea
            value={formData.bio}
            onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            rows="4"
            placeholder="Tell your story..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Location</label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            placeholder="City, Country"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Avatar URL</label>
          <input
            type="url"
            value={formData.avatarUrl}
            onChange={(e) => setFormData({ ...formData, avatarUrl: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            placeholder="https://..."
          />
        </div>

        <div className="space-y-3">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={formData.profilePublic}
              onChange={(e) => setFormData({ ...formData, profilePublic: e.target.checked })}
              className="w-5 h-5 text-purple-600"
            />
            <span className="text-gray-300">Make profile public</span>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={formData.showEarnings}
              onChange={(e) => setFormData({ ...formData, showEarnings: e.target.checked })}
              className="w-5 h-5 text-purple-600"
            />
            <span className="text-gray-300">Show earnings publicly</span>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={formData.showDaoActivity}
              onChange={(e) => setFormData({ ...formData, showDaoActivity: e.target.checked })}
              className="w-5 h-5 text-purple-600"
            />
            <span className="text-gray-300">Show DAO activity</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
};

// Social Media Connection Manager
export const SocialMediaConnections = () => {
  const [connections, setConnections] = useState({
    facebook: { configured: false, connected: false },
    tiktok: { configured: false, connected: false },
    google_youtube: { configured: false, connected: false },
    twitter: { configured: false, connected: false }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConnectionStatus();
  }, []);

  const fetchConnectionStatus = async () => {
    try {
      const response = await axios.get(`${API}/oauth/status`);
      setConnections(response.data);
    } catch (err) {
      console.error('Failed to fetch connection status:', err);
    } finally {
      setLoading(false);
    }
  };

  const connectPlatform = (platform) => {
    window.location.href = `${API}/oauth/connect/${platform}`;
  };

  const disconnectPlatform = async (platform) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/oauth/disconnect/${platform}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchConnectionStatus();
    } catch (err) {
      console.error('Failed to disconnect:', err);
    }
  };

  const platformInfo = {
    facebook: { name: 'Facebook & Instagram', icon: '📘', color: 'blue' },
    tiktok: { name: 'TikTok', icon: '🎵', color: 'pink' },
    google_youtube: { name: 'YouTube', icon: '▶️', color: 'red' },
    twitter: { name: 'Twitter/X', icon: '🐦', color: 'sky' }
  };

  if (loading) {
    return <div className="text-white">Loading connections...</div>;
  }

  return (
    <div className="bg-gray-800 rounded-xl shadow-xl p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Social Media Connections</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(connections).map(([platform, status]) => {
          const info = platformInfo[platform];
          
          return (
            <div key={platform} className="bg-gray-900 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{info.icon}</span>
                  <div>
                    <h3 className="text-white font-semibold">{info.name}</h3>
                    <p className="text-sm text-gray-400">
                      {status.configured ? (status.connected ? 'Connected' : 'Ready to connect') : 'Not configured'}
                    </p>
                  </div>
                </div>
                {status.configured && status.connected && (
                  <span className="text-green-400">✓</span>
                )}
              </div>
              
              {status.configured ? (
                <button
                  onClick={() => status.connected ? disconnectPlatform(platform) : connectPlatform(platform)}
                  className={`w-full px-4 py-2 rounded-lg font-semibold transition-colors ${
                    status.connected
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : `bg-${info.color}-600 hover:bg-${info.color}-700 text-white`
                  }`}
                >
                  {status.connected ? 'Disconnect' : 'Connect'}
                </button>
              ) : (
                <div className="text-sm text-gray-500 italic">
                  Contact admin to configure this platform
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// DAO Proposal Creator
export const ProposalCreator = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    proposalType: 'royalty_adjustment',
    votingEndsInDays: 7,
    targetAssetId: '',
    targetData: {}
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/profile/dao/proposals`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (onSuccess) onSuccess();
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        proposalType: 'royalty_adjustment',
        votingEndsInDays: 7,
        targetAssetId: '',
        targetData: {}
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create proposal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl shadow-xl p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Create DAO Proposal</h2>
      
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
            rows="4"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Proposal Type</label>
          <select
            value={formData.proposalType}
            onChange={(e) => setFormData({ ...formData, proposalType: e.target.value })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
          >
            <option value="royalty_adjustment">Royalty Adjustment</option>
            <option value="platform_addition">Platform Addition</option>
            <option value="policy_change">Policy Change</option>
            <option value="feature_request">Feature Request</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Voting Period (days)</label>
          <input
            type="number"
            min="1"
            max="30"
            value={formData.votingEndsInDays}
            onChange={(e) => setFormData({ ...formData, votingEndsInDays: parseInt(e.target.value) })}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create Proposal'}
        </button>
      </form>
    </div>
  );
};

// DAO Voting Interface
export const ProposalList = () => {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('open');

  useEffect(() => {
    fetchProposals();
  }, [filter]);

  const fetchProposals = async () => {
    try {
      const response = await axios.get(`${API}/profile/dao/proposals`, {
        params: { status: filter === 'all' ? null : filter }
      });
      setProposals(response.data.proposals);
    } catch (err) {
      console.error('Failed to fetch proposals:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-white">Loading proposals...</div>;
  }

  return (
    <div className="bg-gray-800 rounded-xl shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">DAO Proposals</h2>
        
        <div className="flex gap-2">
          {['open', 'approved', 'rejected', 'all'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                filter === f
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {proposals.length > 0 ? (
          proposals.map((proposal) => (
            <div key={proposal.id} className="bg-gray-900 rounded-lg p-6 border border-gray-700">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">{proposal.title}</h3>
                  <p className="text-gray-400 mb-3">{proposal.description}</p>
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      proposal.status === 'open' ? 'bg-green-500/20 text-green-400' :
                      proposal.status === 'approved' ? 'bg-blue-500/20 text-blue-400' :
                      proposal.status === 'rejected' ? 'bg-red-500/20 text-red-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {proposal.status}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(proposal.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Vote Counts */}
              <div className="grid grid-cols-3 gap-4 bg-gray-800 rounded-lg p-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{proposal.votes.yes}</div>
                  <div className="text-sm text-gray-400">Yes</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-400">{proposal.votes.no}</div>
                  <div className="text-sm text-gray-400">No</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-400">{proposal.votes.total}</div>
                  <div className="text-sm text-gray-400">Total</div>
                </div>
              </div>

              {/* View Details Button */}
              <a
                href={`/dao/proposal/${proposal.id}`}
                className="block w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors text-center"
              >
                View Details & Vote
              </a>
            </div>
          ))
        ) : (
          <div className="text-center py-12 text-gray-400">
            No {filter !== 'all' ? filter : ''} proposals found
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced QR Code Display Component with Download
export const QRCodeDisplay = ({ data, title, assetTitle }) => {
  const [qrCodeUrl, setQrCodeUrl] = useState(null);

  useEffect(() => {
    generateQRCode();
  }, [data]);

  const generateQRCode = async () => {
    try {
      const url = await QRCode.toDataURL(data, {
        width: 300,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        },
        errorCorrectionLevel: 'H'  // High error correction for logo overlay
      });
      setQrCodeUrl(url);
    } catch (err) {
      console.error('Failed to generate QR code:', err);
    }
  };

  const handleDownload = () => {
    if (!qrCodeUrl) return;
    
    const link = document.createElement('a');
    link.download = `${assetTitle || 'qr_code'}_${Date.now()}.png`;
    link.href = qrCodeUrl;
    link.click();
  };

  return (
    <div className="bg-gray-900 rounded-lg p-4 text-center">
      {title && <h4 className="text-white font-semibold mb-3">{title}</h4>}
      {qrCodeUrl ? (
        <div>
          <div className="relative inline-block">
            <img src={qrCodeUrl} alt="QR Code" className="mx-auto rounded" />
            {/* BME Logo Overlay Indicator */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-purple-600 rounded text-white text-xs px-2 py-1 font-bold">
              BME
            </div>
          </div>
          <button
            onClick={handleDownload}
            className="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors inline-flex items-center gap-2"
          >
            <span>⬇️</span>
            <span>Download QR Code</span>
          </button>
        </div>
      ) : (
        <div className="w-[300px] h-[300px] bg-gray-800 flex items-center justify-center mx-auto">
          <span className="text-gray-500">Generating QR code...</span>
        </div>
      )}
      <p className="text-xs text-gray-500 mt-2 break-all">{data}</p>
    </div>
  );
};