"""
Smart Contract & Blockchain Models
Handles smart contract triggers, DAO voting, and blockchain integration
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid

class BlockchainNetwork(str, Enum):
    """Supported blockchain networks"""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"  # Binance Smart Chain
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"
    SEPOLIA = "sepolia"  # Testnet
    MUMBAI = "mumbai"    # Polygon testnet

class ContractType(str, Enum):
    """Types of smart contracts"""
    LICENSING = "licensing"
    DAO_VOTING = "dao_voting"
    ROYALTY_SPLIT = "royalty_split"
    NFT_MINTING = "nft_minting"
    ESCROW = "escrow"
    GOVERNANCE = "governance"
    REVENUE_SHARING = "revenue_sharing"
    RIGHTS_MANAGEMENT = "rights_management"

class TriggerCondition(str, Enum):
    """Conditions that trigger smart contracts"""
    VALIDATION_SUCCESS = "validation_success"
    COMPLIANCE_APPROVED = "compliance_approved"
    RIGHTS_VERIFIED = "rights_verified"
    METADATA_VALIDATED = "metadata_validated"
    BATCH_COMPLETED = "batch_completed"
    MANUAL_TRIGGER = "manual_trigger"
    SCHEDULED_TRIGGER = "scheduled_trigger"
    THRESHOLD_REACHED = "threshold_reached"

class ContractStatus(str, Enum):
    """Smart contract execution status"""
    PENDING = "pending"
    DEPLOYED = "deployed"
    TRIGGERED = "triggered"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class VoteType(str, Enum):
    """Types of DAO votes"""
    LICENSING_APPROVAL = "licensing_approval"
    CONTENT_ACCEPTANCE = "content_acceptance"
    ROYALTY_DISTRIBUTION = "royalty_distribution"
    PLATFORM_GOVERNANCE = "platform_governance"
    PARAMETER_CHANGE = "parameter_change"
    EMERGENCY_ACTION = "emergency_action"

class VoteStatus(str, Enum):
    """DAO vote status"""
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class TokenStandard(str, Enum):
    """Token standards for smart contracts"""
    ERC20 = "erc20"      # Fungible tokens
    ERC721 = "erc721"    # NFTs
    ERC1155 = "erc1155"  # Multi-token standard
    ERC2981 = "erc2981"  # Royalty standard

class SmartContractTemplate(BaseModel):
    """Smart contract template configuration"""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_name: str
    contract_type: ContractType
    description: str
    
    # Blockchain Configuration
    supported_networks: List[BlockchainNetwork]
    default_network: BlockchainNetwork
    gas_limit: Optional[int] = None
    gas_price_gwei: Optional[float] = None
    
    # Contract Parameters
    contract_abi: Dict[str, Any]  # Application Binary Interface
    bytecode: Optional[str] = None
    constructor_params: List[Dict[str, Any]] = []
    
    # Trigger Configuration
    trigger_conditions: List[TriggerCondition]
    auto_trigger: bool = True
    requires_approval: bool = False
    
    # Licensing Specific
    licensing_terms: Optional[Dict[str, Any]] = None
    royalty_percentage: Optional[float] = None
    
    # DAO Voting Specific
    voting_period_hours: Optional[int] = 168  # 1 week default
    quorum_percentage: Optional[float] = 51.0
    proposal_threshold: Optional[int] = 1000  # Token amount to propose
    
    # Compliance Requirements
    requires_metadata_validation: bool = True
    requires_rights_verification: bool = True
    minimum_compliance_score: float = 85.0
    
    # Template Metadata
    is_audited: bool = False
    audit_report_url: Optional[str] = None
    created_by: str = "system"
    created_date: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"

class SmartContractInstance(BaseModel):
    """Deployed smart contract instance"""
    contract_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    contract_name: str
    
    # Blockchain Details
    network: BlockchainNetwork
    contract_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    
    # Content Association
    content_id: str
    isrc: Optional[str] = None
    user_id: str
    
    # Contract Configuration
    constructor_args: Dict[str, Any] = {}
    contract_params: Dict[str, Any] = {}
    
    # Status and Lifecycle
    status: ContractStatus = ContractStatus.PENDING
    deployed_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    
    # Trigger Information
    trigger_condition: TriggerCondition
    triggered_by: Optional[str] = None
    trigger_data: Dict[str, Any] = {}
    
    # Gas and Fees
    deployment_gas_used: Optional[int] = None
    execution_gas_used: Optional[int] = None
    total_gas_cost_eth: Optional[float] = None
    
    # Results
    execution_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DAOProposal(BaseModel):
    """DAO proposal for voting"""
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_title: str
    proposal_description: str
    vote_type: VoteType
    
    # Content Association
    content_id: Optional[str] = None
    isrc: Optional[str] = None
    contract_id: Optional[str] = None
    
    # Proposer Information
    proposer_address: str
    proposer_user_id: str
    
    # Voting Configuration
    network: BlockchainNetwork
    voting_contract_address: Optional[str] = None
    
    # Voting Parameters
    voting_period_start: datetime
    voting_period_end: datetime
    quorum_required: float  # Percentage
    approval_threshold: float  # Percentage to pass
    
    # Proposal Data
    proposal_data: Dict[str, Any] = {}
    
    # Voting Results
    status: VoteStatus = VoteStatus.ACTIVE
    total_votes: int = 0
    yes_votes: int = 0
    no_votes: int = 0
    abstain_votes: int = 0
    
    # Execution
    executed: bool = False
    execution_transaction_hash: Optional[str] = None
    execution_block_number: Optional[int] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class BlockchainTransaction(BaseModel):
    """Blockchain transaction record"""
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_hash: str
    network: BlockchainNetwork
    
    # Transaction Details
    from_address: str
    to_address: str
    value_eth: float = 0.0
    gas_used: int
    gas_price_gwei: float
    transaction_fee_eth: float
    
    # Block Information
    block_number: int
    block_hash: str
    transaction_index: int
    
    # Contract Interaction
    contract_address: Optional[str] = None
    function_name: Optional[str] = None
    function_params: Dict[str, Any] = {}
    
    # BME Platform Context
    content_id: Optional[str] = None
    user_id: Optional[str] = None
    contract_id: Optional[str] = None
    proposal_id: Optional[str] = None
    
    # Status
    status: str = "confirmed"  # pending, confirmed, failed
    confirmation_count: int = 0
    
    # Timestamps
    submitted_at: datetime = Field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None

class LicensingContract(BaseModel):
    """Automatic licensing contract configuration"""
    licensing_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    contract_id: str
    
    # Licensing Terms
    license_type: str  # exclusive, non-exclusive, sync, master
    territory_codes: List[str]
    usage_rights: List[str]
    
    # Financial Terms
    upfront_fee_eth: Optional[float] = None
    royalty_percentage: float
    minimum_guarantee_eth: Optional[float] = None
    
    # Contract Parties
    licensor_address: str
    licensee_address: Optional[str] = None  # Auto-filled when licensed
    
    # Terms and Conditions
    license_duration_months: Optional[int] = None  # None = perpetual
    exclusive: bool = False
    transferable: bool = False
    sub_licensable: bool = False
    
    # Auto-Trigger Configuration
    auto_approve_threshold: Optional[float] = None  # Compliance score
    requires_dao_vote: bool = False
    dao_approval_threshold: float = 60.0  # Percentage
    
    # Execution Status
    is_active: bool = True
    triggered: bool = False
    licensed: bool = False
    
    # Contract Execution
    trigger_transaction_hash: Optional[str] = None
    license_transaction_hash: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TriggerRule(BaseModel):
    """Rules for automatic contract triggering"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str
    description: str
    
    # Trigger Conditions
    trigger_condition: TriggerCondition
    
    # Validation Requirements
    min_validation_score: float = 85.0
    requires_rights_compliance: bool = True
    requires_territory_clearance: bool = True
    required_metadata_fields: List[str] = []
    
    # Contract Actions
    contract_templates: List[str] = []  # Template IDs to trigger
    create_dao_proposal: bool = False
    auto_deploy: bool = True
    
    # Filtering Criteria
    user_whitelist: List[str] = []  # User IDs
    territory_filter: List[str] = []  # Territory codes
    usage_type_filter: List[str] = []  # Usage types
    content_type_filter: List[str] = []  # Media types
    
    # Advanced Logic
    custom_conditions: Dict[str, Any] = {}  # JSON logic
    cooldown_hours: int = 24  # Prevent spam triggering
    
    # Status
    is_active: bool = True
    trigger_count: int = 0
    last_triggered: Optional[datetime] = None
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class Web3Configuration(BaseModel):
    """Web3 and blockchain configuration"""
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Network Configuration
    default_network: BlockchainNetwork = BlockchainNetwork.POLYGON
    supported_networks: List[BlockchainNetwork] = [
        BlockchainNetwork.ETHEREUM,
        BlockchainNetwork.POLYGON,
        BlockchainNetwork.BASE
    ]
    
    # RPC Endpoints
    rpc_endpoints: Dict[str, str] = {
        "ethereum": "https://eth-mainnet.g.alchemy.com/v2/",
        "polygon": "https://polygon-mainnet.g.alchemy.com/v2/",
        "base": "https://mainnet.base.org",
        "sepolia": "https://eth-sepolia.g.alchemy.com/v2/",
        "mumbai": "https://polygon-mumbai.g.alchemy.com/v2/"
    }
    
    # Gas Configuration
    default_gas_limit: int = 500000
    max_gas_price_gwei: float = 100.0
    gas_multiplier: float = 1.1  # Safety margin
    
    # Contract Deployment
    deployer_private_key: Optional[str] = None  # Encrypted
    deployer_address: Optional[str] = None
    
    # DAO Configuration
    dao_token_address: Optional[str] = None
    dao_governance_address: Optional[str] = None
    dao_treasury_address: Optional[str] = None
    
    # Platform Fees
    platform_fee_percentage: float = 2.5
    platform_fee_address: Optional[str] = None
    
    # Security
    multi_sig_required: bool = True
    multi_sig_threshold: int = 2
    multi_sig_addresses: List[str] = []
    
    # Monitoring
    enable_transaction_monitoring: bool = True
    webhook_urls: List[str] = []
    
    # Metadata
    updated_at: datetime = Field(default_factory=datetime.now)

