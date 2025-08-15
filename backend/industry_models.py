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
INDUSTRY_PARTNERS = {
    "streaming_platforms": {
        "major": [
            {
                "name": "Spotify",
                "tier": "major",
                "territories": ["global"],
                "supported_formats": ["mp3", "ogg"],
                "monthly_active_users": 500000000,
                "audio_quality": ["96kbps", "160kbps", "320kbps"]
            },
            {
                "name": "Apple Music",
                "tier": "major", 
                "territories": ["global"],
                "supported_formats": ["aac", "alac"],
                "monthly_active_users": 100000000,
                "audio_quality": ["256kbps", "lossless"]
            },
            {
                "name": "Amazon Music",
                "tier": "major",
                "territories": ["global"],
                "supported_formats": ["mp3", "flac"],
                "monthly_active_users": 100000000,
                "audio_quality": ["256kbps", "hd", "ultra_hd"]
            },
            {
                "name": "YouTube Music",
                "tier": "major",
                "territories": ["global"],
                "supported_formats": ["mp3", "aac"],
                "monthly_active_users": 100000000,
                "audio_quality": ["128kbps", "256kbps"]
            },
            {
                "name": "Tidal",
                "tier": "major",
                "territories": ["global"],
                "supported_formats": ["flac", "mqa"],
                "monthly_active_users": 5000000,
                "audio_quality": ["320kbps", "lossless", "master"]
            }
        ],
        "independent": [
            {
                "name": "Bandcamp",
                "tier": "independent",
                "territories": ["global"],
                "supported_formats": ["flac", "mp3", "wav"],
                "audio_quality": ["320kbps", "lossless"]
            },
            {
                "name": "SoundCloud",
                "tier": "independent", 
                "territories": ["global"],
                "supported_formats": ["mp3", "aac"],
                "monthly_active_users": 76000000,
                "audio_quality": ["128kbps"]
            }
        ]
    },
    "record_labels": {
        "major": [
            {
                "name": "Universal Music Group",
                "tier": "major",
                "label_type": "major",
                "territories": ["global"],
                "genres": ["pop", "rock", "hip-hop", "country", "electronic"]
            },
            {
                "name": "Sony Music Entertainment", 
                "tier": "major",
                "label_type": "major",
                "territories": ["global"],
                "genres": ["pop", "rock", "r&b", "country", "classical"]
            },
            {
                "name": "Warner Music Group",
                "tier": "major",
                "label_type": "major", 
                "territories": ["global"],
                "genres": ["pop", "rock", "hip-hop", "alternative", "electronic"]
            }
        ],
        "independent": [
            {
                "name": "Secretly Group",
                "tier": "independent",
                "label_type": "independent",
                "territories": ["US", "UK"],
                "genres": ["indie", "alternative", "electronic"]
            },
            {
                "name": "Epitaph Records",
                "tier": "independent",
                "label_type": "independent",
                "territories": ["global"],
                "genres": ["punk", "alternative", "indie"]
            }
        ]
    },
    "radio_stations": {
        "major": [
            {
                "name": "iHeartRadio",
                "tier": "major",
                "market_size": "major",
                "territories": ["US"],
                "coverage_area": "national"
            },
            {
                "name": "SiriusXM",
                "tier": "major", 
                "market_size": "major",
                "territories": ["US", "CA"],
                "coverage_area": "satellite"
            }
        ]
    },
    "tv_networks": {
        "major": [
            {
                "name": "MTV",
                "tier": "major",
                "network_type": "cable",
                "territories": ["global"],
                "programming_types": ["music_videos", "reality", "awards"]
            },
            {
                "name": "VH1",
                "tier": "major",
                "network_type": "cable", 
                "territories": ["US"],
                "programming_types": ["music", "reality", "documentaries"]
            }
        ]
    },
    "venues": {
        "major": [
            {
                "name": "Madison Square Garden",
                "tier": "major",
                "venue_type": "arena",
                "capacity": 20000,
                "location": {"city": "New York", "state": "NY", "country": "US"}
            },
            {
                "name": "Red Rocks Amphitheatre",
                "tier": "major",
                "venue_type": "outdoor",
                "capacity": 9525,
                "location": {"city": "Morrison", "state": "CO", "country": "US"}
            }
        ]
    },
    "booking_agencies": {
        "major": [
            {
                "name": "Creative Artists Agency (CAA)",
                "tier": "major",
                "agency_size": "major",
                "territories": ["global"],
                "commission_rate": 10.0
            },
            {
                "name": "William Morris Endeavor (WME)",
                "tier": "major", 
                "agency_size": "major",
                "territories": ["global"],
                "commission_rate": 10.0
            }
        ]
    }
}

# Big Mann Entertainment IPI Numbers
BIG_MANN_IPI_NUMBERS = [
    {
        "ipi_number": "813048171",
        "entity_name": "Big Mann Entertainment",
        "entity_type": "company",
        "role": "publisher",
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
        "ipi_number": "578413032",
        "entity_name": "John LeGerron Spivey",
        "entity_type": "individual",
        "role": "songwriter",
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