import React from 'react';

/**
 * Performance Utility
 * Provides utilities for optimizing React component performance
 */

/**
 * Debounce function - delays execution until after wait time has elapsed
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function - ensures function is called at most once in specified time period
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
export const throttle = (func, limit = 300) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Lazy load images - only load images when they're in viewport
 * @param {string} src - Image source
 * @param {string} placeholder - Placeholder image
 * @returns {Object} Image loading state
 */
export const useLazyImage = (src, placeholder = '') => {
  const [imageSrc, setImageSrc] = React.useState(placeholder);
  const [imageRef, setImageRef] = React.useState();

  React.useEffect(() => {
    let observer;
    if (imageRef && 'IntersectionObserver' in window) {
      observer = new IntersectionObserver(
        entries => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              setImageSrc(src);
              observer.unobserve(imageRef);
            }
          });
        },
        {
          rootMargin: '50px'
        }
      );
      observer.observe(imageRef);
    } else {
      // Fallback for browsers without IntersectionObserver
      setImageSrc(src);
    }

    return () => {
      if (observer && observer.unobserve && imageRef) {
        observer.unobserve(imageRef);
      }
    };
  }, [src, imageRef, placeholder]);

  return { imageSrc, setImageRef };
};

/**
 * Measure component render time (development only)
 * @param {string} componentName - Name of the component
 * @param {Function} callback - Optional callback with render time
 */
export const measureRenderTime = (componentName, callback) => {
  if (process.env.NODE_ENV === 'development') {
    React.useEffect(() => {
      const startTime = performance.now();
      return () => {
        const endTime = performance.now();
        const renderTime = endTime - startTime;
        console.log(`[Performance] ${componentName} rendered in ${renderTime.toFixed(2)}ms`);
        if (callback) callback(renderTime);
      };
    });
  }
};

/**
 * Cache API responses in sessionStorage
 * @param {string} key - Cache key
 * @param {Function} fetchFunction - Function to fetch data
 * @param {number} ttl - Time to live in milliseconds (default: 5 minutes)
 * @returns {Promise} Cached or fresh data
 */
export const cacheAPIResponse = async (key, fetchFunction, ttl = 5 * 60 * 1000) => {
  try {
    const cached = sessionStorage.getItem(key);
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;
      if (age < ttl) {
        console.log(`[Cache] Using cached data for ${key}`);
        return data;
      }
    }
  } catch (error) {
    console.error('[Cache] Error reading from cache:', error);
  }

  // Fetch fresh data
  const data = await fetchFunction();
  
  try {
    sessionStorage.setItem(key, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
  } catch (error) {
    console.error('[Cache] Error writing to cache:', error);
  }

  return data;
};

/**
 * Clear cache by key or all cache
 * @param {string} key - Optional key to clear specific cache
 */
export const clearCache = (key = null) => {
  if (key) {
    sessionStorage.removeItem(key);
  } else {
    sessionStorage.clear();
  }
};
