import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'https://bme-profile-boost.preview.emergentagent.com';

// AI Royalty Forecasting Component
export const AIRoyaltyForecasting = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [forecastConfig, setForecastConfig] = useState({
    asset_id: '',
    period: 'monthly',
    horizon_months: 12,
    model_type: 'ensemble',
    include_scenarios: true,
    confidence_intervals: true
  });
  const [modelPerformance, setModelPerformance] = useState(null);

  const handleForecastGeneration = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/api/premium/forecasting/generate?user_id=user_123`, forecastConfig);
      if (response.data) {
        setForecastData(response.data);
      }
    } catch (error) {
      console.error('Error generating forecast:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchModelPerformance = async () => {
    try {
      const response = await axios.get(`${API}/api/premium/forecasting/model-performance?user_id=user_123`);
      if (response.data) {
        setModelPerformance(response.data);
      }
    } catch (error) {
      console.error('Error fetching model performance:', error);
    }
  };

  useEffect(() => {
    fetchModelPerformance();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">AI Royalty Forecasting</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Predictive modeling for revenue optimization</p>
        </div>
        <div className="flex space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            🤖 AI-Powered
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            📈 Predictive Analytics
          </span>
        </div>
      </div>

      {/* Model Performance Cards */}
      {modelPerformance && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Model Accuracy</p>
                <p className="text-2xl font-bold text-green-600">{(modelPerformance.ensemble_accuracy * 100).toFixed(1)}%</p>
              </div>
              <span className="text-2xl">🎯</span>
            </div>
          </div>
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Data Points</p>
                <p className="text-2xl font-bold text-blue-600">{modelPerformance.data_points?.toLocaleString() || '0'}</p>
              </div>
              <span className="text-2xl">📊</span>
            </div>
          </div>
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Best Model</p>
                <p className="text-lg font-bold text-purple-600">{modelPerformance.best_model?.replace('_', ' ') || 'Ensemble'}</p>
              </div>
              <span className="text-2xl">🏆</span>
            </div>
          </div>
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Last Updated</p>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  {new Date(modelPerformance.last_trained).toLocaleDateString()}
                </p>
              </div>
              <span className="text-2xl">⏰</span>
            </div>
          </div>
        </div>
      )}

      {/* Forecast Configuration */}
      <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Generate New Forecast</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Asset ID (Optional)
            </label>
            <input
              type="text"
              value={forecastConfig.asset_id}
              onChange={(e) => setForecastConfig({...forecastConfig, asset_id: e.target.value})}
              placeholder="Leave blank for portfolio forecast"
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Forecast Period
            </label>
            <select
              value={forecastConfig.period}
              onChange={(e) => setForecastConfig({...forecastConfig, period: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            >
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Forecast Horizon (Months)
            </label>
            <input
              type="number"
              min="1"
              max="36"
              value={forecastConfig.horizon_months}
              onChange={(e) => setForecastConfig({...forecastConfig, horizon_months: parseInt(e.target.value)})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Model Type
            </label>
            <select
              value={forecastConfig.model_type}
              onChange={(e) => setForecastConfig({...forecastConfig, model_type: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            >
              <option value="ensemble">Ensemble (Best)</option>
              <option value="random_forest">Random Forest</option>
              <option value="gradient_boosting">Gradient Boosting</option>
              <option value="linear_regression">Linear Regression</option>
            </select>
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={forecastConfig.include_scenarios}
                onChange={(e) => setForecastConfig({...forecastConfig, include_scenarios: e.target.checked})}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Include Scenarios</span>
            </label>
          </div>

          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={forecastConfig.confidence_intervals}
                onChange={(e) => setForecastConfig({...forecastConfig, confidence_intervals: e.target.checked})}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Confidence Intervals</span>
            </label>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={handleForecastGeneration}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Generating Forecast...</span>
              </>
            ) : (
              <>
                <span>🤖</span>
                <span>Generate AI Forecast</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Forecast Results */}
      {forecastData && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Total Predicted Revenue</h4>
              <p className="text-3xl font-bold text-green-600">
                ${forecastData.total_predicted_revenue?.toLocaleString(undefined, {minimumFractionDigits: 2})}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Over {forecastConfig.horizon_months} months
              </p>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Confidence Score</h4>
              <p className="text-3xl font-bold text-blue-600">
                {(forecastData.confidence_score * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Model confidence level
              </p>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Model Accuracy</h4>
              <p className="text-3xl font-bold text-purple-600">
                {(forecastData.model_accuracy * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Historical performance
              </p>
            </div>
          </div>

          {/* Forecast Timeline */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Revenue Forecast Timeline</h4>
            <div className="space-y-3">
              {forecastData.forecast_data?.map((period, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {new Date(period.date).toLocaleDateString()}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Confidence: {(period.confidence_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-600">
                      ${period.predicted_revenue?.toLocaleString(undefined, {minimumFractionDigits: 2})}
                    </p>
                    {period.confidence_interval && (
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        ${period.confidence_interval.lower?.toFixed(2)} - ${period.confidence_interval.upper?.toFixed(2)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Insights */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">🎯 Key Insights</h4>
            <div className="space-y-2">
              {forecastData.key_insights?.map((insight, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <span className="text-blue-600 mt-1">•</span>
                  <p className="text-gray-700 dark:text-gray-300">{insight}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Scenarios */}
          {forecastData.scenarios && forecastData.scenarios.length > 0 && (
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">📊 What-If Scenarios</h4>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {forecastData.scenarios.map((scenario, index) => (
                  <div key={index} className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                    <h5 className="font-semibold text-gray-900 dark:text-white mb-2">
                      {scenario.scenario_type?.replace('_', ' ').toUpperCase()}
                    </h5>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {scenario.description}
                    </p>
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Impact</p>
                        <p className={`font-bold ${scenario.impact_percentage > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {scenario.impact_percentage > 0 ? '+' : ''}{scenario.impact_percentage?.toFixed(1)}%
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-600 dark:text-gray-400">Revenue</p>
                        <p className="font-bold text-gray-900 dark:text-white">
                          ${scenario.predicted_revenue?.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Smart Contract Builder Component
export const SmartContractBuilder = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [templates, setTemplates] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [activeTab, setActiveTab] = useState('templates');
  const [loading, setLoading] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);

  const fetchTemplates = async () => {
    try {
      const response = await axios.get(`${API}/api/premium/contracts/templates?user_id=user_123`);
      if (response.data) {
        setTemplates(response.data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchUserContracts = async () => {
    try {
      const response = await axios.get(`${API}/api/premium/contracts/user/user_123?requesting_user_id=user_123`);
      if (response.data) {
        setContracts(response.data);
      }
    } catch (error) {
      console.error('Error fetching contracts:', error);
    }
  };

  const createContractFromTemplate = async (templateId, name, description) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/api/premium/contracts/from-template?user_id=user_123`, {
        template_id: templateId,
        name: name,
        description: description
      });
      if (response.data) {
        await fetchUserContracts();
        setActiveTab('my-contracts');
      }
    } catch (error) {
      console.error('Error creating contract:', error);
    } finally {
      setLoading(false);
    }
  };

  const simulateContract = async (contractId) => {
    setLoading(true);
    try {
      const simulationRequest = {
        contract_id: contractId,
        historical_data: {
          avg_daily_events: 15,
          avg_transaction_value: 45.0
        },
        scenario_parameters: {
          events_multiplier: 1.2
        },
        simulation_period_days: 30
      };

      const response = await axios.post(
        `${API}/api/premium/contracts/${contractId}/simulate?user_id=user_123`,
        simulationRequest
      );
      if (response.data) {
        setSimulationResult(response.data);
      }
    } catch (error) {
      console.error('Error simulating contract:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
    fetchUserContracts();
  }, []);

  const tabs = [
    { id: 'templates', name: 'Templates', icon: '📋' },
    { id: 'my-contracts', name: 'My Contracts', icon: '📄' },
    { id: 'builder', name: 'Visual Builder', icon: '🔧' },
    { id: 'simulation', name: 'Simulation', icon: '🧪' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Smart Contract Builder</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Visual drag-and-drop smart contract creation</p>
        </div>
        <div className="flex space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
            🔗 Blockchain Ready
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            🎨 Visual Builder
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <div key={template.id} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6 hover:shadow-lg transition-shadow`}>
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{template.name}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    template.complexity_score > 0.6 ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                    template.complexity_score > 0.4 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                    'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  }`}>
                    {template.complexity_score > 0.6 ? 'Advanced' : template.complexity_score > 0.4 ? 'Medium' : 'Basic'}
                  </span>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 mb-4">{template.description}</p>
                
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Use Cases:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {template.use_cases?.slice(0, 2).map((useCase, index) => (
                        <span key={index} className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                          {useCase}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>Components: {template.components?.length || 0}</span>
                    <span>Gas: ~{template.estimated_gas?.toLocaleString()}</span>
                  </div>
                </div>
                
                <button
                  onClick={() => {
                    setSelectedTemplate(template);
                    // Show creation modal (simplified for demo)
                    const name = prompt('Contract Name:');
                    const description = prompt('Contract Description:');
                    if (name && description) {
                      createContractFromTemplate(template.id, name, description);
                    }
                  }}
                  className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Use Template
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* My Contracts Tab */}
      {activeTab === 'my-contracts' && (
        <div className="space-y-6">
          {contracts.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📄</div>
              <p className="text-gray-600 dark:text-gray-400">No contracts created yet</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                Use a template or create a custom contract to get started
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {contracts.map((contract) => (
                <div key={contract.id} className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{contract.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {contract.contract_type?.replace('_', ' ').toUpperCase()}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      contract.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                      contract.status === 'deployed' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                    }`}>
                      {contract.status}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 dark:text-gray-400 mb-4">{contract.description}</p>
                  
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-4">
                    <span>Components: {contract.components?.length || 0}</span>
                    <span>Version: {contract.version}</span>
                  </div>
                  
                  <div className="space-y-2">
                    <button
                      onClick={() => simulateContract(contract.id)}
                      disabled={loading}
                      className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
                    >
                      🧪 Simulate Contract
                    </button>
                    
                    {contract.solidity_code && (
                      <button className="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors">
                        📝 View Code
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Visual Builder Tab */}
      {activeTab === 'builder' && (
        <div className="space-y-6">
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-8 text-center`}>
            <div className="text-6xl mb-4">🚧</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Visual Builder Coming Soon</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Drag-and-drop contract builder with real-time preview is under development
            </p>
            
            {/* Component Palette Preview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
              <div className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <div className="text-2xl mb-2">⚡</div>
                <p className="text-sm font-medium">Triggers</p>
              </div>
              <div className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <div className="text-2xl mb-2">❓</div>
                <p className="text-sm font-medium">Conditions</p>
              </div>
              <div className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <div className="text-2xl mb-2">⚙️</div>
                <p className="text-sm font-medium">Actions</p>
              </div>
              <div className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
                <div className="text-2xl mb-2">🔧</div>
                <p className="text-sm font-medium">Modifiers</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Simulation Tab */}
      {activeTab === 'simulation' && (
        <div className="space-y-6">
          {simulationResult ? (
            <div className="space-y-6">
              {/* Simulation Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total Executions</p>
                      <p className="text-2xl font-bold text-blue-600">{simulationResult.total_executions}</p>
                    </div>
                    <span className="text-2xl">🔄</span>
                  </div>
                </div>
                
                <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
                      <p className="text-2xl font-bold text-green-600">
                        {((simulationResult.successful_executions / simulationResult.total_executions) * 100).toFixed(1)}%
                      </p>
                    </div>
                    <span className="text-2xl">✅</span>
                  </div>
                </div>
                
                <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Avg Gas Cost</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {simulationResult.gas_estimates?.average_gas_per_execution?.toLocaleString() || '0'}
                      </p>
                    </div>
                    <span className="text-2xl">⛽</span>
                  </div>
                </div>
                
                <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-4`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Cost</p>
                      <p className="text-2xl font-bold text-orange-600">
                        ${simulationResult.gas_estimates?.monthly_gas_cost_usd || '0'}
                      </p>
                    </div>
                    <span className="text-2xl">💰</span>
                  </div>
                </div>
              </div>

              {/* Financial Projections */}
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">💼 Financial Impact</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Automation Savings</p>
                    <p className="text-xl font-bold text-green-600">
                      ${simulationResult.financial_projections?.automation_cost_savings?.toLocaleString() || '0'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Time Saved</p>
                    <p className="text-xl font-bold text-blue-600">
                      {simulationResult.financial_projections?.processing_time_saved_hours?.toFixed(1) || '0'} hours
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">ROI Estimate</p>
                    <p className="text-xl font-bold text-purple-600">
                      {simulationResult.financial_projections?.roi_estimate?.toFixed(1) || '0'}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">💡 Recommendations</h4>
                <div className="space-y-2">
                  {simulationResult.recommendations?.map((recommendation, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <span className="text-blue-600 mt-1">•</span>
                      <p className="text-gray-700 dark:text-gray-300">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🧪</div>
              <p className="text-gray-600 dark:text-gray-400">No simulation results yet</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                Run a simulation from the "My Contracts" tab to see results here
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Multi-Currency Payout Component
export const MultiCurrencyPayouts = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [supportedCurrencies, setSupportedCurrencies] = useState(null);
  const [payoutPreferences, setPayoutPreferences] = useState({
    primary_currency: 'USD',
    payout_method: 'bank_transfer',
    minimum_payout: 50.0,
    payout_frequency: 'monthly',
    auto_convert: true
  });
  const [conversionEstimate, setConversionEstimate] = useState(null);
  const [estimateParams, setEstimateParams] = useState({
    amount: 100,
    from_currency: 'USD',
    to_currency: 'EUR'
  });

  const fetchSupportedCurrencies = async () => {
    try {
      const response = await axios.get(`${API}/api/premium/payouts/currencies?user_id=user_123`);
      if (response.data) {
        setSupportedCurrencies(response.data);
      }
    } catch (error) {
      console.error('Error fetching currencies:', error);
    }
  };

  const getConversionEstimate = async () => {
    try {
      const response = await axios.get(`${API}/api/premium/payouts/estimate`, {
        params: { ...estimateParams, user_id: 'user_123' }
      });
      if (response.data) {
        setConversionEstimate(response.data);
      }
    } catch (error) {
      console.error('Error getting estimate:', error);
    }
  };

  const savePayoutPreferences = async () => {
    try {
      const response = await axios.post(`${API}/api/premium/payouts/configure?user_id=user_123`, payoutPreferences);
      if (response.data?.success) {
        alert('Payout preferences saved successfully!');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
    }
  };

  useEffect(() => {
    fetchSupportedCurrencies();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Multi-Currency Payouts</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Optimize payouts with crypto and fiat options</p>
        </div>
        <div className="flex space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            💰 Multi-Currency
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
            ⚡ Crypto Ready
          </span>
        </div>
      </div>

      {/* Supported Currencies */}
      {supportedCurrencies && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Fiat Currencies */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">💵 Fiat Currencies</h3>
            <div className="space-y-3">
              {supportedCurrencies.fiat_currencies?.map((currency) => (
                <div key={currency.code} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {currency.symbol} {currency.name} ({currency.code})
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Methods: {currency.supported_methods?.join(', ')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cryptocurrencies */}
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">₿ Cryptocurrencies</h3>
            <div className="space-y-3">
              {supportedCurrencies.cryptocurrencies?.map((crypto) => (
                <div key={crypto.code} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {crypto.symbol} {crypto.name} ({crypto.code})
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Network: {crypto.network}, Min: {crypto.min_payout}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Conversion Estimator */}
      <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">🔄 Conversion Estimator</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Amount</label>
            <input
              type="number"
              value={estimateParams.amount}
              onChange={(e) => setEstimateParams({...estimateParams, amount: parseFloat(e.target.value)})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">From</label>
            <select
              value={estimateParams.from_currency}
              onChange={(e) => setEstimateParams({...estimateParams, from_currency: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            >
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="BTC">BTC</option>
              <option value="ETH">ETH</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">To</label>
            <select
              value={estimateParams.to_currency}
              onChange={(e) => setEstimateParams({...estimateParams, to_currency: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            >
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
              <option value="BTC">BTC</option>
              <option value="ETH">ETH</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={getConversionEstimate}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
            >
              Calculate
            </button>
          </div>
        </div>

        {conversionEstimate && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Original Amount</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {conversionEstimate.original_amount} {conversionEstimate.from_currency}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Converted Amount</p>
                <p className="text-lg font-bold text-green-600">
                  {conversionEstimate.converted_amount?.toFixed(4)} {conversionEstimate.to_currency}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Fees</p>
                <p className="text-lg font-bold text-red-600">
                  ${conversionEstimate.fees?.total_fees?.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Net Amount</p>
                <p className="text-lg font-bold text-blue-600">
                  {conversionEstimate.net_amount?.toFixed(4)} {conversionEstimate.to_currency}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Payout Preferences */}
      <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">⚙️ Payout Preferences</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Primary Currency</label>
            <select
              value={payoutPreferences.primary_currency}
              onChange={(e) => setPayoutPreferences({...payoutPreferences, primary_currency: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            >
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="BTC">BTC</option>
              <option value="ETH">ETH</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Payout Method</label>
            <select
              value={payoutPreferences.payout_method}
              onChange={(e) => setPayoutPreferences({...payoutPreferences, payout_method: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            >
              <option value="bank_transfer">Bank Transfer</option>
              <option value="paypal">PayPal</option>
              <option value="crypto_wallet">Crypto Wallet</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Minimum Payout</label>
            <input
              type="number"
              value={payoutPreferences.minimum_payout}
              onChange={(e) => setPayoutPreferences({...payoutPreferences, minimum_payout: parseFloat(e.target.value)})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Payout Frequency</label>
            <select
              value={payoutPreferences.payout_frequency}
              onChange={(e) => setPayoutPreferences({...payoutPreferences, payout_frequency: e.target.value})}
              className={`w-full px-3 py-2 border rounded-lg ${isDarkMode ? 'bg-gray-800 border-gray-600 text-white' : 'bg-white border-gray-300'}`}
            >
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="auto_convert"
              checked={payoutPreferences.auto_convert}
              onChange={(e) => setPayoutPreferences({...payoutPreferences, auto_convert: e.target.checked})}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="auto_convert" className="text-sm text-gray-700 dark:text-gray-300">
              Auto-convert to preferred currency
            </label>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={savePayoutPreferences}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center space-x-2"
          >
            <span>💾</span>
            <span>Save Preferences</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// Premium Dashboard Overview Component
export const PremiumDashboardOverview = () => {
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem('darkMode') === 'true');
  const [overviewData, setOverviewData] = useState(null);
  const [revenueIntelligence, setRevenueIntelligence] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchPremiumOverview = async () => {
    setLoading(true);
    try {
      const [overviewResponse, revenueResponse] = await Promise.all([
        axios.get(`${API}/api/premium/dashboard/overview?user_id=user_123`),
        axios.get(`${API}/api/premium/revenue-intelligence/dashboard?user_id=user_123&time_period=30d`)
      ]);

      if (overviewResponse.data) {
        setOverviewData(overviewResponse.data);
      }
      if (revenueResponse.data) {
        setRevenueIntelligence(revenueResponse.data);
      }
    } catch (error) {
      console.error('Error fetching premium overview:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPremiumOverview();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Premium Dashboard</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Advanced analytics and AI-powered insights</p>
        </div>
        <div className="flex space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-medium bg-gold-100 text-gold-800" style={{backgroundColor: '#fef3c7', color: '#92400e'}}>
            ⭐ Premium Active
          </span>
        </div>
      </div>

      {/* Premium Features Status */}
      {overviewData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">AI Forecasting</h3>
              <span className="text-2xl">🤖</span>
            </div>
            <p className="text-2xl font-bold text-blue-600 mb-2">
              {(overviewData.ai_forecasting?.accuracy_score * 100).toFixed(0)}%
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Accuracy Score</p>
            <p className="text-xs text-green-600 mt-1">
              Next: ${overviewData.ai_forecasting?.next_forecast_revenue?.toLocaleString()}
            </p>
          </div>

          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">Smart Contracts</h3>
              <span className="text-2xl">📄</span>
            </div>
            <p className="text-2xl font-bold text-purple-600 mb-2">
              {overviewData.smart_contracts?.active_contracts}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Active Contracts</p>
            <p className="text-xs text-green-600 mt-1">
              {(overviewData.smart_contracts?.automation_efficiency * 100).toFixed(0)}% Efficient
            </p>
          </div>

          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">Revenue Intelligence</h3>
              <span className="text-2xl">📊</span>
            </div>
            <p className="text-2xl font-bold text-green-600 mb-2">
              +{overviewData.revenue_intelligence?.growth_rate?.toFixed(1)}%
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Growth Rate</p>
            <p className="text-xs text-blue-600 mt-1">
              {overviewData.revenue_intelligence?.optimization_opportunities} Opportunities
            </p>
          </div>

          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">Multi-Currency</h3>
              <span className="text-2xl">💰</span>
            </div>
            <p className="text-2xl font-bold text-orange-600 mb-2">
              ${overviewData.multi_currency_payouts?.total_saved_fees?.toLocaleString()}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Fees Saved</p>
            <p className="text-xs text-green-600 mt-1">
              {overviewData.multi_currency_payouts?.supported_currencies} Currencies
            </p>
          </div>
        </div>
      )}

      {/* Revenue Intelligence Summary */}
      {revenueIntelligence && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">💼 Revenue Overview</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Total Revenue</span>
                <span className="text-xl font-bold text-green-600">
                  ${revenueIntelligence.revenue_overview?.total_revenue?.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Growth Rate</span>
                <span className="text-lg font-semibold text-blue-600">
                  +{revenueIntelligence.revenue_overview?.revenue_growth}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Top Platform</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {revenueIntelligence.revenue_overview?.top_performing_platform}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-400">Overall ROI</span>
                <span className="text-lg font-bold text-purple-600">
                  {revenueIntelligence.roi_metrics?.overall_roi}%
                </span>
              </div>
            </div>
          </div>

          <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">🎯 Key Insights</h3>
            <div className="space-y-3">
              {revenueIntelligence.predictive_insights?.map((insight, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <span className="text-blue-600 mt-1">•</span>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {overviewData?.recommendations && (
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">💡 Premium Recommendations</h3>
          <div className="space-y-3">
            {overviewData.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <span className="text-blue-600 mt-1">💡</span>
                <p className="text-gray-700 dark:text-gray-300">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Usage Statistics */}
      {overviewData?.premium_features_usage && (
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-lg p-6`}>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">📈 Monthly Usage</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {overviewData.premium_features_usage.forecasting_requests_month}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Forecasts Generated</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {overviewData.premium_features_usage.contracts_created_month}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Contracts Created</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {overviewData.premium_features_usage.simulations_run_month}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Simulations Run</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {overviewData.premium_features_usage.optimization_suggestions_applied}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Optimizations Applied</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};