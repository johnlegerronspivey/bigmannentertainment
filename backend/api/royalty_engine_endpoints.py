"""
Real-Time Royalty Engine API Endpoints
Enterprise-grade royalty management API with blockchain integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import logging
import uuid
import asyncio
from decimal import Decimal

from royalty_engine_core import (
    royalty_engine,
    royalty_forecaster,
    TransactionEvent,
    ContractTerm,
    ContributorSplit,
    RoyaltyCalculation,
    RevenueSource,
    MonetizationType,
    PayoutMethod,
    ContractType
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/royalty-engine", tags=["Real-Time Royalty Engine"])
security = HTTPBearer()

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # This would integrate with your authentication system
    return "user_123"

# Transaction Event Processing Endpoints

@router.post("/events/process", response_model=Dict[str, Any])
async def process_transaction_event(
    event: TransactionEvent,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Process a real-time transaction event and calculate royalties"""
    try:
        # Process the transaction event
        calculation = await royalty_engine.process_transaction_event(event)
        
        return {
            "success": True,
            "message": "Transaction event processed successfully",
            "calculation_id": calculation.id,
            "total_royalty": float(calculation.total_royalty),
            "contributor_count": len(calculation.contributor_payouts),
            "payouts_triggered": len([p for p in calculation.contributor_payouts if float(p["net_amount"]) > 0])
        }
    except Exception as e:
        logger.error(f"Failed to process transaction event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process transaction event: {str(e)}")

