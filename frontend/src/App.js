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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Enhanced Payment Checkout Component
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
      // You might want to validate the token here
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      // Add user profile endpoint if needed
      setLoading(false);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      clearAuth();
    }
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
                placeholder="Email address"
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
                  placeholder="Email address"
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
const Library = () => <div className="p-8"><h1 className="text-2xl font-bold">Media Library</h1><p>Your uploaded content will appear here.</p></div>;
const Upload = () => <div className="p-8"><h1 className="text-2xl font-bold">Upload Content</h1><p>Upload your audio, video, and image files here.</p></div>;
const Distribute = () => <div className="p-8"><h1 className="text-2xl font-bold">Distribute Content</h1><p>Distribute your content across platforms.</p></div>;
const Platforms = () => <div className="p-8"><h1 className="text-2xl font-bold">Platforms</h1><p>View all 90+ distribution platforms.</p></div>;
const Pricing = () => <div className="p-8"><h1 className="text-2xl font-bold">Pricing</h1><p>Choose your subscription plan.</p></div>;
const Profile = () => <div className="p-8"><h1 className="text-2xl font-bold">Profile</h1><p>Manage your account settings.</p></div>;

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
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;