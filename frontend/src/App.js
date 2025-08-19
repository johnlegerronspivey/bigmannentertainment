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
class WebAuthnService {
  constructor(apiBaseUrl) {
    this.apiBaseUrl = apiBaseUrl;
  }

  // Check if WebAuthn is supported
  isWebAuthnSupported() {
    return window.PublicKeyCredential !== undefined;
  }

  // Register a new WebAuthn credential
  async registerCredential(accessToken) {
    try {
      // Step 1: Get registration options from backend
      const optionsResponse = await axios.post(`${this.apiBaseUrl}/webauthn/register/begin`, {}, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      const options = optionsResponse.data;

      // Step 2: Convert base64url strings to ArrayBuffers
      const credentialCreationOptions = {
        publicKey: {
          challenge: this.base64urlToBuffer(options.challenge),
          rp: options.rp,
          user: {
            id: this.base64urlToBuffer(options.user.id),
            name: options.user.name,
            displayName: options.user.displayName
          },
          pubKeyCredParams: options.pubKeyCredParams,
          authenticatorSelection: options.authenticatorSelection,
          timeout: options.timeout,
          attestation: options.attestation,
          excludeCredentials: options.excludeCredentials?.map(cred => ({
            id: this.base64urlToBuffer(cred.id),
            type: cred.type
          }))
        }
      };

      // Step 3: Create credential using WebAuthn API
      const credential = await navigator.credentials.create(credentialCreationOptions);

      // Step 4: Send credential to backend for verification
      const registrationResponse = {
        id: credential.id,
        rawId: this.bufferToBase64url(credential.rawId),
        response: {
          clientDataJSON: this.bufferToBase64url(credential.response.clientDataJSON),
          attestationObject: this.bufferToBase64url(credential.response.attestationObject)
        },
        type: credential.type
      };

      const verificationResponse = await axios.post(`${this.apiBaseUrl}/webauthn/register/complete`, registrationResponse, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });

      return verificationResponse.data;

    } catch (error) {
      console.error('WebAuthn registration error:', error);
      throw error;
    }
  }

  // Authenticate using WebAuthn
  async authenticateWithWebAuthn(email) {
    try {
      // Step 1: Get authentication options from backend
      const optionsResponse = await axios.post(`${this.apiBaseUrl}/webauthn/authenticate/begin`, { email });
      const options = optionsResponse.data;

      // Step 2: Convert base64url strings to ArrayBuffers
      const credentialRequestOptions = {
        publicKey: {
          challenge: this.base64urlToBuffer(options.challenge),
          rpId: options.rpId,
          allowCredentials: options.allowCredentials?.map(cred => ({
            id: this.base64urlToBuffer(cred.id),
            type: cred.type,
            transports: cred.transports
          })),
          userVerification: options.userVerification,
          timeout: options.timeout
        }
      };

      // Step 3: Get credential using WebAuthn API
      const assertion = await navigator.credentials.get(credentialRequestOptions);

      // Step 4: Send assertion to backend for verification
      const authenticationResponse = {
        id: assertion.id,
        rawId: this.bufferToBase64url(assertion.rawId),
        response: {
          authenticatorData: this.bufferToBase64url(assertion.response.authenticatorData),
          clientDataJSON: this.bufferToBase64url(assertion.response.clientDataJSON),
          signature: this.bufferToBase64url(assertion.response.signature),
          userHandle: assertion.response.userHandle ? this.bufferToBase64url(assertion.response.userHandle) : null
        },
        type: assertion.type
      };

      const verificationResponse = await axios.post(`${this.apiBaseUrl}/webauthn/authenticate/complete`, {
        email,
        ...authenticationResponse
      });

      return verificationResponse.data;

    } catch (error) {
      console.error('WebAuthn authentication error:', error);
      throw error;
    }
  }

  // Utility methods for base64url encoding/decoding
  base64urlToBuffer(base64url) {
    const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    const padding = base64.length % 4;
    const padded = padding ? base64 + '='.repeat(4 - padding) : base64;
    const binary = atob(padded);
    const buffer = new ArrayBuffer(binary.length);
    const view = new Uint8Array(buffer);
    for (let i = 0; i < binary.length; i++) {
      view[i] = binary.charCodeAt(i);
    }
    return buffer;
  }

  bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  }
}

