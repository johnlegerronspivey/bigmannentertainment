"""Agency onboarding endpoints - registration, KYC, talent, contracts."""
import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from config.database import db
from auth.service import get_current_user
from models.core import User
from models.agency import (
    VerificationStatus, AgencyRegistrationRequest,
    TalentCreationRequest, LicenseContractRequest,
)

agency_router = APIRouter(prefix="/agency", tags=["Agency Onboarding"])

@agency_router.post("/register")
async def register_agency(
    agency_data: AgencyRegistrationRequest,
    current_user: User = Depends(get_current_user)
):
    """Register a new agency"""
    try:
        # Check if user already has an agency
        existing_agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if existing_agency:
            raise HTTPException(status_code=400, detail="User already has an agency registered")
        
        # Create agency record
        agency_dict = {
            "id": str(uuid.uuid4()),
            "name": agency_data.name,
            "business_registration_number": agency_data.business_registration_number,
            "contact_info": agency_data.contact_info,
            "wallet_addresses": agency_data.wallet_addresses,
            "business_type": agency_data.business_type,
            "tax_id": agency_data.tax_id,
            "operating_countries": agency_data.operating_countries,
            "verification_status": VerificationStatus.PENDING,
            "verification_documents": [],
            "kyc_completed": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "commission_rate": 0.15,
            "auto_approve_licenses": False,
            "min_license_price": 50.0,
            "total_talent": 0,
            "total_assets": 0,
            "total_licenses_sold": 0,
            "total_revenue": 0.0,
            "owner_user_id": current_user.id,
            "owner_email": current_user.email
        }
        
        # Insert into database
        result = await db.agencies.insert_one(agency_dict)
        
        # Create audit log
        audit_log = {
            "id": str(uuid.uuid4()),
            "entity_type": "agency",
            "entity_id": agency_dict["id"],
            "action": "registered",
            "actor_id": current_user.id,
            "actor_type": "user",
            "action_data": {"agency_name": agency_data.name},
            "timestamp": datetime.now(timezone.utc)
        }
        await db.audit_logs.insert_one(audit_log)
        
        return {
            "agency_id": agency_dict["id"],
            "status": "registered",
            "verification_status": agency_dict["verification_status"],
            "message": "Agency registered successfully. KYC verification required."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register agency: {str(e)}")

@agency_router.get("/profile")
async def get_agency_profile(current_user: User = Depends(get_current_user)):
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
        
        # Convert MongoDB document to JSON serializable format
        agency_data = {
            "id": agency["id"],
            "name": agency["name"],
            "business_registration_number": agency.get("business_registration_number"),
            "contact_info": agency.get("contact_info", {}),
            "wallet_addresses": agency.get("wallet_addresses", {}),
            "business_type": agency.get("business_type"),
            "tax_id": agency.get("tax_id"),
            "operating_countries": agency.get("operating_countries", []),
            "verification_status": agency["verification_status"],
            "verification_documents": agency.get("verification_documents", []),
            "kyc_completed": agency.get("kyc_completed", False),
            "created_at": agency["created_at"].isoformat() if isinstance(agency["created_at"], datetime) else str(agency["created_at"]),
            "updated_at": agency["updated_at"].isoformat() if isinstance(agency["updated_at"], datetime) else str(agency["updated_at"]),
            "commission_rate": agency.get("commission_rate", 0.15),
            "auto_approve_licenses": agency.get("auto_approve_licenses", False),
            "min_license_price": agency.get("min_license_price", 50.0),
            "total_talent": talent_count,
            "total_assets": asset_count,
            "total_licenses_sold": license_count,
            "total_revenue": agency.get("total_revenue", 0.0),
            "owner_user_id": agency["owner_user_id"],
            "owner_email": agency["owner_email"]
        }
        
        return {"agency": agency_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agency profile: {str(e)}")

@agency_router.put("/profile")
async def update_agency_profile(
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
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
        
        return {"status": "updated", "message": "Agency profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agency profile: {str(e)}")

@agency_router.post("/upload-kyc")
async def upload_kyc_documents(
    files: List[UploadFile] = File(...),
    document_type: str = Form("kyc"),
    current_user: User = Depends(get_current_user)
):
    """Upload KYC documents for agency verification"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        uploaded_documents = []
        
        for file in files:
            # Mock upload process (since AWS might not be configured)
            mock_s3_url = f"https://mock-s3-bucket.s3.amazonaws.com/kyc/{agency['id']}/{file.filename}"
            
            uploaded_documents.append({
                "filename": file.filename,
                "original_filename": file.filename,
                "s3_url": mock_s3_url,
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
        
        return {
            "status": "uploaded",
            "documents": uploaded_documents,
            "message": "KYC documents uploaded successfully. Verification pending."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload KYC documents: {str(e)}")

@agency_router.post("/talent")
async def create_talent(
    talent_data: TalentCreationRequest,
    current_user: User = Depends(get_current_user)
):
    """Create new talent profile"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Create talent record
        talent_dict = {
            "id": str(uuid.uuid4()),
            "agency_id": agency["id"],
            "name": talent_data.name,
            "stage_name": talent_data.stage_name,
            "bio": talent_data.bio,
            "age_range": talent_data.age_range,
            "gender": talent_data.gender,
            "ethnicity": talent_data.ethnicity,
            "categories": talent_data.categories,
            "skills": talent_data.skills,
            "languages": talent_data.languages,
            "profile_images": [],
            "portfolio_images": [],
            "portfolio_videos": [],
            "active": True,
            "verified": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "total_licensed_images": 0,
            "total_licensing_revenue": 0.0
        }
        
        # Insert into database
        result = await db.talent.insert_one(talent_dict)
        
        # Update agency talent count
        await db.agencies.update_one(
            {"id": agency["id"]},
            {"$inc": {"total_talent": 1}}
        )
        
        return {
            "talent_id": talent_dict["id"],
            "status": "created",
            "message": "Talent profile created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create talent: {str(e)}")

@agency_router.get("/talent")
async def get_agency_talent(current_user: User = Depends(get_current_user)):
    """Get all talent for agency"""
    try:
        agency = await db.agencies.find_one({"owner_user_id": current_user.id})
        if not agency:
            raise HTTPException(status_code=404, detail="Agency not found")
        
        # Get talent list
        talent_cursor = db.talent.find({"agency_id": agency["id"]})
        talent_list = []
        
        async for talent in talent_cursor:
            talent_data = {
                "id": talent["id"],
                "agency_id": talent["agency_id"],
                "name": talent["name"],
                "stage_name": talent.get("stage_name"),
                "bio": talent.get("bio", ""),
                "age_range": talent.get("age_range"),
                "gender": talent.get("gender"),
                "ethnicity": talent.get("ethnicity"),
                "categories": talent.get("categories", []),
                "skills": talent.get("skills", []),
                "languages": talent.get("languages", []),
                "profile_images": talent.get("profile_images", []),
                "portfolio_images": talent.get("portfolio_images", []),
                "portfolio_videos": talent.get("portfolio_videos", []),
                "active": talent.get("active", True),
                "verified": talent.get("verified", False),
                "created_at": talent["created_at"].isoformat() if isinstance(talent["created_at"], datetime) else str(talent["created_at"]),
                "updated_at": talent["updated_at"].isoformat() if isinstance(talent["updated_at"], datetime) else str(talent["updated_at"]),
                "total_licensed_images": talent.get("total_licensed_images", 0),
                "total_licensing_revenue": talent.get("total_licensing_revenue", 0.0)
            }
            talent_list.append(talent_data)
        
        return {"talent": talent_list, "total": len(talent_list)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agency talent: {str(e)}")

@agency_router.post("/talent/{talent_id}/upload-assets")
async def upload_talent_assets(
    talent_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
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
            # Determine asset type
            asset_type = "image" if file.content_type and file.content_type.startswith("image/") else "video"
            
            # Mock upload process
            mock_s3_url = f"https://mock-s3-bucket.s3.amazonaws.com/assets/{agency['id']}/{talent_id}/{file.filename}"
            
            # Create asset record
            asset_dict = {
                "id": str(uuid.uuid4()),
                "agency_id": agency["id"],
                "talent_id": talent_id,
                "filename": file.filename,
                "original_filename": file.filename,
                "file_type": asset_type,
                "mime_type": file.content_type or "application/octet-stream",
                "file_size": 1024000,  # Mock size
                "s3_url": mock_s3_url,
                "thumbnail_url": f"{mock_s3_url}_thumb.jpg",
                "preview_url": f"{mock_s3_url}_preview.jpg",
                "dimensions": {"width": 1920, "height": 1080},
                "title": file.filename,
                "description": f"{asset_type.title()} asset for {talent['name']}",
                "keywords": [],
                "categories": [],
                "model_released": False,
                "property_released": False,
                "available_for_licensing": True,
                "base_license_price": 100.0,
                "status": "active",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "view_count": 0,
                "download_count": 0,
                "license_count": 0,
                "total_revenue": 0.0
            }
            
            # Insert asset into database
            result = await db.license_assets.insert_one(asset_dict)
            
            # Convert to JSON serializable format for response
            asset_response = {
                "id": asset_dict["id"],
                "agency_id": asset_dict["agency_id"],
                "talent_id": asset_dict["talent_id"],
                "filename": asset_dict["filename"],
                "original_filename": asset_dict["original_filename"],
                "file_type": asset_dict["file_type"],
                "mime_type": asset_dict["mime_type"],
                "file_size": asset_dict["file_size"],
                "s3_url": asset_dict["s3_url"],
                "thumbnail_url": asset_dict["thumbnail_url"],
                "preview_url": asset_dict["preview_url"],
                "dimensions": asset_dict["dimensions"],
                "title": asset_dict["title"],
                "description": asset_dict["description"],
                "keywords": asset_dict["keywords"],
                "categories": asset_dict["categories"],
                "model_released": asset_dict["model_released"],
                "property_released": asset_dict["property_released"],
                "available_for_licensing": asset_dict["available_for_licensing"],
                "base_license_price": asset_dict["base_license_price"],
                "status": asset_dict["status"],
                "created_at": asset_dict["created_at"].isoformat(),
                "updated_at": asset_dict["updated_at"].isoformat(),
                "view_count": asset_dict["view_count"],
                "download_count": asset_dict["download_count"],
                "license_count": asset_dict["license_count"],
                "total_revenue": asset_dict["total_revenue"]
            }
            uploaded_assets.append(asset_response)
        
        # Update agency asset count
        await db.agencies.update_one(
            {"id": agency["id"]},
            {"$inc": {"total_assets": len(uploaded_assets)}}
        )
        
        return {
            "status": "uploaded",
            "assets": uploaded_assets,
            "message": f"Uploaded {len(uploaded_assets)} assets successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload talent assets: {str(e)}")

@agency_router.post("/license-contract")
async def create_license_contract(
    contract_data: LicenseContractRequest,
    current_user: User = Depends(get_current_user)
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
        contract_dict = {
            "id": str(uuid.uuid4()),
            "agency_id": agency["id"],
            "talent_id": contract_data.talent_id,
            "asset_id": contract_data.asset_id,
            "blockchain_network": contract_data.blockchain_network,
            "contract_standard": contract_data.contract_standard,
            "license_type": contract_data.license_type,
            "base_price": contract_data.base_price,
            "currency": "USD",
            "royalty_splits": contract_data.royalty_splits,
            "usage_terms": contract_data.usage_terms,
            "exclusivity": contract_data.exclusivity,
            "duration_months": contract_data.duration_months,
            "territory": contract_data.territory,
            "status": "draft",
            "created_at": datetime.now(timezone.utc),
            "deployed_at": None,
            "expires_at": None,
            "contract_address": None,
            "token_id": None,
            "transaction_hash": None
        }
        
        # Insert into database
        result = await db.license_contracts.insert_one(contract_dict)
        
        return {
            "contract_id": contract_dict["id"],
            "status": "created",
            "message": "License contract created. Ready for blockchain deployment."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create license contract: {str(e)}")

@agency_router.post("/license-contract/{contract_id}/deploy")
async def deploy_license_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user)
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
        
        # Mock blockchain deployment
        mock_contract_address = f"0x{hashlib.md5(contract_id.encode()).hexdigest()}"
        mock_token_id = int(hashlib.md5(contract_id.encode()).hexdigest()[:8], 16)
        mock_tx_hash = f"0x{hashlib.sha256(contract_id.encode()).hexdigest()}"
        
        # Update contract with blockchain info
        await db.license_contracts.update_one(
            {"id": contract_id},
            {
                "$set": {
                    "contract_address": mock_contract_address,
                    "token_id": str(mock_token_id),
                    "transaction_hash": mock_tx_hash,
                    "status": "deployed",
                    "deployed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "status": "deployed",
            "blockchain_network": contract["blockchain_network"],
            "contract_address": mock_contract_address,
            "token_id": mock_token_id,
            "transaction_hash": mock_tx_hash,
            "explorer_url": f"https://etherscan.io/tx/{mock_tx_hash}" if contract["blockchain_network"] == "ethereum" else None,
            "message": "License contract deployed to blockchain successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy license contract: {str(e)}")

@agency_router.get("/dashboard")
async def get_agency_dashboard(current_user: User = Depends(get_current_user)):
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
        
        # Get recent activity (convert to JSON serializable format)
        recent_logs_cursor = db.audit_logs.find(
            {"entity_id": {"$in": [agency["id"]]}}
        ).sort("timestamp", -1).limit(10)
        
        recent_logs = []
        async for log in recent_logs_cursor:
            log_data = {
                "id": log["id"],
                "entity_type": log["entity_type"],
                "entity_id": log["entity_id"],
                "action": log["action"],
                "actor_id": log["actor_id"],
                "actor_type": log["actor_type"],
                "action_data": log.get("action_data", {}),
                "timestamp": log["timestamp"].isoformat() if isinstance(log["timestamp"], datetime) else str(log["timestamp"])
            }
            recent_logs.append(log_data)
        
        # Calculate revenue metrics (mock data for now)
        total_revenue = agency.get("total_revenue", 0.0)
        monthly_revenue = total_revenue * 0.1  # Mock calculation
        
        # Get licensing activity (convert to JSON serializable format)
        recent_contracts_cursor = db.license_contracts.find(
            {"agency_id": agency["id"]}
        ).sort("created_at", -1).limit(5)
        
        recent_contracts = []
        async for contract in recent_contracts_cursor:
            contract_data = {
                "id": contract["id"],
                "agency_id": contract["agency_id"],
                "talent_id": contract.get("talent_id"),
                "asset_id": contract["asset_id"],
                "blockchain_network": contract["blockchain_network"],
                "contract_standard": contract["contract_standard"],
                "license_type": contract["license_type"],
                "base_price": contract["base_price"],
                "currency": contract.get("currency", "USD"),
                "status": contract["status"],
                "created_at": contract["created_at"].isoformat() if isinstance(contract["created_at"], datetime) else str(contract["created_at"]),
                "deployed_at": contract["deployed_at"].isoformat() if contract.get("deployed_at") and isinstance(contract["deployed_at"], datetime) else None,
                "contract_address": contract.get("contract_address"),
                "token_id": contract.get("token_id"),
                "transaction_hash": contract.get("transaction_hash")
            }
            recent_contracts.append(contract_data)
        
        dashboard_data = {
            "agency_info": {
                "id": agency["id"],
                "name": agency["name"],
                "verification_status": agency["verification_status"],
                "kyc_completed": agency.get("kyc_completed", False),
                "created_at": agency["created_at"].isoformat() if isinstance(agency["created_at"], datetime) else str(agency["created_at"])
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
        raise HTTPException(status_code=500, detail=f"Failed to get agency dashboard: {str(e)}")

@agency_router.get("/status")
async def agency_status():
    """Get agency module status"""
    return {
        "status": "operational",
        "module": "Agency Onboarding",
        "version": "1.0.0",
        "features": [
            "Agency Registration",
            "Talent Management", 
            "Asset Upload",
            "License Contracts",
            "Blockchain Integration",
            "Dashboard Analytics"
        ]
    }


