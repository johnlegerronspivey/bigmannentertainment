import React, { useState, useCallback, useRef, useEffect } from 'react';
import './EnhancedUpload.css';

const EnhancedUploadComponent = ({ onUploadComplete, currentUser }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [validationErrors, setValidationErrors] = useState({});
  const [batchMode, setBatchMode] = useState(false);
  const [validationResults, setValidationResults] = useState({});
  const [duplicateAlerts, setDuplicateAlerts] = useState({});
  const [metadataPreview, setMetadataPreview] = useState({});
  const [processingStatus, setProcessingStatus] = useState('idle');
  const [selectedTab, setSelectedTab] = useState('upload');
  
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

  // Enhanced file type configurations for Phase 2
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
      accept: ['.json', '.xml', '.csv', '.ddex', '.mead', '.txt', '.id3', '.musicbrainz'],
      maxSize: 50 * 1024 * 1024, // 50MB for metadata files
      label: 'Metadata Files'
    },
    batch: {
      accept: ['.zip', '.tar', '.gz'],
      maxSize: 500 * 1024 * 1024, // 500MB for batch uploads
      label: 'Batch Upload Archives'
    }
  };

  // Enhanced validation functions for Phase 2
  const validateISRC = (isrc) => {
    const isrcPattern = /^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$/;
    if (!isrc) return true;
    return isrcPattern.test(isrc.toUpperCase());
  };

  const validateUPC = (upc) => {
    const upcPattern = /^[0-9]{12}$/;
    if (!upc) return true;
    return upcPattern.test(upc);
  };

  const validateTitle = (title) => {
    return title && title.length >= 1 && title.length <= 200;
  };

  const validateDuration = (duration) => {
    const durationPattern = /^([0-9]+:)?[0-5]?[0-9]:[0-5][0-9]$/;
    if (!duration) return true;
    return durationPattern.test(duration);
  };

  const validateYear = (year) => {
    const currentYear = new Date().getFullYear();
    return year >= 1900 && year <= currentYear + 5;
  };

  // Detect metadata file format
  const detectMetadataFormat = (file) => {
    const extension = file.name.toLowerCase().split('.').pop();
    const formatMap = {
      'json': 'json',
      'xml': file.name.toLowerCase().includes('ddex') ? 'ddex_ern' : 'mead',
      'csv': 'csv',
      'ddex': 'ddex_ern',
      'mead': 'mead',
      'id3': 'id3',
      'musicbrainz': 'musicbrainz'
    };
    return formatMap[extension] || 'json';
  };

  // Check for duplicates in real-time
  const checkDuplicates = async (identifier, type) => {
    if (!identifier || identifier.length < 3) return;
    
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/metadata/duplicates/check?identifier_type=${type}&identifier_value=${identifier}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data.duplicates_found > 0) {
          setDuplicateAlerts(prev => ({
            ...prev,
            [type]: {
              found: true,
              count: data.duplicates_found,
              details: data.duplicate_details
            }
          }));
        } else {
          setDuplicateAlerts(prev => {
            const updated = { ...prev };
            delete updated[type];
            return updated;
          });
        }
      }
    } catch (error) {
      console.error('Error checking duplicates:', error);
    }
  };

  // Enhanced metadata validation with duplicate checking
  const handleMetadataChange = (field, value) => {
    setMetadata(prev => ({
      ...prev,
      [field]: value
    }));

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
        if (value && !validateISRC(value)) {
          errors.isrc = 'ISRC must be in format: CCXXXYYNNNNN (e.g., USRC17607839)';
        } else {
          delete errors.isrc;
          if (value && value.length >= 12) {
            checkDuplicates(value, 'isrc');
          }
        }
        break;
      case 'upc':
        if (value && !validateUPC(value)) {
          errors.upc = 'UPC must be 12 digits';
        } else {
          delete errors.upc;
          if (value && value.length === 12) {
            checkDuplicates(value, 'upc');
          }
        }
        break;
      case 'duration':
        if (value && !validateDuration(value)) {
          errors.duration = 'Duration must be in format MM:SS or HH:MM:SS';
        } else {
          delete errors.duration;
        }
        break;
      case 'copyrightYear':
        if (value && !validateYear(parseInt(value))) {
          errors.copyrightYear = 'Year must be between 1900 and ' + (new Date().getFullYear() + 5);
        } else {
          delete errors.copyrightYear;
        }
        break;
      default:
        break;
    }
    
    setValidationErrors(errors);
  };

  // Parse metadata file and show preview
  const parseMetadataFile = async (file) => {
    if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
      return;
    }
    
    try {
      const text = await file.text();
      const metadata = JSON.parse(text);
      
      setMetadataPreview(prev => ({
        ...prev,
        [file.name]: {
          parsed: true,
          data: metadata,
          format: detectMetadataFormat(file)
        }
      }));
    } catch (error) {
      setMetadataPreview(prev => ({
        ...prev,
        [file.name]: {
          parsed: false,
          error: 'Failed to parse JSON: ' + error.message,
          format: detectMetadataFormat(file)
        }
      }));
    }
  };

  // Get file type based on extension
  const getFileType = (file) => {
    const extension = file.name.toLowerCase();
    
    if (fileTypeConfig.media.accept.some(ext => extension.endsWith(ext))) {
      return 'media';
    } else if (fileTypeConfig.artwork.accept.some(ext => extension.endsWith(ext))) {
      return 'artwork';
    } else if (fileTypeConfig.metadata.accept.some(ext => extension.endsWith(ext))) {
      return 'metadata';
    } else if (fileTypeConfig.batch.accept.some(ext => extension.endsWith(ext))) {
      return 'batch';
    }
    return 'unknown';
  };

  // Enhanced single file upload with metadata validation
  const uploadSingleFile = async (file) => {
    const fileType = getFileType(file);
    
    if (fileType === 'metadata') {
      return await uploadMetadataFile(file);
    } else if (fileType === 'batch') {
      return await processBatchFile(file);
    } else {
      return await uploadMediaFile(file, fileType);
    }
  };

  // Metadata file upload with parsing and validation
  const uploadMetadataFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', detectMetadataFormat(file));
    formData.append('validate', 'true');
    formData.append('check_duplicates', 'true');
    
    const response = await fetch(`${BACKEND_URL}/api/metadata/parse`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Store validation results for display
    setValidationResults(prev => ({
      ...prev,
      [file.name]: result
    }));
    
    return result;
  };

  // Media file upload
  const uploadMediaFile = async (file, fileType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', currentUser?.id || 'unknown');
    formData.append('user_email', currentUser?.email || '');
    formData.append('user_name', currentUser?.full_name || '');
    
    // Add metadata
    Object.keys(metadata).forEach(key => {
      if (metadata[key]) {
        formData.append(`metadata_${key}`, metadata[key]);
      }
    });
    
    const response = await fetch(`${BACKEND_URL}/api/media/s3/upload/${fileType}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }
    
    return await response.json();
  };

  // Process batch file
  const processBatchFile = async (file) => {
    // For now, just return a placeholder - batch processing would require additional backend support
    return {
      message: 'Batch file received - processing not yet implemented',
      filename: file.name,
      size: file.size
    };
  };

  // Batch processing handler
  const processBatchUpload = async (filesToProcess) => {
    setProcessingStatus('processing');
    const results = [];
    
    for (let i = 0; i < filesToProcess.length; i++) {
      const file = filesToProcess[i];
      setUploadProgress(prev => ({
        ...prev,
        batch: {
          current: i + 1,
          total: filesToProcess.length,
          fileName: file.name
        }
      }));
      
      try {
        const result = await uploadSingleFile(file);
        results.push({
          file: file.name,
          success: true,
          result
        });
      } catch (error) {
        results.push({
          file: file.name,
          success: false,
          error: error.message
        });
      }
    }
    
    setProcessingStatus('completed');
    return results;
  };

  // File handling
  const handleFiles = (fileList) => {
    const newFiles = Array.from(fileList);
    
    // Validate files
    const validatedFiles = newFiles.filter(file => {
      const fileType = getFileType(file);
      if (fileType === 'unknown') {
        console.warn(`Unsupported file type: ${file.name}`);
        return false;
      }
      
      const config = fileTypeConfig[fileType];
      if (file.size > config.maxSize) {
        console.warn(`File too large: ${file.name}`);
        return false;
      }
      
      return true;
    });
    
    setFiles(prev => [...prev, ...validatedFiles]);
    
    // Parse metadata files for preview
    validatedFiles.forEach(file => {
      if (getFileType(file) === 'metadata') {
        parseMetadataFile(file);
      }
    });
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

  // Upload handler
  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setProcessingStatus('processing');
    
    try {
      let results;
      if (batchMode || files.length > 1) {
        results = await processBatchUpload(files);
      } else {
        const result = await uploadSingleFile(files[0]);
        results = [{ file: files[0].name, success: true, result }];
      }
      
      setProcessingStatus('completed');
      
      if (onUploadComplete) {
        onUploadComplete(results);
      }
      
      // Clear files after successful upload
      setFiles([]);
      setMetadata({
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
      
    } catch (error) {
      console.error('Upload error:', error);
      setProcessingStatus('error');
    } finally {
      setUploading(false);
    }
  };

  // Render validation results
  const renderValidationResults = () => {
    const results = Object.entries(validationResults);
    if (results.length === 0) return null;
    
    return (
      <div className="validation-results">
        <h3>Validation Results</h3>
        {results.map(([fileName, result]) => (
          <div key={fileName} className="validation-result-item">
            <h4>{fileName}</h4>
            <div className={`status ${result.validation_status}`}>
              Status: {result.validation_status}
            </div>
            {result.validation_errors && result.validation_errors.length > 0 && (
              <div className="errors">
                <h5>Errors:</h5>
                <ul>
                  {result.validation_errors.map((error, idx) => (
                    <li key={idx} className={`error ${error.severity}`}>
                      <strong>{error.field}:</strong> {error.message}
                      {error.suggested_fix && (
                        <div className="suggestion">Suggestion: {error.suggested_fix}</div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.duplicates_found > 0 && (
              <div className="duplicates-alert">
                <h5>⚠️ Duplicates Found: {result.duplicates_found}</h5>
                <ul>
                  {result.duplicate_details.map((dup, idx) => (
                    <li key={idx}>
                      {dup.identifier_type.toUpperCase()}: {dup.identifier_value} 
                      (First seen: {new Date(dup.first_seen_date).toLocaleDateString()})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  // Render duplicate alerts
  const renderDuplicateAlerts = () => {
    const alerts = Object.entries(duplicateAlerts);
    if (alerts.length === 0) return null;
    
    return (
      <div className="duplicate-alerts">
        {alerts.map(([type, alert]) => (
          <div key={type} className="duplicate-alert">
            ⚠️ {alert.count} duplicate {type.toUpperCase()}(s) found in platform
          </div>
        ))}
      </div>
    );
  };

  // Render metadata preview
  const renderMetadataPreview = () => {
    const previews = Object.entries(metadataPreview);
    if (previews.length === 0) return null;
    
    return (
      <div className="metadata-preview">
        <h3>Metadata Preview</h3>
        {previews.map(([fileName, preview]) => (
          <div key={fileName} className="preview-item">
            <h4>{fileName} ({preview.format})</h4>
            {preview.parsed ? (
              <pre className="metadata-data">
                {JSON.stringify(preview.data, null, 2)}
              </pre>
            ) : (
              <div className="error">Error: {preview.error}</div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="enhanced-upload-container">
      <div className="upload-tabs">
        <button 
          className={`tab ${selectedTab === 'upload' ? 'active' : ''}`}
          onClick={() => setSelectedTab('upload')}
        >
          Upload
        </button>
        <button 
          className={`tab ${selectedTab === 'results' ? 'active' : ''}`}
          onClick={() => setSelectedTab('results')}
        >
          Results
        </button>
        <button 
          className={`tab ${selectedTab === 'preview' ? 'active' : ''}`}
          onClick={() => setSelectedTab('preview')}
        >
          Preview
        </button>
      </div>

      {selectedTab === 'upload' && (
        <div className="upload-section">
          <div className="upload-modes">
            <label className="mode-toggle">
              <input
                type="checkbox"
                checked={batchMode}
                onChange={(e) => setBatchMode(e.target.checked)}
              />
              Batch Processing Mode
            </label>
          </div>

          <div 
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="drop-content">
              <div className="upload-icon">📁</div>
              <h3>Drag & Drop Files Here</h3>
              <p>Or click to select files</p>
              <div className="supported-formats">
                <p><strong>Supported:</strong></p>
                <p>📊 Metadata: JSON, XML, CSV, DDEX, MEAD, ID3</p>
                <p>🎵 Media: MP3, WAV, FLAC, MP4, AVI, MOV</p>
                <p>🖼️ Artwork: JPG, PNG, GIF, BMP, WEBP</p>
                <p>📦 Batch: ZIP, TAR, GZ</p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="file-input"
                accept=".mp3,.wav,.flac,.mp4,.avi,.mov,.jpg,.png,.gif,.json,.xml,.csv,.zip,.tar,.gz"
              />
            </div>
          </div>

          {files.length > 0 && (
            <div className="files-list">
              <h3>Selected Files ({files.length})</h3>
              {files.map((file, index) => (
                <div key={index} className="file-item">
                  <span className="file-name">{file.name}</span>
                  <span className="file-type">{getFileType(file)}</span>
                  <span className="file-size">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                  <button
                    onClick={() => setFiles(prev => prev.filter((_, i) => i !== index))}
                    className="remove-file"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Metadata input form */}
          <div className="metadata-form">
            <h3>Metadata Information</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  value={metadata.title}
                  onChange={(e) => handleMetadataChange('title', e.target.value)}
                  className={validationErrors.title ? 'error' : ''}
                />
                {validationErrors.title && (
                  <span className="error-text">{validationErrors.title}</span>
                )}
              </div>

              <div className="form-group">
                <label>Artist</label>
                <input
                  type="text"
                  value={metadata.artist}
                  onChange={(e) => handleMetadataChange('artist', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Album</label>
                <input
                  type="text"
                  value={metadata.album}
                  onChange={(e) => handleMetadataChange('album', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>ISRC</label>
                <input
                  type="text"
                  value={metadata.isrc}
                  onChange={(e) => handleMetadataChange('isrc', e.target.value)}
                  placeholder="USRC17607839"
                  className={validationErrors.isrc ? 'error' : ''}
                />
                {validationErrors.isrc && (
                  <span className="error-text">{validationErrors.isrc}</span>
                )}
              </div>

              <div className="form-group">
                <label>UPC</label>
                <input
                  type="text"
                  value={metadata.upc}
                  onChange={(e) => handleMetadataChange('upc', e.target.value)}
                  placeholder="123456789012"
                  className={validationErrors.upc ? 'error' : ''}
                />
                {validationErrors.upc && (
                  <span className="error-text">{validationErrors.upc}</span>
                )}
              </div>

              <div className="form-group">
                <label>Rights Holders</label>
                <input
                  type="text"
                  value={metadata.rightsHolders}
                  onChange={(e) => handleMetadataChange('rightsHolders', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Genre</label>
                <input
                  type="text"
                  value={metadata.genre}
                  onChange={(e) => handleMetadataChange('genre', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Duration</label>
                <input
                  type="text"
                  value={metadata.duration}
                  onChange={(e) => handleMetadataChange('duration', e.target.value)}
                  placeholder="3:45"
                  className={validationErrors.duration ? 'error' : ''}
                />
                {validationErrors.duration && (
                  <span className="error-text">{validationErrors.duration}</span>
                )}
              </div>

              <div className="form-group">
                <label>Copyright Year</label>
                <input
                  type="number"
                  value={metadata.copyrightYear}
                  onChange={(e) => handleMetadataChange('copyrightYear', e.target.value)}
                  className={validationErrors.copyrightYear ? 'error' : ''}
                />
                {validationErrors.copyrightYear && (
                  <span className="error-text">{validationErrors.copyrightYear}</span>
                )}
              </div>

              <div className="form-group full-width">
                <label>Description</label>
                <textarea
                  value={metadata.description}
                  onChange={(e) => handleMetadataChange('description', e.target.value)}
                  rows="3"
                />
              </div>

              <div className="form-group full-width">
                <label>Tags (comma-separated)</label>
                <input
                  type="text"
                  value={metadata.tags}
                  onChange={(e) => handleMetadataChange('tags', e.target.value)}
                  placeholder="hip-hop, rap, urban"
                />
              </div>
            </div>
          </div>

          {renderDuplicateAlerts()}

          {processingStatus !== 'idle' && (
            <div className="processing-status">
              <div className={`status ${processingStatus}`}>
                {processingStatus === 'processing' && '⏳ Processing...'}
                {processingStatus === 'completed' && '✅ Completed'}
                {processingStatus === 'error' && '❌ Error'}
              </div>
              {uploadProgress.batch && (
                <div className="batch-progress">
                  Processing {uploadProgress.batch.current} of {uploadProgress.batch.total}: 
                  {uploadProgress.batch.fileName}
                </div>
              )}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            className="upload-button"
          >
            {uploading ? '⏳ Uploading...' : `📤 Upload ${files.length} File(s)`}
          </button>
        </div>
      )}

      {selectedTab === 'results' && renderValidationResults()}
      {selectedTab === 'preview' && renderMetadataPreview()}
    </div>
  );
};

export default EnhancedUploadComponent;