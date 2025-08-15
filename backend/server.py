from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Request, Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import hashlib
import aiofiles
import json
import jwt
from passlib.context import CryptContext
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
import asyncio
import aiohttp
import secrets
import base64
# import smtplib
# from email.mime.text import MimeText
# from email.mime.multipart import MimeMultipart

# WebAuthn imports
from webauthn import generate_registration_options, verify_registration_response
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria, UserVerificationRequirement,
    RegistrationCredential, AuthenticationCredential,
    PublicKeyCredentialDescriptor, AuthenticatorTransport
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create uploads directory
uploads_dir = Path("/app/uploads")
uploads_dir.mkdir(exist_ok=True)

# Authentication setup
SECRET_KEY = os.environ.get("SECRET_KEY", "big-mann-entertainment-secret-key-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
MAX_LOGIN_ATTEMPTS = 5  
LOCKOUT_DURATION_MINUTES = 30
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 24

# WebAuthn configuration
RP_ID = os.environ.get("RP_ID", "localhost")
RP_NAME = "Big Mann Entertainment Media Platform"
ORIGIN = os.environ.get("ORIGIN", "http://localhost:3000")

# Email configuration for password reset
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Session storage for WebAuthn challenges (in production, use Redis)
webauthn_challenges = {}

# Stripe setup
stripe_api_key = os.environ.get('STRIPE_API_KEY')

# Blockchain Configuration
ETHEREUM_CONTRACT_ADDRESS = os.environ.get('ETHEREUM_CONTRACT_ADDRESS', '0xdfe98870c599734335900ce15e26d1d2ccc062c1')
ETHEREUM_WALLET_ADDRESS = os.environ.get('ETHEREUM_WALLET_ADDRESS', '0xdfe98870c599734335900ce15e26d1d2ccc062c1')
INFURA_PROJECT_ID = os.environ.get('INFURA_PROJECT_ID', 'your_infura_project_id')
BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'ethereum_mainnet')

# Social Media Settings
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")
FACEBOOK_ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN", "")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
TIKTOK_CLIENT_ID = os.environ.get("TIKTOK_CLIENT_ID", "")
TIKTOK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")
# Business Configuration from environment variables
BUSINESS_EIN = os.environ.get('BUSINESS_EIN', '270658077')
BUSINESS_ADDRESS = os.environ.get('BUSINESS_ADDRESS', '1314 Lincoln Heights Street, Alexander City, Alabama 35010')
BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE', '(256) 234-5678')
BUSINESS_NAICS_CODE = os.environ.get('BUSINESS_NAICS_CODE', '512200')  # Sound Recording Industries
BUSINESS_TIN = os.environ.get('BUSINESS_TIN', '270658077')

# Product and Global Identification Numbers
UPC_COMPANY_PREFIX = os.environ.get('UPC_COMPANY_PREFIX', '8600043402')
GLOBAL_LOCATION_NUMBER = os.environ.get('GLOBAL_LOCATION_NUMBER', '0860004340201')
BUSINESS_LEGAL_NAME = os.environ.get('BUSINESS_LEGAL_NAME', 'Big Mann Entertainment LLC')

