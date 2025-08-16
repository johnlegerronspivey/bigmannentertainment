from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# Industry Identifiers Models (IPI, ISNI, AARC)
class IndustryIdentifier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_name: str  # Name of the person or organization
    entity_type: str  # "company", "individual", "band", "organization"
    
    # IPI (Interested Parties Information) Numbers
    ipi_number: Optional[str] = None  # IPI number (e.g., 813048171, 578413032)
    ipi_role: Optional[str] = None  # "songwriter", "composer", "lyricist", "publisher", "performer", "producer"
    
    # ISNI (International Standard Name Identifier) Numbers  
    isni_number: Optional[str] = None  # ISNI number (e.g., 0000000491551894)
    isni_status: Optional[str] = "active"  # active, inactive, pending
    
    # AARC (Alliance of Artists and Recording Companies) Numbers
    aarc_number: Optional[str] = None  # AARC number (e.g., RC00002057, FA02933539)
    aarc_type: Optional[str] = None  # "record_company", "featured_artist", "performer"
    
    territory: str = "US"  # Territory where identifiers are registered
    status: str = "active"  # active, inactive, pending, suspended
    contact_info: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Industry Partner Models
class IndustryPartner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # streaming, record_label, radio, tv, venue, booking, etc.
    tier: str  # major, independent, regional, local
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    authentication_type: str = "none"  # none, api_key, oauth, jwt
    status: str = "active"  # active, inactive, pending, suspended
    integration_type: str  # full_api, webhook, manual, scheduled
    supported_formats: List[str] = []  # mp3, wav, flac, mp4, etc.
    content_types: List[str] = []  # audio, video, podcast, live
    territories: List[str] = []  # US, UK, global, etc.
    revenue_share: Optional[float] = None
    contact_info: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    ipi_numbers: List[str] = []  # Associated IPI numbers
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StreamingPlatform(IndustryPartner):
    monthly_active_users: Optional[int] = None
    audio_quality: List[str] = []  # 128kbps, 320kbps, lossless
    video_quality: List[str] = []  # HD, 4K, 8K
    subscription_tiers: List[str] = []
    geographic_coverage: List[str] = []

class RecordLabel(IndustryPartner):
    label_type: str  # major, independent, boutique
    distribution_network: List[str] = []
    artist_roster_size: Optional[int] = None
    genres: List[str] = []

class RadioStation(IndustryPartner):
    frequency: Optional[str] = None
    market_size: str  # major, medium, small
    format: str  # pop, rock, country, talk, etc.
    coverage_area: str
    listener_demographics: Dict[str, Any] = {}

class TVNetwork(IndustryPartner):
    network_type: str  # broadcast, cable, streaming, satellite
    programming_types: List[str] = []
    target_demographics: Dict[str, Any] = {}
    prime_time_slots: List[str] = []

class Venue(IndustryPartner):
    venue_type: str  # arena, theater, club, festival, outdoor
    capacity: Optional[int] = None
    location: Dict[str, str] = {}
    technical_specs: Dict[str, Any] = {}
    booking_calendar: Dict[str, Any] = {}

class BookingAgency(IndustryPartner):
    agency_size: str  # boutique, mid_tier, major
    artist_types: List[str] = []
    commission_rate: Optional[float] = None
    territory_focus: List[str] = []

# Distribution and Content Models
class ContentDistribution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    partner_id: str
    distribution_status: str  # pending, processing, live, failed, removed
    distribution_date: Optional[datetime] = None
    content_url: Optional[str] = None
    partner_content_id: Optional[str] = None
    metadata_mapping: Dict[str, Any] = {}
    performance_metrics: Dict[str, Any] = {}
    revenue_data: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IndustryAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str
    product_id: Optional[str] = None
    date: datetime
    plays: int = 0
    downloads: int = 0
    streams: int = 0
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    revenue: float = 0.0
    territories: Dict[str, int] = {}
    demographics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RevenueTracking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    distribution_id: str
    partner_id: str
    product_id: str
    revenue_type: str  # streaming, download, licensing, sync
    gross_amount: float
    partner_fee: float
    net_amount: float
    currency: str = "USD"
    period_start: datetime
    period_end: datetime
    payout_status: str  # pending, processing, paid, disputed
    payout_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Industry Connection Templates
