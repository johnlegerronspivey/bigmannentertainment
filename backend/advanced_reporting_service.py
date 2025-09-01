"""
Advanced Reporting Service for Metadata Parser & Validator
Provides comprehensive analytics, trending, and export capabilities
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import io
import csv
import json
from collections import defaultdict, Counter

from metadata_models import ValidationStatus, MetadataFormat

logger = logging.getLogger(__name__)

class AdvancedReportingService:
    """Service for generating advanced reports and analytics"""
    
    def __init__(self, mongo_db=None):
        self.mongo_db = mongo_db
    
    async def generate_comprehensive_report(self, user_id: str, date_range: Dict = None) -> Dict:
        """Generate comprehensive metadata validation report"""
        
        if self.mongo_db is None:
            return {}
        
        try:
            # Set default date range (last 30 days)
            if not date_range:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.fromisoformat(date_range.get('start_date'))
                end_date = datetime.fromisoformat(date_range.get('end_date'))
            
            query = {
                'user_id': user_id,
                'upload_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            # Get all validation results in date range
            cursor = self.mongo_db["metadata_validation_results"].find(query)
            results = await cursor.to_list(length=None)
            
            report = {
                'report_info': {
                    'generated_at': datetime.now().isoformat(),
                    'user_id': user_id,
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_validations': len(results)
                },
                'validation_summary': await self._calculate_validation_summary(results),
                'format_analysis': await self._calculate_format_analysis(results),
                'duplicate_analysis': await self._calculate_duplicate_analysis(results),
                'error_analysis': await self._calculate_error_analysis(results),
                'temporal_trends': await self._calculate_temporal_trends(results),
                'quality_metrics': await self._calculate_quality_metrics(results),
                'recommendations': await self._generate_recommendations(results)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            return {}
    
    async def generate_platform_analytics(self, date_range: Dict = None) -> Dict:
        """Generate platform-wide analytics (admin only)"""
        
        if self.mongo_db is None:
            return {}
        
        try:
            # Set default date range (last 30 days)
            if not date_range:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.fromisoformat(date_range.get('start_date'))
                end_date = datetime.fromisoformat(date_range.get('end_date'))
            
            query = {
                'upload_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            # Get all validation results in date range
            cursor = self.mongo_db["metadata_validation_results"].find(query)
            results = await cursor.to_list(length=None)
            
            # User activity analysis
            user_activity = defaultdict(int)
            for result in results:
                user_activity[result.get('user_id')] += 1
            
            report = {
                'platform_overview': {
                    'generated_at': datetime.now().isoformat(),
                    'date_range': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_validations': len(results),
                    'active_users': len(user_activity),
                    'avg_validations_per_user': sum(user_activity.values()) / len(user_activity) if user_activity else 0
                },
                'platform_validation_summary': await self._calculate_validation_summary(results),
                'platform_format_analysis': await self._calculate_format_analysis(results),
                'platform_duplicate_analysis': await self._calculate_duplicate_analysis(results),
                'user_activity_analysis': {
                    'top_users': sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10],
                    'user_distribution': dict(Counter(user_activity.values()))
                },
                'platform_trends': await self._calculate_temporal_trends(results),
                'platform_quality_metrics': await self._calculate_quality_metrics(results)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating platform analytics: {str(e)}")
            return {}
    
    async def generate_duplicate_report(self, user_id: Optional[str] = None, scope: str = 'user') -> Dict:
        """Generate detailed duplicate detection report"""
        
        if self.mongo_db is None:
            return {}
        
        try:
            # Build query based on scope
            if scope == 'user' and user_id:
                query = {'user_id': user_id, 'duplicate_count': {'$gt': 0}}
            else:
                query = {'duplicate_count': {'$gt': 0}}
            
            cursor = self.mongo_db["metadata_validation_results"].find(query)
            results = await cursor.to_list(length=None)
            
            # Analyze duplicates
            duplicate_patterns = defaultdict(list)
            identifier_conflicts = defaultdict(int)
            
            for result in results:
                for duplicate in result.get('duplicates_found', []):
                    identifier_type = duplicate.get('identifier_type')
                    identifier_value = duplicate.get('identifier_value')
                    
                    duplicate_patterns[f"{identifier_type}:{identifier_value}"].append({
                        'user_id': result.get('user_id'),
                        'file_name': result.get('file_name'),
                        'upload_date': result.get('upload_date'),
                        'first_seen': duplicate.get('first_seen_date'),
                        'last_seen': duplicate.get('last_seen_date')
                    })
                    
                    identifier_conflicts[identifier_type] += 1
            
            report = {
                'duplicate_summary': {
                    'generated_at': datetime.now().isoformat(),
                    'scope': scope,
                    'user_id': user_id,
                    'total_files_with_duplicates': len(results),
                    'unique_duplicate_identifiers': len(duplicate_patterns),
                    'identifier_type_breakdown': dict(identifier_conflicts)
                },
                'top_duplicate_patterns': sorted(
                    [(key, len(files)) for key, files in duplicate_patterns.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:20],
                'detailed_conflicts': {
                    key: files for key, files in list(duplicate_patterns.items())[:10]
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating duplicate report: {str(e)}")
            return {}
    
    async def generate_error_trend_report(self, user_id: Optional[str] = None, days: int = 30) -> Dict:
        """Generate error trend analysis report"""
        
        if self.mongo_db is None:
            return {}
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = {
                'upload_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            if user_id:
                query['user_id'] = user_id
            
            cursor = self.mongo_db["metadata_validation_results"].find(query)
            results = await cursor.to_list(length=None)
            
            # Analyze errors over time
            daily_errors = defaultdict(lambda: defaultdict(int))
            error_categories = defaultdict(int)
            
            for result in results:
                date_key = result.get('upload_date', datetime.now()).date().isoformat()
                
                for error in result.get('validation_errors', []):
                    error_field = error.get('field', 'unknown')
                    error_severity = error.get('severity', 'unknown')
                    
                    daily_errors[date_key][error_field] += 1
                    error_categories[f"{error_field}:{error_severity}"] += 1
            
            report = {
                'error_trend_summary': {
                    'generated_at': datetime.now().isoformat(),
                    'user_id': user_id,
                    'analysis_period_days': days,
                    'total_files_analyzed': len(results),
                    'total_error_occurrences': sum(error_categories.values())
                },
                'daily_error_trends': dict(daily_errors),
                'top_error_categories': sorted(
                    error_categories.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:15],
                'error_frequency_distribution': dict(Counter(error_categories.values()))
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating error trend report: {str(e)}")
            return {}
    
    async def export_report_csv(self, report_data: Dict, report_type: str) -> bytes:
        """Export report data to CSV format"""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        try:
            if report_type == 'validation_summary':
                # Export validation summary
                writer.writerow(['Metric', 'Value'])
                
                summary = report_data.get('validation_summary', {})
                for key, value in summary.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                
            elif report_type == 'format_analysis':
                # Export format analysis
                writer.writerow(['Format', 'Count', 'Percentage', 'Success Rate'])
                
                format_data = report_data.get('format_analysis', {}).get('format_distribution', {})
                total = sum(format_data.values())
                
                for format_type, count in format_data.items():
                    percentage = (count / total * 100) if total > 0 else 0
                    writer.writerow([format_type, count, f"{percentage:.1f}%", "N/A"])
                
            elif report_type == 'duplicate_patterns':
                # Export duplicate patterns
                writer.writerow(['Identifier', 'Conflict Count', 'Identifier Type'])
                
                patterns = report_data.get('top_duplicate_patterns', [])
                for pattern, count in patterns:
                    identifier_type = pattern.split(':')[0] if ':' in pattern else 'unknown'
                    writer.writerow([pattern, count, identifier_type])
                
            elif report_type == 'error_analysis':
                # Export error analysis
                writer.writerow(['Error Field', 'Severity', 'Count'])
                
                errors = report_data.get('top_error_categories', [])
                for error_info, count in errors:
                    if ':' in error_info:
                        field, severity = error_info.split(':', 1)
                        writer.writerow([field, severity, count])
                    else:
                        writer.writerow([error_info, 'unknown', count])
            
            # Get CSV content as bytes
            csv_content = output.getvalue().encode('utf-8')
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            return b''
        finally:
            output.close()
    
    async def export_report_json(self, report_data: Dict) -> bytes:
        """Export report data to JSON format"""
        
        try:
            json_content = json.dumps(report_data, indent=2, default=str)
            return json_content.encode('utf-8')
        except Exception as e:
            logger.error(f"Error exporting JSON: {str(e)}")
            return b''
    
    async def _calculate_validation_summary(self, results: List[Dict]) -> Dict:
        """Calculate validation summary statistics"""
        
        if not results:
            return {}
        
        status_counts = defaultdict(int)
        total_processing_time = 0
        processing_count = 0
        
        for result in results:
            status = result.get('validation_status', 'unknown')
            status_counts[status] += 1
            
            processing_time = result.get('processing_time')
            if processing_time:
                total_processing_time += processing_time
                processing_count += 1
        
        total = len(results)
        
        return {
            'total_validations': total,
            'valid_count': status_counts.get('valid', 0),
            'warning_count': status_counts.get('warning', 0),
            'error_count': status_counts.get('error', 0),
            'success_rate': (status_counts.get('valid', 0) / total * 100) if total > 0 else 0,
            'warning_rate': (status_counts.get('warning', 0) / total * 100) if total > 0 else 0,
            'error_rate': (status_counts.get('error', 0) / total * 100) if total > 0 else 0,
            'avg_processing_time': (total_processing_time / processing_count) if processing_count > 0 else 0
        }
    
    async def _calculate_format_analysis(self, results: List[Dict]) -> Dict:
        """Calculate format distribution and analysis"""
        
        format_counts = defaultdict(int)
        format_success_rates = defaultdict(lambda: {'total': 0, 'valid': 0})
        
        for result in results:
            file_format = result.get('file_format', 'unknown')
            format_counts[file_format] += 1
            
            format_success_rates[file_format]['total'] += 1
            if result.get('validation_status') == 'valid':
                format_success_rates[file_format]['valid'] += 1
        
        # Calculate success rates
        format_success_calculated = {}
        for fmt, stats in format_success_rates.items():
            format_success_calculated[fmt] = (stats['valid'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        return {
            'format_distribution': dict(format_counts),
            'format_success_rates': format_success_calculated,
            'most_popular_format': max(format_counts, key=format_counts.get) if format_counts else None,
            'total_formats_used': len(format_counts)
        }
    
    async def _calculate_duplicate_analysis(self, results: List[Dict]) -> Dict:
        """Calculate duplicate detection statistics"""
        
        files_with_duplicates = 0
        total_duplicates = 0
        duplicate_types = defaultdict(int)
        
        for result in results:
            duplicate_count = result.get('duplicate_count', 0)
            if duplicate_count > 0:
                files_with_duplicates += 1
                total_duplicates += duplicate_count
                
                for duplicate in result.get('duplicates_found', []):
                    duplicate_types[duplicate.get('identifier_type', 'unknown')] += 1
        
        total_files = len(results)
        
        return {
            'files_with_duplicates': files_with_duplicates,
            'total_duplicate_instances': total_duplicates,
            'duplicate_rate': (files_with_duplicates / total_files * 100) if total_files > 0 else 0,
            'duplicate_types_breakdown': dict(duplicate_types),
            'avg_duplicates_per_file': (total_duplicates / files_with_duplicates) if files_with_duplicates > 0 else 0
        }
    
    async def _calculate_error_analysis(self, results: List[Dict]) -> Dict:
        """Calculate error pattern analysis"""
        
        error_fields = defaultdict(int)
        error_severities = defaultdict(int)
        total_errors = 0
        
        for result in results:
            for error in result.get('validation_errors', []):
                field = error.get('field', 'unknown')
                severity = error.get('severity', 'unknown')
                
                error_fields[field] += 1
                error_severities[severity] += 1
                total_errors += 1
        
        return {
            'total_errors': total_errors,
            'top_error_fields': dict(sorted(error_fields.items(), key=lambda x: x[1], reverse=True)[:10]),
            'error_severity_distribution': dict(error_severities),
            'most_common_error_field': max(error_fields, key=error_fields.get) if error_fields else None
        }
    
    async def _calculate_temporal_trends(self, results: List[Dict]) -> Dict:
        """Calculate temporal trends and patterns"""
        
        daily_counts = defaultdict(int)
        hourly_counts = defaultdict(int)
        
        for result in results:
            upload_date = result.get('upload_date')
            if upload_date:
                if isinstance(upload_date, str):
                    upload_date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                
                date_key = upload_date.date().isoformat()
                hour_key = upload_date.hour
                
                daily_counts[date_key] += 1
                hourly_counts[hour_key] += 1
        
        return {
            'daily_upload_pattern': dict(daily_counts),
            'hourly_upload_pattern': dict(hourly_counts),
            'peak_upload_day': max(daily_counts, key=daily_counts.get) if daily_counts else None,
            'peak_upload_hour': max(hourly_counts, key=hourly_counts.get) if hourly_counts else None
        }
    
    async def _calculate_quality_metrics(self, results: List[Dict]) -> Dict:
        """Calculate overall quality metrics"""
        
        if not results:
            return {}
        
        total_files = len(results)
        clean_files = sum(1 for r in results if r.get('validation_status') == 'valid' and r.get('duplicate_count', 0) == 0)
        files_with_warnings = sum(1 for r in results if r.get('validation_status') == 'warning')
        files_with_errors = sum(1 for r in results if r.get('validation_status') == 'error')
        
        # Calculate quality score (0-100)
        quality_score = (clean_files / total_files * 100) if total_files > 0 else 0
        
        return {
            'overall_quality_score': round(quality_score, 2),
            'clean_files_percentage': round((clean_files / total_files * 100), 2) if total_files > 0 else 0,
            'files_needing_attention': files_with_warnings + files_with_errors,
            'quality_grade': self._get_quality_grade(quality_score)
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    async def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        
        recommendations = []
        
        if not results:
            return recommendations
        
        # Analyze common issues and generate recommendations
        total_files = len(results)
        error_rate = sum(1 for r in results if r.get('validation_status') == 'error') / total_files
        duplicate_rate = sum(1 for r in results if r.get('duplicate_count', 0) > 0) / total_files
        
        if error_rate > 0.2:  # More than 20% errors
            recommendations.append("High error rate detected. Consider reviewing metadata requirements and validation rules.")
        
        if duplicate_rate > 0.1:  # More than 10% duplicates
            recommendations.append("Significant duplicate identifiers found. Implement stricter ID management processes.")
        
        # Format-specific recommendations
        format_counts = defaultdict(int)
        for result in results:
            format_counts[result.get('file_format', 'unknown')] += 1
        
        if len(format_counts) > 3:
            recommendations.append("Multiple metadata formats in use. Consider standardizing on fewer formats for consistency.")
        
        # Error pattern recommendations
        error_fields = defaultdict(int)
        for result in results:
            for error in result.get('validation_errors', []):
                error_fields[error.get('field', 'unknown')] += 1
        
        top_error_field = max(error_fields, key=error_fields.get) if error_fields else None
        if top_error_field and error_fields[top_error_field] > total_files * 0.15:
            recommendations.append(f"Frequent validation errors in '{top_error_field}' field. Provide additional guidance or validation for this field.")
        
        if not recommendations:
            recommendations.append("Metadata quality looks good! Continue following current validation practices.")
        
        return recommendations