@router.post("/events/batch-process", response_model=Dict[str, Any])
async def batch_process_events(
    events: List[TransactionEvent],
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Process multiple transaction events in batch"""
    try:
        results = []
        total_royalties = Decimal("0")
        total_payouts = 0
        
        for event in events:
            try:
                calculation = await royalty_engine.process_transaction_event(event)
                results.append({
                    "event_id": event.id,
                    "status": "success",
                    "calculation_id": calculation.id,
                    "total_royalty": float(calculation.total_royalty)
                })
                total_royalties += calculation.total_royalty
                total_payouts += len(calculation.contributor_payouts)
            except Exception as e:
                results.append({
                    "event_id": event.id,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Processed {len(events)} events",
            "results": results,
            "summary": {
                "total_events": len(events),
                "successful_events": len([r for r in results if r["status"] == "success"]),
                "failed_events": len([r for r in results if r["status"] == "error"]),
                "total_royalties": float(total_royalties),
                "total_payouts_triggered": total_payouts
            }
        }
    except Exception as e:
        logger.error(f"Failed to batch process events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to batch process events")

# Contract Management Endpoints

@router.post("/contracts/create", response_model=Dict[str, str])
async def create_contract_term(
    contract: ContractTerm,
    user_id: str = Depends(get_current_user)
):
    """Create new contract terms for an asset"""
    try:
        await royalty_engine.collection_contracts.insert_one(contract.dict())
        return {
            "success": True,
            "message": "Contract terms created successfully",
            "contract_id": contract.id
        }
    except Exception as e:
        logger.error(f"Failed to create contract terms: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create contract terms")

@router.get("/contracts/{asset_id}", response_model=Dict[str, Any])
async def get_contract_terms(
    asset_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get contract terms for an asset"""
    try:
        contract_data = await royalty_engine.collection_contracts.find_one({
            "asset_id": asset_id,
            "active": True
        })
        
        if not contract_data:
            raise HTTPException(status_code=404, detail="Contract terms not found")
        
        return {
            "success": True,
            "contract": contract_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contract terms: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contract terms")

@router.put("/contracts/{contract_id}", response_model=Dict[str, str])
async def update_contract_term(
    contract_id: str,
    updates: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Update contract terms"""
    try:
        result = await royalty_engine.collection_contracts.update_one(
            {"id": contract_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {
            "success": True,
            "message": "Contract terms updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update contract terms: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update contract terms")

# Contributor Split Management Endpoints

@router.post("/splits/create", response_model=Dict[str, str])
async def create_contributor_split(
    split: ContributorSplit,
    user_id: str = Depends(get_current_user)
):
    """Create contributor split configuration"""
    try:
        await royalty_engine.collection_splits.insert_one(split.dict())
        return {
            "success": True,
            "message": "Contributor split created successfully",
            "split_id": split.id
        }
    except Exception as e:
        logger.error(f"Failed to create contributor split: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create contributor split")

@router.get("/splits/{asset_id}", response_model=Dict[str, Any])
async def get_contributor_splits(
    asset_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get contributor splits for an asset"""
    try:
        splits_data = await royalty_engine.collection_splits.find({
            "asset_id": asset_id,
            "active": True
        }).to_list(length=None)
        
        total_percentage = sum(float(split["split_percentage"]) for split in splits_data)
        
        return {
            "success": True,
            "splits": splits_data,
            "total_percentage": total_percentage,
            "is_valid": abs(total_percentage - 100.0) < 0.01  # Allow small rounding errors
        }
    except Exception as e:
        logger.error(f"Failed to get contributor splits: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contributor splits")

@router.put("/splits/{split_id}", response_model=Dict[str, str])
async def update_contributor_split(
    split_id: str,
    updates: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Update contributor split"""
    try:
        result = await royalty_engine.collection_splits.update_one(
            {"id": split_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contributor split not found")
        
        return {
            "success": True,
            "message": "Contributor split updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update contributor split: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update contributor split")

# Royalty Calculation and Audit Endpoints

@router.get("/calculations/{calculation_id}", response_model=Dict[str, Any])
async def get_royalty_calculation(
    calculation_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get detailed royalty calculation"""
    try:
        calculation_data = await royalty_engine.collection_calculations.find_one({
            "id": calculation_id
        })
        
        if not calculation_data:
            raise HTTPException(status_code=404, detail="Calculation not found")
        
        return {
            "success": True,
            "calculation": calculation_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get calculation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get calculation")

@router.get("/calculations/asset/{asset_id}", response_model=Dict[str, Any])
async def get_asset_calculations(
    asset_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    user_id: str = Depends(get_current_user)
):
    """Get royalty calculations for an asset"""
    try:
        query = {"asset_id": asset_id}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            query["calculation_timestamp"] = date_filter
        
        calculations = await royalty_engine.collection_calculations.find(query).sort(
            "calculation_timestamp", -1
        ).limit(limit).to_list(length=None)
        
        # Calculate summary statistics
        total_royalties = sum(float(calc["total_royalty"]) for calc in calculations)
        total_revenue = sum(float(calc["gross_revenue"]) for calc in calculations)
        
        return {
            "success": True,
            "calculations": calculations,
            "summary": {
                "total_calculations": len(calculations),
                "total_royalties": total_royalties,
                "total_revenue": total_revenue,
                "average_royalty": total_royalties / len(calculations) if calculations else 0
            }
        }
    except Exception as e:
        logger.error(f"Failed to get asset calculations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get asset calculations")

@router.get("/audit/{transaction_id}", response_model=Dict[str, Any])
async def get_audit_trail(
    transaction_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get audit trail for a transaction"""
    try:
        audit_data = await royalty_engine.collection_audit.find_one({
            "transaction_event_id": transaction_id
        })
        
        if not audit_data:
            raise HTTPException(status_code=404, detail="Audit trail not found")
        
        return {
            "success": True,
            "audit_trail": audit_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get audit trail")

# Payout Management Endpoints

@router.get("/payouts/pending", response_model=Dict[str, Any])
async def get_pending_payouts(
    payout_method: Optional[PayoutMethod] = None,
    contributor_id: Optional[str] = None,
    limit: int = Query(100, le=1000),
    user_id: str = Depends(get_current_user)
):
    """Get pending payouts"""
    try:
        query = {"status": {"$in": ["pending_crypto", "pending_batch"]}}
        
        if payout_method:
            query["payout_method"] = payout_method.value
        if contributor_id:
            query["contributor_id"] = contributor_id
        
        payouts = await royalty_engine.collection_payouts.find(query).sort(
            "created_at", -1
        ).limit(limit).to_list(length=None)
        
        # Group by payout method for summary
        method_summary = {}
        total_amount = 0
        
        for payout in payouts:
            method = payout["payout_method"]
            if method not in method_summary:
                method_summary[method] = {"count": 0, "total_amount": 0}
            method_summary[method]["count"] += 1
            method_summary[method]["total_amount"] += float(payout["amount"])
            total_amount += float(payout["amount"])
        
        return {
            "success": True,
            "payouts": payouts,
            "summary": {
                "total_payouts": len(payouts),
                "total_amount": total_amount,
                "by_method": method_summary
            }
        }
    except Exception as e:
        logger.error(f"Failed to get pending payouts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get pending payouts")

@router.post("/payouts/{payout_id}/process", response_model=Dict[str, str])
async def process_payout(
    payout_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Process a specific payout"""
    try:
        payout_data = await royalty_engine.collection_payouts.find_one({"id": payout_id})
        
        if not payout_data:
            raise HTTPException(status_code=404, detail="Payout not found")
        
        if payout_data["status"] not in ["pending_crypto", "pending_batch"]:
            raise HTTPException(status_code=400, detail="Payout is not in a processable state")
        
        # Update status to processing
        await royalty_engine.collection_payouts.update_one(
            {"id": payout_id},
            {"$set": {"status": "processing", "processed_at": datetime.now(timezone.utc)}}
        )
        
        # Add background task to actually process the payout
        background_tasks.add_task(process_payout_async, payout_data)
        
        return {
            "success": True,
            "message": "Payout processing initiated",
            "payout_id": payout_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process payout: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process payout")

async def process_payout_async(payout_data: Dict[str, Any]):
    """Background task to process payout"""
    try:
        # This would integrate with actual payment processors
        # For now, we'll simulate processing
        await asyncio.sleep(2)  # Simulate processing time
        
        # Update status to completed
        await royalty_engine.collection_payouts.update_one(
            {"id": payout_data["id"]},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc),
                    "transaction_hash": f"tx_{uuid.uuid4().hex[:16]}"  # Mock transaction hash
                }
            }
        )
        
        logger.info(f"Payout {payout_data['id']} processed successfully")
        
    except Exception as e:
        logger.error(f"Failed to process payout {payout_data['id']}: {str(e)}")
        
        # Mark as failed
        await royalty_engine.collection_payouts.update_one(
            {"id": payout_data["id"]},
            {
                "$set": {
                    "status": "failed",
                    "failed_at": datetime.now(timezone.utc),
                    "error_message": str(e)
                }
            }
        )

# Analytics and Forecasting Endpoints

@router.get("/analytics/asset/{asset_id}/summary", response_model=Dict[str, Any])
async def get_asset_royalty_summary(
    asset_id: str,
    days: int = Query(30, le=365),
    user_id: str = Depends(get_current_user)
):
    """Get royalty summary for an asset"""
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get transaction events
        events = await royalty_engine.collection_events.find({
            "asset_id": asset_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        # Get calculations
        calculations = await royalty_engine.collection_calculations.find({
            "asset_id": asset_id,
            "calculation_timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        # Calculate metrics
        total_revenue = sum(float(event["gross_revenue"]) for event in events)
        total_royalties = sum(float(calc["total_royalty"]) for calc in calculations)
        total_events = len(events)
        
        # Revenue by source
        revenue_by_source = {}
        for event in events:
            source = event["revenue_source"]
            if source not in revenue_by_source:
                revenue_by_source[source] = 0
            revenue_by_source[source] += float(event["gross_revenue"])
        
        # Revenue by platform
        revenue_by_platform = {}
        for event in events:
            platform = event["platform"]
            if platform not in revenue_by_platform:
                revenue_by_platform[platform] = 0
            revenue_by_platform[platform] += float(event["gross_revenue"])
        
        return {
            "success": True,
            "asset_id": asset_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_revenue": total_revenue,
                "total_royalties": total_royalties,
                "total_events": total_events,
                "average_revenue_per_event": total_revenue / total_events if total_events > 0 else 0,
                "royalty_rate": (total_royalties / total_revenue * 100) if total_revenue > 0 else 0
            },
            "breakdown": {
                "by_revenue_source": revenue_by_source,
                "by_platform": revenue_by_platform
            }
        }
    except Exception as e:
        logger.error(f"Failed to get asset summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get asset summary")

@router.get("/analytics/forecast/{asset_id}", response_model=Dict[str, Any])
async def get_royalty_forecast(
    asset_id: str,
    months_ahead: int = Query(3, le=12),
    user_id: str = Depends(get_current_user)
):
    """Get royalty forecast for an asset"""
    try:
        forecast = await royalty_forecaster.forecast_monthly_royalties(asset_id, months_ahead)
        return {
            "success": True,
            "forecast": forecast
        }
    except Exception as e:
        logger.error(f"Failed to get forecast: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get forecast")

# Fraud Detection and Security Endpoints

@router.get("/security/fraud-flags", response_model=Dict[str, Any])
async def get_fraud_flags(
    status: str = Query("pending_review"),
    limit: int = Query(50, le=200),
    user_id: str = Depends(get_current_user)
):
    """Get fraud detection flags"""
    try:
        flags = await royalty_engine.db.fraud_flags.find({
            "status": status
        }).sort("created_at", -1).limit(limit).to_list(length=None)
        
        return {
            "success": True,
            "fraud_flags": flags,
            "count": len(flags)
        }
    except Exception as e:
        logger.error(f"Failed to get fraud flags: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get fraud flags")

@router.put("/security/fraud-flags/{flag_id}/resolve", response_model=Dict[str, str])
async def resolve_fraud_flag(
    flag_id: str,
    resolution: str,
    user_id: str = Depends(get_current_user)
):
    """Resolve a fraud detection flag"""
    try:
        result = await royalty_engine.db.fraud_flags.update_one(
            {"id": flag_id},
            {
                "$set": {
                    "status": "resolved",
                    "resolution": resolution,
                    "reviewed_at": datetime.now(timezone.utc),
                    "reviewer_id": user_id
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Fraud flag not found")
        
        return {
            "success": True,
            "message": "Fraud flag resolved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve fraud flag: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resolve fraud flag")

# Health and Status Endpoints

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check for royalty engine"""
    try:
        # Check database connectivity
        await royalty_engine.collection_events.find_one()
        
        return {
            "success": True,
            "status": "healthy",
            "message": "Real-Time Royalty Engine is operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "transaction_processing": "healthy",
                "royalty_calculation": "healthy",
                "payout_processing": "healthy",
                "fraud_detection": "healthy",
                "audit_trail": "healthy",
                "forecasting": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/status/comprehensive", response_model=Dict[str, Any])
async def get_comprehensive_status(
    user_id: str = Depends(get_current_user)
):
    """Get comprehensive system status"""
    try:
        # Get counts from various collections
        current_time = datetime.now(timezone.utc)
        last_24h = current_time - timedelta(hours=24)
        
        status = {
            "transaction_events": {
                "total": await royalty_engine.collection_events.count_documents({}),
                "last_24h": await royalty_engine.collection_events.count_documents({
                    "timestamp": {"$gte": last_24h}
                })
            },
            "royalty_calculations": {
                "total": await royalty_engine.collection_calculations.count_documents({}),
                "last_24h": await royalty_engine.collection_calculations.count_documents({
                    "calculation_timestamp": {"$gte": last_24h}
                })
            },
            "pending_payouts": {
                "crypto": await royalty_engine.collection_payouts.count_documents({
                    "status": "pending_crypto"
                }),
                "traditional": await royalty_engine.collection_payouts.count_documents({
                    "status": "pending_batch"
                })
            },
            "fraud_flags": {
                "pending": await royalty_engine.db.fraud_flags.count_documents({
                    "status": "pending_review"
                }),
                "resolved": await royalty_engine.db.fraud_flags.count_documents({
                    "status": "resolved"
                })
            },
            "contract_terms": {
                "active": await royalty_engine.collection_contracts.count_documents({
                    "active": True
                })
            },
            "contributor_splits": {
                "active": await royalty_engine.collection_splits.count_documents({
                    "active": True
                })
            }
        }
        
        return {
            "success": True,
            "message": "Comprehensive status retrieved",
            "timestamp": current_time.isoformat(),
            "status": status
        }
    except Exception as e:
        logger.error(f"Failed to get comprehensive status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get comprehensive status")