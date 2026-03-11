"""
Agency Onboarding API Endpoints
Complete agency registration, talent management, and licensing workflow
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import json
import logging

from .models import User
from .auth import get_current_user
from .database import get_database
from .agency_models import (
    Agency, Talent, LicenseContract, LicenseAsset, DisputeCase, AuditLog, RoyaltyPayment,
    AgencyRegistrationRequest, TalentCreationRequest, LicenseContractRequest, AssetUploadRequest,
    VerificationStatus, LicenseType, BlockchainNetwork, ContractStandard, DisputeStatus
)
from .blockchain_service import blockchain_service
from .aws_storage_service import storage_service

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Create router
agency_router = APIRouter(prefix="/agency", tags=["Agency Onboarding"])

# Agency Management Endpoints

@agency_router.post("/register")
async def register_agency(
    agency_data: AgencyRegistrationRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Register a new agency"""
    try:
        # Check if user already has an agency
        existing_agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if existing_agency:
            raise HTTPException(status_code=400, detail="User already has an agency registered")
        
        # Create agency record
        agency = Agency(
            name=agency_data.name,
            business_registration_number=agency_data.business_registration_number,
            contact_info=agency_data.contact_info,
            wallet_addresses=agency_data.wallet_addresses,
            business_type=agency_data.business_type,
            tax_id=agency_data.tax_id,
            operating_countries=agency_data.operating_countries,
            verification_status=VerificationStatus.PENDING
        )
        
        # Add owner information
        agency_dict = agency.dict()
        agency_dict["owner_user_id"] = current_user.id
        agency_dict["owner_email"] = current_user.email
        
        # Insert into database
        result = await db.agencies.insert_one(agency_dict)
        agency_dict["_id"] = result.inserted_id
        
        # Create audit log
        await _create_audit_log(
            db=db,
            entity_type="agency",
            entity_id=agency.id,
            action="registered",
            actor_id=current_user.id,
            actor_type="user",
            action_data={"agency_name": agency.name}
        )
        
        return {
            "agency_id": agency.id,
            "status": "registered",
            "verification_status": agency.verification_status,
            "message": "Agency registered successfully. KYC verification required."
        }
        
    except Exception as e:
        logger.error(f"Error registering agency: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register agency: {str(e)}")

