"""
Smart Contract & DAO API Endpoints
Handles Web3 integration, contract deployment, and DAO voting
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import jwt

from blockchain_models import (
    BlockchainNetwork, ContractType, TriggerCondition, SmartContractTemplate,
    SmartContractInstance, DAOProposal, VoteType, LicensingContract, TriggerRule,
    DEFAULT_CONTRACT_TEMPLATES
)
from smart_contract_service import SmartContractService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contracts", tags=["Smart Contracts & DAO"])

# Global services
contract_service = None
mongo_db = None

# Authentication setup (copied to avoid circular import)
SECRET_KEY = "big-mann-entertainment-secret-key-2025"
ALGORITHM = "HS256"
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    if mongo_db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    user = await mongo_db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Get current admin user"""
    if not current_user.get('is_admin') and current_user.get('role') not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

def init_contract_service(db, services_dict):
    """Initialize smart contract service"""
    global contract_service, mongo_db
    mongo_db = db
    contract_service = SmartContractService(mongo_db=db)
    services_dict['smart_contracts'] = contract_service
    
    # Initialize Web3 connections in background
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(contract_service.initialize_web3_connections())
    except RuntimeError:
        # If no event loop is running, start one for initialization
        asyncio.run(contract_service.initialize_web3_connections())

@router.post("/trigger/validation")
async def trigger_validation_contracts(
    background_tasks: BackgroundTasks,
    content_id: str = Form(...),
    validation_data: Dict[str, Any] = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Trigger smart contracts when content validation succeeds"""
    
    try:
        # Process validation triggers in background
        background_tasks.add_task(
            contract_service.process_validation_trigger,
            content_id,
            current_user.get('id'),
            validation_data
        )
        
        return {
            "success": True,
            "message": "Validation trigger processing started",
            "content_id": content_id,
            "trigger_type": "validation_success"
        }
        
    except Exception as e:
        logger.error(f"Error triggering validation contracts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger validation contracts: {str(e)}"
        )

@router.post("/trigger/compliance")
async def trigger_compliance_contracts(
    background_tasks: BackgroundTasks,
    content_id: str = Form(...),
    compliance_result: Dict[str, Any] = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Trigger smart contracts when compliance check passes"""
    
    try:
        # Process compliance triggers in background
        background_tasks.add_task(
            contract_service.process_compliance_trigger,
            content_id,
            current_user.get('id'),
            compliance_result
        )
        
        return {
            "success": True,
            "message": "Compliance trigger processing started",
            "content_id": content_id,
            "trigger_type": "compliance_approved"
        }
        
    except Exception as e:
        logger.error(f"Error triggering compliance contracts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger compliance contracts: {str(e)}"
        )

@router.post("/deploy")
async def deploy_contract(
    template_name: str = Form(...),
    content_id: str = Form(...),
    network: str = Form("polygon"),
    constructor_params: Optional[Dict[str, Any]] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Manually deploy smart contract from template"""
    
    try:
        # Validate network
        try:
            blockchain_network = BlockchainNetwork(network)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid network: {network}"
            )
        
        # Get template
        template = DEFAULT_CONTRACT_TEMPLATES.get(template_name)
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Contract template '{template_name}' not found"
            )
        
        # Prepare trigger data
        trigger_data = {
            "content_id": content_id,
            "user_id": current_user.get('id'),
            "manual_deployment": True,
            "constructor_params": constructor_params or {}
        }
        
        # Deploy contract
        contract_id = await contract_service.deploy_contract_from_template(
            template, content_id, current_user.get('id'), trigger_data
        )
        
        if contract_id:
            return {
                "success": True,
                "message": "Contract deployed successfully",
                "contract_id": contract_id,
                "template_name": template_name,
                "network": network
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Contract deployment failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying contract: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deploy contract: {str(e)}"
        )

@router.post("/execute/{contract_id}")
async def execute_contract_function(
    contract_id: str,
    function_name: str = Form(...),
    parameters: Optional[Dict[str, Any]] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Execute function on deployed smart contract"""
    
    try:
        success = await contract_service.execute_contract_function(
            contract_id=contract_id,
            function_name=function_name,
            params=parameters or {},
            user_id=current_user.get('id')
        )
        
        if success:
            return {
                "success": True,
                "message": f"Function '{function_name}' executed successfully",
                "contract_id": contract_id,
                "function_name": function_name
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Function execution failed: {function_name}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing contract function: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute contract function: {str(e)}"
        )

@router.get("/templates")
async def get_contract_templates():
    """Get available smart contract templates"""
    
    try:
        templates = {}
        
        for template_name, template in DEFAULT_CONTRACT_TEMPLATES.items():
            templates[template_name] = {
                "name": template.template_name,
                "type": template.contract_type.value,
                "description": template.description,
                "supported_networks": [network.value for network in template.supported_networks],
                "default_network": template.default_network.value,
                "trigger_conditions": [condition.value for condition in template.trigger_conditions],
                "auto_trigger": template.auto_trigger,
                "requires_approval": template.requires_approval,
                "requires_metadata_validation": template.requires_metadata_validation,
                "requires_rights_verification": template.requires_rights_verification,
                "minimum_compliance_score": template.minimum_compliance_score,
                "is_audited": template.is_audited,
                "version": template.version
            }
            
            # Add type-specific information
            if template.contract_type == ContractType.LICENSING and template.licensing_terms:
                templates[template_name]["licensing_info"] = {
                    "default_royalty": template.licensing_terms.get("default_royalty"),
                    "royalty_percentage": template.royalty_percentage
                }
            
            if template.contract_type == ContractType.DAO_VOTING:
                templates[template_name]["voting_info"] = {
                    "voting_period_hours": template.voting_period_hours,
                    "quorum_percentage": template.quorum_percentage,
                    "proposal_threshold": template.proposal_threshold
                }
        
        return {
            "success": True,
            "contract_templates": templates,
            "total_count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Error getting contract templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get contract templates: {str(e)}"
        )

@router.get("/instances")
async def get_user_contracts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get user's smart contract instances"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Build query
        query = {"user_id": current_user.get('id')}
        if status_filter:
            query["status"] = status_filter
        
        # Get total count
        total_count = await mongo_db["smart_contract_instances"].count_documents(query)
        
        # Get paginated results
        cursor = mongo_db["smart_contract_instances"].find(query).sort("created_at", -1).skip(offset).limit(limit)
        contracts = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id and format response
        for contract in contracts:
            contract.pop("_id", None)
        
        return {
            "success": True,
            "contracts": contracts,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user contracts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user contracts: {str(e)}"
        )

@router.get("/instance/{contract_id}")
async def get_contract_details(
    contract_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about specific contract instance"""
    
    try:
        contract_instance = await contract_service._load_contract_instance(contract_id)
        
        if not contract_instance:
            raise HTTPException(
                status_code=404,
                detail="Contract not found"
            )
        
        # Check ownership (users can only see their own contracts unless admin)
        if (contract_instance.user_id != current_user.get('id') and 
            not current_user.get('is_admin')):
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        return {
            "success": True,
            "contract": contract_instance.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting contract details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get contract details: {str(e)}"
        )

# DAO Voting Endpoints

@router.post("/dao/proposal")
async def create_dao_proposal(
    title: str = Form(...),
    description: str = Form(...),
    vote_type: str = Form(...),
    content_id: Optional[str] = Form(None),
    voting_period_hours: int = Form(168),
    current_user: dict = Depends(get_current_user)
):
    """Create new DAO proposal"""
    
    try:
        # Validate vote type
        try:
            dao_vote_type = VoteType(vote_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid vote type: {vote_type}"
            )
        
        # Create proposal using service
        proposal_id = await contract_service.create_dao_proposal(
            content_id or f"manual_proposal_{datetime.now().timestamp()}",
            current_user.get('id'),
            {
                "manual_proposal": True,
                "proposal_title": title,
                "proposal_description": description
            },
            TriggerRule(
                rule_name="Manual Proposal",
                description="Manually created proposal",
                trigger_condition=TriggerCondition.MANUAL_TRIGGER,
                created_by=current_user.get('id')
            )
        )
        
        if proposal_id:
            return {
                "success": True,
                "message": "DAO proposal created successfully",
                "proposal_id": proposal_id,
                "voting_period_hours": voting_period_hours
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create DAO proposal"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating DAO proposal: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create DAO proposal: {str(e)}"
        )

@router.post("/dao/vote/{proposal_id}")
async def vote_on_proposal(
    proposal_id: str,
    vote_choice: str = Form(...),
    voting_power: int = Form(1),
    current_user: dict = Depends(get_current_user)
):
    """Submit vote on DAO proposal"""
    
    try:
        # Validate vote choice
        if vote_choice.lower() not in ["yes", "no", "abstain"]:
            raise HTTPException(
                status_code=400,
                detail="Vote choice must be 'yes', 'no', or 'abstain'"
            )
        
        success = await contract_service.vote_on_proposal(
            proposal_id=proposal_id,
            vote_choice=vote_choice,
            user_id=current_user.get('id'),
            voting_power=voting_power
        )
        
        if success:
            return {
                "success": True,
                "message": f"Vote '{vote_choice}' submitted successfully",
                "proposal_id": proposal_id,
                "vote_choice": vote_choice,
                "voting_power": voting_power
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to submit vote"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting vote: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit vote: {str(e)}"
        )

@router.get("/dao/proposals")
async def get_dao_proposals(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get DAO proposals with voting status"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Build query
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        # Get total count
        total_count = await mongo_db["dao_proposals"].count_documents(query)
        
        # Get paginated results
        cursor = mongo_db["dao_proposals"].find(query).sort("created_at", -1).skip(offset).limit(limit)
        proposals = await cursor.to_list(length=limit)
        
        # Format proposals for response
        formatted_proposals = []
        for proposal in proposals:
            proposal.pop("_id", None)
            
            # Calculate voting statistics
            if proposal.get("total_votes", 0) > 0:
                proposal["voting_stats"] = {
                    "approval_rate": (proposal.get("yes_votes", 0) / proposal["total_votes"]) * 100,
                    "participation_rate": proposal["total_votes"],  # Would calculate against total eligible voters
                    "time_remaining": None  # Would calculate from voting_period_end
                }
            
            formatted_proposals.append(proposal)
        
        return {
            "success": True,
            "proposals": formatted_proposals,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting DAO proposals: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get DAO proposals: {str(e)}"
        )

@router.get("/dao/proposal/{proposal_id}")
async def get_proposal_details(
    proposal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about specific DAO proposal"""
    
    try:
        proposal = await contract_service._load_dao_proposal(proposal_id)
        
        if not proposal:
            raise HTTPException(
                status_code=404,
                detail="Proposal not found"
            )
        
        return {
            "success": True,
            "proposal": proposal.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting proposal details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get proposal details: {str(e)}"
        )

# Licensing Contract Endpoints

@router.post("/licensing/create")
async def create_licensing_contract(
    content_id: str = Form(...),
    license_type: str = Form("non-exclusive"),
    territories: List[str] = Form(...),
    usage_rights: List[str] = Form(...),
    royalty_percentage: float = Form(...),
    upfront_fee_eth: Optional[float] = Form(None),
    duration_months: Optional[int] = Form(None),
    exclusive: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    """Create automatic licensing contract"""
    
    try:
        licensing_terms = {
            "license_type": license_type,
            "territories": territories,
            "usage_rights": usage_rights,
            "royalty_percentage": royalty_percentage,
            "upfront_fee_eth": upfront_fee_eth,
            "duration_months": duration_months,
            "exclusive": exclusive
        }
        
        contract_id = await contract_service.create_licensing_contract(
            content_id=content_id,
            user_id=current_user.get('id'),
            licensing_terms=licensing_terms
        )
        
        if contract_id:
            return {
                "success": True,
                "message": "Licensing contract created successfully",
                "contract_id": contract_id,
                "licensing_terms": licensing_terms
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create licensing contract"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating licensing contract: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create licensing contract: {str(e)}"
        )

@router.get("/analytics")
async def get_blockchain_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get blockchain and smart contract analytics"""
    
    try:
        analytics = await contract_service.get_analytics()
        
        return {
            "success": True,
            "blockchain_analytics": analytics.dict()
        }
        
    except Exception as e:
        logger.error(f"Error getting blockchain analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get blockchain analytics: {str(e)}"
        )

@router.get("/networks")
async def get_supported_networks():
    """Get supported blockchain networks"""
    
    try:
        networks = {}
        
        for network in BlockchainNetwork:
            networks[network.value] = {
                "name": network.value.title(),
                "type": "mainnet" if network.value not in ["sepolia", "mumbai"] else "testnet",
                "native_token": "ETH" if "ethereum" in network.value or network.value == "sepolia" 
                              else "MATIC" if "polygon" in network.value or network.value == "mumbai"
                              else "BNB" if network.value == "bsc" else "ETH"
            }
        
        return {
            "success": True,
            "supported_networks": networks,
            "default_network": "polygon"
        }
        
    except Exception as e:
        logger.error(f"Error getting supported networks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported networks: {str(e)}"
        )

# Admin endpoints
@router.get("/admin/all-contracts")
async def admin_get_all_contracts(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_admin_user)
):
    """Admin endpoint to get all smart contract instances"""
    
    try:
        if mongo_db is None:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        # Get total count
        total_count = await mongo_db["smart_contract_instances"].count_documents({})
        
        # Get paginated results
        cursor = mongo_db["smart_contract_instances"].find({}).sort("created_at", -1).skip(offset).limit(limit)
        contracts = await cursor.to_list(length=limit)
        
        # Remove MongoDB _id for response
        for contract in contracts:
            contract.pop("_id", None)
        
        return {
            "success": True,
            "contracts": contracts,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting all contracts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get all contracts: {str(e)}"
        )

@router.get("/admin/platform-analytics")
async def admin_get_platform_analytics(
    current_user: dict = Depends(get_current_admin_user)
):
    """Admin endpoint for platform-wide blockchain analytics"""
    
    try:
        analytics = await contract_service.get_analytics()
        
        # Additional platform statistics
        if mongo_db:
            # Transaction statistics
            total_transactions = await mongo_db["blockchain_transactions"].count_documents({})
            
            # Network usage
            network_pipeline = [
                {"$group": {"_id": "$network", "count": {"$sum": 1}}}
            ]
            network_usage = {}
            async for result in mongo_db["smart_contract_instances"].aggregate(network_pipeline):
                network_usage[result["_id"]] = result["count"]
            
            analytics_dict = analytics.dict()
            analytics_dict["platform_stats"] = {
                "total_blockchain_transactions": total_transactions,
                "network_distribution": network_usage
            }
            
            return {
                "success": True,
                "platform_analytics": analytics_dict
            }
        
        return {
            "success": True,
            "platform_analytics": analytics.dict()
        }
        
    except Exception as e:
        logger.error(f"Error getting platform analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get platform analytics: {str(e)}"
        )