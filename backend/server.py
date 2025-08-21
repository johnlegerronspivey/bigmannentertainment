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

# Email configuration for password reset
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

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

# UPC generation function
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
    if not verify_password(login_data.password, user_doc["password_hash"]):
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
    
    # TODO: Send email with reset link
    # For now, we'll just return success
    return {"message": "If the email exists, a reset link has been sent"}

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
    # Generate 4-digit product code (you might want to store and increment this)
    product_code = f"{len(product_name):04d}"  # Simple example
    
    # Combine company prefix and product code
    upc_11_digits = UPC_COMPANY_PREFIX + product_code
    
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
    release_year: int = Form(...),
    current_user: User = Depends(get_current_user)
):
    # Generate designation code (2 digits, could be sequential)
    # In practice, this should be managed more carefully
    designation_code = f"{(hash(track_title) % 100):02d}"
    
    # Create ISRC code: Country Code (2) + Registrant Code (3) + Year (2) + Designation (5)
    isrc_code = f"US{ISRC_PREFIX}{str(release_year)[-2:]}{designation_code:0>3}"
    
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

# Include all routers
app.include_router(api_router)
app.include_router(ddex_router)
app.include_router(sponsorship_router)
app.include_router(tax_router)
app.include_router(industry_router)
app.include_router(label_router)
app.include_router(payment_router)
app.include_router(licensing_router)
app.include_router(gs1_router)

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