@agency_router.get("/profile")
async def get_agency_profile(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get agency profile for current user"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Get talent count
        talent_count = await db.talent.count_documents({"agency_id": agency["id"]})
        
        # Get asset count
        asset_count = await db.license_assets.count_documents({"agency_id": agency["id"]})
        
        # Get license count
        license_count = await db.license_contracts.count_documents({"agency_id": agency["id"]})
        
        # Update counts
        agency["total_talent"] = talent_count
        agency["total_assets"] = asset_count
        agency["total_licenses_sold"] = license_count
        
        return {"agency": agency}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agency profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agency profile: {str(e)}")

@agency_router.put("/profile")
async def update_agency_profile(
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update agency profile"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Update allowed fields
        allowed_fields = [
            "name", "contact_info", "business_type", "operating_countries",
            "commission_rate", "auto_approve_licenses", "min_license_price"
        ]
        
        update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        await db.agencies.update_one(
            {"id": agency["id"]},
            {"$set": update_fields}
        )
        
        # Create audit log
        await _create_audit_log(
            db=db,
            entity_type="agency",
            entity_id=agency["id"],
            action="updated",
            actor_id=current_user.id,
            actor_type="user",
            action_data=update_fields
        )
        
        return {"status": "updated", "message": "Agency profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agency profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update agency profile: {str(e)}")

@agency_router.post("/upload-kyc")
async def upload_kyc_documents(
    files: List[UploadFile] = File(...),
    document_type: str = Form("kyc"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload KYC documents for agency verification"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        uploaded_documents = []
        
        for file in files:
            # Read file data
            file_data = await file.read()
            
            # Upload to S3
            upload_result = await storage_service.upload_document(
                file_data=file_data,
                filename=file.filename,
                agency_id=agency["id"],
                document_type=document_type
            )
            
            if upload_result["status"] == "success":
                uploaded_documents.append({
                    "filename": upload_result["filename"],
                    "original_filename": upload_result["original_filename"],
                    "s3_url": upload_result["s3_url"],
                    "document_type": document_type,
                    "upload_date": datetime.now(timezone.utc).isoformat()
                })
        
        # Update agency with document URLs
        await db.agencies.update_one(
            {"id": agency["id"]},
            {
                "$push": {"verification_documents": {"$each": [doc["s3_url"] for doc in uploaded_documents]}},
                "$set": {"kyc_completed": True, "updated_at": datetime.now(timezone.utc)}
            }
        )
        
        # Create audit log
        await _create_audit_log(
            db=db,
            entity_type="agency",
            entity_id=agency["id"],
            action="kyc_uploaded",
            actor_id=current_user.id,
            actor_type="user",
            action_data={"documents_count": len(uploaded_documents), "document_type": document_type}
        )
        
        return {
            "status": "uploaded",
            "documents": uploaded_documents,
            "message": "KYC documents uploaded successfully. Verification pending."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading KYC documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload KYC documents: {str(e)}")

# Talent Management Endpoints

@agency_router.post("/talent")
async def create_talent(
    talent_data: TalentCreationRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create new talent profile"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Create talent record
        talent = Talent(
            agency_id=agency["id"],
            name=talent_data.name,
            stage_name=talent_data.stage_name,
            bio=talent_data.bio,
            age_range=talent_data.age_range,
            gender=talent_data.gender,
            ethnicity=talent_data.ethnicity,
            categories=talent_data.categories,
            skills=talent_data.skills,
            languages=talent_data.languages
        )
        
        # Insert into database
        talent_dict = talent.dict()
        result = await db.talent.insert_one(talent_dict)
        talent_dict["_id"] = result.inserted_id
        
        # Update agency talent count
        await db.agencies.update_one(
            {"id": agency["id"]},
            {"$inc": {"total_talent": 1}}
        )
        
        # Create audit log
        await _create_audit_log(
            db=db,
            entity_type="talent",
            entity_id=talent.id,
            action="created",
            actor_id=current_user.id,
            actor_type="user",
            action_data={"talent_name": talent.name, "agency_id": agency["id"]}
        )
        
        return {
            "talent_id": talent.id,
            "status": "created",
            "message": "Talent profile created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating talent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create talent: {str(e)}")

@agency_router.get("/talent")
async def get_agency_talent(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all talent for agency"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Get talent list
        talent_list = await db.talent.find({"agency_id": agency["id"]}).to_list(100)
        
        return {"talent": talent_list, "total": len(talent_list)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agency talent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agency talent: {str(e)}")

@agency_router.post("/talent/{talent_id}/upload-assets")
async def upload_talent_assets(
    talent_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload portfolio assets for talent"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Verify talent belongs to agency
        talent = await db.talent.find_one({"id": talent_id, "agency_id": agency["id"]})
        if not talent:
            raise HTTPException(status_code=404, detail="Talent not found")
        
        uploaded_assets = []
        
        for file in files:
            # Read file data
            file_data = await file.read()
            
            # Determine asset type
            asset_type = "image" if file.content_type.startswith("image/") else "video"
            
            # Upload to S3
            upload_result = await storage_service.upload_agency_asset(
                file_data=file_data,
                filename=file.filename,
                agency_id=agency["id"],
                asset_type=asset_type,
                metadata={"talent_id": talent_id}
            )
            
            if upload_result["status"] == "success":
                # Create asset record
                asset = LicenseAsset(
                    agency_id=agency["id"],
                    talent_id=talent_id,
                    filename=upload_result["filename"],
                    original_filename=upload_result["original_filename"],
                    file_type=asset_type,
                    mime_type=upload_result["mime_type"],
                    file_size=upload_result["file_size"],
                    s3_url=upload_result["s3_url"],
                    thumbnail_url=upload_result["thumbnail_url"],
                    preview_url=upload_result["preview_url"],
                    dimensions=upload_result["dimensions"],
                    title=upload_result["original_filename"],
                    description=f"{asset_type.title()} asset for {talent['name']}"
                )
                
                # Insert asset into database
                asset_dict = asset.dict()
                result = await db.license_assets.insert_one(asset_dict)
                asset_dict["_id"] = result.inserted_id
                
                uploaded_assets.append(asset_dict)
        
        # Update agency asset count
        await db.agencies.update_one(
            {"id": agency["id"]},
            {"$inc": {"total_assets": len(uploaded_assets)}}
        )
        
        # Create audit log
        await _create_audit_log(
            db=db,
            entity_type="talent",
            entity_id=talent_id,
            action="assets_uploaded",
            actor_id=current_user.id,
            actor_type="user",
            action_data={"assets_count": len(uploaded_assets), "agency_id": agency["id"]}
        )
        
        return {
            "status": "uploaded",
            "assets": uploaded_assets,
            "message": f"Uploaded {len(uploaded_assets)} assets successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading talent assets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload talent assets: {str(e)}")

# Licensing Workflow Endpoints

@agency_router.post("/license-contract")
async def create_license_contract(
    contract_data: LicenseContractRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new license contract"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Verify asset belongs to agency
        asset = await db.license_assets.find_one({"id": contract_data.asset_id, "agency_id": agency["id"]})
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Create license contract
        license_contract = LicenseContract(
            agency_id=agency["id"],
            talent_id=contract_data.talent_id,
            asset_id=contract_data.asset_id,
            blockchain_network=contract_data.blockchain_network,
            contract_standard=contract_data.contract_standard,
            license_type=contract_data.license_type,
            base_price=contract_data.base_price,
            royalty_splits=contract_data.royalty_splits,
            usage_terms=contract_data.usage_terms,
            exclusivity=contract_data.exclusivity,
            duration_months=contract_data.duration_months,
            territory=contract_data.territory
        )
        
        # Insert into database
        contract_dict = license_contract.dict()
        result = await db.license_contracts.insert_one(contract_dict)
        contract_dict["_id"] = result.inserted_id
        
        # Create audit log
        await _create_audit_log(
            db=db,
            entity_type="license",
            entity_id=license_contract.id,
            action="created",
            actor_id=current_user.id,
            actor_type="user",
            action_data={
                "asset_id": contract_data.asset_id,
                "blockchain": contract_data.blockchain_network,
                "license_type": contract_data.license_type,
                "base_price": contract_data.base_price
            }
        )
        
        return {
            "contract_id": license_contract.id,
            "status": "created",
            "message": "License contract created. Ready for blockchain deployment."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating license contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create license contract: {str(e)}")

@agency_router.post("/license-contract/{contract_id}/deploy")
async def deploy_license_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Deploy license contract to blockchain"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Get license contract
        contract = await db.license_contracts.find_one({"id": contract_id, "agency_id": agency["id"]})
        if not contract:
            raise HTTPException(status_code=404, detail="License contract not found")
        
        if contract["status"] != "draft":
            raise HTTPException(status_code=400, detail="Contract already deployed")
        
        # Deploy to blockchain
        blockchain_network = contract["blockchain_network"]
        contract_standard = contract["contract_standard"]
        
        # Deploy contract
        deployment_result = await blockchain_service.deploy_contract(
            blockchain=blockchain_network,
            contract_type=contract_standard.lower(),
            params={
                "name": f"BME License {contract_id[:8]}",
                "symbol": "BMELIT"
            }
        )
        
        if deployment_result["status"] != "deployed":
            raise HTTPException(status_code=500, detail=f"Blockchain deployment failed: {deployment_result.get('error')}")
        
        # Generate unique token ID
        import hashlib
        token_id = int(hashlib.md5(contract_id.encode()).hexdigest()[:8], 16)
        
        # Mint license token
        mint_result = await blockchain_service.mint_license_token(
            blockchain=blockchain_network,
            contract_params={
                "contract_address": deployment_result["contract_address"],
                "to_address": agency["wallet_addresses"].get(blockchain_network),
                "token_id": token_id,
                "metadata_uri": f"https://api.bigmannentertainment.com/metadata/{contract_id}"
            }
        )
        
        if mint_result["status"] not in ["minted", "prepared"]:
            raise HTTPException(status_code=500, detail=f"Token minting failed: {mint_result.get('error')}")
        
        # Update contract with blockchain info
        await db.license_contracts.update_one(
            {"id": contract_id},
            {
                "$set": {
                    "contract_address": deployment_result["contract_address"],
                    "token_id": str(token_id),
                    "transaction_hash": deployment_result["transaction_hash"],
                    "status": "deployed",
                    "deployed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Create audit log
        await _create_audit_log(
            db=db,
            entity_type="license",
            entity_id=contract_id,
            action="deployed",
            actor_id=current_user.id,
            actor_type="user",
            action_data={
                "blockchain_network": blockchain_network,
                "contract_address": deployment_result["contract_address"],
                "token_id": token_id,
                "transaction_hash": deployment_result["transaction_hash"]
            },
            blockchain_tx_hash=deployment_result["transaction_hash"]
        )
        
        return {
            "status": "deployed",
            "blockchain_network": blockchain_network,
            "contract_address": deployment_result["contract_address"],
            "token_id": token_id,
            "transaction_hash": deployment_result["transaction_hash"],
            "explorer_url": f"https://etherscan.io/tx/{deployment_result['transaction_hash']}" if blockchain_network == "ethereum" else None,
            "message": "License contract deployed to blockchain successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying license contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy license contract: {str(e)}")

@agency_router.get("/dashboard")
async def get_agency_dashboard(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get comprehensive agency dashboard data"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Get dashboard statistics
        talent_count = await db.talent.count_documents({"agency_id": agency["id"]})
        asset_count = await db.license_assets.count_documents({"agency_id": agency["id"]})
        
        # Get contract statistics
        total_contracts = await db.license_contracts.count_documents({"agency_id": agency["id"]})
        deployed_contracts = await db.license_contracts.count_documents({"agency_id": agency["id"], "status": "deployed"})
        active_licenses = await db.license_contracts.count_documents({"agency_id": agency["id"], "status": "active"})
        
        # Get recent activity
        recent_logs = await db.audit_logs.find(
            {"entity_id": {"$in": [agency["id"]]}}
        ).sort("timestamp", -1).limit(10).to_list(10)
        
        # Calculate revenue metrics (mock data for now)
        total_revenue = agency.get("total_revenue", 0.0)
        monthly_revenue = total_revenue * 0.1  # Mock calculation
        
        # Get licensing activity
        recent_contracts = await db.license_contracts.find(
            {"agency_id": agency["id"]}
        ).sort("created_at", -1).limit(5).to_list(5)
        
        dashboard_data = {
            "agency_info": {
                "id": agency["id"],
                "name": agency["name"],
                "verification_status": agency["verification_status"],
                "kyc_completed": agency.get("kyc_completed", False),
                "created_at": agency["created_at"]
            },
            "statistics": {
                "total_talent": talent_count,
                "total_assets": asset_count,
                "total_contracts": total_contracts,
                "deployed_contracts": deployed_contracts,
                "active_licenses": active_licenses,
                "total_revenue": total_revenue,
                "monthly_revenue": monthly_revenue
            },
            "recent_activity": recent_logs,
            "recent_contracts": recent_contracts,
            "verification_needed": not agency.get("kyc_completed", False) or agency["verification_status"] == "pending"
        }
        
        return {"dashboard": dashboard_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agency dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agency dashboard: {str(e)}")

# Helper Functions

async def _create_audit_log(db, entity_type: str, entity_id: str, action: str, 
                          actor_id: str, actor_type: str, action_data: Dict[str, Any],
                          blockchain_tx_hash: str = None):
    """Create audit log entry"""
    try:
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            action_data=action_data,
            blockchain_tx_hash=blockchain_tx_hash
        )
        
        await db.audit_logs.insert_one(audit_log.dict())
        
    except Exception as e:
        logger.error(f"Error creating audit log: {str(e)}")
        # Don't raise exception for audit log failures