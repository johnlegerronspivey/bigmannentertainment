import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Sun, 
  CloudRain, 
  Snowflake, 
  Wind,
  Activity, 
  MapPin, 
  Clock, 
  Calendar,
  Target,
  Settings,
  TestTube,
  Play,
  Pause,
  AlertCircle,
  CheckCircle,
  Info,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

// AWS Amplify imports
import { API, Auth } from 'aws-amplify';

const TriggerConfigurator = () => {
  const [triggers, setTriggers] = useState([]);
  const [selectedTrigger, setSelectedTrigger] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState({});

  // Trigger form state
  const [triggerForm, setTriggerForm] = useState({
    name: '',
    description: '',
    type: 'weather',
    conditions: {},
    actions: {},
    priority: 1,
    isActive: true,
    campaigns: [],
    schedule: {
      enabled: false,
      startTime: '',
      endTime: '',
      days: []
    }
  });

  // Trigger types and their configurations
  const triggerTypes = {
    weather: {
      name: 'Weather Triggers',
      icon: Sun,
      color: 'yellow',
      conditions: [
        { id: 'temperature', name: 'Temperature', type: 'range', unit: '°C' },
        { id: 'condition', name: 'Weather Condition', type: 'select', options: ['sunny', 'cloudy', 'rainy', 'snowy', 'stormy'] },
        { id: 'humidity', name: 'Humidity', type: 'range', unit: '%' },
        { id: 'windSpeed', name: 'Wind Speed', type: 'range', unit: 'km/h' }
      ]
    },
    time: {
      name: 'Time-Based Triggers',
      icon: Clock,
      color: 'blue',
      conditions: [
        { id: 'timeRange', name: 'Time Range', type: 'timeRange' },
        { id: 'dayOfWeek', name: 'Day of Week', type: 'multiSelect', options: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] },
        { id: 'holiday', name: 'Holiday Period', type: 'boolean' }
      ]
    },
    location: {
      name: 'Location-Based Triggers',
      icon: MapPin,
      color: 'green',
      conditions: [
        { id: 'geofence', name: 'Geofence', type: 'location' },
        { id: 'traffic', name: 'Traffic Density', type: 'select', options: ['low', 'medium', 'high'] },
        { id: 'footfall', name: 'Footfall Count', type: 'range', unit: 'people/hour' }
      ]
    },
    sports: {
      name: 'Sports & Events',
      icon: Activity,
      color: 'red',
      conditions: [
        { id: 'eventType', name: 'Event Type', type: 'select', options: ['football', 'basketball', 'baseball', 'hockey', 'soccer', 'concert', 'festival'] },
        { id: 'eventStatus', name: 'Event Status', type: 'select', options: ['scheduled', 'live', 'completed'] },
        { id: 'teamName', name: 'Team/Artist Name', type: 'text' },
        { id: 'venueRadius', name: 'Venue Radius', type: 'range', unit: 'km' }
      ]
    },
    custom: {
      name: 'Custom Triggers',
      icon: Settings,
      color: 'purple',
      conditions: [
        { id: 'apiEndpoint', name: 'API Endpoint', type: 'url' },
        { id: 'conditionLogic', name: 'Condition Logic', type: 'code' },
        { id: 'triggerFrequency', name: 'Check Frequency', type: 'select', options: ['1min', '5min', '15min', '30min', '1hour'] }
      ]
    }
  };

  // Creative actions that can be triggered
  const creativeActions = [
    { id: 'switchVariant', name: 'Switch Creative Variant', type: 'select' },
    { id: 'overlayText', name: 'Add Text Overlay', type: 'text' },
    { id: 'changeColor', name: 'Change Color Scheme', type: 'color' },
    { id: 'playAnimation', name: 'Play Animation', type: 'select' },
    { id: 'updateCta', name: 'Update Call-to-Action', type: 'text' }
  ];

  useEffect(() => {
    loadTriggers();
  }, []);

  const loadTriggers = async () => {
    setLoading(true);
    try {
      const response = await API.get('doohapi', '/triggers', {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });
      setTriggers(response.triggers || []);
    } catch (error) {
      console.error('Error loading triggers:', error);
      // Mock data for demonstration
      setTriggers([
        {
          id: 'trigger_001',
          name: 'Hot Weather Summer Creative',
          description: 'Switch to summer-themed creative when temperature exceeds 25°C',
          type: 'weather',
          conditions: {
            temperature: { operator: '>', value: 25 },
            condition: { operator: '=', value: 'sunny' }
          },
          actions: {
            switchVariant: 'summer_theme',
            overlayText: 'Beat the Heat!'
          },
          priority: 1,
          isActive: true,
          lastTriggered: '2025-01-15T14:30:00Z',
          triggerCount: 45,
          campaigns: ['Summer Music Festival 2025'],
          status: 'active'
        },
        {
          id: 'trigger_002',
          name: 'Rainy Day Indoor Promo',
          description: 'Promote indoor events during rainy weather',
          type: 'weather',
          conditions: {
            condition: { operator: '=', value: 'rainy' }
          },
          actions: {
            switchVariant: 'indoor_theme',
            overlayText: 'Perfect Indoor Vibes'
          },
          priority: 2,
          isActive: true,
          lastTriggered: '2025-01-12T09:15:00Z',
          triggerCount: 23,
          campaigns: ['New Artist Launch'],
          status: 'active'
        },
        {
          id: 'trigger_003',
          name: 'Game Day Excitement',
          description: 'Activate during live sports events',
          type: 'sports',
          conditions: {
            eventType: { operator: '=', value: 'football' },
            eventStatus: { operator: '=', value: 'live' },
            venueRadius: { operator: '<=', value: 5 }
          },
          actions: {
            switchVariant: 'sports_theme',
            overlayText: 'Game Day Energy!'
          },
          priority: 3,
          isActive: false,
          lastTriggered: null,
          triggerCount: 0,
          campaigns: [],
          status: 'draft'
        }
      ]);
    }
    setLoading(false);
  };

  const createTrigger = async () => {
    setLoading(true);
    try {
      const response = await API.post('doohapi', '/triggers', {
        body: triggerForm,
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setTriggers([...triggers, response.trigger]);
      setShowCreateModal(false);
      resetTriggerForm();
    } catch (error) {
      console.error('Error creating trigger:', error);
    }
    setLoading(false);
  };

  const updateTrigger = async (triggerId, updates) => {
    try {
      await API.put('doohapi', `/triggers/${triggerId}`, {
        body: updates,
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setTriggers(triggers.map(trigger => 
        trigger.id === triggerId ? { ...trigger, ...updates } : trigger
      ));
    } catch (error) {
      console.error('Error updating trigger:', error);
    }
  };

  const deleteTrigger = async (triggerId) => {
    if (!window.confirm('Are you sure you want to delete this trigger?')) return;

    try {
      await API.del('doohapi', `/triggers/${triggerId}`, {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setTriggers(triggers.filter(t => t.id !== triggerId));
    } catch (error) {
      console.error('Error deleting trigger:', error);
    }
  };

  const testTrigger = async (triggerId) => {
    try {
      const response = await API.post('doohapi', `/triggers/${triggerId}/test`, {
        headers: {
          Authorization: `Bearer ${(await Auth.currentSession()).getAccessToken().getJwtToken()}`
        }
      });

      setTestResults({
        ...testResults,
        [triggerId]: response.result
      });
    } catch (error) {
      console.error('Error testing trigger:', error);
    }
  };

  const resetTriggerForm = () => {
    setTriggerForm({
      name: '',
      description: '',
      type: 'weather',
      conditions: {},
      actions: {},
      priority: 1,
      isActive: true,
      campaigns: [],
      schedule: {
        enabled: false,
        startTime: '',
        endTime: '',
        days: []
      }
    });
  };

  const renderConditionInput = (conditionConfig, value, onChange) => {
    switch (conditionConfig.type) {
      case 'range':
        return (
          <div className="grid grid-cols-3 gap-2">
            <select 
              value={value?.operator || '>'} 
              onChange={(e) => onChange({...value, operator: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value=">">Greater than</option>
              <option value="<">Less than</option>
              <option value=">=">Greater or equal</option>
              <option value="<=">Less or equal</option>
              <option value="=">Equal to</option>
            </select>
            <input
              type="number"
              value={value?.value || ''}
              onChange={(e) => onChange({...value, value: parseFloat(e.target.value)})}
              placeholder="Value"
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <span className="flex items-center text-sm text-gray-500 px-2">
              {conditionConfig.unit}
            </span>
          </div>
        );

      case 'select':
        return (
          <select
            value={value?.value || ''}
            onChange={(e) => onChange({...value, operator: '=', value: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">Select option...</option>
            {conditionConfig.options.map(option => (
              <option key={option} value={option}>
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </option>
            ))}
          </select>
        );

      case 'multiSelect':
        return (
          <div className="space-y-2">
            {conditionConfig.options.map(option => (
              <label key={option} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={value?.value?.includes(option) || false}
                  onChange={(e) => {
                    const currentValues = value?.value || [];
                    const newValues = e.target.checked
                      ? [...currentValues, option]
                      : currentValues.filter(v => v !== option);
                    onChange({...value, operator: 'in', value: newValues});
                  }}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700 capitalize">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'text':
        return (
          <input
            type="text"
            value={value?.value || ''}
            onChange={(e) => onChange({...value, operator: '=', value: e.target.value})}
            placeholder="Enter value..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        );

      case 'boolean':
        return (
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value?.value || false}
              onChange={(e) => onChange({...value, operator: '=', value: e.target.checked})}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Enable condition</span>
          </label>
        );

      default:
        return (
          <input
            type="text"
            value={value?.value || ''}
            onChange={(e) => onChange({...value, operator: '=', value: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          />
        );
    }
  };

  const renderTriggerCard = (trigger) => {
    const typeConfig = triggerTypes[trigger.type];
    const TypeIcon = typeConfig?.icon || Settings;
    const testResult = testResults[trigger.id];

    return (
      <div key={trigger.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg bg-${typeConfig?.color || 'gray'}-100`}>
              <TypeIcon className={`w-5 h-5 text-${typeConfig?.color || 'gray'}-600`} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{trigger.name}</h3>
              <p className="text-sm text-gray-600">{trigger.description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              trigger.isActive 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {trigger.isActive ? 'Active' : 'Inactive'}
            </span>
            <div className="flex space-x-1">
              <button 
                onClick={() => testTrigger(trigger.id)}
                className="p-2 text-gray-400 hover:text-blue-600 rounded"
                title="Test trigger"
              >
                <TestTube className="w-4 h-4" />
              </button>
              <button 
                onClick={() => {
                  setSelectedTrigger(trigger);
                  setTriggerForm({...trigger});
                  setShowCreateModal(true);
                }}
                className="p-2 text-gray-400 hover:text-green-600 rounded"
                title="Edit trigger"
              >
                <Edit className="w-4 h-4" />
              </button>
              <button 
                onClick={() => deleteTrigger(trigger.id)}
                className="p-2 text-gray-400 hover:text-red-600 rounded"
                title="Delete trigger"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Conditions Summary */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Conditions:</h4>
          <div className="flex flex-wrap gap-2">
            {Object.entries(trigger.conditions).map(([key, condition]) => (
              <span key={key} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                {key}: {condition.operator} {condition.value}
              </span>
            ))}
          </div>
        </div>

        {/* Actions Summary */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Actions:</h4>
          <div className="flex flex-wrap gap-2">
            {Object.entries(trigger.actions).map(([key, value]) => (
              <span key={key} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                {key}: {value}
              </span>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500">Priority</p>
            <p className="text-sm font-medium">{trigger.priority}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Triggered</p>
            <p className="text-sm font-medium">{trigger.triggerCount} times</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Campaigns</p>
            <p className="text-sm font-medium">{trigger.campaigns.length}</p>
          </div>
        </div>

        {/* Test Results */}
        {testResult && (
          <div className={`p-3 rounded-lg text-sm ${
            testResult.success 
              ? 'bg-green-50 text-green-800 border border-green-200' 
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            <div className="flex items-center space-x-2">
              {testResult.success ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                <AlertCircle className="w-4 h-4" />
              )}
              <span className="font-medium">
                Test {testResult.success ? 'Passed' : 'Failed'}
              </span>
            </div>
            <p className="mt-1">{testResult.message}</p>
          </div>
        )}

        {/* Toggle */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            Last triggered: {trigger.lastTriggered 
              ? new Date(trigger.lastTriggered).toLocaleDateString()
              : 'Never'
            }
          </div>
          <button
            onClick={() => updateTrigger(trigger.id, { isActive: !trigger.isActive })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
              trigger.isActive ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              trigger.isActive ? 'translate-x-6' : 'translate-x-1'
            }`} />
          </button>
        </div>
      </div>
    );
  };

  const renderCreateModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {selectedTrigger ? 'Edit Trigger' : 'Create New Trigger'}
          </h2>
          <button 
            onClick={() => {
              setShowCreateModal(false);
              setSelectedTrigger(null);
              resetTriggerForm();
            }}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Trigger Name</label>
              <input
                type="text"
                value={triggerForm.name}
                onChange={(e) => setTriggerForm({...triggerForm, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter trigger name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Trigger Type</label>
              <select
                value={triggerForm.type}
                onChange={(e) => setTriggerForm({...triggerForm, type: e.target.value, conditions: {}})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {Object.entries(triggerTypes).map(([key, type]) => (
                  <option key={key} value={key}>{type.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={triggerForm.description}
              onChange={(e) => setTriggerForm({...triggerForm, description: e.target.value})}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe what this trigger does"
            />
          </div>

          {/* Conditions */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trigger Conditions</h3>
            <div className="space-y-4">
              {triggerTypes[triggerForm.type]?.conditions.map(conditionConfig => (
                <div key={conditionConfig.id} className="p-4 border border-gray-200 rounded-lg">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {conditionConfig.name}
                  </label>
                  {renderConditionInput(
                    conditionConfig,
                    triggerForm.conditions[conditionConfig.id],
                    (value) => setTriggerForm({
                      ...triggerForm,
                      conditions: {
                        ...triggerForm.conditions,
                        [conditionConfig.id]: value
                      }
                    })
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Creative Actions</h3>
            <div className="space-y-4">
              {creativeActions.map(action => (
                <div key={action.id} className="p-4 border border-gray-200 rounded-lg">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {action.name}
                  </label>
                  {action.type === 'select' ? (
                    <select
                      value={triggerForm.actions[action.id] || ''}
                      onChange={(e) => setTriggerForm({
                        ...triggerForm,
                        actions: {
                          ...triggerForm.actions,
                          [action.id]: e.target.value
                        }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      <option value="">Select action...</option>
                      <option value="default">Default</option>
                      <option value="summer_theme">Summer Theme</option>
                      <option value="winter_theme">Winter Theme</option>
                      <option value="sports_theme">Sports Theme</option>
                      <option value="night_theme">Night Theme</option>
                    </select>
                  ) : (
                    <input
                      type="text"
                      value={triggerForm.actions[action.id] || ''}
                      onChange={(e) => setTriggerForm({
                        ...triggerForm,
                        actions: {
                          ...triggerForm.actions,
                          [action.id]: e.target.value
                        }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      placeholder={`Enter ${action.name.toLowerCase()}...`}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                value={triggerForm.priority}
                onChange={(e) => setTriggerForm({...triggerForm, priority: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>High (1)</option>
                <option value={2}>Medium (2)</option>
                <option value={3}>Low (3)</option>
              </select>
            </div>
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="isActive"
                checked={triggerForm.isActive}
                onChange={(e) => setTriggerForm({...triggerForm, isActive: e.target.checked})}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="isActive" className="text-sm font-medium text-gray-700">
                Activate trigger immediately
              </label>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-4 mt-8">
          <button 
            onClick={() => {
              setShowCreateModal(false);
              setSelectedTrigger(null);
              resetTriggerForm();
            }}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button 
            onClick={createTrigger}
            disabled={loading || !triggerForm.name}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading && <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>}
            <Save className="w-4 h-4" />
            <span>{selectedTrigger ? 'Update Trigger' : 'Create Trigger'}</span>
          </button>
        </div>
      </div>
    </div>
  );

  const filteredTriggers = triggers.filter(trigger => 
    activeTab === 'all' || 
    (activeTab === 'active' && trigger.isActive) ||
    (activeTab === 'inactive' && !trigger.isActive) ||
    (activeTab === trigger.type)
  );

  if (loading && triggers.length === 0) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trigger Configurator</h1>
          <p className="text-gray-600 mt-1">Define contextual triggers for dynamic creative optimization</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          <span>New Trigger</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'all', name: 'All Triggers', count: triggers.length },
            { id: 'active', name: 'Active', count: triggers.filter(t => t.isActive).length },
            { id: 'inactive', name: 'Inactive', count: triggers.filter(t => !t.isActive).length },
            ...Object.entries(triggerTypes).map(([key, type]) => ({
              id: key,
              name: type.name,
              count: triggers.filter(t => t.type === key).length
            }))
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name} ({tab.count})
            </button>
          ))}
        </nav>
      </div>

      {/* Triggers Grid */}
      <div className="grid gap-6">
        {filteredTriggers.length > 0 ? (
          filteredTriggers.map(renderTriggerCard)
        ) : (
          <div className="text-center py-12">
            <Zap className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No triggers found</h3>
            <p className="text-gray-600 mb-4">
              {activeTab === 'all' 
                ? "You haven't created any triggers yet." 
                : `No ${activeTab} triggers found.`
              }
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              <span>Create Your First Trigger</span>
            </button>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showCreateModal && renderCreateModal()}
    </div>
  );
};

export default TriggerConfigurator;