import axios from 'axios';
import toast from './toast';
import logger from './logger';
import { cacheAPIResponse, clearCache } from './performance';

/**
 * API Utility
 * Centralized API handling with error management, caching, and interceptors
 */

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    logger.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    logger.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => {
    logger.log('API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    logger.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('token');
          clearCache();
          if (window.location.pathname !== '/login') {
            toast.error('Session expired. Please login again.');
            window.location.href = '/login';
          }
          break;
          
        case 403:
          toast.error('You do not have permission to perform this action.');
          break;
          
        case 404:
          toast.error('The requested resource was not found.');
          break;
          
        case 429:
          toast.error('Too many requests. Please try again later.');
          break;
          
        case 500:
        case 502:
        case 503:
          toast.error('Server error. Please try again later.');
          break;
          
        default:
          toast.error(data?.detail || data?.message || 'An error occurred. Please try again.');
      }
    } else if (error.request) {
      // Request made but no response
      toast.error('Network error. Please check your connection.');
    } else {
      // Something else happened
      toast.error('An unexpected error occurred.');
    }
    
    return Promise.reject(error);
  }
);

/**
 * GET request with optional caching
 * @param {string} url - API endpoint
 * @param {Object} config - Axios config
 * @param {boolean} useCache - Whether to use caching
 * @param {number} cacheTTL - Cache time to live in milliseconds
 * @returns {Promise} API response
 */
export const get = async (url, config = {}, useCache = false, cacheTTL = 5 * 60 * 1000) => {
  if (useCache) {
    return cacheAPIResponse(
      `api_${url}`,
      () => api.get(url, config).then(res => res.data),
      cacheTTL
    );
  }
  const response = await api.get(url, config);
  return response.data;
};

/**
 * POST request
 * @param {string} url - API endpoint
 * @param {Object} data - Request body
 * @param {Object} config - Axios config
 * @returns {Promise} API response
 */
export const post = async (url, data = {}, config = {}) => {
  const response = await api.post(url, data, config);
  return response.data;
};

/**
 * PUT request
 * @param {string} url - API endpoint
 * @param {Object} data - Request body
 * @param {Object} config - Axios config
 * @returns {Promise} API response
 */
export const put = async (url, data = {}, config = {}) => {
  const response = await api.put(url, data, config);
  return response.data;
};

/**
 * PATCH request
 * @param {string} url - API endpoint
 * @param {Object} data - Request body
 * @param {Object} config - Axios config
 * @returns {Promise} API response
 */
export const patch = async (url, data = {}, config = {}) => {
  const response = await api.patch(url, data, config);
  return response.data;
};

/**
 * DELETE request
 * @param {string} url - API endpoint
 * @param {Object} config - Axios config
 * @returns {Promise} API response
 */
export const del = async (url, config = {}) => {
  const response = await api.delete(url, config);
  return response.data;
};

/**
 * Upload file with progress tracking
 * @param {string} url - API endpoint
 * @param {FormData} formData - Form data with file
 * @param {Function} onProgress - Progress callback
 * @returns {Promise} API response
 */
export const uploadFile = async (url, formData, onProgress = null) => {
  const config = {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  };
  
  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      onProgress(percentCompleted);
    };
  }
  
  const response = await api.post(url, formData, config);
  return response.data;
};

/**
 * Download file
 * @param {string} url - API endpoint
 * @param {string} filename - Filename for download
 * @returns {Promise} Download result
 */
export const downloadFile = async (url, filename) => {
  const response = await api.get(url, {
    responseType: 'blob'
  });
  
  // Create blob link to download
  const urlBlob = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = urlBlob;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  window.URL.revokeObjectURL(urlBlob);
  
  toast.success(`Downloaded ${filename}`);
  return { success: true };
};

/**
 * Batch requests with error handling
 * @param {Array} requests - Array of request promises
 * @returns {Promise} Array of results
 */
export const batchRequests = async (requests) => {
  try {
    const results = await Promise.allSettled(requests);
    
    const successful = results.filter(r => r.status === 'fulfilled').map(r => r.value);
    const failed = results.filter(r => r.status === 'rejected').map(r => r.reason);
    
    if (failed.length > 0) {
      logger.warn(`${failed.length} requests failed out of ${requests.length}`);
    }
    
    return { successful, failed, allSuccess: failed.length === 0 };
  } catch (error) {
    logger.error('Batch requests error:', error);
    throw error;
  }
};

export default api;
