import React, { useState, useRef, useEffect } from 'react';
import './ImageUpload.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://creator-profile-hub-2.preview.emergentagent.com';

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
    return localStorage.getItem('access_token');
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
      const response = await fetch(`${BACKEND_URL}/api/media/platforms`, {
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

export { MediaUploadComponent };
import './ImageUpload.css';

const ImageUploadComponent = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedFiles, setSelectedFiles] = useState([]); // For batch upload
    const [preview, setPreview] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState(null);
    const [error, setError] = useState('');
    const [metadataStandards, setMetadataStandards] = useState(null);
    const [userImages, setUserImages] = useState([]);
    const [modelReleases, setModelReleases] = useState([]);
    const [isBatchMode, setIsBatchMode] = useState(false);
    const [web3Config, setWeb3Config] = useState({
        enableNFT: false,
        blockchain: 'polygon',
        tokenStandard: 'ERC721'
    });
    const [royaltyRecipients, setRoyaltyRecipients] = useState([
        { address: '', percentage: 100, role: 'creator' }
    ]);
    const [daoGovernance, setDaoGovernance] = useState({
        enableDAO: false,
        proposalType: 'licensing_terms',
        votingPeriod: 7
    });
    
    const fileInputRef = useRef(null);
    const batchFileInputRef = useRef(null);
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

    // Form data state
    const [formData, setFormData] = useState({
        modelName: '',
        agencyName: '',
        photographerName: '',
        shootDate: '',
        usageRights: 'editorial_only',
        territoryRights: 'worldwide',
        durationRights: 'perpetual',
        exclusive: false,
        headline: '',
        caption: '',
        keywords: '',
        copyrightNotice: '',
        licenseTerms: '',
        contentRating: 'general',
        targetAgencies: [],
        basePricing: '',
        maxResolution: '4000'
    });

    useEffect(() => {
        fetchMetadataStandards();
        fetchUserImages();
        fetchModelReleases();
    }, []);

    const fetchMetadataStandards = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/images/metadata-standards`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setMetadataStandards(data);
            }
        } catch (error) {
            console.error('Error fetching metadata standards:', error);
        }
    };

    const fetchUserImages = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/images/user/images?limit=10`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUserImages(data.images);
            }
        } catch (error) {
            console.error('Error fetching user images:', error);
        }
    };

    const fetchModelReleases = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${backendUrl}/api/images/model-releases?limit=10`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setModelReleases(data.releases);
            }
        } catch (error) {
            console.error('Error fetching model releases:', error);
        }
    };

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                setError('Please select an image file');
                return;
            }

            // Validate file size (500MB limit)
            const maxSize = 500 * 1024 * 1024; // 500MB
            if (file.size > maxSize) {
                setError('File size exceeds 500MB limit');
                return;
            }

            setSelectedFile(file);
            setError('');

            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => setPreview(e.target.result);
            reader.readAsDataURL(file);
        }
    };

    const handleBatchFileSelect = (event) => {
        const files = Array.from(event.target.files);
        const validFiles = [];
        const maxSize = 500 * 1024 * 1024; // 500MB

        files.forEach(file => {
            if (file.type.startsWith('image/') && file.size <= maxSize) {
                validFiles.push(file);
            }
        });

        if (validFiles.length !== files.length) {
            setError(`${files.length - validFiles.length} files were skipped (invalid type or too large)`);
        } else {
            setError('');
        }

        // Create previews for valid files
        const filePromises = validFiles.map(file => {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve({
                    file,
                    preview: e.target.result,
                    id: Date.now() + Math.random()
                });
                reader.readAsDataURL(file);
            });
        });

        Promise.all(filePromises).then(fileData => {
            setSelectedFiles(prev => [...prev, ...fileData]);
        });
    };

    const removeBatchFile = (fileId) => {
        setSelectedFiles(prev => prev.filter(f => f.id !== fileId));
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleAgencySelection = (agencyId) => {
        setFormData(prev => ({
            ...prev,
            targetAgencies: prev.targetAgencies.includes(agencyId)
                ? prev.targetAgencies.filter(id => id !== agencyId)
                : [...prev.targetAgencies, agencyId]
        }));
    };

    const handleWeb3ConfigChange = (e) => {
        const { name, value, type, checked } = e.target;
        setWeb3Config(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleRoyaltyRecipientChange = (index, field, value) => {
        const updated = [...royaltyRecipients];
        updated[index][field] = value;
        
        // Ensure percentages don't exceed 100%
        if (field === 'percentage') {
            const total = updated.reduce((sum, recipient) => sum + Number(recipient.percentage), 0);
            if (total > 100) {
                setError('Total royalty percentages cannot exceed 100%');
                return;
            }
        }
        
        setRoyaltyRecipients(updated);
        setError('');
    };

    const addRoyaltyRecipient = () => {
        const currentTotal = royaltyRecipients.reduce((sum, recipient) => sum + Number(recipient.percentage), 0);
        if (currentTotal >= 100) {
            setError('Cannot add more recipients - total percentage already at 100%');
            return;
        }
        
        setRoyaltyRecipients(prev => [...prev, { address: '', percentage: 0, role: 'contributor' }]);
    };

    const removeRoyaltyRecipient = (index) => {
        if (royaltyRecipients.length > 1) {
            setRoyaltyRecipients(prev => prev.filter((_, i) => i !== index));
        }
    };

    const handleDaoConfigChange = (e) => {
        const { name, value, type, checked } = e.target;
        setDaoGovernance(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const uploadImage = async () => {
        const filesToUpload = isBatchMode ? selectedFiles : (selectedFile ? [{ file: selectedFile, preview }] : []);
        
        if (filesToUpload.length === 0) {
            setError('Please select image file(s) to upload');
            return;
        }

        // Validate required fields for commercial usage
        if (formData.usageRights !== 'editorial_only' && (!formData.modelName || !formData.photographerName || !formData.shootDate)) {
            setError('Model name, photographer name, and shoot date are required for commercial usage');
            return;
        }

        // Validate Web3 configuration if enabled
        if (web3Config.enableNFT) {
            const totalPercentage = royaltyRecipients.reduce((sum, recipient) => sum + Number(recipient.percentage), 0);
            if (totalPercentage !== 100) {
                setError('Royalty percentages must total exactly 100%');
                return;
            }

            for (const recipient of royaltyRecipients) {
                if (!recipient.address || !recipient.address.match(/^0x[a-fA-F0-9]{40}$/)) {
                    setError('All royalty recipients must have valid Ethereum addresses');
                    return;
                }
            }
        }

        setUploading(true);
        setError('');
        setUploadResult(null);

        try {
            const token = localStorage.getItem('token');
            const results = [];

            // Process uploads (single or batch)
            for (const fileData of filesToUpload) {
                const uploadFormData = new FormData();
                
                uploadFormData.append('file', fileData.file);
                uploadFormData.append('model_name', formData.modelName);
                uploadFormData.append('agency_name', formData.agencyName);
                uploadFormData.append('photographer_name', formData.photographerName);
                uploadFormData.append('shoot_date', formData.shootDate);
                uploadFormData.append('usage_rights', formData.usageRights);
                uploadFormData.append('territory_rights', formData.territoryRights);
                uploadFormData.append('duration_rights', formData.durationRights);
                uploadFormData.append('exclusive', formData.exclusive);
                uploadFormData.append('headline', formData.headline);
                uploadFormData.append('caption', formData.caption);
                uploadFormData.append('keywords', formData.keywords);
                uploadFormData.append('copyright_notice', formData.copyrightNotice);
                uploadFormData.append('license_terms', formData.licenseTerms);
                uploadFormData.append('content_rating', formData.contentRating);
                uploadFormData.append('target_agencies', JSON.stringify(formData.targetAgencies));
                uploadFormData.append('base_pricing', formData.basePricing);
                uploadFormData.append('max_resolution', formData.maxResolution);
                
                // Add Web3 configuration
                if (web3Config.enableNFT) {
                    uploadFormData.append('enable_nft', 'true');
                    uploadFormData.append('blockchain', web3Config.blockchain);
                    uploadFormData.append('token_standard', web3Config.tokenStandard);
                    uploadFormData.append('royalty_recipients', JSON.stringify(royaltyRecipients));
                }

                // Add DAO governance configuration
                if (daoGovernance.enableDAO) {
                    uploadFormData.append('enable_dao', 'true');
                    uploadFormData.append('proposal_type', daoGovernance.proposalType);
                    uploadFormData.append('voting_period', daoGovernance.votingPeriod);
                }

                const endpoint = isBatchMode ? '/api/images/batch-upload' : '/api/images/upload';
                const response = await fetch(`${backendUrl}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: uploadFormData
                });

                const result = await response.json();
                results.push({ file: fileData.file, result, success: response.ok });
            }

            // Process results
            const successCount = results.filter(r => r.success).length;
            const failureCount = results.length - successCount;

            if (successCount > 0) {
                setUploadResult({
                    success: true,
                    batch_mode: isBatchMode,
                    total_files: results.length,
                    successful_uploads: successCount,
                    failed_uploads: failureCount,
                    results: results,
                    web3_enabled: web3Config.enableNFT,
                    dao_enabled: daoGovernance.enableDAO
                });

                // Reset form
                if (!isBatchMode) {
                    setSelectedFile(null);
                    setPreview(null);
                } else {
                    setSelectedFiles([]);
                }
                
                setFormData(prev => ({
                    ...prev,
                    modelName: '',
                    agencyName: '',
                    photographerName: '',
                    shootDate: '',
                    headline: '',
                    caption: '',
                    keywords: '',
                    copyrightNotice: '',
                    licenseTerms: '',
                    targetAgencies: []
                }));

                fetchUserImages(); // Refresh images list
            } else {
                const firstError = results.find(r => !r.success);
                setError(firstError?.result?.detail || 'All uploads failed');
            }
        } catch (error) {
            setError('Network error during upload');
            console.error('Upload error:', error);
        } finally {
            setUploading(false);
        }
    };

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className="image-upload-container">
            <div className="image-upload-header">
                <img 
                    src="/big-mann-logo.png" 
                    alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
                    className="upload-logo"
                />
                <h2>📸 Professional Image Upload</h2>
                <p>Upload images with IPTC/XMP metadata and model release compliance</p>
            </div>

            {/* Metadata Standards Info */}
            {metadataStandards && (
                <div className="metadata-standards-info">
                    <h3>🏷️ Supported Metadata Standards</h3>
                    <div className="standards-grid">
                        <div className="standard-card">
                            <h4>IPTC Metadata</h4>
                            <p>International Press Telecommunications Council standard for image metadata</p>
                            <div className="required-fields">
                                <strong>Required for Commercial:</strong> Photographer, Copyright Notice
                            </div>
                        </div>
                        <div className="standard-card">
                            <h4>XMP Metadata</h4>
                            <p>Extensible Metadata Platform for rich metadata embedding</p>
                            <div className="required-fields">
                                <strong>Required for Commercial:</strong> Creator, Rights, Usage Terms
                            </div>
                        </div>
                        <div className="standard-card">
                            <h4>DDEX Compliant</h4>
                            <p>Digital Data Exchange for music and media industry integration</p>
                            <div className="required-fields">
                                <strong>Required for Commercial:</strong> Usage Type, Territory, Duration
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Upload Section */}
            <div className="upload-section">
                <h3>Upload Image</h3>
                
                {/* File Selection */}
                <div className="file-selection">
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileSelect}
                        accept="image/*"
                        style={{ display: 'none' }}
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="file-select-button"
                        disabled={uploading}
                    >
                        📁 Select Image File
                    </button>
                    <p className="file-requirements">
                        Maximum file size: 500MB | Supported formats: JPEG, PNG, TIFF, RAW
                    </p>
                </div>

                {/* File Preview */}
                {preview && (
                    <div className="file-preview">
                        <img src={preview} alt="Preview" className="preview-image" />
                        <div className="preview-info">
                            <p><strong>File:</strong> {selectedFile.name}</p>
                            <p><strong>Size:</strong> {formatFileSize(selectedFile.size)}</p>
                            <p><strong>Type:</strong> {selectedFile.type}</p>
                        </div>
                    </div>
                )}

                {/* Metadata Form */}
                <div className="metadata-form">
                    <h4>📋 Image Metadata & Rights</h4>
                    
                    {/* Basic Information */}
                    <div className="form-section">
                        <h5>Basic Information</h5>
                        <div className="form-grid">
                            <div className="form-group">
                                <label htmlFor="headline">Headline</label>
                                <input
                                    type="text"
                                    id="headline"
                                    name="headline"
                                    value={formData.headline}
                                    onChange={handleInputChange}
                                    placeholder="Image headline"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="photographerName">Photographer Name *</label>
                                <input
                                    type="text"
                                    id="photographerName"
                                    name="photographerName"
                                    value={formData.photographerName}
                                    onChange={handleInputChange}
                                    placeholder="Photographer name"
                                    required
                                />
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="caption">Caption/Description</label>
                            <textarea
                                id="caption"
                                name="caption"
                                value={formData.caption}
                                onChange={handleInputChange}
                                placeholder="Detailed image description"
                                rows="3"
                            />
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="keywords">Keywords (comma-separated)</label>
                            <input
                                type="text"
                                id="keywords"
                                name="keywords"
                                value={formData.keywords}
                                onChange={handleInputChange}
                                placeholder="fashion, portrait, studio, commercial"
                            />
                        </div>
                    </div>

                    {/* Model Information */}
                    <div className="form-section">
                        <h5>Model Information</h5>
                        <div className="form-grid">
                            <div className="form-group">
                                <label htmlFor="modelName">Model Name</label>
                                <input
                                    type="text"
                                    id="modelName"
                                    name="modelName"
                                    value={formData.modelName}
                                    onChange={handleInputChange}
                                    placeholder="Model's full name"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="agencyName">Agency Name</label>
                                <select
                                    id="agencyName"
                                    name="agencyName"
                                    value={formData.agencyName}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select Agency</option>
                                    <option value="img_models">IMG Models</option>
                                    <option value="elite_model_management">Elite Model Management</option>
                                    <option value="ford_models">Ford Models</option>
                                    <option value="wilhelmina_models">Wilhelmina Models</option>
                                    <option value="next_management">Next Management</option>
                                    <option value="women_management">Women Management</option>
                                    <option value="society_management">The Society Management</option>
                                    <option value="storm_models">Storm Models</option>
                                    <option value="premier_model_management">Premier Model Management</option>
                                    <option value="select_model_management">Select Model Management</option>
                                    <option value="la_models">LA Models</option>
                                    <option value="new_york_models">New York Models</option>
                                    <option value="dna_models">DNA Models</option>
                                    <option value="modelwerk">Modelwerk</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label htmlFor="shootDate">Shoot Date</label>
                                <input
                                    type="date"
                                    id="shootDate"
                                    name="shootDate"
                                    value={formData.shootDate}
                                    onChange={handleInputChange}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Rights & Licensing */}
                    <div className="form-section">
                        <h5>Rights & Licensing</h5>
                        <div className="form-grid">
                            <div className="form-group">
                                <label htmlFor="usageRights">Usage Rights *</label>
                                <select
                                    id="usageRights"
                                    name="usageRights"
                                    value={formData.usageRights}
                                    onChange={handleInputChange}
                                    required
                                >
                                    <option value="editorial_only">Editorial Only</option>
                                    <option value="commercial">Commercial Use</option>
                                    <option value="unrestricted">Unrestricted</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label htmlFor="territoryRights">Territory Rights</label>
                                <select
                                    id="territoryRights"
                                    name="territoryRights"
                                    value={formData.territoryRights}
                                    onChange={handleInputChange}
                                >
                                    <option value="worldwide">Worldwide</option>
                                    <option value="north_america">North America</option>
                                    <option value="europe">Europe</option>
                                    <option value="asia">Asia</option>
                                    <option value="us_only">US Only</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label htmlFor="durationRights">Duration Rights</label>
                                <select
                                    id="durationRights"
                                    name="durationRights"
                                    value={formData.durationRights}
                                    onChange={handleInputChange}
                                >
                                    <option value="perpetual">Perpetual</option>
                                    <option value="1_year">1 Year</option>
                                    <option value="5_years">5 Years</option>
                                    <option value="10_years">10 Years</option>
                                </select>
                            </div>
                        </div>
                        
                        <div className="form-group">
                            <label htmlFor="copyrightNotice">Copyright Notice *</label>
                            <input
                                type="text"
                                id="copyrightNotice"
                                name="copyrightNotice"
                                value={formData.copyrightNotice}
                                onChange={handleInputChange}
                                placeholder="© 2025 Photographer Name. All rights reserved."
                                required
                            />
                        </div>
                        
                        <div className="form-group">
                            <label>
                                <input
                                    type="checkbox"
                                    name="exclusive"
                                    checked={formData.exclusive}
                                    onChange={handleInputChange}
                                />
                                Exclusive Rights
                            </label>
                        </div>
                    </div>

                    {/* Content Rating */}
                    <div className="form-section">
                        <h5>Content Rating</h5>
                        <div className="form-group">
                            <label htmlFor="contentRating">Content Rating</label>
                            <select
                                id="contentRating"
                                name="contentRating"
                                value={formData.contentRating}
                                onChange={handleInputChange}
                            >
                                <option value="general">General</option>
                                <option value="mature">Mature</option>
                                <option value="adult">Adult</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Batch Upload Toggle */}
                <div className="form-section">
                    <label>
                        <input
                            type="checkbox"
                            checked={isBatchMode}
                            onChange={(e) => setIsBatchMode(e.target.checked)}
                        />
                        Enable Batch Upload Mode
                    </label>
                </div>

                {/* Batch Upload Section */}
                {isBatchMode && (
                    <div className="batch-upload">
                        <h3>📁 Batch Image Upload</h3>
                        <input
                            type="file"
                            ref={batchFileInputRef}
                            onChange={handleBatchFileSelect}
                            accept="image/*"
                            multiple
                            style={{ display: 'none' }}
                        />
                        <button
                            onClick={() => batchFileInputRef.current?.click()}
                            className="file-select-button"
                            disabled={uploading}
                        >
                            📎 Select Multiple Images
                        </button>
                        
                        {selectedFiles.length > 0 && (
                            <div className="batch-files-grid">
                                {selectedFiles.map((fileData) => (
                                    <div key={fileData.id} className="batch-file-item">
                                        <img src={fileData.preview} alt="Batch preview" />
                                        <div className="batch-file-info">
                                            <div>{fileData.file.name}</div>
                                            <div>{formatFileSize(fileData.file.size)}</div>
                                        </div>
                                        <button
                                            onClick={() => removeBatchFile(fileData.id)}
                                            className="remove-batch-file"
                                        >
                                            ×
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Web3 NFT Integration */}
                <div className="web3-integration">
                    <h3>🔗 Web3 NFT Licensing</h3>
                    
                    <div className="form-group">
                        <label>
                            <input
                                type="checkbox"
                                name="enableNFT"
                                checked={web3Config.enableNFT}
                                onChange={handleWeb3ConfigChange}
                            />
                            Enable NFT Minting for Image Licensing
                        </label>
                    </div>

                    {web3Config.enableNFT && (
                        <>
                            <div className="form-grid">
                                <div className="form-group">
                                    <label htmlFor="blockchain">Blockchain Network</label>
                                    <select
                                        id="blockchain"
                                        name="blockchain"
                                        value={web3Config.blockchain}
                                        onChange={handleWeb3ConfigChange}
                                    >
                                        <option value="polygon">Polygon (Recommended - Low Gas)</option>
                                        <option value="ethereum">Ethereum (Higher Gas)</option>
                                        <option value="base">Base (Fast & Cheap)</option>
                                    </select>
                                </div>
                                
                                <div className="form-group">
                                    <label htmlFor="tokenStandard">Token Standard</label>
                                    <select
                                        id="tokenStandard"
                                        name="tokenStandard"
                                        value={web3Config.tokenStandard}
                                        onChange={handleWeb3ConfigChange}
                                    >
                                        <option value="ERC721">ERC-721 (Unique NFT)</option>
                                        <option value="ERC1155">ERC-1155 (Batch Mintable)</option>
                                    </select>
                                </div>
                            </div>

                            <div className="royalty-splits">
                                <h4>💰 Royalty Distribution</h4>
                                {royaltyRecipients.map((recipient, index) => (
                                    <div key={index} className="royalty-recipient">
                                        <input
                                            type="text"
                                            placeholder="Ethereum address (0x...)"
                                            value={recipient.address}
                                            onChange={(e) => handleRoyaltyRecipientChange(index, 'address', e.target.value)}
                                        />
                                        <input
                                            type="number"
                                            min="0"
                                            max="100"
                                            placeholder="Percentage"
                                            value={recipient.percentage}
                                            onChange={(e) => handleRoyaltyRecipientChange(index, 'percentage', e.target.value)}
                                        />
                                        <select
                                            value={recipient.role}
                                            onChange={(e) => handleRoyaltyRecipientChange(index, 'role', e.target.value)}
                                        >
                                            <option value="creator">Creator</option>
                                            <option value="photographer">Photographer</option>
                                            <option value="agency">Agency</option>
                                            <option value="platform">Platform</option>
                                            <option value="contributor">Contributor</option>
                                        </select>
                                        {royaltyRecipients.length > 1 && (
                                            <button
                                                onClick={() => removeRoyaltyRecipient(index)}
                                                className="remove-recipient-btn"
                                            >
                                                Remove
                                            </button>
                                        )}
                                    </div>
                                ))}
                                <button onClick={addRoyaltyRecipient} className="add-recipient-btn">
                                    + Add Royalty Recipient
                                </button>
                                <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '10px' }}>
                                    Total: {royaltyRecipients.reduce((sum, r) => sum + Number(r.percentage || 0), 0)}%
                                    (Must equal 100%)
                                </p>
                            </div>
                        </>
                    )}
                </div>

                {/* DAO Governance */}
                <div className="dao-governance">
                    <h3>🏛️ DAO Governance</h3>
                    
                    <div className="form-group">
                        <label>
                            <input
                                type="checkbox"
                                name="enableDAO"
                                checked={daoGovernance.enableDAO}
                                onChange={handleDaoConfigChange}
                            />
                            Enable DAO governance approval for licensing terms
                        </label>
                    </div>

                    {daoGovernance.enableDAO && (
                        <div className="governance-options">
                            <div className="governance-option">
                                <label>
                                    <input
                                        type="radio"
                                        name="proposalType"
                                        value="licensing_terms"
                                        checked={daoGovernance.proposalType === 'licensing_terms'}
                                        onChange={handleDaoConfigChange}
                                    />
                                    Licensing Terms Proposal
                                </label>
                            </div>
                            <div className="governance-option">
                                <label>
                                    <input
                                        type="radio"
                                        name="proposalType"
                                        value="agency_onboarding"
                                        checked={daoGovernance.proposalType === 'agency_onboarding'}
                                        onChange={handleDaoConfigChange}
                                    />
                                    Agency Onboarding
                                </label>
                            </div>
                            <div className="governance-option">
                                <label>
                                    <input
                                        type="radio"
                                        name="proposalType"
                                        value="royalty_adjustment"
                                        checked={daoGovernance.proposalType === 'royalty_adjustment'}
                                        onChange={handleDaoConfigChange}
                                    />
                                    Royalty Adjustment
                                </label>
                            </div>
                        </div>
                    )}
                </div>

                {/* Pricing Information */}
                <div className="form-section">
                    <h5>💲 Licensing Pricing</h5>
                    <div className="form-grid">
                        <div className="form-group">
                            <label htmlFor="basePricing">Base License Price (ETH)</label>
                            <input
                                type="number"
                                id="basePricing"
                                name="basePricing"
                                step="0.001"
                                min="0"
                                value={formData.basePricing}
                                onChange={handleInputChange}
                                placeholder="0.1"
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="maxResolution">Max Resolution (px)</label>
                            <select
                                id="maxResolution"
                                name="maxResolution"
                                value={formData.maxResolution}
                                onChange={handleInputChange}
                            >
                                <option value="1920">HD (1920px)</option>
                                <option value="2560">QHD (2560px)</option>
                                <option value="4000">4K (4000px)</option>
                                <option value="8000">8K (8000px)</option>
                                <option value="unlimited">Unlimited</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Commercial Usage Warning */}
                {formData.usageRights !== 'editorial_only' && (
                    <div className="commercial-warning">
                        <h4>⚠️ Commercial Usage Requirements</h4>
                        <ul>
                            <li>Model release form will be automatically generated</li>
                            <li>Model name, photographer name, and shoot date are required</li>
                            <li>Copyright notice must be included</li>
                            <li>Territory and duration rights will be enforced</li>
                            {web3Config.enableNFT && <li>NFT will be minted with embedded licensing terms</li>}
                            {daoGovernance.enableDAO && <li>Proposal will be created for DAO approval</li>}
                        </ul>
                    </div>
                )}

                {/* Error Display */}
                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                {/* Upload Button */}
                <button
                    onClick={uploadImage}
                    disabled={!selectedFile || uploading}
                    className="upload-button"
                >
                    {uploading ? 'Processing Upload...' : '📤 Upload Image with Metadata'}
                </button>
            </div>

            {/* Upload Result */}
            {uploadResult && (
                <div className="upload-result">
                    <h4>✅ Upload {uploadResult.batch_mode ? 'Batch' : ''} Successful</h4>
                    
                    {uploadResult.batch_mode && (
                        <div className="batch-summary">
                            <p><strong>Total Files:</strong> {uploadResult.total_files}</p>
                            <p><strong>Successful:</strong> {uploadResult.successful_uploads}</p>
                            <p><strong>Failed:</strong> {uploadResult.failed_uploads}</p>
                        </div>
                    )}

                    {uploadResult.web3_enabled && (
                        <div className="web3-results">
                            <h5>🔗 NFT Minting Results</h5>
                            <div className="result-grid">
                                <div className="result-item">
                                    <strong>Blockchain:</strong> {web3Config.blockchain}
                                </div>
                                <div className="result-item">
                                    <strong>Token Standard:</strong> {web3Config.tokenStandard}
                                </div>
                                <div className="result-item">
                                    <strong>Royalty Recipients:</strong> {royaltyRecipients.length}
                                </div>
                            </div>
                        </div>
                    )}

                    {uploadResult.dao_enabled && (
                        <div className="dao-results">
                            <h5>🏛️ DAO Governance</h5>
                            <p><strong>Proposal Type:</strong> {daoGovernance.proposalType}</p>
                            <p><strong>Voting Period:</strong> {daoGovernance.votingPeriod} days</p>
                            <p>DAO proposal created for community voting on licensing terms.</p>
                        </div>
                    )}

                    {!uploadResult.batch_mode && uploadResult.results && uploadResult.results[0] && (
                        <div className="result-grid">
                            <div className="result-item">
                                <strong>File:</strong> {uploadResult.results[0].file.name}
                            </div>
                            <div className="result-item">
                                <strong>Dimensions:</strong> {uploadResult.results[0].result.file_info?.dimensions || 'N/A'}
                            </div>
                            <div className="result-item">
                                <strong>IPTC Fields:</strong> {uploadResult.results[0].result.metadata_summary?.iptc_fields || 0}
                            </div>
                            <div className="result-item">
                                <strong>DDEX Compliant:</strong> {uploadResult.results[0].result.metadata_summary?.ddex_compliant ? '✅' : '❌'}
                            </div>
                            <div className="result-item">
                                <strong>Model Release:</strong> {uploadResult.results[0].result.metadata_summary?.has_model_release ? '✅' : '❌'}
                            </div>
                            <div className="result-item">
                                <strong>Commercial Approved:</strong> {uploadResult.results[0].result.metadata_summary?.commercial_approved === true ? '✅' : 
                                                                       uploadResult.results[0].result.metadata_summary?.commercial_approved === false ? '❌' : 'N/A'}
                            </div>
                        </div>
                    )}

                    {uploadResult.batch_mode && uploadResult.results && (
                        <div className="batch-results">
                            <h5>📊 Individual File Results</h5>
                            {uploadResult.results.map((fileResult, index) => (
                                <div key={index} className={`file-result ${fileResult.success ? 'success-state' : 'error-state'}`}>
                                    <h6>{fileResult.file.name}</h6>
                                    {fileResult.success ? (
                                        <p>✅ Successfully uploaded and processed</p>
                                    ) : (
                                        <p>❌ {fileResult.result.detail || 'Upload failed'}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                    
                    {uploadResult.results && uploadResult.results[0] && uploadResult.results[0].result.validation && (
                        <div className="validation-results">
                            <h5>Validation Results</h5>
                            <p><strong>Risk Level:</strong> {uploadResult.results[0].result.validation.risk_level}</p>
                            {uploadResult.results[0].result.validation.issues && uploadResult.results[0].result.validation.issues.length > 0 && (
                                <div className="validation-issues">
                                    <strong>Issues:</strong>
                                    <ul>
                                        {uploadResult.results[0].result.validation.issues.map((issue, index) => (
                                            <li key={index}>{issue}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Recent Uploads */}
            {userImages.length > 0 && (
                <div className="recent-uploads">
                    <h3>📂 Recent Uploads</h3>
                    <div className="images-grid">
                        {userImages.map((image) => (
                            <div key={image.id} className="image-card">
                                <div className="image-info">
                                    <h4>{image.file_name}</h4>
                                    <p>{image.dimensions} • {formatFileSize(image.file_size)}</p>
                                    <div className="image-tags">
                                        <span className={`tag usage-${image.usage_rights}`}>
                                            {image.usage_rights.replace('_', ' ')}
                                        </span>
                                        <span className={`tag status-${image.status}`}>
                                            {image.status}
                                        </span>
                                        {image.has_model_release && <span className="tag model-release">Model Release</span>}
                                        {image.ddex_compliant && <span className="tag ddex">DDEX</span>}
                                    </div>
                                    {image.validation_errors.length > 0 && (
                                        <div className="validation-errors">
                                            <strong>Issues:</strong> {image.validation_errors.join(', ')}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ImageUploadComponent;