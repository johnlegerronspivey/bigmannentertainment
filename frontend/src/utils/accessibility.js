/**
 * Accessibility Utilities
 * Helps improve accessibility (a11y) across the application
 */

/**
 * Announce message to screen readers
 */
export const announceToScreenReader = (message, priority = 'polite') => {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority); // 'polite' or 'assertive'
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only'; // Screen reader only class
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

/**
 * Focus trap for modals
 * Traps keyboard focus within a container
 */
export class FocusTrap {
  constructor(element) {
    this.element = element;
    this.focusableElements = null;
    this.firstFocusable = null;
    this.lastFocusable = null;
  }
  
  activate() {
    // Get all focusable elements
    this.focusableElements = this.element.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    
    if (this.focusableElements.length === 0) return;
    
    this.firstFocusable = this.focusableElements[0];
    this.lastFocusable = this.focusableElements[this.focusableElements.length - 1];
    
    // Focus first element
    this.firstFocusable.focus();
    
    // Add event listener
    this.element.addEventListener('keydown', this.handleKeyDown);
  }
  
  deactivate() {
    this.element.removeEventListener('keydown', this.handleKeyDown);
  }
  
  handleKeyDown = (e) => {
    if (e.key !== 'Tab') return;
    
    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === this.firstFocusable) {
        e.preventDefault();
        this.lastFocusable.focus();
      }
    } else {
      // Tab
      if (document.activeElement === this.lastFocusable) {
        e.preventDefault();
        this.firstFocusable.focus();
      }
    }
  };
}

/**
 * Keyboard navigation helper
 * Handles arrow key navigation for lists and grids
 */
export const handleArrowKeyNavigation = (event, currentIndex, totalItems, options = {}) => {
  const {
    onNext,
    onPrevious,
    loop = true,
    orientation = 'vertical' // 'vertical' or 'horizontal'
  } = options;
  
  const nextKey = orientation === 'vertical' ? 'ArrowDown' : 'ArrowRight';
  const prevKey = orientation === 'vertical' ? 'ArrowUp' : 'ArrowLeft';
  
  if (event.key === nextKey) {
    event.preventDefault();
    let nextIndex = currentIndex + 1;
    if (nextIndex >= totalItems) {
      nextIndex = loop ? 0 : currentIndex;
    }
    onNext && onNext(nextIndex);
  } else if (event.key === prevKey) {
    event.preventDefault();
    let prevIndex = currentIndex - 1;
    if (prevIndex < 0) {
      prevIndex = loop ? totalItems - 1 : 0;
    }
    onPrevious && onPrevious(prevIndex);
  }
};

/**
 * Skip to main content link
 * Helps keyboard users skip navigation
 */
export const SkipToContent = ({ targetId = 'main-content' }) => {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-purple-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg"
    >
      Skip to main content
    </a>
  );
};

/**
 * Get ARIA label for button based on state
 */
export const getButtonAriaLabel = (action, state = {}) => {
  const { loading, disabled, count } = state;
  
  let label = action;
  
  if (loading) {
    label = `${action} in progress`;
  } else if (disabled) {
    label = `${action} (disabled)`;
  }
  
  if (count !== undefined) {
    label += ` (${count} items)`;
  }
  
  return label;
};

/**
 * Focus management utilities
 */
export const focusManagement = {
  /**
   * Store current focus to restore later
   */
  storeFocus() {
    return document.activeElement;
  },
  
  /**
   * Restore previously stored focus
   */
  restoreFocus(element) {
    if (element && element.focus) {
      element.focus();
    }
  },
  
  /**
   * Focus first error in form
   */
  focusFirstError(formElement) {
    const errorField = formElement.querySelector('[aria-invalid="true"]');
    if (errorField) {
      errorField.focus();
    }
  },
  
  /**
   * Move focus to element by ID
   */
  focusElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      // Make sure element is focusable
      if (!element.hasAttribute('tabindex')) {
        element.setAttribute('tabindex', '-1');
      }
      element.focus();
    }
  }
};

/**
 * Color contrast checker
 * Helps ensure text meets WCAG contrast requirements
 */
export const checkColorContrast = (foreground, background) => {
  // Convert hex to RGB
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  };
  
  // Calculate relative luminance
  const getLuminance = (rgb) => {
    const { r, g, b } = rgb;
    const [rs, gs, bs] = [r, g, b].map(val => {
      val = val / 255;
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };
  
  const fg = hexToRgb(foreground);
  const bg = hexToRgb(background);
  
  if (!fg || !bg) return null;
  
  const l1 = getLuminance(fg);
  const l2 = getLuminance(bg);
  
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  
  const contrast = (lighter + 0.05) / (darker + 0.05);
  
  return {
    ratio: contrast.toFixed(2),
    passAA: contrast >= 4.5,
    passAAA: contrast >= 7,
    passAALarge: contrast >= 3
  };
};

/**
 * Screen reader only CSS class helper
 * Creates a class that's visually hidden but readable by screen readers
 */
export const srOnlyClass = 'sr-only absolute -left-[10000px] w-[1px] h-[1px] overflow-hidden';

/**
 * Responsive image alt text generator
 * Generates contextual alt text based on image purpose
 */
export const generateAltText = (context, options = {}) => {
  const { decorative = false, filename, description } = options;
  
  if (decorative) {
    return ''; // Decorative images should have empty alt
  }
  
  if (description) {
    return description;
  }
  
  // Generate basic alt from filename
  if (filename) {
    return filename
      .replace(/\.[^/.]+$/, '') // Remove extension
      .replace(/[-_]/g, ' ') // Replace dashes/underscores with spaces
      .replace(/\b\w/g, l => l.toUpperCase()); // Capitalize words
  }
  
  return `Image in ${context} section`;
};

export default {
  announceToScreenReader,
  FocusTrap,
  handleArrowKeyNavigation,
  SkipToContent,
  getButtonAriaLabel,
  focusManagement,
  checkColorContrast,
  srOnlyClass,
  generateAltText
};