# Enhanced Entertainment Industry Partners with Photography, Video, Streaming, Gaming
ENTERTAINMENT_INDUSTRY_PARTNERS = {
    # Existing categories
    "streaming_platforms": {
        "major": [
            {"name": "Spotify", "api_endpoint": "https://api.spotify.com/v1", "supported_formats": ["mp3", "flac"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Apple Music", "api_endpoint": "https://api.music.apple.com/v1", "supported_formats": ["mp3", "aac"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Amazon Music", "api_endpoint": "https://api.amazonalexa.com", "supported_formats": ["mp3", "flac"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "YouTube Music", "api_endpoint": "https://developers.google.com/youtube/v3", "supported_formats": ["mp3", "mp4"], "content_types": ["audio", "video"], "territories": ["global"]},
            {"name": "Tidal", "api_endpoint": "https://api.tidal.com/v1", "supported_formats": ["flac", "mp3"], "content_types": ["audio"], "territories": ["global"]}
        ],
        "independent": [
            {"name": "Bandcamp", "api_endpoint": "https://bandcamp.com/api", "supported_formats": ["flac", "mp3"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "SoundCloud", "api_endpoint": "https://api.soundcloud.com", "supported_formats": ["mp3"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Deezer", "api_endpoint": "https://api.deezer.com", "supported_formats": ["mp3"], "content_types": ["audio"], "territories": ["global"]}
        ]
    },
    
    # Professional Photography Services
    "photography_services": {
        "album_cover": [
            {"name": "Album Cover Zone", "specialties": ["album_covers", "single_covers", "EP_covers"], "price_range": "$500-$2500", "territories": ["US", "UK", "global"]},
            {"name": "Creative Alliance", "specialties": ["album_art", "promotional_photos", "band_photography"], "price_range": "$750-$5000", "territories": ["global"]},
            {"name": "Music Photography Co", "specialties": ["conceptual_covers", "artistic_photography"], "price_range": "$1000-$3000", "territories": ["US", "CA"]}
        ],
        "promotional": [
            {"name": "Artist Photo Studio", "specialties": ["headshots", "promotional_photos", "press_photos"], "price_range": "$300-$1500", "territories": ["US"]},
            {"name": "Music Marketing Photos", "specialties": ["social_media_content", "promotional_campaigns"], "price_range": "$400-$2000", "territories": ["global"]},
            {"name": "Professional Music Photography", "specialties": ["artist_portraits", "lifestyle_shots"], "price_range": "$500-$2500", "territories": ["US", "UK"]}
        ],
        "event": [
            {"name": "Concert Photography Network", "specialties": ["live_concerts", "music_festivals", "studio_sessions"], "price_range": "$200-$1000", "territories": ["US"]},
            {"name": "Live Music Photos", "specialties": ["performance_photography", "backstage_photography"], "price_range": "$250-$1200", "territories": ["global"]},
            {"name": "Event Photo Services", "specialties": ["venue_photography", "audience_shots", "atmosphere_capture"], "price_range": "$300-$800", "territories": ["US", "UK", "CA"]}
        ]
    },
    
    # Stock Photography Platforms
    "stock_photography": {
        "major": [
            {"name": "Shutterstock", "api_endpoint": "https://api.shutterstock.com/v2", "commission_rate": "15-40%", "content_types": ["photos", "vectors", "videos"], "territories": ["global"]},
            {"name": "Getty Images", "api_endpoint": "https://api.gettyimages.com/v3", "commission_rate": "20-45%", "content_types": ["photos", "videos", "editorial"], "territories": ["global"]},
            {"name": "Adobe Stock", "api_endpoint": "https://stock.adobe.io/Rest/Media/1", "commission_rate": "33-35%", "content_types": ["photos", "vectors", "videos", "templates"], "territories": ["global"]},
            {"name": "iStock", "api_endpoint": "https://api.istockphoto.com", "commission_rate": "15-25%", "content_types": ["photos", "vectors", "videos"], "territories": ["global"]}
        ],
        "independent": [
            {"name": "Unsplash", "api_endpoint": "https://api.unsplash.com", "commission_rate": "free+attribution", "content_types": ["photos"], "territories": ["global"]},
            {"name": "500px", "api_endpoint": "https://api.500px.com/v1", "commission_rate": "30-60%", "content_types": ["photos"], "territories": ["global"]},
            {"name": "Alamy", "api_endpoint": "https://api.alamy.com", "commission_rate": "40-50%", "content_types": ["photos", "vectors"], "territories": ["global"]}
        ]
    },
    
    # Social Media Photography Platforms
    "social_media_photography": {
        "content_creation": [
            {"name": "Instagram Creator Studio", "api_endpoint": "https://graph.facebook.com/v17.0", "content_types": ["photos", "stories", "reels"], "monetization": ["creator_fund", "brand_partnerships"], "territories": ["global"]},
            {"name": "TikTok Creator Center", "api_endpoint": "https://developers.tiktok.com/doc", "content_types": ["short_videos", "photos"], "monetization": ["creator_fund", "live_gifts"], "territories": ["global"]},
            {"name": "YouTube Thumbnails", "api_endpoint": "https://developers.google.com/youtube/v3", "content_types": ["thumbnails", "channel_art", "community_posts"], "monetization": ["ad_revenue", "memberships"], "territories": ["global"]},
            {"name": "Pinterest Business", "api_endpoint": "https://developers.pinterest.com/docs/api/v5", "content_types": ["pins", "boards", "idea_pins"], "monetization": ["shopping_ads", "promoted_pins"], "territories": ["global"]}
        ],
        "thumbnail_services": [
            {"name": "Thumbnail Creator Pro", "specialties": ["youtube_thumbnails", "podcast_covers", "social_media_graphics"], "price_range": "$25-$150", "territories": ["global"]},
            {"name": "Social Media Graphics Co", "specialties": ["instagram_posts", "story_templates", "tiktok_graphics"], "price_range": "$50-$300", "territories": ["global"]},
            {"name": "Content Creation Studio", "specialties": ["brand_graphics", "promotional_content", "social_campaigns"], "price_range": "$100-$500", "territories": ["US", "UK"]}
        ]
    },
    
    # Film and Video Production
    "video_production": {
        "music_videos": [
            {"name": "Music Video Network", "specialties": ["music_videos", "lyric_videos", "promotional_videos"], "price_range": "$5000-$50000", "territories": ["US", "UK", "CA"]},
            {"name": "Independent Film Collective", "specialties": ["narrative_videos", "conceptual_videos", "documentary"], "price_range": "$3000-$25000", "territories": ["global"]},
            {"name": "Creative Video Solutions", "specialties": ["commercial_videos", "brand_content", "social_video"], "price_range": "$2000-$15000", "territories": ["US"]}
        ],
        "production_companies": [
            {"name": "Major Production Studios", "specialties": ["feature_films", "documentaries", "series"], "price_range": "$100000+", "territories": ["US", "UK"]},
            {"name": "Independent Production", "specialties": ["indie_films", "short_films", "web_series"], "price_range": "$10000-$100000", "territories": ["global"]},
            {"name": "Commercial Production", "specialties": ["commercials", "corporate_videos", "training_videos"], "price_range": "$5000-$50000", "territories": ["US", "UK", "CA"]}
        ]
    },
    
    # Podcast Industry Integration
    "podcast_platforms": {
        "hosting": [
            {"name": "Spotify for Podcasters", "api_endpoint": "https://api.spotify.com/v1", "monetization": ["ad_revenue", "subscriptions"], "content_types": ["audio", "video"], "territories": ["global"]},
            {"name": "Apple Podcasts", "api_endpoint": "https://podcasts.apple.com/us/genre/podcasts", "monetization": ["subscriptions", "premium_content"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Google Podcasts", "api_endpoint": "https://developers.google.com/search/docs/data-types/podcast", "monetization": ["ad_revenue"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Podscribe", "specialties": ["podcast_advertising", "attribution", "analytics"], "monetization": ["programmatic_ads"], "territories": ["US", "UK"]}
        ],
        "production": [
            {"name": "Podcast Production Network", "specialties": ["full_production", "editing", "sound_design"], "price_range": "$500-$5000", "territories": ["US", "UK"]},
            {"name": "Audio Content Creators", "specialties": ["scripting", "voice_over", "post_production"], "price_range": "$300-$3000", "territories": ["global"]},
            {"name": "Podcast Studio Services", "specialties": ["recording", "mixing", "mastering"], "price_range": "$200-$2000", "territories": ["US", "CA"]}
        ]
    },
    
    # Live Streaming Platforms
    "live_streaming": {
        "major": [
            {"name": "Twitch", "api_endpoint": "https://dev.twitch.tv/docs/api", "monetization": ["subscriptions", "bits", "ads"], "content_types": ["live_video", "music", "gaming"], "territories": ["global"]},
            {"name": "YouTube Live", "api_endpoint": "https://developers.google.com/youtube/v3", "monetization": ["super_chat", "memberships", "ads"], "content_types": ["live_video", "music", "educational"], "territories": ["global"]},
            {"name": "Facebook Live", "api_endpoint": "https://developers.facebook.com/docs/live-video-api", "monetization": ["stars", "fan_subscriptions"], "content_types": ["live_video", "music", "events"], "territories": ["global"]},
            {"name": "Instagram Live", "api_endpoint": "https://developers.facebook.com/docs/instagram-api", "monetization": ["badges", "brand_partnerships"], "content_types": ["live_video", "music"], "territories": ["global"]}
        ],
        "music_focused": [
            {"name": "StageIt", "specialties": ["live_concerts", "intimate_performances"], "monetization": ["ticket_sales", "tips"], "territories": ["US", "UK"]},
            {"name": "Bandsintown PLUS", "specialties": ["virtual_concerts", "livestream_events"], "monetization": ["ticket_sales", "merchandise"], "territories": ["global"]},
            {"name": "Veeps", "specialties": ["premium_livestreams", "exclusive_content"], "monetization": ["ticket_sales", "VIP_packages"], "territories": ["global"]}
        ]
    },
    
    # Gaming and Esports Industry
    "gaming_esports": {
        "platforms": [
            {"name": "Steam", "api_endpoint": "https://steamcommunity.com/dev", "content_types": ["game_soundtracks", "audio_content"], "monetization": ["sales", "dlc"], "territories": ["global"]},
            {"name": "Epic Games Store", "specialties": ["game_audio", "soundtrack_distribution"], "monetization": ["revenue_share"], "territories": ["global"]},
            {"name": "Riot Games", "specialties": ["esports_music", "game_soundtracks"], "monetization": ["licensing", "partnerships"], "territories": ["global"]},
            {"name": "Blizzard Entertainment", "specialties": ["game_music", "cinematic_audio"], "monetization": ["licensing"], "territories": ["global"]}
        ],
        "esports_organizations": [
            {"name": "Team Liquid", "specialties": ["team_anthems", "event_music"], "monetization": ["sponsorships", "licensing"], "territories": ["global"]},
            {"name": "Cloud9", "specialties": ["brand_music", "streaming_content"], "monetization": ["partnerships"], "territories": ["US"]},
            {"name": "FaZe Clan", "specialties": ["content_creation", "music_collaborations"], "monetization": ["brand_deals", "merchandise"], "territories": ["global"]}
        ]
    },
    
    # Fashion Photography
    "fashion_photography": {
        "music_fashion": [
            {"name": "Music Style Photography", "specialties": ["artist_styling", "album_fashion", "stage_outfits"], "price_range": "$1000-$10000", "territories": ["US", "UK"]},
            {"name": "Concert Fashion Studios", "specialties": ["performance_wear", "red_carpet", "editorial"], "price_range": "$1500-$8000", "territories": ["global"]},
            {"name": "Artist Brand Photography", "specialties": ["brand_partnerships", "fashion_campaigns"], "price_range": "$2000-$15000", "territories": ["US", "UK", "EU"]}
        ],
        "commercial": [
            {"name": "Brand Photography Network", "specialties": ["merchandise_photography", "product_shoots"], "price_range": "$500-$5000", "territories": ["global"]},
            {"name": "E-commerce Photo Services", "specialties": ["online_store_photos", "lifestyle_photography"], "price_range": "$300-$3000", "territories": ["US", "UK"]},
            {"name": "Fashion Commerce Studios", "specialties": ["lookbook_photography", "catalog_shoots"], "price_range": "$800-$6000", "territories": ["global"]}
        ]
    },
    
    # Existing categories (abbreviated for space)
    "record_labels": {
        "major": [
            {"name": "Universal Music Group", "api_endpoint": None, "supported_formats": ["mp3", "flac", "vinyl"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Sony Music Entertainment", "api_endpoint": None, "supported_formats": ["mp3", "flac", "vinyl"], "content_types": ["audio"], "territories": ["global"]},
            {"name": "Warner Music Group", "api_endpoint": None, "supported_formats": ["mp3", "flac", "vinyl"], "content_types": ["audio"], "territories": ["global"]}
        ]
    }
}

# Big Mann Entertainment Industry Identifiers (IPI, ISNI, AARC)
BIG_MANN_INDUSTRY_IDENTIFIERS = [
    {
        "entity_name": "Big Mann Entertainment",
        "entity_type": "company",
        
        # IPI Information
        "ipi_number": "813048171",
        "ipi_role": "publisher",
        
        # ISNI Information (not applicable for companies typically)
        "isni_number": None,
        "isni_status": None,
        
        # AARC Information  
        "aarc_number": "RC00002057",
        "aarc_type": "record_company",
        
        "territory": "US",
        "status": "active",
        "contact_info": {
            "address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
            "phone": "334-669-8638",
            "email": "info@bigmannentertainment.com"
        },
        "metadata": {
            "registered_date": "2024-01-01",
            "business_type": "Sound Recording Industries",
            "naics_code": "512200"
        }
    },
    {
        "entity_name": "John LeGerron Spivey",
        "entity_type": "individual",
        
        # IPI Information
        "ipi_number": "578413032",
        "ipi_role": "songwriter",
        
        # ISNI Information
        "isni_number": "0000000491551894",
        "isni_status": "active",
        
        # AARC Information
        "aarc_number": "FA02933539", 
        "aarc_type": "featured_artist",
        
        "territory": "US",
        "status": "active",
        "contact_info": {
            "address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
            "phone": "334-669-8638"
        },
        "metadata": {
            "registered_date": "2024-01-01",
            "performing_rights_org": "ASCAP",
            "primary_instrument": "vocals"
        }
    }
]