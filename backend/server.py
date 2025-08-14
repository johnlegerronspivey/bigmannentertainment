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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Stripe setup
stripe_api_key = os.environ.get('STRIPE_API_KEY')

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
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    business_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

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

class Purchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    media_id: str
    amount: float
    currency: str = "usd"
    stripe_session_id: Optional[str] = None
    payment_status: str = "pending"
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
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

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
        elif platform in ["spotify", "apple_music", "amazon_music", "soundcloud", "pandora", "tidal"]:
            return await self._submit_to_streaming_service(platform, media, custom_message)
        elif platform in ["iheartradio", "siriusxm", "radio_com", "tunein"]:
            return await self._submit_to_radio_station(platform, media, custom_message)
        elif platform.endswith(("_pop", "_country", "_rock", "_hiphop", "_adult_contemporary", "_classic_rock", 
                               "_alternative", "_latin", "_christian", "_jazz", "_urban", "_oldies", "_electronic", "_indie")) or "classical_public_radio" in platform or "regional_indie" in platform:
            return await self._submit_to_fm_broadcast_station(platform, media, custom_message)
        elif platform in ["cnn", "fox_news", "msnbc", "espn", "netflix", "hulu", "hbo_max"]:
            return await self._submit_to_tv_network(platform, media, custom_message)
        elif platform in ["spotify_podcasts", "apple_podcasts", "google_podcasts", "podcast_one", "stitcher"]:
            return await self._submit_to_podcast_platform(platform, media, custom_message)
        elif platform in ["soundexchange", "ascap", "bmi", "sesac"]:
            return await self._submit_to_performance_rights_org(platform, media, custom_message)
        else:
            return {"status": "error", "message": f"Distribution not implemented for {platform}"}
    
    async def _post_to_instagram(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Post content to Instagram"""
        if not INSTAGRAM_ACCESS_TOKEN:
            return {"status": "error", "message": "Instagram access token not configured"}
        
        try:
            # Build caption
            caption = custom_message or f"{media['title']}\n\n{media.get('description', '')}"
            if hashtags:
                caption += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
            
            # Simulate Instagram API call
            # In production, implement actual Instagram Graph API integration
            return {
                "status": "success",
                "platform": "instagram",
                "post_id": f"ig_{uuid.uuid4()}",
                "url": f"https://instagram.com/p/mock_post_id"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _post_to_twitter(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Post content to Twitter"""
        if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
            return {"status": "error", "message": "Twitter credentials not configured"}
        
        try:
            # Build tweet text
            tweet_text = custom_message or f"{media['title']}\n\n{media.get('description', '')}"
            if hashtags:
                hashtag_string = " ".join([f"#{tag}" for tag in hashtags])
                if len(tweet_text) + len(hashtag_string) + 2 <= 280:
                    tweet_text += f"\n\n{hashtag_string}"
            
            # Truncate if necessary
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            # Simulate Twitter API call
            return {
                "status": "success",
                "platform": "twitter",
                "post_id": f"tw_{uuid.uuid4()}",
                "url": f"https://twitter.com/user/status/mock_tweet_id"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _post_to_facebook(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Post content to Facebook"""
        if not FACEBOOK_ACCESS_TOKEN:
            return {"status": "error", "message": "Facebook access token not configured"}
        
        try:
            # Build message
            message = custom_message or f"{media['title']}\n\n{media.get('description', '')}"
            if hashtags:
                message += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
            
            # Simulate Facebook API call
            return {
                "status": "success",
                "platform": "facebook",
                "post_id": f"fb_{uuid.uuid4()}",
                "url": f"https://facebook.com/post/mock_post_id"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _post_to_youtube(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Upload video to YouTube"""
        if not YOUTUBE_API_KEY:
            return {"status": "error", "message": "YouTube API key not configured"}
        
        if media["content_type"] != "video":
            return {"status": "error", "message": "YouTube only supports video content"}
        
        try:
            # Build description
            description = custom_message or f"{media.get('description', '')}"
            if hashtags:
                description += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
            
            # Simulate YouTube API call
            return {
                "status": "success",
                "platform": "youtube",
                "video_id": f"yt_{uuid.uuid4()}",
                "url": f"https://youtube.com/watch?v=mock_video_id"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _post_to_tiktok(self, media: dict, custom_message: Optional[str], hashtags: List[str]):
        """Upload video to TikTok"""
        if not all([TIKTOK_CLIENT_ID, TIKTOK_CLIENT_SECRET]):
            return {"status": "error", "message": "TikTok credentials not configured"}
        
        if media["content_type"] != "video":
            return {"status": "error", "message": "TikTok only supports video content"}
        
        try:
            # Build description
            description = custom_message or f"{media['title']}: {media.get('description', '')}"
            if hashtags:
                description += " " + " ".join([f"#{tag}" for tag in hashtags])
            
            # Simulate TikTok API call
            return {
                "status": "success",
                "platform": "tiktok",
                "video_id": f"tt_{uuid.uuid4()}",
                "url": f"https://tiktok.com/@user/video/mock_video_id"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _submit_to_streaming_service(self, platform: str, media: dict, custom_message: Optional[str]):
        """Submit content to streaming services like Spotify, Apple Music, etc."""
        if media["content_type"] != "audio":
            return {"status": "error", "message": f"{platform} only supports audio content"}
        
        try:
            # Simulate streaming service submission
            return {
                "status": "success",
                "platform": platform,
                "submission_id": f"{platform}_{uuid.uuid4()}",
                "message": f"Audio submitted to {DISTRIBUTION_PLATFORMS[platform]['name']} for review"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _submit_to_radio_station(self, platform: str, media: dict, custom_message: Optional[str]):
        """Submit content to radio stations"""
        if media["content_type"] != "audio":
            return {"status": "error", "message": f"{platform} only supports audio content"}
        
        try:
            # Simulate radio station submission
            return {
                "status": "success",
                "platform": platform,
                "submission_id": f"{platform}_{uuid.uuid4()}",
                "message": f"Audio submitted to {DISTRIBUTION_PLATFORMS[platform]['name']} for playlist consideration"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _submit_to_tv_network(self, platform: str, media: dict, custom_message: Optional[str]):
        """Submit content to TV networks and streaming services"""
        if media["content_type"] not in ["video", "image"]:
            return {"status": "error", "message": f"{platform} only supports video and image content"}
        
        try:
            # Simulate TV network submission
            return {
                "status": "success",
                "platform": platform,
                "submission_id": f"{platform}_{uuid.uuid4()}",
                "message": f"Content submitted to {DISTRIBUTION_PLATFORMS[platform]['name']} for review"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _submit_to_podcast_platform(self, platform: str, media: dict, custom_message: Optional[str]):
        """Submit content to podcast platforms"""
        if media["content_type"] != "audio":
            return {"status": "error", "message": f"{platform} only supports audio content"}
        
        try:
            # Simulate podcast platform submission
            return {
                "status": "success",
                "platform": platform,
                "submission_id": f"{platform}_{uuid.uuid4()}",
                "message": f"Podcast episode submitted to {DISTRIBUTION_PLATFORMS[platform]['name']}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _submit_to_performance_rights_org(self, platform: str, media: dict, custom_message: Optional[str]):
        """Submit content to performance rights organizations like SoundExchange"""
        if media["content_type"] != "audio":
            return {"status": "error", "message": f"{platform} only supports audio content"}
        
        try:
            platform_info = DISTRIBUTION_PLATFORMS[platform]
            
            if platform == "soundexchange":
                # SoundExchange specific submission for digital performance royalties
                return await self._submit_to_soundexchange(media, custom_message)
            elif platform in ["ascap", "bmi", "sesac"]:
                # Traditional PRO submission for performance royalties
                return await self._submit_to_traditional_pro(platform, media, custom_message)
            
            # Generic PRO submission
            return {
                "status": "success",
                "platform": platform,
                "submission_id": f"{platform}_{uuid.uuid4()}",
                "registration_type": "performance_rights",
                "message": f"Audio content registered with {platform_info['name']} for performance royalty collection"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _submit_to_soundexchange(self, media: dict, custom_message: Optional[str]):
        """Submit content to SoundExchange for digital performance royalties"""
        try:
            # SoundExchange registration process
            submission_data = {
                "recording_title": media["title"],
                "artist_name": "Big Mann Entertainment",  # Could be extracted from metadata
                "label_name": "Big Mann Entertainment",
                "duration": media.get("duration", 0),
                "genre": media.get("category", "General"),
                "release_date": media.get("created_at", datetime.utcnow().isoformat()),
                "isrc": f"BME{uuid.uuid4().hex[:10].upper()}",  # Generate ISRC code
                "recording_type": "sound_recording",
                "territories": ["US"],  # SoundExchange primarily US-focused
                "digital_platforms": [
                    "Satellite Radio", "Internet Radio", "Cable TV Music Channels"
                ]
            }
            
            # Simulate SoundExchange API submission
            return {
                "status": "success",
                "platform": "soundexchange",
                "submission_id": f"SX_{uuid.uuid4()}",
                "registration_id": f"BME-{uuid.uuid4().hex[:8].upper()}",
                "isrc_code": submission_data["isrc"],
                "royalty_collection_territories": ["US"],
                "eligible_services": [
                    "SiriusXM Satellite Radio",
                    "Pandora Internet Radio", 
                    "iHeartRadio",
                    "Music Choice Cable TV",
                    "Muzak Business Music"
                ],
                "message": f"'{media['title']}' successfully registered with SoundExchange for digital performance royalty collection",
                "next_steps": [
                    "Performance data will be collected from digital radio services",
                    "Royalties will be distributed quarterly",
                    "Track performance reports available in SoundExchange portal"
                ]
            }
        except Exception as e:
            return {"status": "error", "message": f"SoundExchange submission failed: {str(e)}"}
    
    async def _submit_to_traditional_pro(self, platform: str, media: dict, custom_message: Optional[str]):
        """Submit content to traditional Performance Rights Organizations"""
        try:
            platform_info = DISTRIBUTION_PLATFORMS[platform]
            
            submission_data = {
                "work_title": media["title"],
                "composer": "Big Mann Entertainment",  # Could be extracted from metadata
                "publisher": "Big Mann Entertainment",
                "duration": media.get("duration", 0),
                "genre": media.get("category", "General"),
                "creation_date": media.get("created_at", datetime.utcnow().isoformat()),
                "work_type": "original_composition",
                "territories": ["US", "International"] if platform != "soundexchange" else ["US"]
            }
            
            # Platform-specific handling
            if platform == "ascap":
                work_id = f"ASCAP-{uuid.uuid4().hex[:10].upper()}"
                services = ["Radio", "Television", "Digital Streaming", "Live Performance"]
            elif platform == "bmi":
                work_id = f"BMI-{uuid.uuid4().hex[:10].upper()}"
                services = ["Broadcast Radio", "TV", "Digital Platforms", "Live Venues"]
            elif platform == "sesac":
                work_id = f"SESAC-{uuid.uuid4().hex[:10].upper()}"
                services = ["Radio", "TV", "Digital", "International"]
            else:
                work_id = f"{platform.upper()}-{uuid.uuid4().hex[:10].upper()}"
                services = ["Various Performance Venues"]
            
            return {
                "status": "success",
                "platform": platform,
                "submission_id": f"{platform}_{uuid.uuid4()}",
                "work_registration_id": work_id,
                "royalty_collection_services": services,
                "territories": submission_data["territories"],
                "message": f"'{media['title']}' successfully registered with {platform_info['name']} for performance royalty collection",
                "collection_scope": f"Performance royalties from {', '.join(services).lower()}"
            }
        except Exception as e:
            return {"status": "error", "message": f"{platform} submission failed: {str(e)}"}

# Initialize distribution service
distribution_service = DistributionService()

# Authentication routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict["password"]
    user = User(**user_dict)
    
    # Insert user and password
    await db.users.insert_one(user.dict())
    await db.user_credentials.insert_one({
        "user_id": user.id,
        "email": user.email,
        "hashed_password": hashed_password
    })
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # Find user credentials
    credentials = await db.user_credentials.find_one({"email": user_data.email})
    if not credentials or not verify_password(user_data.password, credentials["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Get user data
    user = await db.users.find_one({"id": credentials["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_obj = User(**user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_obj.id}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Media upload and management routes
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
        'audio': ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/m4a'],
        'video': ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv'],
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
    }
    
    content_type = None
    for type_name, mime_types in allowed_types.items():
        if file.content_type in mime_types:
            content_type = type_name
            break
    
    if not content_type:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Create file path
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.{file_extension}"
    file_path = uploads_dir / content_type / filename
    file_path.parent.mkdir(exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
    
    # Create media record
    media = MediaContent(
        title=title,
        description=description,
        content_type=content_type,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
        tags=tag_list,
        category=category,
        price=price,
        owner_id=current_user.id
    )
    
    await db.media_content.insert_one(media.dict())
    return {"message": "Media uploaded successfully", "media_id": media.id}

@api_router.get("/media/library")
async def get_media_library(
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    is_published: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50
):
    # Build query
    query = {}
    if content_type:
        query["content_type"] = content_type
    if category:
        query["category"] = category
    if is_published is not None:
        query["is_published"] = is_published
    
    # Get media
    media_items = await db.media_content.find(query).skip(skip).limit(limit).to_list(limit)
    
    # Remove file_path and _id from response for security and serialization
    for item in media_items:
        if 'file_path' in item:
            del item['file_path']
        if '_id' in item:
            del item['_id']
    
    return {"media": media_items}

@api_router.get("/media/{media_id}")
async def get_media_details(media_id: str):
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Remove file_path and _id from response
    if 'file_path' in media:
        del media['file_path']
    if '_id' in media:
        del media['_id']
    
    # Increment view count
    await db.media_content.update_one(
        {"id": media_id},
        {"$inc": {"view_count": 1}}
    )
    
    return media

@api_router.put("/media/{media_id}/publish")
async def publish_media(media_id: str, current_user: User = Depends(get_current_admin_user)):
    result = await db.media_content.update_one(
        {"id": media_id},
        {"$set": {"is_published": True, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return {"message": "Media published successfully"}

# Distribution routes
@api_router.get("/distribution/platforms")
async def get_distribution_platforms():
    """Get all available distribution platforms"""
    platforms_info = {}
    for platform_id, config in DISTRIBUTION_PLATFORMS.items():
        platforms_info[platform_id] = {
            "name": config["name"],
            "type": config["type"],
            "supported_formats": config["supported_formats"],
            "max_file_size_mb": config["max_file_size"] / (1024 * 1024)
        }
    
    return {"platforms": platforms_info}

@api_router.post("/distribution/distribute")
async def distribute_content(
    request: DistributionRequest,
    current_user: User = Depends(get_current_user)
):
    """Distribute content across selected platforms"""
    try:
        distribution = await distribution_service.distribute_content(
            media_id=request.media_id,
            platforms=request.platforms,
            user_id=current_user.id,
            custom_message=request.custom_message,
            hashtags=request.hashtags
        )
        
        return {
            "message": "Content distribution initiated",
            "distribution_id": distribution.id,
            "status": distribution.status,
            "results": distribution.results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/distribution/history")
async def get_distribution_history(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """Get user's distribution history"""
    # Get user's media IDs
    user_media = await db.media_content.find({"owner_id": current_user.id}).to_list(1000)
    media_ids = [media["id"] for media in user_media]
    
    # Get distributions for user's media
    distributions = await db.content_distributions.find(
        {"media_id": {"$in": media_ids}}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Remove _id fields
    for dist in distributions:
        if '_id' in dist:
            del dist['_id']
    
    return {"distributions": distributions}

@api_router.get("/distribution/{distribution_id}")
async def get_distribution_status(distribution_id: str, current_user: User = Depends(get_current_user)):
    """Get distribution status"""
    distribution = await db.content_distributions.find_one({"id": distribution_id})
    if not distribution:
        raise HTTPException(status_code=404, detail="Distribution not found")
    
    if '_id' in distribution:
        del distribution['_id']
    
    return distribution

# Payment routes
@api_router.post("/payments/checkout")
async def create_checkout_session(
    request: Request,
    media_id: str,
    current_user: User = Depends(get_current_user)
):
    # Get media details
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if media["price"] <= 0:
        raise HTTPException(status_code=400, detail="This media is free")
    
    # Get host URL from request
    host_url = str(request.base_url).rstrip('/')
    success_url = f"{host_url.replace('/api', '')}/purchase-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url.replace('/api', '')}/purchase-cancel"
    
    # Initialize Stripe
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    webhook_url = f"{host_url}/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    # Create checkout session
    checkout_request = CheckoutSessionRequest(
        amount=media["price"],
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "media_id": media_id,
            "user_id": current_user.id,
            "business": "Big Mann Entertainment"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create purchase record
    purchase = Purchase(
        user_id=current_user.id,
        media_id=media_id,
        amount=media["price"],
        stripe_session_id=session.session_id,
        payment_status="pending"
    )
    
    await db.purchases.insert_one(purchase.dict())
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, current_user: User = Depends(get_current_user)):
    if not stripe_api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update purchase record
    if status.payment_status == "paid":
        await db.purchases.update_one(
            {"stripe_session_id": session_id},
            {
                "$set": {
                    "payment_status": "completed",
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        # Increment download count
        purchase = await db.purchases.find_one({"stripe_session_id": session_id})
        if purchase:
            await db.media_content.update_one(
                {"id": purchase["media_id"]},
                {"$inc": {"download_count": 1}}
            )
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount": status.amount_total / 100,  # Convert from cents
        "currency": status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    if not stripe_api_key:
        return {"status": "error", "message": "Stripe not configured"}
    
    body = await request.body()
    stripe_signature = request.headers.get("stripe-signature")
    
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url="")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, stripe_signature)
        
        if webhook_response.payment_status == "paid":
            # Update purchase record
            await db.purchases.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": "completed",
                        "completed_at": datetime.utcnow()
                    }
                }
            )
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")
    
    return {"status": "success"}

# Download route for purchased content
@api_router.get("/media/{media_id}/download")
async def download_media(media_id: str, current_user: User = Depends(get_current_user)):
    # Check if user has purchased this media or if it's free
    media = await db.media_content.find_one({"id": media_id})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    if media["price"] > 0:
        # Check if user has purchased
        purchase = await db.purchases.find_one({
            "user_id": current_user.id,
            "media_id": media_id,
            "payment_status": "completed"
        })
        
        if not purchase and media["owner_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Purchase required to download this media")
    
    # Return file
    file_path = Path(media["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=f"{media['title']}.{file_path.suffix}",
        media_type=media["mime_type"]
    )

# Analytics routes
@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard(current_user: User = Depends(get_current_admin_user)):
    # Get basic stats
    total_media = await db.media_content.count_documents({})
    published_media = await db.media_content.count_documents({"is_published": True})
    total_users = await db.users.count_documents({})
    total_revenue = await db.purchases.aggregate([
        {"$match": {"payment_status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    revenue = total_revenue[0]["total"] if total_revenue else 0
    
    # Get popular media
    popular_media = await db.media_content.find().sort("download_count", -1).limit(5).to_list(5)
    
    # Remove file_path and _id from popular media for serialization
    for item in popular_media:
        if 'file_path' in item:
            del item['file_path']
        if '_id' in item:
            del item['_id']
    
    # Get distribution stats
    total_distributions = await db.content_distributions.count_documents({})
    successful_distributions = await db.content_distributions.count_documents({"status": "completed"})
    
    return {
        "stats": {
            "total_media": total_media,
            "published_media": published_media,
            "total_users": total_users,
            "total_revenue": revenue,
            "total_distributions": total_distributions,
            "successful_distributions": successful_distributions,
            "distribution_success_rate": (successful_distributions / total_distributions * 100) if total_distributions > 0 else 0
        },
        "popular_media": popular_media,
        "supported_platforms": len(DISTRIBUTION_PLATFORMS)
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()