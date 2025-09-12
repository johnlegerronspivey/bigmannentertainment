import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || 'https://social-connect-148.preview.emergentagent.com';

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
  const [activeModule, setActiveModule] = useState('content-manager');
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

            {/* Module Content - For now showing main dashboard */}
            {activeModule === 'content-manager' && (
              <MainDashboard
                kpiData={kpiData}
                recentActivities={recentActivities}
                systemAlerts={systemAlerts}
              />
            )}
            {activeModule !== 'content-manager' && (
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 text-center">
                <div className="text-6xl mb-4">🚧</div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Module Under Development
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  The {activeModule.replace('-', ' ')} module is currently being implemented.
                  Check back soon for full functionality!
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ComprehensivePlatform;