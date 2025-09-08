import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Budget Management Component
export const BudgetManagement = () => {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedBudget, setSelectedBudget] = useState(null);
  const [budgetCategories, setBudgetCategories] = useState([
    'Marketing & Promotion',
    'Recording & Production',
    'Distribution',
    'Equipment',
    'Travel & Tours',
    'Legal & Administrative',
    'Talent & Personnel',
    'Miscellaneous'
  ]);

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    setLoading(true);
    try {
      // Mock budget data since backend endpoint may not exist
      const mockBudgets = [
        {
          id: 1,
          name: 'Q4 2024 Marketing Campaign',
          category: 'Marketing & Promotion',
          total_budget: 25000,
          spent: 18500,
          remaining: 6500,
          status: 'active',
          start_date: '2024-10-01',
          end_date: '2024-12-31',
          line_items: [
            { name: 'Social Media Ads', budgeted: 10000, spent: 8500 },
            { name: 'Influencer Partnerships', budgeted: 8000, spent: 6000 },
            { name: 'Content Creation', budgeted: 7000, spent: 4000 }
          ]
        },
        {
          id: 2,
          name: 'Album Production Budget',
          category: 'Recording & Production',
          total_budget: 50000,
          spent: 35000,
          remaining: 15000,
          status: 'active',
          start_date: '2024-09-01',
          end_date: '2025-02-28',
          line_items: [
            { name: 'Studio Time', budgeted: 20000, spent: 18000 },
            { name: 'Producer Fees', budgeted: 15000, spent: 12000 },
            { name: 'Mixing & Mastering', budgeted: 10000, spent: 5000 },
            { name: 'Session Musicians', budgeted: 5000, spent: 0 }
          ]
        },
        {
          id: 3,
          name: 'Distribution & Licensing',
          category: 'Distribution',
          total_budget: 15000,
          spent: 12000,
          remaining: 3000,
          status: 'completed',
          start_date: '2024-08-01',
          end_date: '2024-11-30',
          line_items: [
            { name: 'Platform Distribution Fees', budgeted: 8000, spent: 7500 },
            { name: 'Licensing & Rights', budgeted: 4000, spent: 3000 },
            { name: 'International Distribution', budgeted: 3000, spent: 1500 }
          ]
        }
      ];
      setBudgets(mockBudgets);
    } catch (error) {
      console.error('Error fetching budgets:', error);
      // Set empty array on error
      setBudgets([]);
    } finally {
      setLoading(false);
    }
  };

  const createBudget = async (budgetData) => {
    try {
      // Mock budget creation
      const newBudget = {
        id: Date.now(),
        ...budgetData,
        spent: 0,
        remaining: budgetData.total_budget,
        status: 'active',
        line_items: budgetData.line_items || []
      };
      setBudgets(prev => [...prev, newBudget]);
      setShowAddModal(false);
    } catch (error) {
      console.error('Error creating budget:', error);
      alert('Error creating budget');
    }
  };

  const updateBudget = async (budgetId, updates) => {
    try {
      setBudgets(prev => prev.map(budget => 
        budget.id === budgetId ? { ...budget, ...updates } : budget
      ));
    } catch (error) {
      console.error('Error updating budget:', error);
    }
  };

  const deleteBudget = async (budgetId) => {
    try {
      setBudgets(prev => prev.filter(budget => budget.id !== budgetId));
    } catch (error) {
      console.error('Error deleting budget:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-bold">📊 Budget Management</h3>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm"
        >
          + Create Budget
        </button>
      </div>

      {/* Budget Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-800">Total Budgets</h4>
          <p className="text-2xl font-bold text-blue-600">{budgets.length}</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-green-800">Total Allocated</h4>
          <p className="text-2xl font-bold text-green-600">
            ${budgets.reduce((sum, b) => sum + b.total_budget, 0).toLocaleString()}
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-red-800">Total Spent</h4>
          <p className="text-2xl font-bold text-red-600">
            ${budgets.reduce((sum, b) => sum + b.spent, 0).toLocaleString()}
          </p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-orange-800">Remaining</h4>
          <p className="text-2xl font-bold text-orange-600">
            ${budgets.reduce((sum, b) => sum + b.remaining, 0).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Budget List */}
      <div className="space-y-4">
        {budgets.map((budget) => (
          <div key={budget.id} className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="text-lg font-semibold">{budget.name}</h4>
                <p className="text-sm text-gray-600">{budget.category}</p>
                <p className="text-sm text-gray-500">
                  {budget.start_date} to {budget.end_date}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  budget.status === 'active' ? 'bg-green-100 text-green-800' :
                  budget.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {budget.status}
                </span>
                <button
                  onClick={() => setSelectedBudget(budget)}
                  className="text-purple-600 hover:text-purple-800 text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => deleteBudget(budget.id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>

            {/* Budget Progress */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Budget Progress</span>
                <span>{Math.round((budget.spent / budget.total_budget) * 100)}% used</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    (budget.spent / budget.total_budget) > 0.9 ? 'bg-red-500' :
                    (budget.spent / budget.total_budget) > 0.7 ? 'bg-orange-500' :
                    'bg-green-500'
                  }`}
                  style={{ width: `${Math.min((budget.spent / budget.total_budget) * 100, 100)}%` }}
                ></div>
              </div>
            </div>

            {/* Budget Details */}
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Total Budget:</span>
                <p className="font-semibold">${budget.total_budget.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-600">Spent:</span>
                <p className="font-semibold text-red-600">${budget.spent.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-600">Remaining:</span>
                <p className="font-semibold text-green-600">${budget.remaining.toLocaleString()}</p>
              </div>
            </div>

            {/* Line Items */}
            {budget.line_items && budget.line_items.length > 0 && (
              <div className="mt-4">
                <h5 className="text-sm font-medium mb-2">Budget Breakdown:</h5>
                <div className="space-y-1">
                  {budget.line_items.map((item, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span>{item.name}</span>
                      <span>${item.spent.toLocaleString()} / ${item.budgeted.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {budgets.length === 0 && !loading && (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No budgets created yet</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg"
          >
            Create Your First Budget
          </button>
        </div>
      )}

      {/* Add Budget Modal */}
      {showAddModal && (
        <BudgetModal
          onClose={() => setShowAddModal(false)}
          onSave={createBudget}
          categories={budgetCategories}
        />
      )}

      {/* Edit Budget Modal */}
      {selectedBudget && (
        <BudgetModal
          budget={selectedBudget}
          onClose={() => setSelectedBudget(null)}
          onSave={(updates) => {
            updateBudget(selectedBudget.id, updates);
            setSelectedBudget(null);
          }}
          categories={budgetCategories}
        />
      )}
    </div>
  );
};

// Budget Modal Component
const BudgetModal = ({ budget, onClose, onSave, categories }) => {
  const [formData, setFormData] = useState({
    name: budget?.name || '',
    category: budget?.category || categories[0],
    total_budget: budget?.total_budget || '',
    start_date: budget?.start_date || '',
    end_date: budget?.end_date || '',
    description: budget?.description || ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      ...formData,
      total_budget: parseFloat(formData.total_budget)
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">
          {budget ? 'Edit Budget' : 'Create New Budget'}
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Budget Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Total Budget ($)</label>
            <input
              type="number"
              step="0.01"
              value={formData.total_budget}
              onChange={(e) => setFormData(prev => ({ ...prev, total_budget: e.target.value }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start Date</label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Date</label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              rows="3"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md"
            >
              {budget ? 'Update' : 'Create'} Budget
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Financial Reports Component
export const FinancialReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportPeriod, setReportPeriod] = useState('current_month');
  const [reportType, setReportType] = useState('summary');

  const reportTypes = [
    { value: 'summary', label: 'Financial Summary' },
    { value: 'transactions', label: 'Transaction Report' },
    { value: 'royalties', label: 'Royalty Report' },
    { value: 'budgets', label: 'Budget Analysis' },
    { value: 'profit_loss', label: 'Profit & Loss Statement' },
    { value: 'cash_flow', label: 'Cash Flow Report' }
  ];

  const reportPeriods = [
    { value: 'current_month', label: 'Current Month' },
    { value: 'last_month', label: 'Last Month' },
    { value: 'current_quarter', label: 'Current Quarter' },
    { value: 'last_quarter', label: 'Last Quarter' },
    { value: 'current_year', label: 'Current Year' },
    { value: 'last_year', label: 'Last Year' },
    { value: 'custom', label: 'Custom Range' }
  ];

  useEffect(() => {
    fetchReports();
  }, [reportPeriod, reportType]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      // Mock financial reports data
      const mockReports = [
        {
          id: 1,
          name: 'November 2024 Financial Summary',
          type: 'summary',
          period: 'current_month',
          generated_date: '2024-11-15',
          data: {
            total_revenue: 45250,
            total_expenses: 28300,
            net_profit: 16950,
            revenue_breakdown: {
              streaming: 28500,
              licensing: 12000,
              merchandise: 4750
            },
            expense_breakdown: {
              marketing: 12000,
              production: 8500,
              distribution: 4200,
              administrative: 3600
            }
          }
        },
        {
          id: 2,
          name: 'Q4 2024 Royalty Report',
          type: 'royalties',
          period: 'current_quarter',
          generated_date: '2024-11-01',
          data: {
            total_royalties: 38500,
            performance_royalties: 22000,
            mechanical_royalties: 16500,
            top_earning_tracks: [
              { title: 'Summer Vibes', earnings: 8500 },
              { title: 'Midnight Dreams', earnings: 6200 },
              { title: 'City Lights', earnings: 4800 }
            ]
          }
        },
        {
          id: 3,
          name: 'Budget vs Actual - October 2024',
          type: 'budgets',
          period: 'last_month',
          generated_date: '2024-11-01',
          data: {
            total_budgeted: 50000,
            total_spent: 42300,
            variance: 7700,
            categories: [
              { name: 'Marketing', budgeted: 20000, spent: 18500, variance: 1500 },
              { name: 'Production', budgeted: 15000, spent: 12800, variance: 2200 },
              { name: 'Distribution', budgeted: 10000, spent: 8000, variance: 2000 },
              { name: 'Administrative', budgeted: 5000, spent: 3000, variance: 2000 }
            ]
          }
        }
      ];
      setReports(mockReports);
    } catch (error) {
      console.error('Error fetching reports:', error);
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    setLoading(true);
    try {
      // Mock report generation
      const newReport = {
        id: Date.now(),
        name: `${reportTypes.find(t => t.value === reportType)?.label} - ${new Date().toLocaleDateString()}`,
        type: reportType,
        period: reportPeriod,
        generated_date: new Date().toISOString().split('T')[0],
        data: { status: 'generated', message: 'Report generated successfully' }
      };
      setReports(prev => [newReport, ...prev]);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (report, format = 'pdf') => {
    // Mock download functionality
    alert(`Downloading ${report.name} as ${format.toUpperCase()}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-bold">📈 Financial Reports</h3>
        <button
          onClick={generateReport}
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm"
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {/* Report Generation Controls */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Report Type</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              {reportTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Period</label>
            <select
              value={reportPeriod}
              onChange={(e) => setReportPeriod(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              {reportPeriods.map(period => (
                <option key={period.value} value={period.value}>{period.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-4">
        {reports.map((report) => (
          <div key={report.id} className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="text-lg font-semibold">{report.name}</h4>
                <p className="text-sm text-gray-600">
                  {reportTypes.find(t => t.value === report.type)?.label} • 
                  Generated on {new Date(report.generated_date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setSelectedReport(report)}
                  className="text-purple-600 hover:text-purple-800 text-sm"
                >
                  View
                </button>
                <button
                  onClick={() => downloadReport(report, 'pdf')}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  PDF
                </button>
                <button
                  onClick={() => downloadReport(report, 'excel')}
                  className="text-green-600 hover:text-green-800 text-sm"
                >
                  Excel
                </button>
              </div>
            </div>

            {/* Report Preview */}
            {report.data && (
              <div className="mt-4 p-4 bg-gray-50 rounded">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {report.type === 'summary' && (
                    <>
                      <div>
                        <span className="text-gray-600">Revenue:</span>
                        <p className="font-semibold text-green-600">
                          ${report.data.total_revenue?.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-600">Expenses:</span>
                        <p className="font-semibold text-red-600">
                          ${report.data.total_expenses?.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-600">Net Profit:</span>
                        <p className="font-semibold text-blue-600">
                          ${report.data.net_profit?.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-600">Margin:</span>
                        <p className="font-semibold">
                          {((report.data.net_profit / report.data.total_revenue) * 100).toFixed(1)}%
                        </p>
                      </div>
                    </>
                  )}
                  
                  {report.type === 'royalties' && (
                    <>
                      <div>
                        <span className="text-gray-600">Total Royalties:</span>
                        <p className="font-semibold">${report.data.total_royalties?.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Performance:</span>
                        <p className="font-semibold">${report.data.performance_royalties?.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Mechanical:</span>
                        <p className="font-semibold">${report.data.mechanical_royalties?.toLocaleString()}</p>
                      </div>
                    </>
                  )}

                  {report.type === 'budgets' && (
                    <>
                      <div>
                        <span className="text-gray-600">Budgeted:</span>
                        <p className="font-semibold">${report.data.total_budgeted?.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Spent:</span>
                        <p className="font-semibold">${report.data.total_spent?.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Variance:</span>
                        <p className={`font-semibold ${report.data.variance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ${Math.abs(report.data.variance).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-600">Utilization:</span>
                        <p className="font-semibold">
                          {((report.data.total_spent / report.data.total_budgeted) * 100).toFixed(1)}%
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {reports.length === 0 && !loading && (
        <div className="text-center py-8">
          <p className="text-gray-500 mb-4">No reports generated yet</p>
          <button
            onClick={generateReport}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg"
          >
            Generate Your First Report
          </button>
        </div>
      )}

      {/* Report Detail Modal */}
      {selectedReport && (
        <ReportDetailModal
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
          onDownload={downloadReport}
        />
      )}
    </div>
  );
};

// Report Detail Modal
const ReportDetailModal = ({ report, onClose, onDownload }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">{report.name}</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => onDownload(report, 'pdf')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
            >
              Download PDF
            </button>
            <button
              onClick={() => onDownload(report, 'excel')}
              className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
            >
              Download Excel
            </button>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
        </div>
        
        <div className="space-y-6">
          {/* Report Content */}
          <div className="bg-gray-50 p-4 rounded">
            <pre className="whitespace-pre-wrap text-sm">
              {JSON.stringify(report.data, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default { BudgetManagement, FinancialReports };