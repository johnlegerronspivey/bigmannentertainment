import React, { useState, useEffect } from 'react';
import './SmartContract.css';

const SmartContractComponent = () => {
    const [user, setUser] = useState(null);
    const [contracts, setContracts] = useState([]);
    const [proposals, setProposals] = useState([]);
    const [templates, setTemplates] = useState({});
    const [networks, setNetworks] = useState({});
    const [analytics, setAnalytics] = useState(null);
    const [ethereumStatus, setEthereumStatus] = useState(null);
    const [walletBalance, setWalletBalance] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('contracts');
    
    // Form states
    const [deployForm, setDeployForm] = useState({
        template_name: '',
        content_id: '',
        network: 'polygon',
        constructor_params: {}
    });
    
    const [proposalForm, setProposalForm] = useState({
        title: '',
        description: '',
        vote_type: 'content_acceptance',
        content_id: '',
        voting_period_hours: 168
    });
    
    const [licensingForm, setLicensingForm] = useState({
        content_id: '',
        license_type: 'non-exclusive',
        territories: ['US'],
        usage_rights: ['streaming'],
        royalty_percentage: 10.0,
        upfront_fee_eth: '',
        duration_months: '',
        exclusive: false
    });

    const getBackendUrl = () => {
        return process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    };

    const getAuthToken = () => {
        return localStorage.getItem('token');
    };

    const getAuthHeaders = () => {
        const token = getAuthToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    };

    useEffect(() => {
        checkUserAuth();
        fetchInitialData();
    }, []);

    const checkUserAuth = () => {
        const token = getAuthToken();
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({ 
                    id: payload.sub, 
                    username: payload.username || 'User',
                    is_admin: payload.is_admin || false
                });
            } catch (error) {
                console.error('Error parsing token:', error);
                localStorage.removeItem('token');
            }
        }
    };

    const fetchInitialData = async () => {
        try {
            await Promise.all([
                fetchContracts(),
                fetchProposals(), 
                fetchTemplates(),
                fetchNetworks(),
                fetchAnalytics(),
                fetchEthereumStatus(),
                fetchWalletBalance()
            ]);
        } catch (error) {
            console.error('Error fetching initial data:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchContracts = async () => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/contracts/instances`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setContracts(data.contracts || []);
            }
        } catch (error) {
            console.error('Error fetching contracts:', error);
        }
    };

    const fetchProposals = async () => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/contracts/dao/proposals`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setProposals(data.proposals || []);
            }
        } catch (error) {
            console.error('Error fetching proposals:', error);
        }
    };

    const fetchTemplates = async () => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/contracts/templates`);
            
            if (response.ok) {
                const data = await response.json();
                setTemplates(data.contract_templates || {});
            }
        } catch (error) {
            console.error('Error fetching templates:', error);
        }
    };

    const fetchNetworks = async () => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/contracts/networks`);
            
            if (response.ok) {
                const data = await response.json();
                setNetworks(data.supported_networks || {});
            }
        } catch (error) {
            console.error('Error fetching networks:', error);
        }
    };

    const fetchAnalytics = async () => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/contracts/analytics`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setAnalytics(data.blockchain_analytics || null);
            }
        } catch (error) {
            console.error('Error fetching analytics:', error);
        }
    };

    const deployContract = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('template_name', deployForm.template_name);
            formData.append('content_id', deployForm.content_id);
            formData.append('network', deployForm.network);
            
            const response = await fetch(`${getBackendUrl()}/api/contracts/deploy`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert(`Contract deployed successfully! Contract ID: ${data.contract_id}`);
                setDeployForm({
                    template_name: '',
                    content_id: '',
                    network: 'polygon',
                    constructor_params: {}
                });
                await fetchContracts();
            } else {
                alert(`Error: ${data.detail || 'Failed to deploy contract'}`);
            }
        } catch (error) {
            console.error('Error deploying contract:', error);
            alert('Error deploying contract');
        } finally {
            setLoading(false);
        }
    };

    const createProposal = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('title', proposalForm.title);
            formData.append('description', proposalForm.description);
            formData.append('vote_type', proposalForm.vote_type);
            formData.append('content_id', proposalForm.content_id);
            formData.append('voting_period_hours', proposalForm.voting_period_hours);
            
            const response = await fetch(`${getBackendUrl()}/api/contracts/dao/proposal`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert(`DAO proposal created successfully! Proposal ID: ${data.proposal_id}`);
                setProposalForm({
                    title: '',
                    description: '',
                    vote_type: 'content_acceptance',
                    content_id: '',
                    voting_period_hours: 168
                });
                await fetchProposals();
            } else {
                alert(`Error: ${data.detail || 'Failed to create proposal'}`);
            }
        } catch (error) {
            console.error('Error creating proposal:', error);
            alert('Error creating proposal');
        } finally {
            setLoading(false);
        }
    };

    const voteOnProposal = async (proposalId, voteChoice) => {
        try {
            const formData = new FormData();
            formData.append('vote_choice', voteChoice);
            formData.append('voting_power', '1');
            
            const response = await fetch(`${getBackendUrl()}/api/contracts/dao/vote/${proposalId}`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert(`Vote "${voteChoice}" submitted successfully!`);
                await fetchProposals();
            } else {
                alert(`Error: ${data.detail || 'Failed to submit vote'}`);
            }
        } catch (error) {
            console.error('Error voting:', error);
            alert('Error submitting vote');
        }
    };

    const createLicensingContract = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('content_id', licensingForm.content_id);
            formData.append('license_type', licensingForm.license_type);
            licensingForm.territories.forEach(territory => {
                formData.append('territories', territory);
            });
            licensingForm.usage_rights.forEach(right => {
                formData.append('usage_rights', right);
            });
            formData.append('royalty_percentage', licensingForm.royalty_percentage);
            if (licensingForm.upfront_fee_eth) {
                formData.append('upfront_fee_eth', licensingForm.upfront_fee_eth);
            }
            if (licensingForm.duration_months) {
                formData.append('duration_months', licensingForm.duration_months);
            }
            formData.append('exclusive', licensingForm.exclusive);
            
            const response = await fetch(`${getBackendUrl()}/api/contracts/licensing/create`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert(`Licensing contract created successfully! Contract ID: ${data.contract_id}`);
                setLicensingForm({
                    content_id: '',
                    license_type: 'non-exclusive',
                    territories: ['US'],
                    usage_rights: ['streaming'],
                    royalty_percentage: 10.0,
                    upfront_fee_eth: '',
                    duration_months: '',
                    exclusive: false
                });
                await fetchContracts();
            } else {
                alert(`Error: ${data.detail || 'Failed to create licensing contract'}`);
            }
        } catch (error) {
            console.error('Error creating licensing contract:', error);
            alert('Error creating licensing contract');
        } finally {
            setLoading(false);
        }
    };

    if (!user) {
        return (
            <div className="smart-contract-container">
                <div className="auth-required">
                    <h2>Authentication Required</h2>
                    <p>Please log in to access Smart Contract & DAO features.</p>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="smart-contract-container">
                <div className="loading">
                    <div className="loading-spinner"></div>
                    <p>Loading Smart Contract data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="smart-contract-container">
            <div className="smart-contract-header">
                <img 
                    src="/big-mann-logo.png" 
                    alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
                    className="smart-contract-logo"
                />
                <h1>🔗 Smart Contracts & DAO</h1>
                <p>Web3 Integration for Automatic Licensing and Community Governance</p>
            </div>

            <div className="tab-navigation">
                <button 
                    className={activeTab === 'contracts' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('contracts')}
                >
                    My Contracts ({contracts.length})
                </button>
                <button 
                    className={activeTab === 'deploy' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('deploy')}
                >
                    Deploy Contract
                </button>
                <button 
                    className={activeTab === 'dao' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('dao')}
                >
                    DAO Proposals ({proposals.length})
                </button>
                <button 
                    className={activeTab === 'licensing' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('licensing')}
                >
                    Licensing
                </button>
                <button 
                    className={activeTab === 'analytics' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('analytics')}
                >
                    Analytics
                </button>
            </div>

            <div className="tab-content">
                {activeTab === 'contracts' && (
                    <div className="contracts-section">
                        <h2>My Smart Contracts</h2>
                        
                        {contracts.length === 0 ? (
                            <div className="empty-state">
                                <p>No smart contracts deployed yet.</p>
                                <button onClick={() => setActiveTab('deploy')}>Deploy Your First Contract</button>
                            </div>
                        ) : (
                            <div className="contracts-grid">
                                {contracts.map((contract, index) => (
                                    <div key={index} className="contract-card">
                                        <div className="contract-header">
                                            <h3>{contract.contract_name}</h3>
                                            <span className={`status ${contract.status}`}>
                                                {contract.status}
                                            </span>
                                        </div>
                                        <div className="contract-details">
                                            <p><strong>Network:</strong> {contract.network}</p>
                                            <p><strong>Content ID:</strong> {contract.content_id}</p>
                                            {contract.contract_address && (
                                                <p><strong>Address:</strong> 
                                                    <code>{contract.contract_address.substring(0, 10)}...</code>
                                                </p>
                                            )}
                                            <p><strong>Created:</strong> {new Date(contract.created_at).toLocaleDateString()}</p>
                                        </div>
                                        {contract.status === 'deployed' && (
                                            <div className="contract-actions">
                                                <button onClick={() => {
                                                    // Add execute function functionality
                                                    alert('Execute function feature coming soon!');
                                                }}>Execute Function</button>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'deploy' && (
                    <div className="deploy-section">
                        <h2>Deploy Smart Contract</h2>
                        
                        <form onSubmit={deployContract} className="deploy-form">
                            <div className="form-group">
                                <label>Contract Template</label>
                                <select
                                    value={deployForm.template_name}
                                    onChange={(e) => setDeployForm({...deployForm, template_name: e.target.value})}
                                    required
                                >
                                    <option value="">Select a template...</option>
                                    {Object.entries(templates).map(([key, template]) => (
                                        <option key={key} value={key}>
                                            {template.name} - {template.description}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Content ID</label>
                                <input
                                    type="text"
                                    value={deployForm.content_id}
                                    onChange={(e) => setDeployForm({...deployForm, content_id: e.target.value})}
                                    placeholder="Enter content identifier to associate with contract"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Blockchain Network</label>
                                <select
                                    value={deployForm.network}
                                    onChange={(e) => setDeployForm({...deployForm, network: e.target.value})}
                                >
                                    {Object.entries(networks).map(([key, network]) => (
                                        <option key={key} value={key}>
                                            {network.name} ({network.type})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <button type="submit" disabled={loading}>
                                {loading ? 'Deploying...' : 'Deploy Contract'}
                            </button>
                        </form>

                        <div className="templates-info">
                            <h3>Available Templates</h3>
                            <div className="templates-grid">
                                {Object.entries(templates).map(([key, template]) => (
                                    <div key={key} className="template-card">
                                        <h4>{template.name}</h4>
                                        <p>{template.description}</p>
                                        <div className="template-details">
                                            <span className="template-type">{template.type}</span>
                                            <span className="template-network">{template.default_network}</span>
                                            {template.is_audited && <span className="audited">✅ Audited</span>}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'dao' && (
                    <div className="dao-section">
                        <h2>DAO Governance</h2>
                        
                        <div className="create-proposal">
                            <h3>Create New Proposal</h3>
                            <form onSubmit={createProposal} className="proposal-form">
                                <div className="form-group">
                                    <label>Proposal Title</label>
                                    <input
                                        type="text"
                                        value={proposalForm.title}
                                        onChange={(e) => setProposalForm({...proposalForm, title: e.target.value})}
                                        placeholder="Enter proposal title"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        value={proposalForm.description}
                                        onChange={(e) => setProposalForm({...proposalForm, description: e.target.value})}
                                        placeholder="Describe your proposal..."
                                        rows="4"
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Vote Type</label>
                                    <select
                                        value={proposalForm.vote_type}
                                        onChange={(e) => setProposalForm({...proposalForm, vote_type: e.target.value})}
                                    >
                                        <option value="content_acceptance">Content Acceptance</option>
                                        <option value="licensing_approval">Licensing Approval</option>
                                        <option value="royalty_distribution">Royalty Distribution</option>
                                        <option value="platform_governance">Platform Governance</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Content ID (Optional)</label>
                                    <input
                                        type="text"
                                        value={proposalForm.content_id}
                                        onChange={(e) => setProposalForm({...proposalForm, content_id: e.target.value})}
                                        placeholder="Associated content identifier"
                                    />
                                </div>

                                <button type="submit" disabled={loading}>
                                    {loading ? 'Creating...' : 'Create Proposal'}
                                </button>
                            </form>
                        </div>

                        <div className="proposals-list">
                            <h3>Active Proposals</h3>
                            {proposals.length === 0 ? (
                                <p>No active proposals.</p>
                            ) : (
                                <div className="proposals-grid">
                                    {proposals.map((proposal, index) => (
                                        <div key={index} className="proposal-card">
                                            <div className="proposal-header">
                                                <h4>{proposal.proposal_title}</h4>
                                                <span className={`status ${proposal.status}`}>
                                                    {proposal.status}
                                                </span>
                                            </div>
                                            <p>{proposal.proposal_description}</p>
                                            
                                            <div className="voting-stats">
                                                <div className="vote-counts">
                                                    <span>👍 {proposal.yes_votes || 0}</span>
                                                    <span>👎 {proposal.no_votes || 0}</span>
                                                    <span>🤷 {proposal.abstain_votes || 0}</span>
                                                </div>
                                                <div className="total-votes">
                                                    Total: {proposal.total_votes || 0} votes
                                                </div>
                                            </div>

                                            {proposal.status === 'active' && (
                                                <div className="voting-actions">
                                                    <button onClick={() => voteOnProposal(proposal.proposal_id, 'yes')}>
                                                        Vote Yes
                                                    </button>
                                                    <button onClick={() => voteOnProposal(proposal.proposal_id, 'no')}>
                                                        Vote No
                                                    </button>
                                                    <button onClick={() => voteOnProposal(proposal.proposal_id, 'abstain')}>
                                                        Abstain
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {activeTab === 'licensing' && (
                    <div className="licensing-section">
                        <h2>Automatic Licensing Contracts</h2>
                        
                        <form onSubmit={createLicensingContract} className="licensing-form">
                            <div className="form-group">
                                <label>Content ID</label>
                                <input
                                    type="text"
                                    value={licensingForm.content_id}
                                    onChange={(e) => setLicensingForm({...licensingForm, content_id: e.target.value})}
                                    placeholder="Enter content identifier for licensing"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>License Type</label>
                                <select
                                    value={licensingForm.license_type}
                                    onChange={(e) => setLicensingForm({...licensingForm, license_type: e.target.value})}
                                >
                                    <option value="non-exclusive">Non-Exclusive</option>
                                    <option value="exclusive">Exclusive</option>
                                    <option value="sync">Sync License</option>
                                    <option value="master">Master License</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Royalty Percentage</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    min="0"
                                    max="100"
                                    value={licensingForm.royalty_percentage}
                                    onChange={(e) => setLicensingForm({...licensingForm, royalty_percentage: parseFloat(e.target.value)})}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={licensingForm.exclusive}
                                        onChange={(e) => setLicensingForm({...licensingForm, exclusive: e.target.checked})}
                                    />
                                    Exclusive License
                                </label>
                            </div>

                            <button type="submit" disabled={loading}>
                                {loading ? 'Creating...' : 'Create Licensing Contract'}
                            </button>
                        </form>
                    </div>
                )}

                {activeTab === 'analytics' && (
                    <div className="analytics-section">
                        <h2>Blockchain Analytics</h2>
                        
                        {analytics ? (
                            <div className="analytics-grid">
                                <div className="analytics-card">
                                    <h3>Smart Contracts</h3>
                                    <div className="analytics-stats">
                                        <div className="stat">
                                            <span className="stat-number">{analytics.total_contracts_deployed}</span>
                                            <span className="stat-label">Total Deployed</span>
                                        </div>
                                        <div className="stat">
                                            <span className="stat-number">{analytics.successful_executions}</span>
                                            <span className="stat-label">Successful Executions</span>
                                        </div>
                                        <div className="stat">
                                            <span className="stat-number">{analytics.failed_executions}</span>
                                            <span className="stat-label">Failed Executions</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="analytics-card">
                                    <h3>DAO Governance</h3>
                                    <div className="analytics-stats">
                                        <div className="stat">
                                            <span className="stat-number">{analytics.total_proposals}</span>
                                            <span className="stat-label">Total Proposals</span>
                                        </div>
                                        <div className="stat">
                                            <span className="stat-number">{analytics.passed_proposals}</span>
                                            <span className="stat-label">Passed</span>
                                        </div>
                                        <div className="stat">
                                            <span className="stat-number">{analytics.rejected_proposals}</span>
                                            <span className="stat-label">Rejected</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="analytics-card">
                                    <h3>Financial Metrics</h3>
                                    <div className="analytics-stats">
                                        <div className="stat">
                                            <span className="stat-number">{analytics.total_gas_spent_eth.toFixed(4)} ETH</span>
                                            <span className="stat-label">Gas Spent</span>
                                        </div>
                                        <div className="stat">
                                            <span className="stat-number">{analytics.total_licensing_revenue_eth.toFixed(4)} ETH</span>
                                            <span className="stat-label">Licensing Revenue</span>
                                        </div>
                                        <div className="stat">
                                            <span className="stat-number">{analytics.total_royalties_distributed_eth.toFixed(4)} ETH</span>
                                            <span className="stat-label">Royalties Distributed</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <p>No analytics data available.</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SmartContractComponent;