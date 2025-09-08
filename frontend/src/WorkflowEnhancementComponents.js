import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Enhanced User Dashboard with Workflow Progress
export const EnhancedUserDashboard = () => {
  const [userData, setUserData] = useState(null);
  const [workflowProgress, setWorkflowProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch user data
      const userResponse = await axios.get(`${API}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserData(userResponse.data);

      // Fetch workflow progress data
      const progressResponse = await axios.get(`${API}/api/user/workflow-progress`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setWorkflowProgress(progressResponse.data || {});
      
      setError('');
    } catch (error) {
      setError('Failed to load dashboard data');
      console.error('Dashboard data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  const progressSteps = [
    { 
      id: 'registration', 
      title: 'Account Setup', 
      completed: true, 
      description: 'Complete profile and business information',
      action: 'View Profile',
      link: '/profile'
    },
    { 
      id: 'upload', 
      title: 'Upload Content', 
      completed: workflowProgress.uploads_count > 0, 
      description: 'Upload your first media content',
      action: 'Upload Content',
      link: '/upload'
    },
    { 
      id: 'distribute', 
      title: 'Distribute Content', 
      completed: workflowProgress.distributions_count > 0, 
      description: 'Distribute to 106+ platforms worldwide',
      action: 'Start Distribution',
      link: '/distribute'
    },
    { 
      id: 'earn', 
      title: 'Track Earnings', 
      completed: workflowProgress.earnings_total > 0, 
      description: 'Monitor revenue and royalties',
      action: 'View Earnings',
      link: '/earnings'
    },
    { 
      id: 'payout', 
      title: 'Request Payouts', 
      completed: workflowProgress.payouts_count > 0, 
      description: 'Request and manage your payouts',
      action: 'Manage Payouts',
      link: '/earnings'
    }
  ];

  const completedSteps = progressSteps.filter(step => step.completed).length;
  const progressPercentage = (completedSteps / progressSteps.length) * 100;
  const nextStep = progressSteps.find(step => !step.completed);

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-800 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {userData?.full_name || 'Creator'}!
        </h1>
        <p className="text-purple-100">
          Your journey to global distribution success continues
        </p>
      </div>

      {/* Progress Overview */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Your Progress</h2>
          <div className="text-sm text-gray-500">
            {completedSteps} of {progressSteps.length} steps completed
          </div>
        </div>
        
        <div className="mb-6">
          <div className="flex justify-between text-sm font-medium text-gray-700 mb-2">
            <span>Progress</span>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        {nextStep && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-1">Next Step: {nextStep.title}</h3>
            <p className="text-blue-700 text-sm mb-3">{nextStep.description}</p>
            <Link 
              to={nextStep.link}
              className="inline-block bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
            >
              {nextStep.action}
            </Link>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-purple-600">{workflowProgress.uploads_count || 0}</div>
          <div className="text-sm text-gray-600">Content Uploaded</div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-green-600">{workflowProgress.distributions_count || 0}</div>
          <div className="text-sm text-gray-600">Distributions</div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-blue-600">${(workflowProgress.earnings_total || 0).toFixed(2)}</div>
          <div className="text-sm text-gray-600">Total Earnings</div>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-2xl font-bold text-orange-600">{workflowProgress.payouts_count || 0}</div>
          <div className="text-sm text-gray-600">Payouts</div>
        </div>
      </div>

      {/* Workflow Steps */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Complete Your Journey</h2>
        <div className="space-y-4">
          {progressSteps.map((step, index) => (
            <div key={step.id} className={`flex items-start space-x-4 p-4 rounded-lg ${
              step.completed 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-gray-50 border border-gray-200'
            }`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                step.completed 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {step.completed ? '✓' : index + 1}
              </div>
              <div className="flex-grow">
                <h3 className={`font-medium ${
                  step.completed ? 'text-green-900' : 'text-gray-900'
                }`}>
                  {step.title}
                </h3>
                <p className={`text-sm ${
                  step.completed ? 'text-green-700' : 'text-gray-600'
                }`}>
                  {step.description}
                </p>
              </div>
              <div>
                <Link 
                  to={step.link}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    step.completed 
                      ? 'bg-green-600 text-white hover:bg-green-700' 
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                  }`}
                >
                  {step.action}
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link 
            to="/upload"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <div className="font-medium">Upload Content</div>
              <div className="text-sm text-gray-600">Add new media</div>
            </div>
          </Link>

          <Link 
            to="/distribute"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
            </div>
            <div>
              <div className="font-medium">Distribute</div>
              <div className="text-sm text-gray-600">Share to 106+ platforms</div>
            </div>
          </Link>

          <Link 
            to="/earnings"
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div>
              <div className="font-medium">View Earnings</div>
              <div className="text-sm text-gray-600">Track your revenue</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

// Onboarding Progress Tracker Component
export const OnboardingTracker = ({ currentStep = 1 }) => {
  const steps = [
    { id: 1, title: 'Create Account', description: 'Sign up and verify your email' },
    { id: 2, title: 'Complete Profile', description: 'Add your business information' },
    { id: 3, title: 'Upload Content', description: 'Add your first media file' },
    { id: 4, title: 'Distribute', description: 'Send to platforms worldwide' },
    { id: 5, title: 'Earn Revenue', description: 'Start collecting royalties' }
  ];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <h3 className="text-sm font-medium text-gray-900 mb-3">Setup Progress</h3>
      <div className="flex items-center space-x-2">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step.id <= currentStep 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 text-gray-600'
            }`}>
              {step.id <= currentStep ? '✓' : step.id}
            </div>
            {step.id < steps.length && (
              <div className={`w-12 h-1 mx-2 ${
                step.id < currentStep ? 'bg-purple-600' : 'bg-gray-200'
              }`}></div>
            )}
          </div>
        ))}
      </div>
      <div className="mt-3">
        <p className="text-sm text-gray-600">
          Step {currentStep} of {steps.length}: {steps[currentStep - 1]?.description}
        </p>
      </div>
    </div>
  );
};

// Enhanced Navigation Component with Progress Indicators
export const ProgressAwareNavigation = ({ workflowProgress = {} }) => {
  const navigationItems = [
    {
      name: 'Upload',
      path: '/upload',
      completed: workflowProgress.uploads_count > 0,
      count: workflowProgress.uploads_count || 0
    },
    {
      name: 'Library',
      path: '/library',
      completed: workflowProgress.uploads_count > 0,
      count: workflowProgress.library_count || 0
    },
    {
      name: 'Distribute',
      path: '/distribute',
      completed: workflowProgress.distributions_count > 0,
      count: workflowProgress.distributions_count || 0
    },
    {
      name: 'Earnings',
      path: '/earnings',
      completed: workflowProgress.earnings_total > 0,
      amount: workflowProgress.earnings_total || 0
    }
  ];

  return (
    <nav className="bg-white shadow-sm border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-8">
          {navigationItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center space-x-2 py-4 text-sm font-medium border-b-2 ${
                item.completed
                  ? 'text-purple-600 border-purple-600'
                  : 'text-gray-500 hover:text-gray-700 border-transparent hover:border-gray-300'
              }`}
            >
              <span>{item.name}</span>
              {item.completed && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ✓
                </span>
              )}
              {item.count !== undefined && item.count > 0 && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  {item.count}
                </span>
              )}
              {item.amount !== undefined && item.amount > 0 && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  ${item.amount.toFixed(2)}
                </span>
              )}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

