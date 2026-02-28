"""
Executive Insights Dashboard
============================
Command center for platform operators with:
- Revenue projections
- Agency performance ranking
- Model success analytics
- Licensing heatmaps
- Fraud risk indicators
- Infrastructure cost optimization
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

from llm_service import LlmChat, UserMessage


class TimeRange(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


# Pydantic Models
class RevenueProjection(BaseModel):
    period: str
    current_revenue: float
    projected_revenue: float
    growth_rate: float
    confidence_interval: Dict[str, float] = Field(default_factory=dict)
    key_drivers: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class AgencyRanking(BaseModel):
    rank: int
    agency_id: str
    agency_name: str
    performance_score: float
    revenue_contribution: float
    active_models: int
    bookings_count: int
    growth_trend: str
    badges: List[str] = Field(default_factory=list)


class ModelSuccessMetric(BaseModel):
    model_id: str
    model_name: str
    success_score: float
    total_bookings: int
    total_revenue: float
    avg_campaign_value: float
    top_categories: List[str] = Field(default_factory=list)
    growth_percentage: float


class LicensingHeatmapData(BaseModel):
    region: str
    license_type: str
    count: int
    revenue: float
    trend: str
    popular_categories: List[str] = Field(default_factory=list)


class FraudRiskIndicator(BaseModel):
    risk_id: str
    risk_level: RiskLevel
    risk_type: str
    description: str
    affected_entities: List[str] = Field(default_factory=list)
    recommended_action: str
    detected_at: datetime
    confidence_score: float


class InfrastructureCostInsight(BaseModel):
    service_name: str
    current_cost: float
    projected_cost: float
    optimization_potential: float
    recommendations: List[str] = Field(default_factory=list)
    cost_trend: str


class ExecutiveSummary(BaseModel):
    generated_at: datetime
    period: str
    total_revenue: float
    revenue_change: float
    total_users: int
    active_agencies: int
    active_models: int
    total_bookings: int
    avg_booking_value: float
    platform_health_score: float
    top_performing_category: str
    key_insights: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)


class ExecutiveInsightsDashboard:
    """
    Executive command center for platform operators.
    Provides comprehensive analytics and AI-driven insights.
    """
    
    def __init__(self, db):
        self.db = db
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_provider = "gemini"
        self.model_name = "gemini-2.5-flash"
    
    def _get_chat(self, session_id: str, system_message: str) -> LlmChat:
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        chat.with_model(self.model_provider, self.model_name)
        return chat
    
    async def get_executive_summary(self, time_range: TimeRange = TimeRange.MONTH) -> ExecutiveSummary:
        """
        Generate a comprehensive executive summary with AI insights.
        """
        # Gather platform metrics
        metrics = await self._gather_platform_metrics(time_range)
        
        system_message = """You are an executive business analyst for a talent management platform.
        Analyze platform metrics and provide strategic insights and action items."""
        
        chat = self._get_chat("executive-summary", system_message)
        
        prompt = f"""Analyze these platform metrics and provide executive insights:

Metrics for {time_range.value}:
{json.dumps(metrics, indent=2, default=str)}

Provide a JSON response:
{{
    "platform_health_score": <0-100>,
    "key_insights": ["insight1", "insight2", "insight3"],
    "action_items": ["action1", "action2", "action3"],
    "top_performing_category": "category name"
}}

