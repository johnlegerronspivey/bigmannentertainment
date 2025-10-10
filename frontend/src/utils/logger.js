/**
 * Development Logger Utility
 * Only logs in development mode, removes console statements in production
 */

const isDevelopment = process.env.NODE_ENV === 'development';

const logger = {
  log: (...args) => {
    if (isDevelopment) {
      console.log('[BME]', ...args);
    }
  },
  
  info: (...args) => {
    if (isDevelopment) {
      console.info('[BME INFO]', ...args);
    }
  },
  
  warn: (...args) => {
    if (isDevelopment) {
      console.warn('[BME WARN]', ...args);
    }
  },
  
  error: (...args) => {
    // Always log errors, even in production
    console.error('[BME ERROR]', ...args);
  },
  
  debug: (...args) => {
    if (isDevelopment) {
      console.debug('[BME DEBUG]', ...args);
    }
  }
};

export default logger;