// Success Celebration Component
export const SuccessCelebration = ({ type, details, onClose }) => {
  const celebrations = {
    upload: {
      title: '🎉 Content Uploaded Successfully!',
      message: 'Your content is ready for distribution to 106+ platforms worldwide.',
      nextAction: 'Start Distribution',
      nextPath: '/distribute'
    },
    distribution: {
      title: '🚀 Distribution Started!',
      message: 'Your content is being distributed to selected platforms.',
      nextAction: 'Track Progress',
      nextPath: '/distribute'
    },
    earnings: {
      title: '💰 First Earnings Received!',
      message: 'Congratulations! You\'re now earning revenue from your content.',
      nextAction: 'View Earnings',
      nextPath: '/earnings'
    },
    payout: {
      title: '🏦 Payout Processed!',
      message: 'Your payout request has been processed successfully.',
      nextAction: 'View History',
      nextPath: '/earnings'
    }
  };

  const celebration = celebrations[type] || celebrations.upload;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">{celebration.title}</h2>
        <p className="text-gray-600 mb-6">{celebration.message}</p>
        {details && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap">{details}</pre>
          </div>
        )}
        <div className="flex space-x-4">
          <Link
            to={celebration.nextPath}
            className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700"
            onClick={onClose}
          >
            {celebration.nextAction}
          </Link>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

// Enhanced Error Handling Component
export const ErrorBoundaryComponent = ({ error, retry, context }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <svg className="mx-auto h-12 w-12 text-red-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L5.232 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <h3 className="text-lg font-medium text-red-900 mb-2">Something went wrong</h3>
      <p className="text-red-700 mb-4">{error?.message || 'An unexpected error occurred'}</p>
      {context && (
        <p className="text-red-600 text-sm mb-4">Context: {context}</p>
      )}
      <div className="flex justify-center space-x-4">
        {retry && (
          <button
            onClick={retry}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            Try Again
          </button>
        )}
        <Link
          to="/"
          className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
        >
          Go Home
        </Link>
      </div>
    </div>
  );
};

export default {
  EnhancedUserDashboard,
  OnboardingTracker,
  ProgressAwareNavigation,
  SuccessCelebration,
  ErrorBoundaryComponent
};