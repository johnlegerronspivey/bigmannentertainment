import React, { useState, useEffect, useContext, createContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useLocation, useParams } from "react-router-dom";
import axios from "axios";
import { DDEXERNCreator, DDEXCWRCreator, DDEXMessageList, DDEXIdentifierGenerator, DDEXAdminDashboard } from "./DDEXComponents";
import { SponsorshipDashboard, SponsorshipDealCreator, MetricsRecorder, AdminSponsorshipOverview } from "./SponsorshipComponents";
import { TaxDashboard, Form1099Management, TaxReports, BusinessTaxInfo, BusinessLicenseManagement, ComplianceDashboard } from "./TaxComponents";
import { BusinessIdentifiers, UPCGenerator, ISRCGenerator, ProductManagement } from "./BusinessComponents";
import { IndustryDashboard, IndustryPartners, GlobalDistribution, IndustryCoverage, IPIManagement, IndustryIdentifiersManagement, EnhancedEntertainmentDashboard, PhotographyServices, VideoProductionServices, MonetizationOpportunities, MusicDataExchange, MechanicalLicensingCollective } from "./IndustryComponents";
import { LabelDashboard } from "./LabelComponents";
import { ProjectManagement, MarketingManagement, FinancialManagement } from "./LabelExtendedComponents";
import { PaymentPackages, PaymentCheckout, PaymentStatus, BankAccountManager, DigitalWalletManager } from "./PaymentComponents";
import { EarningsDashboard, RoyaltySplitManager } from "./EarningsComponents";
import { LicensingDashboard, PlatformLicenseManager, LicensingStatus } from './LicensingComponents';
import GS1Components, { GS1Dashboard } from './GS1Components';
import EnhancedUploadComponent from './EnhancedUploadComponent';
import RightsComplianceComponent from './RightsComplianceComponent';
import SmartContractComponent from './SmartContractComponent';
import AuditTrailComponent from './AuditTrailComponent';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Rights & Compliance Component Wrapper
const RightsComplianceWrapper = () => {
  const { user } = useAuth();
  return <RightsComplianceComponent currentUser={user} />;
};
const EnhancedPaymentCheckout = () => {
  const { packageId } = useParams();
  const navigate = useNavigate();
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <button 
          onClick={() => navigate('/pricing')}
          className="text-blue-600 hover:text-blue-800 flex items-center"
        >
          ← Back to Pricing
        </button>
      </div>
      <PaymentCheckout 
        packageId={packageId}
        onSuccess={() => navigate('/payment/success')}
        onCancel={() => navigate('/pricing')}
      />
    </div>
  );
};

