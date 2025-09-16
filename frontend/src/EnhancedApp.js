import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// AWS Amplify Authentication
import AuthWrapper, { useUserRole, ProtectedRoute } from './AuthWrapper';

// New DOOH Components
import CampaignManager from './CampaignManager';
import CreativeLibrary from './CreativeLibrary';
import TriggerConfigurator from './TriggerConfigurator';
import AnalyticsDashboard from './AnalyticsDashboard';

// Existing Platform Components
import { ComprehensivePlatform } from './ComprehensivePlatformComponents';
import { ContentIngestionDashboard } from './ContentIngestionComponents';
import { MusicReportsDashboard } from './MusicReportsComponents';
import { ComprehensiveWorkflowDashboard } from './ComprehensiveWorkflowComponents';
import { SocialMediaStrategyDashboard } from './SocialMediaStrategyComponents';
import { SocialMediaPhases5To10Dashboard } from './SocialMediaPhases5To10Components';
import { RealTimeRoyaltyDashboard } from './RealTimeRoyaltyComponents';

// Enhanced Navigation Component
const EnhancedNavigation = ({ currentPath, onNavigate, userRole, permissions }) => {
  const [isOpen, setIsOpen] = useState(false);

  const navigationSections = [
    {
      title: 'DOOH Platform',
      items: [
        {
          id: 'dashboard',
          name: 'Analytics & Performance',
          path: '/dooh/dashboard',
          icon: '📊',
          permission: 'canViewAnalytics',
          description: 'Real-time campaign analytics and ROI tracking'
        },
        {
          id: 'campaigns',
          name: 'Campaign Manager',
          path: '/dooh/campaigns',
          icon: '🎯',
          permission: 'canManageCampaigns',
          description: 'Create and manage DOOH advertising campaigns'
        },
        {
          id: 'library',
          name: 'Creative Library',
          path: '/dooh/library',
          icon: '🎨',
          permission: 'canManageAssets',
          description: 'Manage creative assets and digital content'
        },
        {
          id: 'triggers',
          name: 'Smart Triggers',
          path: '/dooh/triggers',
          icon: '⚡',
          permission: 'canManageTriggers',
          description: 'Configure contextual triggers and DCO'
        },
      ]
    },
    {
      title: 'Platform Modules',
      items: [
        {
          id: 'comprehensive',
          name: 'Comprehensive Platform',
          path: '/comprehensive-platform',
          icon: '🏢',
          permission: null,
          description: 'Access all platform features and modules'
        },
        {
          id: 'content',
          name: 'Content Management',
          path: '/content-ingestion',
          icon: '📁',
          permission: 'canManageAssets',
          description: 'Content ingestion and management'
        },
        {
          id: 'music-reports',
          name: 'Music Reports',
          path: '/music-reports',
          icon: '📈',
          permission: 'canViewAnalytics',
          description: 'Music industry reports and analytics'
        },
        {
          id: 'workflow',
          name: 'Workflow Management',
          path: '/comprehensive-workflow',
          icon: '⚙️',
          permission: 'canManageCampaigns',
          description: 'Comprehensive workflow management'
        }
      ]
    }
  ];

  // Filter navigation based on user permissions
  const getFilteredItems = (items) => items.filter(item => 
    !item.permission || permissions[item.permission]
  );

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <div className="h-8 w-8 bg-white rounded-full flex items-center justify-center mr-3">
                <span className="text-blue-600 font-bold text-sm">BME</span>
              </div>
              <h1 className="text-xl font-bold text-white">Big Mann Entertainment</h1>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigationSections.map((section) => (
              <div key={section.title} className="relative group">
                <button className="text-white hover:text-blue-200 px-3 py-2 rounded-md text-sm font-medium">
                  {section.title}
                </button>
                <div className="absolute left-0 mt-2 w-80 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-2">
                    {getFilteredItems(section.items).map((item) => (
                      <button
                        key={item.id}
                        onClick={() => onNavigate(item.path)}
                        className={`block w-full text-left px-4 py-3 text-sm hover:bg-gray-50 ${
                          currentPath === item.path ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                        }`}
                      >
                        <div className="flex items-start">
                          <span className="text-lg mr-3">{item.icon}</span>
                          <div>
                            <div className="font-medium text-gray-900">{item.name}</div>
                            <div className="text-gray-500 text-xs">{item.description}</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* User Info */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-white text-sm">Role:</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white text-blue-600 capitalize">
                {userRole}
              </span>
            </div>
            
            {/* Mobile menu button */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden text-white hover:text-blue-200 p-2"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-blue-700">
            {navigationSections.map((section) => (
              <div key={section.title}>
                <div className="px-3 py-2 text-xs font-semibold text-blue-200 uppercase tracking-wider">
                  {section.title}
                </div>
                {getFilteredItems(section.items).map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      onNavigate(item.path);
                      setIsOpen(false);
                    }}
                    className={`block w-full text-left px-3 py-2 rounded-md text-base font-medium ${
                      currentPath === item.path
                        ? 'bg-blue-800 text-white'
                        : 'text-blue-100 hover:text-white hover:bg-blue-600'
                    }`}
                  >
                    <span className="mr-2">{item.icon}</span>
                    {item.name}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};

// Main App Content Component
const AppContent = () => {
  const { userRole, permissions } = useUserRole();
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  const handleNavigate = (path) => {
    setCurrentPath(path);
    window.history.pushState(null, '', path);
    window.location.reload(); // Simple reload for navigation
  };

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <EnhancedNavigation 
        currentPath={currentPath}
        onNavigate={handleNavigate}
        userRole={userRole}
        permissions={permissions}
      />
      
      <main className="flex-1">
        <Routes>
          {/* Default redirect based on user role */}
          <Route 
            path="/" 
            element={
              <Navigate 
                to={userRole === 'admin' ? '/dooh/dashboard' : '/dooh/campaigns'} 
                replace 
              />
            } 
          />
          
          {/* DOOH Platform Routes */}
          <Route 
            path="/dooh/dashboard" 
            element={
              <ProtectedRoute requiredPermission="canViewAnalytics">
                <AnalyticsDashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/dooh/campaigns" 
            element={
              <ProtectedRoute requiredPermission="canManageCampaigns">
                <CampaignManager />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/dooh/library" 
            element={
              <ProtectedRoute requiredPermission="canManageAssets">
                <CreativeLibrary />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/dooh/triggers" 
            element={
              <ProtectedRoute 
                requiredPermission="canManageTriggers"
                fallback={
                  <div className="p-6">
                    <div className="max-w-md mx-auto text-center">
                      <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
                        <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                      </div>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">Premium Feature</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Smart Triggers are available to Sponsors and Platform Administrators.
                      </p>
                      <div className="mt-6">
                        <button
                          onClick={() => handleNavigate('/dooh/campaigns')}
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                        >
                          Go to Campaign Manager
                        </button>
                      </div>
                    </div>
                  </div>
                }
              >
                <TriggerConfigurator />
              </ProtectedRoute>
            } 
          />
          
          {/* Platform Module Routes */}
          <Route path="/comprehensive-platform" element={<ComprehensivePlatform />} />
          <Route 
            path="/content-ingestion" 
            element={
              <ProtectedRoute requiredPermission="canManageAssets">
                <ContentIngestionDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/music-reports" 
            element={
              <ProtectedRoute requiredPermission="canViewAnalytics">
                <MusicReportsDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/comprehensive-workflow" 
            element={
              <ProtectedRoute requiredPermission="canManageCampaigns">
                <ComprehensiveWorkflowDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Legacy routes for existing functionality */}
          <Route path="/social-media-strategy" element={<SocialMediaStrategyDashboard />} />
          <Route path="/social-media-phases-5-10" element={<SocialMediaPhases5To10Dashboard />} />
          <Route path="/real-time-royalty" element={<RealTimeRoyaltyDashboard />} />
          
          {/* Fallback redirect */}
          <Route path="*" element={<Navigate to="/dooh/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
};

// Main Enhanced App Component
const EnhancedApp = () => {
  return (
    <AuthWrapper>
      <Router>
        <AppContent />
      </Router>
    </AuthWrapper>
  );
};

export default EnhancedApp;