// Enhanced Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [webAuthnService] = useState(new WebAuthnService(`${API}/auth`));

  useEffect(() => {
    const token = localStorage.getItem('token');
    const refreshToken = localStorage.getItem('refreshToken');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile();
    } else if (refreshToken) {
      refreshAccessToken();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      // Try to refresh token if profile fetch fails
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await refreshAccessToken();
      } else {
        clearAuth();
      }
    } finally {
      setLoading(false);
    }
  };

  const refreshAccessToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await axios.post(`${API}/auth/refresh`, { 
        refresh_token: refreshToken 
      });
      
      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', newRefreshToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchUserProfile();
    } catch (error) {
      clearAuth();
    }
  };

  const clearAuth = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
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

  // WebAuthn Face ID Login
  const loginWithFaceID = async (email) => {
    try {
      if (!webAuthnService.isWebAuthnSupported()) {
        throw new Error('WebAuthn is not supported on this device');
      }

      const authResult = await webAuthnService.authenticateWithWebAuthn(email);
      const { access_token, refresh_token, user: userData } = authResult;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.message || 'Face ID authentication failed' 
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

  // Enroll Face ID after successful login/registration
  const enrollFaceID = async () => {
    try {
      if (!webAuthnService.isWebAuthnSupported()) {
        throw new Error('WebAuthn is not supported on this device');
      }

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('User must be logged in to enroll Face ID');
      }

      const result = await webAuthnService.registerCredential(token);
      return { success: true, data: result };
    } catch (error) {
      return { 
        success: false, 
        error: error.message || 'Face ID enrollment failed' 
      };
    }
  };

  // Get user's WebAuthn credentials
  const getWebAuthnCredentials = async () => {
    try {
      const response = await axios.get(`${API}/auth/webauthn/credentials`);
      return response.data.credentials;
    } catch (error) {
      console.error('Error fetching WebAuthn credentials:', error);
      return [];
    }
  };

  // Delete WebAuthn credential
  const deleteWebAuthnCredential = async (credentialId) => {
    try {
      await axios.delete(`${API}/auth/webauthn/credentials/${credentialId}`);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to delete credential' 
      };
    }
  };

  // Forgot password
  const forgotPassword = async (email) => {
    try {
      const response = await axios.post(`${API}/auth/forgot-password`, { email });
      return { success: true, message: response.data.message };
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

  const isWebAuthnSupported = () => {
    return webAuthnService.isWebAuthnSupported();
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      loginWithFaceID,
      register, 
      enrollFaceID,
      getWebAuthnCredentials,
      deleteWebAuthnCredential,
      forgotPassword,
      resetPassword,
      logout, 
      loading, 
      isAdmin,
      isWebAuthnSupported
    }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const Header = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-gray-900 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3">
            <img 
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%234F46E5'/%3E%3Ctext x='50' y='55' text-anchor='middle' fill='white' font-size='20' font-weight='bold' font-family='Arial'%3EBM%3C/text%3E%3C/svg%3E" 
              alt="Big Mann Entertainment Logo" 
              className="w-12 h-12 object-contain"
            />
            <div>
              <h1 className="text-xl font-bold">Big Mann Entertainment</h1>
              <p className="text-sm text-gray-300">Digital Media Distribution Empire</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center space-x-6">
            <Link to="/library" className="hover:text-purple-400 transition-colors">Library</Link>
            <Link to="/upload" className="hover:text-purple-400 transition-colors">Upload</Link>
            <Link to="/distribute" className="hover:text-purple-400 transition-colors">Distribute</Link>
            <Link to="/platforms" className="hover:text-purple-400 transition-colors">Platforms</Link>
            <Link to="/business" className="hover:text-purple-400 transition-colors">Business</Link>
            <Link to="/earnings" className="hover:text-purple-400 transition-colors">Earnings</Link>
            <Link to="/pricing" className="hover:text-purple-400 transition-colors">Pricing</Link>
            <div className="relative group">
              <button className="hover:text-purple-400 transition-colors flex items-center">
                Label
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div className="absolute top-full left-0 mt-1 w-64 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <Link to="/label" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Label Dashboard</Link>
                <Link to="/label/artists" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Artist Roster</Link>
                <Link to="/label/ar" className="block px-4 py-2 hover:bg-gray-100 transition-colors">A&R Management</Link>
                <Link to="/label/projects" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Recording Projects</Link>
                <Link to="/label/marketing" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Marketing Campaigns</Link>
                <Link to="/label/finance" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Financial Management</Link>
              </div>
            </div>
            <Link to="/sponsorship" className="hover:text-purple-400 transition-colors">Sponsorship</Link>
            <Link to="/blockchain" className="hover:text-purple-400 transition-colors">Blockchain</Link>
            <Link to="/ddex" className="hover:text-purple-400 transition-colors">DDEX Compliance</Link>
            {isAdmin() && (
              <div className="relative group">
                <button className="flex items-center space-x-1 hover:text-purple-400 transition-colors">
                  <span>Admin</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <div className="absolute top-full left-0 mt-2 w-48 bg-white text-gray-900 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <Link to="/admin" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Dashboard</Link>
                  <Link to="/admin/users" className="block px-4 py-2 hover:bg-gray-100 transition-colors">User Management</Link>
                  <Link to="/admin/content" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Content Moderation</Link>
                  <Link to="/admin/sponsorship" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Sponsorship</Link>
                  <Link to="/admin/tax" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Tax Management</Link>
                  <Link to="/admin/payments" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Payment System</Link>
                  <Link to="/admin/earnings" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Earnings & Royalties</Link>
                  <Link to="/admin/analytics" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Analytics</Link>
                  <Link to="/admin/revenue" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Revenue</Link>
                  <Link to="/admin/blockchain" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Blockchain</Link>
                  <Link to="/admin/ddex" className="block px-4 py-2 hover:bg-gray-100 transition-colors">DDEX Compliance</Link>
                  <Link to="/admin/industry" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Industry Integration</Link>
                  <Link to="/admin/industry/entertainment" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Entertainment Dashboard</Link>
                  <Link to="/admin/industry/photography" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Photography Services</Link>
                  <Link to="/admin/industry/video" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Video Production</Link>
                  <Link to="/admin/industry/monetization" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Monetization</Link>
                  <Link to="/admin/industry/mdx" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Music Data Exchange</Link>
                  <Link to="/admin/industry/mlc" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Mechanical Licensing</Link>
                  <Link to="/admin/security" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Security</Link>
                </div>
              </div>
            )}
            <div className="relative group">
              <button className="hover:text-purple-400 transition-colors flex items-center">
                Label Management
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <div className="absolute top-full left-0 mt-1 w-64 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <Link to="/admin/label" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Label Dashboard</Link>
                <Link to="/admin/label/artists" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Artist Management</Link>
                <Link to="/admin/label/ar" className="block px-4 py-2 hover:bg-gray-100 transition-colors">A&R Management</Link>
                <Link to="/admin/label/projects" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Studio & Projects</Link>
                <Link to="/admin/label/marketing" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Marketing & PR</Link>
                <Link to="/admin/label/finance" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Financial Management</Link>
              </div>
            </div>
          </nav>

          {/* Mobile Menu Button */}
          <button 
            className="lg:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
            </svg>
          </button>

          <div className="hidden lg:flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-sm font-medium flex items-center">
                    {user.full_name}
                    {["owner@bigmannentertainment.com"].includes(user.email) && (
                      <span className="ml-2 px-2 py-1 bg-yellow-500 text-yellow-900 text-xs font-bold rounded-full">
                        👑 OWNER
                      </span>
                    )}
                  </div>
                  {isAdmin() && (
                    <div className="text-xs text-purple-300">
                      {["owner@bigmannentertainment.com"].includes(user.email) 
                        ? "Platform Owner & Administrator" 
                        : "Administrator"
                      }
                    </div>
                  )}
                </div>
                <Link
                  to="/profile"
                  className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg transition-colors"
                >
                  Profile
                </Link>
                <button
                  onClick={logout}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="space-x-2">
                <Link
                  to="/login"
                  className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-pink-600 hover:bg-pink-700 px-4 py-2 rounded-lg transition-colors"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden mt-4 py-4 border-t border-gray-700">
            <nav className="flex flex-col space-y-2">
              <Link to="/library" className="hover:text-purple-400 transition-colors py-2">Library</Link>
              <Link to="/upload" className="hover:text-purple-400 transition-colors py-2">Upload</Link>
              <Link to="/distribute" className="hover:text-purple-400 transition-colors py-2">Distribute</Link>
              <Link to="/platforms" className="hover:text-purple-400 transition-colors py-2">Platforms</Link>
              <Link to="/business" className="hover:text-purple-400 transition-colors py-2">Business</Link>
              <Link to="/earnings" className="hover:text-purple-400 transition-colors py-2">Earnings</Link>
              <Link to="/pricing" className="hover:text-purple-400 transition-colors py-2">Pricing</Link>
              
              {/* Label Management Submenu */}
              <div className="py-1 pl-4">
                <span className="text-purple-300 font-medium block mb-1">Label</span>
                <Link to="/label" className="hover:text-purple-400 transition-colors py-1 pl-4 block text-sm">Dashboard</Link>
                <Link to="/label/artists" className="hover:text-purple-400 transition-colors py-1 pl-4 block text-sm">Artists</Link>
                <Link to="/label/ar" className="hover:text-purple-400 transition-colors py-1 pl-4 block text-sm">A&R</Link>
                <Link to="/label/projects" className="hover:text-purple-400 transition-colors py-1 pl-4 block text-sm">Projects</Link>
                <Link to="/label/marketing" className="hover:text-purple-400 transition-colors py-1 pl-4 block text-sm">Marketing</Link>
                <Link to="/label/finance" className="hover:text-purple-400 transition-colors py-1 pl-4 block text-sm">Finance</Link>
              </div>
              
              <Link to="/industry" className="hover:text-purple-400 transition-colors py-2">Industry</Link>
              <Link to="/sponsorship" className="hover:text-purple-400 transition-colors py-2">Sponsorship</Link>
              <Link to="/blockchain" className="hover:text-purple-400 transition-colors py-2">Blockchain</Link>
              <Link to="/ddex" className="hover:text-purple-400 transition-colors py-2">DDEX Compliance</Link>
              {isAdmin() && (
                <>
                  <div className="border-t border-gray-700 pt-2 mt-2">
                    <div className="text-purple-300 font-medium mb-2">Admin</div>
                    <Link to="/admin" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Dashboard</Link>
                    <Link to="/admin/users" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Users</Link>
                    <Link to="/admin/content" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Content</Link>
                    <Link to="/admin/sponsorship" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Sponsorship</Link>
                    <Link to="/admin/tax" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Tax</Link>
                    <Link to="/admin/analytics" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Analytics</Link>
                    <Link to="/admin/revenue" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Revenue</Link>
                    <Link to="/admin/blockchain" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Blockchain</Link>
                    <Link to="/admin/ddex" className="hover:text-purple-400 transition-colors py-1 pl-4 block">DDEX</Link>
                    <Link to="/admin/industry" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Industry</Link>
                    <Link to="/admin/security" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Security</Link>
                  </div>
                </>
              )}
              {user && (
                <div className="border-t border-gray-700 pt-2 mt-2">
                  <div className="text-sm font-medium mb-2">{user.full_name}</div>
                  <Link to="/profile" className="hover:text-purple-400 transition-colors py-2 block">Profile Settings</Link>
                  <button
                    onClick={logout}
                    className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition-colors w-full text-left mt-2"
                  >
                    Logout
                  </button>
                </div>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

const Home = () => {
  const [featuredMedia, setFeaturedMedia] = useState([]);
  const [stats, setStats] = useState({});
  const { isAdmin } = useAuth();

  useEffect(() => {
    fetchFeaturedMedia();
    fetchStats();
  }, []);

  const fetchFeaturedMedia = async () => {
    try {
      const response = await axios.get(`${API}/media/library?is_published=true&limit=6`);
      setFeaturedMedia(response.data.media);
    } catch (error) {
      console.error('Error fetching featured media:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/analytics`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      // Fallback stats
      setStats({
        users: { total: 0 },
        media: { total: 0 },
        distributions: { total: 0 },
        revenue: { total: 0 },
        platforms: { supported: 68 }
      });
    }
  };

  const platformPreviews = [
    "Instagram", "Twitter", "Facebook", "TikTok", "YouTube", "Spotify", 
    "Apple Music", "SoundCloud", "Ethereum", "OpenSea", "Audius", "iHeartRadio"
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-purple-900 via-blue-900 to-pink-900 text-white py-20">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1483478550801-ceba5fe50e8e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwxfHxkaWdpdGFsJTIwY29udGVudHxlbnwwfHx8fDE3NTUxNTQ0NDl8MA&ixlib=rb-4.1.0&q=85')`
          }}
        ></div>
        <div className="relative container mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <img 
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%234F46E5'/%3E%3Ctext x='50' y='55' text-anchor='middle' fill='white' font-size='16' font-weight='bold' font-family='Arial'%3EBM%3C/text%3E%3C/svg%3E" 
              alt="Big Mann Entertainment Logo" 
              className="w-24 h-24 object-contain"
            />
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6">Big Mann Entertainment</h1>
          <p className="text-xl md:text-2xl mb-4">Complete Media Distribution Empire</p>
          <p className="text-lg mb-8">John LeGerron Spivey - Empowering creators worldwide</p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
            <Link 
              to="/upload" 
              className="bg-purple-600 hover:bg-purple-700 px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Start Creating
            </Link>
            <Link 
              to="/platforms" 
              className="bg-transparent border-2 border-white hover:bg-white hover:text-purple-900 px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              View Platforms
            </Link>
          </div>

          {/* Enhanced Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 md:gap-8">
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <div className="text-2xl md:text-3xl font-bold">{stats.media?.total || 0}</div>
              <div className="text-sm">Total Media</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <div className="text-2xl md:text-3xl font-bold">{stats.media?.published || 0}</div>
              <div className="text-sm">Published</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <div className="text-2xl md:text-3xl font-bold">{stats.users?.total || 0}</div>
              <div className="text-sm">Users</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <div className="text-2xl md:text-3xl font-bold">${stats.revenue?.total || 0}</div>
              <div className="text-sm">Revenue</div>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <div className="text-2xl md:text-3xl font-bold">{stats.platforms?.supported || 68}</div>
              <div className="text-sm">Platforms</div>
            </div>
          </div>
        </div>
      </section>

      {/* Multi-Platform Distribution Showcase */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-gray-900">
              Complete Distribution Empire
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Distribute your content across 68+ platforms including social media, streaming, radio, TV, podcasts, NFT marketplaces, and Web3 platforms
            </p>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
            {platformPreviews.map((platform, index) => (
              <div key={index} className="bg-gray-100 rounded-lg p-4 text-center hover:shadow-md transition-shadow">
                <div className="font-semibold text-gray-800 mb-2">{platform}</div>
                {(platform.includes('Social') || ['Instagram', 'Twitter', 'Facebook', 'TikTok', 'YouTube'].includes(platform)) && (
                  <p className="text-xs text-blue-600 mt-1">Social Media</p>
                )}
                {(['Spotify', 'Apple Music', 'SoundCloud', 'Amazon Music'].includes(platform)) && (
                  <p className="text-xs text-green-600 mt-1">Streaming</p>
                )}
                {(platform.includes('Radio') || ['iHeartRadio', 'Pandora', 'SiriusXM'].includes(platform)) && (
                  <p className="text-xs text-yellow-600 mt-1">Radio</p>
                )}
                {(platform.includes('Performance') || ['SoundExchange', 'ASCAP', 'BMI', 'SESAC'].includes(platform)) && (
                  <p className="text-xs text-orange-600 mt-1">Performance Rights</p>
                )}
                {(platform.includes('FM') || ['Clear Channel', 'Cumulus Country', 'Audacy Rock', 'Urban One Hip-Hop', 'NPR Classical', 'Regional Indie', 'Salem Christian', 'Townsquare AC'].includes(platform)) && (
                  <p className="text-xs text-amber-600 mt-1">FM Radio</p>
                )}
                {(['Ethereum', 'Polygon', 'OpenSea', 'Rarible', 'Foundation', 'Magic Eden'].includes(platform)) && (
                  <p className="text-xs text-cyan-600 mt-1">NFT/Web3</p>
                )}
                {(['Audius', 'Catalog'].includes(platform)) && (
                  <p className="text-xs text-teal-600 mt-1">Web3 Music</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Content */}
      {featuredMedia.length > 0 && (
        <section className="py-16 bg-gray-100">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">Featured Content</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {featuredMedia.map((media) => (
                <div key={media.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        media.content_type === 'audio' ? 'bg-purple-100 text-purple-600' :
                        media.content_type === 'video' ? 'bg-red-100 text-red-600' :
                        'bg-green-100 text-green-600'
                      }`}>
                        {media.content_type.toUpperCase()}
                      </span>
                      <span className="text-lg font-bold text-gray-800">
                        ${media.price > 0 ? media.price.toFixed(2) : 'FREE'}
                      </span>
                    </div>
                    
                    <h3 className="text-xl font-semibold mb-2">{media.title}</h3>
                    <p className="text-gray-600 mb-4 line-clamp-3">{media.description}</p>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>{media.download_count} downloads</span>
                      <span>{media.view_count} views</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

// Admin Dashboard Component
const AdminDashboard = () => {
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin()) {
      fetchAnalytics();
    }
  }, [isAdmin]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/admin/analytics/overview`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin()) {
    return <Navigate to="/" />;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Administrator Dashboard</h1>
        
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-2xl font-bold text-purple-600">
                {analytics.user_analytics?.total_users || 0}
              </div>
              <div className="p-2 bg-purple-100 rounded-full">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
            </div>
            <p className="text-gray-600">Total Users</p>
            <p className="text-sm text-green-600 mt-2">
              +{analytics.user_analytics?.new_users_this_month || 0} this month
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-2xl font-bold text-blue-600">
                {analytics.content_analytics?.total_media || 0}
              </div>
              <div className="p-2 bg-blue-100 rounded-full">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
            </div>
            <p className="text-gray-600">Total Content</p>
            <p className="text-sm text-orange-600 mt-2">
              {analytics.content_analytics?.pending_approval || 0} pending approval
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-2xl font-bold text-green-600">
                {analytics.distribution_analytics?.success_rate?.toFixed(1) || 0}%
              </div>
              <div className="p-2 bg-green-100 rounded-full">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p className="text-gray-600">Distribution Success</p>
            <p className="text-sm text-gray-500 mt-2">
              {analytics.distribution_analytics?.total_distributions || 0} total distributions
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-2xl font-bold text-pink-600">
                ${analytics.revenue_analytics?.total_revenue?.toFixed(2) || 0}
              </div>
              <div className="p-2 bg-pink-100 rounded-full">
                <svg className="w-6 h-6 text-pink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
            <p className="text-gray-600">Total Revenue</p>
            <p className="text-sm text-green-600 mt-2">
              ${analytics.revenue_analytics?.total_commission?.toFixed(2) || 0} commission
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Link to="/admin/users" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-purple-100 rounded-full">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">User Management</h3>
                <p className="text-gray-600 text-sm">Manage user accounts and permissions</p>
              </div>
            </div>
          </Link>

          <Link to="/admin/content" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">Content Moderation</h3>
                <p className="text-gray-600 text-sm">Review and moderate uploaded content</p>
              </div>
            </div>
          </Link>

          <Link to="/admin/label" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-red-100 rounded-full">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">Label Management</h3>
                <p className="text-gray-600 text-sm">Manage artists, A&R, and label operations</p>
              </div>
            </div>
          </Link>

          <Link to="/admin/payments" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">Payment System</h3>
                <p className="text-gray-600 text-sm">Manage payments, subscriptions, and transactions</p>
              </div>
            </div>
          </Link>

          <Link to="/admin/earnings" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-green-100 rounded-full">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">Earnings & Royalties</h3>
                <p className="text-gray-600 text-sm">Track earnings, royalty splits, and payouts</p>
              </div>
            </div>
          </Link>

          <Link to="/admin/analytics" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-green-100 rounded-full">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">Advanced Analytics</h3>
                <p className="text-gray-600 text-sm">View detailed platform analytics</p>
              </div>
            </div>
          </Link>
        </div>

        {/* Recent Activities */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent System Activity</h2>
          <div className="space-y-4">
            {analytics.recent_activities?.slice(0, 10).map((activity, index) => (
              <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{activity.action.replace('_', ' ').toUpperCase()}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(activity.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="text-sm text-gray-600">
                  {activity.resource_type}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Admin User Management Component
const AdminUserManagement = () => {
  const [users, setUsers] = useState([]);
  const [ownershipStatus, setOwnershipStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const { isAdmin, user } = useAuth();

  useEffect(() => {
    if (isAdmin()) {
      fetchUsers();
      fetchOwnershipStatus();
    }
  }, [isAdmin, searchTerm, roleFilter, statusFilter]);

  const fetchUsers = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (roleFilter) params.append('role', roleFilter);
      if (statusFilter) params.append('account_status', statusFilter);
      
      const response = await axios.get(`${API}/admin/users?${params}`);
      setUsers(response.data.users);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOwnershipStatus = async () => {
    try {
      const response = await axios.get(`${API}/admin/ownership/status`);
      setOwnershipStatus(response.data);
    } catch (error) {
      console.error('Error fetching ownership status:', error);
    }
  };

  const handleMakeSuperAdmin = async (userId) => {
    if (window.confirm('Are you sure you want to grant this user super admin access with full ownership rights?')) {
      try {
        await axios.post(`${API}/admin/users/make-super-admin/${userId}`);
        fetchUsers();
        fetchOwnershipStatus();
        alert('User has been granted super admin access with full ownership rights');
      } catch (error) {
        console.error('Error making user super admin:', error);
        alert('Error granting super admin access. ' + (error.response?.data?.detail || 'Please try again.'));
      }
    }
  };

  const handleRevokeAdmin = async (userId) => {
    if (window.confirm('Are you sure you want to revoke admin access from this user?')) {
      try {
        await axios.post(`${API}/admin/users/revoke-admin/${userId}`);
        fetchUsers();
        fetchOwnershipStatus();
        alert('Admin access has been revoked');
      } catch (error) {
        console.error('Error revoking admin access:', error);
        alert('Error revoking admin access. ' + (error.response?.data?.detail || 'Please try again.'));
      }
    }
  };

  const handleUserUpdate = async (userId, updateData) => {
    try {
      await axios.put(`${API}/admin/users/${userId}`, updateData);
      fetchUsers();
      setShowUserModal(false);
      setSelectedUser(null);
    } catch (error) {
      console.error('Error updating user:', error);
      alert('Error updating user. Please try again.');
    }
  };

  const handleUserDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await axios.delete(`${API}/admin/users/${userId}`);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Error deleting user. Please try again.');
      }
    }
  };

  if (!isAdmin()) {
    return <Navigate to="/" />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">User Management & Platform Ownership</h1>
        
        {/* Platform Ownership Status */}
        {ownershipStatus && (
          <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">🏢 Platform Ownership Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p><strong>Platform Owner:</strong> {ownershipStatus.platform_owner}</p>
                <p><strong>Business Entity:</strong> {ownershipStatus.business_entity}</p>
                <p><strong>Your Role:</strong> {ownershipStatus.current_user_role}</p>
              </div>
              <div>
                <p><strong>Total Admin Users:</strong> {ownershipStatus.total_admin_users}</p>
                <p><strong>You are Owner:</strong> {ownershipStatus.current_user_is_john ? "✅ YES" : "❌ NO"}</p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-purple-700 bg-opacity-50 rounded">
              <p className="text-sm">{ownershipStatus.ownership_note}</p>
            </div>
          </div>
        )}
        
        {/* Owner Controls - Only visible to John LeGerron Spivey */}
        {ownershipStatus?.current_user_is_john && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
            <h3 className="text-lg font-bold text-yellow-800 mb-2">👑 Owner Controls</h3>
            <p className="text-yellow-700 text-sm">
              You have complete ownership and control of the Big Mann Entertainment platform. 
              You can grant or revoke admin access to any user below.
            </p>
          </div>
        )}
        
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All Roles</option>
              <option value="user">User</option>
              <option value="admin">Admin</option>
              <option value="moderator">Moderator</option>
              <option value="super_admin">Super Admin</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
              <option value="banned">Banned</option>
            </select>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                          <span className="text-purple-600 font-medium">
                            {user.full_name?.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 flex items-center">
                            {user.full_name}
                            {ownershipStatus?.john_emails?.includes(user.email) && (
                              <span className="ml-2 px-2 py-1 bg-yellow-200 text-yellow-800 text-xs font-semibold rounded-full">
                                👑 OWNER
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        user.role === 'admin' || user.role === 'super_admin' ? 'bg-purple-100 text-purple-800' :
                        user.role === 'moderator' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        user.account_status === 'active' ? 'bg-green-100 text-green-800' :
                        user.account_status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                        user.account_status === 'suspended' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {user.account_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex flex-col space-y-1">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setSelectedUser(user);
                              setShowUserModal(true);
                            }}
                            className="text-purple-600 hover:text-purple-900 text-xs"
                          >
                            Edit
                          </button>
                          {!ownershipStatus?.john_emails?.includes(user.email) && (
                            <button
                              onClick={() => handleUserDelete(user.id)}
                              className="text-red-600 hover:text-red-900 text-xs"
                            >
                              Delete
                            </button>
                          )}
                        </div>
                        
                        {/* Owner Controls - Only visible to John LeGerron Spivey */}
                        {ownershipStatus?.current_user_is_john && !ownershipStatus?.john_emails?.includes(user.email) && (
                          <div className="flex flex-col space-y-1 pt-1 border-t border-gray-200">
                            {user.role !== 'super_admin' && (
                              <button
                                onClick={() => handleMakeSuperAdmin(user.id)}
                                className="text-yellow-600 hover:text-yellow-800 text-xs font-medium"
                                title="Grant full admin access with ownership rights"
                              >
                                👑 Make Super Admin
                              </button>
                            )}
                            {(user.is_admin || ['admin', 'super_admin', 'moderator'].includes(user.role)) && (
                              <button
                                onClick={() => handleRevokeAdmin(user.id)}
                                className="text-orange-600 hover:text-orange-800 text-xs font-medium"
                                title="Remove admin access"
                              >
                                🔒 Revoke Admin
                              </button>
                            )}
                          </div>
                        )}
                        
                        {/* Owner Badge */}
                        {ownershipStatus?.john_emails?.includes(user.email) && (
                          <div className="text-xs text-yellow-600 font-medium">
                            🏢 Platform Owner - Cannot be modified
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* User Edit Modal */}
        {showUserModal && selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">Edit User: {selectedUser.full_name}</h3>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  handleUserUpdate(selectedUser.id, {
                    role: formData.get('role'),
                    account_status: formData.get('account_status'),
                    is_active: formData.get('account_status') === 'active'
                  });
                }}
              >
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                  <select
                    name="role"
                    defaultValue={selectedUser.role}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                    <option value="moderator">Moderator</option>
                    <option value="super_admin">Super Admin</option>
                  </select>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <select
                    name="account_status"
                    defaultValue={selectedUser.account_status}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="suspended">Suspended</option>
                    <option value="banned">Banned</option>
                  </select>
                </div>
                <div className="flex justify-end space-x-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowUserModal(false);
                      setSelectedUser(null);
                    }}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-100"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                  >
                    Update User
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Admin Content Management Component
const AdminContentManagement = () => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ approval_status: '', content_type: '' });
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin()) {
      fetchContent();
    }
  }, [isAdmin, filter]);

  const fetchContent = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.approval_status) params.append('approval_status', filter.approval_status);
      if (filter.content_type) params.append('content_type', filter.content_type);
      
      const response = await axios.get(`${API}/admin/content?${params}`);
      setContent(response.data.content);
    } catch (error) {
      console.error('Error fetching content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleModeration = async (mediaId, action, notes = '') => {
    try {
      await axios.post(`${API}/admin/content/${mediaId}/moderate`, {
        media_id: mediaId,
        action: action,
        notes: notes
      });
      fetchContent(); // Refresh the list
    } catch (error) {
      console.error('Error moderating content:', error);
      alert('Error moderating content. Please try again.');
    }
  };

  if (!isAdmin()) {
    return <Navigate to="/" />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Content Management</h1>
        
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <select
              value={filter.approval_status}
              onChange={(e) => setFilter({ ...filter, approval_status: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All Approval Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
            <select
              value={filter.content_type}
              onChange={(e) => setFilter({ ...filter, content_type: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">All Content Types</option>
              <option value="audio">Audio</option>
              <option value="video">Video</option>
              <option value="image">Image</option>
            </select>
          </div>
        </div>

        {/* Content List */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {content.map((item) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-gray-600 mb-2">{item.description}</p>
                <div className="flex justify-between items-center mb-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    item.content_type === 'audio' ? 'bg-purple-100 text-purple-600' :
                    item.content_type === 'video' ? 'bg-red-100 text-red-600' :
                    'bg-green-100 text-green-600'
                  }`}>
                    {item.content_type.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    item.approval_status === 'approved' ? 'bg-green-100 text-green-600' :
                    item.approval_status === 'rejected' ? 'bg-red-100 text-red-600' :
                    'bg-yellow-100 text-yellow-600'
                  }`}>
                    {item.approval_status.toUpperCase()}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleModeration(item.id, 'approve')}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleModeration(item.id, 'reject')}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleModeration(item.id, 'feature')}
                    className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm"
                  >
                    Feature
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Admin Analytics Component
const AdminAnalytics = () => {
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin()) {
      fetchAnalytics();
    }
  }, [isAdmin]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/admin/analytics/overview`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin()) {
    return <Navigate to="/" />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Advanced Analytics</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* User Analytics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">User Analytics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Total Users:</span>
                <span className="font-semibold">{analytics.user_analytics?.total_users || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Active Users:</span>
                <span className="font-semibold">{analytics.user_analytics?.active_users || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>New This Month:</span>
                <span className="font-semibold">{analytics.user_analytics?.new_users_this_month || 0}</span>
              </div>
            </div>
          </div>

          {/* Content Analytics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Content Analytics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Total Media:</span>
                <span className="font-semibold">{analytics.content_analytics?.total_media || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Published:</span>
                <span className="font-semibold">{analytics.content_analytics?.published_media || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Pending:</span>
                <span className="font-semibold">{analytics.content_analytics?.pending_approval || 0}</span>
              </div>
            </div>
          </div>

          {/* Distribution Analytics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Distribution Analytics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Total:</span>
                <span className="font-semibold">{analytics.distribution_analytics?.total_distributions || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Successful:</span>
                <span className="font-semibold">{analytics.distribution_analytics?.successful_distributions || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Success Rate:</span>
                <span className="font-semibold">{analytics.distribution_analytics?.success_rate?.toFixed(1) || 0}%</span>
              </div>
            </div>
          </div>

          {/* Revenue Analytics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Revenue Analytics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Total Revenue:</span>
                <span className="font-semibold">${analytics.revenue_analytics?.total_revenue?.toFixed(2) || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Commission:</span>
                <span className="font-semibold">${analytics.revenue_analytics?.total_commission?.toFixed(2) || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Transactions:</span>
                <span className="font-semibold">{analytics.revenue_analytics?.total_purchases || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Admin Revenue Management Component
const AdminRevenue = () => {
  const [revenueData, setRevenueData] = useState({});
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin()) {
      fetchRevenueData();
    }
  }, [isAdmin]);

  const fetchRevenueData = async () => {
    try {
      const response = await axios.get(`${API}/admin/revenue`);
      setRevenueData(response.data);
    } catch (error) {
      console.error('Error fetching revenue data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin()) {
    return <Navigate to="/" />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Revenue Management</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Revenue Overview</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span>Total Revenue:</span>
                <span className="font-bold text-green-600">${revenueData.total_revenue || 0}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span>Total Commission:</span>
                <span className="font-bold text-blue-600">${revenueData.total_commission || 0}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span>Total Transactions:</span>
                <span className="font-bold text-purple-600">{revenueData.total_transactions || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Top Earning Content</h2>
            <div className="space-y-3">
              {revenueData.top_earning_content?.slice(0, 5).map((item, index) => (
                <div key={index} className="flex justify-between items-center p-2 border-b">
                  <div>
                    <div className="font-medium">{item.media_title || 'Unknown'}</div>
                    <div className="text-sm text-gray-500">{item.media_type}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold">${item.total_revenue}</div>
                    <div className="text-sm text-gray-500">{item.purchase_count} sales</div>
                  </div>
                </div>
              )) || (
                <p className="text-gray-500">No revenue data available</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Admin Security Component
const AdminSecurity = () => {
  const [securityLogs, setSecurityLogs] = useState([]);
  const [securityStats, setSecurityStats] = useState({});
  const [loading, setLoading] = useState(true);
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin()) {
      fetchSecurityData();
    }
  }, [isAdmin]);

  const fetchSecurityData = async () => {
    try {
      const [logsRes, statsRes] = await Promise.all([
        axios.get(`${API}/admin/security/logs?limit=20`),
        axios.get(`${API}/admin/security/stats`)
      ]);
      setSecurityLogs(logsRes.data.logs);
      setSecurityStats(statsRes.data);
    } catch (error) {
      console.error('Error fetching security data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin()) {
    return <Navigate to="/" />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Security & Audit</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Login Statistics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Successful Logins:</span>
                <span className="font-semibold text-green-600">{securityStats.login_statistics?.successful_logins || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Failed Logins:</span>
                <span className="font-semibold text-red-600">{securityStats.login_statistics?.failed_logins || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Success Rate:</span>
                <span className="font-semibold">{securityStats.login_statistics?.success_rate?.toFixed(1) || 0}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Admin Actions</h3>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{securityStats.admin_actions || 0}</div>
              <div className="text-sm text-gray-600">in last 7 days</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Total Activities</h3>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{securityStats.total_activities || 0}</div>
              <div className="text-sm text-gray-600">in last 7 days</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Security Logs</h2>
          <div className="space-y-3">
            {securityLogs.map((log, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex items-center space-x-4">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div>
                    <div className="font-medium">{log.action}</div>
                    <div className="text-sm text-gray-500">
                      {log.user?.full_name || 'Unknown User'} • {new Date(log.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  {log.resource_type}
                </div>
              </div>
            )) || (
              <p className="text-gray-500">No security logs available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const DDEXCompliance = () => {
  const [activeTab, setActiveTab] = useState('ern');
  const [refreshMessageList, setRefreshMessageList] = useState(0);
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" />;
  }

  const handleSuccess = () => {
    setRefreshMessageList(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">DDEX Compliance</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Generate industry-standard DDEX XML messages for digital music distribution, 
            works registration, and metadata exchange with streaming platforms, radio stations, 
            and Performance Rights Organizations.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-lg p-1 flex">
            <button
              onClick={() => setActiveTab('ern')}
              className={`px-6 py-3 rounded-md transition-colors font-medium ${
                activeTab === 'ern' 
                  ? 'bg-purple-600 text-white' 
                  : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              Create ERN
            </button>
            <button
              onClick={() => setActiveTab('cwr')}
              className={`px-6 py-3 rounded-md transition-colors font-medium ${
                activeTab === 'cwr' 
                  ? 'bg-orange-600 text-white' 
                  : 'text-gray-600 hover:text-orange-600'
              }`}
            >
              Register Work
            </button>
            <button
              onClick={() => setActiveTab('identifiers')}
              className={`px-6 py-3 rounded-md transition-colors font-medium ${
                activeTab === 'identifiers' 
                  ? 'bg-green-600 text-white' 
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              Generate IDs
            </button>
            <button
              onClick={() => setActiveTab('messages')}
              className={`px-6 py-3 rounded-md transition-colors font-medium ${
                activeTab === 'messages' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              My Messages
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="max-w-4xl mx-auto">
          {activeTab === 'ern' && (
            <div>
              <DDEXERNCreator onSuccess={handleSuccess} />
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">What is ERN (Electronic Release Notification)?</h3>
                <p className="text-blue-700 text-sm">
                  ERN is the DDEX standard used to deliver release information and digital assets to 
                  Digital Service Providers (DSPs) like Spotify, Apple Music, Amazon Music, and others. 
                  It contains all the metadata needed for proper distribution and display of your music.
                </p>
              </div>
            </div>
          )}
          
          {activeTab === 'cwr' && (
            <div>
              <DDEXCWRCreator onSuccess={handleSuccess} />
              <div className="mt-6 p-4 bg-orange-50 rounded-lg">
                <h3 className="font-semibold text-orange-800 mb-2">What is CWR (Common Works Registration)?</h3>
                <p className="text-orange-700 text-sm">
                  CWR is the global standard for registering musical works with Performance Rights 
                  Organizations (PROs) like ASCAP, BMI, and SESAC. This ensures you receive proper 
                  royalty payments when your compositions are performed publicly.
                </p>
              </div>
            </div>
          )}
          
          {activeTab === 'identifiers' && (
            <div>
              <DDEXIdentifierGenerator />
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">Industry Standard Identifiers</h3>
                <div className="text-green-700 text-sm space-y-2">
                  <p><strong>ISRC:</strong> Required for all sound recordings, used by streaming platforms and radio for royalty tracking.</p>
                  <p><strong>ISWC:</strong> Required for musical compositions, used by PROs for performance royalty distribution.</p>
                  <p><strong>Catalog Number:</strong> Internal label identifier for organizing and tracking releases.</p>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'messages' && (
            <DDEXMessageList key={refreshMessageList} />
          )}
        </div>

        {/* DDEX Standards Information */}
        <div className="max-w-6xl mx-auto mt-12">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-6 text-center">DDEX Standards Supported</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center p-4 border border-purple-200 rounded-lg">
                <div className="text-purple-600 text-3xl font-bold mb-2">ERN</div>
                <h4 className="font-semibold mb-2">Electronic Release Notification</h4>
                <p className="text-sm text-gray-600">v4.1 - Digital distribution to streaming platforms</p>
              </div>
              
              <div className="text-center p-4 border border-orange-200 rounded-lg">
                <div className="text-orange-600 text-3xl font-bold mb-2">CWR</div>
                <h4 className="font-semibold mb-2">Common Works Registration</h4>
                <p className="text-sm text-gray-600">v3.0 - Musical works registration with PROs</p>
              </div>
              
              <div className="text-center p-4 border border-green-200 rounded-lg">
                <div className="text-green-600 text-3xl font-bold mb-2">DSR</div>
                <h4 className="font-semibold mb-2">Digital Sales Report</h4>
                <p className="text-sm text-gray-600">v4.1 - Sales and usage reporting (coming soon)</p>
              </div>
              
              <div className="text-center p-4 border border-blue-200 rounded-lg">
                <div className="text-blue-600 text-3xl font-bold mb-2">MWN</div>
                <h4 className="font-semibold mb-2">Musical Work Notification</h4>
                <p className="text-sm text-gray-600">v4.1 - Works metadata exchange (coming soon)</p>
              </div>
            </div>
            
            <div className="mt-8 text-center">
              <p className="text-gray-600 mb-4">
                Big Mann Entertainment supports full DDEX compliance for professional music distribution 
                and rights management across all major industry platforms.
              </p>
              <div className="flex justify-center space-x-6 text-sm text-gray-500">
                <span>✓ DDEX Member Standards</span>
                <span>✓ Industry Compliant XML</span>
                <span>✓ Automated Identifier Generation</span>
                <span>✓ Professional Distribution</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPasswordLogin, setShowPasswordLogin] = useState(false);
  const { login, loginWithFaceID, isWebAuthnSupported } = useAuth();
  const navigate = useNavigate();

  const handleFaceIDLogin = async () => {
    if (!formData.email) {
      setError('Please enter your email address first');
      return;
    }

    setLoading(true);
    setError('');

    const result = await loginWithFaceID(formData.email);
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
      // If Face ID fails, show password option
      setShowPasswordLogin(true);
    }
    
    setLoading(false);
  };

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
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='40' fill='%234F46E5'/%3E%3Ctext x='50' y='55' text-anchor='middle' fill='white' font-size='16' font-weight='bold' font-family='Arial'%3EBM%3C/text%3E%3C/svg%3E" 
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

          {/* Email Input (always visible) */}
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

          {/* Face ID Login (Primary Method) */}
          {isWebAuthnSupported() && !showPasswordLogin && (
            <div className="space-y-4">
              <button
                onClick={handleFaceIDLogin}
                disabled={loading || !formData.email}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Authenticating with Face ID...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    🔒 Sign in with Face ID
                  </>
                )}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setShowPasswordLogin(true)}
                  className="text-purple-600 hover:text-purple-500 text-sm"
                >
                  Use password instead
                </button>
              </div>
            </div>
          )}

          {/* Password Login (Fallback or when WebAuthn is not supported) */}
          {(showPasswordLogin || !isWebAuthnSupported()) && (
            <form onSubmit={handlePasswordLogin} className="space-y-4">
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
                  'Sign in with Password'
                )}
              </button>

              {isWebAuthnSupported() && (
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => setShowPasswordLogin(false)}
                    className="text-purple-600 hover:text-purple-500 text-sm"
                  >
                    Use Face ID instead
                  </button>
                </div>
              )}
            </form>
          )}

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
  const [showFaceIDOption, setShowFaceIDOption] = useState(false);
  const { register, enrollFaceID, isWebAuthnSupported } = useAuth();
  const navigate = useNavigate();

  const validateAge = (dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    const age = today.getFullYear() - birthDate.getFullYear() - 
      ((today.getMonth() < birthDate.getMonth() || 
        (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) ? 1 : 0);
    return age >= 13;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate age
    if (!validateAge(formData.date_of_birth)) {
      setError('You must be at least 13 years old to register');
      setLoading(false);
      return;
    }

    const result = await register(formData);
    
    if (result.success) {
      // Show Face ID enrollment option if supported
      if (isWebAuthnSupported()) {
        setShowFaceIDOption(true);
        setStep(2);
      } else {
        navigate('/');
      }
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleFaceIDEnrollment = async () => {
    setLoading(true);
    setError('');

    const result = await enrollFaceID();
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const skipFaceID = () => {
    navigate('/');
  };

  if (step === 2 && showFaceIDOption) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
              alt="Big Mann Entertainment Logo" 
              className="w-16 h-16 object-contain mx-auto mb-4"
            />
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Set Up Face ID
            </h2>
            <p className="text-gray-600">Secure your account with biometric authentication</p>
          </div>
          
          <div className="mt-8 space-y-6">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            <div className="text-center">
              <div className="mb-6">
                <svg className="w-24 h-24 mx-auto text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <p className="text-gray-700 mb-6">
                Enable Face ID for quick and secure access to your Big Mann Entertainment account.
              </p>
            </div>
            
            <button
              onClick={handleFaceIDEnrollment}
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Setting up Face ID...
                </>
              ) : (
                '🔒 Enable Face ID'
              )}
            </button>
            
            <button
              onClick={skipFaceID}
              disabled={loading}
              className="w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-md transition-colors disabled:opacity-50"
            >
              Skip for now
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="text-gray-600">Join Big Mann Entertainment</p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          {/* Personal Information */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <input
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Full Name *"
                />
              </div>
              <div>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Email Address *"
                />
              </div>
              <div>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Password *"
                  minLength="8"
                />
              </div>
              <div>
                <input
                  type="date"
                  required
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Date of Birth *"
                />
              </div>
            </div>
          </div>

          {/* Address Information */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Address Information</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <input
                  type="text"
                  required
                  value={formData.address_line1}
                  onChange={(e) => setFormData({ ...formData, address_line1: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Street Address *"
                />
              </div>
              <div>
                <input
                  type="text"
                  value={formData.address_line2}
                  onChange={(e) => setFormData({ ...formData, address_line2: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Apartment, suite, etc. (Optional)"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <input
                    type="text"
                    required
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="City *"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    required
                    value={formData.state_province}
                    onChange={(e) => setFormData({ ...formData, state_province: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="State/Province *"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    required
                    value={formData.postal_code}
                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="ZIP/Postal Code *"
                  />
                </div>
              </div>
              <div>
                <select
                  required
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="US">United States</option>
                  <option value="CA">Canada</option>
                  <option value="GB">United Kingdom</option>
                  <option value="AU">Australia</option>
                  <option value="DE">Germany</option>
                  <option value="FR">France</option>
                  <option value="JP">Japan</option>
                  <option value="BR">Brazil</option>
                  <option value="IN">India</option>
                  <option value="MX">Mexico</option>
                </select>
              </div>
            </div>
          </div>

          {/* Business Information */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Business Information (Optional)</h3>
            <div>
              <input
                type="text"
                value={formData.business_name}
                onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Business Name (Optional)"
              />
            </div>
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
                Creating account...
              </>
            ) : (
              'Create Account'
            )}
          </button>

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Already have an account? Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

// Forgot Password Component
const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { forgotPassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    const result = await forgotPassword(email);
    
    if (result.success) {
      setMessage(result.message);
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
            src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset your password
          </h2>
          <p className="text-gray-600">Enter your email to receive a reset link</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
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
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending reset link...
              </>
            ) : (
              'Send Reset Link'
            )}
          </button>

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Back to login
            </Link>  
          </div>
        </form>
      </div>
    </div>
  );
};

// Reset Password Component
const ResetPassword = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { resetPassword } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Extract token from URL query parameters
  const urlParams = new URLSearchParams(location.search);
  const token = urlParams.get('token');

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link. Please request a new password reset.');
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    const result = await resetPassword(token, password);
    
    if (result.success) {
      setMessage('Password reset successful! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
              alt="Big Mann Entertainment Logo" 
              className="w-16 h-16 object-contain mx-auto mb-4"
            />
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Invalid Reset Link
            </h2>
            <p className="text-gray-600 mt-4">
              This password reset link is invalid or has expired.
            </p>
            <div className="mt-6">
              <Link 
                to="/forgot-password"
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors"
              >
                Request New Reset Link
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Set new password
          </h2>
          <p className="text-gray-600">Enter your new password</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
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

          <div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="New password"
              minLength="8"
            />
          </div>

          <div>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Confirm new password"
              minLength="8"
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
                Resetting password...
              </>
            ) : (
              'Reset Password'
            )}
          </button>

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Back to login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

// Profile Settings Component for managing Face ID credentials
const ProfileSettings = () => {
  const [credentials, setCredentials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const { user, enrollFaceID, getWebAuthnCredentials, deleteWebAuthnCredential, isWebAuthnSupported } = useAuth();

  useEffect(() => {
    fetchCredentials();
  }, []);

  const fetchCredentials = async () => {
    try {
      const creds = await getWebAuthnCredentials();
      setCredentials(creds);
    } catch (error) {
      console.error('Error fetching credentials:', error);
    }
  };

  const handleEnrollFaceID = async () => {
    setLoading(true);
    setError('');
    setMessage('');

    const result = await enrollFaceID();
    
    if (result.success) {
      setMessage('Face ID enrolled successfully!');
      fetchCredentials();
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleDeleteCredential = async (credentialId) => {
    if (!window.confirm('Are you sure you want to delete this Face ID credential?')) {
      return;
    }

    setLoading(true);
    setError('');

    const result = await deleteWebAuthnCredential(credentialId);
    
    if (result.success) {
      setMessage('Face ID credential deleted successfully');
      fetchCredentials();
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
              Profile Settings
            </h3>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}
            
            {message && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                {message}
              </div>
            )}

            {/* User Information */}
            <div className="mb-8">
              <h4 className="text-md font-medium text-gray-900 mb-4">Account Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <p className="mt-1 text-sm text-gray-900">{user?.full_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Address</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {user?.address_line1}
                    {user?.address_line2 && `, ${user.address_line2}`}
                    <br />
                    {user?.city}, {user?.state_province} {user?.postal_code}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Member Since</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            {/* Face ID Settings */}
            {isWebAuthnSupported() && (
              <div className="mb-8">
                <h4 className="text-md font-medium text-gray-900 mb-4">Face ID Authentication</h4>
                
                {credentials.length === 0 ? (
                  <div className="text-center py-6">
                    <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <p className="text-gray-500 mb-4">No Face ID credentials enrolled</p>
                    <button
                      onClick={handleEnrollFaceID}
                      disabled={loading}
                      className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors disabled:opacity-50"
                    >
                      {loading ? 'Enrolling...' : '🔒 Enroll Face ID'}
                    </button>
                  </div>
                ) : (
                  <div>
                    <div className="space-y-3">
                      {credentials.map((credential) => (
                        <div key={credential.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                          <div>
                            <p className="font-medium text-gray-900">{credential.name}</p>
                            <p className="text-sm text-gray-500">
                              Created: {new Date(credential.created_at).toLocaleDateString()}
                              {credential.last_used && (
                                <span className="mx-2">•</span>
                              )}
                              {credential.last_used && (
                                <>Last used: {new Date(credential.last_used).toLocaleDateString()}</>
                              )}
                            </p>
                          </div>
                          <button
                            onClick={() => handleDeleteCredential(credential.id)}
                            disabled={loading}
                            className="text-red-600 hover:text-red-800 font-medium text-sm disabled:opacity-50"
                          >
                            Delete
                          </button>
                        </div>
                      ))}
                    </div>
                    
                    <div className="mt-4">
                      <button
                        onClick={handleEnrollFaceID}
                        disabled={loading}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors disabled:opacity-50"
                      >
                        {loading ? 'Enrolling...' : '➕ Add Another Face ID'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {!isWebAuthnSupported() && (
              <div className="mb-8">
                <h4 className="text-md font-medium text-gray-900 mb-4">Face ID Authentication</h4>
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-yellow-700">
                        Face ID authentication is not supported on this device or browser. 
                        Please use a device with WebAuthn support to enable Face ID login.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Business Management Dashboard
const BusinessManagement = () => {
  const [activeTab, setActiveTab] = useState('identifiers');

  const tabs = [
    { id: 'identifiers', name: 'Business Identifiers', icon: '🏢' },
    { id: 'upc', name: 'UPC Generator', icon: '📊' },
    { id: 'isrc', name: 'ISRC Generator', icon: '🎵' },
    { id: 'products', name: 'Product Management', icon: '📦' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Business Management</h1>
          <p className="text-gray-600 mt-2">
            Manage your business identifiers, UPC codes, and product catalog
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'identifiers' && <BusinessIdentifiers />}
            {activeTab === 'upc' && <UPCGenerator />}
            {activeTab === 'isrc' && <ISRCGenerator />}
            {activeTab === 'products' && <ProductManagement />}
          </div>
        </div>
      </div>
    </div>
  );
};

const Library = () => {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ content_type: '', category: '' });

  useEffect(() => {
    fetchMedia();
  }, [filter]);

  const fetchMedia = async () => {
    try {
      const params = new URLSearchParams();
      if (filter.content_type) params.append('content_type', filter.content_type);
      if (filter.category) params.append('category', filter.category);
      params.append('is_published', 'true');

      const response = await axios.get(`${API}/media/library?${params}`);
      setMedia(response.data.media);
    } catch (error) {
      console.error('Error fetching media:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (mediaId) => {
    try {
      const response = await axios.post(`${API}/payments/checkout`, { media_id: mediaId });
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('Error processing purchase. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Media Library</h1>
        
        {/* Filters */}
        <div className="mb-8 flex flex-wrap gap-4">
          <select
            value={filter.content_type}
            onChange={(e) => setFilter({ ...filter, content_type: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Types</option>
            <option value="audio">Audio</option>
            <option value="video">Video</option>
            <option value="image">Image</option>
          </select>
          
          <select
            value={filter.category}
            onChange={(e) => setFilter({ ...filter, category: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Categories</option>
            <option value="music">Music</option>
            <option value="podcast">Podcast</option>
            <option value="video">Video</option>
            <option value="photography">Photography</option>
            <option value="art">Art</option>
          </select>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading media...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {media.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      item.content_type === 'audio' ? 'bg-purple-100 text-purple-600' :
                      item.content_type === 'video' ? 'bg-red-100 text-red-600' :
                      'bg-green-100 text-green-600'
                    }`}>
                      {item.content_type.toUpperCase()}
                    </span>
                    <span className="text-lg font-bold text-gray-800">
                      ${item.price > 0 ? item.price.toFixed(2) : 'FREE'}
                    </span>
                  </div>
                  
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-gray-600 mb-4 line-clamp-3">{item.description}</p>
                  
                  <div className="flex flex-wrap gap-1 mb-4">
                    {item.tags.slice(0, 3).map((tag, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>{item.download_count} downloads</span>
                    <span>{item.view_count} views</span>
                  </div>
                  
                  <button
                    onClick={() => handlePurchase(item.id)}
                    className={`w-full py-2 px-4 rounded-md font-semibold transition-colors ${
                      item.price > 0
                        ? 'bg-purple-600 hover:bg-purple-700 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    }`}
                  >
                    {item.price > 0 ? `Purchase $${item.price.toFixed(2)}` : 'Download Free'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {!loading && media.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600">No media found matching your filters.</p>
          </div>
        )}
      </div>
    </div>
  );
};

const Upload = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    price: 0,
    tags: ''
  });
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    return <Navigate to="/login" />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }

    setLoading(true);
    setMessage('');

    const uploadData = new FormData();
    uploadData.append('file', file);
    uploadData.append('title', formData.title);
    uploadData.append('description', formData.description);
    uploadData.append('category', formData.category);
    uploadData.append('price', formData.price.toString());
    uploadData.append('tags', formData.tags);

    try {
      const response = await axios.post(`${API}/media/upload`, uploadData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMessage('Media uploaded successfully! Content will be reviewed before publishing.');
      setFormData({ title: '', description: '', category: '', price: 0, tags: '' });
      setFile(null);
      
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        <h1 className="text-3xl font-bold mb-8">Upload Media</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          {message && (
            <div className={`mb-6 p-4 rounded-md ${
              message.includes('successfully') 
                ? 'bg-green-100 border border-green-400 text-green-700'
                : 'bg-red-100 border border-red-400 text-red-700'
            }`}>
              {message}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Media File *
              </label>
              <input
                type="file"
                accept="audio/*,video/*,image/*"
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 h-32"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              >
                <option value="">Select a category</option>
                <option value="music">Music</option>
                <option value="podcast">Podcast</option>
                <option value="video">Video</option>
                <option value="photography">Photography</option>
                <option value="art">Art</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price ($)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <p className="text-sm text-gray-500 mt-1">Set to 0 for free content</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter tags separated by commas"
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50"
            >
              {loading ? 'Uploading...' : 'Upload Media'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

const Platforms = () => {
  const [platforms, setPlatforms] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      const response = await axios.get(`${API}/distribution/platforms`);
      setPlatforms(response.data.platforms);
    } catch (error) {
      console.error('Error fetching platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  const platformTypeColors = {
    'social_media': 'bg-blue-100 text-blue-800',
    'streaming': 'bg-green-100 text-green-800',
    'radio': 'bg-yellow-100 text-yellow-800',
    'fm_broadcast': 'bg-amber-100 text-amber-800',
    'tv': 'bg-red-100 text-red-800',
    'streaming_tv': 'bg-purple-100 text-purple-800',
    'podcast': 'bg-indigo-100 text-indigo-800',
    'performance_rights': 'bg-orange-100 text-orange-800',
    'blockchain': 'bg-cyan-100 text-cyan-800',
    'nft_marketplace': 'bg-violet-100 text-violet-800',
    'web3_music': 'bg-teal-100 text-teal-800'
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading platforms...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Distribution Platforms</h1>
        <p className="text-gray-600 mb-8">
          Big Mann Entertainment supports distribution to {Object.keys(platforms).length} major platforms across social media, streaming services, radio stations, TV networks, podcast platforms, blockchain networks, NFT marketplaces, and Web3 platforms.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Object.entries(platforms).map(([platformId, platform]) => (
            <div key={platformId} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">{platform.name}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  platformTypeColors[platform.type] || 'bg-gray-100 text-gray-800'
                }`}>
                  {platform.type.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Supported Formats:</p>
                <div className="flex flex-wrap gap-1">
                  {platform.supported_formats.map((format) => (
                    <span key={format} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      {format.toUpperCase()}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="text-sm text-gray-500">
                <p>Max file size: {platform.max_file_size_mb ? platform.max_file_size_mb.toFixed(0) : 'N/A'} MB</p>
              </div>
              
              {platform.description && (
                <div className="mt-3 text-sm text-gray-600">
                  <p>{platform.description}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const Distribute = () => {
  const [userMedia, setUserMedia] = useState([]);
  const [platforms, setPlatforms] = useState({});
  const [selectedMedia, setSelectedMedia] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [customMessage, setCustomMessage] = useState('');
  const [hashtags, setHashtags] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [distributionHistory, setDistributionHistory] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchUserMedia();
      fetchPlatforms();
      fetchDistributionHistory();
    }
  }, [user]);

  const fetchUserMedia = async () => {
    try {
      const response = await axios.get(`${API}/media/library`);
      setUserMedia(response.data.media);
    } catch (error) {
      console.error('Error fetching user media:', error);
    }
  };

  const fetchPlatforms = async () => {
    try {
      const response = await axios.get(`${API}/distribution/platforms`);
      setPlatforms(response.data.platforms);
    } catch (error) {
      console.error('Error fetching platforms:', error);
    }
  };

  const fetchDistributionHistory = async () => {
    try {
      const response = await axios.get(`${API}/distribution/history?limit=10`);
      setDistributionHistory(response.data.distributions);
    } catch (error) {
      console.error('Error fetching distribution history:', error);
    }
  };

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId) 
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const handleDistribute = async (e) => {
    e.preventDefault();
    if (!selectedMedia || selectedPlatforms.length === 0) {
      setMessage('Please select media and at least one platform.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const hashtagArray = hashtags.split(',').map(tag => tag.trim()).filter(tag => tag);
      
      const response = await axios.post(`${API}/distribution/distribute`, {
        media_id: selectedMedia,
        platforms: selectedPlatforms,
        custom_message: customMessage || null,
        hashtags: hashtagArray
      });
      
      setMessage('Content distribution initiated successfully!');
      setSelectedMedia('');
      setSelectedPlatforms([]);
      setCustomMessage('');
      setHashtags('');
      
      // Refresh distribution history
      fetchDistributionHistory();
      
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Distribution failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <Navigate to="/login" />;
  }

  const selectedMediaItem = userMedia.find(media => media.id === selectedMedia);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        <h1 className="text-3xl font-bold mb-8">Content Distribution</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Distribution Form */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6">Distribute Content</h2>
            
            {message && (
              <div className={`mb-6 p-4 rounded-md ${
                message.includes('successfully') 
                  ? 'bg-green-100 border border-green-400 text-green-700'
                  : 'bg-red-100 border border-red-400 text-red-700'
              }`}>
                {message}
              </div>
            )}
            
            <form onSubmit={handleDistribute} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Media *
                </label>
                <select
                  value={selectedMedia}
                  onChange={(e) => setSelectedMedia(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                >
                  <option value="">Choose media to distribute</option>
                  {userMedia.map((media) => (
                    <option key={media.id} value={media.id}>
                      {media.title} ({media.content_type})
                    </option>
                  ))}
                </select>
              </div>
              
              {selectedMediaItem && (
                <div className="bg-gray-50 p-4 rounded-md">
                  <h4 className="font-semibold mb-2">Selected Media Preview</h4>
                  <p className="text-sm text-gray-600">
                    <strong>Title:</strong> {selectedMediaItem.title}<br />
                    <strong>Type:</strong> {selectedMediaItem.content_type}<br />
                    <strong>Category:</strong> {selectedMediaItem.category}
                  </p>
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Platforms * ({Object.keys(platforms).length} available)
                </label>
                <div className="grid grid-cols-1 gap-2 max-h-64 overflow-y-auto border border-gray-300 rounded-md p-3">
                  {Object.entries(platforms).map(([platformId, platform]) => {
                    const isCompatible = selectedMediaItem ? 
                      platform.supported_formats.includes(selectedMediaItem.content_type) : true;
                    
                    return (
                      <label 
                        key={platformId} 
                        className={`flex items-center space-x-2 p-2 rounded cursor-pointer ${
                          isCompatible ? 'hover:bg-gray-100' : 'opacity-50 cursor-not-allowed'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedPlatforms.includes(platformId)}
                          onChange={() => handlePlatformToggle(platformId)}
                          disabled={!isCompatible}
                          className="text-purple-600"
                        />
                        <span className="text-sm flex-1">{platform.name}</span>
                        <span className={`px-1 py-0.5 text-xs rounded ${
                          platform.type === 'social_media' ? 'bg-blue-100 text-blue-600' :
                          platform.type === 'streaming' ? 'bg-green-100 text-green-600' :
                          platform.type === 'blockchain' ? 'bg-cyan-100 text-cyan-600' :
                          platform.type === 'nft_marketplace' ? 'bg-violet-100 text-violet-600' :
                          platform.type === 'web3_music' ? 'bg-teal-100 text-teal-600' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {platform.type.replace('_', ' ')}
                        </span>
                      </label>
                    );
                  })}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {selectedPlatforms.length} platforms selected
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Message (Optional)
                </label>
                <textarea
                  value={customMessage}
                  onChange={(e) => setCustomMessage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 h-24"
                  placeholder="Add a custom message for your content..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hashtags (Optional)
                </label>
                <input
                  type="text"
                  value={hashtags}
                  onChange={(e) => setHashtags(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="music, entertainment, bigmann (comma separated)"
                />
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50"
              >
                {loading ? 'Distributing...' : `Distribute to ${selectedPlatforms.length} Platform${selectedPlatforms.length !== 1 ? 's' : ''}`}
              </button>
            </form>
          </div>
          
          {/* Distribution History */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-6">Distribution History</h2>
            
            {distributionHistory.length === 0 ? (
              <p className="text-gray-600">No distributions yet. Start by distributing your first content!</p>
            ) : (
              <div className="space-y-4">
                {distributionHistory.map((distribution) => (
                  <div key={distribution.id} className="border border-gray-200 rounded-md p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">Distribution #{distribution.id.slice(0, 8)}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        distribution.status === 'completed' ? 'bg-green-100 text-green-800' :
                        distribution.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                        distribution.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {distribution.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      Platforms: {distribution.target_platforms.slice(0, 3).join(', ')}
                      {distribution.target_platforms.length > 3 && ` +${distribution.target_platforms.length - 3} more`}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(distribution.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const Blockchain = () => {
  const [collections, setCollections] = useState([]);
  const [tokens, setTokens] = useState([]);
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchBlockchainData();
    }
  }, [user]);

  const fetchBlockchainData = async () => {
    try {
      const [collectionsRes, tokensRes, walletsRes] = await Promise.all([
        axios.get(`${API}/nft/collections`),
        axios.get(`${API}/nft/tokens`),
        axios.get(`${API}/blockchain/wallets`)
      ]);
      
      setCollections(collectionsRes.data.collections);
      setTokens(tokensRes.data.tokens);
      setWallets(walletsRes.data.wallets);
    } catch (error) {
      console.error('Error fetching blockchain data:', error);
      setMessage('Error loading blockchain data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const connectWallet = async (walletData) => {
    try {
      await axios.post(`${API}/blockchain/wallets`, walletData);
      fetchBlockchainData();
      setMessage('Wallet connected successfully!');
    } catch (error) {
      setMessage('Error connecting wallet. Please try again.');
    }
  };

  if (!user) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Blockchain & Web3</h1>
        
        {message && (
          <div className={`mb-6 p-4 rounded-md ${
            message.includes('successfully') 
              ? 'bg-green-100 border border-green-400 text-green-700'
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}>
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* NFT Collections */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">NFT Collections</h2>
            {collections.length === 0 ? (
              <p className="text-gray-600">No collections created yet.</p>
            ) : (
              <div className="space-y-4">
                {collections.map((collection) => (
                  <div key={collection.id} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold">{collection.name}</h3>
                    <p className="text-sm text-gray-600 mb-2">{collection.description}</p>
                    <div className="flex justify-between text-sm">
                      <span>Supply: {collection.total_supply}</span>
                      <span className="text-purple-600">{collection.blockchain_network}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* NFT Tokens */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Minted NFTs</h2>
            {tokens.length === 0 ? (
              <p className="text-gray-600">No NFTs minted yet.</p>
            ) : (
              <div className="space-y-4">
                {tokens.map((token) => (
                  <div key={token.id} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold">{token.media?.title || 'Untitled'}</h3>
                    <p className="text-sm text-gray-600 mb-2">{token.collection?.name}</p>
                    <div className="flex justify-between text-sm">
                      <span>Price: {token.current_price} ETH</span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        token.is_listed ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {token.is_listed ? 'Listed' : 'Not Listed'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Connected Wallets */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Connected Wallets</h2>
            {wallets.length === 0 ? (
              <div>
                <p className="text-gray-600 mb-4">No wallets connected yet.</p>
                <button
                  onClick={() => {
                    const walletAddress = prompt('Enter your wallet address:');
                    if (walletAddress) {
                      connectWallet({
                        wallet_address: walletAddress,
                        blockchain_network: 'ethereum',
                        wallet_type: 'metamask',
                        is_primary: true
                      });
                    }
                  }}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors"
                >
                  Connect Wallet
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {wallets.map((wallet) => (
                  <div key={wallet.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{wallet.wallet_type}</span>
                      {wallet.is_primary && (
                        <span className="bg-purple-100 text-purple-600 text-xs px-2 py-1 rounded">
                          Primary
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 font-mono">
                      {wallet.wallet_address.slice(0, 6)}...{wallet.wallet_address.slice(-4)}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{wallet.blockchain_network}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Ethereum Configuration */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Platform Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ethereum Contract Address
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value="0xdfe98870c599734335900ce15e26d1d2ccc062c1"
                  readOnly
                  className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600"
                />
                <button
                  onClick={() => {
                    navigator.clipboard.writeText('0xdfe98870c599734335900ce15e26d1d2ccc062c1');
                    setMessage('Contract address copied to clipboard!');
                  }}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                >
                  Copy
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">Official Big Mann Entertainment smart contract</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Platform Wallet
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value="0xdfe98870c599734335900ce15e26d1d2ccc062c1"
                  readOnly
                  className="flex-1 px-3 py-2 bg-gray-100 border border-gray-300 rounded-md text-gray-600"
                />
                <button
                  onClick={() => {
                    navigator.clipboard.writeText('0xdfe98870c599734335900ce15e26d1d2ccc062c1');
                    setMessage('Wallet address copied to clipboard!');
                  }}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                >
                  Copy
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">Primary platform wallet for blockchain operations</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const PurchaseSuccess = () => {
  const [status, setStatus] = useState('checking');
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const sessionId = params.get('session_id');
    
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, [location]);

  const checkPaymentStatus = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      if (response.data.payment_status === 'paid') {
        setStatus('success');
      } else {
        setStatus('pending');
        // Poll again after 2 seconds
        setTimeout(() => checkPaymentStatus(sessionId), 2000);
      }
    } catch (error) {
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        {status === 'checking' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold mb-4">Processing Payment...</h2>
            <p className="text-gray-600">Please wait while we confirm your payment.</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="text-green-600 text-6xl mb-4">✓</div>
            <h2 className="text-2xl font-bold mb-4 text-green-600">Payment Successful!</h2>
            <p className="text-gray-600 mb-6">Your purchase has been completed successfully.</p>
            <Link
              to="/library"
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
            >
              Go to Library
            </Link>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="text-red-600 text-6xl mb-4">✗</div>
            <h2 className="text-2xl font-bold mb-4 text-red-600">Payment Failed</h2>
            <p className="text-gray-600 mb-6">There was an issue processing your payment.</p>
            <Link
              to="/library"
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
            >
              Back to Library
            </Link>
          </>
        )}
      </div>
    </div>
  );
};

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/login" />;
};

const AdminRoute = ({ children }) => {
  const { user, loading, isAdmin } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }
  
  return user && isAdmin() ? children : <Navigate to="/" />;
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/profile" element={<ProtectedRoute><ProfileSettings /></ProtectedRoute>} />
            <Route path="/business" element={<ProtectedRoute><BusinessManagement /></ProtectedRoute>} />
            <Route path="/industry" element={<ProtectedRoute><IndustryDashboard /></ProtectedRoute>} />
            <Route path="/industry/partners" element={<ProtectedRoute><IndustryPartners /></ProtectedRoute>} />
            <Route path="/industry/distribute" element={<ProtectedRoute><GlobalDistribution /></ProtectedRoute>} />
            <Route path="/industry/coverage" element={<ProtectedRoute><IndustryCoverage /></ProtectedRoute>} />
            <Route path="/industry/ipi" element={<ProtectedRoute><IPIManagement /></ProtectedRoute>} />
            <Route path="/industry/identifiers" element={<ProtectedRoute><IndustryIdentifiersManagement /></ProtectedRoute>} />
            <Route path="/industry/entertainment" element={<ProtectedRoute><EnhancedEntertainmentDashboard /></ProtectedRoute>} />
            <Route path="/industry/photography" element={<ProtectedRoute><PhotographyServices /></ProtectedRoute>} />
            <Route path="/industry/video" element={<ProtectedRoute><VideoProductionServices /></ProtectedRoute>} />
            <Route path="/industry/monetization" element={<ProtectedRoute><MonetizationOpportunities /></ProtectedRoute>} />
            <Route path="/industry/mdx" element={<ProtectedRoute><MusicDataExchange /></ProtectedRoute>} />
            <Route path="/industry/mlc" element={<ProtectedRoute><MechanicalLicensingCollective /></ProtectedRoute>} />
            
            {/* Label Management Routes */}
            <Route path="/label" element={<ProtectedRoute><LabelDashboard /></ProtectedRoute>} />
            <Route path="/label/artists" element={<ProtectedRoute><LabelDashboard /></ProtectedRoute>} />
            <Route path="/label/ar" element={<ProtectedRoute><LabelDashboard /></ProtectedRoute>} />
            <Route path="/label/projects" element={<ProtectedRoute><ProjectManagement /></ProtectedRoute>} />
            <Route path="/label/marketing" element={<ProtectedRoute><MarketingManagement /></ProtectedRoute>} />
            <Route path="/label/finance" element={<ProtectedRoute><FinancialManagement /></ProtectedRoute>} />
            
            {/* Payment & Earnings Routes */}
            <Route path="/pricing" element={<PaymentPackages onSelectPackage={(pkg) => window.location.href = `/checkout/${pkg.id}`} />} />
            <Route path="/checkout/:packageId" element={<ProtectedRoute><EnhancedPaymentCheckout /></ProtectedRoute>} />
            <Route path="/payment/success" element={<ProtectedRoute><PaymentStatus /></ProtectedRoute>} />
            <Route path="/payment/cancel" element={<ProtectedRoute><PaymentStatus /></ProtectedRoute>} />
            <Route path="/earnings" element={<ProtectedRoute><EarningsDashboard /></ProtectedRoute>} />
            <Route path="/banking" element={<ProtectedRoute><BankAccountManager /></ProtectedRoute>} />
            <Route path="/wallets" element={<ProtectedRoute><DigitalWalletManager /></ProtectedRoute>} />
            <Route path="/royalties/:mediaId" element={<ProtectedRoute><RoyaltySplitManager /></ProtectedRoute>} />
            <Route path="/library" element={<Library />} />
            <Route path="/platforms" element={<Platforms />} />
            <Route path="/blockchain" element={<Blockchain />} />
            <Route path="/sponsorship" element={<ProtectedRoute><SponsorshipDashboard /></ProtectedRoute>} />
            <Route path="/ddex" element={<ProtectedRoute><DDEXCompliance /></ProtectedRoute>} />
            <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
            <Route path="/distribute" element={<ProtectedRoute><Distribute /></ProtectedRoute>} />
            <Route path="/purchase-success" element={<ProtectedRoute><PurchaseSuccess /></ProtectedRoute>} />
            
            {/* Admin Routes */}
            <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
            <Route path="/admin/users" element={<AdminRoute><AdminUserManagement /></AdminRoute>} />
            <Route path="/admin/content" element={<AdminRoute><AdminContentManagement /></AdminRoute>} />
            <Route path="/admin/sponsorship" element={<AdminRoute><AdminSponsorshipOverview /></AdminRoute>} />
            <Route path="/admin/tax" element={<AdminRoute><TaxDashboard /></AdminRoute>} />
            <Route path="/admin/tax/1099s" element={<AdminRoute><Form1099Management /></AdminRoute>} />
            <Route path="/admin/tax/reports" element={<AdminRoute><TaxReports /></AdminRoute>} />
            <Route path="/admin/tax/business" element={<AdminRoute><BusinessTaxInfo /></AdminRoute>} />
            <Route path="/admin/tax/licenses" element={<AdminRoute><BusinessLicenseManagement /></AdminRoute>} />
            <Route path="/admin/tax/compliance" element={<AdminRoute><ComplianceDashboard /></AdminRoute>} />
            <Route path="/admin/analytics" element={<AdminRoute><AdminAnalytics /></AdminRoute>} />
            <Route path="/admin/revenue" element={<AdminRoute><AdminRevenue /></AdminRoute>} />
            <Route path="/admin/blockchain" element={<AdminRoute><Blockchain /></AdminRoute>} />
            <Route path="/admin/ddex" element={<AdminRoute><DDEXAdminDashboard /></AdminRoute>} />
            <Route path="/admin/industry" element={<AdminRoute><IndustryDashboard /></AdminRoute>} />
            <Route path="/admin/industry/ipi" element={<AdminRoute><IPIManagement /></AdminRoute>} />
            <Route path="/admin/industry/identifiers" element={<AdminRoute><IndustryIdentifiersManagement /></AdminRoute>} />
            <Route path="/admin/industry/entertainment" element={<AdminRoute><EnhancedEntertainmentDashboard /></AdminRoute>} />
            <Route path="/admin/industry/photography" element={<AdminRoute><PhotographyServices /></AdminRoute>} />
            <Route path="/admin/industry/video" element={<AdminRoute><VideoProductionServices /></AdminRoute>} />
            <Route path="/admin/industry/monetization" element={<AdminRoute><MonetizationOpportunities /></AdminRoute>} />
            <Route path="/admin/industry/mdx" element={<AdminRoute><MusicDataExchange /></AdminRoute>} />
            <Route path="/admin/industry/mlc" element={<AdminRoute><MechanicalLicensingCollective /></AdminRoute>} />
            
            {/* Admin Label Management Routes */}
            <Route path="/admin/label" element={<AdminRoute><LabelDashboard /></AdminRoute>} />
            <Route path="/admin/label/artists" element={<AdminRoute><LabelDashboard /></AdminRoute>} />
            <Route path="/admin/label/ar" element={<AdminRoute><LabelDashboard /></AdminRoute>} />
            <Route path="/admin/label/projects" element={<AdminRoute><ProjectManagement /></AdminRoute>} />
            <Route path="/admin/label/marketing" element={<AdminRoute><MarketingManagement /></AdminRoute>} />
            <Route path="/admin/label/finance" element={<AdminRoute><FinancialManagement /></AdminRoute>} />
            
            {/* Admin Payment & Earnings Routes */}
            <Route path="/admin/payments" element={<AdminRoute><PaymentPackages /></AdminRoute>} />
            <Route path="/admin/earnings" element={<AdminRoute><EarningsDashboard /></AdminRoute>} />
            <Route path="/admin/banking" element={<AdminRoute><BankAccountManager /></AdminRoute>} />
            <Route path="/admin/wallets" element={<AdminRoute><DigitalWalletManager /></AdminRoute>} />
            <Route path="/admin/security" element={<AdminRoute><AdminSecurity /></AdminRoute>} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;