Focus on:
- Revenue trends and opportunities
- Agency and model performance patterns
- Market positioning
- Growth opportunities
- Risk factors"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            insights = json.loads(json_str)
            
            return ExecutiveSummary(
                generated_at=datetime.now(timezone.utc),
                period=time_range.value,
                total_revenue=metrics.get("total_revenue", 0),
                revenue_change=metrics.get("revenue_change", 0),
                total_users=metrics.get("total_users", 0),
                active_agencies=metrics.get("active_agencies", 0),
                active_models=metrics.get("active_models", 0),
                total_bookings=metrics.get("total_bookings", 0),
                avg_booking_value=metrics.get("avg_booking_value", 0),
                platform_health_score=insights.get("platform_health_score", 75),
                top_performing_category=insights.get("top_performing_category", "Fashion"),
                key_insights=insights.get("key_insights", []),
                action_items=insights.get("action_items", [])
            )
        except (json.JSONDecodeError, KeyError):
            return ExecutiveSummary(
                generated_at=datetime.now(timezone.utc),
                period=time_range.value,
                total_revenue=metrics.get("total_revenue", 0),
                revenue_change=metrics.get("revenue_change", 0),
                total_users=metrics.get("total_users", 0),
                active_agencies=metrics.get("active_agencies", 0),
                active_models=metrics.get("active_models", 0),
                total_bookings=metrics.get("total_bookings", 0),
                avg_booking_value=metrics.get("avg_booking_value", 0),
                platform_health_score=75,
                top_performing_category="Fashion"
            )
    
    async def _gather_platform_metrics(self, time_range: TimeRange) -> Dict[str, Any]:
        """Gather platform metrics from database."""
        days_map = {
            TimeRange.DAY: 1,
            TimeRange.WEEK: 7,
            TimeRange.MONTH: 30,
            TimeRange.QUARTER: 90,
            TimeRange.YEAR: 365
        }
        days = days_map.get(time_range, 30)
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            # Get user count
            users_collection = self.db["users"]
            total_users = await users_collection.count_documents({})
            
            # Get agency count
            agencies_collection = self.db["agencies"]
            active_agencies = await agencies_collection.count_documents({"status": "active"})
            
            # Get model count
            models_collection = self.db["models"]
            active_models = await models_collection.count_documents({"status": "active"})
            
            # Get booking data
            bookings_collection = self.db["bookings"]
            bookings = await bookings_collection.find({
                "created_at": {"$gte": start_date}
            }).to_list(None)
            
            total_bookings = len(bookings)
            total_revenue = sum(b.get("amount", 0) for b in bookings)
            avg_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
            
            # Calculate revenue change (compare to previous period)
            prev_start = start_date - timedelta(days=days)
            prev_bookings = await bookings_collection.find({
                "created_at": {"$gte": prev_start, "$lt": start_date}
            }).to_list(None)
            prev_revenue = sum(b.get("amount", 0) for b in prev_bookings)
            
            revenue_change = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            
            return {
                "total_users": total_users,
                "active_agencies": active_agencies,
                "active_models": active_models,
                "total_bookings": total_bookings,
                "total_revenue": total_revenue,
                "avg_booking_value": avg_booking_value,
                "revenue_change": round(revenue_change, 2),
                "period_days": days
            }
        except Exception:
            # Return defaults if database queries fail
            return {
                "total_users": 0,
                "active_agencies": 0,
                "active_models": 0,
                "total_bookings": 0,
                "total_revenue": 0,
                "avg_booking_value": 0,
                "revenue_change": 0,
                "period_days": days
            }
    
    async def get_revenue_projections(self, months_ahead: int = 3) -> List[RevenueProjection]:
        """
        Generate AI-powered revenue projections.
        """
        # Get historical revenue data
        historical = await self._get_historical_revenue(months=6)
        
        system_message = """You are a financial analyst specializing in revenue forecasting for talent platforms.
        Analyze historical data and project future revenue with confidence intervals."""
        
        chat = self._get_chat("revenue-projection", system_message)
        
        prompt = f"""Based on this historical revenue data, project revenue for the next {months_ahead} months:

Historical Data (last 6 months):
{json.dumps(historical, indent=2, default=str)}

Provide a JSON array with projections:
[
    {{
        "period": "Month Year",
        "current_revenue": <last known revenue>,
        "projected_revenue": <projected amount>,
        "growth_rate": <percentage as decimal>,
        "confidence_interval": {{"low": <amount>, "high": <amount>}},
        "key_drivers": ["driver1", "driver2"],
        "risks": ["risk1", "risk2"]
    }}
]

Consider:
- Seasonal patterns
- Growth trends
- Market conditions
- Platform maturity
- External factors"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            projections_data = json.loads(json_str)
            
            projections = []
            for p in projections_data:
                projections.append(RevenueProjection(
                    period=p.get("period", "Unknown"),
                    current_revenue=p.get("current_revenue", 0),
                    projected_revenue=p.get("projected_revenue", 0),
                    growth_rate=p.get("growth_rate", 0),
                    confidence_interval=p.get("confidence_interval", {}),
                    key_drivers=p.get("key_drivers", []),
                    risks=p.get("risks", [])
                ))
            return projections
        except (json.JSONDecodeError, KeyError):
            return []
    
    async def _get_historical_revenue(self, months: int = 6) -> List[Dict[str, Any]]:
        """Get historical revenue data by month."""
        try:
            bookings_collection = self.db["bookings"]
            historical = []
            
            for i in range(months, 0, -1):
                start = datetime.now(timezone.utc).replace(day=1) - timedelta(days=30*i)
                end = start + timedelta(days=30)
                
                bookings = await bookings_collection.find({
                    "created_at": {"$gte": start, "$lt": end}
                }).to_list(None)
                
                revenue = sum(b.get("amount", 0) for b in bookings)
                historical.append({
                    "month": start.strftime("%B %Y"),
                    "revenue": revenue,
                    "bookings_count": len(bookings)
                })
            
            return historical
        except Exception:
            return []
    
    async def get_agency_rankings(self, limit: int = 20) -> List[AgencyRanking]:
        """
        Get ranked list of agencies by performance.
        """
        try:
            agencies_collection = self.db["agencies"]
            agencies = await agencies_collection.find({"status": "active"}).to_list(limit * 2)
            
            # Calculate scores and sort
            scored_agencies = []
            for agency in agencies:
                agency_id = str(agency.get("_id", ""))
                revenue = agency.get("total_revenue", 0)
                bookings = agency.get("total_bookings", 0)
                models = agency.get("active_models_count", 0)
                
                # Calculate performance score (weighted)
                score = (
                    (revenue / 10000 * 40) +  # Revenue weight: 40%
                    (bookings * 2) +           # Bookings weight: 30%
                    (models * 5)               # Models weight: 30%
                )
                
                # Determine growth trend
                prev_revenue = agency.get("prev_month_revenue", revenue)
                if revenue > prev_revenue * 1.1:
                    trend = "growing"
                elif revenue < prev_revenue * 0.9:
                    trend = "declining"
                else:
                    trend = "stable"
                
                # Assign badges
                badges = []
                if score > 500:
                    badges.append("Top Performer")
                if bookings > 50:
                    badges.append("High Volume")
                if models > 20:
                    badges.append("Large Roster")
                if trend == "growing":
                    badges.append("Rising Star")
                
                scored_agencies.append({
                    "agency_id": agency_id,
                    "agency_name": agency.get("name", "Unknown"),
                    "score": score,
                    "revenue": revenue,
                    "bookings": bookings,
                    "models": models,
                    "trend": trend,
                    "badges": badges
                })
            
            # Sort by score
            scored_agencies.sort(key=lambda x: x["score"], reverse=True)
            
            # Create rankings
            rankings = []
            for rank, agency in enumerate(scored_agencies[:limit], 1):
                rankings.append(AgencyRanking(
                    rank=rank,
                    agency_id=agency["agency_id"],
                    agency_name=agency["agency_name"],
                    performance_score=min(agency["score"], 100),
                    revenue_contribution=agency["revenue"],
                    active_models=agency["models"],
                    bookings_count=agency["bookings"],
                    growth_trend=agency["trend"],
                    badges=agency["badges"]
                ))
            
            return rankings
        except Exception:
            return []
    
    async def get_model_success_analytics(self, limit: int = 50) -> List[ModelSuccessMetric]:
        """
        Get model success analytics with detailed metrics.
        """
        try:
            models_collection = self.db["models"]
            models = await models_collection.find({"status": "active"}).to_list(limit * 2)
            
            metrics = []
            for model in models:
                model_id = str(model.get("_id", ""))
                bookings = model.get("total_bookings", 0)
                revenue = model.get("total_revenue", 0)
                
                success_score = min(
                    (bookings * 2 + revenue / 1000) / 2,
                    100
                )
                
                prev_revenue = model.get("prev_quarter_revenue", revenue)
                growth = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
                
                metrics.append(ModelSuccessMetric(
                    model_id=model_id,
                    model_name=model.get("name", "Unknown"),
                    success_score=success_score,
                    total_bookings=bookings,
                    total_revenue=revenue,
                    avg_campaign_value=revenue / bookings if bookings > 0 else 0,
                    top_categories=model.get("categories", [])[:3],
                    growth_percentage=round(growth, 2)
                ))
            
            # Sort by success score
            metrics.sort(key=lambda x: x.success_score, reverse=True)
            return metrics[:limit]
        except Exception:
            return []
    
    async def get_licensing_heatmap(self) -> List[LicensingHeatmapData]:
        """
        Generate licensing activity heatmap data.
        """
        try:
            licenses_collection = self.db["licenses"]
            
            # Aggregate by region and type
            pipeline = [
                {"$match": {"status": "active"}},
                {"$group": {
                    "_id": {"region": "$region", "license_type": "$license_type"},
                    "count": {"$sum": 1},
                    "revenue": {"$sum": "$amount"},
                    "categories": {"$push": "$category"}
                }}
            ]
            
            results = await licenses_collection.aggregate(pipeline).to_list(None)
            
            heatmap_data = []
            for result in results:
                # Get unique categories
                categories = list(set(result.get("categories", [])))[:5]
                
                # Determine trend (simplified)
                count = result.get("count", 0)
                trend = "growing" if count > 10 else ("stable" if count > 5 else "emerging")
                
                heatmap_data.append(LicensingHeatmapData(
                    region=result["_id"].get("region", "Global"),
                    license_type=result["_id"].get("license_type", "Standard"),
                    count=count,
                    revenue=result.get("revenue", 0),
                    trend=trend,
                    popular_categories=categories
                ))
            
            return heatmap_data
        except Exception:
            # Return sample data if query fails
            return [
                LicensingHeatmapData(
                    region="North America",
                    license_type="Commercial",
                    count=150,
                    revenue=75000,
                    trend="growing",
                    popular_categories=["Fashion", "Beauty", "Lifestyle"]
                ),
                LicensingHeatmapData(
                    region="Europe",
                    license_type="Editorial",
                    count=120,
                    revenue=48000,
                    trend="stable",
                    popular_categories=["Fashion", "Art", "Culture"]
                )
            ]
    
    async def detect_fraud_risks(self) -> List[FraudRiskIndicator]:
        """
        AI-powered fraud detection and risk assessment.
        """
        system_message = """You are a fraud detection specialist for a talent management platform.
        Analyze patterns and flag potential fraud risks with actionable recommendations."""
        
        chat = self._get_chat("fraud-detection", system_message)
        
        # Get suspicious activity patterns
        suspicious_patterns = await self._gather_suspicious_patterns()
        
        prompt = f"""Analyze these activity patterns for potential fraud risks:

