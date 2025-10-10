/**
 * Form Validation Utilities
 * Provides comprehensive validation functions for forms
 */

/**
 * Email validation
 * @param {string} email - Email to validate
 * @returns {Object} Validation result
 */
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValid = emailRegex.test(email);
  
  return {
    isValid,
    message: isValid ? '' : 'Please enter a valid email address'
  };
};

/**
 * Password validation
 * @param {string} password - Password to validate
 * @param {Object} options - Validation options
 * @returns {Object} Validation result
 */
export const validatePassword = (password, options = {}) => {
  const {
    minLength = 8,
    requireUppercase = true,
    requireLowercase = true,
    requireNumber = true,
    requireSpecialChar = true
  } = options;

  const errors = [];

  if (password.length < minLength) {
    errors.push(`Password must be at least ${minLength} characters long`);
  }

  if (requireUppercase && !/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (requireLowercase && !/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (requireNumber && !/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  if (requireSpecialChar && !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  return {
    isValid: errors.length === 0,
    errors,
    message: errors.join('. ')
  };
};

/**
 * URL validation
 * @param {string} url - URL to validate
 * @returns {Object} Validation result
 */
export const validateURL = (url) => {
  try {
    new URL(url);
    return {
      isValid: true,
      message: ''
    };
  } catch (error) {
    return {
      isValid: false,
      message: 'Please enter a valid URL'
    };
  }
};

/**
 * Phone number validation (US format)
 * @param {string} phone - Phone number to validate
 * @returns {Object} Validation result
 */
export const validatePhone = (phone) => {
  const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
  const isValid = phoneRegex.test(phone.replace(/\s/g, ''));
  
  return {
    isValid,
    message: isValid ? '' : 'Please enter a valid phone number'
  };
};

/**
 * Required field validation
 * @param {any} value - Value to validate
 * @param {string} fieldName - Name of the field
 * @returns {Object} Validation result
 */
export const validateRequired = (value, fieldName = 'This field') => {
  const isValid = value !== undefined && value !== null && value !== '';
  
  return {
    isValid,
    message: isValid ? '' : `${fieldName} is required`
  };
};

/**
 * Number range validation
 * @param {number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {Object} Validation result
 */
export const validateRange = (value, min, max) => {
  const numValue = Number(value);
  const isValid = !isNaN(numValue) && numValue >= min && numValue <= max;
  
  return {
    isValid,
    message: isValid ? '' : `Value must be between ${min} and ${max}`
  };
};

/**
 * File size validation
 * @param {File} file - File to validate
 * @param {number} maxSizeMB - Maximum size in MB
 * @returns {Object} Validation result
 */
export const validateFileSize = (file, maxSizeMB = 50) => {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  const isValid = file && file.size <= maxSizeBytes;
  
  return {
    isValid,
    message: isValid ? '' : `File size must be less than ${maxSizeMB}MB`
  };
};

/**
 * File type validation
 * @param {File} file - File to validate
 * @param {Array} allowedTypes - Allowed MIME types
 * @returns {Object} Validation result
 */
export const validateFileType = (file, allowedTypes = []) => {
  const isValid = file && allowedTypes.includes(file.type);
  
  return {
    isValid,
    message: isValid ? '' : `File type must be one of: ${allowedTypes.join(', ')}`
  };
};

/**
 * ISRC validation (International Standard Recording Code)
 * @param {string} isrc - ISRC to validate
 * @returns {Object} Validation result
 */
export const validateISRC = (isrc) => {
  // Format: CC-XXX-YY-NNNNN or CCXXXYYNNNNN
  const isrcRegex = /^[A-Z]{2}-?[A-Z0-9]{3}-?\d{2}-?\d{5}$/;
  const isValid = isrcRegex.test(isrc);
  
  return {
    isValid,
    message: isValid ? '' : 'Please enter a valid ISRC code (e.g., US-S1Z-99-00001)'
  };
};

/**
 * Comprehensive form validation
 * @param {Object} formData - Form data object
 * @param {Object} validationRules - Validation rules object
 * @returns {Object} Validation result with errors per field
 */
export const validateForm = (formData, validationRules) => {
  const errors = {};
  let isValid = true;

  Object.keys(validationRules).forEach(field => {
    const rules = validationRules[field];
    const value = formData[field];

    rules.forEach(rule => {
      const { validator, message } = rule;
      const result = validator(value);
      
      if (!result.isValid) {
        isValid = false;
        if (!errors[field]) {
          errors[field] = [];
        }
        errors[field].push(message || result.message);
      }
    });
  });

  return {
    isValid,
    errors
  };
};
