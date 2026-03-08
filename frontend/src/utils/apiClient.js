/**
 * Enhanced API Client with retry logic and error handling
 * Provides automatic retry for failed requests and user-friendly error messages
 */

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Retry configuration
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  retryableStatuses: [408, 429, 500, 502, 503, 504]
};

/**
 * Sleep utility for retry delays
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Enhanced fetch with retry logic
 */
async function fetchWithRetry(url, options = {}, retryCount = 0) {
  try {
    const response = await fetch(url, options);
    
    // If response is ok or not retryable, return it
    if (response.ok || !RETRY_CONFIG.retryableStatuses.includes(response.status)) {
      return response;
    }
    
    // If we can retry
    if (retryCount < RETRY_CONFIG.maxRetries) {
      const delay = RETRY_CONFIG.retryDelay * Math.pow(2, retryCount); // Exponential backoff
      console.log(`Retrying request (${retryCount + 1}/${RETRY_CONFIG.maxRetries}) after ${delay}ms...`);
      await sleep(delay);
      return fetchWithRetry(url, options, retryCount + 1);
    }
    
    return response;
  } catch (error) {
    // Network error - retry if possible
    if (retryCount < RETRY_CONFIG.maxRetries) {
      const delay = RETRY_CONFIG.retryDelay * Math.pow(2, retryCount);
      console.log(`Network error, retrying (${retryCount + 1}/${RETRY_CONFIG.maxRetries}) after ${delay}ms...`);
      await sleep(delay);
      return fetchWithRetry(url, options, retryCount + 1);
    }
    throw error;
  }
}

/**
 * Parse error response and provide user-friendly message
 */
function parseErrorResponse(error, status) {
  const errorMessages = {
    400: 'Invalid request. Please check your input and try again.',
    401: 'Your session has expired. Please log in again.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    408: 'Request timeout. Please try again.',
    429: 'Too many requests. Please wait a moment and try again.',
    500: 'Server error. Please try again later.',
    502: 'Service temporarily unavailable. Please try again.',
    503: 'Service is currently down for maintenance. Please try again later.',
    504: 'Request timeout. The server took too long to respond.'
  };
  
  return {
    message: errorMessages[status] || 'An unexpected error occurred. Please try again.',
    originalError: error,
    status,
    userFriendly: true
  };
}

/**
 * Make API request with enhanced error handling and retry
 */
export async function apiRequest(endpoint, options = {}) {
  const url = `${BACKEND_URL}/api${endpoint}`;
  
  // Get token from localStorage
  const token = localStorage.getItem('token');
  
  // Default headers
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };
  
  const fetchOptions = {
    ...options,
    headers
  };
  
  try {
    const response = await fetchWithRetry(url, fetchOptions);
    
    // Parse response body first so we can use the real error message
    const data = await response.json().catch(() => ({}));
    
    // Handle unauthorized
    if (response.status === 401) {
      // Only clear auth for non-login endpoints (actual session expiry)
      const isAuthEndpoint = endpoint.includes('/auth/login') || endpoint.includes('/auth/register');
      if (!isAuthEndpoint) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      // Use the backend's actual error message
      const serverMessage = data.detail || data.message || data.error;
      throw new Error(serverMessage || (isAuthEndpoint ? 'Invalid credentials' : 'Session expired. Please log in again.'));
    }
    
    if (!response.ok) {
      // Use backend error message if available, otherwise fallback
      const serverMessage = data.detail || data.message || data.error;
      if (serverMessage) {
        throw new Error(serverMessage);
      }
      const errorInfo = parseErrorResponse(data, response.status);
      throw new Error(errorInfo.message);
    }
    
    return data;
  } catch (error) {
    // Network error or parsing error
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      throw new Error('Network error. Please check your connection and try again.');
    }
    throw error;
  }
}

/**
 * Convenience methods for different HTTP methods
 */
export const api = {
  get: (endpoint, options = {}) => apiRequest(endpoint, { ...options, method: 'GET' }),
  
  post: (endpoint, data, options = {}) => apiRequest(endpoint, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data)
  }),
  
  put: (endpoint, data, options = {}) => apiRequest(endpoint, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  
  patch: (endpoint, data, options = {}) => apiRequest(endpoint, {
    ...options,
    method: 'PATCH',
    body: JSON.stringify(data)
  }),
  
  delete: (endpoint, options = {}) => apiRequest(endpoint, { ...options, method: 'DELETE' })
};

/**
 * Upload file with progress tracking
 */
export async function uploadFile(endpoint, file, onProgress) {
  const url = `${BACKEND_URL}/api${endpoint}`;
  const token = localStorage.getItem('token');
  
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });
    }
    
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (e) {
          resolve(xhr.responseText);
        }
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`));
      }
    });
    
    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });
    
    xhr.addEventListener('abort', () => {
      reject(new Error('Upload cancelled'));
    });
    
    xhr.open('POST', url);
    if (token) {
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    xhr.send(formData);
  });
}

export default api;
