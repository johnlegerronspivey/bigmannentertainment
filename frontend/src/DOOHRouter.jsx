import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useUserRole, ProtectedRoute } from './AuthWrapper';

// Import DOOH components
import CampaignManager from './CampaignManager';
import CreativeLibrary from './CreativeLibrary';
import TriggerConfigurator from './TriggerConfigurator';
import AnalyticsDashboard from './AnalyticsDashboard';

// Import existing components
import { ComprehensivePlatform } from './ComprehensivePlatformComponents';

// Navigation component
const DOOHNavigation = ({ currentPath, onNavigate }) => {
  const { userRole, permissions } = useUserRole();

  const navigationItems = [
    {
      id: 'dashboard',
      name: 'Analytics Dashboard',
      path: '/dooh/dashboard',
      icon: '📊',
      permission: 'canViewAnalytics',
    },
    {
      id: 'campaigns',
      name: 'Campaign Manager',
      path: '/dooh/campaigns',
      icon: '🎯',
      permission: 'canManageCampaigns',
    },
    {
      id: 'library',
      name: 'Creative Library',
      path: '/dooh/library',
      icon: '🎨',
      permission: 'canManageAssets',
    },
    {
      id: 'triggers',
      name: 'Trigger Configurator',
      path: '/dooh/triggers',
      icon: '⚡',
      permission: 'canManageTriggers',
    },
    {
      id: 'platform',
      name: 'Comprehensive Platform',
      path: '/comprehensive-platform',
      icon: '🏢',
      permission: null, // Available to all authenticated users
    },
  ];

  // Filter navigation based on user permissions
  const availableItems = navigationItems.filter(item => 
    !item.permission || permissions[item.permission]
  );

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-gray-900">BME DOOH Platform</h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {availableItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.path)}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentPath === item.path
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.name}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Role:</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                {userRole}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile navigation */}
      <div className="sm:hidden">
        <div className="pt-2 pb-3 space-y-1">
          {availableItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.path)}
              className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium w-full text-left ${
                currentPath === item.path
                  ? 'bg-blue-50 border-blue-500 text-blue-700'
                  : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{item.icon}</span>
              {item.name}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

// Main DOOH Router component
const DOOHRouter = () => {
  const { userRole, permissions } = useUserRole();

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* Default redirect to dashboard */}
          <Route path="/" element={<Navigate to="/dooh/dashboard" replace />} />
          
          {/* Analytics Dashboard - Available to all roles */}
          <Route 
            path="/dooh/dashboard" 
            element={
              <ProtectedRoute requiredPermission="canViewAnalytics">
                <div>
                  <DOOHNavigation 
                    currentPath="/dooh/dashboard" 
                    onNavigate={(path) => window.location.href = path}
                  />
                  <AnalyticsDashboard />
                </div>
              </ProtectedRoute>
            } 
          />
          
          {/* Campaign Manager - Artists, Sponsors, Admins */}
          <Route 
            path="/dooh/campaigns" 
            element={
              <ProtectedRoute requiredPermission="canManageCampaigns">
                <div>
                  <DOOHNavigation 
                    currentPath="/dooh/campaigns" 
                    onNavigate={(path) => window.location.href = path}
                  />
                  <CampaignManager />
                </div>
              </ProtectedRoute>
            } 
          />
          
          {/* Creative Library - Artists, Sponsors, Admins */}
          <Route 
            path="/dooh/library" 
            element={
              <ProtectedRoute requiredPermission="canManageAssets">
                <div>
                  <DOOHNavigation 
                    currentPath="/dooh/library" 
                    onNavigate={(path) => window.location.href = path}
                  />
                  <CreativeLibrary />
                </div>
              </ProtectedRoute>
            } 
          />
          
          {/* Trigger Configurator - Sponsors and Admins only */}
          <Route 
            path="/dooh/triggers" 
            element={
              <ProtectedRoute 
                requiredPermission="canManageTriggers"
                fallback={
                  <div className="p-6">
                    <div className="text-center">
                      <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
                        <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                      </div>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">Sponsor/Admin Access Required</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Trigger configuration is available to Sponsors and Platform Administrators only.
                      </p>
                    </div>
                  </div>
                }
              >
                <div>
                  <DOOHNavigation 
                    currentPath="/dooh/triggers" 
                    onNavigate={(path) => window.location.href = path}
                  />
                  <TriggerConfigurator />
                </div>
              </ProtectedRoute>
            } 
          />
          
          {/* Comprehensive Platform - Available to all roles */}
          <Route 
            path="/comprehensive-platform" 
            element={
              <div>
                <DOOHNavigation 
                  currentPath="/comprehensive-platform" 
                  onNavigate={(path) => window.location.href = path}
                />
                <ComprehensivePlatform />
              </div>
            } 
          />
          
          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/dooh/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default DOOHRouter;