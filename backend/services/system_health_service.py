"""
Big Mann Entertainment - System Health & Logs Service
Phase 4: Advanced Features - System Health & Logs Backend
"""

import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import logging
import psutil
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SystemComponent(str, Enum):
    API_SERVER = "api_server"
    DATABASE = "database"
    STORAGE = "storage"
    QUEUE = "queue"
    CACHE = "cache"
    CDN = "cdn"
    EXTERNAL_APIS = "external_apis"
    PAYMENT_GATEWAY = "payment_gateway"

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Pydantic Models
class SystemLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: LogLevel
    component: SystemComponent
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SystemMetric(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    component: SystemComponent
    metric_name: str
    metric_value: float
    unit: str
    tags: Dict[str, str] = Field(default_factory=dict)

class HealthCheck(BaseModel):
    component: SystemComponent
    status: HealthStatus
    response_time: float  # in milliseconds
    last_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class SystemAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    message: str
    severity: AlertSeverity
    component: SystemComponent
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PerformanceMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_in: float
    network_out: float
    active_connections: int
    response_time_avg: float
    error_rate: float
    uptime: float  # in hours

class LogQuery(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    level: Optional[LogLevel] = None
    component: Optional[SystemComponent] = None
    user_id: Optional[str] = None
    search_text: Optional[str] = None
    limit: int = 100
    offset: int = 0

class SystemHealthService:
    """Service for system health monitoring and logging"""
    
    def __init__(self):
        self.logs_cache = []
        self.metrics_cache = []
        self.alerts_cache = {}
        self.health_checks = {}
        self._initialize_health_checks()
    
    def _initialize_health_checks(self):
        """Initialize health checks for all components"""
        components = [
            SystemComponent.API_SERVER,
            SystemComponent.DATABASE,
            SystemComponent.STORAGE,
            SystemComponent.QUEUE,
            SystemComponent.CACHE,
            SystemComponent.CDN,
            SystemComponent.EXTERNAL_APIS,
            SystemComponent.PAYMENT_GATEWAY
        ]
        
        for component in components:
            self.health_checks[component] = HealthCheck(
                component=component,
                status=HealthStatus.HEALTHY,
                response_time=50.0
            )
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            # Update health checks with current data
            await self._update_health_checks()
            
            health_statuses = list(self.health_checks.values())
            
            # Calculate overall health
            healthy_count = len([h for h in health_statuses if h.status == HealthStatus.HEALTHY])
            warning_count = len([h for h in health_statuses if h.status == HealthStatus.WARNING])
            critical_count = len([h for h in health_statuses if h.status == HealthStatus.CRITICAL])
            down_count = len([h for h in health_statuses if h.status == HealthStatus.DOWN])
            
            # Determine overall status
            if down_count > 0 or critical_count > 2:
                overall_status = HealthStatus.CRITICAL
            elif critical_count > 0 or warning_count > 1:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.HEALTHY
            
            # Get performance metrics
            performance = await self._get_performance_metrics()
            
            return {
                "success": True,
                "overall_status": overall_status,
                "components": [health.dict() for health in health_statuses],
                "summary": {
                    "healthy": healthy_count,
                    "warning": warning_count,
                    "critical": critical_count,
                    "down": down_count,
                    "total": len(health_statuses)
                },
                "performance": performance.dict(),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_logs(self, query: LogQuery, user_id: str = None) -> Dict[str, Any]:
        """Get system logs based on query parameters"""
        try:
            # Generate sample logs for demo
            sample_logs = self._generate_sample_logs()
            
            # Apply filters
            filtered_logs = sample_logs
            
            if query.level:
                filtered_logs = [log for log in filtered_logs if log.level == query.level]
            if query.component:
                filtered_logs = [log for log in filtered_logs if log.component == query.component]
            if query.user_id:
                filtered_logs = [log for log in filtered_logs if log.user_id == query.user_id]
            if query.search_text:
                filtered_logs = [log for log in filtered_logs if query.search_text.lower() in log.message.lower()]
            if query.start_time:
                filtered_logs = [log for log in filtered_logs if log.timestamp >= query.start_time]
            if query.end_time:
                filtered_logs = [log for log in filtered_logs if log.timestamp <= query.end_time]
            
            # Apply pagination
            total = len(filtered_logs)
            logs = filtered_logs[query.offset:query.offset + query.limit]
            
            return {
                "success": True,
                "logs": [log.dict() for log in logs],
                "total": total,
                "limit": query.limit,
                "offset": query.offset,
                "summary": {
                    "error_count": len([log for log in logs if log.level == LogLevel.ERROR]),
                    "warning_count": len([log for log in logs if log.level == LogLevel.WARNING]),
                    "info_count": len([log for log in logs if log.level == LogLevel.INFO])
                }
            }
        except Exception as e:
            logger.error(f"Error fetching logs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "logs": []
            }
    
    async def get_system_metrics(self, component: SystemComponent = None, 
                               hours: int = 24) -> Dict[str, Any]:
        """Get system metrics for monitoring"""
        try:
            # Generate sample metrics
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            metrics = self._generate_sample_metrics(start_time, end_time, component)
            
            # Group metrics by component and metric name
            grouped_metrics = {}
            for metric in metrics:
                key = f"{metric.component}_{metric.metric_name}"
                if key not in grouped_metrics:
                    grouped_metrics[key] = []
                grouped_metrics[key].append({
                    "timestamp": metric.timestamp.isoformat(),
                    "value": metric.metric_value,
                    "unit": metric.unit
                })
            
            return {
                "success": True,
                "metrics": grouped_metrics,
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "total_data_points": len(metrics)
            }
        except Exception as e:
            logger.error(f"Error fetching system metrics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_alerts(self, severity: AlertSeverity = None, 
                              component: SystemComponent = None,
                              resolved: bool = None) -> Dict[str, Any]:
        """Get system alerts"""
        try:
            # Sample alerts
            sample_alerts = [
                SystemAlert(
                    id="alert_001",
                    title="High CPU Usage",
                    message="CPU usage has exceeded 85% for the past 10 minutes",
                    severity=AlertSeverity.HIGH,
                    component=SystemComponent.API_SERVER,
                    triggered_at=datetime.now(timezone.utc) - timedelta(minutes=15)
                ),
                SystemAlert(
                    id="alert_002",
                    title="Database Connection Pool Full",
                    message="Database connection pool is at 95% capacity",
                    severity=AlertSeverity.MEDIUM,
                    component=SystemComponent.DATABASE,
                    triggered_at=datetime.now(timezone.utc) - timedelta(hours=2)
                ),
                SystemAlert(
                    id="alert_003",
                    title="Storage Space Low",
                    message="Available disk space is below 10GB",
                    severity=AlertSeverity.CRITICAL,
                    component=SystemComponent.STORAGE,
                    triggered_at=datetime.now(timezone.utc) - timedelta(hours=1)
                ),
                SystemAlert(
                    id="alert_004",
                    title="Payment Gateway Timeout",
                    message="Payment gateway response time exceeding 30 seconds",
                    severity=AlertSeverity.HIGH,
                    component=SystemComponent.PAYMENT_GATEWAY,
                    triggered_at=datetime.now(timezone.utc) - timedelta(minutes=45),
                    resolved_at=datetime.now(timezone.utc) - timedelta(minutes=30),
                    acknowledged=True,
                    acknowledged_by="admin_user"
                )
            ]
            
            # Apply filters
            filtered_alerts = sample_alerts
            if severity:
                filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
            if component:
                filtered_alerts = [a for a in filtered_alerts if a.component == component]
            if resolved is not None:
                if resolved:
                    filtered_alerts = [a for a in filtered_alerts if a.resolved_at is not None]
                else:
                    filtered_alerts = [a for a in filtered_alerts if a.resolved_at is None]
            
            return {
                "success": True,
                "alerts": [alert.dict() for alert in filtered_alerts],
                "total": len(filtered_alerts),
                "summary": {
                    "critical": len([a for a in filtered_alerts if a.severity == AlertSeverity.CRITICAL]),
                    "high": len([a for a in filtered_alerts if a.severity == AlertSeverity.HIGH]),
                    "medium": len([a for a in filtered_alerts if a.severity == AlertSeverity.MEDIUM]),
                    "low": len([a for a in filtered_alerts if a.severity == AlertSeverity.LOW]),
                    "unresolved": len([a for a in filtered_alerts if a.resolved_at is None])
                }
            }
        except Exception as e:
            logger.error(f"Error fetching system alerts: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "alerts": []
            }
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> Dict[str, Any]:
        """Acknowledge a system alert"""
        try:
            # In production, this would update the database
            logger.info(f"Alert {alert_id} acknowledged by user {user_id}")
            
            return {
                "success": True,
                "message": "Alert acknowledged successfully",
                "acknowledged_at": datetime.now(timezone.utc).isoformat(),
                "acknowledged_by": user_id
            }
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution_notes: str = None) -> Dict[str, Any]:
        """Resolve a system alert"""
        try:
            # In production, this would update the database
            logger.info(f"Alert {alert_id} resolved by user {user_id}: {resolution_notes}")
            
            return {
                "success": True,
                "message": "Alert resolved successfully",
                "resolved_at": datetime.now(timezone.utc).isoformat(),
                "resolved_by": user_id,
                "resolution_notes": resolution_notes
            }
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and metrics"""
        try:
            stats = {
                "uptime": {
                    "seconds": 1_234_567,
                    "human_readable": "14 days, 6 hours, 56 minutes"
                },
                "requests": {
                    "total_today": 45_678,
                    "total_this_hour": 3_456,
                    "average_per_minute": 57.6,
                    "peak_per_minute": 145
                },
                "errors": {
                    "total_today": 23,
                    "error_rate": 0.05,
                    "critical_errors": 2,
                    "resolved_errors": 21
                },
                "performance": {
                    "average_response_time": 245.6,
                    "p95_response_time": 892.3,
                    "p99_response_time": 1542.8,
                    "slowest_endpoint": "/api/analytics/generate-report"
                },
                "resources": {
                    "cpu_usage": 34.5,
                    "memory_usage": 67.8,
                    "disk_usage": 45.2,
                    "network_usage": 23.4
                },
                "database": {
                    "active_connections": 15,
                    "max_connections": 100,
                    "queries_per_second": 234.5,
                    "slow_queries": 3
                },
                "cache": {
                    "hit_rate": 89.4,
                    "miss_rate": 10.6,
                    "total_keys": 12_456,
                    "memory_usage": "45.2 MB"
                }
            }
            
            return {
                "success": True,
                "stats": stats,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching system stats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_health_checks(self):
        """Update health check statuses"""
        try:
            # Simulate health checks for different components
            import random
            
            for component, health_check in self.health_checks.items():
                # Simulate random health status (mostly healthy)
                status_weights = [0.8, 0.15, 0.04, 0.01]  # healthy, warning, critical, down
                statuses = [HealthStatus.HEALTHY, HealthStatus.WARNING, HealthStatus.CRITICAL, HealthStatus.DOWN]
                
                health_check.status = random.choices(statuses, weights=status_weights)[0]
                health_check.response_time = random.uniform(20, 200)
                health_check.last_check = datetime.now(timezone.utc)
                
                if health_check.status != HealthStatus.HEALTHY:
                    health_check.error_message = f"Component {component} experiencing issues"
                else:
                    health_check.error_message = None
        except Exception as e:
            logger.error(f"Error updating health checks: {str(e)}")
    
    async def _get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        try:
            # Try to get real system metrics, fallback to mock data
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                return PerformanceMetrics(
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    disk_usage=(disk.used / disk.total) * 100,
                    network_in=network.bytes_recv / 1024 / 1024,  # MB
                    network_out=network.bytes_sent / 1024 / 1024,  # MB
                    active_connections=len(psutil.net_connections()),
                    response_time_avg=245.6,
                    error_rate=0.05,
                    uptime=234.5
                )
            except:
                # Fallback to mock data
                return PerformanceMetrics(
                    cpu_usage=34.5,
                    memory_usage=67.8,
                    disk_usage=45.2,
                    network_in=123.4,
                    network_out=89.6,
                    active_connections=25,
                    response_time_avg=245.6,
                    error_rate=0.05,
                    uptime=234.5
                )
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return PerformanceMetrics(
                cpu_usage=0,
                memory_usage=0,
                disk_usage=0,
                network_in=0,
                network_out=0,
                active_connections=0,
                response_time_avg=0,
                error_rate=0,
                uptime=0
            )
    
    def _generate_sample_logs(self) -> List[SystemLog]:
        """Generate sample log entries"""
        import random
        
        logs = []
        components = list(SystemComponent)
        levels = list(LogLevel)
        
        sample_messages = [
            "User authentication successful",
            "Database query executed successfully",
            "File uploaded to storage",
            "Payment processed successfully",
            "API request completed",
            "Cache miss - fetching from database",
            "Background job started",
            "Email notification sent",
            "Asset validation completed",
            "Distribution job initiated",
            "Warning: High memory usage detected",
            "Error: Failed to connect to external API",
            "Critical: Database connection timeout",
            "Debug: Processing batch upload",
            "Info: System maintenance completed"
        ]
        
        # Generate logs for the past 24 hours
        start_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        for i in range(100):
            timestamp = start_time + timedelta(seconds=random.randint(0, 86400))
            
            log = SystemLog(
                timestamp=timestamp,
                level=random.choice(levels),
                component=random.choice(components),
                message=random.choice(sample_messages),
                user_id=f"user_{random.randint(1, 100)}" if random.random() > 0.7 else None,
                session_id=f"session_{random.randint(1000, 9999)}",
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                request_id=f"req_{random.randint(10000, 99999)}"
            )
            logs.append(log)
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs
    
    def _generate_sample_metrics(self, start_time: datetime, end_time: datetime, 
                                component: SystemComponent = None) -> List[SystemMetric]:
        """Generate sample system metrics"""
        import random
        
        metrics = []
        components = [component] if component else list(SystemComponent)
        
        metric_definitions = {
            SystemComponent.API_SERVER: [
                ("response_time", "ms"),
                ("requests_per_second", "req/s"),
                ("error_rate", "%"),
                ("cpu_usage", "%")
            ],
            SystemComponent.DATABASE: [
                ("query_time", "ms"),
                ("connections", "count"),
                ("queries_per_second", "qps")
            ],
            SystemComponent.STORAGE: [
                ("disk_usage", "%"),
                ("io_operations", "ops/s"),
                ("throughput", "MB/s")
            ],
            SystemComponent.CACHE: [
                ("hit_rate", "%"),
                ("memory_usage", "MB"),
                ("operations", "ops/s")
            ]
        }
        
        current_time = start_time
        while current_time <= end_time:
            for comp in components:
                if comp in metric_definitions:
                    for metric_name, unit in metric_definitions[comp]:
                        # Generate realistic metric values
                        base_values = {
                            "response_time": random.uniform(50, 300),
                            "requests_per_second": random.uniform(10, 100),
                            "error_rate": random.uniform(0, 5),
                            "cpu_usage": random.uniform(20, 80),
                            "query_time": random.uniform(10, 100),
                            "connections": random.randint(5, 50),
                            "queries_per_second": random.uniform(50, 500),
                            "disk_usage": random.uniform(30, 90),
                            "io_operations": random.uniform(100, 1000),
                            "throughput": random.uniform(10, 100),
                            "hit_rate": random.uniform(80, 95),
                            "memory_usage": random.uniform(100, 1000),
                            "operations": random.uniform(100, 1000)
                        }
                        
                        metric = SystemMetric(
                            timestamp=current_time,
                            component=comp,
                            metric_name=metric_name,
                            metric_value=base_values.get(metric_name, random.uniform(0, 100)),
                            unit=unit
                        )
                        metrics.append(metric)
            
            current_time += timedelta(minutes=5)  # 5-minute intervals
        
        return metrics

# Global instance
system_health_service = SystemHealthService()