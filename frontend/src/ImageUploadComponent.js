import React, { useState, useRef, useEffect } from 'react';
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
        if (!selectedFile) {
            setError('Please select an image file');
            return;
        }

        // Validate required fields for commercial usage
        if (formData.usageRights !== 'editorial_only' && (!formData.modelName || !formData.photographerName || !formData.shootDate)) {
            setError('Model name, photographer name, and shoot date are required for commercial usage');
            return;
        }

        setUploading(true);
        setError('');
        setUploadResult(null);

        try {
            const token = localStorage.getItem('token');
            const uploadFormData = new FormData();
            
            uploadFormData.append('file', selectedFile);
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

            const response = await fetch(`${backendUrl}/api/images/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: uploadFormData
            });

            const result = await response.json();

            if (response.ok) {
                setUploadResult(result);
                setSelectedFile(null);
                setPreview(null);
                setFormData({
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
                    targetAgencies: []
                });
                fetchUserImages(); // Refresh images list
            } else {
                setError(result.detail || 'Upload failed');
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

                {/* Commercial Usage Warning */}
                {formData.usageRights !== 'editorial_only' && (
                    <div className="commercial-warning">
                        <h4>⚠️ Commercial Usage Requirements</h4>
                        <ul>
                            <li>Model release form will be automatically generated</li>
                            <li>Model name, photographer name, and shoot date are required</li>
                            <li>Copyright notice must be included</li>
                            <li>Territory and duration rights will be enforced</li>
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
                    <h4>✅ Upload Successful</h4>
                    <div className="result-grid">
                        <div className="result-item">
                            <strong>File:</strong> {uploadResult.file_info.filename}
                        </div>
                        <div className="result-item">
                            <strong>Dimensions:</strong> {uploadResult.file_info.dimensions}
                        </div>
                        <div className="result-item">
                            <strong>IPTC Fields:</strong> {uploadResult.metadata_summary.iptc_fields}
                        </div>
                        <div className="result-item">
                            <strong>DDEX Compliant:</strong> {uploadResult.metadata_summary.ddex_compliant ? '✅' : '❌'}
                        </div>
                        <div className="result-item">
                            <strong>Model Release:</strong> {uploadResult.metadata_summary.has_model_release ? '✅' : '❌'}
                        </div>
                        <div className="result-item">
                            <strong>Commercial Approved:</strong> {uploadResult.metadata_summary.commercial_approved === true ? '✅' : 
                                                                   uploadResult.metadata_summary.commercial_approved === false ? '❌' : 'N/A'}
                        </div>
                    </div>
                    
                    {uploadResult.validation && (
                        <div className="validation-results">
                            <h5>Validation Results</h5>
                            <p><strong>Risk Level:</strong> {uploadResult.validation.risk_level}</p>
                            {uploadResult.validation.issues.length > 0 && (
                                <div className="validation-issues">
                                    <strong>Issues:</strong>
                                    <ul>
                                        {uploadResult.validation.issues.map((issue, index) => (
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