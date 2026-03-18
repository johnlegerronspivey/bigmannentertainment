import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import NotificationBell from "./NotificationBell";

const NavigationBar = () => {
  const { user, logout, isAdmin } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLabelDropdownOpen, setIsLabelDropdownOpen] = useState(false);
  const [isAdminDropdownOpen, setIsAdminDropdownOpen] = useState(false);
  const [isBusinessDropdownOpen, setIsBusinessDropdownOpen] = useState(false);
  const [isEthereumDropdownOpen, setIsEthereumDropdownOpen] = useState(false);
  const [isIndustryDropdownOpen, setIsIndustryDropdownOpen] = useState(false);
  const [isContentDropdownOpen, setIsContentDropdownOpen] = useState(false);
  const [isWeb3DropdownOpen, setIsWeb3DropdownOpen] = useState(false);
  const [isSecurityDropdownOpen, setIsSecurityDropdownOpen] = useState(false);
  const [isToolsDropdownOpen, setIsToolsDropdownOpen] = useState(false);
  const [isFinanceDropdownOpen, setIsFinanceDropdownOpen] = useState(false);

  const closeAllDropdowns = () => {
    setIsLabelDropdownOpen(false);
    setIsAdminDropdownOpen(false);
    setIsBusinessDropdownOpen(false);
    setIsEthereumDropdownOpen(false);
    setIsIndustryDropdownOpen(false);
    setIsContentDropdownOpen(false);
    setIsWeb3DropdownOpen(false);
    setIsSecurityDropdownOpen(false);
    setIsToolsDropdownOpen(false);
    setIsFinanceDropdownOpen(false);
  };

  const handleLogout = async () => {
    await logout();
  };

  if (!user) {
    // Public Navigation for non-authenticated users
    return (
      <nav className="bg-purple-800 text-white shadow-lg" data-testid="public-navbar">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <img 
                src="/big-mann-logo.png" 
                alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
                className="w-10 h-10 object-contain"
              />
              <Link to="/" className="text-xl font-bold" data-testid="nav-logo-link">Big Mann Entertainment</Link>
              <span className="text-xs text-gray-500 ml-2">by John LeGerron Spivey</span>
            </div>

            {/* Desktop Public Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <Link to="/" className="hover:text-purple-200" data-testid="nav-home-link">Home</Link>
              <Link to="/platforms" className="hover:text-purple-200" data-testid="nav-platforms-link">Platforms</Link>
              <Link to="/pricing" className="hover:text-purple-200" data-testid="nav-pricing-link">Pricing</Link>
              <Link to="/about" className="hover:text-purple-200" data-testid="nav-about-link">About</Link>
              <Link to="/login" className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg" data-testid="nav-login-link">Login</Link>
              <Link to="/register" className="bg-white text-purple-800 hover:bg-gray-100 px-4 py-2 rounded-lg font-semibold" data-testid="nav-register-link">Sign Up</Link>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="text-white hover:text-purple-200"
                data-testid="nav-mobile-menu-btn"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>

          {/* Mobile Navigation for Public */}
          {isMenuOpen && (
            <div className="md:hidden pb-4 border-t border-purple-600 mt-4" data-testid="nav-mobile-menu">
              <div className="flex flex-col space-y-2">
                <Link to="/" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Home</Link>
                <Link to="/platforms" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Platforms</Link>
                <Link to="/pricing" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Pricing</Link>
                <Link to="/about" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>About</Link>
                <Link to="/login" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Login</Link>
                <Link to="/register" className="bg-white text-purple-800 hover:bg-gray-100 py-2 px-2 rounded-lg font-semibold mt-2" onClick={() => setIsMenuOpen(false)}>Sign Up</Link>
              </div>
            </div>
          )}
        </div>
      </nav>
    );
  }

  return (
    <nav className="bg-purple-800 text-white shadow-lg" data-testid="authenticated-navbar">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-4">
            <img 
              src="/big-mann-logo.png" 
              alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
              className="w-10 h-10 object-contain"
            />
            <Link to="/" className="text-xl font-bold" data-testid="nav-logo-link">Big Mann Entertainment</Link>
          </div>

          {/* Desktop Navigation - Consolidated into dropdown groups */}
          <div className="hidden md:flex items-center space-x-3">

            {/* Admin Dropdown - First item, always visible */}
            {isAdmin() && (
              <div className="relative">
                <button
                  onClick={() => { closeAllDropdowns(); setIsAdminDropdownOpen(!isAdminDropdownOpen); }}
                  className="bg-red-600 hover:bg-red-700 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors font-medium text-sm"
                  data-testid="nav-admin-dropdown"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                  Admin <span>▼</span>
                </button>
                {isAdminDropdownOpen && (
                  <div className="absolute top-full left-0 mt-2 w-52 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                    <Link to="/admin/domain" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Domain Config</Link>
                    <Link to="/admin/rds-upgrade" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-rds-upgrade">RDS Upgrade</Link>
                    <Link to="/admin/users" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>User Management</Link>
                    <Link to="/admin/content" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Content Moderation</Link>
                    <Link to="/admin/analytics" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Analytics</Link>
                    <Link to="/admin/notifications" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Notifications</Link>
                    <Link to="/admin/ddex" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>DDEX Admin</Link>
                    <Link to="/admin/sponsorship" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Sponsorship Admin</Link>
                    <Link to="/admin/industry" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Industry Admin</Link>
                  </div>
                )}
              </div>
            )}

            {/* Content Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsContentDropdownOpen(!isContentDropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-content-dropdown"
              >
                Content <span className="ml-1 text-xs">▼</span>
              </button>
              {isContentDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-52 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                  <Link to="/library" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Library</Link>
                  <Link to="/upload" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Upload</Link>
                  <Link to="/image-upload" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Image Upload & NFT</Link>
                  <Link to="/distribute" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Distribute</Link>
                  <Link to="/distribution-hub" className="block px-4 py-2 text-sm text-purple-300 hover:bg-slate-700 font-medium" onClick={closeAllDropdowns} data-testid="nav-distribution-hub">Distribution Hub</Link>
                  <Link to="/creative-studio" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Creative Studio</Link>
                  <Link to="/watermark" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-watermark">Watermarking</Link>
                  <Link to="/content-management" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-content-management">My Content</Link>
                  <Link to="/platforms" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Platforms</Link>
                </div>
              )}
            </div>

            {/* Business Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsBusinessDropdownOpen(!isBusinessDropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-business-dropdown"
              >
                Business <span className="ml-1 text-xs">▼</span>
              </button>
              {isBusinessDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-56 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600 max-h-80 overflow-y-auto">
                  <Link to="/business" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Business Identifiers</Link>
                  <Link to="/ddex" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>DDEX</Link>
                  <Link to="/sponsorship" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Sponsorship</Link>
                  <Link to="/tax" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Tax Management</Link>
                  <Link to="/gs1-licensing" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>GS1 & Licensing</Link>
                  <Link to="/content-removal" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Content Removal</Link>
                  <Link to="/social-strategy" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Social Media Strategy</Link>
                  <Link to="/content-ingestion" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Content Ingestion</Link>
                  <Link to="/comprehensive-workflow" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>End-to-End Workflow</Link>
                  <Link to="/social-media-phases-5-10" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Social Media Phases 5-10</Link>
                  <Link to="/real-time-royalty-engine" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Real-Time Royalty Engine</Link>
                  <Link to="/workflow-integration" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Workflow Integration Hub</Link>
                  <Link to="/support-center" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Support Center</Link>
                </div>
              )}
            </div>

            {/* Web3 & Blockchain Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsWeb3DropdownOpen(!isWeb3DropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-web3-dropdown"
              >
                Web3 <span className="ml-1 text-xs">▼</span>
              </button>
              {isWeb3DropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-52 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                  <Link to="/dao" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>DAO Governance</Link>
                  <Link to="/dao-v2" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>DAO 2.0</Link>
                  <Link to="/ethereum/deploy" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Deploy Contracts</Link>
                  <Link to="/ethereum/transactions" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Transaction History</Link>
                  <Link to="/ethereum/dao-voting" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>DAO Voting</Link>
                  <Link to="/smart-contracts" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Smart Contracts</Link>
                  <Link to="/digital-twins" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Digital Twins</Link>
                  <Link to="/marketplace" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Royalty Marketplace</Link>
                </div>
              )}
            </div>

            {/* Security Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsSecurityDropdownOpen(!isSecurityDropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-security-dropdown"
              >
                Security <span className="ml-1 text-xs">▼</span>
              </button>
              {isSecurityDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-52 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                  <Link to="/rights-compliance" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Rights & Compliance</Link>
                  <Link to="/audit-trail" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Audit Trail</Link>
                  <Link to="/cve-management" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>CVE Brain</Link>
                  <Link to="/security-audit" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Security Audit</Link>
                  <Link to="/macie" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Macie PII Detection</Link>
                  <Link to="/tenant-management" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Tenant Management</Link>
                </div>
              )}
            </div>

            {/* AWS & Tools Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsToolsDropdownOpen(!isToolsDropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-tools-dropdown"
              >
                Tools <span className="ml-1 text-xs">▼</span>
              </button>
              {isToolsDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-56 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                  <Link to="/aws-enterprise" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>AWS Enterprise</Link>
                  <Link to="/cloudwatch" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>CloudWatch Monitoring</Link>
                  <Link to="/agency-automation" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Agency Automation</Link>
                  <Link to="/usage-analytics" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Usage Analytics</Link>
                  <Link to="/qldb" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Dispute Ledger</Link>
                  <Link to="/enterprise" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Enterprise Command</Link>
                  <Link to="/integrations" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-integrations-link">Live Integrations</Link>
                  <Link to="/aws-media" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-media-link">Media Processing</Link>
                  <Link to="/aws-livestream" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-livestream-link">Live Streaming</Link>
                  <Link to="/aws-comms" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-comms-link">Communications</Link>
                  <Link to="/aws-security" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-security-link">Security (WAF)</Link>
                  <Link to="/aws-ai-analytics" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-ai-link">AI Analytics</Link>
                  <Link to="/aws-data-analytics" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-data-link">Data Analytics</Link>
                  <Link to="/aws-blockchain" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-blockchain-link">Managed Blockchain</Link>
                  <Link to="/aws-ai-content" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-ai-content-link">AI Content (Translate/Polly)</Link>
                  <Link to="/aws-messaging" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-messaging-link">Messaging & Events</Link>
                  <Link to="/aws-infrastructure" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns} data-testid="nav-aws-infra-link">Infrastructure</Link>
                </div>
              )}
            </div>

            {/* Industry Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsIndustryDropdownOpen(!isIndustryDropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-industry-dropdown"
              >
                Industry <span className="ml-1 text-xs">▼</span>
              </button>
              {isIndustryDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                  <Link to="/industry" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Dashboard</Link>
                  <Link to="/industry/partners" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Partners</Link>
                  <Link to="/industry/coverage" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Coverage</Link>
                  <Link to="/industry/identifiers" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Identifiers</Link>
                  <Link to="/music-reports" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Music Reports</Link>
                  <Link to="/agency/register" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Agency Registration</Link>
                  <Link to="/agency/dashboard" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Agency Portal</Link>
                </div>
              )}
            </div>

            {/* Label Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsLabelDropdownOpen(!isLabelDropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-label-dropdown"
              >
                Label <span className="ml-1 text-xs">▼</span>
              </button>
              {isLabelDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                  <Link to="/label/dashboard" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Label Dashboard</Link>
                  <Link to="/label/directory" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Label Directory</Link>
                  <Link to="/uln" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>UL Network</Link>
                  <Link to="/label/projects" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Project Management</Link>
                  <Link to="/label/marketing" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Marketing</Link>
                  <Link to="/label/financial" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Financial Management</Link>
                  <Link to="/label/royalties" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Royalty Splits</Link>
                </div>
              )}
            </div>

            {/* Finance Dropdown */}
            <div className="relative">
              <button
                onClick={() => { closeAllDropdowns(); setIsFinanceDropdownOpen(!isFinanceDropdownOpen); }}
                className="hover:text-purple-200 flex items-center text-sm"
                data-testid="nav-finance-dropdown"
              >
                Finance <span className="ml-1 text-xs">▼</span>
              </button>
              {isFinanceDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-44 bg-slate-800 rounded-md shadow-lg py-1 z-50 border border-slate-600">
                  <Link to="/earnings" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Earnings</Link>
                  <Link to="/payments" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Payments</Link>
                  <Link to="/pricing" className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={closeAllDropdowns}>Pricing</Link>
                </div>
              )}
            </div>

            <Link to="/social" className="hover:text-purple-200 text-sm" data-testid="nav-social-link">Social</Link>
            <Link to="/about" className="hover:text-purple-200 text-sm" data-testid="nav-about-link">About</Link>

            <Link to="/creator-profiles" className="hover:text-purple-200 text-sm" data-testid="nav-creator-profiles-link">Creator Profile</Link>
            <Link to="/messages" className="hover:text-purple-200 text-sm" data-testid="nav-messages-link">Messages</Link>
            <Link to="/creator-analytics" className="hover:text-purple-200 text-sm" data-testid="nav-analytics-link">Analytics</Link>
            <Link to="/subscription" className="hover:text-purple-200 text-sm" data-testid="nav-subscription-link">Plans</Link>

            <NotificationBell />

            <Link 
              to="/profile/settings" 
              className="bg-purple-700 hover:bg-purple-600 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors font-medium text-sm"
              data-testid="nav-profile-link"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
              Profile
            </Link>

            <button onClick={handleLogout} className="hover:text-purple-200 text-sm" data-testid="nav-logout-btn">Logout</button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-white hover:text-purple-200"
              data-testid="nav-mobile-menu-btn"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden pb-4 border-t border-purple-600 mt-4" data-testid="nav-mobile-menu">
            <div className="flex flex-col space-y-2">
              <Link to="/library" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Library</Link>
              <Link to="/upload" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Upload</Link>
              <Link to="/image-upload" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Image Upload & NFT</Link>
              <Link to="/rights-compliance" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Rights & Compliance</Link>
              <Link to="/smart-contracts" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Smart Contracts</Link>
              <Link to="/audit-trail" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Audit Trail</Link>
              <Link to="/distribute" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Distribute</Link>
              <Link to="/platforms" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Platforms</Link>
              <Link to="/business" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Business</Link>
              <Link to="/industry" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Industry</Link>
              <Link to="/earnings" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Earnings</Link>
              <Link to="/payments" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Payments</Link>
              <Link to="/pricing" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Pricing</Link>
              <Link to="/label/dashboard" className="hover:text-purple-200 py-2 px-2" onClick={() => setIsMenuOpen(false)}>Label</Link>
              
              {/* Profile & DAO Links - Highlighted in Mobile Menu */}
              <div className="border-t border-purple-600 mt-2 pt-2">
                <Link 
                  to="/creator-profiles" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>Creator Profile</span>
                </Link>
                <Link 
                  to="/watermark" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>Watermarking</span>
                </Link>
                <Link 
                  to="/content-management" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>My Content</span>
                </Link>
                <Link 
                  to="/messages" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>Messages</span>
                </Link>
                <Link 
                  to="/notifications" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                  data-testid="nav-mobile-notifications-link"
                >
                  <span>Notifications</span>
                </Link>
                <Link 
                  to="/creator-analytics" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>Analytics</span>
                </Link>
                <Link 
                  to="/subscription" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>Plans</span>
                </Link>
                <Link 
                  to="/profile/settings" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>My Profile</span>
                </Link>
                <Link 
                  to="/dao" 
                  className="bg-purple-700 hover:bg-purple-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>DAO Governance</span>
                </Link>

                <Link 
                  to="/social" 
                  className="bg-blue-700 hover:bg-blue-600 py-3 px-4 rounded-lg flex items-center gap-2 mb-2 transition-colors font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span>Social Media</span>
                </Link>
              </div>
              
              {isAdmin() && (
                <Link 
                  to="/admin/users" 
                  className="hover:text-purple-200 py-2 px-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Admin
                </Link>
              )}
              <button 
                onClick={() => {
                  handleLogout();
                  setIsMenuOpen(false);
                }} 
                className="hover:text-purple-200 py-2 px-2 text-left"
                data-testid="nav-mobile-logout-btn"
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default NavigationBar;
