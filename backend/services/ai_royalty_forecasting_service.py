"""
AI-Powered Royalty Forecasting Service
Big Mann Entertainment Platform - Premium Enhancement

This service provides advanced AI-powered royalty forecasting using machine learning models
to predict future earnings, optimize platform strategies, and support investor decisions.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForecastPeriod(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class ForecastModel(str, Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"

class ScenarioType(str, Enum):
    PLATFORM_EXPANSION = "platform_expansion"
    CONTRIBUTOR_GROWTH = "contributor_growth"
    ENGAGEMENT_BOOST = "engagement_boost"
    GEOGRAPHIC_EXPANSION = "geographic_expansion"
    PRICING_OPTIMIZATION = "pricing_optimization"

class RoyaltyForecastRequest(BaseModel):
    asset_id: Optional[str] = None
    period: ForecastPeriod = ForecastPeriod.MONTHLY
    horizon_months: int = Field(default=12, ge=1, le=36)
    model_type: ForecastModel = ForecastModel.ENSEMBLE
    include_scenarios: bool = True
    confidence_intervals: bool = True

class ScenarioParameters(BaseModel):
    scenario_type: ScenarioType
    parameter_changes: Dict[str, float]  # e.g., {"engagement_rate": 0.15, "platform_count": 3}
    description: str

class ForecastResult(BaseModel):
    asset_id: Optional[str]
    period: ForecastPeriod
    forecast_data: List[Dict[str, Any]]
    total_predicted_revenue: float
    confidence_score: float
    model_accuracy: float
    key_insights: List[str]
    scenarios: Optional[List[Dict[str, Any]]] = None

class AIRoyaltyForecastingService:
    """Advanced AI-powered royalty forecasting service"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_cache = {}
        self.historical_data_cache = {}
        
        # Initialize models
        self._initialize_models()
        
        # Generate sample historical data for demo
        self._generate_sample_data()
    
    def _initialize_models(self):
        """Initialize ML models"""
        self.models = {
            ForecastModel.LINEAR_REGRESSION: LinearRegression(),
            ForecastModel.RANDOM_FOREST: RandomForestRegressor(
                n_estimators=100, 
                random_state=42,
                max_depth=10,
                min_samples_split=5
            ),
            ForecastModel.GRADIENT_BOOSTING: GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        }
        
        self.scalers = {
            model_type: StandardScaler() for model_type in self.models.keys()
        }
    
    def _generate_sample_data(self):
        """Generate realistic sample historical data for training"""
        np.random.seed(42)
        
        # Generate 24 months of historical data
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=730),
            end=datetime.now(),
            freq='D'
        )
        
        sample_assets = [
            "asset_001", "asset_002", "asset_003", "asset_004", "asset_005"
        ]
        
        platforms = ["spotify", "apple_music", "youtube", "tiktok", "instagram", "facebook"]
        territories = ["US", "UK", "CA", "AU", "DE", "FR", "JP"]
        
        data = []
        
        for asset_id in sample_assets:
            base_popularity = np.random.uniform(0.3, 0.9)
            trend_coefficient = np.random.uniform(-0.1, 0.2)
            
            for i, date in enumerate(dates):
                # Simulate seasonal trends
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * i / 365.25)
                
                # Simulate weekly patterns (weekends higher)
                weekly_factor = 1.2 if date.weekday() >= 5 else 1.0
                
                # Simulate trend over time
                trend_factor = 1 + trend_coefficient * (i / len(dates))
                
                for platform in platforms:
                    platform_factor = np.random.uniform(0.5, 2.0)
                    
                    for territory in territories:
                        territory_factor = np.random.uniform(0.3, 1.5)
                        
                        # Calculate engagement metrics
                        base_engagement = base_popularity * seasonal_factor * weekly_factor * trend_factor
                        engagement_rate = max(0, base_engagement * platform_factor * territory_factor * np.random.normal(1, 0.2))
                        
                        streams = int(engagement_rate * np.random.uniform(1000, 50000))
                        cpm = np.random.uniform(0.5, 5.0)  # Cost per mille
                        royalty_rate = np.random.uniform(0.003, 0.01)  # Royalty per stream
                        
                        daily_revenue = streams * royalty_rate * (1 + np.random.normal(0, 0.1))
                        
                        data.append({
                            'date': date,
                            'asset_id': asset_id,
                            'platform': platform,
                            'territory': territory,
                            'streams': streams,
                            'engagement_rate': engagement_rate,
                            'cpm': cpm,
                            'royalty_rate': royalty_rate,
                            'daily_revenue': max(0, daily_revenue),
                            'day_of_week': date.weekday(),
                            'month': date.month,
                            'quarter': (date.month - 1) // 3 + 1,
                            'is_weekend': 1 if date.weekday() >= 5 else 0,
                            'days_since_release': i
                        })
        
        self.historical_data = pd.DataFrame(data)
        logger.info(f"Generated {len(self.historical_data)} rows of sample historical data")
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        features = data.copy()
        
        # Encode categorical variables
        if 'platform' in features.columns:
            if 'platform' not in self.encoders:
                self.encoders['platform'] = LabelEncoder()
                features['platform_encoded'] = self.encoders['platform'].fit_transform(features['platform'])
            else:
                try:
                    features['platform_encoded'] = self.encoders['platform'].transform(features['platform'])
                except ValueError:
                    # Handle unseen categories
                    features['platform_encoded'] = 0
        else:
            features['platform_encoded'] = 0
        
        if 'territory' in features.columns:
            if 'territory' not in self.encoders:
                self.encoders['territory'] = LabelEncoder()
                features['territory_encoded'] = self.encoders['territory'].fit_transform(features['territory'])
            else:
                try:
                    features['territory_encoded'] = self.encoders['territory'].transform(features['territory'])
                except ValueError:
                    # Handle unseen categories
                    features['territory_encoded'] = 0
        else:
            features['territory_encoded'] = 0
        
        # Create rolling averages only if we have enough data
        if len(features) > 7:
            features = features.sort_values(['asset_id', 'platform', 'territory', 'date'])
            features['revenue_7d_avg'] = features.groupby(['asset_id', 'platform', 'territory'])['daily_revenue'].rolling(7, min_periods=1).mean().reset_index(0, drop=True)
            features['revenue_30d_avg'] = features.groupby(['asset_id', 'platform', 'territory'])['daily_revenue'].rolling(30, min_periods=1).mean().reset_index(0, drop=True)
            
            # Create lag features
            features['revenue_lag_1'] = features.groupby(['asset_id', 'platform', 'territory'])['daily_revenue'].shift(1)
            features['revenue_lag_7'] = features.groupby(['asset_id', 'platform', 'territory'])['daily_revenue'].shift(7)
        else:
            # Use simple averages for small datasets
            features['revenue_7d_avg'] = features['daily_revenue']
            features['revenue_30d_avg'] = features['daily_revenue']
            features['revenue_lag_1'] = features['daily_revenue']
            features['revenue_lag_7'] = features['daily_revenue']
        
        # Fill NaN values
        features = features.fillna(0)
        
        return features
    
    def _train_models(self, asset_id: Optional[str] = None):
        """Train ML models on historical data"""
        try:
            # Filter data if specific asset requested
            if asset_id:
                train_data = self.historical_data[self.historical_data['asset_id'] == asset_id]
                if train_data.empty:
                    logger.warning(f"No data found for asset {asset_id}, using all data")
                    train_data = self.historical_data
            else:
                train_data = self.historical_data
            
            # Prepare features
            features_df = self._prepare_features(train_data)
            
            # Select feature columns
            feature_columns = [
                'platform_encoded', 'territory_encoded', 'day_of_week', 'month', 
                'quarter', 'is_weekend', 'days_since_release', 'streams',
                'engagement_rate', 'cpm', 'royalty_rate', 'revenue_7d_avg',
                'revenue_30d_avg', 'revenue_lag_1', 'revenue_lag_7'
            ]
            
            X = features_df[feature_columns]
            y = features_df['daily_revenue']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            model_performance = {}
            
            # Train each model
            for model_type, model in self.models.items():
                try:
                    # Scale features
                    X_train_scaled = self.scalers[model_type].fit_transform(X_train)
                    X_test_scaled = self.scalers[model_type].transform(X_test)
                    
                    # Train model
                    model.fit(X_train_scaled, y_train)
                    
                    # Evaluate
                    y_pred = model.predict(X_test_scaled)
                    mae = mean_absolute_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    model_performance[model_type] = {
                        'mae': mae,
                        'r2': r2,
                        'accuracy': max(0, min(1, r2))  # Convert R² to 0-1 scale
                    }
                    
                    logger.info(f"Model {model_type}: MAE={mae:.4f}, R²={r2:.4f}")
                    
                except Exception as e:
                    logger.error(f"Error training model {model_type}: {e}")
                    model_performance[model_type] = {'mae': float('inf'), 'r2': -1, 'accuracy': 0}
            
            # Cache model performance
            cache_key = asset_id if asset_id else 'global'
            self.model_cache[cache_key] = {
                'performance': model_performance,
                'feature_columns': feature_columns,
                'trained_at': datetime.now(timezone.utc)
            }
            
            return model_performance
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {}
    
    def _predict_with_ensemble(self, X_scaled_dict: Dict, asset_id: Optional[str] = None) -> Dict[str, Any]:
        """Make predictions using ensemble of models"""
        cache_key = asset_id if asset_id else 'global'
        
        if cache_key not in self.model_cache:
            self._train_models(asset_id)
        
        performance = self.model_cache[cache_key]['performance']
        
        predictions = {}
        weights = {}
        total_weight = 0
        
        # Get predictions from each model and calculate weights based on performance
        for model_type, model in self.models.items():
            if model_type in performance and performance[model_type]['accuracy'] > 0:
                try:
                    pred = model.predict(X_scaled_dict[model_type])
                    accuracy = performance[model_type]['accuracy']
                    
                    predictions[model_type] = pred
                    weights[model_type] = accuracy ** 2  # Square to emphasize better models
                    total_weight += weights[model_type]
                    
                except Exception as e:
                    logger.error(f"Error getting prediction from {model_type}: {e}")
        
        if not predictions:
            logger.error("No valid predictions available")
            return {'prediction': np.array([0]), 'confidence': 0, 'model_contributions': {}}
        
        # Calculate weighted ensemble prediction
        ensemble_pred = np.zeros_like(list(predictions.values())[0])
        model_contributions = {}
        
        for model_type, pred in predictions.items():
            weight = weights[model_type] / total_weight
            ensemble_pred += weight * pred
            model_contributions[model_type] = {
                'weight': weight,
                'contribution': float(np.mean(pred))
            }
        
        # Calculate confidence based on model agreement
        if len(predictions) > 1:
            pred_values = np.array(list(predictions.values()))
            std_dev = np.std(pred_values, axis=0)
            mean_pred = np.mean(pred_values, axis=0)
            confidence = 1 - np.mean(std_dev / (mean_pred + 1e-6))  # Coefficient of variation
            confidence = max(0, min(1, confidence))
        else:
            confidence = list(performance.values())[0]['accuracy']
        
        return {
            'prediction': ensemble_pred,
            'confidence': confidence,
            'model_contributions': model_contributions
        }
    
    async def generate_forecast(self, request: RoyaltyForecastRequest) -> ForecastResult:
        """Generate AI-powered royalty forecast"""
        try:
            # Prepare base data for prediction
            if request.asset_id:
                base_data = self.historical_data[
                    self.historical_data['asset_id'] == request.asset_id
                ].tail(30)  # Use last 30 days as base
                
                if base_data.empty:
                    logger.warning(f"No historical data for asset {request.asset_id}")
                    base_data = self.historical_data.groupby(['platform', 'territory']).tail(1)
            else:
                # Use aggregated data for portfolio forecast
                base_data = self.historical_data.groupby(['platform', 'territory']).tail(7).groupby(
                    ['platform', 'territory']
                ).agg({
                    'streams': 'mean',
                    'engagement_rate': 'mean',
                    'cpm': 'mean',
                    'royalty_rate': 'mean',
                    'daily_revenue': 'mean'
                }).reset_index()
            
            # Generate future dates
            start_date = datetime.now().date()
            if request.period == ForecastPeriod.WEEKLY:
                freq = 'W'
                periods = request.horizon_months * 4
            elif request.period == ForecastPeriod.MONTHLY:
                freq = 'M'
                periods = request.horizon_months
            elif request.period == ForecastPeriod.QUARTERLY:
                freq = 'Q'
                periods = max(1, request.horizon_months // 3)
            else:  # YEARLY
                freq = 'Y'
                periods = max(1, request.horizon_months // 12)
            
            future_dates = pd.date_range(
                start=start_date, 
                periods=periods, 
                freq=freq
            )
            
            forecast_data = []
            total_predicted_revenue = 0
            
            # Prepare scaled features for each model
            X_scaled_dict = {}
            for model_type in self.models.keys():
                X_scaled_dict[model_type] = None
            
            # Generate predictions for each time period
            for i, future_date in enumerate(future_dates):
                period_data = []
                period_revenue = 0
                
                # Create prediction features based on base data
                for _, row in base_data.iterrows():
                    # Simulate future metrics with trend and seasonality
                    trend_factor = 1 + (0.05 * i / len(future_dates))  # 5% growth over horizon
                    seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * future_date.dayofyear / 365.25)
                    
                    future_streams = int(row.get('streams', 1000) * trend_factor * seasonal_factor)
                    future_engagement = row.get('engagement_rate', 0.5) * trend_factor * seasonal_factor
                    
                    # Create feature vector with proper encoding
                    platform_encoded = 0
                    territory_encoded = 0
                    
                    # Safely encode platform
                    if 'platform' in row and 'platform' in self.encoders:
                        try:
                            platform_encoded = self.encoders['platform'].transform([row.get('platform', 'spotify')])[0]
                        except ValueError:
                            # Handle unseen categories
                            platform_encoded = 0
                    
                    # Safely encode territory
                    if 'territory' in row and 'territory' in self.encoders:
                        try:
                            territory_encoded = self.encoders['territory'].transform([row.get('territory', 'US')])[0]
                        except ValueError:
                            # Handle unseen categories
                            territory_encoded = 0
                    
                    features = {
                        'platform_encoded': platform_encoded,
                        'territory_encoded': territory_encoded,
                        'day_of_week': future_date.weekday(),
                        'month': future_date.month,
                        'quarter': (future_date.month - 1) // 3 + 1,
                        'is_weekend': 1 if future_date.weekday() >= 5 else 0,
                        'days_since_release': 365 + i * 30,  # Simulate aging
                        'streams': future_streams,
                        'engagement_rate': future_engagement,
                        'cpm': row.get('cpm', 2.5),
                        'royalty_rate': row.get('royalty_rate', 0.005),
                        'revenue_7d_avg': row.get('daily_revenue', 10) * trend_factor,
                        'revenue_30d_avg': row.get('daily_revenue', 10) * trend_factor,
                        'revenue_lag_1': row.get('daily_revenue', 10),
                        'revenue_lag_7': row.get('daily_revenue', 10)
                    }
                    
                    # Prepare for each model
                    feature_vector = np.array([[
                        features['platform_encoded'], features['territory_encoded'],
                        features['day_of_week'], features['month'], features['quarter'],
                        features['is_weekend'], features['days_since_release'],
                        features['streams'], features['engagement_rate'], features['cpm'],
                        features['royalty_rate'], features['revenue_7d_avg'],
                        features['revenue_30d_avg'], features['revenue_lag_1'], features['revenue_lag_7']
                    ]])
                    
                    # Ensure models are trained before using scalers
                    cache_key = request.asset_id if request.asset_id else 'global'
                    if cache_key not in self.model_cache:
                        self._train_models(request.asset_id)
                    
                    for model_type in self.models.keys():
                        try:
                            scaled_features = self.scalers[model_type].transform(feature_vector)
                            if X_scaled_dict[model_type] is None:
                                X_scaled_dict[model_type] = scaled_features
                            else:
                                X_scaled_dict[model_type] = np.vstack([
                                    X_scaled_dict[model_type],
                                    scaled_features
                                ])
                        except Exception as e:
                            logger.warning(f"Error scaling features for {model_type}: {e}")
                            # Use zero-filled array as fallback
                            if X_scaled_dict[model_type] is None:
                                X_scaled_dict[model_type] = np.zeros((1, feature_vector.shape[1]))
                            else:
                                X_scaled_dict[model_type] = np.vstack([
                                    X_scaled_dict[model_type],
                                    np.zeros((1, feature_vector.shape[1]))
                                ])
                
                # Get ensemble prediction
                prediction_result = self._predict_with_ensemble(X_scaled_dict, request.asset_id)
                period_prediction = np.sum(prediction_result['prediction'])
                
                # Add confidence intervals if requested
                confidence_lower = period_prediction * 0.8 if request.confidence_intervals else None
                confidence_upper = period_prediction * 1.2 if request.confidence_intervals else None
                
                period_data = {
                    'date': future_date.isoformat(),
                    'period': request.period.value,
                    'predicted_revenue': float(max(0, period_prediction)),
                    'confidence_score': float(prediction_result['confidence']),
                    'model_contributions': prediction_result['model_contributions']
                }
                
                if request.confidence_intervals:
                    period_data['confidence_interval'] = {
                        'lower': float(max(0, confidence_lower)),
                        'upper': float(confidence_upper)
                    }
                
                forecast_data.append(period_data)
                period_revenue += period_prediction
                total_predicted_revenue += period_prediction
                
                # Reset for next period
                for model_type in X_scaled_dict.keys():
                    X_scaled_dict[model_type] = None
            
            # Generate key insights
            insights = self._generate_insights(forecast_data, request)
            
            # Generate scenarios if requested
            scenarios = []
            if request.include_scenarios:
                scenarios = await self._generate_scenarios(request, base_data, future_dates)
            
            # Calculate overall confidence and accuracy
            avg_confidence = np.mean([p['confidence_score'] for p in forecast_data])
            cache_key = request.asset_id if request.asset_id else 'global'
            model_accuracy = np.mean([
                perf['accuracy'] for perf in self.model_cache.get(cache_key, {}).get('performance', {}).values()
            ]) if cache_key in self.model_cache else 0.7
            
            return ForecastResult(
                asset_id=request.asset_id,
                period=request.period,
                forecast_data=forecast_data,
                total_predicted_revenue=float(max(0, total_predicted_revenue)),
                confidence_score=float(avg_confidence),
                model_accuracy=float(model_accuracy),
                key_insights=insights,
                scenarios=scenarios if scenarios else None
            )
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            raise
    
    def _generate_insights(self, forecast_data: List[Dict], request: RoyaltyForecastRequest) -> List[str]:
        """Generate key insights from forecast data"""
        insights = []
        
        if len(forecast_data) < 2:
            return ["Insufficient data for trend analysis"]
        
        # Analyze revenue trend
        revenues = [p['predicted_revenue'] for p in forecast_data]
        
        if len(revenues) > 1:
            trend = (revenues[-1] - revenues[0]) / revenues[0] if revenues[0] > 0 else 0
            
            if trend > 0.1:
                insights.append(f"Strong growth trend: {trend*100:.1f}% increase expected over forecast period")
            elif trend > 0:
                insights.append(f"Moderate growth: {trend*100:.1f}% increase projected")
            elif trend < -0.1:
                insights.append(f"Declining trend: {abs(trend)*100:.1f}% decrease projected")
            else:
                insights.append("Stable revenue pattern expected")
        
        # Analyze seasonality if monthly or weekly forecast
        if request.period in [ForecastPeriod.MONTHLY, ForecastPeriod.WEEKLY]:
            monthly_data = {}
            for item in forecast_data:
                date = datetime.fromisoformat(item['date'])
                month = date.month
                if month not in monthly_data:
                    monthly_data[month] = []
                monthly_data[month].append(item['predicted_revenue'])
            
            if len(monthly_data) > 3:
                avg_monthly = {month: np.mean(revenues) for month, revenues in monthly_data.items()}
                peak_month = max(avg_monthly, key=avg_monthly.get)
                low_month = min(avg_monthly, key=avg_monthly.get)
                
                month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                              5: 'May', 6: 'June', 7: 'July', 8: 'August',
                              9: 'September', 10: 'October', 11: 'November', 12: 'December'}
                
                insights.append(f"Peak performance expected in {month_names.get(peak_month, 'Unknown')}")
                insights.append(f"Lower performance anticipated in {month_names.get(low_month, 'Unknown')}")
        
        # Confidence analysis
        avg_confidence = np.mean([p['confidence_score'] for p in forecast_data])
        if avg_confidence > 0.8:
            insights.append("High confidence forecast based on strong historical patterns")
        elif avg_confidence > 0.6:
            insights.append("Moderate confidence - consider market volatility factors")
        else:
            insights.append("Lower confidence due to limited historical data or high variability")
        
        # Revenue magnitude insights
        total_revenue = sum(revenues)
        if total_revenue > 100000:
            insights.append("Significant revenue potential - consider scaling strategies")
        elif total_revenue > 10000:
            insights.append("Solid revenue stream - optimize for sustained growth")
        else:
            insights.append("Emerging opportunity - focus on engagement optimization")
        
        return insights
    
    async def _generate_scenarios(self, request: RoyaltyForecastRequest, base_data: pd.DataFrame, future_dates: pd.DatetimeIndex) -> List[Dict[str, Any]]:
        """Generate scenario analysis (what-if simulations)"""
        scenarios = []
        
        try:
            # Scenario 1: Platform Expansion (+25% engagement, +3 platforms)
            scenario_1 = await self._simulate_scenario(
                ScenarioParameters(
                    scenario_type=ScenarioType.PLATFORM_EXPANSION,
                    parameter_changes={"engagement_multiplier": 1.25, "platform_bonus": 0.3},
                    description="Expanding to 3 additional platforms with optimized content"
                ),
                request, base_data, future_dates
            )
            scenarios.append(scenario_1)
            
            # Scenario 2: Engagement Boost (+40% engagement through viral content)
            scenario_2 = await self._simulate_scenario(
                ScenarioParameters(
                    scenario_type=ScenarioType.ENGAGEMENT_BOOST,
                    parameter_changes={"engagement_multiplier": 1.4, "viral_factor": 1.2},
                    description="Viral content strategy boosting engagement by 40%"
                ),
                request, base_data, future_dates
            )
            scenarios.append(scenario_2)
            
            # Scenario 3: Geographic Expansion (+20% revenue from new territories)
            scenario_3 = await self._simulate_scenario(
                ScenarioParameters(
                    scenario_type=ScenarioType.GEOGRAPHIC_EXPANSION,
                    parameter_changes={"territory_multiplier": 1.2, "localization_bonus": 0.15},
                    description="Expanding to new geographic markets with localized content"
                ),
                request, base_data, future_dates
            )
            scenarios.append(scenario_3)
            
        except Exception as e:
            logger.error(f"Error generating scenarios: {e}")
        
        return scenarios
    
    async def _simulate_scenario(self, scenario: ScenarioParameters, request: RoyaltyForecastRequest, 
                                base_data: pd.DataFrame, future_dates: pd.DatetimeIndex) -> Dict[str, Any]:
        """Simulate a specific scenario"""
        try:
            # Apply scenario parameters to base prediction
            modified_request = request.copy()
            
            # Simulate modified forecast with scenario parameters
            base_forecast = await self.generate_forecast(request)
            
            # Apply scenario modifications
            scenario_revenue = 0
            for item in base_forecast.forecast_data:
                base_revenue = item['predicted_revenue']
                
                # Apply scenario multipliers
                modified_revenue = base_revenue
                for param, value in scenario.parameter_changes.items():
                    if 'multiplier' in param:
                        modified_revenue *= value
                    elif 'bonus' in param:
                        modified_revenue *= (1 + value)
                    elif 'factor' in param:
                        modified_revenue *= value
                
                scenario_revenue += modified_revenue
            
            # Calculate impact
            base_total = base_forecast.total_predicted_revenue
            impact = (scenario_revenue - base_total) / base_total if base_total > 0 else 0
            
            return {
                'scenario_type': scenario.scenario_type.value,
                'description': scenario.description,
                'parameter_changes': scenario.parameter_changes,
                'predicted_revenue': float(scenario_revenue),
                'base_revenue': float(base_total),
                'impact_percentage': float(impact * 100),
                'impact_absolute': float(scenario_revenue - base_total),
                'feasibility_score': self._calculate_feasibility(scenario),
                'recommended_actions': self._get_scenario_recommendations(scenario)
            }
            
        except Exception as e:
            logger.error(f"Error simulating scenario {scenario.scenario_type}: {e}")
            return {
                'scenario_type': scenario.scenario_type.value,
                'description': scenario.description,
                'error': str(e)
            }
    
    def _calculate_feasibility(self, scenario: ScenarioParameters) -> float:
        """Calculate feasibility score for a scenario (0-1)"""
        # Simple heuristic - more aggressive changes are less feasible
        total_change = sum(abs(v - 1) if 'multiplier' in k else abs(v) 
                          for k, v in scenario.parameter_changes.items())
        
        # Exponential decay for feasibility
        feasibility = np.exp(-total_change)
        return float(min(1.0, max(0.1, feasibility)))
    
    def _get_scenario_recommendations(self, scenario: ScenarioParameters) -> List[str]:
        """Get actionable recommendations for a scenario"""
        recommendations = []
        
        if scenario.scenario_type == ScenarioType.PLATFORM_EXPANSION:
            recommendations = [
                "Research top-performing platforms in your genre",
                "Prepare platform-specific content formats",
                "Set up automated distribution workflows",
                "Monitor initial performance for optimization"
            ]
        elif scenario.scenario_type == ScenarioType.ENGAGEMENT_BOOST:
            recommendations = [
                "Analyze viral content patterns in your niche",
                "Implement A/B testing for thumbnails and titles",
                "Engage with audience through comments and social media",
                "Create trending hashtag strategies"
            ]
        elif scenario.scenario_type == ScenarioType.GEOGRAPHIC_EXPANSION:
            recommendations = [
                "Research local music preferences and trends",
                "Consider language localization if applicable",
                "Partner with local influencers or artists",
                "Understand regional royalty and licensing requirements"
            ]
        
        return recommendations
    
    async def get_model_performance(self, asset_id: Optional[str] = None) -> Dict[str, Any]:
        """Get model performance metrics"""
        cache_key = asset_id if asset_id else 'global'
        
        if cache_key not in self.model_cache:
            performance = self._train_models(asset_id)
        else:
            performance = self.model_cache[cache_key]['performance']
        
        return {
            'asset_id': asset_id,
            'model_performance': performance,
            'best_model': max(performance.keys(), key=lambda x: performance[x]['accuracy']) if performance else None,
            'ensemble_accuracy': np.mean([p['accuracy'] for p in performance.values()]) if performance else 0,
            'data_points': len(self.historical_data),
            'last_trained': self.model_cache.get(cache_key, {}).get('trained_at', datetime.now(timezone.utc)).isoformat()
        }

# Global instance
ai_royalty_forecasting_service = AIRoyaltyForecastingService()