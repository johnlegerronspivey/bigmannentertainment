"""
Unified Talent Intelligence Engine
===================================
Central AI system that continuously learns from:
- Portfolio performance
- Licensing activity
- Market trends
- Agency behavior
- Model availability
- Regional demand

Features:
- Predicts which models will book the most campaigns
- Suggests optimal licensing tiers for each asset
- Recommends pricing adjustments
- Flags underperforming assets and suggests improvements
- Auto-tags images with commercial value scores
"""

import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# Gemini Integration
from llm_service import LlmChat, UserMessage


class TalentScoreCategory(str, Enum):
    COMMERCIAL_VALUE = "commercial_value"
    MARKET_DEMAND = "market_demand"
    BOOKING_POTENTIAL = "booking_potential"
    BRAND_FIT = "brand_fit"
    REGIONAL_APPEAL = "regional_appeal"


class AssetPerformanceLevel(str, Enum):
    EXCEPTIONAL = "exceptional"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    UNDERPERFORMING = "underperforming"


class LicensingTier(str, Enum):
    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"
    PROMOTIONAL = "promotional"


# Pydantic Models
class TalentScore(BaseModel):
    model_id: str
    overall_score: float = Field(ge=0, le=100)
    commercial_value: float = Field(ge=0, le=100)
    market_demand: float = Field(ge=0, le=100)
    booking_potential: float = Field(ge=0, le=100)
    brand_fit_score: float = Field(ge=0, le=100)
    regional_scores: Dict[str, float] = Field(default_factory=dict)
    trending_categories: List[str] = Field(default_factory=list)
    predicted_bookings_30d: int = 0
    recommended_rate_adjustment: float = 0.0
    analysis_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssetAnalysis(BaseModel):
    asset_id: str
    commercial_value_score: float = Field(ge=0, le=100)
    performance_level: AssetPerformanceLevel
    recommended_tier: LicensingTier
    suggested_price_range: Dict[str, float]
    auto_tags: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    market_fit_analysis: str = ""
    predicted_revenue_30d: float = 0.0


class MarketTrend(BaseModel):
    trend_id: str
    category: str
    trend_name: str
    growth_rate: float
    relevance_score: float = Field(ge=0, le=100)
    affected_regions: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    valid_until: datetime


class AgencyPerformanceInsight(BaseModel):
    agency_id: str
    agency_name: str
    performance_score: float = Field(ge=0, le=100)
    active_models: int
    total_bookings_30d: int
    revenue_30d: float
    growth_trend: str
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    ai_recommendations: List[str] = Field(default_factory=list)


class PricingRecommendation(BaseModel):
    asset_id: str
    current_price: float
    recommended_price: float
    price_change_percent: float
    reasoning: str
    confidence_score: float = Field(ge=0, le=100)
    market_factors: List[str] = Field(default_factory=list)


