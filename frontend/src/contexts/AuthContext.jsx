import React, { useState, useEffect, useContext, createContext } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";
import { api } from "../utils/apiClient";
import { PageLoadingOverlay } from "../components/LoadingSkeleton";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
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
    // eslint-disable-next-line
  }, []);

  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      const userData = await api.get('/auth/me');
      
      if (userData && userData.email) {
        setUser(userData);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } else {
        clearAuth();
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      
      const token = localStorage.getItem('token');
      if (token && !error.message.includes('Session expired')) {
        setUser({ 
          email: 'owner@bigmannentertainment.com', 
          role: 'user',
          temp: true 
        });
      }
      setLoading(false);
    }
    setLoading(false);
  };

  const clearAuth = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setLoading(false);
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, refresh_token, user: userData } = response;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(userData);
      
      toast.success('Welcome back!', {
        description: 'You have successfully logged in.'
      });
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.message || 'Login failed. Please check your credentials.';
      toast.error('Login Failed', {
        description: errorMessage
      });
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await api.post('/auth/register', userData);
      const { access_token, refresh_token, user: newUser } = response;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(newUser);
      
      toast.success('Account Created!', {
        description: 'Welcome to Big Mann Entertainment. Your account has been successfully created.'
      });
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.message || 'Registration failed. Please try again.';
      toast.error('Registration Failed', {
        description: errorMessage
      });
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const forgotPassword = async (email) => {
    try {
      const response = await axios.post(`${API}/auth/forgot-password`, { email });
      return { 
        success: true, 
        message: response.data.message,
        data: response.data
      };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to send reset email' 
      };
    }
  };

  const resetPassword = async (token, newPassword) => {
    try {
      const response = await axios.post(`${API}/auth/reset-password`, { 
        token, 
        new_password: newPassword 
      });
      return { success: true, message: response.data.message };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Password reset failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      clearAuth();
    }
  };

  const isAdmin = () => {
    return user && (user.is_admin || ['admin', 'super_admin', 'moderator'].includes(user.role));
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      register, 
      forgotPassword,
      resetPassword,
      logout, 
      isAdmin,
      loading 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <PageLoadingOverlay message="Verifying your session..." />;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Admin Route Component
export const AdminRoute = ({ children }) => {
  const { user, isAdmin, loading } = useAuth();
  
  if (loading) {
    return <PageLoadingOverlay message="Checking permissions..." />;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  if (!isAdmin()) {
    return <Navigate to="/" />;
  }
  
  return children;
};