// Auth Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      // Try to get current user from backend
      const response = await axios.get(`${API}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data && response.data.email) {
        setUser(response.data);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        // Token is invalid, clear auth
        clearAuth();
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      
      // If token is invalid (401/403), clear auth
      if (error.response?.status === 401 || error.response?.status === 403) {
        clearAuth();
      } else {
        // For other errors, still set loading to false but keep user if token exists
        const token = localStorage.getItem('token');
        if (token) {
          // Create a temporary user object to allow access while API is having issues
          setUser({ 
            email: 'user@bigmannentertainment.com', 
            role: 'user',
            temp: true 
          });
        }
        setLoading(false);
      }
    }
    setLoading(false);
  };

  const clearAuth = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setLoading(false);
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, refresh_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { access_token, refresh_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(newUser);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  // Forgot password
  const forgotPassword = async (email) => {
    try {
      const response = await axios.post(`${API}/auth/forgot-password`, { email });
      return { 
        success: true, 
        message: response.data.message,
        data: response.data
      };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to send reset email' 
      };
    }
  };

  // Reset password
  const resetPassword = async (token, newPassword) => {
    try {
      const response = await axios.post(`${API}/auth/reset-password`, { 
        token, 
        new_password: newPassword 
      });
      return { success: true, message: response.data.message };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Password reset failed' 
      };
    }
  };

  const logout = async () => {
    try {
      // Call backend logout endpoint
      await axios.post(`${API}/auth/logout`);
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      clearAuth();
    }
  };

  const isAdmin = () => {
    return user && (user.is_admin || ['admin', 'super_admin', 'moderator'].includes(user.role));
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      register, 
      forgotPassword,
      resetPassword,
      logout, 
      isAdmin,
      loading 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Admin Route Component
const AdminRoute = ({ children }) => {
  const { user, isAdmin, loading } = useAuth();
  
  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  if (!isAdmin()) {
    return <Navigate to="/" />;
  }
  
  return children;
};

// Navigation Component
const Navigation = () => {
  const { user, logout, isAdmin } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLabelDropdownOpen, setIsLabelDropdownOpen] = useState(false);
  const [isAdminDropdownOpen, setIsAdminDropdownOpen] = useState(false);
  const [isBusinessDropdownOpen, setIsBusinessDropdownOpen] = useState(false);
  const [isIndustryDropdownOpen, setIsIndustryDropdownOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
  };

  if (!user) return null;

  return (
    <nav className="bg-purple-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-4">
            <img 
              src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" 
              alt="Big Mann Entertainment Logo" 
              className="w-8 h-8 object-contain"
            />
            <Link to="/" className="text-xl font-bold">Big Mann Entertainment</Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/library" className="hover:text-purple-200">Library</Link>
            <Link to="/upload" className="hover:text-purple-200">Upload</Link>
            <Link to="/rights-compliance" className="hover:text-purple-200">Rights & Compliance</Link>
            <Link to="/smart-contracts" className="hover:text-purple-200">Smart Contracts</Link>
            <Link to="/audit-trail" className="hover:text-purple-200">Audit Trail</Link>
            <Link to="/distribute" className="hover:text-purple-200">Distribute</Link>
            <Link to="/platforms" className="hover:text-purple-200">Platforms</Link>
            
            {/* Business Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsBusinessDropdownOpen(!isBusinessDropdownOpen)}
                className="hover:text-purple-200 flex items-center"
              >
                Business <span className="ml-1">▼</span>
              </button>
              {isBusinessDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                  <Link to="/business" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Business Identifiers</Link>
                  <Link to="/ddex" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">DDEX</Link>
                  <Link to="/sponsorship" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Sponsorship</Link>
                  <Link to="/tax" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Tax Management</Link>
                  <Link to="/licensing" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Licensing</Link>
                  <Link to="/gs1" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">GS1</Link>
                </div>
              )}
            </div>
            
            {/* Industry Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsIndustryDropdownOpen(!isIndustryDropdownOpen)}
                className="hover:text-purple-200 flex items-center"
              >
                Industry <span className="ml-1">▼</span>
              </button>
              {isIndustryDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                  <Link to="/industry" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Dashboard</Link>
                  <Link to="/industry/partners" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Partners</Link>
                  <Link to="/industry/coverage" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Coverage</Link>
                  <Link to="/industry/identifiers" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Identifiers</Link>
                </div>
              )}
            </div>

            <Link to="/earnings" className="hover:text-purple-200">Earnings</Link>
            <Link to="/pricing" className="hover:text-purple-200">Pricing</Link>

            {/* Label Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsLabelDropdownOpen(!isLabelDropdownOpen)}
                className="hover:text-purple-200 flex items-center"
              >
                Label <span className="ml-1">▼</span>
              </button>
              {isLabelDropdownOpen && (
                <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                  <Link to="/label/dashboard" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Label Dashboard</Link>
                  <Link to="/label/projects" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Project Management</Link>
                  <Link to="/label/marketing" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Marketing</Link>
                  <Link to="/label/financial" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Financial Management</Link>
                  <Link to="/label/royalties" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Royalty Splits</Link>
                </div>
              )}
            </div>

            {/* Admin Dropdown */}
            {isAdmin() && (
              <div className="relative">
                <button
                  onClick={() => setIsAdminDropdownOpen(!isAdminDropdownOpen)}
                  className="hover:text-purple-200 flex items-center"
                >
                  Admin <span className="ml-1">▼</span>
                </button>
                {isAdminDropdownOpen && (
                  <div className="absolute top-full left-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50">
                    <Link to="/admin/users" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">User Management</Link>
                    <Link to="/admin/content" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Content Moderation</Link>
                    <Link to="/admin/analytics" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Analytics</Link>
                    <Link to="/admin/notifications" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Notifications</Link>
                    <Link to="/admin/ddex" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">DDEX Admin</Link>
                    <Link to="/admin/sponsorship" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Sponsorship Admin</Link>
                    <Link to="/admin/industry" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Industry Admin</Link>
                  </div>
                )}
              </div>
            )}

            <button onClick={handleLogout} className="hover:text-purple-200">Logout</button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-white hover:text-purple-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden pb-4 border-t border-purple-600 mt-4">
            <div className="flex flex-col space-y-2">
              <Link 
                to="/library" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Library
              </Link>
              <Link 
                to="/upload" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Upload
              </Link>
              <Link 
                to="/rights-compliance" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Rights & Compliance
              </Link>
              <Link 
                to="/smart-contracts" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Smart Contracts
              </Link>
              <Link 
                to="/audit-trail" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Audit Trail
              </Link>
              <Link 
                to="/distribute" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Distribute
              </Link>
              <Link 
                to="/platforms" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Platforms
              </Link>
              <Link 
                to="/business" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Business
              </Link>
              <Link 
                to="/industry" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Industry
              </Link>
              <Link 
                to="/earnings" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Earnings
              </Link>
              <Link 
                to="/pricing" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Pricing
              </Link>
              <Link 
                to="/label/dashboard" 
                className="hover:text-purple-200 py-2 px-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Label
              </Link>
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

// Home Component
const Home = () => {
  const { user } = useAuth();
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-800 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 sm:py-24">
          <div className="text-center">
            <div className="mb-8">
              <img 
                src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" 
                alt="Big Mann Entertainment Logo" 
                className="w-24 h-24 object-contain mx-auto mb-6"
              />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Big Mann Entertainment
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
              Complete Media Distribution Empire
            </p>
            <p className="text-lg mb-8 max-w-4xl mx-auto">
              Distribute your content across 90+ platforms including social media, streaming, radio, TV, podcasts, NFT marketplaces, and Web3 platforms
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {!user ? (
                <>
                  <Link 
                    to="/register" 
                    className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                  >
                    Start Creating
                  </Link>
                  <Link 
                    to="/platforms" 
                    className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-700 transition-colors"
                  >
                    View Platforms
                  </Link>
                </>
              ) : (
                <>
                  <Link 
                    to="/upload" 
                    className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                  >
                    Upload Content
                  </Link>
                  <Link 
                    to="/distribute" 
                    className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-700 transition-colors"
                  >
                    Start Distribution
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Media Distribution
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From content creation to global distribution, we provide the complete ecosystem for entertainment professionals
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Multi-Format Upload</h3>
              <p className="text-gray-600">Upload audio, video, and images with support for all major formats and high-quality processing.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">90+ Platforms</h3>
              <p className="text-gray-600">Distribute to social media, streaming services, radio stations, TV networks, and emerging Web3 platforms.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Revenue Management</h3>
              <p className="text-gray-600">Track earnings, manage royalty splits, and optimize your revenue streams across all platforms.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Industry Compliance</h3>
              <p className="text-gray-600">DDEX metadata standards, business identifiers, tax management, and full regulatory compliance.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Blockchain & NFTs</h3>
              <p className="text-gray-600">Mint NFTs, deploy smart contracts, and leverage Web3 technologies for next-generation distribution.</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Professional Tools</h3>
              <p className="text-gray-600">Advanced analytics, content management, sponsorship opportunities, and label services.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-purple-50 py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">90+</div>
              <div className="text-gray-600">Distribution Platforms</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">24/7</div>
              <div className="text-gray-600">Global Support</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">100%</div>
              <div className="text-gray-600">Rights Ownership</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-purple-700 mb-2">∞</div>
              <div className="text-gray-600">Upload Capacity</div>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Showcase */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Distribute Everywhere
            </h2>
            <p className="text-xl text-gray-600">
              Reach your audience across all major platforms and emerging networks
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {['Instagram', 'Twitter', 'Facebook', 'TikTok', 'YouTube', 'Spotify', 'Apple Music', 'Netflix', 'CNN', 'MTV', 'OpenSea', 'Billboard'].map((platform) => (
              <div key={platform} className="bg-white p-4 rounded-lg shadow text-center">
                <div className="font-semibold text-gray-800">{platform}</div>
              </div>
            ))}
          </div>

          <div className="text-center mt-8">
            <Link 
              to="/platforms" 
              className="text-purple-600 hover:text-purple-700 font-semibold"
            >
              View all 90+ platforms →
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-purple-600 to-indigo-700 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Distribute Your Content?
          </h2>
          <p className="text-xl mb-8">
            Join thousands of creators who trust Big Mann Entertainment for their media distribution needs
          </p>
          {!user ? (
            <Link 
              to="/register" 
              className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block"
            >
              Get Started Today
            </Link>
          ) : (
            <Link 
              to="/upload" 
              className="bg-white text-purple-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block"
            >
              Upload Your First Content
            </Link>
          )}
        </div>
      </section>
    </div>
  );
};

// Login Component (Password-only, WebAuthn removed)
const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="text-gray-600">Big Mann Entertainment</p>
        </div>

        <div className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handlePasswordLogin} className="space-y-4">
            <div>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter your email"
              />
            </div>

            <div>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Links */}
          <div className="text-center space-y-2">
            <div>
              <Link to="/forgot-password" className="text-purple-600 hover:text-purple-500 text-sm">
                Forgot your password?
              </Link>
            </div>
            <div>
              <Link to="/register" className="text-purple-600 hover:text-purple-500">
                Don't have an account? Sign up
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    business_name: '',
    date_of_birth: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state_province: '',
    postal_code: '',
    country: 'US'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateAge = (dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age >= 18;
  };

  const handleNextStep = () => {
    if (step === 1) {
      // Validate basic info
      if (!formData.email || !formData.password || !formData.full_name) {
        setError('Please fill in all required fields');
        return;
      }
      if (!formData.date_of_birth || !validateAge(formData.date_of_birth)) {
        setError('You must be 18 or older to register');
        return;
      }
      setError('');
      setStep(2);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Convert date string to Date object
    const registrationData = {
      ...formData,
      date_of_birth: new Date(formData.date_of_birth).toISOString()
    };

    const result = await register(registrationData);
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="text-gray-600">Big Mann Entertainment</p>
        </div>

        <div className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Progress indicator */}
          <div className="flex items-center justify-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${step >= 1 ? 'bg-purple-600' : 'bg-gray-300'}`}></div>
            <div className={`w-3 h-3 rounded-full ${step >= 2 ? 'bg-purple-600' : 'bg-gray-300'}`}></div>
          </div>

          {step === 1 && (
            <div className="space-y-4">
              <div>
                <input
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Full Name"
                />
              </div>

              <div>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Password"
                />
              </div>

              <div>
                <input
                  type="text"
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Business Name (Optional)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                <input
                  type="date"
                  required
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <p className="text-xs text-gray-500 mt-1">You must be 18 or older to register</p>
              </div>

              <button
                type="button"
                onClick={handleNextStep}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors"
              >
                Next
              </button>
            </div>
          )}

          {step === 2 && (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <input
                  type="text"
                  required
                  value={formData.address_line1}
                  onChange={(e) => setFormData({ ...formData, address_line1: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Address Line 1"
                />
              </div>

              <div>
                <input
                  type="text"
                  value={formData.address_line2}
                  onChange={(e) => setFormData({ ...formData, address_line2: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Address Line 2 (Optional)"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  required
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="City"
                />
                <input
                  type="text"
                  required
                  value={formData.state_province}
                  onChange={(e) => setFormData({ ...formData, state_province: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="State/Province"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  required
                  value={formData.postal_code}
                  onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Postal Code"
                />
                <select
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="US">United States</option>
                  <option value="CA">Canada</option>
                  <option value="UK">United Kingdom</option>
                  <option value="AU">Australia</option>
                </select>
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-4 rounded-md transition-colors"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Account...
                    </>
                  ) : (
                    'Create Account'
                  )}
                </button>
              </div>
            </form>
          )}

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Already have an account? Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Forgot Password Component
const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [resetData, setResetData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { forgotPassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');
    setResetData(null);

    const result = await forgotPassword(email);
    
    if (result.success) {
      setMessage(result.message);
      // Handle development reset data
      if (result.data && result.data.reset_url) {
        setResetData(result.data);
      }
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleCopyResetUrl = () => {
    if (resetData && resetData.reset_url) {
      navigator.clipboard.writeText(resetData.reset_url);
      alert('Reset URL copied to clipboard!');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset your password
          </h2>
          <p className="text-gray-600">Enter your email to receive a reset link</p>
        </div>

        <div className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {message && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}

          {/* Development Reset Data Display - Only show if email service failed */}
          {resetData && resetData.reset_token && (
            <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded space-y-3">
              <div className="font-semibold">Email Service Unavailable - Development Fallback</div>
              <div className="text-sm">
                <p className="mb-2">{resetData.instructions}</p>
                <div className="bg-blue-50 p-3 rounded border break-all">
                  <div className="font-mono text-xs">{resetData.reset_url}</div>
                </div>
                <div className="flex space-x-2 mt-3">
                  <button
                    onClick={handleCopyResetUrl}
                    className="bg-blue-600 text-white px-3 py-1 text-sm rounded hover:bg-blue-700"
                  >
                    Copy URL
                  </button>
                  <a
                    href={resetData.reset_url}
                    className="bg-green-600 text-white px-3 py-1 text-sm rounded hover:bg-green-700 inline-block"
                  >
                    Go to Reset Page
                  </a>
                </div>
                <p className="text-xs mt-2">Expires in {resetData.expires_in_hours} hours</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Email address"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Reset Password Component
const ResetPassword = () => {
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { resetPassword } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get token from URL parameters
  const token = new URLSearchParams(location.search).get('token');

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link');
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    const result = await resetPassword(token, formData.password);
    
    if (result.success) {
      setMessage('Password reset successfully! Redirecting to login...');
      setTimeout(() => navigate('/login'), 2000);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            Invalid or missing reset token
          </div>
          <Link to="/forgot-password" className="text-purple-600 hover:text-purple-500 mt-4 inline-block">
            Request a new reset link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Set new password
          </h2>
          <p className="text-gray-600">Enter your new password below</p>
        </div>

        <div className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {message && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="New Password"
                minLength="6"
              />
            </div>

            <div>
              <input
                type="password"
                required
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Confirm New Password"
                minLength="6"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Updating Password...' : 'Update Password'}
            </button>
          </form>

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Admin Notification Component
const AdminNotifications = () => {
  const [singleNotification, setSingleNotification] = useState({
    email: '',
    subject: '',
    message: '',
    user_name: ''
  });
  const [bulkNotification, setBulkNotification] = useState({
    subject: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSingleNotification = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await axios.post(`${API}/admin/send-notification`, singleNotification);
      setMessage('Notification sent successfully!');
      setSingleNotification({ email: '', subject: '', message: '', user_name: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send notification');
    }

    setLoading(false);
  };

  const handleBulkNotification = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('subject', bulkNotification.subject);
      formData.append('message', bulkNotification.message);

      const response = await axios.post(`${API}/admin/send-bulk-notification`, formData);
      setMessage(`Bulk notification completed! ${response.data.successful} successful, ${response.data.failed} failed out of ${response.data.total_users} users.`);
      setBulkNotification({ subject: '', message: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send bulk notification');
    }

    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Notifications</h1>
        <p className="text-gray-600">Send email notifications to users from no-reply@bigmannentertainment.com</p>
      </div>

      {message && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
          {message}
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-8">
        {/* Single Notification */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Send Single Notification</h2>
          <form onSubmit={handleSingleNotification} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">User Email</label>
              <input
                type="email"
                required
                value={singleNotification.email}
                onChange={(e) => setSingleNotification({ ...singleNotification, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="user@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">User Name (Optional)</label>
              <input
                type="text"
                value={singleNotification.user_name}
                onChange={(e) => setSingleNotification({ ...singleNotification, user_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input
                type="text"
                required
                value={singleNotification.subject}
                onChange={(e) => setSingleNotification({ ...singleNotification, subject: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Important Update"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                required
                rows="4"
                value={singleNotification.message}
                onChange={(e) => setSingleNotification({ ...singleNotification, message: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Your notification message..."
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Notification'}
            </button>
          </form>
        </div>

        {/* Bulk Notification */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Send Bulk Notification</h2>
          <p className="text-sm text-gray-600 mb-4">Send notification to all active users</p>
          <form onSubmit={handleBulkNotification} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input
                type="text"
                required
                value={bulkNotification.subject}
                onChange={(e) => setBulkNotification({ ...bulkNotification, subject: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Platform Update"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                required
                rows="6"
                value={bulkNotification.message}
                onChange={(e) => setBulkNotification({ ...bulkNotification, message: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Your message to all users..."
              />
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    This will send the notification to ALL active users in the system. Use with caution.
                  </p>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Sending to All Users...' : 'Send Bulk Notification'}
            </button>
          </form>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Email Configuration</h3>
        <p className="text-blue-700 mb-2">
          All notifications are sent from: <strong>no-reply@bigmannentertainment.com</strong>
        </p>
        <p className="text-blue-700 text-sm">
          Emails include professional Big Mann Entertainment branding and are sent using secure SMTP protocols.
          If email service is unavailable, users will receive fallback notifications through the platform.
        </p>
      </div>
    </div>
  );
};

// 404 Error Page Component
const NotFound = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <img 
            src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-24 h-24 object-contain mx-auto mb-6"
          />
        </div>
        <h1 className="text-6xl font-bold text-purple-600 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Page Not Found</h2>
        <p className="text-gray-600 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="space-y-4">
          <Link 
            to="/" 
            className="block bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors"
          >
            Return Home
          </Link>
          <Link 
            to="/platforms" 
            className="block border-2 border-purple-600 text-purple-600 hover:bg-purple-600 hover:text-white font-bold py-3 px-6 rounded-md transition-colors"
          >
            View Platforms
          </Link>
        </div>
        
        <div className="mt-8 text-sm text-gray-500">
          <p>If you believe this is an error, please contact our support team.</p>
        </div>
      </div>
    </div>
  );
};

// Enhanced placeholder components for other routes
const Library = () => {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMedia();
  }, []);

  const loadMedia = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please login.');
        setLoading(false);
        return;
      }

      // Try the correct backend endpoint
      let response;
      try {
        // Primary endpoint - correct backend endpoint
        response = await axios.get(`${API}/media/library`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (firstError) {
        console.log('Library endpoint failed, trying user-media endpoint...');
        try {
          response = await axios.get(`${API}/media`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        } catch (secondError) {
          console.log('Media endpoint failed, trying list endpoint...');
          response = await axios.get(`${API}/media/list`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        }
      }

      // Handle different response formats
      let mediaItems = [];
      if (response.data?.media_items) {
        mediaItems = response.data.media_items;
      } else if (response.data?.media) {
        mediaItems = response.data.media;
      } else if (Array.isArray(response.data)) {
        mediaItems = response.data;
      } else if (response.data?.data) {
        mediaItems = response.data.data;
      }

      console.log('Loaded media items:', mediaItems);
      setMedia(mediaItems || []);
    } catch (error) {
      console.error('Error loading media:', error);
      
      if (error.response?.status === 401) {
        setError('Authentication expired. Please login again.');
      } else if (error.response?.status === 404) {
        setError('Media service not available. This may be temporary.');
      } else {
        setError(`Failed to load media: ${error.response?.data?.detail || error.message}`);
      }
    }
    setLoading(false);
  };

  const filteredMedia = media.filter(item => {
    if (filter === 'all') return true;
    return item.content_type === filter;
  });

  const deleteMedia = async (mediaId) => {
    if (!confirm('Are you sure you want to delete this media?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/media/${mediaId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setMedia(prev => prev.filter(item => item.id !== mediaId));
      alert('Media deleted successfully!');
    } catch (error) {
      console.error('Delete error:', error);
      alert(`Failed to delete media: ${error.response?.data?.detail || error.message}`);
    }
  };

  const refreshMedia = () => {
    loadMedia();
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your media library...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="text-red-600 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Media</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-x-4">
            <button 
              onClick={refreshMedia}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700"
            >
              Retry
            </button>
            <Link to="/upload" className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700">
              Upload New Content
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Media Library</h1>
          <p className="text-gray-600">{media.length} files in your library</p>
        </div>
        <div className="space-x-3">
          <button
            onClick={refreshMedia}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
          >
            Refresh
          </button>
          <Link
            to="/upload"
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
          >
            Upload Content
          </Link>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
          {[
            { key: 'all', label: 'All Files', count: media.length },
            { key: 'audio', label: 'Audio', count: media.filter(m => m.content_type === 'audio').length },
            { key: 'video', label: 'Video', count: media.filter(m => m.content_type === 'video').length },
            { key: 'image', label: 'Images', count: media.filter(m => m.content_type === 'image').length }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === tab.key 
                  ? 'bg-white text-purple-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>
      </div>

      {filteredMedia.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredMedia.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow border overflow-hidden">
              {/* Media Preview */}
              <div className="aspect-video bg-gray-100 flex items-center justify-center">
                {item.content_type === 'image' ? (
                  <img 
                    src={`${API}/media/${item.id}/download`}
                    alt={item.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className={`w-full h-full flex items-center justify-center text-6xl ${item.content_type === 'image' ? 'hidden' : ''}`}>
                  {item.content_type === 'audio' ? '🎵' :
                   item.content_type === 'video' ? '🎥' : '📄'}
                </div>
              </div>

              {/* Media Info */}
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-1 truncate">{item.title}</h3>
                <p className="text-sm text-gray-500 mb-2">
                  {item.content_type} • {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Unknown date'}
                </p>
                
                {item.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{item.description}</p>
                )}

                {/* Actions */}
                <div className="flex space-x-2">
                  <a
                    href={`${API}/media/${item.id}/download`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded text-sm text-center"
                  >
                    View
                  </a>
                  <Link
                    to={`/distribute?media=${item.id}&title=${encodeURIComponent(item.title)}`}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded text-sm text-center"
                  >
                    Distribute
                  </Link>
                  <button
                    onClick={() => deleteMedia(item.id)}
                    className="px-3 py-2 text-red-600 hover:text-red-800 border border-red-200 hover:border-red-300 rounded text-sm"
                  >
                    🗑️
                  </button>
                </div>

                {/* Status */}
                <div className="mt-3 flex justify-between items-center text-xs">
                  <span className={`px-2 py-1 rounded ${
                    item.is_approved ? 'bg-green-100 text-green-800' : 
                    item.approval_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {item.is_approved ? 'Approved' : 
                     item.approval_status === 'pending' ? 'Pending' : 'Draft'}
                  </span>
                  {item.download_count > 0 && (
                    <span className="text-gray-500">{item.download_count} downloads</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m4 0H3a1 1 0 00-1 1v13a1 1 0 001 1h18a1 1 0 001-1V5a1 1 0 00-1-1z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No {filter === 'all' ? '' : filter} files found</h3>
          <p className="text-gray-600 mb-4">
            {filter === 'all' 
              ? 'Your uploaded content will appear here.' 
              : `No ${filter} files in your library.`}
          </p>
          <Link 
            to="/upload" 
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 inline-block"
          >
            Upload Your First {filter === 'all' ? 'Content' : filter.charAt(0).toUpperCase() + filter.slice(1)}
          </Link>
        </div>
      )}
    </div>
  );
};

const Upload = () => {
  const { user } = useAuth();
  
  const handleUploadComplete = (result) => {
    console.log('Upload completed:', result);
    // Optionally refresh user media or show success message
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Upload Media</h1>
          <p className="text-gray-600 mt-2">Upload your music, videos, and artwork with comprehensive metadata</p>
        </div>
        
        <EnhancedUploadComponent 
          currentUser={user}
          onUploadComplete={handleUploadComplete}
        />
      </div>
    </div>
  );
};

const Distribute = () => {
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [userMedia, setUserMedia] = useState([]);
  const [loading, setLoading] = useState(false);
  const [distributions, setDistributions] = useState([]);
  const [loadingMedia, setLoadingMedia] = useState(true);
  const [error, setError] = useState(null);
  
  const location = useLocation();

  // Distribution platforms (91+ platforms as shown in backend)
  const platforms = {
    "Social Media": [
      { id: "instagram", name: "Instagram", icon: "📸", active: true },
      { id: "tiktok", name: "TikTok", icon: "🎵", active: true },
      { id: "facebook", name: "Facebook", icon: "👥", active: true },
      { id: "twitter", name: "Twitter", icon: "🐦", active: true },
      { id: "youtube", name: "YouTube", icon: "📺", active: true },
      { id: "snapchat", name: "Snapchat", icon: "👻", active: true },
    ],
    "Streaming Services": [
      { id: "spotify", name: "Spotify", icon: "🎶", active: true },
      { id: "apple_music", name: "Apple Music", icon: "🍎", active: true },
      { id: "amazon_music", name: "Amazon Music", icon: "🛒", active: true },
      { id: "tidal", name: "Tidal", icon: "🌊", active: true },
      { id: "deezer", name: "Deezer", icon: "🎧", active: true },
      { id: "pandora", name: "Pandora", icon: "📻", active: true },
    ],
    "Radio & Broadcast": [
      { id: "iheartradio", name: "iHeartRadio", icon: "❤️", active: true },
      { id: "siriusxm", name: "SiriusXM", icon: "📡", active: true },
      { id: "clear_channel", name: "Clear Channel", icon: "📻", active: true },
      { id: "cumulus", name: "Cumulus Media", icon: "☁️", active: true },
    ],
    "Television & Video": [
      { id: "netflix", name: "Netflix", icon: "🎬", active: true },
      { id: "hulu", name: "Hulu", icon: "📺", active: true },
      { id: "amazon_prime", name: "Amazon Prime", icon: "🎥", active: true },
      { id: "hbo_max", name: "HBO Max", icon: "🎭", active: true },
    ]
  };

  // Load user media on component mount
  useEffect(() => {
    loadUserMedia();
    loadDistributions();
    
    // Check for pre-selected media from URL parameters
    const urlParams = new URLSearchParams(location.search);
    const mediaId = urlParams.get('media');
    const mediaTitle = urlParams.get('title');
    
    if (mediaId) {
      // Pre-select media if coming from library
      setSelectedMedia({
        id: mediaId,
        title: decodeURIComponent(mediaTitle || 'Selected Media')
      });
    }
  }, [location.search]);

  const loadUserMedia = async () => {
    setLoadingMedia(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please login.');
        setLoadingMedia(false);
        return;
      }

      // Try the correct backend endpoint
      let response;
      try {
        // Primary endpoint - correct backend endpoint
        response = await axios.get(`${API}/media/library`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (firstError) {
        console.log('Library endpoint failed, trying user-media endpoint...');
        try {
          response = await axios.get(`${API}/media`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        } catch (secondError) {
          console.log('Media endpoint failed, trying list endpoint...');
          response = await axios.get(`${API}/media/list`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        }
      }

      // Handle different response formats
      let mediaItems = [];
      if (response.data?.media_items) {
        mediaItems = response.data.media_items;
      } else if (response.data?.media) {
        mediaItems = response.data.media;
      } else if (Array.isArray(response.data)) {
        mediaItems = response.data;
      } else if (response.data?.data) {
        mediaItems = response.data.data;
      }

      console.log('Loaded user media for distribution:', mediaItems);
      setUserMedia(mediaItems || []);
      
      // Auto-select media if passed via URL and exists in user media
      const urlParams = new URLSearchParams(location.search);
      const preSelectedMediaId = urlParams.get('media');
      
      if (preSelectedMediaId && mediaItems.length > 0) {
        const preSelectedMedia = mediaItems.find(m => m.id === preSelectedMediaId);
        if (preSelectedMedia) {
          setSelectedMedia(preSelectedMedia);
        }
      }
      
    } catch (error) {
      console.error('Error loading user media:', error);
      
      if (error.response?.status === 401) {
        setError('Authentication expired. Please login again.');
      } else if (error.response?.status === 404) {
        setError('Media service not available. This may be temporary.');
      } else {
        setError(`Failed to load media: ${error.response?.data?.detail || error.message}`);
      }
    }
    setLoadingMedia(false);
  };

  const loadDistributions = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Try multiple endpoints to get distribution history
      let response;
      try {
        response = await axios.get(`${API}/distribution/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (historyError) {
        console.log('History endpoint failed, trying distribution list...');
        try {
          response = await axios.get(`${API}/distribution`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        } catch (listError) {
          console.log('Distribution list failed, trying status endpoint...');
          response = await axios.get(`${API}/distribution/status`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
        }
      }

      // Handle different response formats
      let distributionData = [];
      if (response.data?.distributions) {
        distributionData = response.data.distributions;
      } else if (Array.isArray(response.data)) {
        distributionData = response.data;
      } else if (response.data?.data) {
        distributionData = response.data.data;
      }

      console.log('Loaded distribution history:', distributionData);
      setDistributions(distributionData || []);
    } catch (error) {
      console.error('Error loading distributions:', error);
      
      // Don't show error to user unless it's critical
      if (error.response?.status === 401) {
        console.log('Authentication required for distribution history');
      }
    }
  };

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const startDistribution = async () => {
    if (!selectedMedia || selectedPlatforms.length === 0) {
      alert('Please select media and at least one platform');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Show initial loading message
      const loadingMessage = `Starting distribution of "${selectedMedia.title}" to ${selectedPlatforms.length} platforms...`;
      console.log(loadingMessage);

      const response = await axios.post(`${API}/distribution/distribute`, {
        media_id: selectedMedia.id,
        platforms: selectedPlatforms,
        custom_message: `Distributing ${selectedMedia.title} to ${selectedPlatforms.length} platforms`,
        hashtags: []
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.data) {
        const distributionResult = response.data;
        
        // Show detailed success message with results
        let successMessage = `🎉 Distribution Successful!\n\n`;
        successMessage += `Content: "${selectedMedia.title}"\n`;
        successMessage += `Distribution ID: ${distributionResult.distribution_id}\n`;
        successMessage += `Platforms: ${selectedPlatforms.length} selected\n`;
        successMessage += `Status: ${distributionResult.status}\n\n`;
        
        // Show individual platform results if available
        if (distributionResult.results) {
          successMessage += `Platform Results:\n`;
          Object.entries(distributionResult.results).forEach(([platform, result]) => {
            const statusIcon = result.status === 'success' ? '✅' : '❌';
            successMessage += `${statusIcon} ${platform}: ${result.status}\n`;
            if (result.post_id || result.track_id || result.video_id) {
              successMessage += `   ID: ${result.post_id || result.track_id || result.video_id}\n`;
            }
          });
        }
        
        successMessage += `\nYou can track the delivery status in your Distribution History.`;
        
        alert(successMessage);
        
        // Reload distributions to show the new one
        loadDistributions();
        
        // Reset selection
        setSelectedPlatforms([]);
        
        // Optional: Show delivery tracking
        console.log('Distribution Details:', distributionResult);
      }
    } catch (error) {
      console.error('Distribution error:', error);
      let errorMessage = `❌ Distribution Failed for "${selectedMedia.title}"\n\n`;
      
      if (error.response?.data?.detail) {
        errorMessage += `Error: ${error.response.data.detail}\n`;
      } else if (error.response?.status === 401) {
        errorMessage += 'Error: Authentication required. Please login again.\n';
      } else if (error.response?.status === 403) {
        errorMessage += 'Error: You do not have permission to distribute this content.\n';
      } else if (error.response?.status === 404) {
        errorMessage += 'Error: Content not found. Please refresh and try again.\n';
      } else if (error.message) {
        errorMessage += `Error: ${error.message}\n`;
      }
      
      errorMessage += '\nPlease check your content and platform selections, then try again.';
      alert(errorMessage);
    }
    setLoading(false);
  };

  const totalPlatforms = Object.values(platforms).reduce((sum, category) => sum + category.length, 0);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Distribute Content</h1>
        <p className="text-gray-600">Distribute your content across {totalPlatforms}+ platforms with a single click</p>
      </div>

      {/* Distribution Status Overview */}
      {distributions.length > 0 && (
        <div className="mb-6 bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-800">Distribution Overview</h3>
              <p className="text-sm text-gray-600">
                {distributions.length} distributions • {
                  distributions.filter(d => d.status === 'completed').length
                } completed • {
                  distributions.filter(d => d.status === 'processing').length
                } processing
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {distributions.filter(d => d.status === 'processing').length > 0 && (
                <div className="flex items-center text-yellow-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600 mr-2"></div>
                  <span className="text-sm">Processing...</span>
                </div>
              )}
              <button
                onClick={loadDistributions}
                className="text-purple-600 hover:text-purple-800 text-sm font-medium"
              >
                Refresh Status
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-red-600 mr-3">⚠️</div>
            <div>
              <h3 className="text-red-800 font-medium">Error Loading Content</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
              <button 
                onClick={loadUserMedia}
                className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Media Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Select Content</h3>
              <button
                onClick={loadUserMedia}
                className="text-purple-600 hover:text-purple-800 text-sm"
              >
                Refresh
              </button>
            </div>
            
            {loadingMedia ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                <p className="mt-2 text-gray-500 text-sm">Loading your content...</p>
              </div>
            ) : userMedia.length > 0 ? (
              <div className="space-y-3">
                {userMedia.map((media) => (
                  <div
                    key={media.id}
                    onClick={() => setSelectedMedia(media)}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedMedia?.id === media.id ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded flex items-center justify-center ${
                        media.content_type === 'audio' ? 'bg-blue-100 text-blue-600' :
                        media.content_type === 'video' ? 'bg-green-100 text-green-600' :
                        'bg-yellow-100 text-yellow-600'
                      }`}>
                        {media.content_type === 'audio' ? '🎵' :
                         media.content_type === 'video' ? '🎥' : '🖼️'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{media.title}</p>
                        <p className="text-sm text-gray-500">{media.content_type}</p>
                      </div>
                      {selectedMedia?.id === media.id && (
                        <div className="text-purple-600">
                          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <div className="text-gray-400 mb-3">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m4 0H3a1 1 0 00-1 1v13a1 1 0 001 1h18a1 1 0 001-1V5a1 1 0 00-1-1z" />
                  </svg>
                </div>
                <p className="mb-2">No content available for distribution</p>
                <Link to="/upload" className="text-purple-600 hover:text-purple-800">
                  Upload your first file
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Platform Selection */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Select Platforms ({selectedPlatforms.length} selected)</h3>
              <div className="space-x-2">
                <button
                  onClick={() => setSelectedPlatforms([])}
                  className="text-gray-600 hover:text-gray-800 px-3 py-1 text-sm"
                >
                  Clear All
                </button>
                <button
                  onClick={() => {
                    const allIds = Object.values(platforms).flat().map(p => p.id);
                    setSelectedPlatforms(allIds);
                  }}
                  className="text-purple-600 hover:text-purple-800 px-3 py-1 text-sm"
                >
                  Select All
                </button>
              </div>
            </div>

            {Object.entries(platforms).map(([category, platformList]) => (
              <div key={category} className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">{category}</h4>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {platformList.map((platform) => (
                    <div
                      key={platform.id}
                      onClick={() => handlePlatformToggle(platform.id)}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedPlatforms.includes(platform.id) 
                          ? 'border-purple-500 bg-purple-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">{platform.icon}</span>
                        <div>
                          <p className="font-medium">{platform.name}</p>
                          <p className="text-xs text-gray-500">
                            {platform.active ? 'Active' : 'Coming Soon'}
                          </p>
                        </div>
                        {selectedPlatforms.includes(platform.id) && (
                          <div className="ml-auto text-purple-600">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            <div className="mt-6 pt-6 border-t">
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  {selectedMedia ? `Selected: ${selectedMedia.title}` : 'No content selected'} • {selectedPlatforms.length} of {totalPlatforms}+ platforms selected
                </div>
                <button
                  onClick={startDistribution}
                  disabled={!selectedMedia || selectedPlatforms.length === 0 || loading}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Distributing...' : `Distribute to ${selectedPlatforms.length} Platforms`}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Distributions */}
      {distributions.length > 0 && (
        <div className="mt-8 bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Distribution History & Delivery Status</h3>
            <button
              onClick={loadDistributions}
              className="text-purple-600 hover:text-purple-800 text-sm"
            >
              Refresh Status
            </button>
          </div>
          <div className="space-y-4">
            {distributions.slice(0, 10).map((dist, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <p className="font-medium text-lg">{dist.media_title || 'Content'}</p>
                    <p className="text-sm text-gray-500 mb-1">
                      Distribution ID: {dist.id || `dist_${index + 1}`}
                    </p>
                    <p className="text-sm text-gray-600">
                      {dist.target_platforms?.length || 0} platforms • Created: {
                        dist.created_at ? new Date(dist.created_at).toLocaleString() : 'Unknown'
                      }
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    dist.status === 'completed' ? 'bg-green-100 text-green-800' :
                    dist.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    dist.status === 'partial' ? 'bg-orange-100 text-orange-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {dist.status === 'completed' ? '✅ Delivered' :
                     dist.status === 'processing' ? '⏳ Processing' :
                     dist.status === 'partial' ? '⚠️ Partial' :
                     '❌ Failed'}
                  </span>
                </div>

                {/* Platform Results */}
                {dist.results && Object.keys(dist.results).length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Platform Delivery Results:</p>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-2">
                      {Object.entries(dist.results).map(([platform, result]) => (
                        <div
                          key={platform}
                          className={`p-2 rounded text-xs flex items-center justify-between ${
                            result.status === 'success' 
                              ? 'bg-green-50 text-green-800 border border-green-200' 
                              : 'bg-red-50 text-red-800 border border-red-200'
                          }`}
                        >
                          <span className="font-medium">
                            {result.status === 'success' ? '✅' : '❌'} {platform}
                          </span>
                          {(result.post_id || result.track_id || result.video_id || result.listing_id) && (
                            <span className="text-xs opacity-75">
                              {(result.post_id || result.track_id || result.video_id || result.listing_id).substring(0, 8)}...
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Selected Platforms List */}
                {dist.target_platforms && dist.target_platforms.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-1">Target Platforms:</p>
                    <div className="flex flex-wrap gap-1">
                      {dist.target_platforms.map((platform, pidx) => (
                        <span
                          key={pidx}
                          className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded"
                        >
                          {platform}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="mt-3 flex gap-2">
                  {dist.status === 'processing' && (
                    <button
                      onClick={loadDistributions}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Check Status
                    </button>
                  )}
                  {dist.status === 'completed' && (
                    <span className="text-green-600 text-sm">
                      ✅ Successfully delivered to all platforms
                    </span>
                  )}
                  {dist.status === 'partial' && (
                    <span className="text-orange-600 text-sm">
                      ⚠️ Delivered to some platforms, check results above
                    </span>
                  )}
                  {dist.status === 'failed' && (
                    <button
                      onClick={() => {
                        setSelectedMedia({ id: dist.media_id, title: dist.media_title || 'Content' });
                        setSelectedPlatforms(dist.target_platforms || []);
                      }}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Retry Distribution
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {distributions.length > 10 && (
            <div className="mt-4 text-center">
              <button
                onClick={() => {
                  // Would implement pagination or "Load More" functionality
                  alert('Pagination feature coming soon! Currently showing last 10 distributions.');
                }}
                className="text-purple-600 hover:text-purple-800 text-sm"
              >
                View All Distributions ({distributions.length} total)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const Platforms = () => (
  <div className="max-w-6xl mx-auto p-6">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Distribution Platforms</h1>
    <p className="text-gray-600 mb-6">Distribute your content across 90+ platforms worldwide</p>
    
    <div className="grid md:grid-cols-3 gap-6 mb-8">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-3 text-purple-600">Social Media</h3>
        <div className="space-y-2 text-sm text-gray-600">
          <p>• Instagram</p>
          <p>• TikTok</p>
          <p>• Facebook</p>
          <p>• Twitter/X</p>
          <p>• YouTube</p>
          <p>• Snapchat</p>
          <p>• LinkedIn</p>
          <p>• Pinterest</p>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-3 text-purple-600">Music Streaming</h3>
        <div className="space-y-2 text-sm text-gray-600">
          <p>• Spotify</p>
          <p>• Apple Music</p>
          <p>• Amazon Music</p>
          <p>• Tidal</p>
          <p>• SoundCloud</p>
          <p>• Pandora</p>
          <p>• Deezer</p>
          <p>• Bandcamp</p>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-3 text-purple-600">TV & Broadcasting</h3>
        <div className="space-y-2 text-sm text-gray-600">
          <p>• Netflix</p>
          <p>• Hulu</p>
          <p>• HBO Max</p>
          <p>• MTV</p>
          <p>• BET</p>
          <p>• CNN</p>
          <p>• ESPN</p>
          <p>• Tubi</p>
        </div>
      </div>
    </div>
    
    <div className="text-center bg-purple-50 p-6 rounded-lg">
      <p className="text-lg font-semibold text-purple-800 mb-2">90+ Platforms Available</p>
      <p className="text-purple-600">Including Web3, NFT Marketplaces, Radio Stations, and More</p>
    </div>
  </div>
);

const Pricing = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleSelectPlan = (planId, planName) => {
    if (!user) {
      // Redirect to register page if not logged in
      navigate('/register');
      return;
    }
    // Redirect to checkout with plan
    navigate(`/payment/checkout/${planId}`);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Pricing Plans</h1>
        <p className="text-xl text-gray-600">Choose the plan that fits your distribution needs</p>
        {!user && (
          <p className="text-purple-600 mt-2">Sign up to get started with any plan</p>
        )}
      </div>
      
      <div className="grid md:grid-cols-3 gap-8">
        <div className="bg-white p-8 rounded-xl shadow-lg border relative">
          <h3 className="text-2xl font-bold mb-3">Basic</h3>
          <div className="mb-6">
            <span className="text-4xl font-bold text-purple-600">$9.99</span>
            <span className="text-gray-500">/month</span>
          </div>
          <ul className="space-y-3 text-gray-600 mb-8">
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              10 releases per month
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Distribution to 25+ platforms
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Standard analytics
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Email support
            </li>
          </ul>
          <button 
            onClick={() => handleSelectPlan('basic', 'Basic')}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            {user ? 'Choose Basic' : 'Sign Up for Basic'}
          </button>
        </div>
        
        <div className="bg-white p-8 rounded-xl shadow-lg border-2 border-purple-600 relative">
          <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
            <span className="bg-purple-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
              MOST POPULAR
            </span>
          </div>
          <h3 className="text-2xl font-bold mb-3">Pro</h3>
          <div className="mb-6">
            <span className="text-4xl font-bold text-purple-600">$29.99</span>
            <span className="text-gray-500">/month</span>
          </div>
          <ul className="space-y-3 text-gray-600 mb-8">
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Unlimited releases
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Distribution to 91+ platforms
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Advanced analytics & reporting
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Priority support
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Royalty management
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              DDEX compliance
            </li>
          </ul>
          <button 
            onClick={() => handleSelectPlan('pro', 'Pro')}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            {user ? 'Choose Pro' : 'Sign Up for Pro'}
          </button>
        </div>
        
        <div className="bg-white p-8 rounded-xl shadow-lg border relative">
          <h3 className="text-2xl font-bold mb-3">Enterprise</h3>
          <div className="mb-6">
            <span className="text-4xl font-bold text-purple-600">$99.99</span>
            <span className="text-gray-500">/month</span>
          </div>
          <ul className="space-y-3 text-gray-600 mb-8">
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Everything in Pro
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              White-label solutions
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              API access & integrations
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Dedicated account manager
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Custom integrations & features
            </li>
            <li className="flex items-center">
              <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              SLA guarantee
            </li>
          </ul>
          <button 
            onClick={() => handleSelectPlan('enterprise', 'Enterprise')}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            {user ? 'Choose Enterprise' : 'Sign Up for Enterprise'}
          </button>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-12 text-center">
        <p className="text-gray-600 mb-4">All plans include:</p>
        <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-500">
          <span>• No setup fees</span>
          <span>• Cancel anytime</span>
          <span>• 14-day free trial</span>
          <span>• 100% rights ownership</span>
          <span>• ISRC & UPC generation</span>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div>
            <h3 className="font-semibold mb-2">Can I upgrade or downgrade my plan?</h3>
            <p className="text-gray-600 text-sm">Yes, you can change your plan at any time. Changes take effect immediately.</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Do you keep any rights to my music?</h3>
            <p className="text-gray-600 text-sm">No, you retain 100% ownership of your content and rights.</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
            <p className="text-gray-600 text-sm">We accept all major credit cards, PayPal, and bank transfers.</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Is there a long-term contract?</h3>
            <p className="text-gray-600 text-sm">No contracts required. You can cancel your subscription anytime.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const Profile = () => (
  <div className="max-w-4xl mx-auto p-6">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Profile Settings</h1>
    <div className="bg-white p-6 rounded-lg shadow">
      <p className="text-gray-600 mb-4">Manage your account settings and preferences.</p>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input type="text" className="w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="Your full name" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input type="email" className="w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="your@email.com" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Business Name</label>
          <input type="text" className="w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="Your business name" />
        </div>
        <button className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
          Save Changes
        </button>
      </div>
    </div>
  </div>
);

// Admin Components
const AdminUsers = () => <div className="p-8"><h1 className="text-2xl font-bold">User Management</h1><p>Admin users management.</p></div>;
const AdminContent = () => <div className="p-8"><h1 className="text-2xl font-bold">Content Moderation</h1><p>Admin content moderation.</p></div>;
const AdminAnalytics = () => <div className="p-8"><h1 className="text-2xl font-bold">Analytics</h1><p>Platform analytics and insights.</p></div>;

// Main App Component
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="App">
          <Navigation />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/platforms" element={<Platforms />} />
            <Route path="/pricing" element={<Pricing />} />

            {/* Protected routes */}
            <Route path="/library" element={<ProtectedRoute><Library /></ProtectedRoute>} />
            <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
            <Route path="/rights-compliance" element={<ProtectedRoute><RightsComplianceWrapper /></ProtectedRoute>} />
            <Route path="/smart-contracts" element={<ProtectedRoute><SmartContractComponent /></ProtectedRoute>} />
            <Route path="/audit-trail" element={<ProtectedRoute><AuditTrailComponent /></ProtectedRoute>} />
            <Route path="/distribute" element={<ProtectedRoute><Distribute /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/earnings" element={<ProtectedRoute><EarningsDashboard /></ProtectedRoute>} />

            {/* Business routes */}
            <Route path="/business" element={<ProtectedRoute><BusinessIdentifiers /></ProtectedRoute>} />
            <Route path="/business/upc" element={<ProtectedRoute><UPCGenerator /></ProtectedRoute>} />
            <Route path="/business/isrc" element={<ProtectedRoute><ISRCGenerator /></ProtectedRoute>} />
            <Route path="/business/products" element={<ProtectedRoute><ProductManagement /></ProtectedRoute>} />

            {/* DDEX routes */}
            <Route path="/ddex" element={<ProtectedRoute><DDEXERNCreator /></ProtectedRoute>} />
            <Route path="/ddex/ern" element={<ProtectedRoute><DDEXERNCreator /></ProtectedRoute>} />
            <Route path="/ddex/cwr" element={<ProtectedRoute><DDEXCWRCreator /></ProtectedRoute>} />
            <Route path="/ddex/messages" element={<ProtectedRoute><DDEXMessageList /></ProtectedRoute>} />
            <Route path="/ddex/identifiers" element={<ProtectedRoute><DDEXIdentifierGenerator /></ProtectedRoute>} />

            {/* Sponsorship routes */}
            <Route path="/sponsorship" element={<ProtectedRoute><SponsorshipDashboard /></ProtectedRoute>} />
            <Route path="/sponsorship/deals" element={<ProtectedRoute><SponsorshipDealCreator /></ProtectedRoute>} />
            <Route path="/sponsorship/metrics" element={<ProtectedRoute><MetricsRecorder /></ProtectedRoute>} />

            {/* Tax routes */}
            <Route path="/tax" element={<ProtectedRoute><TaxDashboard /></ProtectedRoute>} />
            <Route path="/tax/1099" element={<ProtectedRoute><Form1099Management /></ProtectedRoute>} />
            <Route path="/tax/reports" element={<ProtectedRoute><TaxReports /></ProtectedRoute>} />
            <Route path="/tax/business" element={<ProtectedRoute><BusinessTaxInfo /></ProtectedRoute>} />
            <Route path="/tax/licenses" element={<ProtectedRoute><BusinessLicenseManagement /></ProtectedRoute>} />
            <Route path="/tax/compliance" element={<ProtectedRoute><ComplianceDashboard /></ProtectedRoute>} />

            {/* Industry routes */}
            <Route path="/industry" element={<ProtectedRoute><IndustryDashboard /></ProtectedRoute>} />
            <Route path="/industry/partners" element={<ProtectedRoute><IndustryPartners /></ProtectedRoute>} />
            <Route path="/industry/distribution" element={<ProtectedRoute><GlobalDistribution /></ProtectedRoute>} />
            <Route path="/industry/coverage" element={<ProtectedRoute><IndustryCoverage /></ProtectedRoute>} />
            <Route path="/industry/ipi" element={<ProtectedRoute><IPIManagement /></ProtectedRoute>} />
            <Route path="/industry/identifiers" element={<ProtectedRoute><IndustryIdentifiersManagement /></ProtectedRoute>} />
            <Route path="/industry/entertainment" element={<ProtectedRoute><EnhancedEntertainmentDashboard /></ProtectedRoute>} />
            <Route path="/industry/photography" element={<ProtectedRoute><PhotographyServices /></ProtectedRoute>} />
            <Route path="/industry/video" element={<ProtectedRoute><VideoProductionServices /></ProtectedRoute>} />
            <Route path="/industry/monetization" element={<ProtectedRoute><MonetizationOpportunities /></ProtectedRoute>} />
            <Route path="/industry/mdx" element={<ProtectedRoute><MusicDataExchange /></ProtectedRoute>} />
            <Route path="/industry/mlc" element={<ProtectedRoute><MechanicalLicensingCollective /></ProtectedRoute>} />

            {/* Label routes */}
            <Route path="/label/dashboard" element={<ProtectedRoute><LabelDashboard /></ProtectedRoute>} />
            <Route path="/label/projects" element={<ProtectedRoute><ProjectManagement /></ProtectedRoute>} />
            <Route path="/label/marketing" element={<ProtectedRoute><MarketingManagement /></ProtectedRoute>} />
            <Route path="/label/financial" element={<ProtectedRoute><FinancialManagement /></ProtectedRoute>} />
            <Route path="/label/royalties" element={<ProtectedRoute><RoyaltySplitManager /></ProtectedRoute>} />

            {/* Payment routes */}
            <Route path="/payment/packages" element={<ProtectedRoute><PaymentPackages /></ProtectedRoute>} />
            <Route path="/payment/checkout/:packageId" element={<ProtectedRoute><EnhancedPaymentCheckout /></ProtectedRoute>} />
            <Route path="/payment/status" element={<ProtectedRoute><PaymentStatus /></ProtectedRoute>} />
            <Route path="/payment/success" element={<ProtectedRoute><div className="p-8"><h1 className="text-2xl font-bold text-green-600">Payment Successful!</h1></div></ProtectedRoute>} />
            <Route path="/payment/cancel" element={<ProtectedRoute><div className="p-8"><h1 className="text-2xl font-bold text-red-600">Payment Cancelled</h1></div></ProtectedRoute>} />
            <Route path="/payment/bank" element={<ProtectedRoute><BankAccountManager /></ProtectedRoute>} />
            <Route path="/payment/wallet" element={<ProtectedRoute><DigitalWalletManager /></ProtectedRoute>} />

            {/* Licensing routes */}
            <Route path="/licensing" element={<ProtectedRoute><LicensingDashboard /></ProtectedRoute>} />
            <Route path="/licensing/platforms" element={<ProtectedRoute><PlatformLicenseManager /></ProtectedRoute>} />
            <Route path="/licensing/status" element={<ProtectedRoute><LicensingStatus /></ProtectedRoute>} />

            {/* GS1 routes */}
            <Route path="/gs1" element={<ProtectedRoute><GS1Dashboard /></ProtectedRoute>} />

            {/* Admin routes */}
            <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
            <Route path="/admin/content" element={<AdminRoute><AdminContent /></AdminRoute>} />
            <Route path="/admin/analytics" element={<AdminRoute><AdminAnalytics /></AdminRoute>} />
            <Route path="/admin/notifications" element={<AdminRoute><AdminNotifications /></AdminRoute>} />
            <Route path="/admin/ddex" element={<AdminRoute><DDEXAdminDashboard /></AdminRoute>} />
            <Route path="/admin/sponsorship" element={<AdminRoute><AdminSponsorshipOverview /></AdminRoute>} />
            <Route path="/admin/industry" element={<AdminRoute><IndustryDashboard /></AdminRoute>} />
            
            {/* 404 Route - Must be last */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;