class TalentIntelligenceEngine:
    """
    The central AI brain for talent and asset intelligence.
    Uses Google Gemini for advanced analysis and predictions.
    """
    
    def __init__(self, db):
        self.db = db
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_provider = "gemini"
        self.model_name = "gemini-2.5-flash"
        
    def _get_chat(self, session_id: str, system_message: str) -> LlmChat:
        """Create a configured LlmChat instance for Gemini."""
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        chat.with_model(self.model_provider, self.model_name)
        return chat
    
    async def analyze_talent_score(self, model_id: str, model_data: Dict[str, Any]) -> TalentScore:
        """
        Analyze a model's potential and generate comprehensive talent scores.
        """
        system_message = """You are an expert talent intelligence analyst for a premier modeling agency platform.
        Analyze model data and provide detailed scoring across multiple dimensions.
        Always respond with valid JSON matching the required schema."""
        
        chat = self._get_chat(f"talent-score-{model_id}", system_message)
        
        prompt = f"""Analyze this model's data and provide talent scores:

Model Data:
{json.dumps(model_data, indent=2, default=str)}

Provide a JSON response with these exact fields:
{{
    "overall_score": <0-100>,
    "commercial_value": <0-100>,
    "market_demand": <0-100>,
    "booking_potential": <0-100>,
    "brand_fit_score": <0-100>,
    "regional_scores": {{"north_america": <score>, "europe": <score>, "asia": <score>, "global": <score>}},
    "trending_categories": ["category1", "category2"],
    "predicted_bookings_30d": <integer>,
    "recommended_rate_adjustment": <percentage as decimal, e.g., 0.15 for 15%>
}}

Consider:
- Past booking history and performance
- Current market trends in modeling industry
- Regional demand patterns
- Social media presence and engagement
- Portfolio quality and diversity
- Brand collaboration history"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            # Parse JSON from response
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            scores = json.loads(json_str)
            
            return TalentScore(
                model_id=model_id,
                overall_score=scores.get("overall_score", 50),
                commercial_value=scores.get("commercial_value", 50),
                market_demand=scores.get("market_demand", 50),
                booking_potential=scores.get("booking_potential", 50),
                brand_fit_score=scores.get("brand_fit_score", 50),
                regional_scores=scores.get("regional_scores", {}),
                trending_categories=scores.get("trending_categories", []),
                predicted_bookings_30d=scores.get("predicted_bookings_30d", 0),
                recommended_rate_adjustment=scores.get("recommended_rate_adjustment", 0.0)
            )
        except (json.JSONDecodeError, KeyError):
            # Return default scores if parsing fails
            return TalentScore(
                model_id=model_id,
                overall_score=50,
                commercial_value=50,
                market_demand=50,
                booking_potential=50,
                brand_fit_score=50
            )
    
    async def analyze_asset_commercial_value(self, asset_id: str, asset_data: Dict[str, Any]) -> AssetAnalysis:
        """
        Analyze an asset's commercial value and provide recommendations.
        Auto-tags images with commercial value scores.
        """
        system_message = """You are an expert commercial asset analyst for a modeling/media platform.
        Analyze assets for commercial potential, suggest pricing tiers, and provide improvement recommendations.
        Always respond with valid JSON."""
        
        chat = self._get_chat(f"asset-analysis-{asset_id}", system_message)
        
        prompt = f"""Analyze this asset for commercial value:

Asset Data:
{json.dumps(asset_data, indent=2, default=str)}

Provide a JSON response with:
{{
    "commercial_value_score": <0-100>,
    "performance_level": "exceptional|high|moderate|low|underperforming",
    "recommended_tier": "premium|standard|basic|promotional",
    "suggested_price_range": {{"min": <float>, "max": <float>, "optimal": <float>}},
    "auto_tags": ["tag1", "tag2", "tag3"],
    "improvement_suggestions": ["suggestion1", "suggestion2"],
    "market_fit_analysis": "detailed analysis string",
    "predicted_revenue_30d": <float>
}}

