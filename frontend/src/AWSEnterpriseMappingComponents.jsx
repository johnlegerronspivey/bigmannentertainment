import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { toast } from 'sonner';
import { 
  Server, Database, Cloud, Shield, Activity, DollarSign, 
  AlertTriangle, CheckCircle, Clock, RefreshCw, Globe,
  HardDrive, Cpu, Network, Lock, TrendingUp, BarChart3,
  Layers, Settings, Play, Square, Trash2, Eye
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Service Type Icons
const ServiceIcon = ({ type, className = "w-5 h-5" }) => {
  const icons = {
    compute: <Cpu className={className} />,
    storage: <HardDrive className={className} />,
    database: <Database className={className} />,
    networking: <Network className={className} />,
    security: <Shield className={className} />,
    analytics: <BarChart3 className={className} />,
    ai_ml: <Activity className={className} />,
    management: <Settings className={className} />,
    application: <Layers className={className} />,
    media: <Cloud className={className} />
  };
  return icons[type] || <Server className={className} />;
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const statusConfig = {
    active: { color: 'bg-green-500', label: 'Active' },
    running: { color: 'bg-green-500', label: 'Running' },
    inactive: { color: 'bg-gray-500', label: 'Inactive' },
    stopped: { color: 'bg-yellow-500', label: 'Stopped' },
    pending: { color: 'bg-blue-500', label: 'Pending' },
    error: { color: 'bg-red-500', label: 'Error' },
    maintenance: { color: 'bg-orange-500', label: 'Maintenance' },
    terminated: { color: 'bg-red-700', label: 'Terminated' }
  };
  
  const config = statusConfig[status?.toLowerCase()] || statusConfig.inactive;
  
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white ${config.color}`}>
      {config.label}
    </span>
  );
};

// Cost Tier Badge
const CostTierBadge = ({ cost }) => {
  let tier = 'free_tier';
  let color = 'bg-green-100 text-green-800';
  
  if (cost > 500) {
    tier = 'critical';
    color = 'bg-red-100 text-red-800';
  } else if (cost > 200) {
    tier = 'high';
    color = 'bg-orange-100 text-orange-800';
  } else if (cost > 50) {
    tier = 'medium';
    color = 'bg-yellow-100 text-yellow-800';
  } else if (cost > 0) {
    tier = 'low';
    color = 'bg-blue-100 text-blue-800';
  }
  
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      ${cost.toFixed(2)}
    </span>
  );
};

// Overview Dashboard
const OverviewDashboard = ({ metrics, infraMap, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-purple-500 to-purple-700 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Total Resources</p>
                <p className="text-3xl font-bold">{metrics?.total_resources || 0}</p>
              </div>
              <Server className="w-10 h-10 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-700 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Monthly Cost</p>
                <p className="text-3xl font-bold">${(metrics?.total_monthly_cost || 0).toFixed(2)}</p>
              </div>
              <DollarSign className="w-10 h-10 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500 to-blue-700 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Security Score</p>
                <p className="text-3xl font-bold">{metrics?.security_score || 0}%</p>
              </div>
              <Shield className="w-10 h-10 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-500 to-amber-700 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-amber-100 text-sm">Compliance</p>
                <p className="text-3xl font-bold">{metrics?.compliance_score || 0}%</p>
              </div>
              <CheckCircle className="w-10 h-10 text-amber-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Resource Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-600" />
              Resource Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  Healthy
                </span>
                <span className="font-bold text-green-600">{infraMap?.healthy_resources || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  Warning
                </span>
                <span className="font-bold text-yellow-600">{infraMap?.warning_resources || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  Critical
                </span>
                <span className="font-bold text-red-600">{infraMap?.critical_resources || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5 text-blue-600" />
              Resources by Region
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(infraMap?.resources_by_region || {}).slice(0, 5).map(([region, count]) => (
                <div key={region} className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">{region}</span>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Resource Counts by Service */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-600" />
            Resources by Service Type
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(infraMap?.resource_counts || {}).map(([service, count]) => (
              <div key={service} className="text-center p-4 bg-slate-50 rounded-lg">
                <ServiceIcon type={service.split(':')[0]} className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <p className="text-2xl font-bold text-slate-800">{count}</p>
                <p className="text-xs text-slate-500">{service.replace(':', ' ').toUpperCase()}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// EC2 Instances Tab
const EC2InstancesTab = ({ instances, loading, onRefresh, onAction }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">EC2 Instances ({instances.length})</h3>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4">
        {instances.map((instance) => (
          <Card key={instance.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <Cpu className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">{instance.name}</h4>
                    <p className="text-sm text-slate-500">{instance.resource_id}</p>
                  </div>
                </div>
                <StatusBadge status={instance.state} />
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div>
                  <p className="text-xs text-slate-500">Instance Type</p>
                  <p className="font-medium">{instance.instance_type}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Region</p>
                  <p className="font-medium">{instance.region}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Public IP</p>
                  <p className="font-medium">{instance.public_ip || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Private IP</p>
                  <p className="font-medium">{instance.private_ip || 'N/A'}</p>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                {instance.state === 'running' ? (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => onAction(instance.resource_id, 'stop')}
                  >
                    <Square className="w-4 h-4 mr-1" />
                    Stop
                  </Button>
                ) : (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => onAction(instance.resource_id, 'start')}
                  >
                    <Play className="w-4 h-4 mr-1" />
                    Start
                  </Button>
                )}
                <Button variant="ghost" size="sm">
                  <Eye className="w-4 h-4 mr-1" />
                  Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {instances.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            <Server className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>No EC2 instances found</p>
          </div>
        )}
      </div>
    </div>
  );
};

// S3 Buckets Tab
const S3BucketsTab = ({ buckets, loading, onRefresh }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">S3 Buckets ({buckets.length})</h3>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4">
        {buckets.map((bucket) => (
          <Card key={bucket.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <HardDrive className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">{bucket.bucket_name}</h4>
                    <p className="text-sm text-slate-500">Region: {bucket.region}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  {bucket.versioning_enabled && (
                    <Badge variant="secondary">Versioning</Badge>
                  )}
                  {bucket.public_access_blocked && (
                    <Badge className="bg-green-100 text-green-800">Private</Badge>
                  )}
                  {!bucket.public_access_blocked && (
                    <Badge className="bg-red-100 text-red-800">Public</Badge>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div>
                  <p className="text-xs text-slate-500">Encryption</p>
                  <p className="font-medium">{bucket.encryption_enabled ? 'Enabled' : 'Disabled'}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Objects</p>
                  <p className="font-medium">{bucket.object_count || 0}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Storage Class</p>
                  <p className="font-medium">{bucket.storage_class}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {buckets.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            <HardDrive className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>No S3 buckets found</p>
          </div>
        )}
      </div>
    </div>
  );
};

// RDS Instances Tab
const RDSInstancesTab = ({ instances, loading, onRefresh }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">RDS Instances ({instances.length})</h3>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4">
        {instances.map((instance) => (
          <Card key={instance.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Database className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">{instance.db_instance_identifier}</h4>
                    <p className="text-sm text-slate-500">{instance.engine} {instance.engine_version}</p>
                  </div>
                </div>
                <StatusBadge status={instance.status} />
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div>
                  <p className="text-xs text-slate-500">Instance Class</p>
                  <p className="font-medium">{instance.instance_class}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Storage</p>
                  <p className="font-medium">{instance.allocated_storage} GB</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Multi-AZ</p>
                  <p className="font-medium">{instance.multi_az ? 'Yes' : 'No'}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Endpoint</p>
                  <p className="font-medium text-xs truncate">{instance.endpoint || 'N/A'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {instances.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            <Database className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>No RDS instances found</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Lambda Functions Tab
const LambdaFunctionsTab = ({ functions, loading, onRefresh }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Lambda Functions ({functions.length})</h3>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid gap-4">
        {functions.map((func) => (
          <Card key={func.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-amber-100 rounded-lg">
                    <Activity className="w-6 h-6 text-amber-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">{func.function_name}</h4>
                    <p className="text-sm text-slate-500">Runtime: {func.runtime}</p>
                  </div>
                </div>
                <StatusBadge status={func.status} />
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div>
                  <p className="text-xs text-slate-500">Memory</p>
                  <p className="font-medium">{func.memory_size} MB</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Timeout</p>
                  <p className="font-medium">{func.timeout}s</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Code Size</p>
                  <p className="font-medium">{(func.code_size / 1024).toFixed(1)} KB</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Handler</p>
                  <p className="font-medium text-xs truncate">{func.handler}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {functions.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            <Activity className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>No Lambda functions found</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Cost Analysis Tab
const CostAnalysisTab = ({ costBreakdown, loading, onRefresh }) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Cost Analysis</h3>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Total Cost Card */}
      <Card className="bg-gradient-to-r from-green-500 to-emerald-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Total Monthly Cost</p>
              <p className="text-4xl font-bold">${(costBreakdown?.total_cost || 0).toFixed(2)}</p>
              <p className="text-green-100 text-sm mt-1">USD</p>
            </div>
            <DollarSign className="w-16 h-16 text-green-200" />
          </div>
        </CardContent>
      </Card>

      {/* Cost by Service */}
      <Card>
        <CardHeader>
          <CardTitle>Cost by Service</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(costBreakdown?.by_service || {})
              .sort(([, a], [, b]) => b - a)
              .map(([service, cost]) => (
                <div key={service} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <ServiceIcon type={service.toLowerCase().includes('ec2') ? 'compute' : 
                      service.toLowerCase().includes('s3') ? 'storage' :
                      service.toLowerCase().includes('rds') ? 'database' :
                      service.toLowerCase().includes('lambda') ? 'compute' :
                      service.toLowerCase().includes('cloudfront') ? 'networking' : 'management'
                    } />
                    <span className="text-sm">{service}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-32 bg-slate-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full" 
                        style={{ width: `${Math.min((cost / (costBreakdown?.total_cost || 1)) * 100, 100)}%` }}
                      />
                    </div>
                    <span className="font-medium w-20 text-right">${cost.toFixed(2)}</span>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Cost by Region */}
      <Card>
        <CardHeader>
          <CardTitle>Cost by Region</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(costBreakdown?.by_region || {}).map(([region, cost]) => (
              <div key={region} className="p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Globe className="w-4 h-4 text-slate-500" />
                  <span className="text-sm text-slate-600">{region}</span>
                </div>
                <p className="text-xl font-bold">${cost.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main Dashboard Component
const AWSEnterpriseMapping = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [infraMap, setInfraMap] = useState(null);
  const [ec2Instances, setEc2Instances] = useState([]);
  const [s3Buckets, setS3Buckets] = useState([]);
  const [rdsInstances, setRdsInstances] = useState([]);
  const [lambdaFunctions, setLambdaFunctions] = useState([]);
  const [costBreakdown, setCostBreakdown] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  // Fetch health status
  const fetchHealthStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/health`);
      const data = await response.json();
      setHealthStatus(data);
    } catch (error) {
      console.error('Error fetching health status:', error);
    }
  }, []);

  // Fetch metrics
  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/metrics`);
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  }, []);

  // Fetch infrastructure map
  const fetchInfraMap = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/infrastructure-map`);
      if (response.ok) {
        const data = await response.json();
        setInfraMap(data);
      }
    } catch (error) {
      console.error('Error fetching infrastructure map:', error);
    }
  }, []);

  // Fetch EC2 instances
  const fetchEc2Instances = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/resources/ec2`);
      if (response.ok) {
        const data = await response.json();
        setEc2Instances(data);
      }
    } catch (error) {
      console.error('Error fetching EC2 instances:', error);
    }
  }, []);

  // Fetch S3 buckets
  const fetchS3Buckets = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/resources/s3`);
      if (response.ok) {
        const data = await response.json();
        setS3Buckets(data);
      }
    } catch (error) {
      console.error('Error fetching S3 buckets:', error);
    }
  }, []);

  // Fetch RDS instances
  const fetchRdsInstances = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/resources/rds`);
      if (response.ok) {
        const data = await response.json();
        setRdsInstances(data);
      }
    } catch (error) {
      console.error('Error fetching RDS instances:', error);
    }
  }, []);

  // Fetch Lambda functions
  const fetchLambdaFunctions = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/resources/lambda`);
      if (response.ok) {
        const data = await response.json();
        setLambdaFunctions(data);
      }
    } catch (error) {
      console.error('Error fetching Lambda functions:', error);
    }
  }, []);

  // Fetch cost breakdown
  const fetchCostBreakdown = useCallback(async () => {
    try {
      const response = await fetch(`${API}/aws-enterprise/costs`);
      if (response.ok) {
        const data = await response.json();
        setCostBreakdown(data);
      }
    } catch (error) {
      console.error('Error fetching cost breakdown:', error);
    }
  }, []);

  // Execute resource action
  const executeAction = async (resourceId, actionType) => {
    try {
      const response = await fetch(`${API}/aws-enterprise/resources/actions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resource_id: resourceId,
          action_type: actionType,
          created_by: 'admin'
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(`Action ${actionType} executed successfully`);
        fetchEc2Instances();
      } else {
        toast.error('Failed to execute action');
      }
    } catch (error) {
      console.error('Error executing action:', error);
      toast.error('Error executing action');
    }
  };

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchHealthStatus(),
        fetchMetrics(),
        fetchInfraMap(),
        fetchCostBreakdown()
      ]);
      setLoading(false);
    };
    loadData();
  }, [fetchHealthStatus, fetchMetrics, fetchInfraMap, fetchCostBreakdown]);

  // Load tab-specific data when tab changes
  const handleTabChange = useCallback((newTab) => {
    setActiveTab(newTab);
  }, []);

  useEffect(() => {
    const loadTabData = async () => {
      if (activeTab === 'ec2') {
        await fetchEc2Instances();
      } else if (activeTab === 's3') {
        await fetchS3Buckets();
      } else if (activeTab === 'rds') {
        await fetchRdsInstances();
      } else if (activeTab === 'lambda') {
        await fetchLambdaFunctions();
      }
    };
    loadTabData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <Cloud className="w-8 h-8 text-orange-400" />
                AWS Enterprise Mapping
              </h1>
              <p className="text-slate-400 mt-1">
                Full AWS Infrastructure Integration & Cloud Service Management
              </p>
            </div>
            <div className="flex items-center gap-4">
              {healthStatus && (
                <Badge className={healthStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}>
                  {healthStatus.status === 'healthy' ? (
                    <CheckCircle className="w-4 h-4 mr-1" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 mr-1" />
                  )}
                  {healthStatus.status}
                </Badge>
              )}
              <Button 
                variant="outline" 
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
                onClick={() => {
                  fetchMetrics();
                  fetchInfraMap();
                  toast.success('Dashboard refreshed');
                }}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh All
              </Button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-6">
          <TabsList className="bg-slate-800 border border-slate-700 p-1">
            <TabsTrigger value="overview" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white">
              <Activity className="w-4 h-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="ec2" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white">
              <Cpu className="w-4 h-4 mr-2" />
              EC2
            </TabsTrigger>
            <TabsTrigger value="s3" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
              <HardDrive className="w-4 h-4 mr-2" />
              S3
            </TabsTrigger>
            <TabsTrigger value="rds" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <Database className="w-4 h-4 mr-2" />
              RDS
            </TabsTrigger>
            <TabsTrigger value="lambda" className="data-[state=active]:bg-amber-600 data-[state=active]:text-white">
              <Activity className="w-4 h-4 mr-2" />
              Lambda
            </TabsTrigger>
            <TabsTrigger value="costs" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
              <DollarSign className="w-4 h-4 mr-2" />
              Costs
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <OverviewDashboard metrics={metrics} infraMap={infraMap} loading={loading} />
          </TabsContent>

          <TabsContent value="ec2">
            <EC2InstancesTab 
              instances={ec2Instances} 
              loading={loading} 
              onRefresh={fetchEc2Instances}
              onAction={executeAction}
            />
          </TabsContent>

          <TabsContent value="s3">
            <S3BucketsTab 
              buckets={s3Buckets} 
              loading={loading} 
              onRefresh={fetchS3Buckets}
            />
          </TabsContent>

          <TabsContent value="rds">
            <RDSInstancesTab 
              instances={rdsInstances} 
              loading={loading} 
              onRefresh={fetchRdsInstances}
            />
          </TabsContent>

          <TabsContent value="lambda">
            <LambdaFunctionsTab 
              functions={lambdaFunctions} 
              loading={loading} 
              onRefresh={fetchLambdaFunctions}
            />
          </TabsContent>

          <TabsContent value="costs">
            <CostAnalysisTab 
              costBreakdown={costBreakdown} 
              loading={loading} 
              onRefresh={fetchCostBreakdown}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AWSEnterpriseMapping;
