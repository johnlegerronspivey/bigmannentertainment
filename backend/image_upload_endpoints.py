from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
import logging
import json
import os
import uuid
from datetime import datetime
import jwt

from image_metadata_service import (
    ImageMetadataService, 
    ImageMetadata, 
    ModelReleaseForm, 
    IPTCMetadata,
    DDEXImageDescriptor
)
from web3_nft_service import (
    Web3NFTService, 
    NFTMintRequest, 
    DAOProposalRequest,
    RoyaltyRecipient
)

# Import database connection
import asyncio
import motor.motor_asyncio
from pydantic import BaseModel
from decimal import Decimal

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# Database connection - standalone to avoid circular import
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "bigmann_entertainment")]

# User model for authentication
class User(BaseModel):
    id: str
    email: str
    full_name: str
    role: str = "user"
    is_active: bool = True

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token - standalone version"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user from database
        user_doc = await db.users.find_one({"email": email})
        if user_doc is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_doc)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Create router
image_router = APIRouter(prefix="/images", tags=["image_upload"])

# Initialize services
image_service = ImageMetadataService(db)
web3_service = Web3NFTService(db)

@image_router.post("/upload")
async def upload_image_with_metadata(
    file: UploadFile = File(...),
    model_name: Optional[str] = Form(None),
    agency_name: Optional[str] = Form(None),
    photographer_name: Optional[str] = Form(None),
    shoot_date: Optional[str] = Form(None),
    usage_rights: str = Form("editorial_only"),
    territory_rights: str = Form("worldwide"),
    duration_rights: str = Form("perpetual"),
    exclusive: bool = Form(False),
    headline: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    copyright_notice: Optional[str] = Form(None),
    license_terms: Optional[str] = Form(None),
    content_rating: str = Form("general"),
    target_agencies: Optional[str] = Form(None),  # JSON string of agency IDs
    base_pricing: Optional[str] = Form("0"),
    max_resolution: str = Form("4000"),
    # Web3 NFT Parameters
    enable_nft: Optional[str] = Form("false"),
    blockchain: str = Form("polygon"),
    token_standard: str = Form("ERC721"),
    royalty_recipients: Optional[str] = Form(None),  # JSON string
    # DAO Governance Parameters
    enable_dao: Optional[str] = Form("false"),
    proposal_type: str = Form("licensing_terms"),
    voting_period: int = Form(7),
    current_user: User = Depends(get_current_user)
):
    """Upload image with comprehensive metadata extraction and model release validation"""
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size (500MB limit for model agencies)
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 500MB limit")
    
    try:
        # Extract metadata from image
        metadata = await image_service.extract_metadata_from_image(file_content, file.filename)
        
        # Update metadata with form data
        metadata.photographer_id = current_user.id
        metadata.usage_rights = usage_rights
        metadata.license_terms = license_terms
        metadata.content_rating = content_rating
        
        # Parse target agencies
        if target_agencies:
            try:
                agencies = json.loads(target_agencies)
                if isinstance(agencies, list):
                    metadata.ddex_descriptor.agency_name = agencies[0] if agencies else None
            except json.JSONDecodeError:
                pass
        
        # Update IPTC metadata with form data
        if not metadata.iptc_metadata:
            metadata.iptc_metadata = IPTCMetadata()
        
        if headline:
            metadata.iptc_metadata.headline = headline
        if caption:
            metadata.iptc_metadata.caption = caption
        if keywords:
            metadata.iptc_metadata.keywords = [k.strip() for k in keywords.split(',')]
        if copyright_notice:
            metadata.iptc_metadata.copyright_notice = copyright_notice
        if photographer_name:
            metadata.iptc_metadata.photographer = photographer_name
        
        # Update DDEX descriptor with model information
        if metadata.ddex_descriptor:
            if model_name:
                metadata.ddex_descriptor.model_name = model_name
            if agency_name:
                metadata.ddex_descriptor.agency_name = agency_name
            if photographer_name:
                metadata.ddex_descriptor.photographer = photographer_name
            if shoot_date:
                try:
                    metadata.ddex_descriptor.shoot_date = datetime.fromisoformat(shoot_date.replace('Z', '+00:00'))
                except ValueError:
                    pass
        
        # Create model release if commercial usage is intended
        if usage_rights in ["commercial", "unrestricted"] and model_name and photographer_name:
            if not shoot_date:
                raise HTTPException(status_code=400, detail="Shoot date required for commercial usage")
            
            try:
                shoot_datetime = datetime.fromisoformat(shoot_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid shoot date format")
            
            release_data = {
                "model_name": model_name,
                "agency_name": agency_name,
                "photographer_name": photographer_name,
                "shoot_date": shoot_datetime,
                "usage_rights": usage_rights,
                "territory_rights": territory_rights,
                "duration_rights": duration_rights,
                "exclusive": exclusive,
                "signed_date": datetime.now()
            }
            
            model_release = await image_service.create_model_release(release_data)
            metadata.model_release = model_release
        
        # Validate for commercial usage if applicable
        validation_result = None
        if usage_rights in ["commercial", "unrestricted"]:
            validation_result = await image_service.validate_commercial_usage(metadata)
            if not validation_result["approved"]:
                metadata.status = "requires_review"
                metadata.validation_errors = validation_result["issues"]
        
        # Store metadata in database
        metadata_id = await image_service.store_image_metadata(metadata)
        
        # Initialize response data
        response_data = {
            "success": True,
            "metadata_id": metadata_id,
            "file_info": {
                "filename": file.filename,
                "size": len(file_content),
                "dimensions": f"{metadata.width}x{metadata.height}",
                "format": metadata.mime_type
            },
            "metadata_summary": {
                "iptc_fields": len(metadata.iptc_metadata.dict()) if metadata.iptc_metadata else 0,
                "exif_fields": len(metadata.exif_data),
                "ddex_compliant": metadata.ddex_descriptor is not None,
                "has_model_release": metadata.model_release is not None,
                "usage_rights": metadata.usage_rights,
                "commercial_approved": validation_result["approved"] if validation_result else None
            },
            "validation": validation_result
        }

        # Process Web3 NFT minting if enabled
        if enable_nft and enable_nft.lower() == "true":
            try:
                # Parse royalty recipients
                recipients = []
                if royalty_recipients:
                    recipients_data = json.loads(royalty_recipients)
                    for recipient_data in recipients_data:
                        recipients.append(RoyaltyRecipient(
                            address=recipient_data["address"],
                            percentage=int(recipient_data["percentage"]),
                            role=recipient_data["role"]
                        ))
                
                # Create mint request
                mint_request = NFTMintRequest(
                    to_address=current_user.wallet_address or "0x" + "0" * 40,  # Default address if not set
                    token_uri=f"ipfs://metadata_placeholder_{metadata_id}",  # Would be actual IPFS URI
                    license_type=usage_rights,
                    duration=int(duration_rights.replace("_years", "").replace("perpetual", "0")),
                    restrictions=license_terms or "",
                    commercial_use=usage_rights in ["commercial", "unrestricted"],
                    max_resolution=int(max_resolution) if max_resolution != "unlimited" else 999999,
                    base_pricing=Decimal(base_pricing) if base_pricing else Decimal("0"),
                    royalty_recipients=recipients if recipients else [
                        RoyaltyRecipient(
                            address=current_user.wallet_address or "0x" + "0" * 40,
                            percentage=100,
                            role="creator"
                        )
                    ]
                )
                
                # Mint NFT
                nft_result = await web3_service.mint_nft_license(
                    network=blockchain,
                    token_standard=token_standard,
                    mint_request=mint_request,
                    user_id=current_user.id
                )
                
                response_data["nft_minting"] = nft_result
                
            except Exception as e:
                logger.error(f"NFT minting failed: {str(e)}")
                response_data["nft_minting"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Process DAO proposal if enabled
        if enable_dao and enable_dao.lower() == "true":
            try:
                proposal_request = DAOProposalRequest(
                    proposal_type=proposal_type,
                    title=f"License Terms Approval: {file.filename}",
                    description=f"Approve licensing terms for {file.filename} with {usage_rights} usage rights",
                    voting_period=voting_period,
                    proposal_data={
                        "metadata_id": metadata_id,
                        "filename": file.filename,
                        "usage_rights": usage_rights,
                        "base_pricing": base_pricing,
                        "max_resolution": max_resolution,
                        "photographer": photographer_name,
                        "agency": agency_name
                    }
                )
                
                dao_result = await web3_service.create_dao_proposal(
                    network=blockchain,
                    proposal_request=proposal_request,
                    proposer_user_id=current_user.id
                )
                
                response_data["dao_proposal"] = dao_result
                
            except Exception as e:
                logger.error(f"DAO proposal creation failed: {str(e)}")
                response_data["dao_proposal"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Error processing image upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@image_router.post("/batch-upload")
async def batch_upload_images(
    files: List[UploadFile] = File(...),
    model_name: Optional[str] = Form(None),
    agency_name: Optional[str] = Form(None),
    photographer_name: Optional[str] = Form(None),
    shoot_date: Optional[str] = Form(None),
    usage_rights: str = Form("editorial_only"),
    territory_rights: str = Form("worldwide"),
    duration_rights: str = Form("perpetual"),
    exclusive: bool = Form(False),
    headline: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    keywords: Optional[str] = Form(None),
    copyright_notice: Optional[str] = Form(None),
    license_terms: Optional[str] = Form(None),
    content_rating: str = Form("general"),
    target_agencies: Optional[str] = Form(None),
    base_pricing: Optional[str] = Form("0"),
    max_resolution: str = Form("4000"),
    # Web3 NFT Parameters
    enable_nft: Optional[str] = Form("false"),
    blockchain: str = Form("polygon"),
    token_standard: str = Form("ERC1155"),  # Default to ERC1155 for batch
    royalty_recipients: Optional[str] = Form(None),
    # DAO Governance Parameters
    enable_dao: Optional[str] = Form("false"),
    proposal_type: str = Form("licensing_terms"),
    voting_period: int = Form(7),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple images with batch processing and Web3 integration"""
    
    if len(files) > 50:  # Reasonable batch limit
        raise HTTPException(status_code=400, detail="Maximum 50 files per batch")
    
    successful_uploads = []
    failed_uploads = []
    
    # Parse common parameters
    target_agencies_list = json.loads(target_agencies) if target_agencies else []
    
    for file in files:
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                failed_uploads.append({
                    "filename": file.filename,
                    "error": "Invalid file type"
                })
                continue
            
            # Read file content
            file_content = await file.read()
            
            # Validate file size (500MB limit)
            if len(file_content) > 500 * 1024 * 1024:
                failed_uploads.append({
                    "filename": file.filename,
                    "error": "File too large (>500MB)"
                })
                continue
            
            # Process image metadata
            metadata = await image_service.extract_metadata(file_content, file.filename)
            
            # Update metadata with form data
            if model_name:
                metadata.model_name = model_name
            if agency_name:
                metadata.agency_name = agency_name
            if photographer_name:
                metadata.photographer_name = photographer_name
            if shoot_date:
                metadata.shoot_date = datetime.fromisoformat(shoot_date).date()
            
            metadata.usage_rights = usage_rights
            metadata.territory_rights = territory_rights
            metadata.duration_rights = duration_rights
            metadata.exclusive = exclusive
            metadata.headline = headline or f"Image: {file.filename}"
            metadata.caption = caption
            metadata.keywords = keywords.split(',') if keywords else []
            metadata.copyright_notice = copyright_notice
            metadata.license_terms = license_terms
            metadata.content_rating = content_rating
            metadata.target_agencies = target_agencies_list
            
            # Generate model release if commercial usage
            if usage_rights in ['commercial', 'unrestricted'] and model_name and photographer_name:
                metadata.model_release = image_service.generate_model_release(
                    model_name, photographer_name, shoot_date
                )
            
            # Validate metadata
            validation_result = image_service.validate_commercial_usage(metadata)
            
            # Store metadata
            metadata_id = await image_service.store_image_metadata(metadata)
            
            upload_result = {
                "filename": file.filename,
                "metadata_id": metadata_id,
                "file_info": {
                    "size": len(file_content),
                    "dimensions": f"{metadata.width}x{metadata.height}",
                    "format": metadata.mime_type
                },
                "metadata_summary": {
                    "iptc_fields": len(metadata.iptc_metadata.dict()) if metadata.iptc_metadata else 0,
                    "ddex_compliant": metadata.ddex_descriptor is not None,
                    "has_model_release": metadata.model_release is not None,
                    "usage_rights": metadata.usage_rights,
                    "commercial_approved": validation_result["approved"] if validation_result else None
                },
                "validation": validation_result
            }
            
            # Add Web3 processing for batch (if enabled)
            if enable_nft and enable_nft.lower() == "true":
                try:
                    # Parse royalty recipients (same for all files in batch)
                    recipients = []
                    if royalty_recipients:
                        recipients_data = json.loads(royalty_recipients)
                        for recipient_data in recipients_data:
                            recipients.append(RoyaltyRecipient(
                                address=recipient_data["address"],
                                percentage=int(recipient_data["percentage"]),
                                role=recipient_data["role"]
                            ))
                    
                    mint_request = NFTMintRequest(
                        to_address=current_user.wallet_address or "0x" + "0" * 40,
                        token_uri=f"ipfs://batch_metadata_{metadata_id}",
                        license_type=usage_rights,
                        duration=int(duration_rights.replace("_years", "").replace("perpetual", "0")),
                        restrictions=license_terms or "",
                        commercial_use=usage_rights in ["commercial", "unrestricted"],
                        max_resolution=int(max_resolution) if max_resolution != "unlimited" else 999999,
                        base_pricing=Decimal(base_pricing) if base_pricing else Decimal("0"),
                        royalty_recipients=recipients if recipients else [
                            RoyaltyRecipient(
                                address=current_user.wallet_address or "0x" + "0" * 40,
                                percentage=100,
                                role="creator"
                            )
                        ]
                    )
                    
                    nft_result = await web3_service.mint_nft_license(
                        network=blockchain,
                        token_standard=token_standard,
                        mint_request=mint_request,
                        user_id=current_user.id
                    )
                    
                    upload_result["nft_minting"] = nft_result
                    
                except Exception as e:
                    logger.error(f"Batch NFT minting failed for {file.filename}: {str(e)}")
                    upload_result["nft_minting"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            successful_uploads.append(upload_result)
            
        except Exception as e:
            logger.error(f"Batch upload failed for {file.filename}: {str(e)}")
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    # Create DAO proposal for batch if enabled
    dao_result = None
    if enable_dao and enable_dao.lower() == "true" and successful_uploads:
        try:
            proposal_request = DAOProposalRequest(
                proposal_type=proposal_type,
                title=f"Batch License Terms Approval: {len(successful_uploads)} Images",
                description=f"Approve licensing terms for batch upload of {len(successful_uploads)} images with {usage_rights} usage rights",
                voting_period=voting_period,
                proposal_data={
                    "batch_size": len(successful_uploads),
                    "usage_rights": usage_rights,
                    "base_pricing": base_pricing,
                    "max_resolution": max_resolution,
                    "photographer": photographer_name,
                    "agency": agency_name,
                    "metadata_ids": [upload["metadata_id"] for upload in successful_uploads]
                }
            )
            
            dao_result = await web3_service.create_dao_proposal(
                network=blockchain,
                proposal_request=proposal_request,
                proposer_user_id=current_user.id
            )
            
        except Exception as e:
            logger.error(f"Batch DAO proposal creation failed: {str(e)}")
            dao_result = {
                "success": False,
                "error": str(e)
            }
    
    return {
        "success": True,
        "batch_processing": True,
        "total_files": len(files),
        "successful_uploads": len(successful_uploads),
        "failed_uploads": len(failed_uploads),
        "results": successful_uploads,
        "errors": failed_uploads,
        "dao_proposal": dao_result,
        "web3_enabled": enable_nft and enable_nft.lower() == "true"
    }


@image_router.get("/nfts")
async def get_user_nfts(
    network: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get user's minted NFT licenses"""
    try:
        nfts = await web3_service.get_user_nfts(current_user.id, network)
        return {
            "success": True,
            "nfts": nfts,
            "total": len(nfts)
        }
    except Exception as e:
        logger.error(f"Failed to get user NFTs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get NFTs: {str(e)}")


@image_router.get("/dao/proposals")
async def get_dao_proposals(
    network: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get DAO governance proposals"""
    try:
        proposals = await web3_service.get_dao_proposals(network, status)
        return {
            "success": True,
            "proposals": proposals,
            "total": len(proposals)
        }
    except Exception as e:
        logger.error(f"Failed to get DAO proposals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get proposals: {str(e)}")


@image_router.get("/agencies/{agency_id}/portfolio")
async def get_agency_portfolio(
    agency_id: str,
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get agency portfolio with role-based access"""
    try:
        # Check if user has access to agency portfolio
        # This would typically check user role/permissions
        
        portfolio = await image_service.get_agency_portfolio(agency_id, limit)
        return {
            "success": True,
            "agency_id": agency_id,
            "portfolio": portfolio,
            "total": len(portfolio)
        }
    except Exception as e:
        logger.error(f"Failed to get agency portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")

@image_router.post("/model-release")
async def create_model_release(
    model_name: str = Form(...),
    photographer_name: str = Form(...),
    agency_name: Optional[str] = Form(None),
    shoot_date: str = Form(...),
    usage_rights: str = Form(...),
    territory_rights: str = Form("worldwide"),
    duration_rights: str = Form("perpetual"),
    exclusive: bool = Form(False),
    witness_name: Optional[str] = Form(None),
    legal_guardian: Optional[str] = Form(None),
    additional_terms: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Create a standalone model release form"""
    
    try:
        shoot_datetime = datetime.fromisoformat(shoot_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid shoot date format")
    
    release_data = {
        "model_name": model_name,
        "agency_name": agency_name,
        "photographer_name": photographer_name,
        "shoot_date": shoot_datetime,
        "usage_rights": usage_rights,
        "territory_rights": territory_rights,
        "duration_rights": duration_rights,
        "exclusive": exclusive,
        "signed_date": datetime.now(),
        "witness_name": witness_name,
        "legal_guardian": legal_guardian,
        "additional_terms": additional_terms
    }
    
    try:
        model_release = await image_service.create_model_release(release_data)
        
        return {
            "success": True,
            "release_id": model_release.id,
            "model_name": model_release.model_name,
            "usage_rights": model_release.usage_rights,
            "status": model_release.status
        }
        
    except Exception as e:
        logger.error(f"Error creating model release: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating model release: {str(e)}")

@image_router.get("/metadata/{image_id}")
async def get_image_metadata(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive metadata for an image"""
    
    try:
        metadata = await image_service.get_image_metadata(image_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="Image metadata not found")
        
        # Check if user has access to this image
        if metadata.photographer_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied to this image")
        
        return {
            "metadata": metadata.dict(),
            "commercial_validation": await image_service.validate_commercial_usage(metadata) if metadata.usage_rights in ["commercial", "unrestricted"] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving image metadata: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving image metadata")

@image_router.get("/model-releases")
async def get_model_releases(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    status: Optional[str] = None
):
    """Get model releases for current user"""
    
    try:
        query = {"photographer_name": current_user.full_name or current_user.email}
        if status:
            query["status"] = status
        
        releases = []
        async for release in db.model_releases.find(query).limit(limit):
            releases.append(release)
        
        return {
            "releases": releases,
            "count": len(releases)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving model releases: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving model releases")

@image_router.post("/validate-commercial/{image_id}")
async def validate_commercial_usage(
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    """Validate image for commercial usage"""
    
    try:
        metadata = await image_service.get_image_metadata(image_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Check access
        if metadata.photographer_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access denied")
        
        validation_result = await image_service.validate_commercial_usage(metadata)
        
        return {
            "image_id": image_id,
            "validation": validation_result,
            "recommendations": [
                "Ensure model release form is complete and signed",
                "Verify copyright notice is included in IPTC metadata",
                "Confirm usage rights match intended distribution",
                "Check territory restrictions for target markets"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating commercial usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Error validating commercial usage")

@image_router.get("/metadata-standards")
async def get_metadata_standards():
    """Get information about supported metadata standards"""
    
    return {
        "standards": {
            "IPTC": {
                "description": "International Press Telecommunications Council metadata standard",
                "fields": [
                    "headline", "caption", "keywords", "category", "credit", "source",
                    "copyright_notice", "photographer", "city", "state", "country",
                    "date_created", "urgency", "object_name", "edit_status", "special_instructions"
                ],
                "required_for_commercial": ["photographer", "copyright_notice"]
            },
            "XMP": {
                "description": "Extensible Metadata Platform for rich metadata",
                "fields": [
                    "title", "description", "creator", "subject", "rights",
                    "usage_terms", "web_statement", "rating", "label"
                ],
                "required_for_commercial": ["creator", "rights", "usage_terms"]
            },
            "DDEX": {
                "description": "Digital Data Exchange for music and media industry",
                "fields": [
                    "resource_id", "usage_type", "territory", "exclusive", "duration",
                    "model_name", "agency_name", "photographer", "shoot_location", "shoot_date"
                ],
                "required_for_commercial": ["usage_type", "territory", "duration"]
            },
            "EXIF": {
                "description": "Exchangeable image file format for technical metadata",
                "fields": [
                    "camera_make", "camera_model", "lens", "focal_length",
                    "aperture", "iso", "shutter_speed", "date_time"
                ],
                "commercial_relevance": "technical_documentation"
            }
        },
        "commercial_usage_requirements": {
            "model_release": "Required for images featuring recognizable people",
            "property_release": "Required for images featuring private property",
            "copyright_notice": "Must include photographer and year",
            "usage_rights": "Must be set to 'commercial' or 'unrestricted'",
            "territory_licensing": "Must specify geographic usage rights",
            "duration": "Must specify license duration"
        },
        "supported_agencies": [
            "IMG Models", "Elite Model Management", "Ford Models",
            "Wilhelmina Models", "Next Management", "Women Management",
            "The Society Management", "Storm Models", "Premier Model Management",
            "Select Model Management", "Models.com", "LA Models",
            "New York Models", "DNA Models", "Modelwerk"
        ]
    }

@image_router.get("/user/images")
async def get_user_images(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    status: Optional[str] = None,
    usage_rights: Optional[str] = None
):
    """Get images uploaded by current user"""
    
    try:
        query = {"photographer_id": current_user.id}
        if status:
            query["status"] = status
        if usage_rights:
            query["usage_rights"] = usage_rights
        
        images = []
        async for image in db.image_metadata.find(query).sort("upload_date", -1).limit(limit):
            # Remove large fields for listing
            summary = {
                "id": image["id"],
                "file_name": image["file_name"],
                "dimensions": f"{image['width']}x{image['height']}",
                "file_size": image["file_size"],
                "mime_type": image["mime_type"],
                "upload_date": image["upload_date"],
                "usage_rights": image["usage_rights"],
                "status": image["status"],
                "has_model_release": image.get("model_release") is not None,
                "ddex_compliant": image.get("ddex_descriptor") is not None,
                "validation_errors": image.get("validation_errors", [])
            }
            images.append(summary)
        
        return {
            "images": images,
            "count": len(images),
            "filters": {
                "status": ["uploaded", "processing", "approved", "rejected", "requires_review"],
                "usage_rights": ["editorial_only", "commercial", "unrestricted"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user images: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving images")