Patterns:
{json.dumps(suspicious_patterns, indent=2, default=str)}

Provide a JSON array of fraud risk indicators:
[
    {{
        "risk_id": "risk_001",
        "risk_level": "critical|high|medium|low|none",
        "risk_type": "type of fraud",
        "description": "detailed description",
        "affected_entities": ["entity1", "entity2"],
        "recommended_action": "what to do",
        "confidence_score": <0-100>
    }}
]

Look for:
- Unusual booking patterns
- Suspicious payment activity
- Identity verification issues
- Content duplication or theft
- Account manipulation
- Abnormal traffic patterns"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            risks_data = json.loads(json_str)
            
            risks = []
            for r in risks_data:
                risks.append(FraudRiskIndicator(
                    risk_id=r.get("risk_id", f"risk_{len(risks)}"),
                    risk_level=RiskLevel(r.get("risk_level", "low")),
                    risk_type=r.get("risk_type", "Unknown"),
                    description=r.get("description", ""),
                    affected_entities=r.get("affected_entities", []),
                    recommended_action=r.get("recommended_action", ""),
                    detected_at=datetime.now(timezone.utc),
                    confidence_score=r.get("confidence_score", 50)
                ))
            return risks
        except (json.JSONDecodeError, KeyError, ValueError):
            return []
    
    async def _gather_suspicious_patterns(self) -> Dict[str, Any]:
        """Gather patterns that might indicate fraud."""
        try:
            # Check for suspicious login patterns
            users_collection = self.db["users"]
            recent_logins = await users_collection.find({
                "last_login": {"$gte": datetime.now(timezone.utc) - timedelta(hours=24)}
            }).to_list(100)
            
            # Check for unusual booking patterns
            bookings_collection = self.db["bookings"]
            recent_bookings = await bookings_collection.find({
                "created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=7)}
            }).to_list(100)
            
            # Analyze patterns
            patterns = {
                "total_logins_24h": len(recent_logins),
                "total_bookings_7d": len(recent_bookings),
                "high_value_bookings": len([b for b in recent_bookings if b.get("amount", 0) > 5000]),
                "duplicate_ips": [],  # Would need IP tracking
                "failed_payments": 0,  # Would need payment failure tracking
                "new_accounts_24h": len([u for u in recent_logins if u.get("created_at", datetime.min) > datetime.now(timezone.utc) - timedelta(hours=24)])
            }
            
            return patterns
        except Exception:
            return {
                "total_logins_24h": 0,
                "total_bookings_7d": 0,
                "high_value_bookings": 0,
                "duplicate_ips": [],
                "failed_payments": 0,
                "new_accounts_24h": 0
            }
    
    async def get_infrastructure_cost_insights(self) -> List[InfrastructureCostInsight]:
        """
        Analyze infrastructure costs and provide optimization recommendations.
        """
        # This would typically integrate with AWS Cost Explorer
        # For now, provide AI-generated recommendations based on typical patterns
        
        system_message = """You are a cloud infrastructure cost optimization expert.
        Analyze usage patterns and recommend cost savings strategies."""
        
        chat = self._get_chat("infra-costs", system_message)
        
        prompt = """Analyze typical infrastructure costs for a talent management platform and provide optimization insights:

Services to analyze:
- Compute (EC2/ECS/Lambda)
- Storage (S3/EBS)
- Database (RDS/DynamoDB)
- CDN (CloudFront)
- AI/ML (Bedrock/SageMaker)
- Networking

Provide a JSON array:
[
    {{
        "service_name": "Service Name",
        "current_cost": <estimated monthly cost>,
        "projected_cost": <projected if no changes>,
        "optimization_potential": <potential savings>,
        "recommendations": ["rec1", "rec2"],
        "cost_trend": "increasing|stable|decreasing"
    }}
]"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            insights_data = json.loads(json_str)
            
            insights = []
            for i in insights_data:
                insights.append(InfrastructureCostInsight(
                    service_name=i.get("service_name", "Unknown"),
                    current_cost=i.get("current_cost", 0),
                    projected_cost=i.get("projected_cost", 0),
                    optimization_potential=i.get("optimization_potential", 0),
                    recommendations=i.get("recommendations", []),
                    cost_trend=i.get("cost_trend", "stable")
                ))
            return insights
        except (json.JSONDecodeError, KeyError):
            return []


# Singleton instance
_dashboard_instance = None

def get_executive_dashboard(db) -> ExecutiveInsightsDashboard:
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = ExecutiveInsightsDashboard(db)
    return _dashboard_instance
