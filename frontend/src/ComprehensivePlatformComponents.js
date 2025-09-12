import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || 'https://content-hub-277.preview.emergentagent.com';

// Global error handler utility
const handleApiError = (error, context) => {
  console.error(`Error in ${context}:`, error);
  
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    return;
  }
  
  console.error('API Error:', error.response?.data?.message || error.message || 'Unknown error');
};

// Safe API response handler
const handleApiResponse = (response, successCallback, errorMessage = 'API call failed') => {
  if (response?.data?.success) {
    if (successCallback) successCallback(response.data);
    return true;
  } else {
    console.error(errorMessage, response?.data?.message || 'Unknown error');
    return false;
  }
};

// PHASE 1: CORE FOUNDATION COMPONENTS

// Global Header Component
const GlobalHeader = ({ user, notifications, onSearch, onNotificationClick, onUserMenuToggle }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [environment, setEnvironment] = useState('live');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery);
    }
  };

  const toggleDarkMode = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('darkMode', newMode.toString());
    document.documentElement.classList.toggle('dark', newMode);
  };

  const unreadNotifications = notifications?.filter(n => !n.read).length || 0;

  return (
    <header className={`sticky top-0 z-50 ${isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-gray-200'} border-b shadow-sm`}>
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <img 
                src="/logo.png" 
                alt="Big Mann Entertainment" 
                className="h-8 w-auto"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'inline';
                }}
              />
              <span 
                className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}
                style={{display: 'none'}}
              >
                BME Platform
              </span>
            </div>
            
            {/* Environment Toggle */}
            <div className="flex items-center space-x-2">
              <select
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className={`text-sm border rounded px-2 py-1 ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              >
                <option value="live">🟢 Live</option>
                <option value="staging">🟡 Staging</option>
              </select>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-lg mx-8">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="Search assets, contributors, contracts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={`w-full pl-10 pr-4 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 placeholder-gray-500'} focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className={`h-5 w-5 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </form>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className={`p-2 rounded-lg ${isDarkMode ? 'text-yellow-400 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className={`p-2 rounded-lg relative ${isDarkMode ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11c0-3.625-2.957-6.568-6.6-6.568A6.57 6.57 0 005 11v3.159c0 .538-.214 1.055-.595 1.436L3 17h5m6-4v1a3 3 0 11-6 0v-1m6 0a3 3 0 11-6 0" />
                </svg>
                {unreadNotifications > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadNotifications > 9 ? '9+' : unreadNotifications}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className={`absolute right-0 mt-2 w-80 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg shadow-lg z-50`}>
                  <div className={`p-4 border-b ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                    <h3 className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Notifications</h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {notifications && notifications.length > 0 ? notifications.slice(0, 10).map((notification, index) => (
                      <div key={index} className={`p-4 border-b last:border-b-0 ${isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-100 hover:bg-gray-50'} cursor-pointer`}>
                        <div className="flex items-start space-x-3">
                          <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${notification.read ? 'bg-gray-400' : 'bg-blue-500'}`} />
                          <div className="flex-1">
                            <p className={`text-sm ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{notification.title}</p>
                            <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'} mt-1`}>{notification.message}</p>
                            <p className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-400'} mt-1`}>{notification.time}</p>
                          </div>
                        </div>
                      </div>
                    )) : (
                      <div className="p-4 text-center">
                        <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>No notifications</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className={`flex items-center space-x-2 p-2 rounded-lg ${isDarkMode ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user?.name?.charAt(0) || 'U'}
                </div>
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* User Menu Dropdown */}
              {showUserMenu && (
                <div className={`absolute right-0 mt-2 w-56 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg shadow-lg z-50`}>
                  <div className={`p-4 border-b ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                    <p className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{user?.name || 'User'}</p>
                    <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>{user?.email || 'user@example.com'}</p>
                  </div>
                  <div className="py-2">
                    <Link to="/profile" className={`block px-4 py-2 text-sm ${isDarkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'}`}>
                      👤 Profile Settings
                    </Link>
                    <Link to="/dao-governance" className={`block px-4 py-2 text-sm ${isDarkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'}`}>
                      🧠 DAO Governance
                    </Link>
                    <Link to="/settings" className={`block px-4 py-2 text-sm ${isDarkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-700 hover:bg-gray-100'}`}>
                      ⚙️ Settings
                    </Link>
                    <div className={`border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} my-2`} />
                    <button
                      onClick={() => {
                        localStorage.removeItem('token');
                        window.location.href = '/login';
                      }}
                      className={`w-full text-left px-4 py-2 text-sm ${isDarkMode ? 'text-red-400 hover:bg-gray-700' : 'text-red-600 hover:bg-gray-100'}`}
                    >
                      🚪 Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

// Left Sidebar Navigation Component
const LeftSidebar = ({ activeModule, onModuleChange, isCollapsed, onToggleCollapse }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  const modules = [
    { id: 'main-dashboard', name: 'Main Dashboard', icon: '🏠', badge: null },
    { id: 'content-manager', name: 'Content Manager', icon: '📁', badge: null },
    { id: 'distribution-tracker', name: 'Distribution Tracker', icon: '📡', badge: '32' },
    { id: 'royalty-engine', name: 'Royalty Engine', icon: '💰', badge: 'NEW' },
    { id: 'compliance-center', name: 'Compliance Center', icon: '🛡️', badge: '2' },
    { id: 'analytics-forecasting', name: 'Analytics & Forecasting', icon: '📊', badge: null },
    { id: 'sponsorship-campaigns', name: 'Sponsorship & Campaigns', icon: '🤝', badge: null },
    { id: 'contributor-hub', name: 'Contributor Hub', icon: '👥', badge: null },
    { id: 'system-health', name: 'System Health & Logs', icon: '⚙️', badge: null },
    { id: 'dao-governance', name: 'DAO Governance', icon: '🧠', badge: '3' }
  ];

  return (
    <div className={`${isCollapsed ? 'w-16' : 'w-64'} transition-all duration-300 ${isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-gray-50 border-gray-200'} border-r h-screen sticky top-16 overflow-y-auto`}>
      {/* Collapse Button */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={onToggleCollapse}
          className={`w-full flex items-center justify-center p-2 rounded-lg ${isDarkMode ? 'text-gray-400 hover:bg-gray-800 hover:text-white' : 'text-gray-600 hover:bg-gray-200'}`}
        >
          <svg 
            className={`h-5 w-5 transform transition-transform ${isCollapsed ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* Navigation Modules */}
      <nav className="p-4 space-y-2">
        {modules.map((module) => (
          <button
            key={module.id}
            onClick={() => onModuleChange(module.id)}
            className={`w-full flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} p-3 rounded-lg text-left transition-colors ${
              activeModule === module.id
                ? isDarkMode ? 'bg-blue-900 text-blue-100' : 'bg-blue-100 text-blue-900'
                : isDarkMode ? 'text-gray-300 hover:bg-gray-800 hover:text-white' : 'text-gray-700 hover:bg-gray-200'
            }`}
            title={isCollapsed ? module.name : ''}
          >
            <div className="flex items-center space-x-3">
              <span className="text-lg">{module.icon}</span>
              {!isCollapsed && (
                <span className="font-medium">{module.name}</span>
              )}
            </div>
            {!isCollapsed && module.badge && (
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                module.badge === 'NEW' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {module.badge}
              </span>
            )}
          </button>
        ))}
      </nav>
    </div>
  );
};

// KPI Snapshot Cards Component
const KPISnapshotCards = ({ kpiData, onCardClick }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  const kpis = [
    {
      id: 'assets-live',
      title: '🎬 Assets Live',
      value: kpiData?.assetsLive || '1,248',
      status: '✅',
      statusColor: 'text-green-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'platforms-connected',
      title: '🌐 Platforms Connected',
      value: kpiData?.platformsConnected || '32',
      status: '🔄',
      statusColor: 'text-blue-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'royalties-today',
      title: '💸 Royalties Today',
      value: kpiData?.royaltiesToday || '$12,430.88',
      status: '📈',
      statusColor: 'text-green-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'pending-payouts',
      title: '⏳ Pending Payouts',
      value: kpiData?.pendingPayouts || '$3,210.00',
      status: '⚠️',
      statusColor: 'text-yellow-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'compliance-flags',
      title: '🛡️ Compliance Flags',
      value: kpiData?.complianceFlags || '2',
      status: '🔍',
      statusColor: 'text-red-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'forecast-roi',
      title: '📈 Forecast ROI (30d)',
      value: kpiData?.forecastROI || '+18.4%',
      status: '📊',
      statusColor: 'text-purple-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
      {kpis.map((kpi) => (
        <div
          key={kpi.id}
          onClick={() => onCardClick(kpi.id)}
          className={`${kpi.bgColor} ${isDarkMode ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-200 hover:bg-gray-50'} border rounded-lg p-4 cursor-pointer transition-colors shadow-sm`}
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              {kpi.title}
            </h3>
            <span className={`text-lg ${kpi.statusColor}`}>
              {kpi.status}
            </span>
          </div>
          <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            {kpi.value}
          </p>
        </div>
      ))}
    </div>
  );
};

// Main Dashboard View Component
const MainDashboard = ({ kpiData, recentActivities, systemAlerts }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  const handleKPICardClick = (kpiId) => {
    console.log(`KPI card clicked: ${kpiId}`);
    // Handle drill-down navigation
  };

  return (
    <div className="space-y-6">
      {/* KPI Snapshot Cards */}
      <KPISnapshotCards kpiData={kpiData} onCardClick={handleKPICardClick} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <div className={`lg:col-span-2 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
          <h2 className={`text-lg font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            Recent Activities
          </h2>
          <div className="space-y-4">
            {recentActivities && recentActivities.length > 0 ? recentActivities.map((activity, index) => (
              <div key={index} className={`flex items-start space-x-3 p-3 rounded-lg ${isDarkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <div className="flex-shrink-0">
                  <span className="text-lg">{activity.icon}</span>
                </div>
                <div className="flex-1">
                  <p className={`text-sm ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    {activity.description}
                  </p>
                  <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'} mt-1`}>
                    {activity.timestamp}
                  </p>
                </div>
              </div>
            )) : (
              <div className="text-center py-8">
                <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  No recent activities
                </p>
              </div>
            )}
          </div>
        </div>

        {/* System Alerts */}
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
          <h2 className={`text-lg font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            System Alerts
          </h2>
          <div className="space-y-3">
            {systemAlerts && systemAlerts.length > 0 ? systemAlerts.map((alert, index) => (
              <div key={index} className={`p-3 rounded-lg border-l-4 ${
                alert.severity === 'high' ? 'border-red-500 bg-red-50 dark:bg-red-900/20' :
                alert.severity === 'medium' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' :
                'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              }`}>
                <div className="flex items-center justify-between">
                  <p className={`text-sm font-medium ${
                    alert.severity === 'high' ? 'text-red-800 dark:text-red-200' :
                    alert.severity === 'medium' ? 'text-yellow-800 dark:text-yellow-200' :
                    'text-blue-800 dark:text-blue-200'
                  }`}>
                    {alert.title}
                  </p>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    alert.severity === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100' :
                    alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100' :
                    'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
                <p className={`text-xs mt-1 ${
                  alert.severity === 'high' ? 'text-red-700 dark:text-red-300' :
                  alert.severity === 'medium' ? 'text-yellow-700 dark:text-yellow-300' :
                  'text-blue-700 dark:text-blue-300'
                }`}>
                  {alert.message}
                </p>
              </div>
            )) : (
              <div className="text-center py-4">
                <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  No system alerts
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Platform Component
export const ComprehensivePlatform = () => {
  const [activeModule, setActiveModule] = useState('main-dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [kpiData, setKpiData] = useState({});
  const [recentActivities, setRecentActivities] = useState([]);
  const [systemAlerts, setSystemAlerts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [user, setUser] = useState({ name: 'John Spivey', email: 'john.spivey@bigmannentertainment.com' });

  // Initialize sample data
  useEffect(() => {
    // Sample KPI data
    setKpiData({
      assetsLive: '1,248',
      platformsConnected: '32',
      royaltiesToday: '$12,430.88',
      pendingPayouts: '$3,210.00',
      complianceFlags: '2',
      forecastROI: '+18.4%'
    });

    // Sample recent activities
    setRecentActivities([
      {
        icon: '🎵',
        description: 'New track "Summer Vibes" approved for distribution',
        timestamp: '2 minutes ago'
      },
      {
        icon: '💰',
        description: 'Royalty payment of $1,250.00 processed to Artist_123',
        timestamp: '15 minutes ago'
      },
      {
        icon: '📡',
        description: 'Content successfully delivered to Spotify',
        timestamp: '1 hour ago'
      },
      {
        icon: '🛡️',
        description: 'Compliance check completed for territory US',
        timestamp: '2 hours ago'
      }
    ]);

    // Sample system alerts
    setSystemAlerts([
      {
        title: 'Delivery Failed',
        message: 'Unable to deliver content to TikTok due to API limits',
        severity: 'high'
      },
      {
        title: 'Low Balance',
        message: 'Payout wallet balance below $1,000',
        severity: 'medium'
      }
    ]);

    // Sample notifications
    setNotifications([
      {
        title: 'New Royalty Payment',
        message: 'You received $245.67 from Spotify streams',
        time: '5 min ago',
        read: false
      },
      {
        title: 'Content Approved',
        message: 'Your track "Midnight Dreams" has been approved',
        time: '1 hour ago',
        read: false
      },
      {
        title: 'System Maintenance',
        message: 'Scheduled maintenance tonight at 2 AM EST',
        time: '3 hours ago',
        read: true
      }
    ]);
  }, []);

  const handleSearch = (query) => {
    console.log('Search query:', query);
    // Implement search functionality
  };

  const handleNotificationClick = (notification) => {
    console.log('Notification clicked:', notification);
    // Handle notification click
  };

  const handleModuleChange = (moduleId) => {
    setActiveModule(moduleId);
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Global Header */}
      <GlobalHeader
        user={user}
        notifications={notifications}
        onSearch={handleSearch}
        onNotificationClick={handleNotificationClick}
      />

      <div className="flex">
        {/* Left Sidebar */}
        <LeftSidebar
          activeModule={activeModule}
          onModuleChange={handleModuleChange}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={toggleSidebar}
        />

        {/* Main Content */}
        <main className={`flex-1 p-6 ${sidebarCollapsed ? 'ml-0' : 'ml-0'}`}>
          <div className="max-w-full">
            {/* Module Title */}
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white capitalize">
                {activeModule.replace('-', ' ')} Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Manage and monitor your {activeModule.replace('-', ' ')} operations
              </p>
            </div>

            {/* Module Content */}
            {activeModule === 'content-manager' && (
              <ContentManager />
            )}
            {activeModule === 'distribution-tracker' && (
              <DistributionTracker />
            )}
            {activeModule === 'royalty-engine' && (
              <RoyaltyEngine />
            )}
            {activeModule === 'compliance-center' && (
              <ComplianceCenter />
            )}
            {activeModule === 'analytics-forecasting' && (
              <AnalyticsForecasting />
            )}
            {activeModule === 'sponsorship-campaigns' && (
              <SponsorshipCampaigns />
            )}
            {activeModule === 'contributor-hub' && (
              <ContributorHub />
            )}
            {activeModule === 'system-health' && (
              <SystemHealth />
            )}
            {activeModule === 'dao-governance' && (
              <DAOGovernance />
            )}
            {activeModule === 'main-dashboard' && (
              <MainDashboard
                kpiData={kpiData}
                recentActivities={recentActivities}
                systemAlerts={systemAlerts}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

// PHASE 2: CONTENT & DISTRIBUTION MODULES

// Content Manager Component
const ContentManager = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [assets, setAssets] = useState([]);
  const [folders, setFolders] = useState([]);
  const [selectedAssets, setSelectedAssets] = useState([]);
  const [contentStats, setContentStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('assets');

  useEffect(() => {
    fetchContentData();
  }, []);

  const fetchContentData = async () => {
    setLoading(true);
    try {
      const [assetsRes, foldersRes, statsRes] = await Promise.all([
        axios.get(`${API}/api/platform/content/assets?user_id=user_123`),
        axios.get(`${API}/api/platform/content/folders?user_id=user_123`),
        axios.get(`${API}/api/platform/content/stats?user_id=user_123`)
      ]);

      if (assetsRes.data.success) setAssets(assetsRes.data.assets || []);
      if (foldersRes.data.success) setFolders(foldersRes.data.folders || []);
      if (statsRes.data.success) setContentStats(statsRes.data.stats || {});
    } catch (error) {
      handleApiError(error, 'fetchContentData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'assets', name: 'Assets', icon: '📁' },
    { id: 'folders', name: 'Folders', icon: '📂' },
    { id: 'upload', name: 'Upload', icon: '⬆️' },
    { id: 'analytics', name: 'Analytics', icon: '📊' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Content Manager</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Organize and manage all your content assets</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
          <span>➕</span>
          <span>Add Content</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Assets</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.total_assets || '1,248'}</p>
            </div>
            <span className="text-2xl">📁</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.total_size || '45.2 GB'}</p>
            </div>
            <span className="text-2xl">💾</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">This Month</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.this_month?.uploaded || '67'}</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Live Assets</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.by_status?.live || '1,100'}</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'assets' && (
          <div className="space-y-4">
            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search assets..."
                  className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                />
              </div>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Types</option>
                <option>Audio</option>
                <option>Video</option>
                <option>Image</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Status</option>
                <option>Live</option>
                <option>Draft</option>
                <option>Pending Review</option>
              </select>
            </div>

            {/* Assets Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {assets.length > 0 ? assets.map((asset, index) => (
                <div key={asset.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4 hover:shadow-md transition-shadow`}>
                  <div className="aspect-w-16 aspect-h-9 mb-3">
                    <div className={`${isDarkMode ? 'bg-gray-700' : 'bg-gray-100'} rounded-lg flex items-center justify-center`}>
                      <span className="text-2xl">
                        {asset.content_type === 'audio' ? '🎵' : asset.content_type === 'video' ? '🎬' : '🖼️'}
                      </span>
                    </div>
                  </div>
                  <h3 className="font-medium text-gray-900 dark:text-white truncate">{asset.title || 'Untitled'}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{asset.content_type || 'Unknown'}</p>
                  <div className="flex justify-between items-center mt-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      asset.status === 'live' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                      asset.status === 'draft' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                    }`}>
                      {asset.status || 'unknown'}
                    </span>
                    <div className="flex space-x-1">
                      <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">✏️</button>
                      <button className="text-gray-400 hover:text-red-600">🗑️</button>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="col-span-full text-center py-8">
                  <div className="text-4xl mb-4">📁</div>
                  <p className="text-gray-600 dark:text-gray-400">No assets found. Upload your first content to get started!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'folders' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {folders.length > 0 ? folders.map((folder, index) => (
                <div key={folder.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer`}>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{backgroundColor: folder.color || '#3B82F6'}}>
                      <span className="text-white text-lg">📂</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 dark:text-white">{folder.name}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{folder.description || 'No description'}</p>
                    </div>
                  </div>
                </div>
              )) : (
                <div className="col-span-full text-center py-8">
                  <div className="text-4xl mb-4">📂</div>
                  <p className="text-gray-600 dark:text-gray-400">No folders created yet. Organize your content with folders!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'upload' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-8`}>
            <div className="text-center">
              <div className="text-6xl mb-4">⬆️</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Upload Content</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">Drag and drop files here or click to browse</p>
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                Choose Files
              </button>
              <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
                Supported formats: MP3, WAV, MP4, MOV, JPG, PNG • Max size: 100MB
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Content by Type</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Audio</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.audio || '892'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Video</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.video || '234'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Image</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.image || '122'}</span>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Content by Status</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Live</span>
                  <span className="font-medium text-green-600">{contentStats.by_status?.live || '1,100'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Pending Review</span>
                  <span className="font-medium text-yellow-600">{contentStats.by_status?.pending_review || '35'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Draft</span>
                  <span className="font-medium text-gray-600">{contentStats.by_status?.draft || '113'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Distribution Tracker Component
const DistributionTracker = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [distributionJobs, setDistributionJobs] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('jobs');

  useEffect(() => {
    fetchDistributionData();
  }, []);

  const fetchDistributionData = async () => {
    setLoading(true);
    try {
      const [jobsRes, platformsRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/api/platform/distribution/jobs?user_id=user_123`),
        axios.get(`${API}/api/platform/distribution/platforms`),
        axios.get(`${API}/api/platform/distribution/analytics?user_id=user_123`)
      ]);

      if (jobsRes.data.success) setDistributionJobs(jobsRes.data.jobs || []);
      if (platformsRes.data.success) setPlatforms(platformsRes.data.platforms || []);
      if (analyticsRes.data.success) setAnalytics(analyticsRes.data.analytics || {});
    } catch (error) {
      handleApiError(error, 'fetchDistributionData');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'processing': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'jobs', name: 'Distribution Jobs', icon: '📤' },
    { id: 'platforms', name: 'Platforms', icon: '🌐' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
    { id: 'create', name: 'Create Job', icon: '➕' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Distribution Tracker</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Monitor content distribution across all platforms</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
          <span>🚀</span>
          <span>Quick Distribute</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Jobs</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.total_jobs || '156'}</p>
            </div>
            <span className="text-2xl">📤</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Jobs</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.active_jobs || '3'}</p>
            </div>
            <span className="text-2xl">🔄</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">{analytics.success_rate || '93.6'}%</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Avg. Delivery Time</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.average_delivery_time || '4.2'}h</p>
            </div>
            <span className="text-2xl">⏱️</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex flex-wrap gap-4">
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Status</option>
                <option>Active</option>
                <option>Completed</option>
                <option>Failed</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Platforms</option>
                <option>Spotify</option>
                <option>Apple Music</option>
                <option>YouTube</option>
              </select>
            </div>

            {/* Jobs List */}
            <div className="space-y-4">
              {distributionJobs.length > 0 ? distributionJobs.map((job, index) => (
                <div key={job.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{job.asset_title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Distributing to {job.platforms?.length || job.total_platforms || 0} platforms
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Progress</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{width: `${job.progress || 0}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{job.progress || 0}%</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Successful</p>
                      <p className="text-lg font-semibold text-green-600">{job.successful_deliveries || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
                      <p className="text-lg font-semibold text-red-600">{job.failed_deliveries || 0}</p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Started: {job.submitted_at ? new Date(job.submitted_at).toLocaleDateString() : 'N/A'}
                    </div>
                    <div className="flex space-x-2">
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View Details</button>
                      {job.status === 'failed' && (
                        <button className="text-green-600 hover:text-green-700 text-sm font-medium">Retry</button>
                      )}
                    </div>
                  </div>
                </div>
              )) : (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📤</div>
                  <p className="text-gray-600 dark:text-gray-400">No distribution jobs found. Create your first distribution job!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'platforms' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.length > 0 ? platforms.map((platform, index) => (
              <div key={platform.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-gray-900 dark:text-white">{platform.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    platform.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 
                    'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                  }`}>
                    {platform.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{platform.category}</p>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  <p>Max file size: {platform.max_file_size ? `${Math.round(platform.max_file_size / 1024 / 1024)}MB` : 'N/A'}</p>
                  <p>Delivery time: {platform.delivery_time_estimate || 'N/A'}</p>
                </div>
              </div>
            )) : (
              <div className="col-span-full text-center py-8">
                <div className="text-4xl mb-4">🌐</div>
                <p className="text-gray-600 dark:text-gray-400">Loading platforms...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Performance</h3>
              <div className="space-y-3">
                {analytics.platform_performance && Object.entries(analytics.platform_performance).map(([platform, data]) => (
                  <div key={platform} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{platform}</span>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{data.success_rate}%</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{data.avg_delivery_time}h avg</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Daily Distribution</h3>
              <div className="space-y-3">
                {analytics.daily_stats && Object.entries(analytics.daily_stats).map(([day, count]) => (
                  <div key={day} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 capitalize">{day}</span>
                    <span className="font-medium text-gray-900 dark:text-white">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Create Distribution Job</h3>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Content</label>
                <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                  <option>Choose content to distribute...</option>
                  <option>Summer Vibes Instrumental</option>
                  <option>Brand Logo Animation</option>
                  <option>Artist Portrait</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Platforms</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {['Spotify', 'Apple Music', 'YouTube', 'Instagram', 'TikTok', 'Facebook'].map((platform) => (
                    <label key={platform} className="flex items-center space-x-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{platform}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Priority</label>
                <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                  <option>Normal</option>
                  <option>High</option>
                  <option>Urgent</option>
                </select>
              </div>

              <div className="flex space-x-4">
                <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
                  Create Distribution Job
                </button>
                <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700">
                  Save as Draft
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// PHASE 3: FINANCIAL & ANALYTICS MODULES

// Royalty Engine Component (Enhanced from existing Real-Time Royalty Engine)
const RoyaltyEngine = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [royaltyData, setRoyaltyData] = useState({});
  const [revenueAnalytics, setRevenueAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    fetchRoyaltyData();
  }, []);

  const fetchRoyaltyData = async () => {
    setLoading(true);
    try {
      const [revenueRes] = await Promise.all([
        axios.get(`${API}/api/platform/analytics/revenue?user_id=user_123`)
      ]);

      if (revenueRes.data.success) setRevenueAnalytics(revenueRes.data.revenue_breakdown || {});
    } catch (error) {
      handleApiError(error, 'fetchRoyaltyData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '💰' },
    { id: 'payments', name: 'Payments', icon: '💳' },
    { id: 'splits', name: 'Royalty Splits', icon: '📊' },
    { id: 'analytics', name: 'Analytics', icon: '📈' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Royalty Engine</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Real-time royalty tracking and distribution</p>
        </div>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2">
          <span>💸</span>
          <span>Process Payouts</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">${revenueAnalytics.total_revenue?.toLocaleString() || '156,432'}</p>
            </div>
            <span className="text-2xl">💰</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending Payouts</p>
              <p className="text-2xl font-bold text-yellow-600">$3,210</p>
            </div>
            <span className="text-2xl">⏳</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Growth</p>
              <p className="text-2xl font-bold text-green-600">{revenueAnalytics.growth_rate || '+18.4'}%</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Contributors</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">234</p>
            </div>
            <span className="text-2xl">👥</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-green-500 text-green-600 dark:text-green-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Revenue by Platform</h3>
              <div className="space-y-4">
                {revenueAnalytics.by_platform && Object.entries(revenueAnalytics.by_platform).map(([platform, amount]) => (
                  <div key={platform} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{platform}</span>
                    <span className="font-semibold text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Assets</h3>
              <div className="space-y-4">
                {revenueAnalytics.by_asset && Object.entries(revenueAnalytics.by_asset).slice(0, 5).map(([asset, amount]) => (
                  <div key={asset} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400 truncate">{asset}</span>
                    <span className="font-semibold text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'payments' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`${isDarkMode ? 'bg-green-800 border-green-700' : 'bg-green-50 border-green-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-green-900 dark:text-green-100">Instant Payouts</h3>
                <p className="text-green-700 dark:text-green-300 text-sm mt-1">Crypto & Digital Wallets</p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-2">$12,450</p>
              </div>
              <div className={`${isDarkMode ? 'bg-blue-800 border-blue-700' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">Scheduled Payouts</h3>
                <p className="text-blue-700 dark:text-blue-300 text-sm mt-1">Bank Transfers & ACH</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-2">$8,750</p>
              </div>
              <div className={`${isDarkMode ? 'bg-yellow-800 border-yellow-700' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">Pending Review</h3>
                <p className="text-yellow-700 dark:text-yellow-300 text-sm mt-1">Manual Approval Required</p>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100 mt-2">$3,210</p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Payments</h3>
              <div className="space-y-4">
                {[
                  { contributor: 'BeatMaster Pro', amount: 1250.00, date: '2024-01-15', method: 'PayPal', status: 'Completed' },
                  { contributor: 'VocalQueen', amount: 890.50, date: '2024-01-14', method: 'Bank Transfer', status: 'Processing' },
                  { contributor: 'GuitarGuru', amount: 456.75, date: '2024-01-13', method: 'Crypto', status: 'Completed' }
                ].map((payment, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{payment.contributor}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{payment.date} • {payment.method}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 dark:text-white">${payment.amount.toLocaleString()}</p>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        payment.status === 'Completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {payment.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'splits' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Royalty Split Configuration</h3>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                Add New Split
              </button>
            </div>
            
            <div className="space-y-4">
              {[
                { asset: 'Summer Vibes Instrumental', contributors: [
                  { name: 'Producer', percentage: 50, amount: '$11,728' },
                  { name: 'Artist', percentage: 30, amount: '$7,037' },
                  { name: 'Label', percentage: 20, amount: '$4,691' }
                ]},
                { asset: 'Midnight Dreams', contributors: [
                  { name: 'Songwriter', percentage: 40, amount: '$7,294' },
                  { name: 'Vocalist', percentage: 35, amount: '$6,382' },
                  { name: 'Producer', percentage: 25, amount: '$4,559' }
                ]}
              ].map((split, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">{split.asset}</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {split.contributors.map((contributor, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{contributor.name}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{contributor.percentage}%</p>
                        </div>
                        <p className="font-semibold text-gray-900 dark:text-white">{contributor.amount}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Revenue Trends</h3>
              <div className="space-y-3">
                {revenueAnalytics.by_time_period && Object.entries(revenueAnalytics.by_time_period).map(([period, amount]) => (
                  <div key={period} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{period}</span>
                    <span className="font-medium text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Geographic Distribution</h3>
              <div className="space-y-3">
                {revenueAnalytics.by_region && Object.entries(revenueAnalytics.by_region).map(([region, amount]) => (
                  <div key={region} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{region}</span>
                    <span className="font-medium text-gray-900 dark:text-white">${amount.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Analytics & Forecasting Component
const AnalyticsForecasting = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [roiAnalysis, setRoiAnalysis] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('performance');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const [performanceRes, roiRes] = await Promise.all([
        axios.get(`${API}/api/platform/analytics/performance?user_id=user_123`),
        axios.get(`${API}/api/platform/analytics/roi?user_id=user_123`)
      ]);

      if (performanceRes.data.success) setPerformanceMetrics(performanceRes.data.performance_metrics || {});
      if (roiRes.data.success) setRoiAnalysis(roiRes.data.roi_analysis || {});
    } catch (error) {
      handleApiError(error, 'fetchAnalyticsData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'performance', name: 'Performance', icon: '📊' },
    { id: 'forecasting', name: 'Forecasting', icon: '🔮' },
    { id: 'roi', name: 'ROI Analysis', icon: '💹' },
    { id: 'trends', name: 'Trends', icon: '📈' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics & Forecasting</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Advanced analytics and revenue forecasting</p>
        </div>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2">
          <span>📊</span>
          <span>Generate Report</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Streams</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{performanceMetrics.total_streams?.toLocaleString() || '2,456,789'}</p>
            </div>
            <span className="text-2xl">🎵</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Engagement Rate</p>
              <p className="text-2xl font-bold text-blue-600">{performanceMetrics.engagement_rate || '7.8'}%</p>
            </div>
            <span className="text-2xl">👍</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Views</p>
              <p className="text-2xl font-bold text-green-600">{performanceMetrics.total_views?.toLocaleString() || '5,678,901'}</p>
            </div>
            <span className="text-2xl">👁️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Downloads</p>
              <p className="text-2xl font-bold text-purple-600">{performanceMetrics.total_downloads?.toLocaleString() || '123,456'}</p>
            </div>
            <span className="text-2xl">⬇️</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'performance' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Assets</h3>
              <div className="space-y-4">
                {performanceMetrics.top_performing_assets?.slice(0, 5).map((asset, index) => (
                  <div key={asset.id || index} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{asset.title}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{asset.streams?.toLocaleString() || 0} streams</p>
                    </div>
                    <p className="font-semibold text-green-600">${(asset.revenue || 0).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Performance</h3>
              <div className="space-y-4">
                {performanceMetrics.top_platforms?.slice(0, 5).map((platform, index) => (
                  <div key={platform.name || index} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{platform.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{platform.streams?.toLocaleString() || 0} streams</p>
                    </div>
                    <p className="font-semibold text-blue-600">{platform.engagement_rate || 0}% engagement</p>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6 lg:col-span-2`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Audience Demographics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Age Groups</h4>
                  <div className="space-y-2">
                    {performanceMetrics.audience_demographics?.age_groups && Object.entries(performanceMetrics.audience_demographics.age_groups).map(([age, percentage]) => (
                      <div key={age} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{age}</span>
                        <span className="font-medium text-gray-900 dark:text-white">{percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Gender</h4>
                  <div className="space-y-2">
                    {performanceMetrics.audience_demographics?.gender && Object.entries(performanceMetrics.audience_demographics.gender).map(([gender, percentage]) => (
                      <div key={gender} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400 capitalize">{gender}</span>
                        <span className="font-medium text-gray-900 dark:text-white">{percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Top Countries</h4>
                  <div className="space-y-2">
                    {performanceMetrics.audience_demographics?.top_countries?.slice(0, 5).map((country, index) => (
                      <div key={country.country || index} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{country.country}</span>
                        <span className="font-medium text-gray-900 dark:text-white">{country.percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'forecasting' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Revenue Forecast</h3>
                <div className="flex space-x-2">
                  <select className={`px-3 py-2 border rounded-lg text-sm ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                    <option>Next 12 Months</option>
                    <option>Next 6 Months</option>
                    <option>Next Quarter</option>
                  </select>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 text-sm">
                    Generate Forecast
                  </button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">$425K</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Predicted Revenue (12M)</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">+28%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Expected Growth</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">92%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Confidence Level</p>
                </div>
              </div>

              <div className="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <div className="text-4xl mb-4">📈</div>
                <p className="text-gray-600 dark:text-gray-400">Forecast chart would appear here</p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">Interactive revenue projection visualization</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Growth Opportunities</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                    <p className="font-medium text-green-900 dark:text-green-100">TikTok Expansion</p>
                    <p className="text-sm text-green-700 dark:text-green-300">+45% potential revenue increase</p>
                  </div>
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <p className="font-medium text-blue-900 dark:text-blue-100">International Markets</p>
                    <p className="text-sm text-blue-700 dark:text-blue-300">+32% potential from EU/Asia</p>
                  </div>
                  <div className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                    <p className="font-medium text-purple-900 dark:text-purple-100">Podcast Platforms</p>
                    <p className="text-sm text-purple-700 dark:text-purple-300">+28% untapped revenue</p>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Risk Factors</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <p className="font-medium text-yellow-900 dark:text-yellow-100">Platform Algorithm Changes</p>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">Medium risk to organic reach</p>
                  </div>
                  <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <p className="font-medium text-red-900 dark:text-red-100">Market Saturation</p>
                    <p className="text-sm text-red-700 dark:text-red-300">High competition in key genres</p>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <p className="font-medium text-gray-900 dark:text-gray-100">Economic Factors</p>
                    <p className="text-sm text-gray-700 dark:text-gray-300">Low risk to entertainment spending</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'roi' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Overall ROI</h3>
              <div className="text-center py-6">
                <p className="text-4xl font-bold text-green-600 mb-2">{roiAnalysis.roi_percentage || '525.7'}%</p>
                <p className="text-gray-600 dark:text-gray-400">Return on Investment</p>
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Total Investment</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${roiAnalysis.total_investment?.toLocaleString() || '25,000'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Total Revenue</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${roiAnalysis.total_revenue?.toLocaleString() || '156,432'}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">ROI by Platform</h3>
              <div className="space-y-3">
                {roiAnalysis.by_platform && Object.entries(roiAnalysis.by_platform).map(([platform, data]) => (
                  <div key={platform} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{platform}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Investment: ${data.investment?.toLocaleString() || 0}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-green-600">{data.roi?.toFixed(1) || 0}%</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">${data.revenue?.toLocaleString() || 0}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6 lg:col-span-2`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">ROI Trends (Monthly)</h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                {roiAnalysis.monthly_trend?.map((month, index) => (
                  <div key={month.month || index} className="text-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400">{month.month}</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">{month.roi}%</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-green-800 to-green-600' : 'bg-gradient-to-r from-green-500 to-green-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Revenue Trend</h4>
                <p className="text-2xl font-bold">📈 +18.4%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-blue-800 to-blue-600' : 'bg-gradient-to-r from-blue-500 to-blue-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Engagement Trend</h4>
                <p className="text-2xl font-bold">📊 +12.7%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-purple-800 to-purple-600' : 'bg-gradient-to-r from-purple-500 to-purple-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Audience Growth</h4>
                <p className="text-2xl font-bold">👥 +8.9%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
              <div className={`${isDarkMode ? 'bg-gradient-to-r from-orange-800 to-orange-600' : 'bg-gradient-to-r from-orange-500 to-orange-400'} text-white rounded-lg p-4`}>
                <h4 className="font-semibold">Content Performance</h4>
                <p className="text-2xl font-bold">🎯 +15.2%</p>
                <p className="text-sm opacity-90">vs last month</p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Market Insights</h3>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">🎵 Audio Content Dominance</h4>
                  <p className="text-sm text-blue-700 dark:text-blue-300">Audio content shows 34% better performance on weekends and during evening hours (6-10 PM).</p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">📈 Q4 Revenue Spike</h4>
                  <p className="text-sm text-green-700 dark:text-green-300">Historical data shows Q4 typically brings 28% increase in streaming revenue due to holiday listening patterns.</p>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                  <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-2">🌟 Social Media Engagement</h4>
                  <p className="text-sm text-purple-700 dark:text-purple-300">TikTok campaigns show highest engagement rates at 9.8%, significantly outperforming other platforms.</p>
                </div>
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <h4 className="font-medium text-yellow-900 dark:text-yellow-100 mb-2">🎭 Genre Performance</h4>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">Hip-hop and electronic genres show strongest revenue growth, while pop maintains highest overall volume.</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComprehensivePlatform;