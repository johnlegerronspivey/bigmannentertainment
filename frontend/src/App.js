import React, { useState, useEffect, useContext, createContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";

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

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
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
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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
              <p className="text-sm text-gray-300">Digital Media Distribution</p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/library" className="hover:text-purple-400 transition-colors">Library</Link>
            <Link to="/upload" className="hover:text-purple-400 transition-colors">Upload</Link>
            <Link to="/distribute" className="hover:text-purple-400 transition-colors">Distribute</Link>
            <Link to="/platforms" className="hover:text-purple-400 transition-colors">Platforms</Link>
            <Link to="/blockchain" className="hover:text-purple-400 transition-colors">Blockchain</Link>
            {user?.is_admin && (
              <Link to="/admin" className="hover:text-purple-400 transition-colors">Admin</Link>
            )}
          </nav>

          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm">Welcome, {user.full_name}</span>
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
      </div>
    </header>
  );
};

const Home = () => {
  const [featuredMedia, setFeaturedMedia] = useState([]);
  const [stats, setStats] = useState({});

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
      const response = await axios.get(`${API}/analytics/dashboard`);
      setStats(response.data.stats);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

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
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            Big Mann Entertainment
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-200">
            Professional Audio, Video & Digital Media Distribution Platform
          </p>
          <p className="text-lg mb-8 text-gray-300">
            John LeGerron Spivey • Commercial Publishing • Multi-Platform Distribution
          </p>
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Link
              to="/library"
              className="bg-purple-600 hover:bg-purple-700 px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
            >
              Explore Library
            </Link>
            <Link
              to="/register"
              className="bg-pink-600 hover:bg-pink-700 px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
            >
              Start Publishing
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 text-center">
            <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-6 rounded-lg">
              <h3 className="text-3xl font-bold text-purple-600">{stats.total_media || 0}</h3>
              <p className="text-gray-600">Total Media</p>
            </div>
            <div className="bg-gradient-to-r from-blue-100 to-purple-100 p-6 rounded-lg">
              <h3 className="text-3xl font-bold text-blue-600">{stats.published_media || 0}</h3>
              <p className="text-gray-600">Published</p>
            </div>
            <div className="bg-gradient-to-r from-green-100 to-blue-100 p-6 rounded-lg">
              <h3 className="text-3xl font-bold text-green-600">{stats.total_users || 0}</h3>
              <p className="text-gray-600">Users</p>
            </div>
            <div className="bg-gradient-to-r from-yellow-100 to-green-100 p-6 rounded-lg">
              <h3 className="text-3xl font-bold text-yellow-600">${stats.total_revenue || 0}</h3>
              <p className="text-gray-600">Revenue</p>
            </div>
            <div className="bg-gradient-to-r from-red-100 to-yellow-100 p-6 rounded-lg">
              <h3 className="text-3xl font-bold text-red-600">{stats.supported_platforms || 52}</h3>
              <p className="text-gray-600">Platforms</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Media */}
      <section className="py-16 bg-gray-50">
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
                  <p className="text-gray-600 mb-4">{media.description}</p>
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

      {/* Distribution Platforms Preview */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-8">Complete Media Distribution Empire</h2>
          <p className="text-xl text-gray-600 mb-12">
            Distribute across 50+ platforms: Social Media • Streaming • Traditional FM Radio (All Genres) • TV Networks • Performance Royalties
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
            {[
              "Instagram", "Spotify", "Clear Channel Pop", "CNN",
              "Twitter", "Apple Music", "Cumulus Country", "Netflix", 
              "TikTok", "SoundCloud", "Audacy Rock", "ESPN",
              "YouTube", "Pandora", "Urban One Hip-Hop", "HBO Max",
              "Facebook", "Tidal", "NPR Classical", "SoundExchange",
              "LinkedIn", "Amazon Music", "Townsquare AC", "ASCAP",
              "Pinterest", "Deezer", "Regional Indie FM", "BMI",
              "Snapchat", "Bandcamp", "Salem Christian", "SESAC"
            ].map((platform) => (
              <div key={platform} className={`p-3 rounded-lg hover:bg-purple-100 transition-colors text-center ${
                ['SoundExchange', 'ASCAP', 'BMI', 'SESAC'].includes(platform) 
                  ? 'bg-orange-100 border-2 border-orange-200' 
                  : platform.includes('FM') || ['Clear Channel Pop', 'Cumulus Country', 'Audacy Rock', 'Urban One Hip-Hop', 'NPR Classical', 'Townsquare AC', 'Regional Indie FM', 'Salem Christian'].includes(platform)
                  ? 'bg-amber-100 border-2 border-amber-200'
                  : 'bg-gray-100'
              }`}>
                <p className={`font-semibold text-sm ${
                  ['SoundExchange', 'ASCAP', 'BMI', 'SESAC'].includes(platform) 
                    ? 'text-orange-700' 
                    : platform.includes('FM') || ['Clear Channel Pop', 'Cumulus Country', 'Audacy Rock', 'Urban One Hip-Hop', 'NPR Classical', 'Townsquare AC', 'Regional Indie FM', 'Salem Christian'].includes(platform)
                    ? 'text-amber-700'
                    : 'text-gray-700'
                }`}>{platform}</p>
                {['SoundExchange', 'ASCAP', 'BMI', 'SESAC'].includes(platform) && (
                  <p className="text-xs text-orange-600 mt-1">Royalties</p>
                )}
                {(platform.includes('FM') || ['Clear Channel Pop', 'Cumulus Country', 'Audacy Rock', 'Urban One Hip-Hop', 'NPR Classical', 'Townsquare AC', 'Regional Indie FM', 'Salem Christian'].includes(platform)) && (
                  <p className="text-xs text-amber-600 mt-1">FM Radio</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
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
      
      setMessage('Media uploaded successfully!');
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
          Big Mann Entertainment supports distribution to {Object.keys(platforms).length} major platforms across social media, streaming services, radio stations, TV networks, and podcast platforms.
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
                <p>Max file size: {platform.max_file_size_mb.toFixed(0)} MB</p>
              </div>
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
                  Select Platforms *
                </label>
                <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto border border-gray-300 rounded-md p-3">
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
                        <span className="text-sm">{platform.name}</span>
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
                      Platforms: {distribution.target_platforms.join(', ')}
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
            <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
            <Route path="/distribute" element={<ProtectedRoute><Distribute /></ProtectedRoute>} />
            <Route path="/purchase-success" element={<ProtectedRoute><PurchaseSuccess /></ProtectedRoute>} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;