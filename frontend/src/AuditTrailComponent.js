import React, { useState, useEffect } from 'react';
import './AuditTrail.css';

const AuditTrailComponent = () => {
    const [user, setUser] = useState(null);
    const [auditLogs, setAuditLogs] = useState([]);
    const [metadataSnapshots, setMetadataSnapshots] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('logs');
    
    // Filter states
    const [filters, setFilters] = useState({
        start_date: '',
        end_date: '',
        event_types: '',
        severities: '',
        search_text: '',
        content_id: ''
    });
    
    // Pagination states
    const [pagination, setPagination] = useState({
        limit: 50,
        offset: 0,
        total: 0
    });
    
    // Timeline state
    const [timelineData, setTimelineData] = useState([]);
    const [selectedContentId, setSelectedContentId] = useState('');

    const getBackendUrl = () => {
        return process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    };

    const getAuthToken = () => {
        return localStorage.getItem('token');
    };

    const getAuthHeaders = () => {
        const token = getAuthToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    };

    useEffect(() => {
        checkUserAuth();
        fetchInitialData();
    }, []);

    const checkUserAuth = () => {
        const token = getAuthToken();
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({ 
                    id: payload.sub, 
                    username: payload.username || 'User',
                    is_admin: payload.is_admin || false,
                    role: payload.role || 'user'
                });
            } catch (error) {
                console.error('Error parsing token:', error);
                localStorage.removeItem('token');
            }
        }
    };

    const fetchInitialData = async () => {
        try {
            await Promise.all([
                fetchAuditLogs(),
                fetchStatistics(),
                fetchAlerts()
            ]);
        } catch (error) {
            console.error('Error fetching initial data:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAuditLogs = async () => {
        try {
            const queryParams = new URLSearchParams({
                limit: pagination.limit.toString(),
                offset: pagination.offset.toString(),
                ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v))
            });

            const response = await fetch(`${getBackendUrl()}/api/audit/logs?${queryParams}`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setAuditLogs(data.audit_logs || []);
                setPagination(prev => ({
                    ...prev,
                    total: data.total_count || 0
                }));
            }
        } catch (error) {
            console.error('Error fetching audit logs:', error);
        }
    };

    const fetchStatistics = async () => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/audit/statistics`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setStatistics(data.statistics || null);
            }
        } catch (error) {
            console.error('Error fetching statistics:', error);
        }
    };

    const fetchAlerts = async () => {
        try {
            if (!user?.is_admin && user?.role !== 'admin' && user?.role !== 'super_admin') {
                return; // Only admins can see alerts
            }

            const response = await fetch(`${getBackendUrl()}/api/audit/alerts`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setAlerts(data.alerts || []);
            }
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    };

    const fetchContentTimeline = async (contentId) => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/audit/timeline/${contentId}`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                setTimelineData(data.timeline || []);
            }
        } catch (error) {
            console.error('Error fetching content timeline:', error);
        }
    };

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const applyFilters = async () => {
        setPagination(prev => ({ ...prev, offset: 0 }));
        await fetchAuditLogs();
    };

    const clearFilters = () => {
        setFilters({
            start_date: '',
            end_date: '',
            event_types: '',
            severities: '',
            search_text: '',
            content_id: ''
        });
        setPagination(prev => ({ ...prev, offset: 0 }));
        fetchAuditLogs();
    };

    const downloadReport = async (format) => {
        try {
            const formData = new FormData();
            formData.append('report_name', `Audit Report ${new Date().toLocaleDateString()}`);
            formData.append('report_type', 'detailed');
            formData.append('export_format', format);
            
            if (filters.start_date) formData.append('start_date', filters.start_date);
            if (filters.end_date) formData.append('end_date', filters.end_date);
            if (filters.event_types) formData.append('event_types', filters.event_types);

            const response = await fetch(`${getBackendUrl()}/api/audit/reports/generate`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Create and download the report
                const reportBlob = new Blob([JSON.stringify(data.report_data, null, 2)], {
                    type: format === 'json' ? 'application/json' : 'text/plain'
                });
                
                const url = URL.createObjectURL(reportBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `audit_report_${data.report_id}.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                alert('Report downloaded successfully!');
            } else {
                alert('Failed to generate report');
            }
        } catch (error) {
            console.error('Error downloading report:', error);
            alert('Error downloading report');
        }
    };

    const acknowledgeAlert = async (alertId) => {
        try {
            const response = await fetch(`${getBackendUrl()}/api/audit/alerts/${alertId}/acknowledge`, {
                method: 'PUT',
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                await fetchAlerts(); // Refresh alerts
                alert('Alert acknowledged successfully');
            } else {
                alert('Failed to acknowledge alert');
            }
        } catch (error) {
            console.error('Error acknowledging alert:', error);
            alert('Error acknowledging alert');
        }
    };

    const formatTimestamp = (timestamp) => {
        return new Date(timestamp).toLocaleString();
    };

    const getSeverityColor = (severity) => {
        const colors = {
            'info': '#3b82f6',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'critical': '#dc2626',
            'security': '#7c3aed'
        };
        return colors[severity] || colors.info;
    };

    const getEventTypeIcon = (eventType) => {
        const icons = {
            'upload': '📁',
            'validation': '✅',
            'rights_check': '🔒',
            'metadata_update': '📝',
            'user_action': '👤',
            'system_event': '⚙️',
            'compliance_check': '📋',
            'contract_trigger': '📄',
            'export': '📤',
            'login': '🔑',
            'logout': '🚪'
        };
        return icons[eventType] || '📄';
    };

    if (!user) {
        return (
            <div className="audit-trail-container">
                <div className="auth-required">
                    <h2>Authentication Required</h2>
                    <p>Please log in to access Audit Trail features.</p>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="audit-trail-container">
                <div className="loading">
                    <div className="loading-spinner"></div>
                    <p>Loading audit trail data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="audit-trail-container">
            <div className="audit-trail-header">
                <h1>🔍 Audit Trail & Logging</h1>
                <p>Immutable logs of uploads, validations, and rights checks with timestamped metadata snapshots</p>
                <div className="user-access-info">
                    <span className="access-level">
                        Access Level: {user.role === 'super_admin' ? 'Super Admin' : 
                                     user.is_admin || user.role === 'admin' ? 'Admin' : 
                                     'Content Owner'}
                    </span>
                </div>
            </div>

            <div className="tab-navigation">
                <button 
                    className={activeTab === 'logs' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('logs')}
                >
                    Audit Logs ({auditLogs.length})
                </button>
                <button 
                    className={activeTab === 'timeline' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('timeline')}
                >
                    Content Timeline
                </button>
                <button 
                    className={activeTab === 'statistics' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('statistics')}
                >
                    Statistics
                </button>
                {(user.is_admin || user.role === 'admin' || user.role === 'super_admin') && (
                    <button 
                        className={activeTab === 'alerts' ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab('alerts')}
                    >
                        Alerts ({alerts.length})
                    </button>
                )}
                <button 
                    className={activeTab === 'reports' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('reports')}
                >
                    Reports
                </button>
            </div>

            <div className="tab-content">
                {activeTab === 'logs' && (
                    <div className="logs-section">
                        <div className="filters-section">
                            <h3>Filters</h3>
                            <div className="filters-grid">
                                <div className="filter-group">
                                    <label>Start Date</label>
                                    <input 
                                        type="datetime-local"
                                        value={filters.start_date}
                                        onChange={(e) => handleFilterChange('start_date', e.target.value)}
                                    />
                                </div>
                                <div className="filter-group">
                                    <label>End Date</label>
                                    <input 
                                        type="datetime-local"
                                        value={filters.end_date}
                                        onChange={(e) => handleFilterChange('end_date', e.target.value)}
                                    />
                                </div>
                                <div className="filter-group">
                                    <label>Event Types</label>
                                    <select 
                                        value={filters.event_types}
                                        onChange={(e) => handleFilterChange('event_types', e.target.value)}
                                    >
                                        <option value="">All Types</option>
                                        <option value="upload">Upload</option>
                                        <option value="validation">Validation</option>
                                        <option value="rights_check">Rights Check</option>
                                        <option value="metadata_update">Metadata Update</option>
                                        <option value="user_action">User Action</option>
                                        <option value="system_event">System Event</option>
                                    </select>
                                </div>
                                <div className="filter-group">
                                    <label>Severity</label>
                                    <select 
                                        value={filters.severities}
                                        onChange={(e) => handleFilterChange('severities', e.target.value)}
                                    >
                                        <option value="">All Severities</option>
                                        <option value="info">Info</option>
                                        <option value="warning">Warning</option>
                                        <option value="error">Error</option>
                                        <option value="critical">Critical</option>
                                        <option value="security">Security</option>
                                    </select>
                                </div>
                                <div className="filter-group">
                                    <label>Search Text</label>
                                    <input 
                                        type="text"
                                        value={filters.search_text}
                                        onChange={(e) => handleFilterChange('search_text', e.target.value)}
                                        placeholder="Search in logs..."
                                    />
                                </div>
                                <div className="filter-group">
                                    <label>Content ID</label>
                                    <input 
                                        type="text"
                                        value={filters.content_id}
                                        onChange={(e) => handleFilterChange('content_id', e.target.value)}
                                        placeholder="Filter by content ID..."
                                    />
                                </div>
                            </div>
                            <div className="filter-actions">
                                <button onClick={applyFilters} className="apply-btn">Apply Filters</button>
                                <button onClick={clearFilters} className="clear-btn">Clear Filters</button>
                            </div>
                        </div>

                        <div className="logs-list">
                            <h3>Audit Logs</h3>
                            <div className="pagination-info">
                                Showing {pagination.offset + 1} - {Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total} records
                            </div>
                            
                            {auditLogs.length === 0 ? (
                                <div className="empty-state">
                                    <p>No audit logs found matching your criteria.</p>
                                </div>
                            ) : (
                                <div className="logs-grid">
                                    {auditLogs.map((log, index) => (
                                        <div key={index} className="log-card">
                                            <div className="log-header">
                                                <div className="log-event">
                                                    <span className="event-icon">{getEventTypeIcon(log.event_type)}</span>
                                                    <span className="event-name">{log.event_name}</span>
                                                </div>
                                                <div className="log-severity" style={{color: getSeverityColor(log.severity)}}>
                                                    {log.severity?.toUpperCase()}
                                                </div>
                                            </div>
                                            <div className="log-details">
                                                <p className="log-description">{log.event_description}</p>
                                                <div className="log-metadata">
                                                    <span><strong>Timestamp:</strong> {formatTimestamp(log.timestamp)}</span>
                                                    <span><strong>User:</strong> {log.user_email || log.user_id || 'System'}</span>
                                                    {log.content_id && <span><strong>Content:</strong> {log.content_id}</span>}
                                                    {log.isrc && <span><strong>ISRC:</strong> {log.isrc}</span>}
                                                    {log.filename && <span><strong>File:</strong> {log.filename}</span>}
                                                </div>
                                                <div className="log-outcome">
                                                    <span className={`outcome ${log.outcome}`}>
                                                        {log.outcome?.toUpperCase()}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="pagination">
                                <button 
                                    onClick={() => {
                                        setPagination(prev => ({ ...prev, offset: Math.max(0, prev.offset - prev.limit) }));
                                        fetchAuditLogs();
                                    }}
                                    disabled={pagination.offset === 0}
                                >
                                    Previous
                                </button>
                                <span>Page {Math.floor(pagination.offset / pagination.limit) + 1}</span>
                                <button 
                                    onClick={() => {
                                        setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }));
                                        fetchAuditLogs();
                                    }}
                                    disabled={pagination.offset + pagination.limit >= pagination.total}
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'timeline' && (
                    <div className="timeline-section">
                        <h3>Content Timeline</h3>
                        <div className="timeline-controls">
                            <input 
                                type="text"
                                value={selectedContentId}
                                onChange={(e) => setSelectedContentId(e.target.value)}
                                placeholder="Enter content ID to view timeline..."
                            />
                            <button 
                                onClick={() => selectedContentId && fetchContentTimeline(selectedContentId)}
                                disabled={!selectedContentId}
                            >
                                Load Timeline
                            </button>
                        </div>

                        {timelineData.length > 0 && (
                            <div className="timeline-container">
                                <div className="timeline">
                                    {timelineData.map((event, index) => (
                                        <div key={index} className="timeline-event">
                                            <div className="timeline-marker">
                                                <span className="event-icon">{getEventTypeIcon(event.event_type)}</span>
                                            </div>
                                            <div className="timeline-content">
                                                <div className="timeline-header">
                                                    <h4>{event.event_name}</h4>
                                                    <span className="timeline-timestamp">
                                                        {formatTimestamp(event.timestamp)}
                                                    </span>
                                                </div>
                                                <div className="timeline-details">
                                                    <span className={`severity ${event.severity}`}>
                                                        {event.severity?.toUpperCase()}
                                                    </span>
                                                    <span className={`outcome ${event.outcome}`}>
                                                        {event.outcome?.toUpperCase()}
                                                    </span>
                                                </div>
                                                {event.type === 'metadata_snapshot' && (
                                                    <div className="snapshot-info">
                                                        <strong>Metadata Snapshot:</strong> {event.data?.trigger_reason}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'statistics' && (
                    <div className="statistics-section">
                        <h3>Audit Trail Statistics</h3>
                        
                        {statistics ? (
                            <div className="statistics-grid">
                                <div className="stat-card">
                                    <h4>Total Events</h4>
                                    <div className="stat-number">{statistics.total_events}</div>
                                </div>
                                
                                <div className="stat-card">
                                    <h4>Upload Statistics</h4>
                                    <div className="stat-details">
                                        <div>Total: {statistics.upload_stats?.total_uploads || 0}</div>
                                        <div>Success: {statistics.upload_stats?.successful_uploads || 0}</div>
                                        <div>Success Rate: {statistics.upload_stats?.success_rate?.toFixed(1) || 0}%</div>
                                    </div>
                                </div>
                                
                                <div className="stat-card">
                                    <h4>Validation Statistics</h4>
                                    <div className="stat-details">
                                        <div>Total: {statistics.validation_stats?.total_validations || 0}</div>
                                        <div>Success: {statistics.validation_stats?.successful_validations || 0}</div>
                                        <div>Success Rate: {statistics.validation_stats?.success_rate?.toFixed(1) || 0}%</div>
                                    </div>
                                </div>
                                
                                <div className="stat-card">
                                    <h4>Events by Type</h4>
                                    <div className="stat-details">
                                        {Object.entries(statistics.events_by_type || {}).map(([type, count]) => (
                                            <div key={type}>{type}: {count}</div>
                                        ))}
                                    </div>
                                </div>
                                
                                <div className="stat-card">
                                    <h4>Events by Severity</h4>
                                    <div className="stat-details">
                                        {Object.entries(statistics.events_by_severity || {}).map(([severity, count]) => (
                                            <div key={severity} style={{color: getSeverityColor(severity)}}>
                                                {severity}: {count}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <p>No statistics available.</p>
                        )}
                    </div>
                )}

                {activeTab === 'alerts' && (user.is_admin || user.role === 'admin' || user.role === 'super_admin') && (
                    <div className="alerts-section">
                        <h3>Real-time Security Alerts</h3>
                        
                        {alerts.length === 0 ? (
                            <div className="empty-state">
                                <p>No active alerts.</p>
                            </div>
                        ) : (
                            <div className="alerts-grid">
                                {alerts.map((alert, index) => (
                                    <div key={index} className={`alert-card ${alert.severity}`}>
                                        <div className="alert-header">
                                            <h4>{alert.title}</h4>
                                            <span className={`alert-status ${alert.status}`}>
                                                {alert.status?.toUpperCase()}
                                            </span>
                                        </div>
                                        <p>{alert.message}</p>
                                        <div className="alert-metadata">
                                            <span><strong>Type:</strong> {alert.alert_type}</span>
                                            <span><strong>Created:</strong> {formatTimestamp(alert.created_at)}</span>
                                            {alert.user_id && <span><strong>User:</strong> {alert.user_id}</span>}
                                        </div>
                                        {alert.status === 'active' && (
                                            <button 
                                                onClick={() => acknowledgeAlert(alert.alert_id)}
                                                className="acknowledge-btn"
                                            >
                                                Acknowledge
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'reports' && (
                    <div className="reports-section">
                        <h3>Generate Audit Reports</h3>
                        <div className="report-options">
                            <p>Generate comprehensive audit reports with current filter settings</p>
                            <div className="export-buttons">
                                <button onClick={() => downloadReport('json')} className="export-btn">
                                    📄 Download JSON Report
                                </button>
                                <button onClick={() => downloadReport('csv')} className="export-btn">
                                    📊 Download CSV Report
                                </button>
                                <button onClick={() => downloadReport('pdf')} className="export-btn">
                                    📋 Download PDF Report
                                </button>
                            </div>
                            <div className="report-info">
                                <p><strong>Report will include:</strong></p>
                                <ul>
                                    <li>All audit logs matching current filters</li>
                                    <li>Statistical summary</li>
                                    <li>Metadata snapshots (if applicable)</li>
                                    <li>Compliance information</li>
                                    <li>Generated timestamp and user information</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AuditTrailComponent;