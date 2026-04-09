import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { SocialMediaPhases5To10Dashboard } from './SocialMediaPhases5To10Components';
import { RealTimeRoyaltyDashboard } from './RealTimeRoyaltyComponents';
import { 
  AIRoyaltyForecasting,
  SmartContractBuilder,
  MultiCurrencyPayouts,
  PremiumDashboardOverview
} from './PremiumFeaturesComponents';
import { MLCIntegration } from './MLCIntegrationComponents';
import { MDEIntegration } from './MDEIntegrationComponents';
import { GS1AssetRegistry } from './GS1AssetRegistryComponents';
import PDOOHCampaignManager from './PDOOHCampaignManager';

const API = process.env.REACT_APP_BACKEND_URL;

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
const GlobalHeader = ({ user, notifications, onSearch, onNotificationClick, onUserMenuToggle, onMobileMenuToggle }) => {
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
          {/* Mobile Menu Button & Logo */}
          <div className="flex items-center space-x-4">
            {/* Mobile Menu Toggle */}
            <button
              onClick={onMobileMenuToggle}
              className={`lg:hidden p-2 rounded-md ${isDarkMode ? 'text-gray-400 hover:text-white hover:bg-gray-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'}`}
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
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
            
            {/* Environment Toggle - Hidden on small screens */}
            <div className="hidden sm:flex items-center space-x-2">
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
const LeftSidebar = ({ activeModule, onModuleChange, isCollapsed, onToggleCollapse, isMobileMenuOpen, onMobileMenuToggle }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  const modules = [
    { id: 'main-dashboard', name: 'Main Dashboard', icon: '🏠', badge: null },
    { id: 'content-manager', name: 'Content Manager', icon: '📁', badge: null },
    { id: 'distribution-tracker', name: 'Distribution Tracker', icon: '📡', badge: '32' },
    { id: 'royalty-engine', name: 'Royalty Engine', icon: '💰', badge: 'NEW' },
    { id: 'mlc-integration', name: 'MLC Integration', icon: '🏛️', badge: 'NEW' },
    { id: 'mde-integration', name: 'MDE Integration', icon: '🎵', badge: 'NEW' },
    { id: 'ai-forecasting', name: 'AI Forecasting', icon: '🤖', badge: 'PREMIUM' },
    { id: 'smart-contracts', name: 'Smart Contracts', icon: '📄', badge: 'PREMIUM' },
    { id: 'multi-currency', name: 'Multi-Currency Payouts', icon: '🌍', badge: 'PREMIUM' },
    { id: 'pdooh', name: 'pDOOH Campaigns', icon: '📺', badge: 'PREMIUM' },
    { id: 'compliance-center', name: 'Compliance Center', icon: '🛡️', badge: '2' },
    { id: 'analytics-forecasting', name: 'Analytics & Forecasting', icon: '📊', badge: null },
    { id: 'sponsorship-campaigns', name: 'Sponsorship & Campaigns', icon: '🤝', badge: null },
    { id: 'contributor-hub', name: 'Contributor Hub', icon: '👥', badge: null },
    { id: 'system-health', name: 'System Health & Logs', icon: '⚙️', badge: null },
    { id: 'dao-governance', name: 'DAO Governance', icon: '🧠', badge: '3' }
  ];

  return (
    <>
      {/* Mobile Sidebar Overlay */}
      <div className={`fixed inset-0 z-20 bg-black bg-opacity-50 lg:hidden ${isMobileMenuOpen ? 'block' : 'hidden'}`}
           onClick={onMobileMenuToggle}></div>
      
      {/* Sidebar */}
      <div className={`
        ${isCollapsed ? 'w-16' : 'w-64'} 
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        fixed lg:sticky top-16 left-0 z-30 lg:z-auto
        transition-all duration-300 transform lg:transform-none
        ${isDarkMode ? 'bg-gray-900 border-gray-700' : 'bg-gray-50 border-gray-200'} 
        border-r h-screen overflow-y-auto
      `}>
        {/* Collapse Button - Desktop only */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 hidden lg:block">
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

        {/* Mobile Close Button */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 lg:hidden">
          <button
            onClick={onMobileMenuToggle}
            className={`w-full flex items-center justify-between p-2 rounded-lg ${isDarkMode ? 'text-gray-400 hover:bg-gray-800 hover:text-white' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            <span className="font-medium">Navigation</span>
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation Modules */}
        <nav className="p-4 space-y-2">
          {modules.map((module) => (
            <button
              key={module.id}
              onClick={() => {
                onModuleChange(module.id);
                if (window.innerWidth < 1024) {
                  onMobileMenuToggle();
                }
              }}
              className={`w-full flex items-center ${isCollapsed && window.innerWidth >= 1024 ? 'justify-center' : 'justify-between'} p-3 rounded-lg text-left transition-colors ${
                activeModule === module.id
                  ? isDarkMode ? 'bg-blue-900 text-blue-100' : 'bg-blue-100 text-blue-900'
                  : isDarkMode ? 'text-gray-300 hover:bg-gray-800 hover:text-white' : 'text-gray-700 hover:bg-gray-200'
              }`}
              title={isCollapsed && window.innerWidth >= 1024 ? module.name : ''}
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg">{module.icon}</span>
                {(!isCollapsed || window.innerWidth < 1024) && (
                  <span className="font-medium">{module.name}</span>
                )}
              </div>
              {(!isCollapsed || window.innerWidth < 1024) && module.badge && (
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  module.badge === 'NEW' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : module.badge === 'PREMIUM'
                    ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white font-bold shadow-lg'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {module.badge}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>
    </>
  );
};

// KPI Snapshot Cards Component
const KPISnapshotCards = ({ kpiData, onCardClick }) => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');

  const kpis = [
    {
      id: 'assets-live',
      title: '🎬 Assets Live',
      value: kpiData?.assetsLive || '0',
      status: '✅',
      statusColor: 'text-green-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'platforms-connected',
      title: '🌐 Platforms Connected',
      value: kpiData?.platformsConnected || '0',
      status: '🔄',
      statusColor: 'text-blue-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'royalties-today',
      title: '💸 Royalties Today',
      value: kpiData?.royaltiesToday || '$0.00',
      status: '📈',
      statusColor: 'text-green-500',
      bgColor: isDarkMode ? 'bg-gray-800' : 'bg-white'
    },
    {
      id: 'pending-payouts',
      title: '⏳ Pending Payouts',
      value: kpiData?.pendingPayouts || '$0.00',
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
      value: kpiData?.forecastROI || '0%',
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [kpiData, setKpiData] = useState({});
  const [recentActivities, setRecentActivities] = useState([]);
  const [systemAlerts, setSystemAlerts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [user, setUser] = useState({ name: 'John LeGerron Spivey', email: 'owner@bigmannentertainment.com' });

  // Fetch real KPI data from backend
  useEffect(() => {
    const fetchKpiData = async () => {
      try {
        const [contentRes, complianceRes, campaignRes, contributorRes] = await Promise.allSettled([
          axios.get(`${API}/api/platform/content/stats?user_id=user_123`),
          axios.get(`${API}/api/platform/compliance/status?user_id=user_123`),
          axios.get(`${API}/api/platform/sponsorship/analytics?user_id=user_123`),
          axios.get(`${API}/api/platform/contributors/stats?user_id=user_123`),
        ]);
        const content = contentRes.status === 'fulfilled' ? contentRes.value?.data : {};
        const compliance = complianceRes.status === 'fulfilled' ? complianceRes.value?.data : {};
        const campaign = campaignRes.status === 'fulfilled' ? campaignRes.value?.data : {};
        const contributor = contributorRes.status === 'fulfilled' ? contributorRes.value?.data : {};

        const totalAssets = content?.stats?.total_assets || 0;
        const liveAssets = content?.stats?.by_status?.live || 0;
        const compScore = compliance?.overall_compliance?.score || 0;
        const compFlags = (compliance?.overall_compliance?.needs_attention || 0) + (compliance?.overall_compliance?.non_compliant || 0);
        const totalCampaigns = campaign?.analytics?.overview?.total_campaigns || 0;
        const totalEarned = contributor?.stats?.earnings?.total_earned || 0;
        const pendingEarnings = contributor?.stats?.earnings?.pending || 0;

        setKpiData({
          assetsLive: liveAssets.toLocaleString(),
          platformsConnected: totalCampaigns.toString(),
          royaltiesToday: `$${totalEarned.toLocaleString()}`,
          pendingPayouts: `$${pendingEarnings.toLocaleString()}`,
          complianceFlags: compFlags.toString(),
          forecastROI: `${compScore}%`
        });
      } catch (e) {
        console.error('KPI fetch error:', e);
        setKpiData({
          assetsLive: '0', platformsConnected: '0', royaltiesToday: '$0',
          pendingPayouts: '$0', complianceFlags: '0', forecastROI: '0%'
        });
      }
    };
    fetchKpiData();

    // Recent activities & alerts will be populated from real data as user navigates
    setRecentActivities([]);
    setSystemAlerts([]);
    setNotifications([]);
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

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Global Header */}
      <GlobalHeader
        user={user}
        notifications={notifications}
        onSearch={handleSearch}
        onNotificationClick={handleNotificationClick}
        onMobileMenuToggle={toggleMobileMenu}
      />

      <div className="flex">
        {/* Left Sidebar */}
        <LeftSidebar
          activeModule={activeModule}
          onModuleChange={handleModuleChange}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={toggleSidebar}
          isMobileMenuOpen={mobileMenuOpen}
          onMobileMenuToggle={toggleMobileMenu}
        />

        {/* Main Content */}
        <main className={`flex-1 p-4 lg:p-6 ${sidebarCollapsed ? 'lg:ml-0' : 'lg:ml-0'} transition-all duration-300`}>
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
            {activeModule === 'mlc-integration' && (
              <MLCIntegration />
            )}
            {activeModule === 'mde-integration' && (
              <MDEIntegration />
            )}
            {activeModule === 'ai-forecasting' && (
              <AIRoyaltyForecasting />
            )}
            {activeModule === 'smart-contracts' && (
              <SmartContractBuilder />
            )}
            {activeModule === 'multi-currency' && (
              <MultiCurrencyPayouts />
            )}
            {activeModule === 'pdooh' && (
              <PDOOHCampaignManager />
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
              <PremiumDashboardOverview />
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
    { id: 'gs1', name: 'GS1 Registry', icon: '🏷️' },
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
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.total_assets || '0'}</p>
            </div>
            <span className="text-2xl">📁</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.total_size || '0 B'}</p>
            </div>
            <span className="text-2xl">💾</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">This Month</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.this_month?.uploaded || '0'}</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Live Assets</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contentStats.by_status?.live || '0'}</p>
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

        {activeTab === 'gs1' && (
          <GS1AssetRegistry />
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
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.audio || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Video</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.video || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Image</span>
                  <span className="font-medium text-gray-900 dark:text-white">{contentStats.by_type?.image || '0'}</span>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Content by Status</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Live</span>
                  <span className="font-medium text-green-600">{contentStats.by_status?.live || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Pending Review</span>
                  <span className="font-medium text-yellow-600">{contentStats.by_status?.pending_review || '0'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Draft</span>
                  <span className="font-medium text-gray-600">{contentStats.by_status?.draft || '0'}</span>
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
    { id: 'gs1', name: 'GS1 Digital Links', icon: '🔗' },
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
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.total_jobs || '0'}</p>
            </div>
            <span className="text-2xl">📤</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Jobs</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.active_jobs || '0'}</p>
            </div>
            <span className="text-2xl">🔄</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">{analytics.success_rate || '0'}%</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Avg. Delivery Time</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.average_delivery_time || '0'}h</p>
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

        {activeTab === 'gs1' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <span className="mr-2">🔗</span>
                GS1 Digital Links for Distribution
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Generate GS1 Digital Links and QR codes for your assets to enable direct-to-consumer engagement and licensing integration.
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className={`${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'} border rounded-lg p-4`}>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Digital Link Benefits</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-center"><span className="mr-2">✅</span>Direct consumer engagement</li>
                    <li className="flex items-center"><span className="mr-2">✅</span>Royalty tracking integration</li>
                    <li className="flex items-center"><span className="mr-2">✅</span>Global interoperability</li>
                    <li className="flex items-center"><span className="mr-2">✅</span>Compliance with GS1 standards</li>
                  </ul>
                </div>
                
                <div className={`${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'} border rounded-lg p-4`}>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Distribution Integration</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li className="flex items-center"><span className="mr-2">🎵</span>Music metadata with ISRC</li>
                    <li className="flex items-center"><span className="mr-2">🎬</span>Video content with ISAN</li>
                    <li className="flex items-center"><span className="mr-2">🖼️</span>Image assets with licensing</li>
                    <li className="flex items-center"><span className="mr-2">👕</span>Merchandise tracking</li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 text-center">
                <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
                  🚀 Access Full GS1 Registry
                </button>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Available in Content Manager → GS1 Registry tab
                </p>
              </div>
            </div>
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
                  {['Music Data Exchange (MDE)', 'Mechanical Licensing Collective (MLC)', 'Spotify', 'Apple Music', 'YouTube', 'Instagram', 'TikTok', 'Facebook', 'Amazon Music', 'Tidal', 'Pandora'].map((platform) => (
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
              <p className="text-2xl font-bold text-gray-900 dark:text-white">${revenueAnalytics.total_revenue?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">💰</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending Payouts</p>
              <p className="text-2xl font-bold text-yellow-600">$0</p>
            </div>
            <span className="text-2xl">⏳</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Growth</p>
              <p className="text-2xl font-bold text-green-600">{revenueAnalytics.growth_rate ?? 0}%</p>
            </div>
            <span className="text-2xl">📈</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Contributors</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{revenueAnalytics.contributors || '0'}</p>
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
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-2">$0</p>
              </div>
              <div className={`${isDarkMode ? 'bg-blue-800 border-blue-700' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">Scheduled Payouts</h3>
                <p className="text-blue-700 dark:text-blue-300 text-sm mt-1">Bank Transfers & ACH</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-2">$0</p>
              </div>
              <div className={`${isDarkMode ? 'bg-yellow-800 border-yellow-700' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">Pending Review</h3>
                <p className="text-yellow-700 dark:text-yellow-300 text-sm mt-1">Manual Approval Required</p>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100 mt-2">$0</p>
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
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{performanceMetrics.total_streams?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">🎵</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Engagement Rate</p>
              <p className="text-2xl font-bold text-blue-600">{performanceMetrics.engagement_rate ?? 0}%</p>
            </div>
            <span className="text-2xl">👍</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Views</p>
              <p className="text-2xl font-bold text-green-600">{performanceMetrics.total_views?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">👁️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Downloads</p>
              <p className="text-2xl font-bold text-purple-600">{performanceMetrics.total_downloads?.toLocaleString() || '0'}</p>
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
                      <p className="text-sm text-gray-600 dark:text-gray-400">{asset.events?.toLocaleString() || asset.streams?.toLocaleString() || 0} events</p>
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
                      <p className="text-sm text-gray-600 dark:text-gray-400">{platform.events?.toLocaleString() || platform.streams?.toLocaleString() || 0} events</p>
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
                <p className="text-4xl font-bold text-green-600 mb-2">{roiAnalysis.roi_percentage ?? 0}%</p>
                <p className="text-gray-600 dark:text-gray-400">Return on Investment</p>
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Total Investment</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${roiAnalysis.total_investment?.toLocaleString() || '0'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Total Revenue</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${roiAnalysis.total_revenue?.toLocaleString() || '0'}</p>
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

// PHASE 4: ADVANCED FEATURES MODULES

// Compliance Center Component
const ComplianceCenter = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [complianceStatus, setComplianceStatus] = useState({});
  const [complianceAlerts, setComplianceAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    setLoading(true);
    try {
      const [statusRes, alertsRes] = await Promise.all([
        axios.get(`${API}/api/platform/compliance/status?user_id=user_123`),
        axios.get(`${API}/api/platform/compliance/alerts?user_id=user_123`)
      ]);

      if (statusRes.data.success) setComplianceStatus(statusRes.data.overall_compliance || {});
      if (alertsRes.data.success) setComplianceAlerts(alertsRes.data.alerts || []);
    } catch (error) {
      handleApiError(error, 'fetchComplianceData');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: '🛡️' },
    { id: 'alerts', name: 'Alerts', icon: '⚠️' },
    { id: 'rights', name: 'Rights Management', icon: '📜' },
    { id: 'reports', name: 'Reports', icon: '📊' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Compliance Center</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Regulatory compliance and rights management</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
          <span>🔍</span>
          <span>Run Compliance Check</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Compliance Score</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{complianceStatus.score || '0'}%</p>
            </div>
            <span className="text-2xl">🛡️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Compliant Assets</p>
              <p className="text-2xl font-bold text-green-600">{complianceStatus.compliant_assets || '0'}</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Needs Attention</p>
              <p className="text-2xl font-bold text-yellow-600">{complianceStatus.needs_attention || '0'}</p>
            </div>
            <span className="text-2xl">⚠️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Non-Compliant</p>
              <p className="text-2xl font-bold text-red-600">{complianceStatus.non_compliant || '0'}</p>
            </div>
            <span className="text-2xl">❌</span>
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
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance by Type</h3>
              <div className="space-y-4">
                {[
                  { type: 'Copyright', score: 95.2, status: 'compliant' },
                  { type: 'GDPR', score: 78.9, status: 'needs_attention' },
                  { type: 'Territorial Rights', score: 92.1, status: 'compliant' },
                  { type: 'Age Rating', score: 88.7, status: 'compliant' }
                ].map((item, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">{item.type}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{item.score}%</span>
                      <span className={`w-3 h-3 rounded-full ${
                        item.status === 'compliant' ? 'bg-green-500' : 
                        item.status === 'needs_attention' ? 'bg-yellow-500' : 'bg-red-500'
                      }`}></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compliance by Territory</h3>
              <div className="space-y-4">
                {[
                  { territory: 'United States', score: 92.3, assets: 567 },
                  { territory: 'European Union', score: 76.8, assets: 234 },
                  { territory: 'United Kingdom', score: 89.4, assets: 189 },
                  { territory: 'Canada', score: 94.1, assets: 156 },
                  { territory: 'Australia', score: 91.7, assets: 102 }
                ].map((item, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <div>
                      <p className="text-gray-900 dark:text-white font-medium">{item.territory}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{item.assets} assets</p>
                    </div>
                    <span className="text-sm font-medium text-gray-900 dark:text-white">{item.score}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {complianceAlerts.length > 0 ? complianceAlerts.map((alert, index) => (
              <div key={alert.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{alert.title}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(alert.risk_level)}`}>
                        {alert.risk_level}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">{alert.message}</p>
                    {alert.territory && (
                      <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">Territory: {alert.territory}</p>
                    )}
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Review</button>
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">Resolve</button>
                  </div>
                </div>
                {alert.deadline && (
                  <div className="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-600">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Deadline: {new Date(alert.deadline).toLocaleDateString()}
                    </span>
                    <span className={`text-sm font-medium ${
                      new Date(alert.deadline) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) 
                        ? 'text-red-600' : 'text-gray-600 dark:text-gray-400'
                    }`}>
                      {Math.ceil((new Date(alert.deadline) - new Date()) / (1000 * 60 * 60 * 24))} days remaining
                    </span>
                  </div>
                )}
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">✅</div>
                <p className="text-gray-600 dark:text-gray-400">No compliance alerts. Great job!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'rights' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Rights Information</h3>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Add Rights Info
                </button>
              </div>
              
              <div className="space-y-4">
                {[
                  { 
                    asset: 'Summer Vibes Instrumental',
                    owner: 'Big Mann Entertainment',
                    year: 2024,
                    territories: ['US', 'CA', 'UK', 'EU', 'AU'],
                    restrictions: ['No sync without license', 'Attribution required']
                  },
                  { 
                    asset: 'Midnight Dreams',
                    owner: 'Big Mann Entertainment',
                    year: 2024,
                    territories: ['US', 'CA', 'UK'],
                    restrictions: ['Commercial use only']
                  }
                ].map((rights, index) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">{rights.asset}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">© {rights.year} {rights.owner}</p>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">✏️</button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Territories</p>
                        <div className="flex flex-wrap gap-1">
                          {rights.territories.map((territory) => (
                            <span key={territory} className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 text-xs rounded">
                              {territory}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Restrictions</p>
                        <div className="space-y-1">
                          {rights.restrictions.map((restriction, idx) => (
                            <p key={idx} className="text-xs text-gray-600 dark:text-gray-400">• {restriction}</p>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Generate Compliance Report</h3>
                <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
                  Generate Report
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date Range</label>
                  <div className="space-y-2">
                    <input type="date" className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} />
                    <input type="date" className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`} />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Compliance Types</label>
                  <div className="space-y-2">
                    {['Copyright', 'GDPR', 'Territorial Rights', 'Age Rating'].map((type) => (
                      <label key={type} className="flex items-center space-x-2">
                        <input type="checkbox" className="rounded" defaultChecked />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Reports</h3>
              <div className="space-y-4">
                {[
                  { name: 'Q4 Compliance Report', date: '2024-01-15', status: 'completed', type: 'PDF' },
                  { name: 'GDPR Audit Report', date: '2024-01-10', status: 'completed', type: 'PDF' },
                  { name: 'Rights Review Report', date: '2024-01-05', status: 'processing', type: 'PDF' }
                ].map((report, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{report.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{report.date} • {report.type}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        report.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                      }`}>
                        {report.status}
                      </span>
                      {report.status === 'completed' && (
                        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Download</button>
                      )}
                    </div>
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

// Sponsorship & Campaigns Component
const SponsorshipCampaigns = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [campaigns, setCampaigns] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('campaigns');

  useEffect(() => {
    fetchSponsorshipData();
  }, []);

  const fetchSponsorshipData = async () => {
    setLoading(true);
    try {
      const [campaignsRes, opportunitiesRes, analyticsRes] = await Promise.all([
        axios.get(`${API}/api/platform/sponsorship/campaigns?user_id=user_123`),
        axios.get(`${API}/api/platform/sponsorship/opportunities?user_id=user_123`),
        axios.get(`${API}/api/platform/sponsorship/analytics?user_id=user_123`)
      ]);

      if (campaignsRes.data.success) setCampaigns(campaignsRes.data.campaigns || []);
      if (opportunitiesRes.data.success) setOpportunities(opportunitiesRes.data.opportunities || []);
      if (analyticsRes.data.success) setAnalytics(analyticsRes.data.analytics || {});
    } catch (error) {
      handleApiError(error, 'fetchSponsorshipData');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'completed': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'paused': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'cancelled': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'campaigns', name: 'My Campaigns', icon: '🎯' },
    { id: 'opportunities', name: 'Opportunities', icon: '💼' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
    { id: 'create', name: 'Create Campaign', icon: '➕' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Sponsorship & Campaigns</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Manage sponsorship deals and marketing campaigns</p>
        </div>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2">
          <span>🚀</span>
          <span>Launch Campaign</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Campaigns</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.overview?.total_campaigns || '0'}</p>
            </div>
            <span className="text-2xl">🎯</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Campaigns</p>
              <p className="text-2xl font-bold text-green-600">{analytics.overview?.active_campaigns || '0'}</p>
            </div>
            <span className="text-2xl">🟢</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Spend</p>
              <p className="text-2xl font-bold text-blue-600">${analytics.overview?.total_spent?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">💰</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">ROI</p>
              <p className="text-2xl font-bold text-purple-600">{analytics.overview?.roi || '0'}%</p>
            </div>
            <span className="text-2xl">📈</span>
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
        {activeTab === 'campaigns' && (
          <div className="space-y-4">
            {campaigns.length > 0 ? campaigns.map((campaign, index) => (
              <div key={campaign.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{campaign.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(campaign.status)}`}>
                        {campaign.status}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{campaign.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Brand: {campaign.brand_name}</span>
                      <span>Type: {campaign.campaign_type?.replace('_', ' ')}</span>
                      <span>Budget: ${campaign.budget_total?.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View</button>
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">Edit</button>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Budget Used</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full" 
                          style={{width: `${((campaign.budget_spent || 0) / (campaign.budget_total || 1)) * 100}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        ${(campaign.budget_spent || 0).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Start Date</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {campaign.start_date ? new Date(campaign.start_date).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">End Date</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {campaign.end_date ? new Date(campaign.end_date).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Platforms</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {campaign.targeting?.platforms?.length || 0} platforms
                    </p>
                  </div>
                </div>
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🎯</div>
                <p className="text-gray-600 dark:text-gray-400">No campaigns found. Create your first campaign!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'opportunities' && (
          <div className="space-y-4">
            {opportunities.length > 0 ? opportunities.map((opportunity, index) => (
              <div key={opportunity.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{opportunity.title}</h3>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs rounded-full">
                        {opportunity.industry}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{opportunity.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Brand: {opportunity.brand_name}</span>
                      <span>Budget: ${opportunity.budget_range?.min?.toLocaleString()} - ${opportunity.budget_range?.max?.toLocaleString()}</span>
                      <span>Deadline: {new Date(opportunity.deadline).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 ml-4">
                    Apply
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Requirements</p>
                    <div className="space-y-1">
                      {opportunity.requirements?.map((req, idx) => (
                        <p key={idx} className="text-sm text-gray-600 dark:text-gray-400">• {req}</p>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Contact</p>
                    <div className="space-y-1">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Email: {opportunity.contact_info?.email}</p>
                      {opportunity.contact_info?.phone && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">Phone: {opportunity.contact_info.phone}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">💼</div>
                <p className="text-gray-600 dark:text-gray-400">No opportunities available at the moment.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performing Campaigns</h3>
              <div className="space-y-4">
                {analytics.top_performing_campaigns?.slice(0, 5).map((campaign, index) => (
                  <div key={campaign.id || index} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{campaign.title}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{campaign.impressions?.toLocaleString() || 0} impressions</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-green-600">{campaign.roi}% ROI</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{campaign.engagement_rate}% engagement</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Platform Performance</h3>
              <div className="space-y-4">
                {analytics.by_platform && Object.entries(analytics.by_platform).map(([platform, data]) => (
                  <div key={platform} className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white capitalize">{platform}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{data.campaigns} campaigns</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-blue-600">{data.engagement_rate}% engagement</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">${data.cost_per_impression} CPI</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6 lg:col-span-2`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">ROI Trends (Monthly)</h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                {analytics.monthly_trends?.map((month, index) => (
                  <div key={month.month || index} className="text-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400">{month.month}</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">{month.roi}%</p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">${month.spend?.toLocaleString()}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Create New Campaign</h3>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Campaign Name</label>
                  <input 
                    type="text" 
                    placeholder="Enter campaign name..."
                    className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Brand Name</label>
                  <input 
                    type="text" 
                    placeholder="Enter brand name..."
                    className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                <textarea 
                  rows={3}
                  placeholder="Describe your campaign..."
                  className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Campaign Type</label>
                  <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                    <option>Brand Sponsorship</option>
                    <option>Product Placement</option>
                    <option>Influencer Campaign</option>
                    <option>Content Partnership</option>
                    <option>Event Sponsorship</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Budget ($)</label>
                  <input 
                    type="number" 
                    placeholder="0"
                    className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Budget Type</label>
                  <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                    <option>Fixed</option>
                    <option>Performance Based</option>
                    <option>Hybrid</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Start Date</label>
                  <input 
                    type="date" 
                    className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">End Date</label>
                  <input 
                    type="date" 
                    className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Target Platforms</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['Instagram', 'TikTok', 'YouTube', 'Facebook', 'Twitter', 'LinkedIn', 'Snapchat', 'Pinterest'].map((platform) => (
                    <label key={platform} className="flex items-center space-x-2">
                      <input type="checkbox" className="rounded" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{platform}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex space-x-4">
                <button className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700">
                  Create Campaign
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

// Contributor Hub Component
const ContributorHub = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [contributors, setContributors] = useState([]);
  const [collaborationRequests, setCollaborationRequests] = useState([]);
  const [collaborations, setCollaborations] = useState([]);
  const [contributorStats, setContributorStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('discover');

  useEffect(() => {
    fetchContributorData();
  }, []);

  const fetchContributorData = async () => {
    setLoading(true);
    try {
      const [contributorsRes, requestsRes, collaborationsRes, statsRes] = await Promise.all([
        axios.get(`${API}/api/platform/contributors/search?user_id=user_123`),
        axios.get(`${API}/api/platform/contributors/requests?user_id=user_123`),
        axios.get(`${API}/api/platform/contributors/collaborations?user_id=user_123`),
        axios.get(`${API}/api/platform/contributors/stats?user_id=user_123`)
      ]);

      if (contributorsRes.data.success) setContributors(contributorsRes.data.contributors || []);
      if (requestsRes.data.success) setCollaborationRequests(requestsRes.data.requests || []);
      if (collaborationsRes.data.success) setCollaborations(collaborationsRes.data.collaborations || []);
      if (statsRes.data.success) setContributorStats(statsRes.data.stats || {});
    } catch (error) {
      handleApiError(error, 'fetchContributorData');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'discover', name: 'Discover', icon: '🔍' },
    { id: 'requests', name: 'Requests', icon: '📩' },
    { id: 'collaborations', name: 'Active Collaborations', icon: '🤝' },
    { id: 'payments', name: 'Payments', icon: '💳' },
    { id: 'profile', name: 'My Profile', icon: '👤' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Contributor Hub</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Connect and collaborate with creators</p>
        </div>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2">
          <span>➕</span>
          <span>Send Request</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Collaborations</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{contributorStats.profile?.total_collaborations || '0'}</p>
            </div>
            <span className="text-2xl">🤝</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">{contributorStats.profile?.success_rate || '0'}%</p>
            </div>
            <span className="text-2xl">✅</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Earned</p>
              <p className="text-2xl font-bold text-blue-600">${contributorStats.earnings?.total_earned?.toLocaleString() || '0'}</p>
            </div>
            <span className="text-2xl">💰</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Average Rating</p>
              <p className="text-2xl font-bold text-yellow-600">{contributorStats.profile?.average_rating || '0'}⭐</p>
            </div>
            <span className="text-2xl">⭐</span>
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
              {tab.id === 'requests' && collaborationRequests.length > 0 && (
                <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 ml-1">
                  {collaborationRequests.filter(r => r.status === 'pending').length}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {activeTab === 'discover' && (
          <div className="space-y-4">
            {/* Search and Filters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <input
                type="text"
                placeholder="Search contributors..."
                className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              />
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Roles</option>
                <option>Producer</option>
                <option>Vocalist</option>
                <option>Instrumentalist</option>
                <option>Songwriter</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Genres</option>
                <option>Hip-Hop</option>
                <option>Pop</option>
                <option>R&B</option>
                <option>Electronic</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>Any Budget</option>
                <option>Under $500</option>
                <option>$500 - $1000</option>
                <option>$1000+</option>
              </select>
            </div>

            {/* Contributors Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {contributors.length > 0 ? contributors.map((contributor, index) => (
                <div key={contributor.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                      {contributor.stage_name ? contributor.stage_name.charAt(0) : 'C'}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{contributor.stage_name || 'Unknown'}</h3>
                      <div className="flex items-center space-x-2">
                        <span className="text-yellow-500">⭐</span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">{contributor.rating || '0.0'}</span>
                        <span className="text-sm text-gray-500">({contributor.total_collaborations || 0} collaborations)</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{contributor.bio || 'No bio available'}</p>
                  
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Roles</p>
                    <div className="flex flex-wrap gap-1">
                      {contributor.roles?.map((role, idx) => (
                        <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 text-xs rounded">
                          {role}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Skills</p>
                    <div className="flex flex-wrap gap-1">
                      {contributor.skills?.slice(0, 3).map((skill, idx) => (
                        <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs rounded">
                          {skill}
                        </span>
                      ))}
                      {contributor.skills?.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200 text-xs rounded">
                          +{contributor.skills.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <div>
                      {contributor.hourly_rate && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">${contributor.hourly_rate}/hr</p>
                      )}
                      <p className="text-xs text-gray-500">{contributor.location || 'Location not specified'}</p>
                    </div>
                    <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                      Contact
                    </button>
                  </div>
                </div>
              )) : (
                <div className="col-span-full text-center py-8">
                  <div className="text-4xl mb-4">👥</div>
                  <p className="text-gray-600 dark:text-gray-400">No contributors found. Try adjusting your search filters.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'requests' && (
          <div className="space-y-4">
            {collaborationRequests.length > 0 ? collaborationRequests.map((request, index) => (
              <div key={request.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{request.project_title}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        request.status === 'pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        request.status === 'accepted' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        request.status === 'completed' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}>
                        {request.status}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{request.project_description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Roles: {request.required_roles?.join(', ')}</span>
                      {request.budget_range && (
                        <span>Budget: ${request.budget_range.min} - ${request.budget_range.max}</span>
                      )}
                      <span>Timeline: {request.timeline || 'Not specified'}</span>
                    </div>
                  </div>
                  {request.status === 'pending' && (
                    <div className="flex space-x-2 ml-4">
                      <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Accept
                      </button>
                      <button className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700">
                        Decline
                      </button>
                    </div>
                  )}
                </div>
                
                {request.message && (
                  <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <p className="text-sm text-gray-700 dark:text-gray-300">"{request.message}"</p>
                  </div>
                )}
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📩</div>
                <p className="text-gray-600 dark:text-gray-400">No collaboration requests at the moment.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'collaborations' && (
          <div className="space-y-4">
            {collaborations.length > 0 ? collaborations.map((collaboration, index) => (
              <div key={collaboration.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{collaboration.project_title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {collaboration.participants?.length || 0} participants • Started {collaboration.start_date ? new Date(collaboration.start_date).toLocaleDateString() : 'Recently'}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    collaboration.status === 'in_progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                    collaboration.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                  }`}>
                    {collaboration.status?.replace('_', ' ')}
                  </span>
                </div>
                
                {collaboration.milestones && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Milestones</h4>
                    <div className="space-y-2">
                      {collaboration.milestones.map((milestone, idx) => (
                        <div key={idx} className="flex items-center space-x-3">
                          <span className={`w-4 h-4 rounded-full flex-shrink-0 ${
                            milestone.status === 'completed' ? 'bg-green-500' :
                            milestone.status === 'in_progress' ? 'bg-blue-500' :
                            'bg-gray-300 dark:bg-gray-600'
                          }`}></span>
                          <span className="text-sm text-gray-700 dark:text-gray-300">{milestone.title}</span>
                          <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">
                            {milestone.due_date || milestone.date}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Budget: ${collaboration.budget_total?.toLocaleString() || '0'}
                  </div>
                  <div className="flex space-x-2">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View Details</button>
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">Message</button>
                  </div>
                </div>
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🤝</div>
                <p className="text-gray-600 dark:text-gray-400">No active collaborations. Start your first collaboration!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'payments' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`${isDarkMode ? 'bg-green-800 border-green-700' : 'bg-green-50 border-green-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-green-900 dark:text-green-100">Total Earned</h3>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-2">
                  ${contributorStats.earnings?.total_earned?.toLocaleString() || '0'}
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-blue-800 border-blue-700' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">This Month</h3>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-2">
                  ${contributorStats.earnings?.this_month?.toLocaleString() || '1,850'}
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-yellow-800 border-yellow-700' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">Pending</h3>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100 mt-2">
                  ${contributorStats.earnings?.pending?.toLocaleString() || '650'}
                </p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Payment History</h3>
              <div className="space-y-4">
                {[
                  { project: 'Pop Single Vocals', amount: 480.00, date: '2024-01-15', status: 'Paid', method: 'PayPal' },
                  { project: 'Hip-Hop Beat Production', amount: 650.00, date: '2024-01-10', status: 'Processing', method: 'Bank Transfer' },
                  { project: 'Acoustic Guitar Session', amount: 150.00, date: '2024-01-05', status: 'Paid', method: 'Crypto' }
                ].map((payment, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{payment.project}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{payment.date} • {payment.method}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 dark:text-white">${payment.amount}</p>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        payment.status === 'Paid' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
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

        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Profile Statistics</h3>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                  Edit Profile
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Performance Metrics</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Success Rate</span>
                      <span className="font-medium text-green-600">{contributorStats.profile?.success_rate || '0'}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Response Rate</span>
                      <span className="font-medium text-blue-600">{contributorStats.profile?.response_rate || '98.5'}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Avg Response Time</span>
                      <span className="font-medium text-gray-900 dark:text-white">{contributorStats.profile?.average_response_time || '2.3 hours'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Total Reviews</span>
                      <span className="font-medium text-gray-900 dark:text-white">{contributorStats.profile?.total_reviews || '12'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Skills Performance</h4>
                  <div className="space-y-3">
                    {contributorStats.skills_performance?.skill_ratings && Object.entries(contributorStats.skills_performance.skill_ratings).map(([skill, rating]) => (
                      <div key={skill} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">{skill}</span>
                        <div className="flex items-center space-x-1">
                          <span className="text-yellow-500">⭐</span>
                          <span className="font-medium text-gray-900 dark:text-white">{rating}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Achievements</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { title: 'Early Member', description: 'Joined within first 100 users', icon: '🏆' },
                  { title: 'Top Collaborator', description: '90%+ success rate', icon: '⭐' },
                  { title: 'Fast Responder', description: 'Avg response under 4 hours', icon: '⚡' },
                  { title: 'Highly Rated', description: '4.5+ star average', icon: '🌟' }
                ].map((achievement, index) => (
                  <div key={index} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl mb-2">{achievement.icon}</div>
                    <h4 className="font-medium text-gray-900 dark:text-white text-sm">{achievement.title}</h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{achievement.description}</p>
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

// System Health & Logs Component
const SystemHealth = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [systemHealth, setSystemHealth] = useState({});
  const [systemLogs, setSystemLogs] = useState([]);
  const [systemStats, setSystemStats] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchSystemData();
  }, []);

  const fetchSystemData = async () => {
    setLoading(true);
    try {
      const [healthRes, logsRes, statsRes, alertsRes] = await Promise.all([
        axios.get(`${API}/api/platform/system/health`),
        axios.get(`${API}/api/platform/system/logs?limit=50`),
        axios.get(`${API}/api/platform/system/stats`),
        axios.get(`${API}/api/platform/system/alerts`)
      ]);

      if (healthRes.data.success) setSystemHealth(healthRes.data || {});
      if (logsRes.data.success) setSystemLogs(logsRes.data.logs || []);
      if (statsRes.data.success) setSystemStats(statsRes.data.stats || {});
      if (alertsRes.data.success) setAlerts(alertsRes.data.alerts || []);
    } catch (error) {
      handleApiError(error, 'fetchSystemData');
    } finally {
      setLoading(false);  
    }
  };

  const getHealthColor = (status) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'critical': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'down': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'error': return 'text-red-600 dark:text-red-400';
      case 'warning': return 'text-yellow-600 dark:text-yellow-400';
      case 'info': return 'text-blue-600 dark:text-blue-400';
      case 'debug': return 'text-gray-600 dark:text-gray-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const tabs = [
    { id: 'overview', name: 'System Overview', icon: '🏥' },
    { id: 'components', name: 'Components', icon: '⚙️' },
    { id: 'logs', name: 'Logs', icon: '📋' },
    { id: 'alerts', name: 'Alerts', icon: '🚨' },
    { id: 'metrics', name: 'Metrics', icon: '📊' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">System Health & Logs</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Monitor system performance and logs</p>
        </div>
        <div className="flex space-x-2">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2">
            <span>🔄</span>
            <span>Refresh</span>
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2">
            <span>📥</span>
            <span>Export Logs</span>
          </button>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Overall Status</p>
              <p className="text-2xl font-bold text-green-600">{systemHealth.overall_status || 'Healthy'}</p>
            </div>
            <span className="text-2xl">💚</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Uptime</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{systemStats.uptime?.human_readable || '14d 6h'}</p>
            </div>
            <span className="text-2xl">⏱️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Error Rate</p>
              <p className="text-2xl font-bold text-blue-600">{(systemStats.errors?.error_rate || 0.05).toFixed(2)}%</p>
            </div>
            <span className="text-2xl">📊</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Alerts</p>
              <p className="text-2xl font-bold text-yellow-600">{alerts.filter(a => !a.resolved).length}</p>
            </div>
            <span className="text-2xl">🚨</span>
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
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Performance</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">CPU Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: `${systemStats.resources?.cpu_usage || 34.5}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.cpu_usage || 34.5}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">Memory Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: `${systemStats.resources?.memory_usage || 67.8}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.memory_usage || 67.8}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">Disk Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-yellow-600 h-2 rounded-full" style={{width: `${systemStats.resources?.disk_usage || 45.2}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.disk_usage || 45.2}%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">Network Usage</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full" style={{width: `${systemStats.resources?.network_usage || 23.4}%`}}></div>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{systemStats.resources?.network_usage || 23.4}%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Request Statistics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Today</span>
                    <span className="font-medium text-gray-900 dark:text-white">{systemStats.requests?.total_today?.toLocaleString() || '45,678'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">This Hour</span>
                    <span className="font-medium text-gray-900 dark:text-white">{systemStats.requests?.total_this_hour?.toLocaleString() || '3,456'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Avg Response Time</span>
                    <span className="font-medium text-gray-900 dark:text-white">{systemStats.performance?.average_response_time || 245.6}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Error Count</span>
                    <span className="font-medium text-red-600">{systemStats.errors?.total_today || 23}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'components' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemHealth.components?.map((component, index) => (
              <div key={component.component || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-gray-900 dark:text-white">{component.component?.replace('_', ' ') || 'Unknown Component'}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getHealthColor(component.status)}`}>
                    {component.status}
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Response Time</span>
                    <span className="text-gray-900 dark:text-white">{component.response_time?.toFixed(1) || 0}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Last Check</span>
                    <span className="text-gray-900 dark:text-white">
                      {component.last_check ? new Date(component.last_check).toLocaleTimeString() : 'Never'}
                    </span>
                  </div>
                  {component.error_message && (
                    <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-xs text-red-700 dark:text-red-300">
                      {component.error_message}
                    </div>
                  )}
                </div>
              </div>
            )) || (
              <div className="col-span-full text-center py-8">
                <div className="text-4xl mb-4">⚙️</div>
                <p className="text-gray-600 dark:text-gray-400">Loading system components...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-4">
            {/* Log Filters */}
            <div className="flex flex-wrap gap-4">
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Levels</option>
                <option>Error</option>
                <option>Warning</option>
                <option>Info</option>
                <option>Debug</option>
              </select>
              <select className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                <option>All Components</option>
                <option>API Server</option>
                <option>Database</option>
                <option>Storage</option>
                <option>Queue</option>
              </select>
              <input
                type="text"
                placeholder="Search logs..."
                className={`px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
              />
            </div>

            {/* Logs List */}
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg`}>
              <div className="max-h-96 overflow-y-auto">
                {systemLogs.length > 0 ? systemLogs.map((log, index) => (
                  <div key={log.id || index} className="border-b border-gray-200 dark:border-gray-700 last:border-b-0 p-4">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <span className={`text-sm font-mono ${getLogLevelColor(log.level)}`}>
                          {(log.level || 'INFO').toUpperCase()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900 dark:text-white">{log.message || 'No message'}</p>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500 dark:text-gray-400">
                          <span>{log.component || 'unknown'}</span>
                          <span>{log.timestamp ? new Date(log.timestamp).toLocaleString() : 'No timestamp'}</span>
                          {log.user_id && <span>User: {log.user_id}</span>}
                          {log.request_id && <span>Request: {log.request_id}</span>}
                        </div>
                      </div>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">📋</div>
                    <p className="text-gray-600 dark:text-gray-400">No logs available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {alerts.length > 0 ? alerts.map((alert, index) => (
              <div key={alert.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{alert.title}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        alert.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                        alert.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                        alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      }`}>
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400">{alert.message}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                      Component: {alert.component} • {alert.triggered_at ? new Date(alert.triggered_at).toLocaleString() : 'Recently'}
                    </p>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    {!alert.acknowledged && (
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">Acknowledge</button>
                    )}
                    {!alert.resolved && (
                      <button className="text-green-600 hover:text-green-700 text-sm font-medium">Resolve</button>
                    )}
                  </div>
                </div>
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">✅</div>
                <p className="text-gray-600 dark:text-gray-400">No active alerts. System is running smoothly!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Database Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Active Connections</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.database?.active_connections || 15}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Queries/Second</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.database?.queries_per_second || 234.5}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Slow Queries</span>
                  <span className="font-medium text-yellow-600">{systemStats.database?.slow_queries || 3}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Max Connections</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.database?.max_connections || 100}</span>
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Cache Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Hit Rate</span>
                  <span className="font-medium text-green-600">{systemStats.cache?.hit_rate || 89.4}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Miss Rate</span>
                  <span className="font-medium text-red-600">{systemStats.cache?.miss_rate || 10.6}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Total Keys</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.cache?.total_keys?.toLocaleString() || '12,456'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Memory Usage</span>
                  <span className="font-medium text-gray-900 dark:text-white">{systemStats.cache?.memory_usage || '45.2 MB'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// DAO Governance Component
const DAOGovernance = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [proposals, setProposals] = useState([]);
  const [daoMetrics, setDaoMetrics] = useState({});
  const [memberProfile, setMemberProfile] = useState({});
  const [treasury, setTreasury] = useState({});
  const [blockchainStatus, setBlockchainStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('proposals');

  useEffect(() => {
    fetchDaoData();
    fetchBlockchainStatus();
  }, []);

  const fetchDaoData = async () => {
    setLoading(true);
    try {
      const [proposalsRes, metricsRes, memberRes, treasuryRes] = await Promise.all([
        axios.get(`${API}/api/platform/dao/proposals?user_id=user_123`),
        axios.get(`${API}/api/platform/dao/metrics?user_id=user_123`),
        axios.get(`${API}/api/platform/dao/member?user_id=user_123`),
        axios.get(`${API}/api/platform/dao/treasury?user_id=user_123`)
      ]);

      if (proposalsRes.data.success) setProposals(proposalsRes.data.proposals || []);
      if (metricsRes.data.success) setDaoMetrics(metricsRes.data.metrics || {});
      if (memberRes.data.success) setMemberProfile(memberRes.data.member || {});
      if (treasuryRes.data.success) setTreasury(treasuryRes.data.treasury || {});
    } catch (error) {
      handleApiError(error, 'fetchDaoData');
    } finally {
      setLoading(false);
    }
  };

  const fetchBlockchainStatus = async () => {
    try {
      const response = await axios.get(`${API}/api/platform/dao/blockchain/status`);
      if (response.data.success) {
        setBlockchainStatus(response.data);
      }
    } catch (error) {
      handleApiError(error, 'fetchBlockchainStatus');
    }
  };

  const createBlockchainProposal = async (proposalData) => {
    try {
      const response = await axios.post(`${API}/api/platform/dao/proposals?user_id=user_123`, proposalData);
      if (response.data.success) {
        fetchDaoData(); // Refresh data
        return response.data;
      }
    } catch (error) {
      handleApiError(error, 'createBlockchainProposal');
    }
  };

  const castBlockchainVote = async (proposalId, choice, reason = '') => {
    try {
      const response = await axios.post(`${API}/api/platform/dao/proposals/${proposalId}/vote`, {
        choice,
        reason,
        user_id: 'user_123',
        wallet_address: memberProfile.wallet_address || '0xmock'
      });
      if (response.data.success) {
        fetchDaoData(); // Refresh data
        return response.data;
      }
    } catch (error) {
      handleApiError(error, 'castBlockchainVote');
    }
  };

  const getProposalStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'passed': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'rejected': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'executed': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const tabs = [
    { id: 'proposals', name: 'Proposals', icon: '🗳️' },
    { id: 'voting', name: 'Voting Power', icon: '⚡' },
    { id: 'treasury', name: 'Treasury', icon: '🏛️' },
    { id: 'blockchain', name: 'Blockchain', icon: '⛓️' },
    { id: 'governance', name: 'Governance', icon: '🏛️' },
    { id: 'profile', name: 'My Profile', icon: '👤' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">DAO Governance</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Decentralized governance and voting with Ethereum integration</p>
        </div>
        <div className="flex space-x-2">
          {/* Blockchain Connection Status */}
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
            blockchainStatus.blockchain_connected 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          }`}>
            {blockchainStatus.blockchain_connected ? '🟢 Blockchain Connected' : '🟡 Mock Mode'}
          </div>
          <button 
            onClick={() => setActiveTab('blockchain')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <span>➕</span>
            <span>Create Proposal</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Proposals</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{daoMetrics.total_proposals || '15'}</p>
            </div>
            <span className="text-2xl">🗳️</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Proposals</p>
              <p className="text-2xl font-bold text-blue-600">{daoMetrics.active_proposals || '3'}</p>
            </div>
            <span className="text-2xl">🔄</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Token Holders</p>
              <p className="text-2xl font-bold text-green-600">{blockchainStatus.total_token_holders || '247'}</p>
            </div>
            <span className="text-2xl">👥</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">My Voting Power</p>
              <p className="text-2xl font-bold text-green-600">{memberProfile.voting_power?.toLocaleString() || '15,000'}</p>
            </div>
            <span className="text-2xl">⚡</span>
          </div>
        </div>
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Treasury Value</p>
              <p className="text-2xl font-bold text-purple-600">${treasury.total_value_usd?.toLocaleString() || '2,450,000'}</p>
            </div>
            <span className="text-2xl">🏛️</span>
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
        {activeTab === 'proposals' && (
          <div className="space-y-4">
            {proposals.length > 0 ? proposals.map((proposal, index) => (
              <div key={proposal.id || index} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{proposal.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getProposalStatusColor(proposal.status)}`}>
                        {proposal.status}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">{proposal.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Type: {proposal.proposal_type?.replace('_', ' ')}</span>
                      <span>Proposer: {proposal.proposer_id}</span>
                      <span>Voting ends: {proposal.voting_ends ? new Date(proposal.voting_ends).toLocaleDateString() : 'N/A'}</span>
                    </div>
                  </div>
                  {proposal.status === 'active' && (
                    <div className="flex space-x-2 ml-4">
                      <button className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Vote Yes
                      </button>
                      <button className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700">
                        Vote No
                      </button>
                    </div>
                  )}
                </div>
                
                {proposal.status === 'active' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Yes Votes</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{width: `${((proposal.vote_weight_yes || 0) / ((proposal.vote_weight_yes || 0) + (proposal.vote_weight_no || 0) + 0.01)) * 100}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{proposal.yes_votes || 0}</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">No Votes</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-red-600 h-2 rounded-full" 
                            style={{width: `${((proposal.vote_weight_no || 0) / ((proposal.vote_weight_yes || 0) + (proposal.vote_weight_no || 0) + 0.01)) * 100}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{proposal.no_votes || 0}</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Quorum</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{width: `${Math.min(((proposal.total_votes || 0) / (proposal.quorum_required || 1)) * 100, 100)}%`}}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{((proposal.total_votes || 0) / (proposal.quorum_required || 1) * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🗳️</div>
                <p className="text-gray-600 dark:text-gray-400">No proposals found. Create the first proposal!</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'voting' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`${isDarkMode ? 'bg-blue-800 border-blue-700' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100">My Voting Power</h3>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100 mt-2">
                  {memberProfile.voting_power?.toLocaleString() || '15,000'} BME
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-green-800 border-green-700' : 'bg-green-50 border-green-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-green-900 dark:text-green-100">Token Balance</h3>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100 mt-2">
                  {memberProfile.token_balance?.toLocaleString() || '15,000'} BME
                </p>
              </div>
              <div className={`${isDarkMode ? 'bg-purple-800 border-purple-700' : 'bg-purple-50 border-purple-200'} border rounded-lg p-4`}>
                <h3 className="font-semibold text-purple-900 dark:text-purple-100">Delegated Power</h3>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100 mt-2">
                  {memberProfile.delegated_power?.toLocaleString() || '0'} BME
                </p>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Delegation Options</h3>
              <div className="space-y-4">
                <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Delegate Your Voting Power</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Allow another member to vote on your behalf while retaining token ownership.
                  </p>
                  <div className="flex space-x-4">
                    <input 
                      type="text" 
                      placeholder="Enter wallet address..."
                      className={`flex-1 px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                    />
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                      Delegate
                    </button>
                  </div>
                </div>
                
                <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Remove Delegation</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Reclaim your voting power and vote directly on proposals.
                  </p>
                  <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
                    Remove Delegation  
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'treasury' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Treasury Assets</h3>
                <div className="space-y-4">
                  {treasury.assets?.map((asset, index) => (
                    <div key={asset.symbol || index} className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{asset.symbol}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{asset.balance?.toLocaleString()} tokens</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900 dark:text-white">
                          ${asset.value_usd?.toLocaleString()}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{asset.percentage}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Monthly Flow</h3>
                <div className="space-y-3">
                  {treasury.monthly_flow?.slice(-6).map((month, index) => (
                    <div key={month.month || index} className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-400">{month.month}</span>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          Net: ${month.net?.toLocaleString()}
                        </p>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          In: ${month.inflow?.toLocaleString()} | Out: ${month.outflow?.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Transactions</h3>
              <div className="space-y-4">
                {treasury.recent_transactions?.map((tx, index) => (
                  <div key={tx.id || index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{tx.description}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {tx.timestamp ? new Date(tx.timestamp).toLocaleDateString() : 'Recent'} • {tx.token_symbol}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold ${
                        tx.transaction_type === 'deposit' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {tx.transaction_type === 'deposit' ? '+' : '-'}${tx.amount?.toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-32">
                        {tx.transaction_hash}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'blockchain' && (
          <div className="space-y-6">
            {/* Blockchain Status Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Network Status</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Network</span>
                    <span className={`font-medium ${blockchainStatus.blockchain_connected ? 'text-green-600' : 'text-yellow-600'}`}>
                      {blockchainStatus.network || 'Mock'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Connection</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      blockchainStatus.blockchain_connected 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}>
                      {blockchainStatus.blockchain_connected ? 'Connected' : 'Mock Mode'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Participation Rate</span>
                    <span className="font-medium text-blue-600">
                      {(blockchainStatus.participation_rate * 100).toFixed(1) || '73.0'}%
                    </span>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Contract Addresses</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Governance Contract</p>
                    <p className="font-mono text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded">
                      {blockchainStatus.governance_contract || '0xabcd...ef12'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Token Contract</p>
                    <p className="font-mono text-xs text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 p-2 rounded">
                      {blockchainStatus.token_contract || '0x1234...5678'}
                    </p>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Blockchain Proposals</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">On-Chain Proposals</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {blockchainStatus.blockchain_proposals || '0'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Quorum Threshold</span>
                    <span className="font-medium text-purple-600">
                      {blockchainStatus.quorum_threshold?.toLocaleString() || '1,000'} BME
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Blockchain Activity */}
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Blockchain Activity</h3>
              <div className="space-y-4">
                {blockchainStatus.recent_blockchain_proposals?.length > 0 ? (
                  blockchainStatus.recent_blockchain_proposals.map((proposal, index) => (
                    <div key={proposal.id || index} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{proposal.description}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Proposer: {proposal.proposer?.slice(0, 6)}...{proposal.proposer?.slice(-4)}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          proposal.status === 'active' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                          proposal.status === 'passed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {proposal.status}
                        </span>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Category: {proposal.category}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">⛓️</div>
                    <p className="text-gray-600 dark:text-gray-400">No recent blockchain activity</p>
                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                      Blockchain proposals will appear here when created
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Blockchain Integration Tools */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create Blockchain Proposal</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Proposal Title
                    </label>
                    <input 
                      type="text" 
                      placeholder="Enter proposal title..."
                      className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description
                    </label>
                    <textarea 
                      rows={4}
                      placeholder="Describe your proposal..."
                      className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Proposal Type
                    </label>
                    <select className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}>
                      <option value="revenue_distribution">Revenue Distribution</option>
                      <option value="platform_upgrade">Platform Upgrade</option>
                      <option value="policy_change">Policy Change</option>
                      <option value="partnership">Partnership</option>
                      <option value="budget_allocation">Budget Allocation</option>
                    </select>
                  </div>
                  <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                    ⛓️ Create On-Chain Proposal
                  </button>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Smart Contract Integration</h3>
                <div className="space-y-4">
                  <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Voting Power from Blockchain</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      Your voting power is automatically calculated from your BME token balance on-chain.
                    </p>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Current Voting Power</span>
                      <span className="font-semibold text-blue-600">100 BME</span>
                    </div>
                  </div>
                  
                  <div className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Transaction Verification</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      All votes and proposals are recorded on the blockchain for transparency.
                    </p>
                    <button className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                      🔍 View on Blockchain Explorer
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'governance' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Governance Statistics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Token Holders</span>
                    <span className="font-medium text-gray-900 dark:text-white">{daoMetrics.total_token_holders?.toLocaleString() || '1,250'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Unique Voters</span>
                    <span className="font-medium text-gray-900 dark:text-white">{daoMetrics.unique_voters || '234'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Avg Participation</span>
                    <span className="font-medium text-blue-600">{daoMetrics.average_participation || '67.8'}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Votes Cast</span>
                    <span className="font-medium text-gray-900 dark:text-white">{daoMetrics.total_votes_cast?.toLocaleString() || '1,456'}</span>
                  </div>
                </div>
              </div>

              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Smart Contracts</h3>
                <div className="space-y-3">
                  <div className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900 dark:text-white">Governance Contract</span>
                      <span className="text-green-500">✅</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0xabcd...ef12</p>
                  </div>
                  <div className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900 dark:text-white">BME Token Contract</span>
                      <span className="text-green-500">✅</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0x1234...7890</p>
                  </div>
                  <div className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900 dark:text-white">Treasury Contract</span>
                      <span className="text-green-500">✅</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0xfedc...ba09</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">DAO Member Profile</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Participation Stats</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Proposals Created</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.proposals_created || '3'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Votes Cast</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.votes_cast || '12'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Participation Rate</span>
                      <span className="font-medium text-green-600">{memberProfile.participation_rate || '85.7'}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Reputation Score</span>
                      <span className="font-medium text-purple-600">{memberProfile.reputation_score || '92.5'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Token Information</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Token Balance</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.token_balance?.toLocaleString() || '15,000'} BME</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Voting Power</span>
                      <span className="font-medium text-blue-600">{memberProfile.voting_power?.toLocaleString() || '15,000'} BME</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Member Since</span>
                      <span className="font-medium text-gray-900 dark:text-white">Jan 2024</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Role</span>
                      <span className="font-medium text-gray-900 dark:text-white">{memberProfile.role || 'Token Holder'}</span>
                    </div>
                  </div>
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