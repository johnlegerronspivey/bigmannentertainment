import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Tax Dashboard - Main overview for tax management
export const TaxDashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTaxDashboard();
  }, [selectedYear]);

  const fetchTaxDashboard = async () => {
    try {
      const response = await axios.get(`${API}/tax/dashboard/${selectedYear}`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching tax dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate1099s = async () => {
    try {
      const response = await axios.post(`${API}/tax/generate-1099s/${selectedYear}`);
      alert(`Successfully generated ${response.data.forms_generated} 1099 forms!`);
      fetchTaxDashboard(); // Refresh data
    } catch (error) {
      alert('Failed to generate 1099s. Please try again.');
    }
  };

  const handleGenerateAnnualReport = async () => {
    try {
      const response = await axios.post(`${API}/tax/reports/annual/${selectedYear}`);
      alert('Annual tax report generated successfully!');
      fetchTaxDashboard(); // Refresh data
    } catch (error) {
      alert('Failed to generate annual report. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading tax dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Tax Management Dashboard</h1>
              <p className="text-gray-600">EIN: {dashboardData.business_ein || '270658077'}</p>
            </div>
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Tax Year:</label>
              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {[2024, 2023, 2022, 2021, 2020].map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Payments</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${(dashboardData.overview?.total_payments || 0).toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Taxable Payments</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${(dashboardData.overview?.taxable_payments || 0).toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">1099s Generated</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.overview?.forms_generated || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Recipients</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.overview?.total_recipients || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Payment Categories */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Payment Categories</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Nonemployee Compensation</span>
                  <span className="font-medium">
                    ${(dashboardData.payment_categories?.nonemployee_compensation || 0).toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Royalties</span>
                  <span className="font-medium">
                    ${(dashboardData.payment_categories?.royalties || 0).toFixed(2)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">Other Income</span>
                  <span className="font-medium">
                    ${(dashboardData.payment_categories?.other_income || 0).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <button
                  onClick={handleGenerate1099s}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
                >
                  Generate 1099 Forms for {selectedYear}
                </button>
                <button
                  onClick={handleGenerateAnnualReport}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
                >
                  Generate Annual Report
                </button>
                <button
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
                >
                  Export to Accounting System
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Compliance Status */}
        {dashboardData.compliance && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Compliance Status</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {dashboardData.compliance.compliance_score}%
                  </div>
                  <p className="text-gray-600">Compliance Score</p>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900 mb-2">
                    {dashboardData.compliance.current_tax_year}
                  </div>
                  <p className="text-gray-600">Current Tax Year</p>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900 mb-2">
                    {dashboardData.compliance.business_ein}
                  </div>
                  <p className="text-gray-600">Business EIN</p>
                </div>
              </div>

              {dashboardData.compliance.recommendations && (
                <div className="mt-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Recommendations:</h3>
                  <ul className="space-y-2">
                    {dashboardData.compliance.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-600 mr-2">•</span>
                        <span className="text-gray-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// 1099 Forms Management
export const Form1099Management = () => {
  const [forms, setForms] = useState([]);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    document_type: '',
    status: ''
  });

  useEffect(() => {
    fetchForms();
  }, [selectedYear, filters]);

  const fetchForms = async () => {
    try {
      const params = new URLSearchParams();
      params.append('tax_year', selectedYear.toString());
      if (filters.document_type) params.append('document_type', filters.document_type);
      if (filters.status) params.append('status', filters.status);

      const response = await axios.get(`${API}/tax/1099s?${params}`);
      setForms(response.data.forms);
    } catch (error) {
      console.error('Error fetching 1099 forms:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-800',
      'generated': 'bg-blue-100 text-blue-800',
      'sent': 'bg-green-100 text-green-800',
      'filed': 'bg-purple-100 text-purple-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading 1099 forms...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">1099 Forms Management</h1>
          <p className="text-gray-600">Manage and generate 1099 tax forms for recipients</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tax Year</label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {[2024, 2023, 2022, 2021].map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Document Type</label>
                <select
                  value={filters.document_type}
                  onChange={(e) => setFilters({ ...filters, document_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">All Types</option>
                  <option value="1099-NEC">1099-NEC</option>
                  <option value="1099-MISC">1099-MISC</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">All Status</option>
                  <option value="draft">Draft</option>
                  <option value="generated">Generated</option>
                  <option value="sent">Sent</option>
                  <option value="filed">Filed</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={fetchForms}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Forms Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">1099 Forms</h2>
              <div className="text-sm text-gray-500">
                {forms.length} forms for {selectedYear}
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            {forms.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No 1099 forms found</h3>
                <p className="mt-1 text-sm text-gray-500">Generate forms for tax year {selectedYear} to get started.</p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recipient</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generated</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {forms.map((form) => (
                    <tr key={form.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{form.recipient_name}</div>
                        <div className="text-sm text-gray-500">{form.recipient_ein_ssn || 'No TIN on file'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {form.document_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${(form.total_payments || 0).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(form.status)}`}>
                          {form.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {form.generated_date ? new Date(form.generated_date).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-purple-600 hover:text-purple-900 mr-3">View</button>
                        <button className="text-blue-600 hover:text-blue-900 mr-3">Download</button>
                        {form.status === 'generated' && (
                          <button className="text-green-600 hover:text-green-900">Send</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tax Reports Interface
export const TaxReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  useEffect(() => {
    fetchReports();
  }, [selectedYear]);

  const fetchReports = async () => {
    try {
      const response = await axios.get(`${API}/tax/reports?tax_year=${selectedYear}`);
      setReports(response.data.reports);
    } catch (error) {
      console.error('Error fetching tax reports:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading tax reports...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Tax Reports</h1>
              <p className="text-gray-600">Generate and manage tax reports for compliance</p>
            </div>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {[2024, 2023, 2022, 2021].map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Reports Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Generated Reports</h2>
          </div>

          <div className="overflow-x-auto">
            {reports.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No reports found</h3>
                <p className="mt-1 text-sm text-gray-500">Generate your first tax report to get started.</p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Period</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Payments</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recipients</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generated</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {reports.map((report) => (
                    <tr key={report.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {report.report_type.replace('_', ' ').toUpperCase()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(report.period_start).toLocaleDateString()} - {new Date(report.period_end).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${(report.total_payments || 0).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {report.total_recipients || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {report.generated_date ? new Date(report.generated_date).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-purple-600 hover:text-purple-900 mr-3">View</button>
                        <button className="text-blue-600 hover:text-blue-900">Download</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Business Tax Information Management with License Details
export const BusinessTaxInfo = () => {
  const [businessInfo, setBusinessInfo] = useState({
    business_name: 'Big Mann Entertainment',
    ein: '270658077',
    tin: '270658077',
    business_license_number: '',
    license_type: 'Entertainment/Media Production',
    license_state: 'AL',
    license_expiration: '',
    
    // Primary Business Address
    address_line1: '1314 Lincoln Heights Street',
    address_line2: '',
    city: 'Alexander City',
    state: 'AL',
    zip_code: '35010',
    county: 'Tallapoosa County',
    country: 'United States',
    
    // Mailing Address
    mailing_address_same: true,
    mailing_address_line1: '',
    mailing_address_line2: '',
    mailing_city: '',
    mailing_state: '',
    mailing_zip_code: '',
    mailing_country: '',
    
    // Business Details
    business_type: 'corporation',
    tax_classification: 'c_corporation',
    naics_code: '512200',
    sic_code: '7812',
    
    // Incorporation Details
    incorporation_state: 'AL',
    incorporation_date: '',
    state_id_number: '',
    
    // Contact Information
    contact_name: 'John LeGerron Spivey',
    contact_title: 'CEO',
    contact_phone: '334-669-8638',
    contact_email: '',
    
    // Business Operations
    business_description: 'Digital media distribution and entertainment services',
    primary_business_activity: 'Media Distribution Platform',
    date_business_started: '',
    fiscal_year_end: 'December 31',
    
    // Tax Settings
    default_backup_withholding: false,
    auto_generate_1099s: true,
    quarterly_filing_required: true,
    
    // License Status
    license_status: 'active',
    compliance_status: 'compliant',
    
    // Additional Registrations
    dba_names: [],
    federal_tax_deposits: true,
    state_tax_registration: true,
    sales_tax_permit: ''
  });

  const [activeTab, setActiveTab] = useState('basic');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchBusinessInfo();
  }, []);

  const fetchBusinessInfo = async () => {
    try {
      const response = await axios.get(`${API}/tax/business-info`);
      if (response.data.business_info) {
        setBusinessInfo(response.data.business_info);
      }
    } catch (error) {
      console.error('Error fetching business info:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');

    try {
      await axios.put(`${API}/tax/business-info`, businessInfo);
      setMessage('Business tax and license information updated successfully!');
    } catch (error) {
      setMessage('Failed to update business information. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleMailingAddressToggle = (checked) => {
    setBusinessInfo(prev => ({
      ...prev,
      mailing_address_same: checked,
      ...(checked ? {
        mailing_address_line1: '',
        mailing_address_line2: '',
        mailing_city: '',
        mailing_state: '',
        mailing_zip_code: '',
        mailing_country: ''
      } : {})
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading business information...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Business Tax & License Information</h1>
          <p className="text-gray-600">Manage comprehensive business details, tax information, and licensing</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-md ${
            message.includes('successfully') 
              ? 'bg-green-100 border border-green-400 text-green-700'
              : 'bg-red-100 border border-red-400 text-red-700'
          }`}>
            {message}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'basic', label: 'Basic Information', icon: '🏢' },
                { id: 'address', label: 'Address Details', icon: '📍' },
                { id: 'license', label: 'License & Registration', icon: '📋' },
                { id: 'tax', label: 'Tax Configuration', icon: '💼' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-6 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            {/* Basic Information Tab */}
            {activeTab === 'basic' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Basic Business Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Business Name *
                    </label>
                    <input
                      type="text"
                      value={businessInfo.business_name}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, business_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      EIN (Employer Identification Number) *
                    </label>
                    <input
                      type="text"
                      value={businessInfo.ein}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, ein: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      TIN (Taxpayer Identification Number) *
                    </label>
                    <input
                      type="text"
                      value={businessInfo.tin}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, tin: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Business Type *
                    </label>
                    <select
                      value={businessInfo.business_type}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, business_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="corporation">Corporation</option>
                      <option value="llc">LLC</option>
                      <option value="partnership">Partnership</option>
                      <option value="sole_proprietorship">Sole Proprietorship</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tax Classification
                    </label>
                    <select
                      value={businessInfo.tax_classification}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, tax_classification: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="c_corporation">C Corporation</option>
                      <option value="s_corporation">S Corporation</option>
                      <option value="partnership">Partnership</option>
                      <option value="llc">LLC</option>
                      <option value="sole_proprietorship">Sole Proprietorship</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      NAICS Code
                    </label>
                    <input
                      type="text"
                      value={businessInfo.naics_code}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, naics_code: e.target.value })}
                      placeholder="512110 - Motion Picture and Video Production"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Business Description
                    </label>
                    <textarea
                      value={businessInfo.business_description}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, business_description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 h-24"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Primary Business Activity
                    </label>
                    <input
                      type="text"
                      value={businessInfo.primary_business_activity}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, primary_business_activity: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date Business Started
                    </label>
                    <input
                      type="date"
                      value={businessInfo.date_business_started}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, date_business_started: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                </div>

                {/* Contact Information */}
                <div className="border-t pt-6 mt-6">
                  <h4 className="text-md font-semibold text-gray-900 mb-4">Contact Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contact Name *
                      </label>
                      <input
                        type="text"
                        value={businessInfo.contact_name}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, contact_name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contact Title
                      </label>
                      <input
                        type="text"
                        value={businessInfo.contact_title}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, contact_title: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contact Phone
                      </label>
                      <input
                        type="tel"
                        value={businessInfo.contact_phone}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, contact_phone: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contact Email
                      </label>
                      <input
                        type="email"
                        value={businessInfo.contact_email}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, contact_email: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Address Details Tab */}
            {activeTab === 'address' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Address Information</h3>
                
                {/* Primary Business Address */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-semibold text-gray-900 mb-4">Primary Business Address</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Address Line 1 *
                      </label>
                      <input
                        type="text"
                        value={businessInfo.address_line1}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, address_line1: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Address Line 2
                      </label>
                      <input
                        type="text"
                        value={businessInfo.address_line2}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, address_line2: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        City *
                      </label>
                      <input
                        type="text"
                        value={businessInfo.city}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, city: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        State *
                      </label>
                      <input
                        type="text"
                        value={businessInfo.state}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, state: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        ZIP Code *
                      </label>
                      <input
                        type="text"
                        value={businessInfo.zip_code}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, zip_code: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        County
                      </label>
                      <input
                        type="text"
                        value={businessInfo.county}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, county: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Mailing Address */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-md font-semibold text-gray-900">Mailing Address</h4>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={businessInfo.mailing_address_same}
                        onChange={(e) => handleMailingAddressToggle(e.target.checked)}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-600">Same as business address</span>
                    </label>
                  </div>
                  
                  {!businessInfo.mailing_address_same && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Mailing Address Line 1
                        </label>
                        <input
                          type="text"
                          value={businessInfo.mailing_address_line1}
                          onChange={(e) => setBusinessInfo({ ...businessInfo, mailing_address_line1: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          City
                        </label>
                        <input
                          type="text"
                          value={businessInfo.mailing_city}
                          onChange={(e) => setBusinessInfo({ ...businessInfo, mailing_city: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          State
                        </label>
                        <input
                          type="text"
                          value={businessInfo.mailing_state}
                          onChange={(e) => setBusinessInfo({ ...businessInfo, mailing_state: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* License & Registration Tab */}
            {activeTab === 'license' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">License & Registration Information</h3>
                
                {/* Business License */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-semibold text-gray-900 mb-4">Primary Business License</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        License Number
                      </label>
                      <input
                        type="text"
                        value={businessInfo.business_license_number}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, business_license_number: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        License Type
                      </label>
                      <input
                        type="text"
                        value={businessInfo.license_type}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, license_type: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        License State
                      </label>
                      <input
                        type="text"
                        value={businessInfo.license_state}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, license_state: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        License Expiration
                      </label>
                      <input
                        type="date"
                        value={businessInfo.license_expiration}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, license_expiration: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        License Status
                      </label>
                      <select
                        value={businessInfo.license_status}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, license_status: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="active">Active</option>
                        <option value="expired">Expired</option>
                        <option value="suspended">Suspended</option>
                        <option value="pending_renewal">Pending Renewal</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Compliance Status
                      </label>
                      <select
                        value={businessInfo.compliance_status}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, compliance_status: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="compliant">Compliant</option>
                        <option value="non_compliant">Non-Compliant</option>
                        <option value="under_review">Under Review</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Incorporation Details */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-semibold text-gray-900 mb-4">Incorporation Details</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Incorporation State
                      </label>
                      <input
                        type="text"
                        value={businessInfo.incorporation_state}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, incorporation_state: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Incorporation Date
                      </label>
                      <input
                        type="date"
                        value={businessInfo.incorporation_date}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, incorporation_date: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        State ID Number
                      </label>
                      <input
                        type="text"
                        value={businessInfo.state_id_number}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, state_id_number: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Additional Registrations */}
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-semibold text-gray-900 mb-4">Additional Registrations</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Sales Tax Permit
                      </label>
                      <input
                        type="text"
                        value={businessInfo.sales_tax_permit}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, sales_tax_permit: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        SIC Code
                      </label>
                      <input
                        type="text"
                        value={businessInfo.sic_code}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, sic_code: e.target.value })}
                        placeholder="7812 - Motion Picture Production"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>

                  {/* Checkboxes for registrations */}
                  <div className="mt-4 space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={businessInfo.federal_tax_deposits}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, federal_tax_deposits: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Federal Tax Deposits Registered</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={businessInfo.state_tax_registration}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, state_tax_registration: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">State Tax Registration Active</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Tax Configuration Tab */}
            {activeTab === 'tax' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Tax Configuration</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Fiscal Year End
                    </label>
                    <input
                      type="text"
                      value={businessInfo.fiscal_year_end}
                      onChange={(e) => setBusinessInfo({ ...businessInfo, fiscal_year_end: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <div className="space-y-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={businessInfo.default_backup_withholding}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, default_backup_withholding: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Default Backup Withholding</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={businessInfo.auto_generate_1099s}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, auto_generate_1099s: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Auto Generate 1099s</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={businessInfo.quarterly_filing_required}
                        onChange={(e) => setBusinessInfo({ ...businessInfo, quarterly_filing_required: e.target.checked })}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700">Quarterly Filing Required</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Business Information'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Business License Management Component
export const BusinessLicenseManagement = () => {
  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchLicenses();
  }, []);

  const fetchLicenses = async () => {
    try {
      const response = await axios.get(`${API}/tax/licenses`);
      setLicenses(response.data.licenses);
    } catch (error) {
      console.error('Error fetching licenses:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'active': 'bg-green-100 text-green-800',
      'expired': 'bg-red-100 text-red-800',
      'suspended': 'bg-orange-100 text-orange-800',
      'pending_renewal': 'bg-yellow-100 text-yellow-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading business licenses...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Business License Management</h1>
              <p className="text-gray-600">Track and manage all business licenses and permits</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition-colors"
            >
              Add License
            </button>
          </div>
        </div>

        {/* Licenses Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Business Licenses</h2>
          </div>

          <div className="overflow-x-auto">
            {licenses.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No licenses found</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by adding your first business license.</p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">License Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">License Number</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issuing Authority</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expiration</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {licenses.map((license) => (
                    <tr key={license.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{license.license_name}</div>
                        <div className="text-sm text-gray-500">{license.license_type}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {license.license_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {license.issuing_authority} - {license.issuing_state}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {license.expiration_date ? new Date(license.expiration_date).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(license.status)}`}>
                          {license.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-purple-600 hover:text-purple-900 mr-3">View</button>
                        <button className="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                        <button className="text-green-600 hover:text-green-900">Renew</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Compliance Dashboard Component
export const ComplianceDashboard = () => {
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    try {
      const response = await axios.get(`${API}/tax/compliance-dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching compliance data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading compliance dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Compliance Dashboard</h1>
          <p className="text-gray-600">Monitor business compliance and regulatory requirements</p>
        </div>

        {/* Compliance Score */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Overall Compliance Score</h2>
                <p className="text-gray-600">Current compliance status for Big Mann Entertainment</p>
              </div>
              <div className="text-right">
                <div className={`text-4xl font-bold ${
                  (dashboardData.compliance_overview?.compliance_score || 0) >= 90 ? 'text-green-600' :
                  (dashboardData.compliance_overview?.compliance_score || 0) >= 70 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {dashboardData.compliance_overview?.compliance_score || 0}%
                </div>
                <p className="text-sm text-gray-500">Compliance Score</p>
              </div>
            </div>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Licenses</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.compliance_overview?.total_licenses || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Licenses</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.compliance_overview?.active_licenses || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Expiring Soon</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.compliance_overview?.expiring_licenses || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Registrations</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.compliance_overview?.active_registrations || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Alerts and Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Compliance Alerts */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Compliance Alerts</h2>
            </div>
            <div className="p-6">
              {dashboardData.alerts?.expiring_licenses?.length > 0 && (
                <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                  <div className="flex">
                    <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-yellow-800">
                        {dashboardData.alerts.expiring_licenses.length} License(s) Expiring Soon
                      </h3>
                      <ul className="mt-2 text-sm text-yellow-700">
                        {dashboardData.alerts.expiring_licenses.map((license, index) => (
                          <li key={index}>
                            {license.license_name} - {license.days_until_expiry} days remaining
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {dashboardData.alerts?.upcoming_deadlines?.length > 0 && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                  <div className="flex">
                    <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">
                        {dashboardData.alerts.upcoming_deadlines.length} Annual Report(s) Due Soon
                      </h3>
                      <ul className="mt-2 text-sm text-red-700">
                        {dashboardData.alerts.upcoming_deadlines.map((deadline, index) => (
                          <li key={index}>
                            {deadline.registration_type} - Due in {deadline.days_until_due} days
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {(!dashboardData.alerts?.expiring_licenses?.length && !dashboardData.alerts?.upcoming_deadlines?.length) && (
                <div className="text-center py-8">
                  <svg className="mx-auto h-12 w-12 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">All Clear!</h3>
                  <p className="mt-1 text-sm text-gray-500">No compliance issues at this time.</p>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {dashboardData.quick_actions?.map((action, index) => (
                  <button
                    key={index}
                    className={`w-full text-left p-3 rounded-md border transition-colors ${
                      action.priority === 'high' ? 'border-red-200 bg-red-50 hover:bg-red-100' :
                      action.priority === 'medium' ? 'border-yellow-200 bg-yellow-50 hover:bg-yellow-100' :
                      'border-gray-200 bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">{action.label}</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        action.priority === 'high' ? 'bg-red-100 text-red-800' :
                        action.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {action.priority}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};