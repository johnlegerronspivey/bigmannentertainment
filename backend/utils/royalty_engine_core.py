"""
Real-Time Royalty Engine: Core Processing System
Enterprise-grade royalty calculation and distribution engine with blockchain integration
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, Field, validator
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dataclasses import dataclass
import hashlib
import hmac

logger = logging.getLogger(__name__)

# Database connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'royalty_engine')]

class RevenueSource(str, Enum):
    STREAMING = "streaming"
    DOWNLOAD = "download"
    SOCIAL_MEDIA = "social_media"
    SYNC_LICENSE = "sync_license"
    BROADCAST = "broadcast"
    AD_IMPRESSION = "ad_impression"
    SUBSCRIPTION = "subscription"

class MonetizationType(str, Enum):
    AD_SUPPORTED = "ad_supported"
    SUBSCRIPTION = "subscription"
    PURCHASE = "purchase"
    SYNC_FEE = "sync_fee"
    PERFORMANCE_ROYALTY = "performance_royalty"

class PayoutMethod(str, Enum):
    CRYPTO_INSTANT = "crypto_instant"
    ACH_BATCH = "ach_batch"
    WIRE_TRANSFER = "wire_transfer"
    PAYPAL = "paypal"
    STABLECOIN = "stablecoin"

class ContractType(str, Enum):
    FIXED_FEE = "fixed_fee"
    PERCENTAGE = "percentage"
    TIERED_RATES = "tiered_rates"
    MINIMUM_GUARANTEE = "minimum_guarantee"
    HYBRID = "hybrid"

class TransactionEvent(BaseModel):
    """Core transaction event that triggers royalty calculation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    platform: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    territory: str
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    revenue_source: RevenueSource
    monetization_type: MonetizationType
    gross_revenue: Decimal
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.0")
    platform_fee_rate: Decimal = Decimal("0.0")
    metadata: Dict[str, Any] = {}

class ContractTerm(BaseModel):
    """Smart contract terms for royalty calculation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    contract_type: ContractType
    base_rate: Decimal  # Base percentage or fixed amount
    minimum_payout: Decimal = Decimal("0.01")
    maximum_payout: Optional[Decimal] = None
    territory_modifiers: Dict[str, Decimal] = {}  # Territory-specific rate adjustments
    platform_modifiers: Dict[str, Decimal] = {}  # Platform-specific rate adjustments
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    active: bool = True

class ContributorSplit(BaseModel):
    """Contributor split configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    contributor_id: str
    contributor_type: str  # "artist", "producer", "label", "songwriter", etc.
    split_percentage: Decimal
    wallet_address: Optional[str] = None  # For crypto payouts
    payout_method: PayoutMethod = PayoutMethod.ACH_BATCH
    tax_jurisdiction: str = "US"
    minimum_payout_threshold: Decimal = Decimal("1.00")
    active: bool = True

