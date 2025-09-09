import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

// Agency Registration Wizard
export const AgencyRegistrationWizard = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    business_registration_number: '',
    contact_info: {
      email: '',
      phone: '',
      address: '',
      city: '',
      country: '',
      postal_code: ''
    },
    wallet_addresses: {
      ethereum: '',
      solana: ''
    },
    business_type: '',
    tax_id: '',
    operating_countries: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const steps = [
    { id: 1, title: 'Business Information', description: 'Basic agency details' },
    { id: 2, title: 'Contact Details', description: 'Communication information' },
    { id: 3, title: 'Blockchain Wallets', description: 'Cryptocurrency addresses' },
    { id: 4, title: 'Business Registration', description: 'Legal and tax information' },
    { id: 5, title: 'Review & Submit', description: 'Confirm and register' }
  ];

  const countries = [
    'United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Italy', 'Spain',
    'Australia', 'Japan', 'South Korea', 'Brazil', 'Mexico', 'India', 'China'
  ];

  const businessTypes = [
    'Modeling Agency', 'Talent Agency', 'Photography Studio', 'Creative Agency',
    'Entertainment Company', 'Media Production', 'Influencer Management', 'Other'
  ];

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 5));
    }
  };

  const handlePrev = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const validateStep = (step) => {
    switch (step) {
      case 1:
        if (!formData.name.trim()) {
          setError('Agency name is required');
          return false;
        }
        break;
      case 2:
        const { email, phone, address } = formData.contact_info;
        if (!email || !phone || !address) {
          setError('All contact fields are required');
          return false;
        }
        if (!email.includes('@')) {
          setError('Please enter a valid email address');
          return false;
        }
        break;
      case 3:
        const { ethereum, solana } = formData.wallet_addresses;
        if (!ethereum && !solana) {
          setError('At least one wallet address is required');
          return false;
        }
        if (ethereum && !ethereum.startsWith('0x')) {
          setError('Invalid Ethereum wallet address');
          return false;
        }
        break;
      case 4:
        if (!formData.business_type) {
          setError('Business type is required');
          return false;
        }
        break;
    }
    setError('');
    return true;
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/agency/register`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.status === 'registered') {
        navigate('/agency/dashboard');
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Business Information</h3>
            <div>
              <label className="block text-sm font-medium mb-2">Agency Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => updateFormData('name', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Enter your agency name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Business Registration Number</label>
              <input
                type="text"
                value={formData.business_registration_number}
                onChange={(e) => updateFormData('business_registration_number', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Optional registration number"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Contact Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Email Address *</label>
                <input
                  type="email"
                  value={formData.contact_info.email}
                  onChange={(e) => updateFormData('contact_info.email', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="contact@agency.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Phone Number *</label>
                <input
                  type="tel"
                  value={formData.contact_info.phone}
                  onChange={(e) => updateFormData('contact_info.phone', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Business Address *</label>
              <textarea
                value={formData.contact_info.address}
                onChange={(e) => updateFormData('contact_info.address', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                rows={3}
                placeholder="Street address, city, state/province"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">City</label>
                <input
                  type="text"
                  value={formData.contact_info.city}
                  onChange={(e) => updateFormData('contact_info.city', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Country</label>
                <select
                  value={formData.contact_info.country}
                  onChange={(e) => updateFormData('contact_info.country', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Select Country</option>
                  {countries.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Postal Code</label>
                <input
                  type="text"
                  value={formData.contact_info.postal_code}
                  onChange={(e) => updateFormData('contact_info.postal_code', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Blockchain Wallets</h3>
            <p className="text-sm text-gray-600">
              Add your cryptocurrency wallet addresses for receiving license payments and royalties.
            </p>
            <div>
              <label className="block text-sm font-medium mb-2">
                Ethereum Wallet Address
                <span className="text-gray-500 ml-1">(0x...)</span>
              </label>
              <input
                type="text"
                value={formData.wallet_addresses.ethereum}
                onChange={(e) => updateFormData('wallet_addresses.ethereum', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="0x742d35Cc74C3590f54321B53B4c0E8c7..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Solana Wallet Address
                <span className="text-gray-500 ml-1">(Base58)</span>
              </label>
              <input
                type="text"
                value={formData.wallet_addresses.solana}
                onChange={(e) => updateFormData('wallet_addresses.solana', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
              />
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-blue-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-blue-900">Wallet Security</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Only provide wallet addresses you control. Never share private keys or seed phrases.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Business Registration</h3>
            <div>
              <label className="block text-sm font-medium mb-2">Business Type *</label>
              <select
                value={formData.business_type}
                onChange={(e) => updateFormData('business_type', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              >
                <option value="">Select Business Type</option>
                {businessTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Tax ID / EIN</label>
              <input
                type="text"
                value={formData.tax_id}
                onChange={(e) => updateFormData('tax_id', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Optional tax identification number"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Operating Countries</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-40 overflow-y-auto border border-gray-300 rounded-md p-3">
                {countries.map(country => (
                  <label key={country} className="flex items-center text-sm">
                    <input
                      type="checkbox"
                      checked={formData.operating_countries.includes(country)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          updateFormData('operating_countries', [...formData.operating_countries, country]);
                        } else {
                          updateFormData('operating_countries', formData.operating_countries.filter(c => c !== country));
                        }
                      }}
                      className="mr-2"
                    />
                    {country}
                  </label>
                ))}
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Review & Submit</h3>
            <div className="bg-gray-50 rounded-lg p-6 space-y-4">
              <div>
                <h4 className="font-medium text-gray-900">Agency Name</h4>
                <p className="text-gray-700">{formData.name}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Contact Email</h4>
                <p className="text-gray-700">{formData.contact_info.email}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Business Type</h4>
                <p className="text-gray-700">{formData.business_type}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Blockchain Wallets</h4>
                <div className="text-sm text-gray-700">
                  {formData.wallet_addresses.ethereum && (
                    <p>Ethereum: {formData.wallet_addresses.ethereum.substring(0, 10)}...</p>
                  )}
                  {formData.wallet_addresses.solana && (
                    <p>Solana: {formData.wallet_addresses.solana.substring(0, 10)}...</p>
                  )}
                </div>
              </div>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-yellow-400 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-yellow-900">Next Steps</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    After registration, you'll need to complete KYC verification by uploading business documents.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Agency Registration</h1>
        <p className="text-gray-600">Join Big Mann Entertainment's blockchain-powered licensing platform</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                currentStep >= step.id 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {currentStep > step.id ? '✓' : step.id}
              </div>
              <div className="mt-2 text-center">
                <div className="text-sm font-medium text-gray-900">{step.title}</div>
                <div className="text-xs text-gray-500">{step.description}</div>
              </div>
              {index < steps.length - 1 && (
                <div className={`hidden md:block w-full h-1 mt-4 ${
                  currentStep > step.id ? 'bg-purple-600' : 'bg-gray-200'
                }`} style={{ marginLeft: '50px', marginRight: '50px' }} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form Content */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {renderStep()}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8 pt-6 border-t">
          <button
            onClick={handlePrev}
            disabled={currentStep === 1}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          {currentStep < 5 ? (
            <button
              onClick={handleNext}
              className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Registering...' : 'Register Agency'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// Agency Dashboard
export const AgencyDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/agency/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data.dashboard);
    } catch (error) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  const { agency_info, statistics, verification_needed } = dashboardData;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-800 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">{agency_info.name}</h1>
        <div className="flex items-center space-x-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            agency_info.verification_status === 'verified' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {agency_info.verification_status === 'verified' ? 'Verified' : 'Pending Verification'}
          </span>
          {agency_info.kyc_completed && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              KYC Complete
            </span>
          )}
        </div>
      </div>

      {/* Verification Alert */}
      {verification_needed && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-yellow-400 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-yellow-900">Verification Required</h3>
              <p className="text-sm text-yellow-700 mt-1">
                Complete your KYC verification to start licensing assets and receiving payments.
              </p>
              <button className="mt-2 text-sm text-yellow-900 underline hover:text-yellow-800">
                Upload Documents
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{statistics.total_talent}</div>
              <div className="text-sm text-gray-600">Total Talent</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{statistics.total_assets}</div>
              <div className="text-sm text-gray-600">Licensed Assets</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">{statistics.deployed_contracts}</div>
              <div className="text-sm text-gray-600">Active Contracts</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-full">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-4">
              <div className="text-2xl font-bold text-gray-900">${statistics.total_revenue.toFixed(2)}</div>
              <div className="text-sm text-gray-600">Total Revenue</div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-medium">Add Talent</div>
              <div className="text-sm text-gray-600">Register new talent</div>
            </div>
          </button>

          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-medium">Upload Assets</div>
              <div className="text-sm text-gray-600">Add portfolio images</div>
            </div>
          </button>

          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="font-medium">Create License</div>
              <div className="text-sm text-gray-600">New smart contract</div>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        {dashboardData.recent_activity && dashboardData.recent_activity.length > 0 ? (
          <div className="space-y-3">
            {dashboardData.recent_activity.slice(0, 5).map((activity, index) => (
              <div key={index} className="flex items-center text-sm">
                <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
                <span className="text-gray-600">
                  {activity.action} - {new Date(activity.timestamp).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No recent activity</p>
        )}
      </div>
    </div>
  );
};

export default { AgencyRegistrationWizard, AgencyDashboard };