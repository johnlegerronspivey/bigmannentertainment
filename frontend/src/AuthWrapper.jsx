import React, { useEffect, useState } from 'react';
import { Authenticator, useAuthenticator } from '@aws-amplify/ui-react';
import { Amplify } from 'aws-amplify';
import { Hub } from 'aws-amplify/utils';
import awsExports from './aws-exports';
import '@aws-amplify/ui-react/styles.css';

// Configure Amplify
Amplify.configure(awsExports);

// Custom theme for the authenticator
const theme = {
  name: 'BME-DOOH-Theme',
  tokens: {
    components: {
      authenticator: {
        router: {
          boxShadow: '0 0 16px rgba(0, 0, 0, 0.1)',
          borderRadius: '8px',
        },
        form: {
          padding: '2rem',
        },
      },
      button: {
        primary: {
          backgroundColor: '#3B82F6',
          _hover: {
            backgroundColor: '#2563EB',
          },
        },
      },
      fieldcontrol: {
        _focus: {
          borderColor: '#3B82F6',
        },
      },
    },
  },
};

// Form fields configuration
const formFields = {
  signIn: {
    username: {
      placeholder: 'Enter your email address',
      isRequired: true,
      label: 'Email Address',
    },
    password: {
      placeholder: 'Enter your password',
      isRequired: true,
      label: 'Password',
    },
  },
  signUp: {
    given_name: {
      placeholder: 'Enter your first name',
      isRequired: true,
      label: 'First Name',
      order: 1,
    },
    family_name: {
      placeholder: 'Enter your last name',
      isRequired: true,
      label: 'Last Name',
      order: 2,
    },
    username: {
      placeholder: 'Enter your email address',
      isRequired: true,
      label: 'Email Address',
      order: 3,
    },
    password: {
      placeholder: 'Enter your password',
      isRequired: true,
      label: 'Password',
      order: 4,
    },
    confirm_password: {
      placeholder: 'Confirm your password',
      isRequired: true,
      label: 'Confirm Password',
      order: 5,
    },
    'custom:user_type': {
      placeholder: 'Select your role',
      isRequired: true,
      label: 'User Type',
      order: 6,
    },
  },
};

// Services configuration
const services = {
  async handleSignUp(formData) {
    let { username, password, attributes } = formData;
    
    // Add custom attributes based on user type
    const userType = attributes['custom:user_type'] || 'artist';
    
    attributes = {
      ...attributes,
      'custom:user_type': userType,
      'custom:account_status': 'pending_verification',
      'custom:created_at': new Date().toISOString(),
    };

    return { username, password, attributes };
  },
};

// User type selector component
const UserTypeSelector = ({ value, onChange }) => {
  const userTypes = [
    { value: 'artist', label: 'Artist', description: 'Create and manage music campaigns' },
    { value: 'sponsor', label: 'Sponsor', description: 'Fund and promote artist campaigns' },
    { value: 'admin', label: 'Platform Admin', description: 'Manage platform operations' },
  ];

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Select Your Role
      </label>
      <div className="space-y-2">
        {userTypes.map((type) => (
          <label
            key={type.value}
            className={`relative flex cursor-pointer rounded-lg border p-4 shadow-sm focus:outline-none ${
              value === type.value
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-white hover:bg-gray-50'
            }`}
          >
            <input
              type="radio"
              name="user_type"
              value={type.value}
              checked={value === type.value}
              onChange={(e) => onChange(e.target.value)}
              className="mt-0.5 h-4 w-4 shrink-0 cursor-pointer text-blue-600 focus:ring-blue-500"
            />
            <div className="ml-3 flex flex-col">
              <span className="block text-sm font-medium text-gray-900">
                {type.label}
              </span>
              <span className="block text-sm text-gray-500">
                {type.description}
              </span>
            </div>
          </label>
        ))}
      </div>
    </div>
  );
};

// Role-based access control hook
export const useUserRole = () => {
  const { user } = useAuthenticator((context) => [context.user]);
  const [userRole, setUserRole] = useState(null);
  const [permissions, setPermissions] = useState({});

  useEffect(() => {
    if (user) {
      const role = user.attributes?.['custom:user_type'] || 'artist';
      setUserRole(role);
      
      // Set permissions based on role
      const rolePermissions = {
        admin: {
          canManageCampaigns: true,
          canManageUsers: true,
          canViewAnalytics: true,
          canManageTriggers: true,
          canManageAssets: true,
          canAccessAll: true,
        },
        sponsor: {
          canManageCampaigns: true,
          canManageUsers: false,
          canViewAnalytics: true,
          canManageTriggers: true,
          canManageAssets: true,
          canAccessAll: false,
        },
        artist: {
          canManageCampaigns: true,
          canManageUsers: false,
          canViewAnalytics: true,
          canManageTriggers: false,
          canManageAssets: true,
          canAccessAll: false,
        },
      };
      
      setPermissions(rolePermissions[role] || rolePermissions.artist);
    }
  }, [user]);

  return { userRole, permissions, user };
};

// Protected route component
export const ProtectedRoute = ({ children, requiredPermission, fallback }) => {
  const { permissions } = useUserRole();

  if (requiredPermission && !permissions[requiredPermission]) {
    return fallback || (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500">
            You don't have permission to access this feature.
          </p>
        </div>
      </div>
    );
  }

  return children;
};

// Main authentication wrapper component
const AuthWrapper = ({ children }) => {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Listen for auth events
    const listener = (data) => {
      switch (data.payload.event) {
        case 'signIn':
          console.log('User signed in');
          break;
        case 'signUp':
          console.log('User signed up');
          break;
        case 'signOut':
          console.log('User signed out');
          break;
        case 'signIn_failure':
          console.log('User sign in failed');
          break;
        case 'tokenRefresh':
          console.log('Token refresh succeeded');
          break;
        case 'tokenRefresh_failure':
          console.log('Token refresh failed');
          break;
        default:
          break;
      }
    };

    Hub.listen('auth', listener);
    setIsLoading(false);

    return () => Hub.remove('auth', listener);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Authenticator
      theme={theme}
      formFields={formFields}
      services={services}
      components={{
        Header() {
          return (
            <div className="text-center mb-8">
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
                <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 className="mt-4 text-2xl font-bold text-gray-900">
                Big Mann Entertainment
              </h2>
              <p className="mt-2 text-sm text-gray-600">
                Programmatic DOOH Platform
              </p>
            </div>
          );
        },
        Footer() {
          return (
            <div className="text-center mt-8">
              <p className="text-xs text-gray-500">
                © 2026 Big Mann Entertainment. All rights reserved.
              </p>
            </div>
          );
        },
      }}
    >
      {({ signOut, user }) => (
        <div className="min-h-screen bg-gray-50">
          {/* User info bar */}
          <div className="bg-white border-b border-gray-200 px-4 py-2">
            <div className="flex items-center justify-between max-w-7xl mx-auto">
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">
                    {user?.attributes?.given_name?.[0] || user?.username?.[0] || 'U'}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {user?.attributes?.given_name} {user?.attributes?.family_name}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">
                    {user?.attributes?.['custom:user_type'] || 'User'}
                  </p>
                </div>
              </div>
              <button
                onClick={signOut}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign Out
              </button>
            </div>
          </div>
          
          {/* Main content */}
          <main>
            {children}
          </main>
        </div>
      )}
    </Authenticator>
  );
};

export default AuthWrapper;