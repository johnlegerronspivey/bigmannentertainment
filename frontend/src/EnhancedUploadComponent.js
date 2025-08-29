import React, { useState, useCallback, useRef } from 'react';
import './EnhancedUpload.css';

const EnhancedUploadComponent = ({ onUploadComplete, currentUser }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [validationErrors, setValidationErrors] = useState({});
  
  // Metadata state
  const [metadata, setMetadata] = useState({
    title: '',
    artist: '',
    album: '',
    isrc: '',
    upc: '',
    rightsHolders: '',
    genre: '',
    releaseDate: '',
    description: '',
    tags: '',
    copyrightYear: new Date().getFullYear(),
    publisherName: '',
    composerName: '',
    duration: ''
  });

  const fileInputRef = useRef(null);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // File type configurations
  const fileTypeConfig = {
    media: {
      accept: ['.mp3', '.wav', '.flac', '.m4a', '.mp4', '.avi', '.mov', '.wmv'],
      maxSize: 500 * 1024 * 1024, // 500MB
      label: 'Media Files'
    },
    artwork: {
      accept: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
      maxSize: 10 * 1024 * 1024, // 10MB
      label: 'Artwork'
    },
    metadata: {
      accept: ['.txt', '.json', '.xml', '.csv', '.pdf'],
      maxSize: 5 * 1024 * 1024, // 5MB
      label: 'Metadata Files'
    }
  };

  // Real-time validation functions
  const validateISRC = (isrc) => {
    const isrcPattern = /^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$/;
    if (!isrc) return true; // Optional field
    return isrcPattern.test(isrc.toUpperCase());
  };

  const validateUPC = (upc) => {
    const upcPattern = /^[0-9]{12}$/;
    if (!upc) return true; // Optional field
    return upcPattern.test(upc);
  };

  const validateTitle = (title) => {
    return title.length >= 1 && title.length <= 200;
  };

  const validateRightsHolders = (rightsHolders) => {
    if (!rightsHolders) return true; // Optional field
    return rightsHolders.length <= 500;
  };

  // Real-time validation handler
  const handleMetadataChange = (field, value) => {
    setMetadata(prev => ({
      ...prev,
      [field]: value
    }));

    // Real-time validation
    const errors = { ...validationErrors };
    
    switch (field) {
      case 'title':
        if (!validateTitle(value)) {
          errors.title = 'Title must be between 1-200 characters';
        } else {
          delete errors.title;
        }
        break;
      case 'isrc':
        if (!validateISRC(value)) {
          errors.isrc = 'ISRC must be in format: CCXXXYYNNNNN (e.g., USRC17607839)';
        } else {
          delete errors.isrc;
        }
        break;
      case 'upc':
        if (!validateUPC(value)) {
          errors.upc = 'UPC must be 12 digits (e.g., 123456789012)';
        } else {
          delete errors.upc;
        }
        break;
      case 'rightsHolders':
        if (!validateRightsHolders(value)) {
          errors.rightsHolders = 'Rights holders must be under 500 characters';
        } else {
          delete errors.rightsHolders;
        }
        break;
      default:
        break;
    }
    
    setValidationErrors(errors);
  };

  // Drag and drop handlers
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (fileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      file,
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      type: determineFileType(file),
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null,
      status: 'pending',
      progress: 0
    }));

    setFiles(prev => [...prev, ...newFiles]);
  };

  const determineFileType = (file) => {
    const extension = `.${file.name.split('.').pop().toLowerCase()}`;
    
    if (fileTypeConfig.media.accept.includes(extension)) {
      return 'media';
    } else if (fileTypeConfig.artwork.accept.includes(extension)) {
      return 'artwork';
    } else if (fileTypeConfig.metadata.accept.includes(extension)) {
      return 'metadata';
    } else {
      return 'unknown';
    }
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileId];
      return newProgress;
    });
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      alert('Please select files to upload');
      return;
    }

    // Validate metadata
    const hasValidationErrors = Object.keys(validationErrors).length > 0;
    if (hasValidationErrors) {
      alert('Please fix validation errors before uploading');
      return;
    }

    setUploading(true);

    for (const fileItem of files) {
      if (fileItem.status === 'completed') continue;

      try {
        await uploadSingleFile(fileItem);
      } catch (error) {
        console.error(`Failed to upload ${fileItem.file.name}:`, error);
        setFiles(prev => 
          prev.map(f => 
            f.id === fileItem.id 
              ? { ...f, status: 'error', error: error.message }
              : f
          )
        );
      }
    }

    setUploading(false);
  };

  const uploadSingleFile = async (fileItem) => {
    const formData = new FormData();
    formData.append('file', fileItem.file);
    formData.append('user_id', currentUser.id);
    formData.append('user_email', currentUser.email);
    formData.append('user_name', currentUser.full_name);
    formData.append('send_notification', 'true');
    
    // Add metadata
    Object.keys(metadata).forEach(key => {
      if (metadata[key]) {
        formData.append(`metadata_${key}`, metadata[key]);
      }
    });

    // Determine upload endpoint based on file type
    let uploadUrl;
    switch (fileItem.type) {
      case 'media':
        uploadUrl = `${BACKEND_URL}/api/media/s3/upload/audio`;
        if (fileItem.file.type.startsWith('video/')) {
          uploadUrl = `${BACKEND_URL}/api/media/s3/upload/video`;
        }
        break;
      case 'artwork':
        uploadUrl = `${BACKEND_URL}/api/media/s3/upload/image`;
        break;
      default:
        uploadUrl = `${BACKEND_URL}/api/media/s3/upload/image`; // fallback
    }

    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${currentUser.token}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    const result = await response.json();
    
    setFiles(prev => 
      prev.map(f => 
        f.id === fileItem.id 
          ? { ...f, status: 'completed', result }
          : f
      )
    );

    if (onUploadComplete) {
      onUploadComplete(result);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'media': return '🎵';
      case 'artwork': return '🖼️';
      case 'metadata': return '📄';
      default: return '📁';
    }
  };

  return (
    <div className="enhanced-upload-container">
      <h2>Upload Media & Metadata</h2>
      
      {/* Metadata Form */}
      <div className="metadata-form">
        <h3>Media Metadata</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>
              Title <span className="required">*</span>
            </label>
            <input
              type="text"
              value={metadata.title}
              onChange={(e) => handleMetadataChange('title', e.target.value)}
              placeholder="Enter track or album title"
              className={validationErrors.title ? 'error' : ''}
              maxLength={200}
            />
            {validationErrors.title && (
              <div className="validation-error">{validationErrors.title}</div>
            )}
            <div className="char-count">{metadata.title.length}/200</div>
          </div>

          <div className="form-group">
            <label>Artist</label>
            <input
              type="text"
              value={metadata.artist}
              onChange={(e) => handleMetadataChange('artist', e.target.value)}
              placeholder="Artist name"
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label>Album</label>
            <input
              type="text"
              value={metadata.album}
              onChange={(e) => handleMetadataChange('album', e.target.value)}
              placeholder="Album name"
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label>Genre</label>
            <select
              value={metadata.genre}
              onChange={(e) => handleMetadataChange('genre', e.target.value)}
            >
              <option value="">Select Genre</option>
              <option value="pop">Pop</option>
              <option value="rock">Rock</option>
              <option value="hip-hop">Hip Hop</option>
              <option value="r&b">R&B</option>
              <option value="electronic">Electronic</option>
              <option value="jazz">Jazz</option>
              <option value="classical">Classical</option>
              <option value="country">Country</option>
              <option value="folk">Folk</option>
              <option value="alternative">Alternative</option>
              <option value="indie">Indie</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label>
              ISRC
              <span className="tooltip">ℹ️
                <span className="tooltip-text">International Standard Recording Code (12 characters: CCXXXYYNNNNN)</span>
              </span>
            </label>
            <input
              type="text"
              value={metadata.isrc}
              onChange={(e) => handleMetadataChange('isrc', e.target.value.toUpperCase())}
              placeholder="e.g., USRC17607839"
              className={validationErrors.isrc ? 'error' : ''}
              maxLength={12}
            />
            {validationErrors.isrc && (
              <div className="validation-error">{validationErrors.isrc}</div>
            )}
            {metadata.isrc && validateISRC(metadata.isrc) && (
              <div className="validation-success">✓ Valid ISRC format</div>
            )}
          </div>

          <div className="form-group">
            <label>
              UPC
              <span className="tooltip">ℹ️
                <span className="tooltip-text">Universal Product Code (12 digits)</span>
              </span>
            </label>
            <input
              type="text"
              value={metadata.upc}
              onChange={(e) => handleMetadataChange('upc', e.target.value.replace(/\D/g, ''))}
              placeholder="e.g., 123456789012"
              className={validationErrors.upc ? 'error' : ''}
              maxLength={12}
            />
            {validationErrors.upc && (
              <div className="validation-error">{validationErrors.upc}</div>
            )}
            {metadata.upc && validateUPC(metadata.upc) && (
              <div className="validation-success">✓ Valid UPC format</div>
            )}
          </div>

          <div className="form-group">
            <label>Rights Holders</label>
            <textarea
              value={metadata.rightsHolders}
              onChange={(e) => handleMetadataChange('rightsHolders', e.target.value)}
              placeholder="List rights holders, publishers, etc."
              className={validationErrors.rightsHolders ? 'error' : ''}
              maxLength={500}
              rows={3}
            />
            {validationErrors.rightsHolders && (
              <div className="validation-error">{validationErrors.rightsHolders}</div>
            )}
            <div className="char-count">{metadata.rightsHolders.length}/500</div>
          </div>

          <div className="form-group">
            <label>Publisher Name</label>
            <input
              type="text"
              value={metadata.publisherName}
              onChange={(e) => handleMetadataChange('publisherName', e.target.value)}
              placeholder="Publisher name"
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label>Composer</label>
            <input
              type="text"
              value={metadata.composerName}
              onChange={(e) => handleMetadataChange('composerName', e.target.value)}
              placeholder="Composer name"
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label>Release Date</label>
            <input
              type="date"
              value={metadata.releaseDate}
              onChange={(e) => handleMetadataChange('releaseDate', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Copyright Year</label>
            <input
              type="number"
              value={metadata.copyrightYear}
              onChange={(e) => handleMetadataChange('copyrightYear', e.target.value)}
              min="1900"
              max={new Date().getFullYear() + 10}
            />
          </div>

          <div className="form-group full-width">
            <label>Description</label>
            <textarea
              value={metadata.description}
              onChange={(e) => handleMetadataChange('description', e.target.value)}
              placeholder="Brief description of the content"
              maxLength={1000}
              rows={3}
            />
            <div className="char-count">{metadata.description.length}/1000</div>
          </div>

          <div className="form-group full-width">
            <label>Tags</label>
            <input
              type="text"
              value={metadata.tags}
              onChange={(e) => handleMetadataChange('tags', e.target.value)}
              placeholder="Comma-separated tags (e.g., upbeat, dance, summer)"
              maxLength={200}
            />
            <div className="char-count">{metadata.tags.length}/200</div>
          </div>
        </div>
      </div>

      {/* File Upload Area */}
      <div className="upload-section">
        <h3>Upload Files</h3>
        
        <div
          className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="drop-zone-content">
            <div className="upload-icon">📁</div>
            <div className="upload-text">
              <p>Drag and drop your files here</p>
              <p className="upload-subtext">or <span className="browse-link">browse files</span></p>
            </div>
            <div className="supported-formats">
              <div className="format-group">
                <strong>Media:</strong> MP3, WAV, FLAC, M4A, MP4, AVI, MOV (max 500MB)
              </div>
              <div className="format-group">
                <strong>Artwork:</strong> JPG, PNG, GIF, BMP, WebP (max 10MB)
              </div>
              <div className="format-group">
                <strong>Metadata:</strong> TXT, JSON, XML, CSV, PDF (max 5MB)
              </div>
            </div>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".mp3,.wav,.flac,.m4a,.mp4,.avi,.mov,.wmv,.jpg,.jpeg,.png,.gif,.bmp,.webp,.txt,.json,.xml,.csv,.pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="file-list">
          <h4>Selected Files ({files.length})</h4>
          <div className="files">
            {files.map((fileItem) => (
              <div key={fileItem.id} className={`file-item ${fileItem.status}`}>
                <div className="file-info">
                  <div className="file-icon">{getFileIcon(fileItem.type)}</div>
                  <div className="file-details">
                    <div className="file-name">{fileItem.file.name}</div>
                    <div className="file-meta">
                      <span className="file-size">{formatFileSize(fileItem.file.size)}</span>
                      <span className="file-type">{fileItem.type}</span>
                      {fileItem.status === 'error' && (
                        <span className="error-message">{fileItem.error}</span>
                      )}
                    </div>
                  </div>
                  {fileItem.preview && (
                    <div className="file-preview">
                      <img src={fileItem.preview} alt="Preview" />
                    </div>
                  )}
                </div>
                <div className="file-actions">
                  {fileItem.status === 'pending' && (
                    <button
                      type="button"
                      onClick={() => removeFile(fileItem.id)}
                      className="remove-btn"
                    >
                      ×
                    </button>
                  )}
                  {fileItem.status === 'completed' && (
                    <div className="success-indicator">✓</div>
                  )}
                  {fileItem.status === 'error' && (
                    <div className="error-indicator">✗</div>
                  )}
                </div>
                {uploadProgress[fileItem.id] > 0 && (
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${uploadProgress[fileItem.id]}%` }}
                    ></div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Button */}
      <div className="upload-actions">
        <button
          type="button"
          onClick={uploadFiles}
          disabled={uploading || files.length === 0 || Object.keys(validationErrors).length > 0}
          className="upload-btn"
        >
          {uploading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
        </button>
        
        {files.length > 0 && (
          <button
            type="button"
            onClick={() => setFiles([])}
            className="clear-btn"
            disabled={uploading}
          >
            Clear All
          </button>
        )}
      </div>

      {/* Validation Summary */}
      {Object.keys(validationErrors).length > 0 && (
        <div className="validation-summary">
          <h4>Please fix the following errors:</h4>
          <ul>
            {Object.entries(validationErrors).map(([field, error]) => (
              <li key={field}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default EnhancedUploadComponent;