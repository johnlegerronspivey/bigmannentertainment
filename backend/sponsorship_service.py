from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
from .sponsorship_models import *

class SponsorshipBonusCalculator:
    """Service for calculating sponsorship bonuses based on performance metrics"""
    
    def __init__(self):
        self.calculation_cache = {}
    
    def calculate_bonus(self, deal: SponsorshipDeal, metrics: List[PerformanceMetric], 
                       period_start: date, period_end: date) -> List[BonusCalculation]:
        """Calculate bonuses for a sponsorship deal based on performance metrics"""
        calculations = []
        
        # Group metrics by type
        metric_totals = self._aggregate_metrics(metrics, period_start, period_end)
        
        for rule in deal.bonus_rules:
            calculation = self._calculate_rule_bonus(
                deal, rule, metric_totals, period_start, period_end
            )
            if calculation:
                calculations.append(calculation)
        
        return calculations
    
    def _aggregate_metrics(self, metrics: List[PerformanceMetric], 
                          start_date: date, end_date: date) -> Dict[str, float]:
        """Aggregate metrics by type for the given period"""
        totals = {}
        
        for metric in metrics:
            if start_date <= metric.measurement_date <= end_date:
                metric_key = metric.metric_type.value
                if metric_key not in totals:
                    totals[metric_key] = 0.0
                totals[metric_key] += metric.metric_value
        
        return totals
    
    def _calculate_rule_bonus(self, deal: SponsorshipDeal, rule: BonusRule, 
                             metrics: Dict[str, float], period_start: date, 
                             period_end: date) -> Optional[BonusCalculation]:
        """Calculate bonus for a specific rule"""
        
        calculation = BonusCalculation(
            deal_id=deal.id,
            rule_id=rule.id,
            period_start=period_start,
            period_end=period_end,
            calculation_method=rule.bonus_type.value
        )
        
        if rule.bonus_type == BonusType.FIXED:
            calculation.bonus_amount = rule.base_amount or 0.0
            calculation.total_amount = calculation.bonus_amount
            
        elif rule.bonus_type == BonusType.PERFORMANCE:
            calculation = self._calculate_performance_bonus(rule, metrics, calculation)
            
        elif rule.bonus_type == BonusType.MILESTONE:
            calculation = self._calculate_milestone_bonus(rule, metrics, calculation)
            
        elif rule.bonus_type == BonusType.REVENUE_SHARE:
            calculation = self._calculate_revenue_share_bonus(rule, metrics, calculation)
            
        elif rule.bonus_type == BonusType.TIERED:
            calculation = self._calculate_tiered_bonus(rule, metrics, calculation)
        
        # Apply caps and thresholds
        calculation = self._apply_constraints(rule, calculation)
        
        return calculation if calculation.bonus_amount > 0 else None
    
    def _calculate_performance_bonus(self, rule: BonusRule, metrics: Dict[str, float], 
                                   calculation: BonusCalculation) -> BonusCalculation:
        """Calculate performance-based bonus"""
        if not rule.metric_type or rule.metric_type.value not in metrics:
            return calculation
        
        metric_value = metrics[rule.metric_type.value]
        calculation.base_metrics[rule.metric_type.value] = metric_value
        
        # Check if threshold is met
        if rule.threshold and metric_value < rule.threshold:
            calculation.threshold_met = False
            return calculation
        
        # Calculate bonus based on performance
        if rule.rate:
            calculation.bonus_amount = metric_value * rule.rate
        elif rule.base_amount:
            # Performance multiplier based on how much over threshold
            if rule.threshold:
                excess = metric_value - rule.threshold
                multiplier = 1.0 + (excess / rule.threshold)
                calculation.performance_multiplier = min(multiplier, 5.0)  # Cap at 5x
                calculation.bonus_amount = rule.base_amount * calculation.performance_multiplier
            else:
                calculation.bonus_amount = rule.base_amount
        
        calculation.total_amount = calculation.bonus_amount
        return calculation
    
    def _calculate_milestone_bonus(self, rule: BonusRule, metrics: Dict[str, float], 
                                 calculation: BonusCalculation) -> BonusCalculation:
        """Calculate milestone-based bonus"""
        if not rule.metric_type or rule.metric_type.value not in metrics:
            return calculation
        
        metric_value = metrics[rule.metric_type.value]
        calculation.base_metrics[rule.metric_type.value] = metric_value
        
        # Check which milestones are achieved
        for milestone in rule.milestones:
            target = milestone.get("target", 0)
            bonus = milestone.get("bonus", 0)
            
            if metric_value >= target:
                calculation.bonus_amount += bonus
                calculation.applied_rules.append({
                    "milestone_target": target,
                    "milestone_bonus": bonus,
                    "achieved": True
                })
        
        calculation.total_amount = calculation.bonus_amount
        return calculation
    
    def _calculate_revenue_share_bonus(self, rule: BonusRule, metrics: Dict[str, float], 
                                     calculation: BonusCalculation) -> BonusCalculation:
        """Calculate revenue sharing bonus"""
        revenue = metrics.get("revenue", 0.0)
        calculation.base_metrics["revenue"] = revenue
        
        if rule.percentage and revenue > 0:
            calculation.bonus_amount = revenue * (rule.percentage / 100.0)
        
        calculation.total_amount = calculation.bonus_amount
        return calculation
    
    def _calculate_tiered_bonus(self, rule: BonusRule, metrics: Dict[str, float], 
                               calculation: BonusCalculation) -> BonusCalculation:
        """Calculate tiered bonus structure"""
        if not rule.metric_type or rule.metric_type.value not in metrics:
            return calculation
        
        metric_value = metrics[rule.metric_type.value]
        calculation.base_metrics[rule.metric_type.value] = metric_value
        
        # Find applicable tier
        for tier in sorted(rule.tiers, key=lambda x: x.get("min", 0)):
            tier_min = tier.get("min", 0)
            tier_max = tier.get("max", float("inf"))
            tier_rate = tier.get("rate", 0)
            tier_bonus = tier.get("bonus", 0)
            
            if tier_min <= metric_value <= tier_max:
                if tier_rate:
                    calculation.bonus_amount = metric_value * tier_rate
                else:
                    calculation.bonus_amount = tier_bonus
                
                calculation.applied_rules.append({
                    "tier": tier,
                    "applied": True
                })
                break
        
        calculation.total_amount = calculation.bonus_amount
        return calculation
    
    def _apply_constraints(self, rule: BonusRule, 
                          calculation: BonusCalculation) -> BonusCalculation:
        """Apply caps, minimums, and other constraints"""
        
        # Apply minimum performance requirement
        if rule.minimum_performance:
            primary_metric = rule.metric_type.value if rule.metric_type else "views"
            if calculation.base_metrics.get(primary_metric, 0) < rule.minimum_performance:
                calculation.threshold_met = False
                calculation.bonus_amount = 0.0
                calculation.total_amount = 0.0
        
        # Apply bonus cap
        if rule.cap and calculation.bonus_amount > rule.cap:
            calculation.bonus_amount = rule.cap
            calculation.total_amount = rule.cap
            calculation.cap_applied = True
        
        return calculation

