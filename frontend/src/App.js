import React, { useState, useEffect, useContext, createContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { DDEXERNCreator, DDEXCWRCreator, DDEXMessageList, DDEXIdentifierGenerator, DDEXAdminDashboard } from "./DDEXComponents";
import { SponsorshipDashboard, SponsorshipDealCreator, MetricsRecorder, AdminSponsorshipOverview } from "./SponsorshipComponents";
import { TaxDashboard, Form1099Management, TaxReports, BusinessTaxInfo } from "./TaxComponents";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

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
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
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
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
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

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const isAdmin = () => {
    return user && (user.is_admin || ['admin', 'super_admin', 'moderator'].includes(user.role));
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, isAdmin }}>
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
              src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
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
                  <Link to="/admin/analytics" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Analytics</Link>
                  <Link to="/admin/revenue" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Revenue</Link>
                  <Link to="/admin/blockchain" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Blockchain</Link>
                  <Link to="/admin/ddex" className="block px-4 py-2 hover:bg-gray-100 transition-colors">DDEX Compliance</Link>
                  <Link to="/admin/security" className="block px-4 py-2 hover:bg-gray-100 transition-colors">Security</Link>
                </div>
              </div>
            )}
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
                  <div className="text-sm font-medium">{user.full_name}</div>
                  {isAdmin() && <div className="text-xs text-purple-300">Administrator</div>}
                </div>
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
                    <Link to="/admin/analytics" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Analytics</Link>
                    <Link to="/admin/revenue" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Revenue</Link>
                    <Link to="/admin/blockchain" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Blockchain</Link>
                    <Link to="/admin/ddex" className="hover:text-purple-400 transition-colors py-1 pl-4 block">DDEX</Link>
                    <Link to="/admin/security" className="hover:text-purple-400 transition-colors py-1 pl-4 block">Security</Link>
                  </div>
                </>
              )}
              {user && (
                <div className="border-t border-gray-700 pt-2 mt-2">
                  <div className="text-sm font-medium mb-2">{user.full_name}</div>
                  <button
                    onClick={logout}
                    className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg transition-colors w-full text-left"
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
              src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
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
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const { isAdmin } = useAuth();

  useEffect(() => {
    if (isAdmin()) {
      fetchUsers();
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
        <h1 className="text-3xl font-bold mb-8">User Management</h1>
        
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
                          <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
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
                      <button
                        onClick={() => {
                          setSelectedUser(user);
                          setShowUserModal(true);
                        }}
                        className="text-purple-600 hover:text-purple-900 mr-4"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleUserDelete(user.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
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
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
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
            src="https://customer-assets.emergentagent.com/job_audio-video-dist/artifacts/zwcs0h0g_Big%20Mann%20Entertainment%20Logo.png" 
            alt="Big Mann Entertainment Logo" 
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="text-gray-600">Big Mann Entertainment</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
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
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
};

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    business_name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await register(formData);
    
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
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>
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
            <Route path="/admin/analytics" element={<AdminRoute><AdminAnalytics /></AdminRoute>} />
            <Route path="/admin/revenue" element={<AdminRoute><AdminRevenue /></AdminRoute>} />
            <Route path="/admin/blockchain" element={<AdminRoute><Blockchain /></AdminRoute>} />
            <Route path="/admin/ddex" element={<AdminRoute><DDEXAdminDashboard /></AdminRoute>} />
            <Route path="/admin/security" element={<AdminRoute><AdminSecurity /></AdminRoute>} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;