"""
Performance monitoring utilities
Tracks API response times and resource usage
"""
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import psutil


class PerformanceMonitor:
    """Monitor API performance metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._request_times: Dict[str, List[float]] = defaultdict(list)
        self._endpoint_calls: Dict[str, int] = defaultdict(int)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._slow_requests: List[Dict] = []
        self.slow_threshold = 1.0  # 1 second
    
    def record_request(
        self, 
        endpoint: str, 
        duration: float, 
        status_code: int,
        method: str = 'GET'
    ):
        """Record a request and its performance metrics"""
        # Store request time
        if len(self._request_times[endpoint]) >= self.max_history:
            self._request_times[endpoint].pop(0)
        self._request_times[endpoint].append(duration)
        
        # Increment call counter
        self._endpoint_calls[endpoint] += 1
        
        # Track errors
        if status_code >= 400:
            self._error_counts[endpoint] += 1
        
        # Track slow requests
        if duration > self.slow_threshold:
            self._slow_requests.append({
                'endpoint': endpoint,
                'method': method,
                'duration': duration,
                'status_code': status_code,
                'timestamp': datetime.utcnow().isoformat()
            })
            # Keep only last 100 slow requests
            if len(self._slow_requests) > 100:
                self._slow_requests.pop(0)
    
    def get_endpoint_stats(self, endpoint: str) -> Dict:
        """Get statistics for a specific endpoint"""
        times = self._request_times.get(endpoint, [])
        if not times:
            return {
                'endpoint': endpoint,
                'call_count': 0,
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'error_count': 0,
                'error_rate': 0
            }
        
        call_count = self._endpoint_calls[endpoint]
        error_count = self._error_counts[endpoint]
        
        return {
            'endpoint': endpoint,
            'call_count': call_count,
            'avg_response_time': sum(times) / len(times),
            'min_response_time': min(times),
            'max_response_time': max(times),
            'p95_response_time': sorted(times)[int(len(times) * 0.95)] if len(times) > 0 else 0,
            'error_count': error_count,
            'error_rate': (error_count / call_count * 100) if call_count > 0 else 0
        }
    
    def get_all_stats(self) -> Dict:
        """Get overall performance statistics"""
        all_times = [t for times in self._request_times.values() for t in times]
        total_calls = sum(self._endpoint_calls.values())
        total_errors = sum(self._error_counts.values())
        
        # Get top 10 slowest endpoints
        endpoint_stats = [
            self.get_endpoint_stats(endpoint)
            for endpoint in self._endpoint_calls.keys()
        ]
        slowest_endpoints = sorted(
            endpoint_stats, 
            key=lambda x: x['avg_response_time'], 
            reverse=True
        )[:10]
        
        # Get top 10 most called endpoints
        most_called = sorted(
            endpoint_stats,
            key=lambda x: x['call_count'],
            reverse=True
        )[:10]
        
        return {
            'overview': {
                'total_requests': total_calls,
                'total_errors': total_errors,
                'error_rate': (total_errors / total_calls * 100) if total_calls > 0 else 0,
                'avg_response_time': sum(all_times) / len(all_times) if all_times else 0,
                'slow_requests_count': len(self._slow_requests)
            },
            'slowest_endpoints': slowest_endpoints,
            'most_called_endpoints': most_called,
            'recent_slow_requests': self._slow_requests[-10:],
            'system_resources': self.get_system_resources()
        }
    
    def get_system_resources(self) -> Dict:
        """Get current system resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'disk_usage_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def reset_stats(self):
        """Reset all statistics"""
        self._request_times.clear()
        self._endpoint_calls.clear()
        self._error_counts.clear()
        self._slow_requests.clear()


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


# Decorator for timing async functions
def monitor_performance(endpoint_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                duration = time.time() - start_time
                perf_monitor.record_request(
                    endpoint_name, 
                    duration, 
                    status_code
                )
        return wrapper
    return decorator
