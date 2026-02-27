"""
Core Pydantic models for the application.
Extracted from server.py for better organization.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    business_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False
    role: str = "user"
    tenant_id: Optional[str] = ""
    tenant_name: Optional[str] = ""
    last_login: Optional[datetime] = None
    login_count: int = 0
    account_status: str = "active"
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    refresh_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    business_name: Optional[str] = None
    date_of_birth: datetime
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state_province: str
    postal_code: str
    country: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: User


class TokenRefresh(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    business_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    account_status: Optional[str] = None


class BusinessIdentifiers(BaseModel):
    business_legal_name: str
    business_ein: str
    business_tin: str
    business_address: str
    business_phone: str
    business_naics_code: str
    upc_company_prefix: str
    global_location_number: str
    isrc_prefix: str
    publisher_number: str
    ipi_business: Optional[str] = None
    ipi_principal: Optional[str] = None
    ipn_number: Optional[str] = None
    dpid: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductIdentifier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    upc_full_code: str
    gtin: str
    isrc_code: Optional[str] = None
    product_category: str
    artist_name: Optional[str] = None
    album_title: Optional[str] = None
    track_title: Optional[str] = None
    release_date: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    record_label: Optional[str] = None
    publisher_name: Optional[str] = None
    publisher_number: Optional[str] = None
    songwriter_credits: Optional[str] = None
    publishing_rights: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MediaContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    content_type: str
    file_path: str
    file_size: int
    mime_type: str
    duration: Optional[float] = None
    dimensions: Optional[Dict[str, int]] = None
    tags: List[str] = []
    category: str
    price: float = 0.0
    is_published: bool = False
    is_featured: bool = False
    is_approved: bool = False
    approval_status: str = "pending"
    moderation_notes: Optional[str] = None
    download_count: int = 0
    view_count: int = 0
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MediaUpload(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    price: float = 0.0
    tags: List[str] = []


class ContentModerationAction(BaseModel):
    media_id: str
    action: str
    notes: Optional[str] = None


class Purchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    media_id: str
    amount: float
    currency: str = "usd"
    stripe_session_id: Optional[str] = None
    payment_status: str = "pending"
    commission_amount: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class DistributionTarget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    platform: str
    api_endpoint: Optional[str] = None
    credentials: Dict[str, str] = {}
    is_active: bool = True
    settings: Dict[str, Any] = {}


class ContentDistribution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    media_id: str
    target_platforms: List[str] = []
    scheduled_time: Optional[datetime] = None
    status: str = "pending"
    results: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DistributionRequest(BaseModel):
    media_id: str
    platforms: List[str]
    custom_message: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    hashtags: List[str] = []


class SocialPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    media_id: str
    platform: str
    post_content: str
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    status: str = "draft"
    platform_post_id: Optional[str] = None
    engagement_metrics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NFTCollection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    symbol: str
    owner_id: str
    blockchain_network: str
    contract_address: Optional[str] = None
    total_supply: int = 0
    royalty_percentage: float = 10.0
    floor_price: float = 0.0
    volume_traded: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NFTToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collection_id: str
    media_id: str
    token_id: Optional[int] = None
    token_uri: str
    metadata_uri: str
    blockchain_network: str
    contract_address: Optional[str] = None
    owner_wallet: Optional[str] = None
    current_price: float = 0.0
    last_sale_price: float = 0.0
    is_listed: bool = False
    marketplace: Optional[str] = None
    transaction_hash: Optional[str] = None
    minted_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SmartContract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contract_type: str
    blockchain_network: str
    contract_address: str
    abi: Dict[str, Any] = {}
    owner_id: str
    beneficiaries: List[Dict[str, Any]] = []
    is_active: bool = True
    deployed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CryptoWallet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    wallet_address: str
    blockchain_network: str
    wallet_type: str
    is_primary: bool = False
    balance: Dict[str, float] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActivityLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SystemConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    value: Any
    category: str
    description: Optional[str] = None
    is_active: bool = True
    updated_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
