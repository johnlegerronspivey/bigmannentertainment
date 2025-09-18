import React, { useState, useRef, useEffect } from 'react';
import './ImageUpload.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://content-workflow-1.preview.emergentagent.com';

const MediaUploadComponent = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadStatus, setUploadStatus] = useState({});
  const [userMedia, setUserMedia] = useState([]);
  const [distributions, setDistributions] = useState([]);
  const [earnings, setEarnings] = useState(null);
  const [platforms, setPlatforms] = useState({});
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  // Get auth token
  const getAuthToken = () => {
    return localStorage.getItem('token') || localStorage.getItem('access_token');
  };

  // Fetch user's media files
  const fetchUserMedia = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/media/`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserMedia(data.media_files || []);
      }
    } catch (error) {
      console.error('Error fetching media:', error);
    }
  };

  // Fetch available platforms
  const fetchPlatforms = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/distribution/platforms`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlatforms(data.platforms || {});
      }
    } catch (error) {
      console.error('Error fetching platforms:', error);
    }
  };

  // Fetch user earnings
  const fetchEarnings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/media/earnings`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEarnings(data);
      }
    } catch (error) {
      console.error('Error fetching earnings:', error);
    }
  };

  // Fetch distributions
  const fetchDistributions = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/media/distributions`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDistributions(data.distributions || []);
      }
    } catch (error) {
      console.error('Error fetching distributions:', error);
    }
  };

  useEffect(() => {
    fetchUserMedia();
    fetchPlatforms();
    fetchEarnings();
    fetchDistributions();
  }, []);

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
    setError('');
    setSuccess('');
  };

  const uploadFile = async (file, title, description, category) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('description', description);
    formData.append('category', category);

    try {
      setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));
      setUploadStatus(prev => ({ ...prev, [file.name]: 'uploading' }));

      const response = await fetch(`${BACKEND_URL}/api/media/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setUploadProgress(prev => ({ ...prev, [file.name]: 100 }));
        setUploadStatus(prev => ({ ...prev, [file.name]: 'completed' }));
        setSuccess(`${file.name} uploaded successfully!`);
        
        // Refresh media list
        fetchUserMedia();
        
        return result;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }
    } catch (error) {
      setUploadStatus(prev => ({ ...prev, [file.name]: 'failed' }));
      setError(`Upload failed for ${file.name}: ${error.message}`);
      throw error;
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select files to upload');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const uploadPromises = selectedFiles.map((file, index) => {
        const title = document.getElementById(`title-${index}`)?.value || file.name;
        const description = document.getElementById(`description-${index}`)?.value || '';
        const category = document.getElementById(`category-${index}`)?.value || 'music';
        
        return uploadFile(file, title, description, category);
      });

      await Promise.all(uploadPromises);
      setSelectedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDistribute = async (mediaId, selectedPlatforms) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${BACKEND_URL}/api/media/distribute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
          media_id: mediaId,
          platforms: selectedPlatforms,
          pricing_tier: 'basic'
        })
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(`Successfully distributed to ${result.platforms_submitted} platforms!`);
        fetchDistributions();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Distribution failed');
      }
    } catch (error) {
      setError(`Distribution failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const requestPayout = async (amount, method, details) => {
    try {
      setLoading(true);
      
      const formData = new FormData();
      formData.append('amount', amount);
      formData.append('payout_method', method);
      formData.append('payout_details', details);

      const response = await fetch(`${BACKEND_URL}/api/media/request-payout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(`Payout request submitted successfully! You will receive $${result.payout_details.net_amount.toFixed(2)} after processing.`);
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Payout request failed');
      }
    } catch (error) {
      setError(`Payout request failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="media-upload-container">
      <div className="upload-header">
        <img 
          src="https://customer-assets.emergentagent.com/job_rightshub-1/artifacts/st1hihar_Big%20Mann%20Entertainment%20Logo.png" 
          alt="Big Mann Entertainment" 
          className="logo"
        />
        <h1>🎵 Media Distribution Hub</h1>
        <p>Upload, distribute, and monetize your content across 106+ platforms</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">❌</span>
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <span className="alert-icon">✅</span>
          {success}
        </div>
      )}

      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 Upload Media
        </button>
        <button 
          className={`tab-button ${activeTab === 'distribute' ? 'active' : ''}`}
          onClick={() => setActiveTab('distribute')}
        >
          🌐 Distribute
        </button>
        <button 
          className={`tab-button ${activeTab === 'earnings' ? 'active' : ''}`}
          onClick={() => setActiveTab('earnings')}
        >
          💰 Earnings
        </button>
        <button 
          className={`tab-button ${activeTab === 'payouts' ? 'active' : ''}`}
          onClick={() => setActiveTab('payouts')}
        >
          🏦 Payouts
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="upload-section">
          <h2>📤 Upload Your Media</h2>
          
          <div className="file-input-container">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              multiple
              accept="audio/*,video/*,image/*"
              className="file-input"
            />
            <label className="file-input-label">
              Choose Files (Audio, Video, Images)
            </label>
          </div>

          {selectedFiles.length > 0 && (
            <div className="selected-files">
              <h3>Selected Files ({selectedFiles.length})</h3>
              {selectedFiles.map((file, index) => (
                <div key={index} className="file-item">
                  <div className="file-info">
                    <strong>{file.name}</strong>
                    <span className="file-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                  </div>
                  
                  <div className="file-metadata">
                    <input
                      id={`title-${index}`}
                      type="text"
                      placeholder="Title"
                      defaultValue={file.name.replace(/\.[^/.]+$/, "")}
                      className="metadata-input"
                    />
                    <input
                      id={`description-${index}`}
                      type="text"
                      placeholder="Description (optional)"
                      className="metadata-input"
                    />
                    <select id={`category-${index}`} className="metadata-select">
                      <option value="music">Music</option>
                      <option value="video">Video</option>
                      <option value="image">Image</option>
                    </select>
                  </div>

                  {uploadProgress[file.name] !== undefined && (
                    <div className="upload-progress">
                      <div 
                        className="progress-bar"
                        style={{ width: `${uploadProgress[file.name]}%` }}
                      ></div>
                      <span className="progress-text">
                        {uploadStatus[file.name]} - {uploadProgress[file.name]}%
                      </span>
                    </div>
                  )}
                </div>
              ))}
              
              <button 
                onClick={handleUpload}
                disabled={loading}
                className="upload-button"
              >
                {loading ? '⏳ Uploading...' : '🚀 Upload All Files'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Distribute Tab */}
      {activeTab === 'distribute' && (
        <div className="distribute-section">
          <h2>🌐 Distribute Your Media</h2>
          
          <div className="media-list">
            {userMedia.map((media) => (
              <div key={media.id} className="media-card">
                <div className="media-info">
                  <h3>{media.title}</h3>
                  <p>{media.description}</p>
                  <span className="media-type">{media.file_type}</span>
                  <span className="upload-date">
                    Uploaded: {new Date(media.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="platform-selection">
                  <h4>Select Platforms:</h4>
                  <div className="platform-grid">
                    {Object.entries(platforms).map(([id, platform]) => (
                      <label key={id} className="platform-checkbox">
                        <input
                          type="checkbox"
                          value={id}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedPlatforms(prev => [...prev, id]);
                            } else {
                              setSelectedPlatforms(prev => prev.filter(p => p !== id));
                            }
                          }}
                        />
                        <span className="platform-name">{platform.name}</span>
                        <span className="platform-share">{(platform.revenue_share * 100).toFixed(0)}% share</span>
                      </label>
                    ))}
                  </div>
                  
                  <button
                    onClick={() => handleDistribute(media.id, selectedPlatforms)}
                    disabled={selectedPlatforms.length === 0 || loading}
                    className="distribute-button"
                  >
                    {loading ? '⏳ Distributing...' : `🚀 Distribute to ${selectedPlatforms.length} Platforms`}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Earnings Tab */}
      {activeTab === 'earnings' && (
        <div className="earnings-section">
          <h2>💰 Your Earnings</h2>
          
          {earnings && (
            <div className="earnings-dashboard">
              <div className="earnings-summary">
                <div className="summary-card">
                  <h3>Total Earnings</h3>
                  <div className="amount">${earnings.earnings_summary?.total_earnings?.toFixed(2) || '0.00'}</div>
                </div>
                <div className="summary-card">
                  <h3>Total Streams</h3>
                  <div className="amount">{earnings.earnings_summary?.total_streams?.toLocaleString() || '0'}</div>
                </div>
              </div>

              <div className="platform-breakdown">
                <h3>Earnings by Platform</h3>
                {Object.entries(earnings.platform_breakdown || {}).map(([platform, data]) => (
                  <div key={platform} className="platform-earnings">
                    <span className="platform-name">{platform}</span>
                    <span className="platform-streams">{data.streams?.toLocaleString()} streams</span>
                    <span className="platform-earnings-amount">${data.earnings?.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              <div className="media-breakdown">
                <h3>Earnings by Media</h3>
                {Object.entries(earnings.media_breakdown || {}).map(([mediaId, data]) => (
                  <div key={mediaId} className="media-earnings">
                    <span className="media-title">{data.title || 'Untitled'}</span>
                    <span className="media-streams">{data.streams?.toLocaleString()} streams</span>
                    <span className="media-earnings-amount">${data.earnings?.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Payouts Tab */}
      {activeTab === 'payouts' && (
        <div className="payouts-section">
          <h2>🏦 Request Payout</h2>
          
          <div className="payout-form">
            <h3>Request New Payout</h3>
            <div className="form-group">
              <label>Amount ($USD)</label>
              <input
                type="number"
                step="0.01"
                min="1"
                max={earnings?.earnings_summary?.total_earnings || 0}
                placeholder="0.00"
                id="payout-amount"
              />
            </div>
            
            <div className="form-group">
              <label>Payout Method</label>
              <select id="payout-method">
                <option value="paypal">PayPal (2.5% fee)</option>
                <option value="stripe">Stripe (2.9% fee)</option>
                <option value="bank_transfer">Bank Transfer (1.5% fee)</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Payout Details (Email/Account Info)</label>
              <input
                type="text"
                placeholder="paypal@example.com or account details"
                id="payout-details"
              />
            </div>
            
            <button
              onClick={() => {
                const amount = parseFloat(document.getElementById('payout-amount').value);
                const method = document.getElementById('payout-method').value;
                const details = document.getElementById('payout-details').value;
                
                if (amount && method && details) {
                  requestPayout(amount, method, details);
                } else {
                  setError('Please fill in all payout fields');
                }
              }}
              disabled={loading}
              className="payout-button"
            >
              {loading ? '⏳ Processing...' : '💸 Request Payout'}
            </button>
          </div>
          
          <div className="available-balance">
            <h4>Available Balance: ${earnings?.earnings_summary?.total_earnings?.toFixed(2) || '0.00'}</h4>
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaUploadComponent;