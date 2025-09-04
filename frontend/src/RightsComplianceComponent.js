import React, { useState, useEffect } from 'react';
import './RightsCompliance.css';

const RightsComplianceComponent = ({ currentUser }) => {
  const [activeTab, setActiveTab] = useState('check');
  const [complianceCheck, setComplianceCheck] = useState({
    content_id: '',
    isrc: '',
    territories: [],
    usage_types: [],
    strict_mode: false
  });
  
  const [complianceResult, setComplianceResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [territories, setTerritories] = useState({});
  const [usageTypes, setUsageTypes] = useState({});
  const [templates, setTemplates] = useState({});
  const [rightsHistory, setRightsHistory] = useState([]);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Load initial data
  useEffect(() => {
    loadTerritories();
    loadUsageTypes();
    loadTemplates();
    if (activeTab === 'history') {
      loadRightsHistory();
    }
  }, [activeTab]);

  const loadTerritories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/rights/territories`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTerritories(data.territories || {});
      }
    } catch (error) {
      console.error('Error loading territories:', error);
    }
  };

  const loadUsageTypes = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/rights/usage-types`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsageTypes(data.usage_types || {});
      }
    } catch (error) {
      console.error('Error loading usage types:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/rights/templates/usage-rights`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.usage_templates || {});
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadRightsHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/rights/dashboard/rights-summary`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        // This would load actual history data in a real implementation
        setRightsHistory([]);
      }
    } catch (error) {
      console.error('Error loading rights history:', error);
    }
  };

  const handleComplianceCheck = async () => {
    if (!complianceCheck.content_id || complianceCheck.territories.length === 0 || complianceCheck.usage_types.length === 0) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('content_id', complianceCheck.content_id);
      if (complianceCheck.isrc) {
        formData.append('isrc', complianceCheck.isrc);
      }
      formData.append('strict_mode', complianceCheck.strict_mode);
      
      // Add territories and usage types
      complianceCheck.territories.forEach(territory => {
        formData.append('territories', territory);
      });
      complianceCheck.usage_types.forEach(usage => {
        formData.append('usage_types', usage);
      });

      const response = await fetch(`${BACKEND_URL}/api/rights/check-compliance`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setComplianceResult(result);
        setActiveTab('results');
      } else {
        const error = await response.json();
        alert(`Compliance check failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Compliance check error:', error);
      alert('Failed to perform compliance check');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickCheck = async () => {
    if (!complianceCheck.isrc || complianceCheck.territories.length === 0 || complianceCheck.usage_types.length === 0) {
      alert('Please provide ISRC, territory, and usage type for quick check');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('isrc', complianceCheck.isrc);
      formData.append('territory', complianceCheck.territories[0]);
      formData.append('usage_type', complianceCheck.usage_types[0]);

      const response = await fetch(`${BACKEND_URL}/api/rights/quick-check`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setComplianceResult(result);
        setActiveTab('results');
      } else {
        const error = await response.json();
        alert(`Quick check failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Quick check error:', error);
      alert('Failed to perform quick check');
    } finally {
      setLoading(false);
    }
  };

  const handleTerritoryChange = (territoryCode) => {
    setComplianceCheck(prev => ({
      ...prev,
      territories: prev.territories.includes(territoryCode)
        ? prev.territories.filter(t => t !== territoryCode)
        : [...prev.territories, territoryCode]
    }));
  };

  const handleUsageTypeChange = (usageType) => {
    setComplianceCheck(prev => ({
      ...prev,
      usage_types: prev.usage_types.includes(usageType)
        ? prev.usage_types.filter(u => u !== usageType)
        : [...prev.usage_types, usageType]
    }));
  };

  const applyTemplate = (templateName) => {
    const template = templates[templateName];
    if (template) {
      setComplianceCheck(prev => ({
        ...prev,
        territories: template.default_territories,
        usage_types: template.usage_types
      }));
    }
  };

  const renderComplianceStatus = (status) => {
    const statusConfig = {
      compliant: { color: '#10b981', icon: '✅', label: 'Compliant' },
      warning: { color: '#f59e0b', icon: '⚠️', label: 'Warning' },
      non_compliant: { color: '#ef4444', icon: '❌', label: 'Non-Compliant' },
      unknown: { color: '#6b7280', icon: '❓', label: 'Unknown' }
    };
    
    const config = statusConfig[status] || statusConfig.unknown;
    
    return (
      <span className="compliance-status" style={{ color: config.color }}>
        {config.icon} {config.label}
      </span>
    );
  };

  const renderResults = () => {
    if (!complianceResult) return null;

    // Handle both full compliance check and quick check results
    const isQuickCheck = complianceResult.hasOwnProperty('is_compliant');
    
    if (isQuickCheck) {
      return (
        <div className="compliance-results">
          <h3>Quick Compliance Check Results</h3>
          
          <div className="quick-result-summary">
            <div className="result-header">
              <h4>ISRC: {complianceResult.isrc}</h4>
              <p>{complianceResult.territory} • {complianceResult.usage_type}</p>
            </div>
            
            <div className="result-status">
              {renderComplianceStatus(complianceResult.compliance_status)}
            </div>
            
            <div className="result-message">
              {complianceResult.summary_message}
            </div>
          </div>

          {complianceResult.violations && complianceResult.violations.length > 0 && (
            <div className="violations-section">
              <h4>🚫 Violations</h4>
              {complianceResult.violations.map((violation, index) => (
                <div key={index} className="violation-item error">
                  <strong>{violation.type}:</strong> {violation.message}
                </div>
              ))}
            </div>
          )}

          {complianceResult.warnings && complianceResult.warnings.length > 0 && (
            <div className="warnings-section">
              <h4>⚠️ Warnings</h4>
              {complianceResult.warnings.map((warning, index) => (
                <div key={index} className="warning-item warning">
                  <strong>{warning.type}:</strong> {warning.message}
                </div>
              ))}
            </div>
          )}

          <div className="processing-info">
            <small>Processing time: {complianceResult.processing_time?.toFixed(3)}s</small>
          </div>
        </div>
      );
    } else {
      // Full compliance check results
      return (
        <div className="compliance-results">
          <h3>Comprehensive Compliance Results</h3>
          
          <div className="result-summary">
            <div className="summary-header">
              <h4>Content ID: {complianceResult.compliance_result?.content_id}</h4>
              {complianceResult.compliance_result?.isrc && (
                <p>ISRC: {complianceResult.compliance_result.isrc}</p>
              )}
            </div>
            
            <div className="overall-status">
              <h4>Overall Status</h4>
              {renderComplianceStatus(complianceResult.compliance_result?.overall_status)}
            </div>

            <div className="summary-stats">
              <div className="stat-item">
                <span className="stat-number">{complianceResult.summary?.violations_count || 0}</span>
                <span className="stat-label">Violations</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">{complianceResult.summary?.warnings_count || 0}</span>
                <span className="stat-label">Warnings</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">{complianceResult.summary?.missing_rights_count || 0}</span>
                <span className="stat-label">Missing Rights</span>
              </div>
            </div>
          </div>

          {/* Territory Compliance */}
          {complianceResult.compliance_result?.territory_compliance && (
            <div className="territory-compliance">
              <h4>🌍 Territory Compliance</h4>
              <div className="compliance-grid">
                {Object.entries(complianceResult.compliance_result.territory_compliance).map(([territory, status]) => (
                  <div key={territory} className="compliance-item">
                    <span className="territory-name">
                      {territories[territory]?.name || territory}
                    </span>
                    {renderComplianceStatus(status)}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Usage Rights Compliance */}
          {complianceResult.compliance_result?.usage_compliance && (
            <div className="usage-compliance">
              <h4>🎵 Usage Rights Compliance</h4>
              <div className="compliance-grid">
                {Object.entries(complianceResult.compliance_result.usage_compliance).map(([usage, status]) => (
                  <div key={usage} className="compliance-item">
                    <span className="usage-name">
                      {usageTypes[usage]?.name || usage}
                    </span>
                    {renderComplianceStatus(status)}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {complianceResult.compliance_result?.recommendations && complianceResult.compliance_result.recommendations.length > 0 && (
            <div className="recommendations">
              <h4>💡 Recommendations</h4>
              <ul>
                {complianceResult.compliance_result.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="processing-info">
            <small>Processing time: {complianceResult.summary?.processing_time?.toFixed(3)}s</small>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="rights-compliance-container">
      <div className="compliance-header">
        <img 
          src="/big-mann-logo.png" 
          alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
          className="compliance-logo"
        />
        <h2>🔒 Rights & Compliance Checker</h2>
        <p>Verify territory rights, usage permissions, and embargo restrictions</p>
      </div>

      <div className="compliance-tabs">
        <button 
          className={`tab ${activeTab === 'check' ? 'active' : ''}`}
          onClick={() => setActiveTab('check')}
        >
          Compliance Check
        </button>
        <button 
          className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          Results
        </button>
        <button 
          className={`tab ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          Templates
        </button>
        <button 
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
      </div>

      {activeTab === 'check' && (
        <div className="compliance-check-form">
          <div className="form-section">
            <h3>Content Information</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Content ID *</label>
                <input
                  type="text"
                  value={complianceCheck.content_id}
                  onChange={(e) => setComplianceCheck(prev => ({...prev, content_id: e.target.value}))}
                  placeholder="Enter content identifier"
                />
              </div>
              <div className="form-group">
                <label>ISRC (Optional)</label>
                <input
                  type="text"
                  value={complianceCheck.isrc}
                  onChange={(e) => setComplianceCheck(prev => ({...prev, isrc: e.target.value}))}
                  placeholder="US-S1Z-99-00001"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Territories *</h3>
            <div className="selection-grid">
              {Object.entries(territories).map(([code, info]) => (
                <label key={code} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={complianceCheck.territories.includes(code)}
                    onChange={() => handleTerritoryChange(code)}
                  />
                  <span className="checkbox-label">
                    <strong>{code}</strong> - {info.name}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-section">
            <h3>Usage Types *</h3>
            <div className="selection-grid">
              {Object.entries(usageTypes).map(([code, info]) => (
                <label key={code} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={complianceCheck.usage_types.includes(code)}
                    onChange={() => handleUsageTypeChange(code)}
                  />
                  <span className="checkbox-label">
                    <strong>{info.name}</strong>
                    <br />
                    <small>{info.description}</small>
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-section">
            <h3>Options</h3>
            <label className="checkbox-item">
              <input
                type="checkbox"
                checked={complianceCheck.strict_mode}
                onChange={(e) => setComplianceCheck(prev => ({...prev, strict_mode: e.target.checked}))}
              />
              <span className="checkbox-label">Strict Compliance Mode</span>
            </label>
          </div>

          <div className="form-actions">
            <button 
              onClick={handleComplianceCheck}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Checking...' : '🔍 Full Compliance Check'}
            </button>
            <button 
              onClick={handleQuickCheck}
              disabled={loading}
              className="btn-secondary"
            >
              {loading ? 'Checking...' : '⚡ Quick Check'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'results' && renderResults()}

      {activeTab === 'templates' && (
        <div className="templates-section">
          <h3>Rights Templates</h3>
          <div className="templates-grid">
            {Object.entries(templates).map(([templateName, template]) => (
              <div key={templateName} className="template-card">
                <h4>{template.name}</h4>
                <p>{template.description}</p>
                <div className="template-details">
                  <p><strong>Usage Types:</strong> {template.usage_types.join(', ')}</p>
                  <p><strong>Default Territories:</strong> {template.default_territories.join(', ')}</p>
                  <p><strong>Typical Term:</strong> {template.typical_term_months} months</p>
                  {template.industry_standard && (
                    <span className="industry-standard">✅ Industry Standard</span>
                  )}
                </div>
                <button 
                  onClick={() => applyTemplate(templateName)}
                  className="btn-secondary"
                >
                  Apply Template
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="history-section">
          <h3>Rights & Compliance History</h3>
          <p>Compliance check history will be displayed here.</p>
          <div className="coming-soon">
            <p>📊 Advanced compliance analytics and history tracking coming soon!</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default RightsComplianceComponent;