class RoyaltyCalculation(BaseModel):
    """Result of royalty calculation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_event_id: str
    asset_id: str
    gross_revenue: Decimal
    platform_fee: Decimal
    tax_withholding: Decimal
    net_revenue: Decimal
    total_royalty: Decimal
    contributor_payouts: List[Dict[str, Any]]
    calculation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    blockchain_hash: Optional[str] = None
    audit_trail: Dict[str, Any] = {}

class FraudDetectionResult(BaseModel):
    """Fraud detection analysis result"""
    transaction_id: str
    risk_score: float  # 0.0 to 1.0
    flags: List[str]
    is_suspicious: bool
    recommended_action: str

@dataclass
class TaxCalculation:
    """Tax calculation result"""
    gross_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    jurisdiction: str
    tax_type: str

class RoyaltyEngineCore:
    """Core royalty processing engine"""
    
    def __init__(self):
        self.collection_events = db.transaction_events
        self.collection_contracts = db.contract_terms
        self.collection_splits = db.contributor_splits
        self.collection_calculations = db.royalty_calculations
        self.collection_audit = db.audit_trail
        self.collection_payouts = db.payout_queue
        
    async def process_transaction_event(self, event: TransactionEvent) -> RoyaltyCalculation:
        """Process a transaction event and calculate royalties"""
        try:
            # Store the transaction event
            await self.collection_events.insert_one(event.dict())
            
            # Get contract terms for the asset
            contract_terms = await self._get_contract_terms(event.asset_id)
            if not contract_terms:
                raise ValueError(f"No contract terms found for asset {event.asset_id}")
            
            # Get contributor splits
            contributor_splits = await self._get_contributor_splits(event.asset_id)
            if not contributor_splits:
                raise ValueError(f"No contributor splits found for asset {event.asset_id}")
            
            # Perform fraud detection
            fraud_result = await self._detect_fraud(event)
            if fraud_result.is_suspicious:
                await self._flag_suspicious_transaction(event, fraud_result)
                if fraud_result.recommended_action == "BLOCK":
                    raise ValueError(f"Transaction blocked due to fraud detection: {fraud_result.flags}")
            
            # Calculate royalties
            calculation = await self._calculate_royalties(event, contract_terms, contributor_splits)
            
            # Store calculation result
            await self.collection_calculations.insert_one(calculation.dict())
            
            # Create audit trail
            await self._create_audit_trail(event, calculation)
            
            # Trigger payouts if thresholds are met
            await self._trigger_payouts(calculation)
            
            logger.info(f"Processed transaction {event.id} for asset {event.asset_id}")
            return calculation
            
        except Exception as e:
            logger.error(f"Error processing transaction event {event.id}: {str(e)}")
            await self._log_error(event, str(e))
            raise
    
    async def _get_contract_terms(self, asset_id: str) -> Optional[ContractTerm]:
        """Get active contract terms for an asset"""
        current_time = datetime.now(timezone.utc)
        
        contract_data = await self.collection_contracts.find_one({
            "asset_id": asset_id,
            "active": True,
            "effective_date": {"$lte": current_time},
            "$or": [
                {"expiry_date": {"$gt": current_time}},
                {"expiry_date": None}
            ]
        })
        
        if contract_data:
            return ContractTerm(**contract_data)
        return None
    
    async def _get_contributor_splits(self, asset_id: str) -> List[ContributorSplit]:
        """Get active contributor splits for an asset"""
        splits_data = await self.collection_splits.find({
            "asset_id": asset_id,
            "active": True
        }).to_list(length=None)
        
        return [ContributorSplit(**split) for split in splits_data]
    
    async def _detect_fraud(self, event: TransactionEvent) -> FraudDetectionResult:
        """Detect potential fraud in transaction events"""
        flags = []
        risk_score = 0.0
        
        # Check for suspicious revenue amounts
        if event.gross_revenue > Decimal("10000"):  # Very high single transaction
            flags.append("HIGH_REVENUE_SINGLE_TRANSACTION")
            risk_score += 0.3
        
        # Check for rapid successive transactions from same user/device
        if event.user_id:
            recent_count = await self.collection_events.count_documents({
                "user_id": event.user_id,
                "timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(minutes=5)}
            })
            if recent_count > 100:
                flags.append("RAPID_USER_TRANSACTIONS")
                risk_score += 0.4
        
        # Check for unusual territory patterns
        if event.territory not in ["US", "CA", "GB", "DE", "FR", "AU", "JP"]:
            territory_volume = await self.collection_events.count_documents({
                "territory": event.territory,
                "timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(hours=24)}
            })
            if territory_volume > 1000:
                flags.append("UNUSUAL_TERRITORY_VOLUME")
                risk_score += 0.2
        
        # Determine if suspicious
        is_suspicious = risk_score > 0.5
        recommended_action = "BLOCK" if risk_score > 0.7 else "REVIEW" if is_suspicious else "ALLOW"
        
        return FraudDetectionResult(
            transaction_id=event.id,
            risk_score=risk_score,
            flags=flags,
            is_suspicious=is_suspicious,
            recommended_action=recommended_action
        )
    
    async def _calculate_royalties(self, event: TransactionEvent, contract_terms: ContractTerm, 
                                 contributor_splits: List[ContributorSplit]) -> RoyaltyCalculation:
        """Calculate royalties based on contract terms and contributor splits"""
        
        # Apply platform fee
        platform_fee = event.gross_revenue * event.platform_fee_rate
        revenue_after_platform = event.gross_revenue - platform_fee
        
        # Apply territory modifier
        territory_modifier = contract_terms.territory_modifiers.get(event.territory, Decimal("1.0"))
        
        # Apply platform modifier
        platform_modifier = contract_terms.platform_modifiers.get(event.platform, Decimal("1.0"))
        
        # Calculate base royalty
        if contract_terms.contract_type == ContractType.PERCENTAGE:
            base_royalty = revenue_after_platform * contract_terms.base_rate * territory_modifier * platform_modifier
        elif contract_terms.contract_type == ContractType.FIXED_FEE:
            base_royalty = contract_terms.base_rate * territory_modifier * platform_modifier
        else:
            # For now, default to percentage
            base_royalty = revenue_after_platform * contract_terms.base_rate * territory_modifier * platform_modifier
        
        # Apply minimum/maximum constraints
        if base_royalty < contract_terms.minimum_payout:
            base_royalty = contract_terms.minimum_payout
        if contract_terms.maximum_payout and base_royalty > contract_terms.maximum_payout:
            base_royalty = contract_terms.maximum_payout
        
        # Calculate contributor payouts
        contributor_payouts = []
        total_split_percentage = sum(split.split_percentage for split in contributor_splits)
        
        if total_split_percentage != Decimal("100.0"):
            logger.warning(f"Split percentages don't add up to 100% for asset {event.asset_id}")
        
        for split in contributor_splits:
            # Calculate individual payout
            split_amount = base_royalty * (split.split_percentage / Decimal("100.0"))
            
            # Calculate taxes
            tax_calc = await self._calculate_taxes(split_amount, split.tax_jurisdiction)
            
            # Only include if above minimum threshold
            if split_amount >= split.minimum_payout_threshold:
                contributor_payouts.append({
                    "contributor_id": split.contributor_id,
                    "contributor_type": split.contributor_type,
                    "split_percentage": float(split.split_percentage),
                    "gross_amount": float(split_amount),
                    "tax_amount": float(tax_calc.tax_amount),
                    "net_amount": float(tax_calc.net_amount),
                    "payout_method": split.payout_method.value,
                    "wallet_address": split.wallet_address,
                    "currency": event.currency
                })
        
        total_tax = sum(Decimal(str(payout["tax_amount"])) for payout in contributor_payouts)
        total_royalty = sum(Decimal(str(payout["gross_amount"])) for payout in contributor_payouts)
        
        return RoyaltyCalculation(
            transaction_event_id=event.id,
            asset_id=event.asset_id,
            gross_revenue=event.gross_revenue,
            platform_fee=platform_fee,
            tax_withholding=total_tax,
            net_revenue=revenue_after_platform,
            total_royalty=total_royalty,
            contributor_payouts=contributor_payouts,
            audit_trail={
                "contract_terms_id": contract_terms.id,
                "territory_modifier": float(territory_modifier),
                "platform_modifier": float(platform_modifier),
                "fraud_score": 0.0  # Will be updated if fraud detected
            }
        )
    
    async def _calculate_taxes(self, amount: Decimal, jurisdiction: str) -> TaxCalculation:
        """Calculate taxes based on jurisdiction"""
        # Simplified tax calculation - in production, integrate with Avalara/TaxJar
        tax_rates = {
            "US": Decimal("0.30"),  # 30% withholding for US
            "CA": Decimal("0.25"),  # 25% for Canada
            "GB": Decimal("0.20"),  # 20% for UK
            "DE": Decimal("0.26"),  # 26% for Germany
        }
        
        tax_rate = tax_rates.get(jurisdiction, Decimal("0.30"))  # Default to US rate
        tax_amount = amount * tax_rate
        net_amount = amount - tax_amount
        
        return TaxCalculation(
            gross_amount=amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            net_amount=net_amount,
            jurisdiction=jurisdiction,
            tax_type="withholding"
        )
    
    async def _create_audit_trail(self, event: TransactionEvent, calculation: RoyaltyCalculation):
        """Create immutable audit trail entry"""
        audit_entry = {
            "id": str(uuid.uuid4()),
            "transaction_event_id": event.id,
            "calculation_id": calculation.id,
            "timestamp": datetime.now(timezone.utc),
            "event_hash": self._hash_data(event.dict()),
            "calculation_hash": self._hash_data(calculation.dict()),
            "previous_hash": await self._get_last_audit_hash(),
            "data": {
                "event": event.dict(),
                "calculation": calculation.dict(),
                "system_version": "1.0.0"
            }
        }
        
        # Create chain hash
        audit_entry["chain_hash"] = self._hash_data(audit_entry)
        
        await self.collection_audit.insert_one(audit_entry)
    
    def _hash_data(self, data: dict) -> str:
        """Create SHA-256 hash of data"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    async def _get_last_audit_hash(self) -> str:
        """Get the hash of the last audit entry for chaining"""
        last_entry = await self.collection_audit.find_one(
            {}, sort=[("timestamp", -1)]
        )
        return last_entry["chain_hash"] if last_entry else "genesis"
    
    async def _trigger_payouts(self, calculation: RoyaltyCalculation):
        """Trigger payouts for contributors based on calculation"""
        for payout in calculation.contributor_payouts:
            # Check if crypto instant payout
            if payout["payout_method"] in ["crypto_instant", "stablecoin"]:
                await self._queue_crypto_payout(calculation, payout)
            else:
                await self._queue_traditional_payout(calculation, payout)
    
    async def _queue_crypto_payout(self, calculation: RoyaltyCalculation, payout: Dict[str, Any]):
        """Queue cryptocurrency payout"""
        payout_record = {
            "id": str(uuid.uuid4()),
            "calculation_id": calculation.id,
            "contributor_id": payout["contributor_id"],
            "amount": payout["net_amount"],
            "currency": payout["currency"],
            "payout_method": payout["payout_method"],
            "wallet_address": payout["wallet_address"],
            "status": "pending_crypto",
            "created_at": datetime.now(timezone.utc),
            "scheduled_at": datetime.now(timezone.utc),  # Instant
            "metadata": {
                "asset_id": calculation.asset_id,
                "transaction_event_id": calculation.transaction_event_id
            }
        }
        
        await self.collection_payouts.insert_one(payout_record)
    
    async def _queue_traditional_payout(self, calculation: RoyaltyCalculation, payout: Dict[str, Any]):
        """Queue traditional payout (ACH, wire, PayPal)"""
        # Calculate next batch payout date (e.g., monthly on 15th)
        now = datetime.now(timezone.utc)
        next_payout = now.replace(day=15, hour=0, minute=0, second=0, microsecond=0)
        if now.day >= 15:
            if now.month == 12:
                next_payout = next_payout.replace(year=now.year + 1, month=1)
            else:
                next_payout = next_payout.replace(month=now.month + 1)
        
        payout_record = {
            "id": str(uuid.uuid4()),
            "calculation_id": calculation.id,
            "contributor_id": payout["contributor_id"],
            "amount": payout["net_amount"],
            "currency": payout["currency"],
            "payout_method": payout["payout_method"],
            "status": "pending_batch",
            "created_at": datetime.now(timezone.utc),
            "scheduled_at": next_payout,
            "metadata": {
                "asset_id": calculation.asset_id,
                "transaction_event_id": calculation.transaction_event_id
            }
        }
        
        await self.collection_payouts.insert_one(payout_record)
    
    async def _flag_suspicious_transaction(self, event: TransactionEvent, fraud_result: FraudDetectionResult):
        """Flag suspicious transaction for review"""
        flag_record = {
            "id": str(uuid.uuid4()),
            "transaction_event_id": event.id,
            "fraud_score": fraud_result.risk_score,
            "flags": fraud_result.flags,
            "recommended_action": fraud_result.recommended_action,
            "status": "pending_review",
            "created_at": datetime.now(timezone.utc),
            "reviewed_at": None,
            "reviewer_id": None,
            "resolution": None
        }
        
        await db.fraud_flags.insert_one(flag_record)
    
    async def _log_error(self, event: TransactionEvent, error: str):
        """Log processing errors"""
        error_record = {
            "id": str(uuid.uuid4()),
            "transaction_event_id": event.id,
            "error_message": error,
            "timestamp": datetime.now(timezone.utc),
            "event_data": event.dict(),
            "retry_count": 0,
            "resolved": False
        }
        
        await db.processing_errors.insert_one(error_record)