# Pre-defined contract templates
DEFAULT_CONTRACT_TEMPLATES = {
    "auto_licensing": SmartContractTemplate(
        template_name="Automatic Music Licensing",
        contract_type=ContractType.LICENSING,
        description="Automatically deploys licensing contract when content passes validation",
        supported_networks=[BlockchainNetwork.POLYGON, BlockchainNetwork.ETHEREUM],
        default_network=BlockchainNetwork.POLYGON,
        trigger_conditions=[TriggerCondition.VALIDATION_SUCCESS, TriggerCondition.COMPLIANCE_APPROVED],
        licensing_terms={
            "default_royalty": 10.0,
            "exclusive_premium": 25.0,
            "territory_multiplier": {"US": 1.0, "EU": 0.8, "GLOBAL": 1.5}
        },
        requires_metadata_validation=True,
        requires_rights_verification=True,
        minimum_compliance_score=90.0,
        contract_abi={
            "functions": [
                {"name": "createLicense", "inputs": [], "outputs": []},
                {"name": "executeLicense", "inputs": [], "outputs": []},
                {"name": "withdrawRoyalties", "inputs": [], "outputs": []}
            ]
        }
    ),
    
    "dao_content_vote": SmartContractTemplate(
        template_name="DAO Content Approval",
        contract_type=ContractType.DAO_VOTING,
        description="Creates DAO proposal for community voting on content acceptance",
        supported_networks=[BlockchainNetwork.POLYGON, BlockchainNetwork.BASE],
        default_network=BlockchainNetwork.POLYGON,
        trigger_conditions=[TriggerCondition.VALIDATION_SUCCESS],
        voting_period_hours=168,  # 1 week
        quorum_percentage=25.0,
        proposal_threshold=100,  # BME tokens required to propose
        requires_metadata_validation=True,
        minimum_compliance_score=85.0,
        contract_abi={
            "functions": [
                {"name": "createProposal", "inputs": [], "outputs": []},
                {"name": "vote", "inputs": [], "outputs": []},
                {"name": "executeProposal", "inputs": [], "outputs": []}
            ]
        }
    ),
    
    "royalty_split": SmartContractTemplate(
        template_name="Automatic Royalty Split",
        contract_type=ContractType.ROYALTY_SPLIT,
        description="Automatically distributes royalties among rights holders",
        supported_networks=[BlockchainNetwork.POLYGON, BlockchainNetwork.ETHEREUM],
        default_network=BlockchainNetwork.POLYGON,
        trigger_conditions=[TriggerCondition.RIGHTS_VERIFIED],
        requires_rights_verification=True,
        minimum_compliance_score=95.0,
        contract_abi={
            "functions": [
                {"name": "addBeneficiary", "inputs": [], "outputs": []},
                {"name": "distributeRoyalties", "inputs": [], "outputs": []},
                {"name": "claimRoyalties", "inputs": [], "outputs": []}
            ]
        }
    ),
    
    "nft_minting": SmartContractTemplate(
        template_name="Music NFT Minting",
        contract_type=ContractType.NFT_MINTING,
        description="Mints NFT for validated music content",
        supported_networks=[BlockchainNetwork.ETHEREUM, BlockchainNetwork.POLYGON, BlockchainNetwork.BASE],
        default_network=BlockchainNetwork.BASE,
        trigger_conditions=[TriggerCondition.COMPLIANCE_APPROVED],
        requires_metadata_validation=True,
        requires_rights_verification=True,
        minimum_compliance_score=88.0,
        contract_abi={
            "functions": [
                {"name": "mintMusicNFT", "inputs": [], "outputs": []},
                {"name": "setRoyalties", "inputs": [], "outputs": []},
                {"name": "transferFrom", "inputs": [], "outputs": []}
            ]
        }
    )
}

class BlockchainAnalytics(BaseModel):
    """Blockchain analytics and metrics"""
    analytics_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Contract Metrics
    total_contracts_deployed: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # DAO Metrics
    total_proposals: int = 0
    passed_proposals: int = 0
    rejected_proposals: int = 0
    average_participation_rate: float = 0.0
    
    # Financial Metrics
    total_gas_spent_eth: float = 0.0
    total_licensing_revenue_eth: float = 0.0
    total_royalties_distributed_eth: float = 0.0
    
    # Network Distribution
    network_usage: Dict[str, int] = {}
    
    # Performance Metrics
    average_deployment_time_seconds: float = 0.0
    average_execution_time_seconds: float = 0.0
    
    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.now)