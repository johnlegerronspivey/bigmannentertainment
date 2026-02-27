"""
Agency-related models extracted from server.py.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class LicenseType(str, Enum):
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    RIGHTS_MANAGED = "rights_managed"
    ROYALTY_FREE = "royalty_free"


class BlockchainNetwork(str, Enum):
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    POLYGON = "polygon"


class ContractStandard(str, Enum):
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    SPL_TOKEN = "spl_token"


class AgencyRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    business_registration_number: Optional[str] = None
    contact_info: Dict[str, Any]
    wallet_addresses: Dict[str, str]
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    operating_countries: List[str] = Field(default_factory=list)


class TalentCreationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    stage_name: Optional[str] = None
    bio: str = Field(default="", max_length=2000)
    age_range: Optional[str] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class LicenseContractRequest(BaseModel):
    asset_id: str
    talent_id: Optional[str] = None
    blockchain_network: str
    contract_standard: str
    license_type: str
    base_price: float = Field(..., gt=0)
    royalty_splits: Dict[str, float]
    usage_terms: Dict[str, Any]
    exclusivity: bool = False
    duration_months: Optional[int] = None
    territory: List[str] = Field(default_factory=lambda: ["worldwide"])


class NotificationRequest(BaseModel):
    email: str
    subject: str
    message: str
    user_name: Optional[str] = "User"
