import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ComprehensiveLicensingComponents = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [businessInfo, setBusinessInfo] = useState(null);
  const [licenseAgreements, setLicenseAgreements] = useState([]);
  const [automatedWorkflows, setAutomatedWorkflows] = useState([]);
  const [complianceDocs, setComplianceDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Get auth token
  const getAuthToken = () => {
    return localStorage.getItem('token');
  };

  const getAuthHeaders = () => {
    const token = getAuthToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  };

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/comprehensive-licensing/dashboard`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data.comprehensive_licensing_dashboard);
      } else {
        setError('Failed to load licensing dashboard');
      }
    } catch (err) {
      setError('Error loading dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Load business information
  const loadBusinessInformation = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/comprehensive-licensing/business-information`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setBusinessInfo(data.business_information);
      } else {
        setError('Failed to load business information');
      }
    } catch (err) {
      setError('Error loading business information');
    } finally {
      setLoading(false);
    }
  };

  // Load license agreements
  const loadLicenseAgreements = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/comprehensive-licensing/license-agreements`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setLicenseAgreements(data.agreements);
      } else {
        setError('Failed to load license agreements');
      }
    } catch (err) {
      setError('Error loading license agreements');
    } finally {
      setLoading(false);
    }
  };

  // Load automated workflows
  const loadAutomatedWorkflows = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/comprehensive-licensing/workflows`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setAutomatedWorkflows(data.workflows);
      } else {
        setError('Failed to load automated workflows');
      }
    } catch (err) {
      setError('Error loading automated workflows');
    } finally {
      setLoading(false);
    }
  };

  // Load compliance documents
  const loadComplianceDocs = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/comprehensive-licensing/compliance-documents`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setComplianceDocs(data.compliance_documents);
      } else {
        setError('Failed to load compliance documents');
      }
    } catch (err) {
      setError('Error loading compliance documents');
    } finally {
      setLoading(false);
    }
  };

  // Generate comprehensive platform licenses
  const generateAllPlatformLicenses = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/comprehensive-licensing/generate-all-platform-licenses`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Successfully initiated comprehensive licensing for ${data.platforms_licensed} platforms!`);
        loadDashboardData(); // Refresh dashboard
      } else {
        setError('Failed to generate comprehensive licenses');
      }
    } catch (err) {
      setError('Error generating comprehensive licenses');
    } finally {
      setLoading(false);
    }
  };

  // Validate business information
  const validateBusinessInfo = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/comprehensive-licensing/business-information/validate`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Business Information Validation Score: ${data.validation_results.overall_score.toFixed(1)}%`);
      } else {
        setError('Failed to validate business information');
      }
    } catch (err) {
      setError('Error validating business information');
    } finally {
      setLoading(false);
    }
  };

  // Initialize data load
  useEffect(() => {
    loadDashboardData();
    loadBusinessInformation();
  }, []);

  // Tab change handler
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setError('');
    
    switch(tab) {
      case 'agreements':
        loadLicenseAgreements();
        break;
      case 'workflows':
        loadAutomatedWorkflows();
        break;
      case 'compliance':
        loadComplianceDocs();
        break;
      default:
        break;
    }
  };

  // Dashboard Component
  const LicensingDashboard = () => (
    <div className="licensing-dashboard">
      <div className="dashboard-header">
        <h2>🎯 Comprehensive Platform Licensing Dashboard</h2>
        <button 
          onClick={generateAllPlatformLicenses}
          className="generate-licenses-btn"
          disabled={loading}
        >
          {loading ? 'Generating...' : '🚀 Generate All Platform Licenses'}
        </button>
      </div>

      {dashboardData && (
        <div className="dashboard-grid">
          {/* Business Information Summary */}
          <div className="dashboard-card">
            <h3>🏢 Business Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Business Entity:</span>
                <span className="value">{dashboardData.business_information_summary?.business_entity}</span>
              </div>
              <div className="info-item">
                <span className="label">Business Owner:</span>
                <span className="value">{dashboardData.business_information_summary?.business_owner}</span>
              </div>
              <div className="info-item">
                <span className="label">EIN:</span>
                <span className="value">{dashboardData.business_information_summary?.ein}</span>
              </div>
              <div className="info-item">
                <span className="label">GS1 Company Prefix:</span>
                <span className="value">{dashboardData.business_information_summary?.gs1_company_prefix}</span>
              </div>
              <div className="info-item">
                <span className="label">ISAN Prefix:</span>
                <span className="value">{dashboardData.business_information_summary?.isan_prefix || 'johnlegerron'}</span>
              </div>
            </div>
            <button onClick={validateBusinessInfo} className="validate-btn">
              ✅ Validate Business Information
            </button>
          </div>

          {/* Licensing Overview */}
          <div className="dashboard-card">
            <h3>📋 Licensing Overview</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-number">{dashboardData.licensing_overview?.total_comprehensive_agreements || 0}</span>
                <span className="stat-label">Comprehensive Agreements</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">{dashboardData.licensing_overview?.total_platforms_licensed || 0}</span>
                <span className="stat-label">Platforms Licensed</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">${(dashboardData.licensing_overview?.total_licensing_fees || 0).toLocaleString()}</span>
                <span className="stat-label">Total Licensing Investment</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">{dashboardData.licensing_overview?.active_agreements || 0}</span>
                <span className="stat-label">Active Agreements</span>
              </div>
            </div>
          </div>

          {/* Platform Categories */}
          <div className="dashboard-card">
            <h3>🎵 Platform Categories</h3>
            <div className="category-breakdown">
              {dashboardData.platform_category_breakdown && Object.entries(dashboardData.platform_category_breakdown).map(([category, stats]) => (
                <div key={category} className="category-item">
                  <div className="category-header">
                    <span className="category-name">{category.replace('_', ' ').toUpperCase()}</span>
                    <span className="category-count">{stats.platform_count} platforms</span>
                  </div>
                  <div className="category-stats">
                    <span>Agreements: {stats.agreement_count}</span>
                    <span>Investment: ${stats.total_fees?.toLocaleString() || 0}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance Status */}
          <div className="dashboard-card">
            <h3>✅ Compliance Status</h3>
            <div className="compliance-overview">
              <div className="compliance-stat">
                <span className="compliance-number">{dashboardData.compliance_status?.total_compliance_documents || 0}</span>
                <span className="compliance-label">Total Documents</span>
              </div>
              <div className="compliance-stat">
                <span className="compliance-number pending">{dashboardData.compliance_status?.pending_legal_review || 0}</span>
                <span className="compliance-label">Pending Review</span>
              </div>
              <div className="compliance-stat">
                <span className="compliance-number approved">{dashboardData.compliance_status?.approved_documents || 0}</span>
                <span className="compliance-label">Approved</span>
              </div>
            </div>
          </div>

          {/* Automation Status */}
          <div className="dashboard-card">
            <h3>🤖 Automation Status</h3>
            <div className="automation-overview">
              <div className="automation-stat">
                <span className="automation-number">{dashboardData.automation_status?.total_workflows || 0}</span>
                <span className="automation-label">Total Workflows</span>
              </div>
              <div className="automation-processes">
                <h4>Automated Processes:</h4>
                <ul>
                  {dashboardData.automation_status?.automated_processes?.map((process, index) => (
                    <li key={index}>✓ {process}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="dashboard-card">
            <h3>🕒 Recent Activity</h3>
            <div className="activity-list">
              {dashboardData.recent_activity?.slice(0, 5).map((activity, index) => (
                <div key={index} className="activity-item">
                  <span className="activity-type">{activity.type?.replace('_', ' ').toUpperCase()}</span>
                  <span className="activity-description">{activity.description}</span>
                  <span className="activity-date">{new Date(activity.date).toLocaleDateString()}</span>
                </div>
              )) || <p>No recent activity</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // Business Information Component
  const BusinessInformation = () => (
    <div className="business-information">
      <h2>🏢 Consolidated Business Information</h2>
      
      {businessInfo && (
        <div className="business-info-grid">
          <div className="info-section">
            <h3>Core Business Details</h3>
            <div className="info-fields">
              <div className="field">
                <label>Business Entity:</label>
                <span>{businessInfo.business_entity}</span>
              </div>
              <div className="field">
                <label>Business Owner:</label>
                <span>{businessInfo.business_owner}</span>
              </div>
              <div className="field">
                <label>Business Type:</label>
                <span>{businessInfo.business_type}</span>
              </div>
              <div className="field">
                <label>Industry:</label>
                <span>{businessInfo.industry_classification}</span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>Legal Identifiers</h3>
            <div className="info-fields">
              <div className="field">
                <label>EIN:</label>
                <span>{businessInfo.ein}</span>
              </div>
              <div className="field">
                <label>TIN:</label>
                <span>{businessInfo.tin}</span>
              </div>
              <div className="field">
                <label>GS1 Company Prefix:</label>
                <span>{businessInfo.company_prefix}</span>
              </div>
              <div className="field">
                <label>Legal Entity GLN:</label>
                <span>{businessInfo.legal_entity_gln}</span>
              </div>
              <div className="field">
                <label>ISAN Prefix:</label>
                <span>{businessInfo.isan_prefix}</span>
              </div>
            </div>
          </div>

          <div className="info-section">
            <h3>Contact Information</h3>
            <div className="info-fields">
              <div className="field">
                <label>Email:</label>
                <span>{businessInfo.contact_email}</span>
              </div>
              <div className="field">
                <label>Phone:</label>
                <span>{businessInfo.contact_phone || '(334) 669-8638'}</span>
              </div>
              {businessInfo.business_address && (
                <div className="field">
                  <label>Address:</label>
                  <span>
                    {businessInfo.business_address.street}, {businessInfo.business_address.city}, 
                    {businessInfo.business_address.state} {businessInfo.business_address.zip}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="info-section">
            <h3>Platform Integration</h3>
            <div className="info-fields">
              <div className="field">
                <label>Total Platforms:</label>
                <span>{businessInfo.distribution_platform_ids?.length || 0}</span>
              </div>
              <div className="field">
                <label>Platform Credentials:</label>
                <span>{Object.keys(businessInfo.platform_credentials || {}).length} configured</span>
              </div>
              <div className="field">
                <label>API Integrations:</label>
                <span>{Object.keys(businessInfo.api_configurations || {}).length} active</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  // License Agreements Component
  const LicenseAgreements = () => (
    <div className="license-agreements">
      <h2>📋 Comprehensive License Agreements</h2>
      
      <div className="agreements-list">
        {licenseAgreements.length > 0 ? licenseAgreements.map((agreement, index) => (
          <div key={index} className="agreement-card">
            <div className="agreement-header">
              <h3>{agreement.license_type?.replace('_', ' ').toUpperCase()}</h3>
              <span className={`status ${agreement.agreement_status}`}>
                {agreement.agreement_status?.toUpperCase()}
              </span>
            </div>
            
            <div className="agreement-stats">
              <div className="stat">
                <span className="stat-label">Platforms:</span>
                <span className="stat-value">{agreement.total_platforms}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Categories:</span>
                <span className="stat-value">{agreement.platform_categories?.length || 0}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Duration:</span>
                <span className="stat-value">{agreement.license_duration_months} months</span>
              </div>
            </div>

            <div className="agreement-financial">
              <h4>Financial Terms</h4>
              {agreement.licensing_fees && Object.entries(agreement.licensing_fees).map(([category, fee]) => (
                <div key={category} className="fee-item">
                  <span>{category.replace('_', ' ').toUpperCase()}:</span>
                  <span>${fee?.toLocaleString()}</span>
                </div>
              ))}
            </div>

            <div className="agreement-dates">
              <div className="date-item">
                <span>Created:</span>
                <span>{new Date(agreement.created_at).toLocaleDateString()}</span>
              </div>
              {agreement.effective_date && (
                <div className="date-item">
                  <span>Effective:</span>
                  <span>{new Date(agreement.effective_date).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>
        )) : (
          <div className="no-agreements">
            <p>No license agreements found.</p>
            <button onClick={generateAllPlatformLicenses} className="create-agreement-btn">
              🚀 Create Comprehensive Agreement
            </button>
          </div>
        )}
      </div>
    </div>
  );

  // Automated Workflows Component
  const AutomatedWorkflows = () => (
    <div className="automated-workflows">
      <h2>🤖 Automated Licensing Workflows</h2>
      
      <div className="workflows-list">
        {automatedWorkflows.length > 0 ? automatedWorkflows.map((workflow, index) => (
          <div key={index} className="workflow-card">
            <div className="workflow-header">
              <h3>{workflow.workflow_name}</h3>
              <span className={`status ${workflow.workflow_status || 'active'}`}>
                {(workflow.workflow_status || 'active').toUpperCase()}
              </span>
            </div>
            
            <div className="workflow-details">
              <div className="workflow-stat">
                <span className="stat-label">Automation Steps:</span>
                <span className="stat-value">{workflow.automation_steps?.length || 0}</span>
              </div>
              <div className="workflow-stat">
                <span className="stat-label">Trigger Conditions:</span>
                <span className="stat-value">{workflow.trigger_conditions?.length || 0}</span>
              </div>
            </div>

            <div className="workflow-steps">
              <h4>Automation Steps:</h4>
              <ul>
                {workflow.automation_steps?.slice(0, 3).map((step, stepIndex) => (
                  <li key={stepIndex}>
                    {step.step?.replace('_', ' ')} 
                    {step.auto_execute ? ' (Auto)' : ' (Manual)'}
                  </li>
                ))}
              </ul>
            </div>

            <div className="workflow-created">
              <span>Created: {new Date(workflow.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        )) : (
          <div className="no-workflows">
            <p>No automated workflows found.</p>
            <p>Workflows are automatically created when you generate comprehensive licenses.</p>
          </div>
        )}
      </div>
    </div>
  );

  // Compliance Documents Component
  const ComplianceDocuments = () => (
    <div className="compliance-documents">
      <h2>✅ Compliance Documentation</h2>
      
      <div className="compliance-stats">
        <div className="compliance-stat-card">
          <span className="stat-number">{complianceDocs.length}</span>
          <span className="stat-label">Total Documents</span>
        </div>
        <div className="compliance-stat-card">
          <span className="stat-number pending">
            {complianceDocs.filter(doc => doc.legal_review_status === 'pending').length}
          </span>
          <span className="stat-label">Pending Review</span>
        </div>
        <div className="compliance-stat-card">
          <span className="stat-number approved">
            {complianceDocs.filter(doc => doc.legal_review_status === 'approved').length}
          </span>
          <span className="stat-label">Approved</span>
        </div>
      </div>
      
      <div className="documents-list">
        {complianceDocs.length > 0 ? complianceDocs.map((doc, index) => (
          <div key={index} className="document-card">
            <div className="document-header">
              <h3>{doc.document_type?.replace('_', ' ').toUpperCase()}</h3>
              <span className={`status ${doc.legal_review_status}`}>
                {doc.legal_review_status?.toUpperCase()}
              </span>
            </div>
            
            <div className="document-details">
              <div className="detail-item">
                <span className="label">Platform:</span>
                <span className="value">{doc.platform_id}</span>
              </div>
              <div className="detail-item">
                <span className="label">Requirements:</span>
                <span className="value">{doc.compliance_requirements?.length || 0} items</span>
              </div>
              <div className="detail-item">
                <span className="label">Created:</span>
                <span className="value">{new Date(doc.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="compliance-requirements">
              <h4>Compliance Requirements:</h4>
              <ul>
                {doc.compliance_requirements?.slice(0, 3).map((req, reqIndex) => (
                  <li key={reqIndex}>{req.replace('_', ' ')}</li>
                ))}
                {doc.compliance_requirements?.length > 3 && (
                  <li>... and {doc.compliance_requirements.length - 3} more</li>
                )}
              </ul>
            </div>
          </div>
        )) : (
          <div className="no-documents">
            <p>No compliance documents found.</p>
            <p>Documents are automatically generated when you create comprehensive licenses.</p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="comprehensive-licensing-container">
      <div className="licensing-header">
        <h1>🎯 Comprehensive Platform Licensing System</h1>
        <p>Complete business information integration with automated licensing workflows</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="licensing-tabs">
        <button 
          className={activeTab === 'dashboard' ? 'tab active' : 'tab'}
          onClick={() => handleTabChange('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={activeTab === 'business' ? 'tab active' : 'tab'}
          onClick={() => handleTabChange('business')}
        >
          🏢 Business Info
        </button>
        <button 
          className={activeTab === 'agreements' ? 'tab active' : 'tab'}
          onClick={() => handleTabChange('agreements')}
        >
          📋 Agreements
        </button>
        <button 
          className={activeTab === 'workflows' ? 'tab active' : 'tab'}
          onClick={() => handleTabChange('workflows')}
        >
          🤖 Workflows
        </button>
        <button 
          className={activeTab === 'compliance' ? 'tab active' : 'tab'}
          onClick={() => handleTabChange('compliance')}
        >
          ✅ Compliance
        </button>
      </div>

      <div className="licensing-content">
        {loading && <div className="loading-spinner">Loading...</div>}
        
        {activeTab === 'dashboard' && <LicensingDashboard />}
        {activeTab === 'business' && <BusinessInformation />}
        {activeTab === 'agreements' && <LicenseAgreements />}
        {activeTab === 'workflows' && <AutomatedWorkflows />}
        {activeTab === 'compliance' && <ComplianceDocuments />}
      </div>
    </div>
  );
};

export default ComprehensiveLicensingComponents;