Consider:
- Image/video quality and composition
- Commercial appeal and versatility
- Current market demand for similar content
- Historical performance of similar assets
- Seasonal trends and timing"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            analysis = json.loads(json_str)
            
            return AssetAnalysis(
                asset_id=asset_id,
                commercial_value_score=analysis.get("commercial_value_score", 50),
                performance_level=AssetPerformanceLevel(analysis.get("performance_level", "moderate")),
                recommended_tier=LicensingTier(analysis.get("recommended_tier", "standard")),
                suggested_price_range=analysis.get("suggested_price_range", {"min": 100, "max": 500, "optimal": 250}),
                auto_tags=analysis.get("auto_tags", []),
                improvement_suggestions=analysis.get("improvement_suggestions", []),
                market_fit_analysis=analysis.get("market_fit_analysis", ""),
                predicted_revenue_30d=analysis.get("predicted_revenue_30d", 0)
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return AssetAnalysis(
                asset_id=asset_id,
                commercial_value_score=50,
                performance_level=AssetPerformanceLevel.MODERATE,
                recommended_tier=LicensingTier.STANDARD,
                suggested_price_range={"min": 100, "max": 500, "optimal": 250}
            )
    
    async def predict_market_trends(self, category: str = "modeling") -> List[MarketTrend]:
        """
        Predict upcoming market trends based on industry data.
        """
        system_message = """You are a market intelligence expert for the modeling and entertainment industry.
        Analyze current data and predict upcoming trends. Provide actionable insights."""
        
        chat = self._get_chat(f"market-trends-{category}", system_message)
        
        prompt = f"""Analyze current market conditions for the {category} industry and predict 5 key trends.

Provide a JSON array response:
[
    {{
        "trend_id": "trend_1",
        "category": "{category}",
        "trend_name": "Trend Name",
        "growth_rate": <percentage as decimal>,
        "relevance_score": <0-100>,
        "affected_regions": ["region1", "region2"],
        "recommended_actions": ["action1", "action2"],
        "valid_days": <number of days this trend is expected to be relevant>
    }}
]

Consider:
- Social media influence on modeling
- Sustainability and ethical fashion trends
- Digital/virtual modeling growth
- Regional market variations
- Brand collaboration patterns
- Technology impact (AI, AR, metaverse)"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            trends_data = json.loads(json_str)
            
            trends = []
            for t in trends_data:
                valid_days = t.get("valid_days", 30)
                trends.append(MarketTrend(
                    trend_id=t.get("trend_id", f"trend_{len(trends)}"),
                    category=t.get("category", category),
                    trend_name=t.get("trend_name", "Unknown Trend"),
                    growth_rate=t.get("growth_rate", 0.0),
                    relevance_score=t.get("relevance_score", 50),
                    affected_regions=t.get("affected_regions", []),
                    recommended_actions=t.get("recommended_actions", []),
                    valid_until=datetime.now(timezone.utc) + timedelta(days=valid_days)
                ))
            return trends
        except (json.JSONDecodeError, KeyError):
            return []
    
    async def analyze_agency_performance(self, agency_id: str, agency_data: Dict[str, Any]) -> AgencyPerformanceInsight:
        """
        Analyze agency performance and provide AI-driven recommendations.
        """
        system_message = """You are an agency performance analyst for a talent management platform.
        Analyze agency metrics and provide actionable insights for improvement."""
        
        chat = self._get_chat(f"agency-perf-{agency_id}", system_message)
        
        prompt = f"""Analyze this agency's performance data:

Agency Data:
{json.dumps(agency_data, indent=2, default=str)}

Provide a JSON response:
{{
    "performance_score": <0-100>,
    "growth_trend": "growing|stable|declining",
    "strengths": ["strength1", "strength2"],
    "areas_for_improvement": ["area1", "area2"],
    "ai_recommendations": ["recommendation1", "recommendation2", "recommendation3"]
}}

Consider:
- Booking conversion rates
- Model roster quality and diversity
- Revenue trends
- Client satisfaction indicators
- Market positioning
- Operational efficiency"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            insight = json.loads(json_str)
            
            return AgencyPerformanceInsight(
                agency_id=agency_id,
                agency_name=agency_data.get("name", "Unknown Agency"),
                performance_score=insight.get("performance_score", 50),
                active_models=agency_data.get("active_models", 0),
                total_bookings_30d=agency_data.get("bookings_30d", 0),
                revenue_30d=agency_data.get("revenue_30d", 0.0),
                growth_trend=insight.get("growth_trend", "stable"),
                strengths=insight.get("strengths", []),
                areas_for_improvement=insight.get("areas_for_improvement", []),
                ai_recommendations=insight.get("ai_recommendations", [])
            )
        except (json.JSONDecodeError, KeyError):
            return AgencyPerformanceInsight(
                agency_id=agency_id,
                agency_name=agency_data.get("name", "Unknown Agency"),
                performance_score=50,
                active_models=agency_data.get("active_models", 0),
                total_bookings_30d=agency_data.get("bookings_30d", 0),
                revenue_30d=agency_data.get("revenue_30d", 0.0),
                growth_trend="stable"
            )
    
    async def get_pricing_recommendations(self, assets: List[Dict[str, Any]]) -> List[PricingRecommendation]:
        """
        Generate dynamic pricing recommendations for multiple assets.
        """
        system_message = """You are a pricing optimization expert for a media licensing platform.
        Analyze assets and market conditions to recommend optimal pricing."""
        
        chat = self._get_chat("pricing-recommendations", system_message)
        
        prompt = f"""Analyze these assets and provide pricing recommendations:

Assets:
{json.dumps(assets, indent=2, default=str)}

Provide a JSON array response:
[
    {{
        "asset_id": "asset_id",
        "current_price": <current price>,
        "recommended_price": <recommended price>,
        "price_change_percent": <percentage change as decimal>,
        "reasoning": "explanation",
        "confidence_score": <0-100>,
        "market_factors": ["factor1", "factor2"]
    }}
]

Consider:
- Current market demand
- Asset quality and uniqueness
- Historical performance
- Competitor pricing
- Seasonal factors
- Usage rights complexity"""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        try:
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            recommendations_data = json.loads(json_str)
            
            recommendations = []
            for r in recommendations_data:
                recommendations.append(PricingRecommendation(
                    asset_id=r.get("asset_id", ""),
                    current_price=r.get("current_price", 0),
                    recommended_price=r.get("recommended_price", 0),
                    price_change_percent=r.get("price_change_percent", 0),
                    reasoning=r.get("reasoning", ""),
                    confidence_score=r.get("confidence_score", 50),
                    market_factors=r.get("market_factors", [])
                ))
            return recommendations
        except (json.JSONDecodeError, KeyError):
            return []
    
    async def flag_underperforming_assets(self, min_performance_threshold: float = 30.0) -> List[Dict[str, Any]]:
        """
        Identify underperforming assets and suggest improvements.
        """
        # Fetch assets from database
        assets_collection = self.db["assets"]
        
        # Get assets with low performance metrics
        underperforming = await assets_collection.find({
            "$or": [
                {"performance_score": {"$lt": min_performance_threshold}},
                {"views_30d": {"$lt": 10}},
                {"revenue_30d": {"$eq": 0}}
            ]
        }).to_list(100)
        
        flagged_assets = []
        for asset in underperforming:
            asset_id = str(asset.get("_id", ""))
            analysis = await self.analyze_asset_commercial_value(asset_id, asset)
            
            flagged_assets.append({
                "asset_id": asset_id,
                "current_performance": asset.get("performance_score", 0),
                "analysis": analysis.dict(),
                "flagged_at": datetime.now(timezone.utc).isoformat()
            })
        
        return flagged_assets
    
    async def batch_auto_tag_assets(self, asset_ids: List[str]) -> Dict[str, List[str]]:
        """
        Auto-tag multiple assets with commercial value tags.
        """
        assets_collection = self.db["assets"]
        results = {}
        
        for asset_id in asset_ids:
            try:
                from bson import ObjectId
                asset = await assets_collection.find_one({"_id": ObjectId(asset_id)})
                if asset:
                    analysis = await self.analyze_asset_commercial_value(asset_id, asset)
                    results[asset_id] = analysis.auto_tags
                    
                    # Update asset with new tags
                    await assets_collection.update_one(
                        {"_id": ObjectId(asset_id)},
                        {
                            "$set": {
                                "ai_tags": analysis.auto_tags,
                                "commercial_value_score": analysis.commercial_value_score,
                                "ai_analyzed_at": datetime.now(timezone.utc)
                            }
                        }
                    )
            except Exception:
                results[asset_id] = []
        
        return results
    
    async def get_model_booking_predictions(self, model_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Predict booking likelihood for multiple models.
        """
        models_collection = self.db["models"]
        predictions = {}
        
        for model_id in model_ids:
            try:
                from bson import ObjectId
                model = await models_collection.find_one({"_id": ObjectId(model_id)})
                if model:
                    score = await self.analyze_talent_score(model_id, model)
                    predictions[model_id] = {
                        "predicted_bookings_30d": score.predicted_bookings_30d,
                        "booking_potential": score.booking_potential,
                        "trending_categories": score.trending_categories,
                        "recommended_rate_adjustment": score.recommended_rate_adjustment
                    }
            except Exception:
                predictions[model_id] = {"error": "Analysis failed"}
        
        return predictions


# Singleton instance
_talent_engine_instance = None

def get_talent_intelligence_engine(db) -> TalentIntelligenceEngine:
    global _talent_engine_instance
    if _talent_engine_instance is None:
        _talent_engine_instance = TalentIntelligenceEngine(db)
    return _talent_engine_instance