class SponsorshipAnalytics:
    """Service for analyzing sponsorship performance and ROI"""
    
    def __init__(self):
        self.calculator = SponsorshipBonusCalculator()
    
    def generate_campaign_summary(self, deal: SponsorshipDeal, 
                                 metrics: List[PerformanceMetric],
                                 payouts: List[SponsorshipPayout],
                                 period_start: date, period_end: date) -> CampaignSummary:
        """Generate comprehensive campaign performance summary"""
        
        summary = CampaignSummary(
            deal_id=deal.id,
            period_start=period_start,
            period_end=period_end
        )
        
        # Aggregate performance metrics
        summary = self._aggregate_performance_metrics(summary, metrics, period_start, period_end)
        
        # Calculate financial metrics
        summary = self._calculate_financial_metrics(summary, deal, payouts, period_start, period_end)
        
        # Calculate derived metrics
        summary = self._calculate_derived_metrics(summary)
        
        # Assess performance vs targets
        summary = self._assess_target_achievement(summary, deal)
        
        return summary
    
    def _aggregate_performance_metrics(self, summary: CampaignSummary, 
                                     metrics: List[PerformanceMetric],
                                     start_date: date, end_date: date) -> CampaignSummary:
        """Aggregate all performance metrics for the period"""
        
        for metric in metrics:
            if start_date <= metric.measurement_date <= end_date:
                if metric.metric_type == MetricType.VIEWS:
                    summary.total_views += metric.metric_value
                elif metric.metric_type == MetricType.DOWNLOADS:
                    summary.total_downloads += metric.metric_value
                elif metric.metric_type == MetricType.STREAMS:
                    summary.total_streams += metric.metric_value
                elif metric.metric_type == MetricType.ENGAGEMENT:
                    summary.total_engagement += metric.metric_value
                elif metric.metric_type == MetricType.CLICKS:
                    summary.total_clicks += metric.metric_value
                elif metric.metric_type == MetricType.CONVERSIONS:
                    summary.total_conversions += metric.metric_value
                elif metric.metric_type == MetricType.REVENUE:
                    summary.total_revenue += metric.metric_value
        
        return summary
    
    def _calculate_financial_metrics(self, summary: CampaignSummary, 
                                   deal: SponsorshipDeal,
                                   payouts: List[SponsorshipPayout],
                                   start_date: date, end_date: date) -> CampaignSummary:
        """Calculate financial performance metrics"""
        
        for payout in payouts:
            if start_date <= payout.period_start <= end_date or start_date <= payout.period_end <= end_date:
                summary.total_spend += payout.amount
                
                if payout.payout_type == "base_fee":
                    summary.base_fees += payout.amount
                elif payout.payout_type == "bonus":
                    summary.bonus_payments += payout.amount
        
        # Calculate average bonus
        period_days = (end_date - start_date).days + 1
        if period_days > 0:
            summary.average_bonus_per_period = summary.bonus_payments / max(1, period_days // 30)
        
        return summary
    
    def _calculate_derived_metrics(self, summary: CampaignSummary) -> CampaignSummary:
        """Calculate derived performance metrics"""
        
        # Cost per thousand impressions
        if summary.total_views > 0:
            summary.cpm = (summary.total_spend / summary.total_views) * 1000
        
        # Cost per click
        if summary.total_clicks > 0:
            summary.cpc = summary.total_spend / summary.total_clicks
        
        # Cost per acquisition
        if summary.total_conversions > 0:
            summary.cpa = summary.total_spend / summary.total_conversions
        
        # Return on investment
        if summary.total_spend > 0:
            summary.roi = ((summary.total_revenue - summary.total_spend) / summary.total_spend) * 100
        
        # Engagement rate
        if summary.total_views > 0:
            summary.engagement_rate = (summary.total_engagement / summary.total_views) * 100
        
        # Conversion rate
        if summary.total_clicks > 0:
            summary.conversion_rate = (summary.total_conversions / summary.total_clicks) * 100
        
        return summary
    
    def _assess_target_achievement(self, summary: CampaignSummary, 
                                  deal: SponsorshipDeal) -> CampaignSummary:
        """Assess performance against KPI targets"""
        
        for kpi, target in deal.kpi_targets.items():
            actual = getattr(summary, f"total_{kpi}", 0)
            if target > 0:
                achievement = (actual / target) * 100
                summary.target_achievement[kpi] = min(achievement, 200)  # Cap at 200%
        
        # Calculate overall performance grade
        if summary.target_achievement:
            avg_achievement = sum(summary.target_achievement.values()) / len(summary.target_achievement)
            if avg_achievement >= 90:
                summary.performance_grade = "A"
            elif avg_achievement >= 80:
                summary.performance_grade = "B"
            elif avg_achievement >= 70:
                summary.performance_grade = "C"
            elif avg_achievement >= 60:
                summary.performance_grade = "D"
            else:
                summary.performance_grade = "F"
        
        return summary

class SponsorshipRecommendationEngine:
    """Service for recommending optimal sponsorship strategies"""
    
    def __init__(self):
        pass
    
    def recommend_bonus_structure(self, sponsor: Sponsor, 
                                 historical_performance: Dict[str, Any]) -> List[BonusRule]:
        """Recommend optimal bonus structure based on sponsor and performance data"""
        
        recommendations = []
        
        # Base performance bonus
        performance_rule = BonusRule(
            name="Performance Bonus",
            bonus_type=BonusType.PERFORMANCE,
            metric_type=MetricType.VIEWS,
            rate=0.001,  # $0.001 per view
            threshold=1000,  # Minimum 1000 views
            cap=1000.0  # Maximum $1000 bonus
        )
        recommendations.append(performance_rule)
        
        # Milestone bonuses based on sponsor tier
        if sponsor.tier in ["gold", "platinum"]:
            milestone_rule = BonusRule(
                name="Milestone Bonuses",
                bonus_type=BonusType.MILESTONE,
                metric_type=MetricType.VIEWS,
                milestones=[
                    {"target": 10000, "bonus": 200},
                    {"target": 50000, "bonus": 500},
                    {"target": 100000, "bonus": 1000}
                ]
            )
            recommendations.append(milestone_rule)
        
        # Engagement bonus for premium sponsors
        if sponsor.tier == "platinum":
            engagement_rule = BonusRule(
                name="Engagement Bonus",
                bonus_type=BonusType.PERFORMANCE,
                metric_type=MetricType.ENGAGEMENT,
                rate=0.01,  # $0.01 per engagement
                threshold=100
            )
            recommendations.append(engagement_rule)
        
        return recommendations
    
    def optimize_campaign_targeting(self, deal: SponsorshipDeal, 
                                   performance_history: List[PerformanceMetric]) -> Dict[str, Any]:
        """Recommend optimal targeting based on performance history"""
        
        recommendations = {
            "recommended_platforms": [],
            "optimal_content_types": [],
            "best_posting_times": [],
            "target_demographics": {}
        }
        
        # Analyze platform performance
        platform_performance = {}
        for metric in performance_history:
            if metric.platform:
                if metric.platform not in platform_performance:
                    platform_performance[metric.platform] = {"views": 0, "engagement": 0}
                
                if metric.metric_type == MetricType.VIEWS:
                    platform_performance[metric.platform]["views"] += metric.metric_value
                elif metric.metric_type == MetricType.ENGAGEMENT:
                    platform_performance[metric.platform]["engagement"] += metric.metric_value
        
        # Sort platforms by performance
        sorted_platforms = sorted(
            platform_performance.items(),
            key=lambda x: x[1]["views"] + x[1]["engagement"],
            reverse=True
        )
        
        recommendations["recommended_platforms"] = [p[0] for p in sorted_platforms[:5]]
        
        return recommendations