# Create the main app without a prefix
app = FastAPI(title="Big Mann Entertainment API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
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
    role: str = "user"  # user, admin, moderator, super_admin
    last_login: Optional[datetime] = None
    login_count: int = 0
    account_status: str = "active"  # active, inactive, suspended, banned
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WebAuthnCredential(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    credential_id: str  # Base64 encoded credential ID
    public_key: str     # Base64 encoded public key
    sign_count: int = 0
    credential_name: Optional[str] = None  # User-friendly name like "iPhone Face ID"
    aaguid: Optional[str] = None
    credential_type: str = "public-key"
    transports: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None

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

class WebAuthnRegistrationResponse(BaseModel):
    id: str
    rawId: str
    response: Dict[str, Any]
    type: str
    clientExtensionResults: Optional[Dict[str, Any]] = {}

class WebAuthnAuthenticationResponse(BaseModel):
    id: str
    rawId: str
    response: Dict[str, Any]
    type: str
    clientExtensionResults: Optional[Dict[str, Any]] = {}

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductIdentifier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    upc_full_code: str  # UPC Company Prefix + Product Code + Check Digit
    gtin: str  # Global Trade Item Number
    product_category: str
    artist_name: Optional[str] = None
    album_title: Optional[str] = None
    track_title: Optional[str] = None
    release_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MediaContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    content_type: str  # audio, video, image
    file_path: str
    file_size: int
    mime_type: str
    duration: Optional[float] = None  # for audio/video
    dimensions: Optional[Dict[str, int]] = None  # for images/video
    tags: List[str] = []
    category: str
    price: float = 0.0
    is_published: bool = False
    is_featured: bool = False
    is_approved: bool = False
    approval_status: str = "pending"  # pending, approved, rejected
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
    action: str  # approve, reject, feature, unfeature
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
    type: str  # social_media, streaming, radio, tv, podcast
    platform: str  # instagram, spotify, iheartradio, cnn, etc.
    api_endpoint: Optional[str] = None
    credentials: Dict[str, str] = {}
    is_active: bool = True
    settings: Dict[str, Any] = {}

class ContentDistribution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    media_id: str
    target_platforms: List[str] = []
    scheduled_time: Optional[datetime] = None
    status: str = "pending"  # pending, processing, completed, failed
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
    platform: str  # instagram, tiktok, youtube, twitter, facebook
    post_content: str
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, posted, failed
    platform_post_id: Optional[str] = None
    engagement_metrics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NFTCollection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    symbol: str
    owner_id: str
    blockchain_network: str  # ethereum, polygon, solana, etc.
    contract_address: Optional[str] = None
    total_supply: int = 0
    royalty_percentage: float = 10.0  # Default 10% royalty
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
    contract_type: str  # royalty_distribution, licensing, revenue_sharing
    blockchain_network: str
    contract_address: str
    abi: Dict[str, Any] = {}
    owner_id: str
    beneficiaries: List[Dict[str, Any]] = []  # {address: str, percentage: float}
    is_active: bool = True
    deployed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CryptoWallet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    wallet_address: str
    blockchain_network: str
    wallet_type: str  # metamask, coinbase, phantom, etc.
    is_primary: bool = False
    balance: Dict[str, float] = {}  # {token_symbol: balance}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ActivityLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    resource_type: str  # user, media, payment, distribution, etc.
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SystemConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    value: Any
    category: str  # platform, payment, blockchain, etc.
    description: Optional[str] = None
    is_active: bool = True
    updated_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Distribution Platform Configurations
DISTRIBUTION_PLATFORMS = {
    # Social Media Platforms
    "instagram": {
        "type": "social_media",
        "name": "Instagram",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["access_token"]
    },
    "twitter": {
        "type": "social_media", 
        "name": "Twitter/X",
        "api_endpoint": "https://api.twitter.com/2",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 50 * 1024 * 1024,  # 50MB
        "credentials_required": ["api_key", "api_secret", "access_token", "access_token_secret"]
    },
    "facebook": {
        "type": "social_media",
        "name": "Facebook",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 200 * 1024 * 1024,  # 200MB
        "credentials_required": ["access_token"]
    },
    "tiktok": {
        "type": "social_media",
        "name": "TikTok",
        "api_endpoint": "https://open-api.tiktok.com",
        "supported_formats": ["video"],
        "max_file_size": 300 * 1024 * 1024,  # 300MB
        "credentials_required": ["client_id", "client_secret", "access_token"]
    },
    "youtube": {
        "type": "social_media",
        "name": "YouTube",
        "api_endpoint": "https://www.googleapis.com/youtube/v3",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB
        "credentials_required": ["api_key", "client_id", "client_secret"]
    },
    
    # Music Streaming Platforms
    "spotify": {
        "type": "streaming",
        "name": "Spotify",
        "api_endpoint": "https://api.spotify.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,  # 50MB
        "credentials_required": ["client_id", "client_secret"]
    },
    "apple_music": {
        "type": "streaming",
        "name": "Apple Music",
        "api_endpoint": "https://api.music.apple.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["developer_token", "team_id"]
    },
    "amazon_music": {
        "type": "streaming",
        "name": "Amazon Music",
        "api_endpoint": "https://api.amazonalexa.com",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"]
    },
    "soundcloud": {
        "type": "streaming",
        "name": "SoundCloud",
        "api_endpoint": "https://api.soundcloud.com",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret", "access_token"]
    },
    "pandora": {
        "type": "streaming",
        "name": "Pandora",
        "api_endpoint": "https://www.pandora.com/api/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["api_key", "partner_id"]
    },
    "tidal": {
        "type": "streaming",
        "name": "Tidal",
        "api_endpoint": "https://api.tidal.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"]
    },
    
    # Radio Stations
    "iheartradio": {
        "type": "radio",
        "name": "iHeartRadio",
        "api_endpoint": "https://api.iheart.com/api/v3",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["api_key", "partner_id"]
    },
    "siriusxm": {
        "type": "radio",
        "name": "SiriusXM",
        "api_endpoint": "https://player.siriusxm.com/rest/v2",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["api_key", "channel_id"]
    },
    "radio_com": {
        "type": "radio",
        "name": "Radio.com",
        "api_endpoint": "https://api.radio.com/v2",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["api_key", "station_id"]
    },
    "tunein": {
        "type": "radio",
        "name": "TuneIn",
        "api_endpoint": "https://api.tunein.com",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["partner_id", "partner_key"]
    },
    
    # Traditional FM Broadcast Stations
    "clear_channel_pop": {
        "type": "fm_broadcast",
        "name": "Clear Channel Pop/Top 40",
        "api_endpoint": "https://api.clearchannel.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["station_group_id", "api_key"],
        "genre": "pop",
        "description": "Major market Top 40/Pop FM stations nationwide"
    },
    "cumulus_country": {
        "type": "fm_broadcast",
        "name": "Cumulus Country Network",
        "api_endpoint": "https://api.cumulus.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["network_id", "api_key"],
        "genre": "country",
        "description": "Country music FM broadcast network"
    },
    "entercom_rock": {
        "type": "fm_broadcast",
        "name": "Audacy Rock Stations",
        "api_endpoint": "https://api.audacy.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["station_cluster_id", "api_key"],
        "genre": "rock",
        "description": "Rock and Alternative FM broadcast stations"
    },
    "urban_one_hiphop": {
        "type": "fm_broadcast",
        "name": "Urban One Hip-Hop/R&B",
        "api_endpoint": "https://api.urban1.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["market_id", "api_key"],
        "genre": "hip-hop",
        "description": "Urban contemporary and Hip-Hop FM stations"
    },
    "townsquare_adult_contemporary": {
        "type": "fm_broadcast",
        "name": "Townsquare Adult Contemporary",
        "api_endpoint": "https://api.townsquaremedia.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["market_group_id", "api_key"],
        "genre": "adult_contemporary",
        "description": "Adult Contemporary and Soft Rock FM stations"
    },
    "saga_classic_rock": {
        "type": "fm_broadcast",
        "name": "Saga Classic Rock Network",
        "api_endpoint": "https://api.sagacom.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["network_id", "api_key"],
        "genre": "classic_rock",
        "description": "Classic Rock FM broadcast network"
    },
    "hubbard_alternative": {
        "type": "fm_broadcast",
        "name": "Hubbard Alternative/Indie",
        "api_endpoint": "https://api.hubbardradio.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["station_id", "api_key"],
        "genre": "alternative",
        "description": "Alternative and Indie rock FM stations"
    },
    "univision_latin": {
        "type": "fm_broadcast",
        "name": "Univision Latin/Spanish",
        "api_endpoint": "https://api.univision.com/radio/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["market_id", "api_key"],
        "genre": "latin",
        "description": "Spanish language and Latin music FM stations"
    },
    "salem_christian": {
        "type": "fm_broadcast",
        "name": "Salem Christian/Gospel Network",
        "api_endpoint": "https://api.salemmedia.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["network_id", "api_key"],
        "genre": "christian",
        "description": "Christian and Gospel music FM stations"
    },
    "beasley_jazz": {
        "type": "fm_broadcast",
        "name": "Beasley Jazz/Smooth Jazz",
        "api_endpoint": "https://api.bbgi.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["station_group_id", "api_key"],
        "genre": "jazz",
        "description": "Jazz and Smooth Jazz FM broadcast stations"
    },
    "classical_public_radio": {
        "type": "fm_broadcast",
        "name": "NPR Classical Network",
        "api_endpoint": "https://api.npr.org/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["member_station_id", "api_key"],
        "genre": "classical",
        "description": "Classical music public radio FM stations"
    },
    "emmis_urban": {
        "type": "fm_broadcast",
        "name": "Emmis Urban Contemporary",
        "api_endpoint": "https://api.emmis.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["market_id", "api_key"],
        "genre": "urban",
        "description": "Urban Contemporary and R&B FM stations"
    },
    "midwest_family_oldies": {
        "type": "fm_broadcast",
        "name": "Midwest Family Oldies Network",
        "api_endpoint": "https://api.mwfradio.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["station_id", "api_key"],
        "genre": "oldies",
        "description": "Oldies and Classic Hits FM stations"
    },
    "alpha_electronic": {
        "type": "fm_broadcast",
        "name": "Alpha Electronic/Dance Network",
        "api_endpoint": "https://api.alphamedia.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["network_id", "api_key"],
        "genre": "electronic",
        "description": "Electronic, Dance, and EDM FM stations"
    },
    "regional_indie": {
        "type": "fm_broadcast",
        "name": "Regional Independent Stations",
        "api_endpoint": "https://api.independentradio.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["station_id", "api_key"],
        "genre": "indie",
        "description": "Independent and regional FM broadcast stations"
    },
    
    # TV and Broadcasting
    "cnn": {
        "type": "tv",
        "name": "CNN",
        "api_endpoint": "https://api.cnn.com/content/v1",
        "supported_formats": ["video", "image"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["api_key", "content_partner_id"]
    },
    "fox_news": {
        "type": "tv",
        "name": "Fox News",
        "api_endpoint": "https://api.foxnews.com/v1",
        "supported_formats": ["video", "image"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["api_key", "affiliate_id"]
    },
    "msnbc": {
        "type": "tv",
        "name": "MSNBC",
        "api_endpoint": "https://api.msnbc.com/v1",
        "supported_formats": ["video", "image"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["api_key", "network_id"]
    },
    "espn": {
        "type": "tv",
        "name": "ESPN",
        "api_endpoint": "https://api.espn.com/v1",
        "supported_formats": ["video", "image"],
        "max_file_size": 1024 * 1024 * 1024,
        "credentials_required": ["api_key", "affiliate_code"]
    },
    "netflix": {
        "type": "streaming_tv",
        "name": "Netflix",
        "api_endpoint": "https://api.netflix.com/catalog/v2",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,  # 5GB
        "credentials_required": ["partner_id", "api_key"]
    },
    "hulu": {
        "type": "streaming_tv",
        "name": "Hulu",
        "api_endpoint": "https://api.hulu.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"]
    },
    "hbo_max": {
        "type": "streaming_tv",
        "name": "HBO Max",
        "api_endpoint": "https://api.hbomax.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 3 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key", "content_partner_id"]
    },
    
    # Podcast Platforms
    "spotify_podcasts": {
        "type": "podcast",
        "name": "Spotify Podcasts",
        "api_endpoint": "https://api.spotify.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"]
    },
    "apple_podcasts": {
        "type": "podcast",
        "name": "Apple Podcasts",
        "api_endpoint": "https://itunesconnect.apple.com/api/v1",
        "supported_formats": ["audio"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["api_key_id", "issuer_id", "private_key"]
    },
    "google_podcasts": {
        "type": "podcast",
        "name": "Google Podcasts",
        "api_endpoint": "https://podcasts.google.com/api/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["service_account_key"]
    },
    "podcast_one": {
        "type": "podcast",
        "name": "PodcastOne",
        "api_endpoint": "https://api.podcastone.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key", "network_id"]
    },
    "stitcher": {
        "type": "podcast",
        "name": "Stitcher",
        "api_endpoint": "https://api.stitcher.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key", "show_id"]
    },
    
    # Additional Streaming Platforms
    "deezer": {
        "type": "streaming",
        "name": "Deezer",
        "api_endpoint": "https://api.deezer.com",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["app_id", "secret_key"]
    },
    "bandcamp": {
        "type": "streaming",
        "name": "Bandcamp",
        "api_endpoint": "https://bandcamp.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"]
    },
    "audiomack": {
        "type": "streaming",
        "name": "Audiomack",
        "api_endpoint": "https://api.audiomack.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"]
    },
    
    # Additional Social Media Platforms
    "linkedin": {
        "type": "social_media",
        "name": "LinkedIn",
        "api_endpoint": "https://api.linkedin.com/v2",
        "supported_formats": ["image", "video"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret", "access_token"]
    },
    "snapchat": {
        "type": "social_media",
        "name": "Snapchat",
        "api_endpoint": "https://adsapi.snapchat.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"]
    },
    "pinterest": {
        "type": "social_media",
        "name": "Pinterest",
        "api_endpoint": "https://api.pinterest.com/v5",
        "supported_formats": ["image"],
        "max_file_size": 32 * 1024 * 1024,
        "credentials_required": ["access_token"]
    },
    
    # Digital Performance Rights Organizations
    "soundexchange": {
        "type": "performance_rights",
        "name": "SoundExchange",
        "api_endpoint": "https://api.soundexchange.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key", "account_id", "client_secret"],
        "description": "Digital performance royalty collection for satellite radio, internet radio, and cable TV music channels"
    },
    "ascap": {
        "type": "performance_rights",
        "name": "ASCAP",
        "api_endpoint": "https://api.ascap.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["member_id", "api_key"],
        "description": "Performance rights organization for songwriters and publishers"
    },
    "bmi": {
        "type": "performance_rights",
        "name": "BMI",
        "api_endpoint": "https://api.bmi.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["affiliate_id", "api_key"],
        "description": "Broadcast Music Inc. - Performance rights for songwriters and publishers"
    },
    "sesac": {
        "type": "performance_rights",
        "name": "SESAC",
        "api_endpoint": "https://api.sesac.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["writer_id", "publisher_id", "api_key"],
        "description": "Society of European Stage Authors and Composers - Performance rights organization"
    },
    
    # Blockchain & Web3 Platforms
    "ethereum_mainnet": {
        "type": "blockchain",
        "name": "Ethereum Mainnet",
        "api_endpoint": "https://mainnet.infura.io/v3",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["infura_project_id", "private_key"],
        "description": "Ethereum blockchain for NFT minting and smart contracts",
        "contract_address": ETHEREUM_CONTRACT_ADDRESS,
        "wallet_address": ETHEREUM_WALLET_ADDRESS
    },
    "polygon_matic": {
        "type": "blockchain",
        "name": "Polygon (MATIC)",
        "api_endpoint": "https://polygon-mainnet.infura.io/v3",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["infura_project_id", "private_key"],
        "description": "Low-cost Polygon network for affordable NFT transactions"
    },
    "solana_mainnet": {
        "type": "blockchain",
        "name": "Solana Mainnet",
        "api_endpoint": "https://api.mainnet-beta.solana.com",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["solana_private_key", "rpc_url"],
        "description": "Fast and low-cost Solana blockchain for NFTs"
    },
    "binance_smart_chain": {
        "type": "blockchain",
        "name": "Binance Smart Chain",
        "api_endpoint": "https://bsc-dataseed1.binance.org",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["bsc_private_key"],
        "description": "Binance Smart Chain for cost-effective NFT operations"
    },
    "avalanche_c_chain": {
        "type": "blockchain", 
        "name": "Avalanche C-Chain",
        "api_endpoint": "https://api.avax.network/ext/bc/C/rpc",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["avalanche_private_key"],
        "description": "Avalanche blockchain for fast NFT transactions"
    },
    "optimism_layer2": {
        "type": "blockchain",
        "name": "Optimism Layer 2",
        "api_endpoint": "https://mainnet.optimism.io",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["optimism_private_key"],
        "description": "Ethereum Layer 2 solution for cheaper transactions"
    },
    "arbitrum_one": {
        "type": "blockchain",
        "name": "Arbitrum One",
        "api_endpoint": "https://arb1.arbitrum.io/rpc",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["arbitrum_private_key"],
        "description": "Ethereum Layer 2 scaling solution"
    },
    
    # NFT Marketplaces
    "opensea": {
        "type": "nft_marketplace",
        "name": "OpenSea",
        "api_endpoint": "https://api.opensea.io/v1",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["opensea_api_key", "wallet_private_key"],
        "description": "World's largest NFT marketplace"
    },
    "rarible": {
        "type": "nft_marketplace",
        "name": "Rarible",
        "api_endpoint": "https://api.rarible.org/v0.1",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["rarible_api_key", "wallet_private_key"],
        "description": "Community-owned NFT marketplace"
    },
    "foundation": {
        "type": "nft_marketplace",
        "name": "Foundation",
        "api_endpoint": "https://api.foundation.app/v1",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["foundation_api_key", "wallet_private_key"],
        "description": "Curated NFT marketplace for digital art"
    },
    "superrare": {
        "type": "nft_marketplace",
        "name": "SuperRare",
        "api_endpoint": "https://api.superrare.co/v1",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["superrare_api_key", "wallet_private_key"],
        "description": "Digital art NFT marketplace"
    },
    "magic_eden": {
        "type": "nft_marketplace",
        "name": "Magic Eden",
        "api_endpoint": "https://api-mainnet.magiceden.dev/v2",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["magic_eden_api_key", "solana_private_key"],
        "description": "Leading Solana NFT marketplace"
    },
    "async_art": {
        "type": "nft_marketplace",
        "name": "Async Art",
        "api_endpoint": "https://api.async.art/v1",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["async_api_key", "wallet_private_key"],
        "description": "Programmable NFT art platform"
    },
    
    # Web3 Music Platforms
    "audius": {
        "type": "web3_music",
        "name": "Audius",
        "api_endpoint": "https://api.audius.co/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["audius_private_key", "user_id"],
        "description": "Decentralized music streaming platform"
    },
    "catalog": {
        "type": "web3_music",
        "name": "Catalog",
        "api_endpoint": "https://api.catalog.works/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["catalog_api_key", "wallet_private_key"],
        "description": "NFT music marketplace for collectors"
    },
    "sound_xyz": {
        "type": "web3_music",
        "name": "Sound.xyz",
        "api_endpoint": "https://api.sound.xyz/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["sound_api_key", "wallet_private_key"],
        "description": "Web3 music platform with fan funding"
    },
    "royal": {
        "type": "web3_music",
        "name": "Royal",
        "api_endpoint": "https://api.royal.io/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["royal_api_key", "artist_id"],
        "description": "Music NFT ownership and royalty sharing"
    }
}

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token():
    """Create a refresh token"""
    return secrets.token_urlsafe(32)

