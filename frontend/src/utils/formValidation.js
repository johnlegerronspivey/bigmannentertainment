/**
 * Frontend Form Validation Utilities
 * Provides real-time validation with user-friendly error messages
 */

/**
 * Email validation
 */
export const validateEmail = (email) => {
  if (!email) {
    return { valid: false, message: 'Email is required' };
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, message: 'Please enter a valid email address' };
  }
  
  return { valid: true };
};

/**
 * Password strength validation
 */
export const validatePassword = (password) => {
  if (!password) {
    return { valid: false, message: 'Password is required' };
  }
  
  const errors = [];
  
  if (password.length < 8) {
    errors.push('at least 8 characters');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('one uppercase letter');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('one lowercase letter');
  }
  
  if (!/[0-9]/.test(password)) {
    errors.push('one number');
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('one special character');
  }
  
  if (errors.length > 0) {
    return {
      valid: false,
      message: `Password must contain ${errors.join(', ')}`
    };
  }
  
  return { valid: true };
};

/**
 * Password confirmation validation
 */
export const validatePasswordMatch = (password, confirmPassword) => {
  if (!confirmPassword) {
    return { valid: false, message: 'Please confirm your password' };
  }
  
  if (password !== confirmPassword) {
    return { valid: false, message: 'Passwords do not match' };
  }
  
  return { valid: true };
};

/**
 * Required field validation
 */
export const validateRequired = (value, fieldName = 'This field') => {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return { valid: false, message: `${fieldName} is required` };
  }
  return { valid: true };
};

/**
 * Minimum length validation
 */
export const validateMinLength = (value, minLength, fieldName = 'This field') => {
  if (!value || value.length < minLength) {
    return {
      valid: false,
      message: `${fieldName} must be at least ${minLength} characters`
    };
  }
  return { valid: true };
};

/**
 * Maximum length validation
 */
export const validateMaxLength = (value, maxLength, fieldName = 'This field') => {
  if (value && value.length > maxLength) {
    return {
      valid: false,
      message: `${fieldName} must not exceed ${maxLength} characters`
    };
  }
  return { valid: true };
};

/**
 * URL validation
 */
export const validateURL = (url) => {
  if (!url) {
    return { valid: false, message: 'URL is required' };
  }
  
  try {
    new URL(url);
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      return { valid: false, message: 'URL must start with http:// or https://' };
    }
    return { valid: true };
  } catch (error) {
    return { valid: false, message: 'Please enter a valid URL' };
  }
};

/**
 * Phone number validation
 */
export const validatePhone = (phone) => {
  if (!phone) {
    return { valid: false, message: 'Phone number is required' };
  }
  
  const phoneRegex = /^[\d\s\-\+\(\)]+$/;
  if (!phoneRegex.test(phone)) {
    return { valid: false, message: 'Please enter a valid phone number' };
  }
  
  const digitsOnly = phone.replace(/\D/g, '');
  if (digitsOnly.length < 10) {
    return { valid: false, message: 'Phone number must have at least 10 digits' };
  }
  
  return { valid: true };
};

/**
 * Number validation
 */
export const validateNumber = (value, options = {}) => {
  const { min, max, integer = false, fieldName = 'This field' } = options;
  
  if (!value && value !== 0) {
    return { valid: false, message: `${fieldName} is required` };
  }
  
  const num = Number(value);
  if (isNaN(num)) {
    return { valid: false, message: `${fieldName} must be a valid number` };
  }
  
  if (integer && !Number.isInteger(num)) {
    return { valid: false, message: `${fieldName} must be a whole number` };
  }
  
  if (min !== undefined && num < min) {
    return { valid: false, message: `${fieldName} must be at least ${min}` };
  }
  
  if (max !== undefined && num > max) {
    return { valid: false, message: `${fieldName} must not exceed ${max}` };
  }
  
  return { valid: true };
};

/**
 * Date validation
 */
export const validateDate = (date, options = {}) => {
  const { min, max, future = false, past = false, fieldName = 'Date' } = options;
  
  if (!date) {
    return { valid: false, message: `${fieldName} is required` };
  }
  
  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) {
    return { valid: false, message: 'Please enter a valid date' };
  }
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  if (future && dateObj <= today) {
    return { valid: false, message: `${fieldName} must be in the future` };
  }
  
  if (past && dateObj >= today) {
    return { valid: false, message: `${fieldName} must be in the past` };
  }
  
  if (min && dateObj < new Date(min)) {
    return { valid: false, message: `${fieldName} must be after ${new Date(min).toLocaleDateString()}` };
  }
  
  if (max && dateObj > new Date(max)) {
    return { valid: false, message: `${fieldName} must be before ${new Date(max).toLocaleDateString()}` };
  }
  
  return { valid: true };
};

/**
 * File validation
 */
export const validateFile = (file, options = {}) => {
  const {
    maxSize = 10 * 1024 * 1024, // 10MB default
    allowedTypes = [],
    fieldName = 'File'
  } = options;
  
  if (!file) {
    return { valid: false, message: `${fieldName} is required` };
  }
  
  // Check file size
  if (file.size > maxSize) {
    const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(2);
    return {
      valid: false,
      message: `${fieldName} size must not exceed ${maxSizeMB}MB`
    };
  }
  
  // Check file type
  if (allowedTypes.length > 0) {
    const fileExt = file.name.split('.').pop().toLowerCase();
    const fileType = file.type.toLowerCase();
    
    const isAllowed = allowedTypes.some(type => 
      fileType.includes(type) || fileExt === type
    );
    
    if (!isAllowed) {
      return {
        valid: false,
        message: `${fieldName} must be one of: ${allowedTypes.join(', ')}`
      };
    }
  }
  
  return { valid: true };
};

/**
 * Form validation helper
 * Validates multiple fields at once
 */
export const validateForm = (fields, validationRules) => {
  const errors = {};
  let isValid = true;
  
  Object.keys(validationRules).forEach(fieldName => {
    const rules = validationRules[fieldName];
    const value = fields[fieldName];
    
    for (const rule of rules) {
      const result = rule(value);
      if (!result.valid) {
        errors[fieldName] = result.message;
        isValid = false;
        break; // Stop at first error for this field
      }
    }
  });
  
  return { isValid, errors };
};

/**
 * Real-time field validation
 * Returns a function that validates on input change
 */
export const createFieldValidator = (validationRules) => {
  return (fieldName, value) => {
    const rules = validationRules[fieldName];
    if (!rules) return { valid: true };
    
    for (const rule of rules) {
      const result = rule(value);
      if (!result.valid) {
        return result;
      }
    }
    
    return { valid: true };
  };
};

export default {
  validateEmail,
  validatePassword,
  validatePasswordMatch,
  validateRequired,
  validateMinLength,
  validateMaxLength,
  validateURL,
  validatePhone,
  validateNumber,
  validateDate,
  validateFile,
  validateForm,
  createFieldValidator
};
