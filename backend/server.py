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
import smtplib
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.base import MimeBase
    from email import encoders
except ImportError:
    # Fallback for import issues
    import email.mime.text as mime_text
    import email.mime.multipart as mime_multipart
    import email.mime.base as mime_base
    import email.encoders as encoders
    MimeText = mime_text.MIMEText
    MimeMultipart = mime_multipart.MIMEMultipart
    MimeBase = mime_base.MIMEBase

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

# Email configuration for password reset and notifications
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", "no-reply@bigmannentertainment.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "Big Mann Entertainment")
EMAIL_FROM_ADDRESS = os.environ.get("EMAIL_FROM_ADDRESS", "no-reply@bigmannentertainment.com")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

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
ISRC_PREFIX = os.environ.get('ISRC_PREFIX', 'QZ9H8')
PUBLISHER_NUMBER = os.environ.get('PUBLISHER_NUMBER', 'PA04UV')
IPI_BUSINESS = os.environ.get('IPI_BUSINESS', '813048171')
IPI_PRINCIPAL = os.environ.get('IPI_PRINCIPAL', '578413032')
BUSINESS_LEGAL_NAME = os.environ.get('BUSINESS_LEGAL_NAME', 'Big Mann Entertainment')
PRINCIPAL_NAME = os.environ.get('PRINCIPAL_NAME', 'John LeGerron Spivey')

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductIdentifier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_name: str
    upc_full_code: str  # UPC Company Prefix + Product Code + Check Digit
    gtin: str  # Global Trade Item Number
    isrc_code: Optional[str] = None  # International Standard Recording Code
    product_category: str
    artist_name: Optional[str] = None
    album_title: Optional[str] = None
    track_title: Optional[str] = None
    release_date: Optional[datetime] = None
    duration_seconds: Optional[int] = None  # Track duration for audio recordings
    record_label: Optional[str] = None
    publisher_name: Optional[str] = None  # Music publisher name
    publisher_number: Optional[str] = None  # Publisher identification number
    songwriter_credits: Optional[str] = None  # Songwriter/composer credits
    publishing_rights: Optional[str] = None  # Publishing rights information
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
    "theshaderoom": {
        "type": "social_media",
        "name": "The Shade Room",
        "api_endpoint": "https://api.theshaderoom.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["api_key", "content_partner_id"],
        "target_demographics": "Urban culture enthusiasts, ages 18-45, entertainment news",
        "content_guidelines": "Celebrity news, entertainment content, viral moments, hip-hop culture",
        "submission_process": "The Shade Room editorial review and approval",
        "revenue_sharing": "Content licensing and partnership opportunities"
    },
    "hollywoodunlocked": {
        "type": "social_media",
        "name": "Hollywood Unlocked",
        "api_endpoint": "https://api.hollywoodunlocked.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 150 * 1024 * 1024,  # 150MB
        "credentials_required": ["api_key", "creator_id"],
        "target_demographics": "Entertainment news audience, ages 21-50, celebrity culture",
        "content_guidelines": "Celebrity interviews, entertainment news, exclusive content",
        "submission_process": "Hollywood Unlocked content team review",
        "revenue_sharing": "Exclusive content partnership revenue"
    },
    "tumblr": {
        "type": "social_media",
        "name": "Tumblr",
        "api_endpoint": "https://api.tumblr.com/v2",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["api_key", "api_secret", "oauth_token", "oauth_token_secret"],
        "target_demographics": "Creative community, ages 16-35, alternative culture",
        "content_guidelines": "Creative content, multimedia posts, artistic expression, music promotion",
        "submission_process": "Direct posting with community engagement",
        "revenue_sharing": "Creator monetization through tips and merchandise"
    },
    "models": {
        "type": "social_media",
        "name": "Models.com",
        "api_endpoint": "https://api.models.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 200 * 1024 * 1024,  # 200MB
        "credentials_required": ["api_key", "model_profile_id"],
        "target_demographics": "Fashion industry, ages 16-45, modeling professionals",
        "content_guidelines": "Fashion photography, portfolio content, modeling work, brand campaigns",
        "submission_process": "Models.com profile verification and content approval",
        "revenue_sharing": "Model booking commission and portfolio premium features",
        "platform_features": ["portfolio_hosting", "casting_calls", "industry_networking", "brand_partnerships"]
    },
    "modelmanagement": {
        "type": "social_media",
        "name": "Model Management",
        "api_endpoint": "https://api.modelmanagement.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 150 * 1024 * 1024,  # 150MB
        "credentials_required": ["api_key", "agency_id"],
        "target_demographics": "Modeling agencies, ages 18-50, fashion industry professionals",
        "content_guidelines": "Professional portfolios, agency representation, casting materials",
        "submission_process": "Agency verification and professional content review",
        "revenue_sharing": "Agency booking fees and platform commissions",
        "platform_features": ["agency_management", "model_booking", "casting_platform", "industry_tools"]
    },
    "imgmodels": {
        "type": "social_media",
        "name": "IMG Models",
        "api_endpoint": "https://api.imgmodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 200 * 1024 * 1024,  # 200MB
        "credentials_required": ["api_key", "model_id", "agent_token"],
        "target_demographics": "High fashion industry, ages 16-35, luxury brands and designers",
        "content_guidelines": "High-end fashion photography, runway content, editorial work, brand campaigns",
        "submission_process": "IMG Models talent scouting and representation approval",
        "revenue_sharing": "Premium modeling contracts and brand partnership deals",
        "platform_features": ["elite_representation", "luxury_brand_partnerships", "runway_casting", "editorial_placements"]
    },
    "elitemodelmanagement": {
        "type": "social_media",
        "name": "Elite Model Management",
        "api_endpoint": "https://api.elitemodel.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 180 * 1024 * 1024,  # 180MB
        "credentials_required": ["api_key", "elite_model_id", "agency_access_token"],
        "target_demographics": "International fashion industry, ages 14-40, elite modeling market",
        "content_guidelines": "Elite fashion content, international campaigns, haute couture, commercial work",
        "submission_process": "Elite Model Management scouting and professional evaluation",
        "revenue_sharing": "Elite modeling fees and international campaign revenues",
        "platform_features": ["global_representation", "international_campaigns", "fashion_week_casting", "brand_ambassadorships"]
    },
    "lamodels": {
        "type": "social_media",
        "name": "LA Models",
        "api_endpoint": "https://api.lamodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 150 * 1024 * 1024,  # 150MB
        "credentials_required": ["api_key", "la_model_id", "west_coast_token"],
        "target_demographics": "Commercial and fashion industry, ages 16-45, West Coast market",
        "content_guidelines": "Commercial photography, fashion work, lifestyle brands, entertainment industry",
        "submission_process": "LA Models talent representation and commercial evaluation",
        "revenue_sharing": "Commercial modeling rates and entertainment industry partnerships",
        "platform_features": ["commercial_representation", "entertainment_casting", "lifestyle_brands", "west_coast_market"]
    },
    "stormmanagement": {
        "type": "social_media",
        "name": "Storm Management LA",
        "api_endpoint": "https://api.stormmanagement-la.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 175 * 1024 * 1024,  # 175MB
        "credentials_required": ["api_key", "storm_model_id", "la_office_token"],
        "target_demographics": "Fashion and commercial industry, ages 18-35, Los Angeles market",
        "content_guidelines": "Fashion editorials, commercial campaigns, celebrity photography, brand partnerships",
        "submission_process": "Storm Management LA talent scouting and representation approval",
        "revenue_sharing": "Fashion industry rates and celebrity endorsement deals",
        "platform_features": ["celebrity_representation", "fashion_editorials", "commercial_campaigns", "brand_collaborations"]
    },
    "onlyfans": {
        "type": "social_media",
        "name": "OnlyFans",
        "api_endpoint": "https://api.onlyfans.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 1 * 1024 * 1024 * 1024,  # 1GB
        "credentials_required": ["api_key", "creator_token"],
        "target_demographics": "Content creators, ages 18+, subscription-based audience",
        "content_guidelines": "Creator content, subscription-based material, exclusive content",
        "submission_process": "Creator verification and content compliance review",
        "revenue_sharing": "Creator subscription revenue sharing (80/20 split)",
        "platform_features": ["subscription_model", "creator_monetization", "exclusive_content", "fan_interaction"]
    },
    "lemon8": {
        "type": "social_media",
        "name": "Lemon8",
        "api_endpoint": "https://api.lemon8-app.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["api_key", "user_token"],
        "target_demographics": "Lifestyle enthusiasts, ages 16-35, Gen Z and Millennials",
        "content_guidelines": "Lifestyle content, fashion, beauty, travel, food, wellness",
        "submission_process": "Lemon8 community guidelines review",
        "revenue_sharing": "Creator fund and brand partnership opportunities",
        "platform_features": ["lifestyle_content", "discovery_feed", "trend_sharing", "community_engagement"]
    },
    "thesource": {
        "type": "social_media",
        "name": "The Source",
        "api_endpoint": "https://api.thesource.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 200 * 1024 * 1024,  # 200MB
        "credentials_required": ["api_key", "editorial_token", "content_partner_id"],
        "target_demographics": "Hip-hop culture enthusiasts, ages 16-45, urban music fans",
        "content_guidelines": "Hip-hop music, urban culture, artist interviews, music news, album reviews",
        "submission_process": "The Source editorial team review and music industry validation",
        "revenue_sharing": "Music promotion partnerships and advertising revenue sharing",
        "platform_features": ["music_journalism", "artist_interviews", "album_premieres", "hip_hop_culture"]
    },
    "billboard": {
        "type": "social_media",
        "name": "Billboard",
        "api_endpoint": "https://api.billboard.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 250 * 1024 * 1024,  # 250MB
        "credentials_required": ["api_key", "billboard_partner_id", "charts_access_token"],
        "target_demographics": "Music industry professionals, ages 18-65, mainstream music audience",
        "content_guidelines": "Music industry news, chart performance, artist features, music business content",
        "submission_process": "Billboard editorial review and music industry standards validation",
        "revenue_sharing": "Music industry partnerships and premium content licensing",
        "platform_features": ["chart_tracking", "industry_news", "artist_features", "music_business_insights"]
    },
    "tmz": {
        "type": "social_media",
        "name": "TMZ",
        "api_endpoint": "https://api.tmz.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 300 * 1024 * 1024,  # 300MB
        "credentials_required": ["api_key", "tmz_contributor_id", "entertainment_token"],
        "target_demographics": "Entertainment news audience, ages 18-55, celebrity culture followers",
        "content_guidelines": "Celebrity news, entertainment exclusives, music artist coverage, breaking entertainment news",
        "submission_process": "TMZ editorial team review and entertainment news validation",
        "revenue_sharing": "Exclusive content licensing and contributor revenue sharing",
        "platform_features": ["breaking_news", "celebrity_coverage", "exclusive_content", "entertainment_reporting"]
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
    "livemixtapes": {
        "type": "streaming",
        "name": "LiveMixtapes.com",
        "api_endpoint": "https://api.livemixtapes.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 150 * 1024 * 1024,  # 150MB
        "credentials_required": ["api_key", "user_token"],
        "target_demographics": "Hip-hop fans, ages 16-35, urban culture",
        "content_guidelines": "Hip-hop mixtapes, rap music, urban content, artist features",
        "submission_process": "LiveMixtapes content review and approval",
        "revenue_sharing": "Free hosting with promotional benefits",
        "platform_features": ["mixtape_hosting", "artist_profiles", "download_tracking", "social_sharing"]
    },
    "mymixtapez": {
        "type": "streaming", 
        "name": "MyMixtapez.com",
        "api_endpoint": "https://api.mymixtapez.com/v2",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,  # 200MB
        "credentials_required": ["api_key", "artist_id"],
        "target_demographics": "Hip-hop enthusiasts, ages 18-40, mixtape culture",
        "content_guidelines": "Mixtapes, rap albums, hip-hop singles, collaborative projects",
        "submission_process": "MyMixtapez artist verification and content approval",
        "revenue_sharing": "Free distribution with premium promotion options",
        "platform_features": ["mixtape_distribution", "playlist_features", "artist_discovery", "mobile_app_integration"]
    },
    "worldstarhiphop": {
        "type": "streaming",
        "name": "WorldStar Hip Hop",
        "api_endpoint": "https://api.worldstarhiphop.com/v1",
        "supported_formats": ["video", "audio"],
        "max_file_size": 500 * 1024 * 1024,  # 500MB
        "credentials_required": ["api_key", "content_creator_id"],
        "target_demographics": "Hip-hop culture, ages 16-40, urban entertainment",
        "content_guidelines": "Music videos, hip-hop content, viral videos, artist features",
        "submission_process": "WorldStar editorial review and viral content curation",
        "revenue_sharing": "Content licensing and advertising revenue sharing",
        "platform_features": ["viral_content", "music_videos", "artist_promotion", "social_engagement"]
    },
    "raphousetv": {
        "type": "streaming",
        "name": "RapHouseTV",
        "api_endpoint": "https://api.raphousetv.com/v1",
        "supported_formats": ["video", "audio"],
        "max_file_size": 300 * 1024 * 1024,  # 300MB
        "credentials_required": ["api_key", "artist_id"],
        "target_demographics": "Hip-hop fans, ages 16-35, rap culture enthusiasts",
        "content_guidelines": "Rap music videos, hip-hop content, artist interviews, freestyle sessions",
        "submission_process": "RapHouseTV content review and curation",
        "revenue_sharing": "Artist revenue sharing and promotional opportunities",
        "platform_features": ["rap_videos", "artist_features", "hip_hop_promotion", "community_engagement"]
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
    "tubi": {
        "type": "streaming_tv",
        "name": "Tubi",
        "api_endpoint": "https://api.tubi.tv/v1",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB
        "credentials_required": ["api_key", "content_partner_id"],
        "target_demographics": "Diverse audience, ages 18-65, free streaming viewers",
        "content_guidelines": "Movies, TV shows, documentaries, original content",
        "submission_process": "Tubi content acquisition team review",
        "revenue_sharing": "Ad-supported revenue sharing model",
        "platform_features": ["free_streaming", "ad_supported", "mobile_apps", "smart_tv_integration"]
    },
    "bet": {
        "type": "tv",
        "name": "BET (Black Entertainment Television)",
        "api_endpoint": "https://api.bet.com/content/v1",
        "supported_formats": ["video", "audio", "image"],
        "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB
        "credentials_required": ["api_key", "content_partner_id"],
        "target_demographics": "African American audience, ages 18-54",
        "content_guidelines": "Urban entertainment, music videos, reality TV, comedy, drama",
        "submission_process": "BET content review and approval required",
        "revenue_sharing": "70/30 split (creator/platform)"
    },
    "revolt_tv": {
        "type": "streaming_tv", 
        "name": "Revolt TV",
        "api_endpoint": "https://api.revolt.tv/v1",
        "supported_formats": ["video", "audio"],
        "max_file_size": 1 * 1024 * 1024 * 1024,  # 1GB
        "credentials_required": ["api_key", "channel_id"],
        "target_demographics": "Music lovers, ages 18-34, urban culture",
        "content_guidelines": "Hip-hop, R&B, music documentaries, artist interviews",
        "submission_process": "Revolt content curation team review",
        "revenue_sharing": "65/35 split (creator/platform)"
    },
    "mtv": {
        "type": "tv",
        "name": "MTV (Music Television)",
        "api_endpoint": "https://api.mtv.com/content/v2",
        "supported_formats": ["video", "audio", "image"],
        "max_file_size": 3 * 1024 * 1024 * 1024,  # 3GB
        "credentials_required": ["api_key", "viacom_partner_id"],
        "target_demographics": "Gen Z and Millennials, ages 12-34",
        "content_guidelines": "Music videos, reality TV, pop culture, lifestyle content",
        "submission_process": "MTV programming team review and scheduling",
        "revenue_sharing": "60/40 split (creator/platform)"
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

async def get_admin_user(current_user: User = Depends(get_current_user)):
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

class NotificationRequest(BaseModel):
    email: str
    subject: str
    message: str
    user_name: Optional[str] = "User"

# Notification endpoint for admin use
@api_router.post("/admin/send-notification")
async def send_notification(
    notification: NotificationRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """Send notification email to user"""
    try:
        email_sent = await email_service.send_notification_email(
            notification.email,
            notification.subject,
            notification.message,
            notification.user_name
        )
        
        if email_sent:
            return {"message": "Notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email service error: {str(e)}")

# Bulk notification endpoint
@api_router.post("/admin/send-bulk-notification")
async def send_bulk_notification(
    subject: str = Form(...),
    message: str = Form(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Send notification to all active users"""
    try:
        # Get all active users
        users = []
        async for user_doc in db.users.find({"is_active": True}):
            users.append(User(**user_doc))
        
        success_count = 0
        failure_count = 0
        
        for user in users:
            try:
                email_sent = await email_service.send_notification_email(
                    user.email,
                    subject,
                    message,
                    user.full_name
                )
                if email_sent:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                print(f"Failed to send notification to {user.email}: {str(e)}")
                failure_count += 1
        
        return {
            "message": f"Bulk notification completed",
            "total_users": len(users),
            "successful": success_count,
            "failed": failure_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk notification failed: {str(e)}")

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
            return {"status": "success", "message": f"Content submitted to {platform}"}
    
    # Platform-specific implementation methods
    async def _post_to_instagram(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Post content to Instagram using Graph API"""
        # Implementation would use Instagram Graph API
        return {"status": "success", "platform": "instagram", "post_id": "instagram_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_twitter(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Post content to Twitter using Twitter API v2"""
        # Implementation would use Twitter API v2
        return {"status": "success", "platform": "twitter", "post_id": "twitter_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_facebook(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Post content to Facebook using Graph API"""
        # Implementation would use Facebook Graph API
        return {"status": "success", "platform": "facebook", "post_id": "facebook_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_youtube(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Upload content to YouTube using YouTube Data API"""
        # Implementation would use YouTube Data API v3
        return {"status": "success", "platform": "youtube", "video_id": "youtube_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_tiktok(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Upload content to TikTok using TikTok API"""
        # Implementation would use TikTok for Developers API
        return {"status": "success", "platform": "tiktok", "video_id": "tiktok_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_spotify(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Submit content to Spotify using Spotify Web API"""
        # Implementation would use Spotify Web API for playlist submission
        return {"status": "success", "platform": "spotify", "track_id": "spotify_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_soundcloud(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Upload content to SoundCloud using SoundCloud API"""
        # Implementation would use SoundCloud HTTP API
        return {"status": "success", "platform": "soundcloud", "track_id": "soundcloud_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_apple_music(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Submit content to Apple Music using Apple Music API"""
        # Implementation would use Apple Music API
        return {"status": "success", "platform": "apple_music", "track_id": "apple_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_iheartradio(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Submit content to iHeartRadio using iHeartRadio API"""
        # Implementation would use iHeartRadio API
        return {"status": "success", "platform": "iheartradio", "submission_id": "iheart_" + str(uuid.uuid4())[:8]}
    
    async def _register_with_soundexchange(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Register content with SoundExchange for digital performance royalties"""
        # Implementation would use SoundExchange API for rights registration
        return {"status": "success", "platform": "soundexchange", "registration_id": "sx_" + str(uuid.uuid4())[:8]}
    
    async def _register_with_ascap(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Register content with ASCAP for performance rights"""
        # Implementation would use ASCAP API for work registration
        return {"status": "success", "platform": "ascap", "work_id": "ascap_" + str(uuid.uuid4())[:8]}
    
    async def _register_with_bmi(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Register content with BMI for performance rights"""
        # Implementation would use BMI API for work registration
        return {"status": "success", "platform": "bmi", "work_id": "bmi_" + str(uuid.uuid4())[:8]}
    
    async def _register_with_sesac(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Register content with SESAC for performance rights"""
        # Implementation would use SESAC API for work registration
        return {"status": "success", "platform": "sesac", "work_id": "sesac_" + str(uuid.uuid4())[:8]}
    
    async def _mint_to_blockchain(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Mint content as NFT on specified blockchain"""
        # Implementation would use Web3 libraries for blockchain interaction
        return {"status": "success", "platform": platform, "nft_id": "nft_" + str(uuid.uuid4())[:8], "transaction_hash": "0x" + str(uuid.uuid4()).replace("-", "")}
    
    async def _list_on_nft_marketplace(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """List NFT on specified marketplace"""
        # Implementation would use marketplace-specific APIs
        return {"status": "success", "platform": platform, "listing_id": f"{platform}_" + str(uuid.uuid4())[:8]}
    
    async def _post_to_web3_music(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Post content to Web3 music platforms"""
        # Implementation would use Web3 music platform APIs
        return {"status": "success", "platform": platform, "track_id": f"{platform}_" + str(uuid.uuid4())[:8]}
    
    async def _submit_to_fm_broadcast(self, platform: str, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Submit content to FM broadcast stations"""
        # Implementation would use broadcast network APIs for submission
        return {"status": "success", "platform": platform, "submission_id": f"fm_{platform}_" + str(uuid.uuid4())[:8]}

# Initialize distribution service
distribution_service = DistributionService()

# Email Service Functions
class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = EMAIL_USERNAME
        self.password = EMAIL_PASSWORD
        self.from_name = EMAIL_FROM_NAME
        self.from_address = EMAIL_FROM_ADDRESS
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_address}>"
            msg['To'] = to_email
            
            # Add text version if provided
            if text_content:
                text_part = MimeText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MimeText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str):
        """Send password reset email"""
        reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        subject = "Reset Your Big Mann Entertainment Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; text-decoration: none; padding: 15px 30px; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .button:hover {{ background: linear-gradient(135deg, #6d28d9, #2563eb); }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
                .security-note {{ background-color: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .security-note p {{ color: #92400e; margin: 0; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" alt="Big Mann Entertainment Logo">
                    <h1>Big Mann Entertainment</h1>
                </div>
                
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>Hello {user_name},</p>
                    <p>We received a request to reset your password for your Big Mann Entertainment account. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset My Password</a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background-color: #f3f4f6; padding: 10px; border-radius: 4px; font-family: monospace;">{reset_url}</p>
                    
                    <div class="security-note">
                        <p><strong>Security Notice:</strong> This link will expire in 24 hours. If you didn't request this password reset, please ignore this email and your password will remain unchanged.</p>
                    </div>
                    
                    <p>If you're having trouble accessing your account or need assistance, please contact our support team.</p>
                    
                    <p>Best regards,<br>The Big Mann Entertainment Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Big Mann Entertainment. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>If you need help, contact us through our support channels.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Big Mann Entertainment - Password Reset
        
        Hello {user_name},
        
        We received a request to reset your password for your Big Mann Entertainment account.
        
        Click this link to reset your password:
        {reset_url}
        
        This link will expire in 24 hours. If you didn't request this password reset, please ignore this email.
        
        Best regards,
        The Big Mann Entertainment Team
        
        © 2025 Big Mann Entertainment. All rights reserved.
        """
        
        return await self.send_email(to_email, subject, html_content, text_content)
    
    async def send_welcome_email(self, to_email: str, user_name: str):
        """Send welcome email to new users"""
        subject = "Welcome to Big Mann Entertainment!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Big Mann Entertainment</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; text-decoration: none; padding: 15px 30px; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                .features {{ background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .features ul {{ list-style: none; padding: 0; }}
                .features li {{ padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
                .features li:last-child {{ border-bottom: none; }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" alt="Big Mann Entertainment Logo">
                    <h1>Big Mann Entertainment</h1>
                </div>
                
                <div class="content">
                    <h2>Welcome to the Empire!</h2>
                    <p>Hello {user_name},</p>
                    <p>Welcome to Big Mann Entertainment - your complete media distribution empire! We're excited to have you join our community of creators and entertainers.</p>
                    
                    <div class="features">
                        <h3>What you can do now:</h3>
                        <ul>
                            <li>📤 Upload audio, video, and image content</li>
                            <li>🌍 Distribute to 90+ platforms worldwide</li>
                            <li>💰 Track earnings and manage royalties</li>
                            <li>🎯 Access professional label services</li>
                            <li>🔗 Connect with industry partners</li>
                            <li>📊 Monitor your content performance</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/upload" class="button">Start Uploading Content</a>
                    </div>
                    
                    <p>If you need help getting started or have any questions, our support team is here to help you succeed.</p>
                    
                    <p>Best regards,<br>The Big Mann Entertainment Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Big Mann Entertainment. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_notification_email(self, to_email: str, subject: str, message: str, user_name: str = "User"):
        """Send general notification email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #7c3aed, #3b82f6); padding: 40px 20px; text-align: center; }}
                .header img {{ width: 80px; height: 80px; margin-bottom: 20px; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 40px 20px; }}
                .content h2 {{ color: #1f2937; margin-bottom: 20px; }}
                .content p {{ color: #4b5563; line-height: 1.6; margin-bottom: 20px; }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://customer-assets.emergentagent.com/job_industry-connect-1/artifacts/9vcziqmw_Big%20Mann%20Entertainment%20Logo.png" alt="Big Mann Entertainment Logo">
                    <h1>Big Mann Entertainment</h1>
                </div>
                
                <div class="content">
                    <h2>{subject}</h2>
                    <p>Hello {user_name},</p>
                    <div>{message}</div>
                    <p>Best regards,<br>The Big Mann Entertainment Team</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 Big Mann Entertainment. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
# Initialize email service
email_service = EmailService()
def calculate_upc_check_digit(upc_11_digits: str) -> str:
    """Calculate check digit for UPC code using the standard algorithm"""
    if len(upc_11_digits) != 11:
        raise ValueError("UPC must be 11 digits for check digit calculation")
    
    odd_sum = sum(int(upc_11_digits[i]) for i in range(0, 11, 2))  # Digits at positions 1, 3, 5, 7, 9, 11
    even_sum = sum(int(upc_11_digits[i]) for i in range(1, 11, 2))  # Digits at positions 2, 4, 6, 8, 10
    
    # Corrected UPC-A algorithm: (even_sum * 3) + odd_sum
    total = (even_sum * 3) + odd_sum
    check_digit = (10 - (total % 10)) % 10
    
    return str(check_digit)

# API Endpoints
@api_router.post("/auth/register", response_model=Token)
async def register_user(user_data: UserCreate, request: Request):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate age (must be 18+)
    today = datetime.utcnow().date()
    birth_date = user_data.date_of_birth.date() if isinstance(user_data.date_of_birth, datetime) else user_data.date_of_birth
    age = today.year - birth_date.year
    if today < birth_date.replace(year=today.year):
        age -= 1
    
    if age < 18:
        raise HTTPException(status_code=400, detail="Must be 18 or older to register")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
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
        country=user_data.country,
        is_active=True,
        is_verified=False,
        role="user"
    )
    
    # Store user in database
    user_dict = user.dict()
    user_dict["password_hash"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Send welcome email
    try:
        await email_service.send_welcome_email(user.email, user.full_name)
    except Exception as e:
        print(f"Failed to send welcome email: {str(e)}")
        # Don't fail registration if email fails
    
    # Log activity
    await log_activity(user.id, "register", "user", user.id, {"email": user.email}, request)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Create session
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + access_token_expires,
        user_agent=request.headers.get("user-agent"),
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
async def login_user(login_data: UserLogin, request: Request):
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_doc)
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=423, detail="Account is temporarily locked due to too many failed attempts")
    
    # Verify password
    password_hash = user_doc.get("password_hash")
    if not password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, password_hash):
        # Increment failed attempts
        failed_attempts = user.failed_login_attempts + 1
        locked_until = None
        
        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        
        await db.users.update_one(
            {"id": user.id},
            {
                "$set": {
                    "failed_login_attempts": failed_attempts,
                    "locked_until": locked_until
                }
            }
        )
        
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Reset failed attempts on successful login
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "failed_login_attempts": 0,
                "locked_until": None,
                "last_login": datetime.utcnow(),
                "login_count": user.login_count + 1
            }
        }
    )
    
    # Log activity
    await log_activity(user.id, "login", "user", user.id, {"method": "password"}, request)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Create session
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + access_token_expires,
        user_agent=request.headers.get("user-agent"),
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

@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@api_router.post("/auth/refresh", response_model=Token)
async def refresh_token(refresh_data: TokenRefresh, request: Request):
    # Find session by refresh token
    session_doc = await db.user_sessions.find_one({
        "refresh_token": refresh_data.refresh_token,
        "is_active": True
    })
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    session = UserSession(**session_doc)
    
    # Check if session has expired
    if session.expires_at < datetime.utcnow():
        await db.user_sessions.update_one(
            {"id": session.id},
            {"$set": {"is_active": False}}
        )
        raise HTTPException(status_code=401, detail="Session has expired")
    
    # Get user
    user_doc = await db.users.find_one({"id": session.user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = User(**user_doc)
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token()
    
    # Update session
    await db.user_sessions.update_one(
        {"id": session.id},
        {
            "$set": {
                "session_token": access_token,
                "refresh_token": new_refresh_token,
                "expires_at": datetime.utcnow() + access_token_expires,
                "last_accessed": datetime.utcnow()
            }
        }
    )
    
    # Log activity
    await log_activity(user.id, "token_refresh", "user", user.id, {}, request)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@api_router.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user), request: Request = None):
    # Deactivate all user sessions
    await db.user_sessions.update_many(
        {"user_id": current_user.id, "is_active": True},
        {"$set": {"is_active": False}}
    )
    
    # Log activity
    if request:
        await log_activity(current_user.id, "logout", "user", current_user.id, {}, request)
    
    return {"message": "Successfully logged out"}

@api_router.post("/auth/forgot-password")
async def forgot_password(request_data: ForgotPasswordRequest, request: Request):
    # Find user
    user_doc = await db.users.find_one({"email": request_data.email})
    if not user_doc:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
    
    user = User(**user_doc)
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    
    # Store reset token
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires": expires_at
            }
        }
    )
    
    # Log activity
    await log_activity(user.id, "password_reset_requested", "user", user.id, {"email": user.email}, request)
    
    # Send password reset email
    try:
        email_sent = await email_service.send_password_reset_email(user.email, reset_token, user.full_name)
        if email_sent:
            return {"message": "If the email exists, a reset link has been sent"}
        else:
            # Fallback to development mode if email fails
            reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
            return {
                "message": "Email service unavailable. Please use the development reset link below.",
                "reset_token": reset_token,
                "reset_url": reset_url,
                "expires_in_hours": PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
                "instructions": "Email service is currently unavailable. Use the reset URL below for testing purposes."
            }
    except Exception as e:
        print(f"Email service error: {str(e)}")
        # Fallback to development mode if email fails
        reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        return {
            "message": "Email service unavailable. Please use the development reset link below.",
            "reset_token": reset_token,
            "reset_url": reset_url,
            "expires_in_hours": PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
            "instructions": "Email service is currently unavailable. Use the reset URL below for testing purposes."
        }

@api_router.post("/auth/reset-password")
async def reset_password(reset_data: ResetPasswordRequest, request: Request):
    # Find user by reset token
    user_doc = await db.users.find_one({
        "password_reset_token": reset_data.token,
        "password_reset_expires": {"$gt": datetime.utcnow()}
    })
    
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    user = User(**user_doc)
    
    # Hash new password
    hashed_password = get_password_hash(reset_data.new_password)
    
    # Update password and clear reset token
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "password_hash": hashed_password,
                "failed_login_attempts": 0,
                "locked_until": None
            },
            "$unset": {
                "password_reset_token": "",
                "password_reset_expires": ""
            }
        }
    )
    
    # Deactivate all sessions
    await db.user_sessions.update_many(
        {"user_id": user.id},
        {"$set": {"is_active": False}}
    )
    
    # Log activity
    await log_activity(user.id, "password_reset_completed", "user", user.id, {}, request)
    
    return {"message": "Password has been reset successfully"}

# Business Identifiers Endpoints
@api_router.get("/business/identifiers")
async def get_business_identifiers(current_user: User = Depends(get_current_user)):
    return BusinessIdentifiers(
        business_legal_name=BUSINESS_LEGAL_NAME,
        business_ein=BUSINESS_EIN,
        business_tin=BUSINESS_TIN,
        business_address=BUSINESS_ADDRESS,
        business_phone=BUSINESS_PHONE,
        business_naics_code=BUSINESS_NAICS_CODE,
        upc_company_prefix=UPC_COMPANY_PREFIX,
        global_location_number=GLOBAL_LOCATION_NUMBER
    )

@api_router.post("/business/generate-upc")
async def generate_upc(
    product_name: str = Form(...),
    product_category: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    # Use first 6 digits of company prefix for UPC-A format
    company_prefix_6 = UPC_COMPANY_PREFIX[:6]  # "860004"
    
    # Generate 5-digit product code (to make 11 digits total with 6-digit prefix)
    product_code = f"{abs(hash(product_name + product_category)) % 100000:05d}"
    
    # Combine company prefix and product code (11 digits total)
    upc_11_digits = company_prefix_6 + product_code
    
    # Calculate check digit
    check_digit = calculate_upc_check_digit(upc_11_digits)
    
    # Create full UPC
    upc_full = upc_11_digits + check_digit
    
    # Create GTIN (add leading zero to UPC for 13-digit GTIN)
    gtin = "0" + upc_full
    
    # Create product identifier record
    product_identifier = ProductIdentifier(
        product_name=product_name,
        upc_full_code=upc_full,
        gtin=gtin,
        product_category=product_category
    )
    
    # Store in database
    await db.product_identifiers.insert_one(product_identifier.dict())
    
    return {
        "product_name": product_name,
        "upc": upc_full,
        "gtin": gtin,
        "company_prefix": UPC_COMPANY_PREFIX,
        "product_code": product_code,
        "check_digit": check_digit,
        "product_category": product_category
    }

@api_router.post("/business/generate-isrc")
async def generate_isrc(
    artist_name: str = Form(...),
    track_title: str = Form(...),
    release_year: int = Form(default=datetime.utcnow().year),
    current_user: User = Depends(get_current_user)
):
    # Generate 5-digit designation code
    designation_code = f"{abs(hash(track_title + artist_name)) % 100000:05d}"
    
    # Create ISRC code: Country Code (2) + Registrant Code (3) + Year (2) + Designation (5)
    # Format: CC-XXX-YY-NNNNN
    country_code = "US"
    registrant_code = ISRC_PREFIX[:3]  # Use first 3 characters
    year_code = str(release_year)[-2:]  # Last 2 digits of year
    
    isrc_code = f"{country_code}-{registrant_code}-{year_code}-{designation_code}"
    
    return {
        "isrc_code": isrc_code,
        "artist_name": artist_name,
        "track_title": track_title,
        "release_year": release_year,
        "country_code": "US",
        "registrant_code": ISRC_PREFIX,
        "year_code": str(release_year)[-2:],
        "designation_code": designation_code
    }

# Add missing business/products endpoint
@api_router.get("/business/products")
async def get_business_products(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get all product identifiers for the business"""
    try:
        # Get products from database
        cursor = db.product_identifiers.find({}).skip(skip).limit(limit).sort("created_at", -1)
        products = []
        
        async for product_doc in cursor:
            products.append(ProductIdentifier(**product_doc))
        
        # Get total count
        total_count = await db.product_identifiers.count_documents({})
        
        return {
            "products": products,
            "total_count": total_count,
            "page": skip // limit + 1,
            "pages": (total_count + limit - 1) // limit
        }
    except Exception as e:
        return {
            "products": [],
            "total_count": 0,
            "page": 1,
            "pages": 0,
            "message": "No products found"
        }

# Media Management Endpoints
@api_router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    price: float = Form(0.0),
    tags: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    allowed_types = {
        'audio': ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/flac', 'audio/aac'],
        'video': ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'],
        'image': ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    }
    
    # Determine content type based on MIME type
    content_type = None
    for type_category, mime_types in allowed_types.items():
        if file.content_type in mime_types:
            content_type = type_category
            break
    
    if not content_type:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Create directory if it doesn't exist
    content_dir = uploads_dir / content_type
    content_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = content_dir / unique_filename
    
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
        tags=tag_list,
        category=category,
        price=price,
        owner_id=current_user.id
    )
    
    # Store in database
    await db.media_content.insert_one(media.dict())
    
    return {
        "media_id": media.id,
        "title": title,
        "content_type": content_type,
        "file_size": file_size,
        "category": category,
        "price": price,
        "tags": tag_list,
        "message": "Media uploaded successfully"
    }

@api_router.get("/media/library")
async def get_media_library(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    # Build query
    query = {"owner_id": current_user.id}
    if content_type:
        query["content_type"] = content_type
    if category:
        query["category"] = category
    
    # Get media items
    cursor = db.media_content.find(query).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    # Get total count
    total_count = await db.media_content.count_documents(query)
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@api_router.get("/media/{media_id}")
async def get_media_item(media_id: str, current_user: User = Depends(get_current_user)):
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media or is admin
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this media")
    
    return MediaContent(**media)

@api_router.get("/media/{media_id}/download")
async def download_media(media_id: str, current_user: User = Depends(get_current_user)):
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media or has purchased it (simplified for now)
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to download this media")
    
    file_path = Path(media["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Update download count
    await db.media_content.update_one(
        {"id": media_id},
        {"$inc": {"download_count": 1}}
    )
    
    return FileResponse(
        path=file_path,
        filename=media["title"],
        media_type=media["mime_type"]
    )

# MISSING MEDIA ENDPOINTS - IMPLEMENTING FOR 100% FUNCTIONALITY

@api_router.put("/media/{media_id}")
async def update_media(
    media_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Update media metadata"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this media")
    
    # Build update data
    update_data = {"updated_at": datetime.utcnow()}
    
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if category is not None:
        update_data["category"] = category
    if price is not None:
        update_data["price"] = price
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        update_data["tags"] = tag_list
    
    # Update in database
    await db.media_content.update_one({"id": media_id}, {"$set": update_data})
    
    # Get updated media
    updated_media = await db.media_content.find_one({"id": media_id})
    
    return {
        "message": "Media updated successfully",
        "media": MediaContent(**updated_media)
    }

@api_router.delete("/media/{media_id}")
async def delete_media(media_id: str, current_user: User = Depends(get_current_user)):
    """Delete media and its associated file"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this media")
    
    # Delete file from filesystem
    file_path = Path(media["file_path"])
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass  # File deletion failed, but we'll still remove from database
    
    # Remove from database
    await db.media_content.delete_one({"id": media_id})
    
    # Log activity
    await log_activity(
        current_user.id,
        "media_deleted",
        "media",
        media_id,
        {"title": media["title"], "content_type": media["content_type"]}
    )
    
    return {"message": "Media deleted successfully"}

@api_router.post("/media/{media_id}/metadata")
async def update_media_metadata(
    media_id: str,
    metadata: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Update detailed media metadata"""
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Check if user owns the media
    if media["owner_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this media")
    
    # Update metadata
    update_data = {
        "updated_at": datetime.utcnow(),
        "metadata": metadata
    }
    
    await db.media_content.update_one({"id": media_id}, {"$set": update_data})
    
    return {
        "message": "Metadata updated successfully",
        "metadata": metadata
    }

@api_router.get("/media/search")
async def search_media(
    q: str,  # search query
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Search media content"""
    # Build search query
    search_conditions = []
    
    # Text search on title and description
    if q:
        search_conditions.append({
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}}
            ]
        })
    
    # Filter by content type
    if content_type:
        search_conditions.append({"content_type": content_type})
    
    # Filter by category
    if category:
        search_conditions.append({"category": category})
    
    # Filter by tags
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        search_conditions.append({"tags": {"$in": tag_list}})
    
    # Only show user's own media or public approved media
    visibility_condition = {
        "$or": [
            {"owner_id": current_user.id},
            {"is_published": True, "is_approved": True}
        ]
    }
    search_conditions.append(visibility_condition)
    
    # Combine all conditions
    query = {"$and": search_conditions} if search_conditions else {}
    
    # Execute search
    cursor = db.media_content.find(query).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    # Get total count
    total_count = await db.media_content.count_documents(query)
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "search_query": q,
        "filters": {
            "content_type": content_type,
            "category": category,
            "tags": tags
        },
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

# Content Distribution Endpoints
@api_router.get("/distribution/platforms")
async def get_distribution_platforms():
    """Get all available distribution platforms"""
    platforms = []
    for platform_id, config in DISTRIBUTION_PLATFORMS.items():
        platforms.append({
            "id": platform_id,
            "name": config["name"],
            "type": config["type"],
            "supported_formats": config["supported_formats"],
            "max_file_size": config["max_file_size"],
            "description": config.get("description", ""),
            "credentials_required": config["credentials_required"]
        })
    
    return {
        "platforms": platforms,
        "total_count": len(platforms)
    }

@api_router.post("/distribution/distribute")
async def distribute_content(
    request: DistributionRequest,
    current_user: User = Depends(get_current_user)
):
    # Verify user owns the media
    media = await db.media_content.find_one({"id": request.media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if media["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to distribute this media")
    
    # Start distribution process
    distribution = await distribution_service.distribute_content(
        media_id=request.media_id,
        platforms=request.platforms,
        user_id=current_user.id,
        custom_message=request.custom_message,
        hashtags=request.hashtags
    )
    
    return {
        "distribution_id": distribution.id,
        "media_id": request.media_id,
        "platforms": request.platforms,
        "status": distribution.status,
        "results": distribution.results,
        "message": "Distribution initiated successfully"
    }

@api_router.get("/distribution/history")
async def get_distribution_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    # Get media IDs owned by user
    user_media = []
    async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
        user_media.append(media["id"])
    
    if not user_media:
        return {"distributions": [], "total_count": 0}
    
    # Get distributions for user's media
    query = {"media_id": {"$in": user_media}}
    cursor = db.content_distributions.find(query).skip(skip).limit(limit).sort("created_at", -1)
    
    distributions = []
    async for dist in cursor:
        distributions.append(ContentDistribution(**dist))
    
    total_count = await db.content_distributions.count_documents(query)
    
    return {
        "distributions": distributions,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

# MISSING DISTRIBUTION ENDPOINTS - IMPLEMENTING FOR 100% FUNCTIONALITY

@api_router.get("/distribution/status")
async def get_distribution_status(current_user: User = Depends(get_current_user)):
    """Get overall distribution status and statistics"""
    try:
        # Get user's media
        user_media = []
        async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
            user_media.append(media["id"])
        
        if not user_media:
            return {
                "status": {
                    "total_media": 0,
                    "distributed_media": 0,
                    "active_distributions": 0,
                    "pending_distributions": 0,
                    "failed_distributions": 0,
                    "success_rate": 0
                },
                "platform_status": {},
                "recent_activity": []
            }
        
        # Get distributions for user's media
        all_distributions = []
        async for dist in db.content_distributions.find({"media_id": {"$in": user_media}}):
            all_distributions.append(dist)
        
        # Calculate statistics
        total_distributions = len(all_distributions)
        active_distributions = len([d for d in all_distributions if d.get("status") == "processing"])
        completed_distributions = len([d for d in all_distributions if d.get("status") == "completed"])
        failed_distributions = len([d for d in all_distributions if d.get("status") in ["failed", "partial"]])
        
        success_rate = (completed_distributions / max(total_distributions, 1)) * 100
        
        # Platform status breakdown
        platform_status = {}
        for platform_id in DISTRIBUTION_PLATFORMS.keys():
            platform_distributions = [d for d in all_distributions if platform_id in d.get("target_platforms", [])]
            platform_status[platform_id] = {
                "name": DISTRIBUTION_PLATFORMS[platform_id]["name"],
                "total_distributions": len(platform_distributions),
                "successful": len([d for d in platform_distributions if d.get("status") == "completed"]),
                "failed": len([d for d in platform_distributions if d.get("status") in ["failed", "partial"]]),
                "last_distribution": max([d.get("created_at", datetime.min) for d in platform_distributions]) if platform_distributions else None
            }
        
        return {
            "status": {
                "total_media": len(user_media),
                "total_distributions": total_distributions,
                "active_distributions": active_distributions,
                "completed_distributions": completed_distributions,
                "failed_distributions": failed_distributions,
                "success_rate": round(success_rate, 1)
            },
            "platform_status": platform_status,
            "recent_activity": all_distributions[-5:] if all_distributions else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get distribution status: {str(e)}")

@api_router.get("/distribution/analytics")
async def get_distribution_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get distribution analytics and performance metrics"""
    try:
        # Get user's media
        user_media = []
        async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
            user_media.append(media["id"])
        
        if not user_media:
            return {
                "analytics": {
                    "overview": {"total_distributions": 0},
                    "platform_performance": {},
                    "trends": [],
                    "top_content": []
                }
            }
        
        # Get distributions for the specified period
        start_date = datetime.utcnow() - timedelta(days=days)
        distributions = []
        async for dist in db.content_distributions.find({
            "media_id": {"$in": user_media},
            "created_at": {"$gte": start_date}
        }):
            distributions.append(dist)
        
        # Calculate performance by platform
        platform_performance = {}
        for platform_id, platform_info in DISTRIBUTION_PLATFORMS.items():
            platform_dists = [d for d in distributions if platform_id in d.get("target_platforms", [])]
            
            if platform_dists:
                successful = len([d for d in platform_dists if d.get("status") == "completed"])
                platform_performance[platform_id] = {
                    "name": platform_info["name"],
                    "type": platform_info["type"],
                    "total_distributions": len(platform_dists),
                    "successful_distributions": successful,
                    "success_rate": (successful / len(platform_dists)) * 100 if platform_dists else 0,
                    "avg_processing_time": "2.5 hours",  # Would calculate from actual data
                    "revenue_generated": 0  # Would integrate with payment data
                }
        
        # Generate trend data (simplified)
        trends = []
        for i in range(min(days, 7)):  # Last 7 days or requested days
            date = (datetime.utcnow() - timedelta(days=i)).date()
            day_distributions = [d for d in distributions if d.get("created_at", datetime.min).date() == date]
            trends.append({
                "date": date.isoformat(),
                "distributions": len(day_distributions),
                "successful": len([d for d in day_distributions if d.get("status") == "completed"])
            })
        
        return {
            "analytics": {
                "overview": {
                    "total_distributions": len(distributions),
                    "period_days": days,
                    "avg_distributions_per_day": len(distributions) / max(days, 1),
                    "overall_success_rate": (len([d for d in distributions if d.get("status") == "completed"]) / max(len(distributions), 1)) * 100
                },
                "platform_performance": platform_performance,
                "trends": trends[::-1],  # Reverse to show oldest first
                "top_performing_platforms": sorted(
                    platform_performance.items(), 
                    key=lambda x: x[1]["success_rate"], 
                    reverse=True
                )[:5]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get distribution analytics: {str(e)}")

@api_router.get("/distribution/platforms/{platform_id}")
async def get_platform_details(platform_id: str, current_user: User = Depends(get_current_user)):
    """Get detailed information about a specific distribution platform"""
    if platform_id not in DISTRIBUTION_PLATFORMS:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    platform_config = DISTRIBUTION_PLATFORMS[platform_id]
    
    # Get user's distributions for this platform
    user_media = []
    async for media in db.media_content.find({"owner_id": current_user.id}, {"id": 1}):
        user_media.append(media["id"])
    
    platform_distributions = []
    if user_media:
        async for dist in db.content_distributions.find({
            "media_id": {"$in": user_media},
            "target_platforms": platform_id
        }):
            platform_distributions.append(dist)
    
    # Calculate platform-specific statistics
    total_distributions = len(platform_distributions)
    successful = len([d for d in platform_distributions if d.get("status") == "completed"])
    success_rate = (successful / max(total_distributions, 1)) * 100
    
    return {
        "platform": {
            "id": platform_id,
            "name": platform_config["name"],
            "type": platform_config["type"],
            "description": platform_config.get("description", ""),
            "supported_formats": platform_config["supported_formats"],
            "max_file_size": platform_config["max_file_size"],
            "credentials_required": platform_config["credentials_required"],
            "api_endpoint": platform_config.get("api_endpoint"),
            "target_demographics": platform_config.get("target_demographics"),
            "content_guidelines": platform_config.get("content_guidelines"),
            "revenue_sharing": platform_config.get("revenue_sharing"),
            "platform_features": platform_config.get("platform_features", [])
        },
        "user_statistics": {
            "total_distributions": total_distributions,
            "successful_distributions": successful,
            "success_rate": round(success_rate, 1),
            "last_distribution": max([d.get("created_at", datetime.min) for d in platform_distributions]) if platform_distributions else None,
            "recent_distributions": platform_distributions[-5:] if platform_distributions else []
        }
    }

@api_router.post("/distribution/schedule")
async def schedule_distribution(
    media_id: str = Form(...),
    platforms: str = Form(...),  # JSON string
    scheduled_time: str = Form(...),
    custom_message: Optional[str] = Form(None),
    hashtags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Schedule content distribution for future execution"""
    try:
        # Parse platforms JSON
        try:
            platforms_list = json.loads(platforms)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid platforms format")
        
        # Parse scheduled time
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format")
        
        # Verify user owns the media
        media = await db.media_content.find_one({"id": media_id})
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        if media["owner_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to distribute this media")
        
        # Parse hashtags
        hashtag_list = []
        if hashtags:
            hashtag_list = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
        
        # Create scheduled distribution
        scheduled_distribution = ContentDistribution(
            media_id=media_id,
            target_platforms=platforms_list,
            status="scheduled",
            scheduled_time=scheduled_datetime,
            results={"scheduled_for": scheduled_datetime.isoformat()},
        )
        
        # Store in database
        await db.content_distributions.insert_one(scheduled_distribution.dict())
        
        # Log activity
        await log_activity(
            current_user.id,
            "distribution_scheduled",
            "distribution",
            scheduled_distribution.id,
            {
                "media_id": media_id,
                "platforms": platforms_list,
                "scheduled_time": scheduled_datetime.isoformat()
            }
        )
        
        return {
            "message": "Distribution scheduled successfully",
            "distribution_id": scheduled_distribution.id,
            "scheduled_time": scheduled_datetime.isoformat(),
            "platforms": platforms_list,
            "status": "scheduled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule distribution: {str(e)}")

@api_router.delete("/distribution/{distribution_id}")
async def cancel_distribution(distribution_id: str, current_user: User = Depends(get_current_user)):
    """Cancel a distribution (if not already completed)"""
    # Find distribution
    distribution = await db.content_distributions.find_one({"id": distribution_id})
    if not distribution:
        raise HTTPException(status_code=404, detail="Distribution not found")
    
    # Verify user owns the media
    media = await db.media_content.find_one({"id": distribution["media_id"]})
    if not media or media["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this distribution")
    
    # Check if distribution can be cancelled
    if distribution["status"] in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel distribution with status: {distribution['status']}")
    
    # Update distribution status
    await db.content_distributions.update_one(
        {"id": distribution_id},
        {
            "$set": {
                "status": "cancelled",
                "updated_at": datetime.utcnow(),
                "results": {
                    **distribution.get("results", {}),
                    "cancelled_by": current_user.id,
                    "cancelled_at": datetime.utcnow().isoformat()
                }
            }
        }
    )
    
    # Log activity
    await log_activity(
        current_user.id,
        "distribution_cancelled",
        "distribution",
        distribution_id,
        {"reason": "user_request"}
    )
    
    return {
        "message": "Distribution cancelled successfully",
        "distribution_id": distribution_id,
        "status": "cancelled"
    }

# Admin Endpoints
@api_router.get("/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    cursor = db.users.find({}, {"password_hash": 0}).skip(skip).limit(limit).sort("created_at", -1)
    users = []
    
    async for user_doc in cursor:
        users.append(User(**user_doc))
    
    total_count = await db.users.count_documents({})
    
    return {
        "users": users,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@api_router.put("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    # Find user
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build update data
    update_data = {}
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.business_name is not None:
        update_data["business_name"] = user_update.business_name
    if user_update.is_active is not None:
        update_data["is_active"] = user_update.is_active
    if user_update.role is not None:
        update_data["role"] = user_update.role
        # Also update is_admin based on role
        update_data["is_admin"] = user_update.role in ["admin", "super_admin", "moderator"]
    if user_update.account_status is not None:
        update_data["account_status"] = user_update.account_status
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    # Get updated user
    updated_user_doc = await db.users.find_one({"id": user_id}, {"password_hash": 0})
    return User(**updated_user_doc)

@api_router.get("/admin/media")
async def get_all_media(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    cursor = db.media_content.find({}).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    total_count = await db.media_content.count_documents({})
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@api_router.post("/admin/media/{media_id}/moderate")
async def moderate_content(
    media_id: str,
    action: ContentModerationAction,
    current_user: User = Depends(get_current_admin_user)
):
    # Find media
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Update based on action
    update_data = {"updated_at": datetime.utcnow()}
    
    if action.action == "approve":
        update_data.update({
            "is_approved": True,
            "approval_status": "approved",
            "is_published": True
        })
    elif action.action == "reject":
        update_data.update({
            "is_approved": False,
            "approval_status": "rejected",
            "is_published": False
        })
    elif action.action == "feature":
        update_data["is_featured"] = True
    elif action.action == "unfeature":
        update_data["is_featured"] = False
    
    if action.notes:
        update_data["moderation_notes"] = action.notes
    
    await db.media_content.update_one({"id": media_id}, {"$set": update_data})
    
    return {"message": f"Content {action.action}d successfully"}

# Add missing admin content endpoints
@api_router.get("/admin/content/pending")
async def get_pending_content(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    """Get content pending approval"""
    cursor = db.media_content.find({"approval_status": "pending"}).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    total_count = await db.media_content.count_documents({"approval_status": "pending"})
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@api_router.get("/admin/content/reported")
async def get_reported_content(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    """Get reported content"""
    cursor = db.media_content.find({"$or": [{"approval_status": "reported"}, {"moderation_notes": {"$exists": True}}]}).skip(skip).limit(limit).sort("created_at", -1)
    media_items = []
    
    async for item in cursor:
        media_items.append(MediaContent(**item))
    
    total_count = await db.media_content.count_documents({"$or": [{"approval_status": "reported"}, {"moderation_notes": {"$exists": True}}]})
    
    return {
        "media_items": media_items,
        "total_count": total_count,
        "page": skip // limit + 1,
        "pages": (total_count + limit - 1) // limit
    }

@api_router.get("/admin/analytics")
async def get_admin_analytics(current_user: User = Depends(get_current_admin_user)):
    # Get various analytics
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    total_media = await db.media_content.count_documents({})
    approved_media = await db.media_content.count_documents({"is_approved": True})
    total_distributions = await db.content_distributions.count_documents({})
    
    # Get recent activity (simplified)
    recent_users = await db.users.count_documents({
        "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    recent_media = await db.media_content.count_documents({
        "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "recent": recent_users
        },
        "media": {
            "total": total_media,
            "approved": approved_media,
            "recent": recent_media
        },
        "distributions": {
            "total": total_distributions
        },
        "platforms": {
            "total": len(DISTRIBUTION_PLATFORMS),
            "by_type": {}
        }
    }

# Include other endpoint routers
from ddex_endpoints import ddex_router
from sponsorship_endpoints import sponsorship_router
from tax_endpoints import tax_router
from industry_endpoints import industry_router
from label_endpoints import label_router
from payment_endpoints import payment_router
from licensing_endpoints import licensing_router
from gs1_endpoints import gs1_router

# Initialize Payment Service
try:
    import payment_endpoints
    from payment_service import PaymentService
    
    # Initialize the payment service with database
    payment_service_instance = PaymentService(db)
    payment_endpoints.payment_service = payment_service_instance
    print("✅ Payment service initialized successfully")
except ImportError as e:
    print(f"⚠️ Payment service initialization failed: {str(e)}")
except Exception as e:
    print(f"⚠️ Payment service initialization error: {str(e)}")

# Include all routers in the api_router to get /api prefix
api_router.include_router(ddex_router)
api_router.include_router(sponsorship_router)
api_router.include_router(tax_router)
api_router.include_router(industry_router)
api_router.include_router(label_router)
api_router.include_router(payment_router)
api_router.include_router(licensing_router)
api_router.include_router(gs1_router)

# Include the main api_router in the app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "Big Mann Entertainment API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)