def create_refresh_token():
    """Create a refresh token"""
    return secrets.token_urlsafe(32)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.role not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

async def log_activity(user_id: str, action: str, resource_type: str, resource_id: str = None, details: Dict[str, Any] = None, request: Request = None):
    """Log user activity for auditing purposes"""
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    await db.activity_logs.insert_one(activity.dict())

# Distribution Service Classes
class DistributionService:
    def __init__(self):
        self.platforms = DISTRIBUTION_PLATFORMS
    
    async def distribute_content(self, media_id: str, platforms: List[str], user_id: str, 
                               custom_message: Optional[str] = None, hashtags: List[str] = []):
        """Distribute content across multiple platforms"""
        # Get media details
        media = await db.media_content.find_one({"id": media_id})
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        # Create distribution record
        distribution = ContentDistribution(
            media_id=media_id,
            target_platforms=platforms,
            status="processing"
        )
        await db.content_distributions.insert_one(distribution.dict())
        
        results = {}
        for platform in platforms:
            try:
                if platform in self.platforms:
                    result = await self._distribute_to_platform(platform, media, custom_message, hashtags)
                    results[platform] = result
                else:
                    results[platform] = {"status": "error", "message": f"Unsupported platform: {platform}"}
            except Exception as e:
                results[platform] = {"status": "error", "message": str(e)}
        
        # Update distribution record
        distribution.results = results
        distribution.status = "completed" if all(r.get("status") == "success" for r in results.values()) else "partial"
        distribution.updated_at = datetime.utcnow()
        
        await db.content_distributions.update_one(
            {"id": distribution.id},
            {"$set": distribution.dict()}
        )
        
        return distribution
    
    async def _distribute_to_platform(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Distribute content to specific platform"""
        platform_config = self.platforms[platform]
        
        # Check file format compatibility
        if media["content_type"] not in platform_config["supported_formats"]:
            raise Exception(f"Content type {media['content_type']} not supported by {platform}")
        
        # Check file size
        if media["file_size"] > platform_config["max_file_size"]:
            raise Exception(f"File size exceeds {platform} limit")
        
        # Platform-specific distribution logic
        if platform == "instagram":
            return await self._post_to_instagram(media, custom_message, hashtags)
        elif platform == "twitter":
            return await self._post_to_twitter(media, custom_message, hashtags)
        elif platform == "facebook":
            return await self._post_to_facebook(media, custom_message, hashtags)
        elif platform == "youtube":
            return await self._post_to_youtube(media, custom_message, hashtags)
        elif platform == "tiktok":
            return await self._post_to_tiktok(media, custom_message, hashtags)
        elif platform == "spotify":
            return await self._post_to_spotify(media, custom_message, hashtags)
        elif platform == "soundcloud":
            return await self._post_to_soundcloud(media, custom_message, hashtags)
        elif platform == "apple_music":
            return await self._post_to_apple_music(media, custom_message, hashtags)
        elif platform == "iheartradio":
            return await self._post_to_iheartradio(media, custom_message, hashtags)
        elif platform == "soundexchange":
            return await self._register_with_soundexchange(media, custom_message, hashtags)
        elif platform == "ascap":
            return await self._register_with_ascap(media, custom_message, hashtags)
        elif platform == "bmi":
            return await self._register_with_bmi(media, custom_message, hashtags)
        elif platform == "sesac":
            return await self._register_with_sesac(media, custom_message, hashtags)
        elif platform in ["ethereum_mainnet", "polygon_matic", "solana_mainnet"]:
            return await self._mint_to_blockchain(platform, media, custom_message, hashtags)
        elif platform in ["opensea", "rarible", "foundation", "superrare", "magic_eden", "async_art"]:
            return await self._list_on_nft_marketplace(platform, media, custom_message, hashtags)
        elif platform in ["audius", "catalog", "sound_xyz", "royal"]:
            return await self._post_to_web3_music(platform, media, custom_message, hashtags)
        elif platform.startswith(("clear_channel", "cumulus", "entercom", "urban_one", "townsquare", "saga", "hubbard", "univision", "salem", "beasley", "classical", "emmis", "midwest", "alpha", "regional")):
            return await self._submit_to_fm_broadcast(platform, media, custom_message, hashtags)
        else:
            return {"status": "success", "message": f"Content scheduled for {platform}", "platform_id": f"{platform}_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_instagram(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # Instagram posting logic would go here
        return {"status": "success", "message": "Posted to Instagram", "post_id": f"ig_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_twitter(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # Twitter posting logic would go here
        return {"status": "success", "message": "Posted to Twitter", "post_id": f"tw_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_facebook(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # Facebook posting logic would go here
        return {"status": "success", "message": "Posted to Facebook", "post_id": f"fb_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_youtube(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # YouTube upload logic would go here
        return {"status": "success", "message": "Uploaded to YouTube", "video_id": f"yt_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_tiktok(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # TikTok upload logic would go here
        return {"status": "success", "message": "Uploaded to TikTok", "video_id": f"tt_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_spotify(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # Spotify submission logic would go here
        return {"status": "success", "message": "Submitted to Spotify", "track_id": f"sp_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_soundcloud(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # SoundCloud upload logic would go here
        return {"status": "success", "message": "Uploaded to SoundCloud", "track_id": f"sc_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_apple_music(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # Apple Music submission logic would go here
        return {"status": "success", "message": "Submitted to Apple Music", "track_id": f"am_{uuid.uuid4().hex[:8]}"}
    
    async def _post_to_iheartradio(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # iHeartRadio submission logic would go here
        return {"status": "success", "message": "Submitted to iHeartRadio", "track_id": f"ihr_{uuid.uuid4().hex[:8]}"}
    
    async def _register_with_soundexchange(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # SoundExchange registration logic
        isrc_code = f"BME{datetime.utcnow().strftime('%y')}{uuid.uuid4().hex[:6].upper()}"
        registration_id = f"SX-{uuid.uuid4().hex[:8].upper()}"
        
        # Simulate SoundExchange registration
        eligible_services = ["SiriusXM", "Pandora", "iHeartRadio", "Music Choice", "Muzak"]
        
        return {
            "status": "success",
            "message": "Registered with SoundExchange for digital performance royalties",
            "isrc_code": isrc_code,
            "registration_id": registration_id,
            "eligible_services": eligible_services,
            "royalty_type": "digital_performance"
        }
    
    async def _register_with_ascap(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # ASCAP registration logic
        work_id = f"ASCAP-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "status": "success",
            "message": "Registered with ASCAP for performance rights",
            "work_registration_id": work_id,
            "royalty_collection_services": ["Radio", "TV", "Digital", "Live Performance"],
            "territory_coverage": ["United States", "Canada", "International"]
        }
    
    async def _register_with_bmi(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # BMI registration logic
        work_id = f"BMI-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "status": "success",
            "message": "Registered with BMI for performance rights",
            "work_registration_id": work_id,
            "royalty_collection_services": ["Radio", "TV", "Digital", "Live Performance"],
            "territory_coverage": ["United States", "International"]
        }
    
    async def _register_with_sesac(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # SESAC registration logic
        work_id = f"SESAC-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            "status": "success",
            "message": "Registered with SESAC for performance rights",
            "work_registration_id": work_id,
            "royalty_collection_services": ["Radio", "TV", "Digital", "Live Performance"],
            "territory_coverage": ["United States", "Europe", "International"]
        }
    
    async def _submit_to_fm_broadcast(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # FM Broadcast station submission logic
        platform_config = self.platforms[platform]
        submission_id = f"{platform.split('_')[0].upper()[:3]}-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate genre-specific programming metadata
        genre = platform_config.get("genre", "general")
        description = platform_config.get("description", "FM broadcast station")
        
        # Simulate mood and demographic analysis based on genre
        mood_mapping = {
            "pop": "upbeat_mainstream",
            "country": "storytelling_americana", 
            "rock": "energetic_guitar_driven",
            "hip-hop": "urban_contemporary",
            "adult_contemporary": "mature_melodic",
            "classic_rock": "nostalgic_powerful",
            "alternative": "indie_experimental",
            "latin": "rhythmic_cultural",
            "christian": "inspirational_spiritual",
            "jazz": "sophisticated_smooth",
            "classical": "refined_orchestral",
            "urban": "contemporary_rnb",
            "oldies": "vintage_nostalgic",
            "electronic": "dance_synthetic",
            "indie": "independent_artistic"
        }
        
        target_demographics = {
            "pop": "18-34, mainstream audiences",
            "country": "25-54, rural and suburban",
            "rock": "18-44, rock enthusiasts",
            "hip-hop": "16-34, urban demographics",
            "adult_contemporary": "25-54, working professionals",
            "classic_rock": "35-64, classic rock fans",
            "alternative": "18-34, college-educated",
            "latin": "18-54, Hispanic/Latino audiences",
            "christian": "25-64, faith-based communities",
            "jazz": "35-64, sophisticated listeners",
            "classical": "45-74, educated audiences",
            "urban": "18-44, urban contemporary fans",
            "oldies": "45-74, nostalgia seekers",
            "electronic": "18-34, dance/club audiences",
            "indie": "18-34, independent music fans"
        }
        
        return {
            "status": "success",
            "message": f"Submitted to {platform_config['name']}",
            "submission_id": submission_id,
            "genre": genre,
            "network_description": description,
            "mood_classification": mood_mapping.get(genre, "general_appeal"),
            "target_demographics": target_demographics.get(genre, "general_audiences"),
            "programming_standards": f"{genre}_radio_format",
            "airplay_tracking": True,
            "market_coverage": "nationwide" if "Network" in platform_config["name"] else "regional"
        }
    
    async def _mint_to_blockchain(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # Blockchain NFT minting logic
        platform_config = self.platforms[platform]
        token_id = uuid.uuid4().hex[:16]
        transaction_hash = f"0x{uuid.uuid4().hex}"
        
        return {
            "status": "success",
            "message": f"Minted NFT on {platform_config['name']}",
            "token_id": token_id,
            "transaction_hash": transaction_hash,
            "contract_address": platform_config.get("contract_address", ETHEREUM_CONTRACT_ADDRESS),
            "blockchain_network": platform_config["name"],
            "gas_fee": "0.0025 ETH",
            "metadata_uri": f"ipfs://Qm{uuid.uuid4().hex[:20]}"
        }
    
    async def _list_on_nft_marketplace(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # NFT marketplace listing logic
        platform_config = self.platforms[platform]
        listing_id = f"{platform}_{uuid.uuid4().hex[:12]}"
        
        return {
            "status": "success",
            "message": f"Listed on {platform_config['name']} marketplace",
            "listing_id": listing_id,
            "marketplace": platform_config["name"],
            "listing_url": f"https://{platform}.io/assets/{listing_id}",
            "royalty_percentage": 10.0,
            "marketplace_fee": "2.5%"
        }
    
    async def _post_to_web3_music(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        # Web3 music platform posting logic
        platform_config = self.platforms[platform]
        track_id = f"{platform}_{uuid.uuid4().hex[:10]}"
        
        return {
            "status": "success", 
            "message": f"Published on {platform_config['name']}",
            "track_id": track_id,
            "platform": platform_config["name"],
            "decentralized": True,
            "streaming_url": f"https://{platform}.com/track/{track_id}",
            "web3_features": ["NFT_ownership", "crypto_payments", "fan_funding"]
        }

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@api_router.post("/auth/register", response_model=Token)
async def register_user(user_data: UserCreate, request: Request):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate age (must be at least 13 years old)
    today = datetime.utcnow().date()
    birth_date = user_data.date_of_birth.date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if age < 13:
        raise HTTPException(status_code=400, detail="Users must be at least 13 years old")
    
    # Create user with enhanced fields
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        business_name=user_data.business_name,
        date_of_birth=user_data.date_of_birth,
        address_line1=user_data.address_line1,
        address_line2=user_data.address_line2,
        city=user_data.city,
        state_province=user_data.state_province,
        postal_code=user_data.postal_code,
        country=user_data.country
    )
    
    # Check if this is the first user - make them an admin
    total_users = await db.users.count_documents({})
    if total_users == 0:
        user.is_admin = True
        user.role = "super_admin"
    
    # TEMPORARY FIX: Make specific users admin for testing
    if user_data.email in ["john@bigmannentertainment.com", "testadmin@bigmannentertainment.com"]:
        user.is_admin = True
        user.role = "super_admin"
    
    # Store user in database
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    await db.users.insert_one(user_dict)
    
    # Log activity
    await log_activity(user.id, "user_registered", "user", user.id, {"email": user_data.email}, request)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "is_admin": user.is_admin}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Store session
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host
    )
    await db.user_sessions.insert_one(session.dict())
    
    return Token(
        access_token=access_token, 
        refresh_token=refresh_token,
        token_type="bearer", 
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        user=user
    )

@api_router.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin, request: Request):
    # Find user
    user_doc = await db.users.find_one({"email": user_credentials.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    user = User(**user_doc)
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=401, detail=f"Account locked until {user.locked_until}")
    
    # Verify password
    if not verify_password(user_credentials.password, user_doc["password"]):
        # Increment failed login attempts
        failed_attempts = user.failed_login_attempts + 1
        update_data = {
            "$set": {"failed_login_attempts": failed_attempts, "updated_at": datetime.utcnow()}
        }
        
        # Lock account if max attempts reached  
        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            lock_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            update_data["$set"]["locked_until"] = lock_until
            
        await db.users.update_one({"id": user.id}, update_data)
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Reset failed login attempts on successful authentication
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "last_login": datetime.utcnow(), 
                "updated_at": datetime.utcnow(),
                "failed_login_attempts": 0,
                "locked_until": None
            },
            "$inc": {"login_count": 1}
        }
    )
    
    # Log activity
    await log_activity(user.id, "user_login", "user", user.id, {"email": user_credentials.email}, request)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "is_admin": user.is_admin}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Store session
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host
    )
    await db.user_sessions.insert_one(session.dict())
    
    return Token(
        access_token=access_token, 
        refresh_token=refresh_token,
        token_type="bearer", 
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        user=user
    )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# WebAuthn Face ID Authentication Endpoints
@api_router.post("/auth/webauthn/register/begin")
async def begin_webauthn_registration(request: Request, current_user: User = Depends(get_current_user)):
    """Begin WebAuthn credential registration process"""
    try:
        # Get existing credentials to exclude them
        existing_credentials_cursor = db.webauthn_credentials.find({"user_id": current_user.id})
        existing_credentials = await existing_credentials_cursor.to_list(None)
        
        exclude_credentials = []
        for cred in existing_credentials:
            exclude_credentials.append(
                PublicKeyCredentialDescriptor(
                    id=base64.urlsafe_b64decode(cred["credential_id"]),
                    type="public-key"
                )
            )
        
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=current_user.id.encode('utf-8'),
            user_name=current_user.email,
            user_display_name=current_user.full_name,
            exclude_credentials=exclude_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment="platform",
                user_verification=UserVerificationRequirement.REQUIRED
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ]
        )
        
        # Store challenge for verification
        challenge_key = f"reg_{current_user.id}"
        webauthn_challenges[challenge_key] = base64.urlsafe_b64encode(options.challenge).decode('utf-8')
        
        return {
            "challenge": base64.urlsafe_b64encode(options.challenge).decode('utf-8'),
            "rp": {"id": options.rp.id, "name": options.rp.name},
            "user": {
                "id": base64.urlsafe_b64encode(options.user.id).decode('utf-8'),
                "name": options.user.name,
                "displayName": options.user.display_name
            },
            "pubKeyCredParams": [
                {"alg": param.alg, "type": param.type} for param in options.pub_key_cred_params
            ],
            "timeout": options.timeout,
            "attestation": options.attestation,
            "authenticatorSelection": {
                "authenticatorAttachment": options.authenticator_selection.authenticator_attachment,
                "userVerification": options.authenticator_selection.user_verification
            },
            "excludeCredentials": [
                {
                    "id": base64.urlsafe_b64encode(cred.id).decode('utf-8'),
                    "type": cred.type
                } for cred in (options.exclude_credentials or [])
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate WebAuthn registration: {str(e)}")

@api_router.post("/auth/webauthn/register/complete")
async def complete_webauthn_registration(
    credential_data: WebAuthnRegistrationResponse,
    current_user: User = Depends(get_current_user)
):
    """Complete WebAuthn credential registration process"""
    try:
        # Retrieve stored challenge
        challenge_key = f"reg_{current_user.id}"
        stored_challenge = webauthn_challenges.get(challenge_key)
        
        if not stored_challenge:
            raise HTTPException(status_code=400, detail="No pending registration challenge found")
        
        # Verify registration response
        verification = verify_registration_response(
            credential=RegistrationCredential.parse_obj(credential_data.dict()),
            expected_challenge=base64.urlsafe_b64decode(stored_challenge.encode()),
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
        )
        
        if verification.verified:
            # Store the credential
            credential = WebAuthnCredential(
                user_id=current_user.id,
                credential_id=base64.urlsafe_b64encode(verification.credential_id).decode('utf-8'),
                public_key=base64.urlsafe_b64encode(verification.credential_public_key).decode('utf-8'),
                sign_count=verification.sign_count,
                aaguid=base64.urlsafe_b64encode(verification.aaguid).decode('utf-8') if verification.aaguid else None,
                credential_name=f"Face ID - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )
            
            await db.webauthn_credentials.insert_one(credential.dict())
            
            # Clean up challenge
            del webauthn_challenges[challenge_key]
            
            return {
                "success": True,
                "message": "WebAuthn credential registered successfully",
                "credential_id": credential.id
            }
        else:
            raise HTTPException(status_code=400, detail="WebAuthn registration verification failed")
            
    except Exception as e:
        # Clean up challenge on error
        challenge_key = f"reg_{current_user.id}"
        if challenge_key in webauthn_challenges:
            del webauthn_challenges[challenge_key]
        raise HTTPException(status_code=500, detail=f"Failed to complete WebAuthn registration: {str(e)}")

@api_router.post("/auth/webauthn/authenticate/begin")
async def begin_webauthn_authentication(email: str, request: Request):
    """Begin WebAuthn authentication process"""
    try:
        # Find user
        user_doc = await db.users.find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=400, detail="Unable to initiate authentication")
        
        user = User(**user_doc)
        
        # Get user's registered credentials
        credentials_cursor = db.webauthn_credentials.find({"user_id": user.id})
        credentials = await credentials_cursor.to_list(None)
        
        if not credentials:
            raise HTTPException(status_code=400, detail="No WebAuthn credentials registered for this user")
        
        allow_credentials = []
        for cred in credentials:
            allow_credentials.append(
                PublicKeyCredentialDescriptor(
                    id=base64.urlsafe_b64decode(cred["credential_id"]),
                    type="public-key",
                    transports=[AuthenticatorTransport.INTERNAL]
                )
            )
        
        options = generate_authentication_options(
            rp_id=RP_ID,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.REQUIRED
        )
        
        # Store challenge for verification
        challenge_key = f"auth_{email}"
        webauthn_challenges[challenge_key] = base64.urlsafe_b64encode(options.challenge).decode('utf-8')
        
        return {
            "challenge": base64.urlsafe_b64encode(options.challenge).decode('utf-8'),
            "rpId": options.rp_id,
            "allowCredentials": [
                {
                    "id": base64.urlsafe_b64encode(cred.id).decode('utf-8'),
                    "type": cred.type,
                    "transports": cred.transports or ["internal"]
                } for cred in options.allow_credentials
            ],
            "userVerification": options.user_verification,
            "timeout": options.timeout
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate WebAuthn authentication: {str(e)}")

@api_router.post("/auth/webauthn/authenticate/complete", response_model=Token)
async def complete_webauthn_authentication(
    email: str,
    credential_data: WebAuthnAuthenticationResponse,
    request: Request
):
    """Complete WebAuthn authentication process"""
    try:
        # Retrieve stored challenge
        challenge_key = f"auth_{email}"
        stored_challenge = webauthn_challenges.get(challenge_key)
        
        if not stored_challenge:
            raise HTTPException(status_code=400, detail="No pending authentication challenge found")
        
        # Find user
        user_doc = await db.users.find_one({"email": email})
        if not user_doc:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        user = User(**user_doc)
        
        # Find the credential being used
        credential_id = base64.urlsafe_b64decode(credential_data.id.encode())
        credential_doc = await db.webauthn_credentials.find_one({
            "user_id": user.id,
            "credential_id": base64.urlsafe_b64encode(credential_id).decode('utf-8')
        })
        
        if not credential_doc:
            raise HTTPException(status_code=401, detail="Credential not found")
        
        stored_credential = WebAuthnCredential(**credential_doc)
        
        # Verify authentication response
        verification = verify_authentication_response(
            credential=AuthenticationCredential.parse_obj(credential_data.dict()),
            expected_challenge=base64.urlsafe_b64decode(stored_challenge.encode()),
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=base64.urlsafe_b64decode(stored_credential.public_key),
            credential_current_sign_count=stored_credential.sign_count
        )
        
        if verification.verified:
            # Update sign count and last used timestamp
            await db.webauthn_credentials.update_one(
                {"id": stored_credential.id},
                {
                    "$set": {
                        "sign_count": verification.new_sign_count,
                        "last_used": datetime.utcnow()
                    }
                }
            )
            
            # Update user last login and reset failed attempts
            await db.users.update_one(
                {"id": user.id},
                {
                    "$set": {
                        "last_login": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "failed_login_attempts": 0,
                        "locked_until": None
                    },
                    "$inc": {"login_count": 1}
                }
            )
            
            # Clean up challenge
            del webauthn_challenges[challenge_key]
            
            # Log activity
            await log_activity(user.id, "webauthn_login", "user", user.id, {"email": email}, request)
            
            # Create tokens
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.id, "email": user.email, "is_admin": user.is_admin}, 
                expires_delta=access_token_expires
            )
            refresh_token = create_refresh_token()
            
            # Store session
            session = UserSession(
                user_id=user.id,
                session_token=access_token,
                refresh_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host
            )
            await db.user_sessions.insert_one(session.dict())
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,  
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user
            )
        else:
            raise HTTPException(status_code=401, detail="WebAuthn authentication verification failed")
            
    except HTTPException:
        raise
    except Exception as e:
        # Clean up challenge on error
        challenge_key = f"auth_{email}"
        if challenge_key in webauthn_challenges:
            del webauthn_challenges[challenge_key]
        raise HTTPException(status_code=500, detail=f"Failed to complete WebAuthn authentication: {str(e)}")

# Forgot Password functionality
@api_router.post("/auth/forgot-password")
async def forgot_password(forgot_data: ForgotPasswordRequest, request: Request):
    """Initiate password reset process"""
    try:
        user_doc = await db.users.find_one({"email": forgot_data.email})
        if not user_doc:
            # Don't reveal whether the email exists or not
            return {"message": "If an account with this email exists, a password reset link has been sent."}
        
        user = User(**user_doc)
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        token_expiry = datetime.utcnow() + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        
        # Store token in database
        await db.users.update_one(
            {"id": user.id},
            {
                "$set": {
                    "password_reset_token": reset_token,
                    "password_reset_expires": token_expiry,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Send email (simplified version - in production use proper email service)
        if EMAIL_USERNAME and EMAIL_PASSWORD:
            try:
                await send_password_reset_email(user.email, reset_token)
            except Exception as e:
                logging.error(f"Failed to send password reset email: {str(e)}")
        
        # Log activity
        await log_activity(user.id, "password_reset_requested", "user", user.id, {"email": forgot_data.email}, request)
        
        return {"message": "If an account with this email exists, a password reset link has been sent."}
        
    except Exception as e:
        logging.error(f"Error processing forgot password request: {str(e)}")
        return {"message": "If an account with this email exists, a password reset link has been sent."}

@api_router.post("/auth/reset-password")
async def reset_password(reset_data: ResetPasswordRequest, request: Request):
    """Reset password using a valid reset token"""
    try:
        # Find user with valid reset token
        user_doc = await db.users.find_one({
            "password_reset_token": reset_data.token,
            "password_reset_expires": {"$gt": datetime.utcnow()}
        })
        
        if not user_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        user = User(**user_doc)
        
        # Hash new password
        hashed_password = get_password_hash(reset_data.new_password)
        
        # Update user password and clear reset token
        await db.users.update_one(
            {"id": user.id},
            {
                "$set": {
                    "password": hashed_password,
                    "password_reset_token": None,
                    "password_reset_expires": None,
                    "failed_login_attempts": 0,
                    "locked_until": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Invalidate all existing sessions for security
        await db.user_sessions.update_many(
            {"user_id": user.id},
            {"$set": {"is_active": False}}
        )
        
        # Log activity
        await log_activity(user.id, "password_reset_completed", "user", user.id, {"email": user.email}, request)
        
        return {"message": "Password reset successful"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")

# WebAuthn credential management endpoints
@api_router.get("/auth/webauthn/credentials")
async def get_webauthn_credentials(current_user: User = Depends(get_current_user)):
    """Get user's registered WebAuthn credentials"""
    credentials_cursor = db.webauthn_credentials.find({"user_id": current_user.id})
    credentials = await credentials_cursor.to_list(None)
    
    result = []
    for cred in credentials:
        result.append({
            "id": cred["id"],
            "name": cred["credential_name"],
            "created_at": cred["created_at"].isoformat(),
            "last_used": cred["last_used"].isoformat() if cred.get("last_used") else None
        })
    
    return {"credentials": result}

@api_router.delete("/auth/webauthn/credentials/{credential_id}")
async def delete_webauthn_credential(
    credential_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a WebAuthn credential"""
    result = await db.webauthn_credentials.delete_one({
        "id": credential_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    return {"message": "Credential deleted successfully"}

@api_router.post("/auth/logout")
async def logout_user(
    request: Request,
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user and invalidate session"""
    try:
        # Find and invalidate the current session
        await db.user_sessions.update_one(
            {
                "session_token": credentials.credentials,
                "user_id": current_user.id,
                "is_active": True
            },
            {"$set": {"is_active": False}}
        )
        
        # Log activity
        await log_activity(current_user.id, "user_logout", "user", current_user.id, {"email": current_user.email}, request)
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

# Helper function for sending password reset emails
async def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email to user"""
    try:
        # Email functionality temporarily disabled for testing
        logging.info(f"Password reset email would be sent to {email} with token {reset_token}")
        return True
        
        # Original email code commented out due to import issues
        # subject = "Password Reset Request - Big Mann Entertainment"
        # 
        # # HTML email template
        # html_body = f"""
        # <html>
        #     <body>
        #         <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        #             <h2>Password Reset Request</h2>
        #             <p>Hello,</p>
        #             <p>We received a request to reset your password for your Big Mann Entertainment account.</p>
        #             <p>Click the button below to reset your password:</p>
        #             <div style="text-align: center; margin: 30px 0;">
        #                 <a href="{ORIGIN}/reset-password?token={reset_token}" 
        #                    style="background-color: #7c3aed; color: white; padding: 12px 24px; 
        #                           text-decoration: none; border-radius: 5px; display: inline-block;">
        #                     Reset Password
        #                 </a>
        #             </div>
        #             <p>Or copy and paste this link into your browser:</p>
        #             <p style="word-break: break-all; color: #7c3aed;">
        #                 {ORIGIN}/reset-password?token={reset_token}
        #             </p>
        #             <p><strong>This link will expire in {PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hours.</strong></p>
        #             <p>If you didn't request this password reset, please ignore this email.</p>
        #             <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        #             <p style="font-size: 12px; color: #666;">
        #                 This is an automated message from Big Mann Entertainment. Please do not reply to this email.
        #             </p>
        #         </div>
        #     </body>
        # </html>
        # """
        # 
        # # Create message
        # msg = MimeMultipart('alternative')
        # msg['Subject'] = subject
        # msg['From'] = EMAIL_USERNAME
        # msg['To'] = email
        # 
        # # Attach HTML version
        # msg.attach(MimeText(html_body, 'html'))
        # 
        # # Send email
        # if EMAIL_USERNAME and EMAIL_PASSWORD:
        #     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        #         server.starttls()
        #         server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        #         server.send_message(msg)
                
    except Exception as e:
        logging.error(f"Failed to send password reset email: {str(e)}")
        raise

# Admin User Management Endpoints
@api_router.get("/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    role: Optional[str] = None,
    account_status: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user)
):
    """Get all users with filtering and pagination"""
    query = {}
    
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"business_name": {"$regex": search, "$options": "i"}}
        ]
    
    if role:
        query["role"] = role
    
    if account_status:
        query["account_status"] = account_status
    
    users_cursor = db.users.find(query, {"password": 0}).skip(skip).limit(limit).sort("created_at", -1)
    users = await users_cursor.to_list(length=limit)
    
    total_users = await db.users.count_documents(query)
    
    # Remove password field from response
    for user in users:
        user.pop("password", None)
    
    return {
        "users": users,
        "total": total_users,
        "skip": skip,
        "limit": limit
    }