# Forecasting and Analytics Engine
class RoyaltyForecaster:
    """Predictive analytics for royalty forecasting"""
    
    def __init__(self):
        self.collection_events = db.transaction_events
        self.collection_calculations = db.royalty_calculations
    
    async def forecast_monthly_royalties(self, asset_id: str, months_ahead: int = 3) -> Dict[str, Any]:
        """Forecast royalties for the next N months"""
        # Get historical data for the asset
        from datetime import timedelta
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=365)  # Look back 1 year
        
        historical_data = await self.collection_events.find({
            "asset_id": asset_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        if not historical_data:
            return {"forecast": [], "confidence": 0.0, "trend": "insufficient_data"}
        
        # Simple forecasting based on trends (in production, use ML models)
        monthly_revenues = {}
        for event in historical_data:
            month_key = event["timestamp"].strftime("%Y-%m")
            if month_key not in monthly_revenues:
                monthly_revenues[month_key] = Decimal("0")
            monthly_revenues[month_key] += event["gross_revenue"]
        
        # Calculate trend
        revenues = list(monthly_revenues.values())
        if len(revenues) >= 2:
            trend = float((revenues[-1] - revenues[0]) / len(revenues))
        else:
            trend = 0.0
        
        # Generate forecast
        last_revenue = revenues[-1] if revenues else Decimal("0")
        forecast = []
        
        for i in range(months_ahead):
            projected_revenue = last_revenue + (Decimal(str(trend)) * (i + 1))
            projected_revenue = max(projected_revenue, Decimal("0"))  # Don't go negative
            
            forecast.append({
                "month": (end_date + timedelta(days=30 * (i + 1))).strftime("%Y-%m"),
                "projected_revenue": float(projected_revenue),
                "confidence": max(0.8 - (i * 0.1), 0.3)  # Decreasing confidence
            })
        
        return {
            "asset_id": asset_id,
            "forecast": forecast,
            "historical_average": float(sum(revenues) / len(revenues)) if revenues else 0.0,
            "trend_direction": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
            "confidence": 0.7 if len(revenues) >= 6 else 0.5
        }

# Initialize services
royalty_engine = RoyaltyEngineCore()
royalty_forecaster = RoyaltyForecaster()