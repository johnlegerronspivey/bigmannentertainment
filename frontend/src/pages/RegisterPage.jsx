import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    business_name: '',
    date_of_birth: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state_province: '',
    postal_code: '',
    country: 'US'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateAge = (dateOfBirth) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age >= 18;
  };

  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) {
      errors.push("Password must be at least 8 characters long");
    }
    if (!/[A-Z]/.test(password)) {
      errors.push("Password must contain at least one uppercase letter");
    }
    if (!/[a-z]/.test(password)) {
      errors.push("Password must contain at least one lowercase letter");
    }
    if (!/\d/.test(password)) {
      errors.push("Password must contain at least one number");
    }
    return errors;
  };

  const validateEmail = (email) => {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailPattern.test(email);
  };

  const handleNextStep = () => {
    if (step === 1) {
      if (!formData.email || !formData.password || !formData.full_name) {
        setError('Please fill in all required fields');
        return;
      }
      
      if (!validateEmail(formData.email)) {
        setError('Please enter a valid email address');
        return;
      }
      
      const passwordErrors = validatePassword(formData.password);
      if (passwordErrors.length > 0) {
        setError(passwordErrors.join('. '));
        return;
      }
      
      if (!formData.date_of_birth || !validateAge(formData.date_of_birth)) {
        setError('You must be 18 or older to register');
        return;
      }
      setError('');
      setStep(2);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!formData.address_line1 || !formData.city || !formData.state_province || !formData.postal_code) {
      setError('Please fill in all required address fields');
      setLoading(false);
      return;
    }

    const registrationData = {
      ...formData,
      date_of_birth: new Date(formData.date_of_birth).toISOString()
    };

    const result = await register(registrationData);
    
    if (result.success) {
      setSuccess('Account created successfully! Welcome to Big Mann Entertainment - Founded by John LeGerron Spivey!');
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-purple-100 flex items-center justify-center py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white rounded-2xl shadow-xl p-6 sm:p-8">
        <div className="text-center">
          <img 
            src="/big-mann-logo.png" 
            alt="Big Mann Entertainment Logo - Owned by John LeGerron Spivey" 
            className="w-16 h-16 sm:w-20 sm:h-20 object-contain mx-auto mb-4"
          />
          <h2 className="mt-4 sm:mt-6 text-center text-2xl sm:text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-sm sm:text-base text-gray-600">Big Mann Entertainment - Founded by John LeGerron Spivey</p>
        </div>

        <div className="mt-6 sm:mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-r shadow-sm">
              <div className="flex items-center">
                <span className="text-red-500 mr-2">⚠️</span>
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}
          
          {success && (
            <div className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-r shadow-sm">
              <div className="flex items-center">
                <span className="text-green-500 mr-2">✓</span>
                <span className="text-sm">{success}</span>
              </div>
            </div>
          )}

          {/* Enhanced Progress indicator */}
          <div className="flex items-center justify-center space-x-4 mb-6">
            <div className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${step >= 1 ? 'bg-purple-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                1
              </div>
              <span className="ml-2 text-xs sm:text-sm font-medium text-gray-700">Personal Info</span>
            </div>
            <div className="w-8 sm:w-12 h-1 bg-gray-300">
              <div className={`h-full transition-all duration-300 ${step >= 2 ? 'bg-purple-600 w-full' : 'w-0'}`}></div>
            </div>
            <div className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${step >= 2 ? 'bg-purple-600 text-white' : 'bg-gray-300 text-gray-600'}`}>
                2
              </div>
              <span className="ml-2 text-xs sm:text-sm font-medium text-gray-700">Address</span>
            </div>
          </div>

          {step === 1 && (
            <div className="space-y-5">
              <div>
                <label htmlFor="register-full-name" className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name <span className="text-red-500">*</span>
                </label>
                <input
                  id="register-full-name"
                  name="full_name"
                  type="text"
                  autoComplete="name"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label htmlFor="register-email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address <span className="text-red-500">*</span>
                </label>
                <input
                  id="register-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="john@example.com"
                />
              </div>

              <div>
                <label htmlFor="register-password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password <span className="text-red-500">*</span>
                </label>
                <input
                  id="register-password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="Create a strong password"
                />
                <p className="text-xs text-gray-500 mt-2 flex items-start">
                  <span className="mr-1">💡</span>
                  <span>Must be at least 8 characters with uppercase, lowercase, and number</span>
                </p>
              </div>

              <div>
                <label htmlFor="register-business-name" className="block text-sm font-medium text-gray-700 mb-2">
                  Business Name <span className="text-gray-400 text-xs">(Optional)</span>
                </label>
                <input
                  id="register-business-name"
                  name="business_name"
                  type="text"
                  autoComplete="organization"
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="Your business or artist name"
                />
              </div>

              <div>
                <label htmlFor="register-date-of-birth" className="block text-sm font-medium text-gray-700 mb-2">
                  Date of Birth <span className="text-red-500">*</span>
                </label>
                <input
                  id="register-date-of-birth"
                  name="date_of_birth"
                  type="date"
                  autoComplete="bday"
                  required
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
                <p className="text-xs text-gray-500 mt-2">You must be 18 or older to register</p>
              </div>

              <button
                type="button"
                onClick={handleNextStep}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg transition-all transform hover:scale-[1.02] shadow-md hover:shadow-lg"
              >
                Continue to Address →
              </button>
              
              <p className="text-center text-sm text-gray-600 mt-4">
                Already have an account? <Link to="/login" className="text-purple-600 hover:text-purple-700 font-semibold">Sign in</Link>
              </p>
            </div>
          )}

          {step === 2 && (
            <form onSubmit={handleRegister} className="space-y-5">
              <div>
                <label htmlFor="register-address-line1" className="block text-sm font-medium text-gray-700 mb-2">
                  Street Address <span className="text-red-500">*</span>
                </label>
                <input
                  id="register-address-line1"
                  name="address_line1"
                  type="text"
                  autoComplete="address-line1"
                  required
                  value={formData.address_line1}
                  onChange={(e) => setFormData({ ...formData, address_line1: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="123 Main Street"
                />
              </div>

              <div>
                <label htmlFor="register-address-line2" className="block text-sm font-medium text-gray-700 mb-2">
                  Address Line 2 <span className="text-gray-400 text-xs">(Optional)</span>
                </label>
                <input
                  id="register-address-line2"
                  name="address_line2"
                  type="text"
                  autoComplete="address-line2"
                  value={formData.address_line2}
                  onChange={(e) => setFormData({ ...formData, address_line2: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  placeholder="Apartment, suite, etc."
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="register-city" className="block text-sm font-medium text-gray-700 mb-2">
                    City <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="register-city"
                    name="city"
                    type="text"
                    autoComplete="address-level2"
                    required
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    placeholder="Los Angeles"
                  />
                </div>
                <div>
                  <label htmlFor="register-state-province" className="block text-sm font-medium text-gray-700 mb-2">
                    State/Province <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="register-state-province"
                    name="state_province"
                    type="text"
                    autoComplete="address-level1"
                    required
                    value={formData.state_province}
                    onChange={(e) => setFormData({ ...formData, state_province: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    placeholder="CA"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="register-postal-code" className="block text-sm font-medium text-gray-700 mb-2">
                    Postal Code <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="register-postal-code"
                    name="postal_code"
                    type="text"
                    autoComplete="postal-code"
                    required
                    value={formData.postal_code}
                    onChange={(e) => setFormData({ ...formData, postal_code: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    placeholder="90001"
                  />
                </div>
                <div>
                  <label htmlFor="register-country" className="block text-sm font-medium text-gray-700 mb-2">
                    Country <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="register-country"
                    name="country"
                    autoComplete="country"
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  >
                  <option value="US">United States</option>
                  <option value="CA">Canada</option>
                  <option value="UK">United Kingdom</option>
                  <option value="AU">Australia</option>
                  <option value="DE">Germany</option>
                  <option value="FR">France</option>
                  <option value="ES">Spain</option>
                  <option value="IT">Italy</option>
                  <option value="NL">Netherlands</option>
                  <option value="SE">Sweden</option>
                  <option value="NO">Norway</option>
                  <option value="DK">Denmark</option>
                  <option value="JP">Japan</option>
                  <option value="KR">South Korea</option>
                  <option value="BR">Brazil</option>
                  <option value="MX">Mexico</option>
                  <option value="IN">India</option>
                  <option value="NG">Nigeria</option>
                  <option value="ZA">South Africa</option>
                  <option value="NZ">New Zealand</option>
                </select>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mt-6">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="w-full sm:flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 px-4 rounded-lg transition-all shadow-sm hover:shadow-md"
                >
                  ← Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full sm:flex-1 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-md hover:shadow-lg transform hover:scale-[1.02]"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Account...
                    </>
                  ) : (
                    'Create Account'
                  )}
                </button>
              </div>
            </form>
          )}

          <div className="text-center">
            <Link to="/login" className="text-purple-600 hover:text-purple-500">
              Already have an account? Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