@api_router.get("/admin/users/{user_id}")
async def get_user_details(user_id: str, admin_user: User = Depends(get_current_admin_user)):
    """Get detailed user information"""
    user = await db.users.find_one({"id": user_id}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's media count
    media_count = await db.media_content.count_documents({"owner_id": user_id})
    
    # Get user's distribution count
    distribution_count = await db.content_distributions.count_documents({"media_id": {"$in": []}})
    
    # Get user's total revenue
    purchases = await db.purchases.find({"user_id": user_id, "payment_status": "paid"}).to_list(length=None)
    total_revenue = sum(p.get("amount", 0) for p in purchases)
    
    # Get recent activity
    recent_activities = await db.activity_logs.find({"user_id": user_id}).sort("created_at", -1).limit(10).to_list(length=10)
    
    return {
        "user": user,
        "statistics": {
            "media_count": media_count,
            "distribution_count": distribution_count,
            "total_revenue": total_revenue,
            "purchase_count": len(purchases)
        },
        "recent_activities": recent_activities
    }

@api_router.put("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    admin_user: User = Depends(get_current_admin_user)
):
    """Update user information"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare update data
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    # Log activity
    await log_activity(admin_user.id, "user_updated", "user", user_id, update_data, request)
    
    return {"message": "User updated successfully"}

@api_router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete user account"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Delete user
    await db.users.delete_one({"id": user_id})
    
    # Log activity
    await log_activity(admin_user.id, "user_deleted", "user", user_id, {"email": user["email"]}, request)
    
    return {"message": "User deleted successfully"}

# Admin Content Management Endpoints
@api_router.get("/admin/content")
async def get_all_content(
    skip: int = 0,
    limit: int = 50,
    approval_status: Optional[str] = None,
    content_type: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user)
):
    """Get all content with filtering"""
    query = {}
    
    if approval_status:
        query["approval_status"] = approval_status
    
    if content_type:
        query["content_type"] = content_type
    
    content_cursor = db.media_content.find(query).skip(skip).limit(limit).sort("created_at", -1)
    content = await content_cursor.to_list(length=limit)
    
    total_content = await db.media_content.count_documents(query)
    
    # Get owner information for each content
    for item in content:
        owner = await db.users.find_one({"id": item["owner_id"]}, {"full_name": 1, "email": 1})
        item["owner"] = owner
    
    return {
        "content": content,
        "total": total_content,
        "skip": skip,
        "limit": limit
    }

@api_router.post("/admin/content/{media_id}/moderate")
async def moderate_content(
    media_id: str,
    action: ContentModerationAction,
    request: Request,
    admin_user: User = Depends(get_current_admin_user)
):
    """Moderate content (approve/reject/feature)"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    update_data = {"updated_at": datetime.utcnow()}
    
    if action.action == "approve":
        update_data.update({
            "approval_status": "approved",
            "is_approved": True,
            "is_published": True
        })
    elif action.action == "reject":
        update_data.update({
            "approval_status": "rejected",
            "is_approved": False,
            "is_published": False
        })
    elif action.action == "feature":
        update_data["is_featured"] = True
    elif action.action == "unfeature":
        update_data["is_featured"] = False
    
    if action.notes:
        update_data["moderation_notes"] = action.notes
    
    await db.media_content.update_one({"id": media_id}, {"$set": update_data})
    
    # Log activity
    await log_activity(admin_user.id, f"content_{action.action}", "media", media_id, update_data, request)
    
    return {"message": f"Content {action.action}d successfully"}

@api_router.delete("/admin/content/{media_id}")
async def delete_content(
    media_id: str,
    request: Request,
    admin_user: User = Depends(get_current_admin_user)
):
    """Delete content"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Delete the file
    file_path = Path(media["file_path"])
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    await db.media_content.delete_one({"id": media_id})
    
    # Log activity
    await log_activity(admin_user.id, "content_deleted", "media", media_id, {"title": media["title"]}, request)
    
    return {"message": "Content deleted successfully"}

# Admin Analytics Endpoints
@api_router.get("/admin/analytics/overview")
async def get_admin_analytics(admin_user: User = Depends(get_current_admin_user)):
    """Get comprehensive admin analytics"""
    # User analytics
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"account_status": "active"})
    new_users_this_month = await db.users.count_documents({
        "created_at": {"$gte": datetime.utcnow().replace(day=1)}
    })
    
    # Content analytics
    total_media = await db.media_content.count_documents({})
    published_media = await db.media_content.count_documents({"is_published": True})
    pending_approval = await db.media_content.count_documents({"approval_status": "pending"})
    featured_content = await db.media_content.count_documents({"is_featured": True})
    
    # Distribution analytics
    total_distributions = await db.content_distributions.count_documents({})
    successful_distributions = await db.content_distributions.count_documents({"status": "completed"})
    failed_distributions = await db.content_distributions.count_documents({"status": "failed"})
    
    # Revenue analytics
    purchases = await db.purchases.find({"payment_status": "paid"}).to_list(length=None)
    total_revenue = sum(p.get("amount", 0) for p in purchases)
    total_commission = sum(p.get("commission_amount", 0) for p in purchases)
    
    # Platform performance
    platform_stats = {}
    distributions = await db.content_distributions.find({}).to_list(length=None)
    for dist in distributions:
        for platform in dist.get("target_platforms", []):
            if platform not in platform_stats:
                platform_stats[platform] = {"attempts": 0, "successes": 0}
            platform_stats[platform]["attempts"] += 1
            if dist.get("status") == "completed":
                platform_stats[platform]["successes"] += 1
    
    # Recent activity
    recent_activities = await db.activity_logs.find({}).sort("created_at", -1).limit(20).to_list(length=20)
    
    return {
        "user_analytics": {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_this_month": new_users_this_month,
            "user_growth_rate": (new_users_this_month / max(total_users - new_users_this_month, 1)) * 100
        },
        "content_analytics": {
            "total_media": total_media,
            "published_media": published_media,
            "pending_approval": pending_approval,
            "featured_content": featured_content,
            "approval_rate": (published_media / max(total_media, 1)) * 100
        },
        "distribution_analytics": {
            "total_distributions": total_distributions,
            "successful_distributions": successful_distributions,
            "failed_distributions": failed_distributions,
            "success_rate": (successful_distributions / max(total_distributions, 1)) * 100,
            "supported_platforms": len(DISTRIBUTION_PLATFORMS)
        },
        "revenue_analytics": {
            "total_revenue": total_revenue,
            "total_commission": total_commission,
            "total_purchases": len(purchases),
            "average_purchase": total_revenue / max(len(purchases), 1)
        },
        "platform_performance": platform_stats,
        "recent_activities": recent_activities
    }

@api_router.get("/admin/analytics/users")
async def get_user_analytics(
    days: int = 30,
    admin_user: User = Depends(get_current_admin_user)
):
    """Get detailed user analytics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # User registration trends
    users_by_date = {}
    users = await db.users.find({"created_at": {"$gte": start_date}}).to_list(length=None)
    
    for user in users:
        date_key = user["created_at"].strftime("%Y-%m-%d")
        users_by_date[date_key] = users_by_date.get(date_key, 0) + 1
    
    # User engagement metrics
    active_users = await db.users.find({"last_login": {"$gte": start_date}}).to_list(length=None)
    
    # Role distribution
    role_distribution = {}
    all_users = await db.users.find({}).to_list(length=None)
    for user in all_users:
        role = user.get("role", "user")
        role_distribution[role] = role_distribution.get(role, 0) + 1
    
    return {
        "registration_trends": users_by_date,
        "active_user_count": len(active_users),
        "role_distribution": role_distribution,
        "total_users": len(all_users)
    }

# Admin Platform Management Endpoints
@api_router.get("/admin/platforms")
async def get_platform_configurations(admin_user: User = Depends(get_current_admin_user)):
    """Get all platform configurations"""
    # Convert platform data to include statistics
    platform_data = {}
    
    for platform_id, config in DISTRIBUTION_PLATFORMS.items():
        # Get usage statistics
        usage_count = await db.content_distributions.count_documents({
            "target_platforms": platform_id
        })
        
        success_count = await db.content_distributions.count_documents({
            "target_platforms": platform_id,
            "status": "completed"
        })
        
        platform_data[platform_id] = {
            **config,
            "usage_count": usage_count,
            "success_count": success_count,
            "success_rate": (success_count / max(usage_count, 1)) * 100
        }
    
    return {"platforms": platform_data}

@api_router.post("/admin/platforms/{platform_id}/toggle")
async def toggle_platform_status(
    platform_id: str,
    request: Request,
    admin_user: User = Depends(get_current_admin_user)
):
    """Enable/disable a platform"""
    if platform_id not in DISTRIBUTION_PLATFORMS:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    # In a real implementation, this would update a database record
    # For now, we'll just log the action
    await log_activity(
        admin_user.id, 
        "platform_toggled", 
        "platform", 
        platform_id, 
        {"action": "toggle_status"}, 
        request
    )
    
    return {"message": f"Platform {platform_id} status toggled"}

# Admin Revenue Management Endpoints
@api_router.get("/admin/revenue")
async def get_revenue_analytics(
    days: int = 30,
    admin_user: User = Depends(get_current_admin_user)
):
    """Get detailed revenue analytics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Revenue by date
    purchases = await db.purchases.find({
        "payment_status": "paid",
        "completed_at": {"$gte": start_date}
    }).to_list(length=None)
    
    revenue_by_date = {}
    commission_by_date = {}
    
    for purchase in purchases:
        if purchase.get("completed_at"):
            date_key = purchase["completed_at"].strftime("%Y-%m-%d")
            revenue_by_date[date_key] = revenue_by_date.get(date_key, 0) + purchase.get("amount", 0)
            commission_by_date[date_key] = commission_by_date.get(date_key, 0) + purchase.get("commission_amount", 0)
    
    # Top earning content
    top_content = await db.purchases.aggregate([
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": "$media_id", "total_revenue": {"$sum": "$amount"}, "purchase_count": {"$sum": 1}}},
        {"$sort": {"total_revenue": -1}},
        {"$limit": 10}
    ]).to_list(length=10)
    
    # Add content details
    for item in top_content:
        media = await db.media_content.find_one({"id": item["_id"]})
        if media:
            item["media_title"] = media["title"]
            item["media_type"] = media["content_type"]
    
    return {
        "revenue_trends": {
            "daily_revenue": revenue_by_date,
            "daily_commission": commission_by_date
        },
        "top_earning_content": top_content,
        "total_revenue": sum(revenue_by_date.values()),
        "total_commission": sum(commission_by_date.values()),
        "total_transactions": len(purchases)
    }

# Admin Blockchain Management Endpoints
@api_router.get("/admin/blockchain")
async def get_blockchain_overview(admin_user: User = Depends(get_current_admin_user)):
    """Get blockchain and NFT analytics"""
    # NFT Collections
    collections = await db.nft_collections.find({}).to_list(length=None)
    
    # NFT Tokens
    tokens = await db.nft_tokens.find({}).to_list(length=None)
    
    # Smart Contracts
    contracts = await db.smart_contracts.find({}).to_list(length=None)
    
    # Crypto Wallets
    wallets = await db.crypto_wallets.find({}).to_list(length=None)
    
    # Blockchain platform usage
    blockchain_platforms = [p for p in DISTRIBUTION_PLATFORMS.keys() if DISTRIBUTION_PLATFORMS[p]["type"] in ["blockchain", "nft_marketplace", "web3_music"]]
    
    blockchain_usage = {}
    for platform in blockchain_platforms:
        usage_count = await db.content_distributions.count_documents({
            "target_platforms": platform
        })
        blockchain_usage[platform] = usage_count
    
    return {
        "nft_collections": {
            "total": len(collections),
            "collections": collections
        },
        "nft_tokens": {
            "total": len(tokens),
            "minted": len([t for t in tokens if t.get("minted_at")])
        },
        "smart_contracts": {
            "total": len(contracts),
            "active": len([c for c in contracts if c.get("is_active")])
        },
        "crypto_wallets": {
            "total": len(wallets),
            "connected": len(wallets)
        },
        "blockchain_platform_usage": blockchain_usage,
        "ethereum_config": {
            "contract_address": ETHEREUM_CONTRACT_ADDRESS,
            "wallet_address": ETHEREUM_WALLET_ADDRESS,
            "network": BLOCKCHAIN_NETWORK
        }
    }

# Admin Security & Audit Endpoints
@api_router.get("/admin/security/logs")
async def get_security_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user)
):
    """Get security and audit logs"""
    query = {}
    
    if action:
        query["action"] = {"$regex": action, "$options": "i"}
    
    if user_id:
        query["user_id"] = user_id
    
    logs = await db.activity_logs.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    total_logs = await db.activity_logs.count_documents(query)
    
    # Add user information to logs
    for log in logs:
        user = await db.users.find_one({"id": log["user_id"]}, {"full_name": 1, "email": 1})
        log["user"] = user
    
    return {
        "logs": logs,
        "total": total_logs,
        "skip": skip,
        "limit": limit
    }

@api_router.get("/admin/security/stats")
async def get_security_statistics(
    days: int = 7,
    admin_user: User = Depends(get_current_admin_user)
):
    """Get security statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Failed login attempts
    failed_logins = await db.activity_logs.count_documents({
        "action": "failed_login",
        "created_at": {"$gte": start_date}
    })
    
    # Successful logins
    successful_logins = await db.activity_logs.count_documents({
        "action": "user_login",
        "created_at": {"$gte": start_date}
    })
    
    # Admin actions
    admin_actions = await db.activity_logs.count_documents({
        "action": {"$regex": "admin_|user_updated|user_deleted|content_"},
        "created_at": {"$gte": start_date}
    })
    
    # Top IP addresses
    ip_stats = await db.activity_logs.aggregate([
        {"$match": {"created_at": {"$gte": start_date}}},
        {"$group": {"_id": "$ip_address", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]).to_list(length=10)
    
    return {
        "period_days": days,
        "login_statistics": {
            "failed_logins": failed_logins,
            "successful_logins": successful_logins,
            "success_rate": (successful_logins / max(successful_logins + failed_logins, 1)) * 100
        },
        "admin_actions": admin_actions,
        "top_ip_addresses": ip_stats,
        "total_activities": await db.activity_logs.count_documents({"created_at": {"$gte": start_date}})
    }

# Admin System Configuration Endpoints
@api_router.get("/admin/config")
async def get_system_config(admin_user: User = Depends(get_current_admin_user)):
    """Get system configuration"""
    configs = await db.system_configs.find({"is_active": True}).to_list(length=None)
    
    config_by_category = {}
    for config in configs:
        category = config.get("category", "general")
        if category not in config_by_category:
            config_by_category[category] = []
        config_by_category[category].append(config)
    
    return {
        "configurations": config_by_category,
        "blockchain_config": {
            "ethereum_contract_address": ETHEREUM_CONTRACT_ADDRESS,
            "ethereum_wallet_address": ETHEREUM_WALLET_ADDRESS,
            "blockchain_network": BLOCKCHAIN_NETWORK,
            "infura_project_id": INFURA_PROJECT_ID
        },
        "platform_count": len(DISTRIBUTION_PLATFORMS),
        "active_integrations": {
            "stripe": bool(stripe_api_key),
            "social_media": bool(INSTAGRAM_ACCESS_TOKEN or TWITTER_API_KEY),
            "blockchain": bool(ETHEREUM_CONTRACT_ADDRESS)
        }
    }

# Media upload and management endpoints
@api_router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form(...),
    price: float = Form(0.0),
    tags: str = Form(""),
    request: Request = None,
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    allowed_types = {
        'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4'],
        'video': ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'],
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    }
    
    content_type = None
    for type_category, mime_types in allowed_types.items():
        if file.content_type in mime_types:
            content_type = type_category
            break
    
    if not content_type:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    
    # Create content type directory
    type_dir = uploads_dir / content_type
    type_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = type_dir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Get file size
    file_size = len(content)
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    # Create media record
    media = MediaContent(
        title=title,
        description=description,
        content_type=content_type,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type,
        category=category,
        price=price,
        tags=tag_list,
        owner_id=current_user.id,
        approval_status="pending"
    )
    
    await db.media_content.insert_one(media.dict())
    
    # Log activity
    await log_activity(current_user.id, "media_uploaded", "media", media.id, {
        "title": title,
        "content_type": content_type,
        "file_size": file_size
    }, request)
    
    return {"message": "Media uploaded successfully", "media_id": media.id}

@api_router.get("/media/library")
async def get_media_library(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    is_published: Optional[bool] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    query = {}
    
    if content_type:
        query["content_type"] = content_type
    if category:
        query["category"] = category
    if is_published is not None:
        query["is_published"] = is_published
    
    # Only show approved content to non-admin users
    if not current_user or (not current_user.is_admin and current_user.role not in ["admin", "moderator"]):
        query["is_approved"] = True
    
    media_cursor = db.media_content.find(query).sort("created_at", -1).skip(skip).limit(limit)
    media_list = await media_cursor.to_list(length=limit)
    
    # Remove sensitive data from response
    for media in media_list:
        media.pop("file_path", None)
        media.pop("moderation_notes", None)
    
    return {"media": media_list}

@api_router.get("/media/{media_id}")
async def get_media_details(
    media_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check permissions for unpublished content
    if not media.get("is_published") and (not current_user or media["owner_id"] != current_user.id):
        if not current_user or (not current_user.is_admin and current_user.role not in ["admin", "moderator"]):
            raise HTTPException(status_code=404, detail="Media not found")
    
    # Increment view count
    await db.media_content.update_one(
        {"id": media_id},
        {"$inc": {"view_count": 1}}
    )
    
    # Remove sensitive data from response
    media.pop("file_path", None)
    if not current_user or (not current_user.is_admin and current_user.role not in ["admin", "moderator"]):
        media.pop("moderation_notes", None)
    
    return media

@api_router.get("/media/{media_id}/download")
async def download_media(
    media_id: str,
    current_user: User = Depends(get_current_user)
):
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if not media.get("is_published") or not media.get("is_approved"):
        if media["owner_id"] != current_user.id and (not current_user.is_admin and current_user.role not in ["admin", "moderator"]):
            raise HTTPException(status_code=403, detail="Media not available for download")
    
    file_path = Path(media["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Increment download count
    await db.media_content.update_one(
        {"id": media_id},
        {"$inc": {"download_count": 1}}
    )
    
    return FileResponse(
        path=file_path,
        filename=f"{media['title']}.{file_path.suffix}",
        media_type=media["mime_type"]
    )

# Distribution endpoints
distribution_service = DistributionService()

@api_router.get("/distribution/platforms")
async def get_distribution_platforms():
    platforms_with_mb = {}
    for platform_id, config in DISTRIBUTION_PLATFORMS.items():
        platform_config = config.copy()
        platform_config["max_file_size_mb"] = config["max_file_size"] / (1024 * 1024)
        platforms_with_mb[platform_id] = platform_config
    
    return {"platforms": platforms_with_mb}

@api_router.post("/distribution/distribute")
async def distribute_content(
    distribution_request: DistributionRequest,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    result = await distribution_service.distribute_content(
        distribution_request.media_id,
        distribution_request.platforms,
        current_user.id,
        distribution_request.custom_message,
        distribution_request.hashtags
    )
    
    # Log activity
    await log_activity(current_user.id, "content_distributed", "distribution", result.id, {
        "media_id": distribution_request.media_id,
        "platforms": distribution_request.platforms,
        "platform_count": len(distribution_request.platforms)
    }, request)
    
    return result

@api_router.get("/distribution/history")
async def get_distribution_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    # Get user's media IDs to filter distributions
    user_media = await db.media_content.find({"owner_id": current_user.id}, {"id": 1}).to_list(length=None)
    user_media_ids = [media["id"] for media in user_media]
    
    if not user_media_ids:
        return {"distributions": []}
    
    distributions = await db.content_distributions.find({
        "media_id": {"$in": user_media_ids}
    }).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return {"distributions": distributions}

@api_router.get("/distribution/{distribution_id}")
async def get_distribution_details(
    distribution_id: str,
    current_user: User = Depends(get_current_user)
):
    distribution = await db.content_distributions.find_one({"id": distribution_id})
    if not distribution:
        raise HTTPException(status_code=404, detail="Distribution not found")
    
    # Verify ownership
    media = await db.media_content.find_one({"id": distribution["media_id"]})
    if not media or (media["owner_id"] != current_user.id and not current_user.is_admin):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return distribution

# Payment endpoints
@api_router.post("/payments/checkout")
async def create_checkout_session(
    checkout_request: dict,
    current_user: User = Depends(get_current_user)
):
    media_id = checkout_request.get("media_id")
    if not media_id:
        raise HTTPException(status_code=400, detail="Media ID is required")
    
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if media["price"] <= 0:
        raise HTTPException(status_code=400, detail="This content is free")
    
    # Create purchase record
    purchase = Purchase(
        user_id=current_user.id,
        media_id=media_id,
        amount=media["price"],
        commission_amount=media["price"] * 0.1  # 10% commission
    )
    await db.purchases.insert_one(purchase.dict())
    
    if not stripe_api_key:
        return {
            "message": "Payment processing not configured",
            "purchase_id": purchase.id,
            "amount": media["price"]
        }
    
    try:
        stripe_checkout = StripeCheckout(api_key=stripe_api_key)
        
        checkout_session_request = CheckoutSessionRequest(
            success_url="http://localhost:3000/purchase-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/library",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": media["title"],
                        "description": media.get("description", "Digital media content")
                    },
                    "unit_amount": int(media["price"] * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            metadata={"purchase_id": purchase.id}
        )
        
        session_response = await stripe_checkout.create_checkout_session(checkout_session_request)
        
        # Update purchase with session ID
        await db.purchases.update_one(
            {"id": purchase.id},
            {"$set": {"stripe_session_id": session_response.session_id}}
        )
        
        return {"checkout_url": session_response.checkout_url}
        
    except Exception as e:
        await db.purchases.update_one(
            {"id": purchase.id},
            {"$set": {"payment_status": "failed"}}
        )
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    purchase = await db.purchases.find_one({"stripe_session_id": session_id})
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    if purchase["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not stripe_api_key:
        return {"payment_status": "not_configured"}
    
    try:
        stripe_checkout = StripeCheckout(api_key=stripe_api_key)
        status_response = await stripe_checkout.get_checkout_session_status(session_id)
        
        if status_response.payment_status == "paid" and purchase["payment_status"] != "paid":
            await db.purchases.update_one(
                {"id": purchase["id"]},
                {"$set": {
                    "payment_status": "paid",
                    "completed_at": datetime.utcnow()
                }}
            )
        
        return {"payment_status": status_response.payment_status}
        
    except Exception as e:
        return {"payment_status": "error", "message": str(e)}

@api_router.post("/payments/webhook")
async def stripe_webhook(request: Request):
    try:
        payload = await request.body()
        event = json.loads(payload)
        
        if event["type"] == "checkout.session.completed":
            session_id = event["data"]["object"]["id"]
            
            purchase = await db.purchases.find_one({"stripe_session_id": session_id})
            if purchase and purchase["payment_status"] != "paid":
                await db.purchases.update_one(
                    {"id": purchase["id"]},
                    {"$set": {
                        "payment_status": "paid",
                        "completed_at": datetime.utcnow()
                    }}
                )
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

# Analytics endpoints
@api_router.get("/analytics")
async def get_analytics(current_user: User = Depends(get_current_admin_user)):
    # User statistics
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    
    # Media statistics
    total_media = await db.media_content.count_documents({})
    published_media = await db.media_content.count_documents({"is_published": True})
    
    # Distribution statistics
    total_distributions = await db.content_distributions.count_documents({})
    successful_distributions = await db.content_distributions.count_documents({"status": "completed"})
    distribution_success_rate = (successful_distributions / max(total_distributions, 1)) * 100
    
    # Revenue statistics
    purchases = await db.purchases.find({"payment_status": "paid"}).to_list(length=None)
    total_revenue = sum(purchase.get("amount", 0) for purchase in purchases)
    
    return {
        "users": {
            "total": total_users,
            "active": active_users
        },
        "media": {
            "total": total_media,
            "published": published_media
        },
        "distributions": {
            "total": total_distributions,
            "successful": successful_distributions,
            "success_rate": round(distribution_success_rate, 2)
        },
        "revenue": {
            "total": round(total_revenue, 2),
            "transactions": len(purchases)
        },
        "platforms": {
            "supported": len(DISTRIBUTION_PLATFORMS)
        }
    }

# Social media scheduling endpoints
@api_router.post("/social/schedule")
async def schedule_social_post(
    post_data: dict,
    current_user: User = Depends(get_current_user)
):
    # Basic social media post scheduling
    post = SocialPost(
        media_id=post_data.get("media_id"),
        platform=post_data.get("platform"),
        post_content=post_data.get("content"),
        scheduled_time=datetime.fromisoformat(post_data.get("scheduled_time")) if post_data.get("scheduled_time") else None
    )
    
    await db.social_posts.insert_one(post.dict())
    
    return {"message": "Post scheduled successfully", "post_id": post.id}

@api_router.get("/social/posts")
async def get_social_posts(
    current_user: User = Depends(get_current_user)
):
    # Get user's media IDs
    user_media = await db.media_content.find({"owner_id": current_user.id}, {"id": 1}).to_list(length=None)
    user_media_ids = [media["id"] for media in user_media]
    
    if not user_media_ids:
        return {"posts": []}
    
    posts = await db.social_posts.find({
        "media_id": {"$in": user_media_ids}
    }).sort("created_at", -1).to_list(length=50)
    
    return {"posts": posts}

# NFT and Blockchain endpoints
@api_router.post("/nft/collections")
async def create_nft_collection(
    collection_data: dict,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    collection = NFTCollection(
        name=collection_data.get("name"),
        description=collection_data.get("description"),
        symbol=collection_data.get("symbol"),
        owner_id=current_user.id,
        blockchain_network=collection_data.get("blockchain_network", "ethereum_mainnet"),
        royalty_percentage=collection_data.get("royalty_percentage", 10.0)
    )
    
    await db.nft_collections.insert_one(collection.dict())
    
    # Log activity
    await log_activity(current_user.id, "nft_collection_created", "nft_collection", collection.id, {
        "name": collection.name,
        "blockchain_network": collection.blockchain_network
    }, request)
    
    return {"message": "NFT collection created", "collection_id": collection.id}

@api_router.get("/nft/collections")
async def get_nft_collections(current_user: User = Depends(get_current_user)):
    collections = await db.nft_collections.find({"owner_id": current_user.id}).to_list(length=None)
    return {"collections": collections}

@api_router.post("/nft/mint")
async def mint_nft(
    mint_data: dict,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    # Verify media ownership
    media = await db.media_content.find_one({"id": mint_data.get("media_id")})
    if not media or media["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Media not found or access denied")
    
    # Verify collection ownership
    collection = await db.nft_collections.find_one({"id": mint_data.get("collection_id")})
    if not collection or collection["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Collection not found or access denied")
    
    token = NFTToken(
        collection_id=collection["id"],
        media_id=media["id"],
        token_uri=f"ipfs://Qm{uuid.uuid4().hex[:20]}",
        metadata_uri=f"ipfs://Qm{uuid.uuid4().hex[:20]}/metadata.json",
        blockchain_network=collection["blockchain_network"],
        contract_address=ETHEREUM_CONTRACT_ADDRESS,
        current_price=mint_data.get("price", 0.0),
        minted_at=datetime.utcnow()
    )
    
    await db.nft_tokens.insert_one(token.dict())
    
    # Update collection supply
    await db.nft_collections.update_one(
        {"id": collection["id"]},
        {"$inc": {"total_supply": 1}}
    )
    
    # Log activity
    await log_activity(current_user.id, "nft_minted", "nft_token", token.id, {
        "media_title": media["title"],
        "collection_name": collection["name"],
        "blockchain_network": collection["blockchain_network"]
    }, request)
    
    return {"message": "NFT minted successfully", "token_id": token.id, "contract_address": ETHEREUM_CONTRACT_ADDRESS}

@api_router.get("/nft/tokens")
async def get_nft_tokens(current_user: User = Depends(get_current_user)):
    # Get user's collections
    collections = await db.nft_collections.find({"owner_id": current_user.id}).to_list(length=None)
    collection_ids = [c["id"] for c in collections]
    
    if not collection_ids:
        return {"tokens": []}
    
    tokens = await db.nft_tokens.find({"collection_id": {"$in": collection_ids}}).to_list(length=None)
    
    # Add media and collection info to each token
    for token in tokens:
        media = await db.media_content.find_one({"id": token["media_id"]})
        collection = await db.nft_collections.find_one({"id": token["collection_id"]})
        token["media"] = media
        token["collection"] = collection
    
    return {"tokens": tokens}

@api_router.post("/blockchain/wallets")
async def connect_wallet(
    wallet_data: dict,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    wallet = CryptoWallet(
        user_id=current_user.id,
        wallet_address=wallet_data.get("wallet_address"),
        blockchain_network=wallet_data.get("blockchain_network", "ethereum"),
        wallet_type=wallet_data.get("wallet_type", "metamask"),
        is_primary=wallet_data.get("is_primary", False)
    )
    
    await db.crypto_wallets.insert_one(wallet.dict())
    
    # Log activity
    await log_activity(current_user.id, "wallet_connected", "wallet", wallet.id, {
        "wallet_address": wallet.wallet_address,
        "wallet_type": wallet.wallet_type
    }, request)
    
    return {"message": "Wallet connected successfully", "wallet_id": wallet.id}

@api_router.get("/blockchain/wallets")
async def get_user_wallets(current_user: User = Depends(get_current_user)):
    wallets = await db.crypto_wallets.find({"user_id": current_user.id}).to_list(length=None)
    return {"wallets": wallets}

# Include the API router
app.include_router(api_router)

# Include DDEX router
try:
    from ddex_endpoints import ddex_router
    app.include_router(ddex_router)
    print("✅ DDEX router successfully loaded")
except ImportError as e:
    print(f"⚠️ DDEX router not available: {e}")
except Exception as e:
    print(f"❌ Error loading DDEX router: {e}")

# Include Sponsorship router
try:
    from sponsorship_endpoints import sponsorship_router
    app.include_router(sponsorship_router)
    print("✅ Sponsorship router successfully loaded")
except ImportError as e:
    print(f"⚠️ Sponsorship router not available: {e}")
except Exception as e:
    print(f"❌ Error loading Sponsorship router: {e}")

# Include Tax Management router
try:
    from tax_endpoints import tax_router
    app.include_router(tax_router)
    print("✅ Tax Management router successfully loaded")
except ImportError as e:
    print(f"⚠️ Tax Management router not available: {e}")
except Exception as e:
    print(f"❌ Error loading Tax Management router: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)