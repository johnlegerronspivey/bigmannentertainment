import React, { useState } from 'react';

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
      <div data-testid="left-sidebar" className={`
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
            data-testid="sidebar-collapse-toggle"
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
              data-testid={`sidebar-module-${module.id}`}
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

export { LeftSidebar };
