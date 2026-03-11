from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
from enum import Enum

class DDEXMessageType(str, Enum):
    ERN = "ERN"  # Electronic Release Notification
    DSR = "DSR"  # Digital Sales Report
    CWR = "CWR"  # Common Works Registration
    MWN = "MWN"  # Musical Work Notification

class ReleaseType(str, Enum):
    ALBUM = "Album"
    SINGLE = "Single"
    EP = "EP"
    COMPILATION = "Compilation"
    LIVE = "Live"
    REMIX = "Remix"
    SOUNDTRACK = "Soundtrack"

class TerritoryCode(str, Enum):
    WORLDWIDE = "Worldwide"
    US = "US"
    CA = "CA" 
    GB = "GB"
    DE = "DE"
    FR = "FR"
    JP = "JP"
    AU = "AU"

class RightsType(str, Enum):
    PERMANENT_DOWNLOAD = "PermanentDownload"
    CONDITIONAL_DOWNLOAD = "ConditionalDownload"
    NON_INTERACTIVE_STREAM = "NonInteractiveStream"
    ON_DEMAND_STREAM = "OnDemandStream"
    USER_DEFINED = "UserDefined"

# DDEX Party (Label, Artist, etc.)
class DDEXParty(BaseModel):
    party_id: str = Field(default_factory=lambda: f"PARTY_{uuid.uuid4().hex[:8].upper()}")
    party_name: str
    party_type: str  # Label, Artist, Distributor, Publisher, etc.
    dpid: Optional[str] = None  # DDEX Party Identifier
    isni: Optional[str] = None  # International Standard Name Identifier
    ipi: Optional[str] = None   # Interested Parties Information
    ipn: Optional[str] = None   # IPI Name Number
    
    # Contact information
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    
    # Business identifiers
    tax_id: Optional[str] = None
    business_registration: Optional[str] = None

# DDEX Resource (Audio, Video, Image)
class DDEXResource(BaseModel):
    resource_id: str = Field(default_factory=lambda: f"R{uuid.uuid4().hex[:12].upper()}")
    resource_type: str  # SoundRecording, Video, Image, Text, Software
    title: str
    duration: Optional[str] = None  # ISO 8601 duration format (PT3M30S)
    
    # Technical details
    file_path: str
    mime_type: str
    file_size: int
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    
    # Identifiers
    isrc: Optional[str] = None  # International Standard Recording Code
    grid: Optional[str] = None  # Global Release Identifier
    
    # Contributors
    artists: List[DDEXParty] = []
    contributors: List[Dict[str, Any]] = []  # Producer, Composer, etc.
    
    # Rights and metadata
    copyright_year: Optional[int] = None
    production_year: Optional[int] = None
    parental_warning_type: Optional[str] = "NotExplicit"
    genre: Optional[str] = None
    sub_genre: Optional[str] = None
    
class DDEXRelease(BaseModel):
    release_id: str = Field(default_factory=lambda: f"R{uuid.uuid4().hex[:8].upper()}")
    release_type: ReleaseType
    title: str
    display_artist: str
    label_name: str
    
    # Identifiers
    grid: Optional[str] = None  # Global Release Identifier
    icpn: Optional[str] = None  # International Cataloguing of Products Number
    ean: Optional[str] = None   # European Article Number
    upc: Optional[str] = None   # Universal Product Code
    catalog_number: Optional[str] = None
    
    # Dates
    release_date: date
    original_release_date: Optional[date] = None
    
    # Commercial details
    suggested_retail_price: Optional[float] = None
    wholesale_price: Optional[float] = None
    currency: str = "USD"
    
    # Resources and tracks
    resources: List[DDEXResource] = []
    track_listing: List[Dict[str, Any]] = []
    
    # Rights and territories
    territories: List[TerritoryCode] = [TerritoryCode.WORLDWIDE]
    rights_granted: List[RightsType] = []
    
    # Parties
    rights_controller: Optional[DDEXParty] = None
    marketing_label: Optional[DDEXParty] = None
    distributor: Optional[DDEXParty] = None

class DDEXMusicalWork(BaseModel):
    work_id: str = Field(default_factory=lambda: f"MW{uuid.uuid4().hex[:8].upper()}")
    title: str
    sub_title: Optional[str] = None
    
    # Identifiers
    iswc: Optional[str] = None  # International Standard Musical Work Code
    work_number: Optional[str] = None
    
    # Contributors
    composers: List[DDEXParty] = []
    lyricists: List[DDEXParty] = []
    arrangers: List[DDEXParty] = []
    publishers: List[DDEXParty] = []
    
    # Rights information
    copyright_owner: Optional[DDEXParty] = None
    copyright_year: Optional[int] = None
    publishing_rights_owner: Optional[DDEXParty] = None
    
    # Performance rights organizations
    performing_rights_society: Optional[str] = None  # ASCAP, BMI, SESAC, etc.
    mechanical_rights_society: Optional[str] = None
    
    # Usage information
    duration: Optional[str] = None
    key: Optional[str] = None
    tempo: Optional[str] = None
    time_signature: Optional[str] = None

class DDEXMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"MSG_{uuid.uuid4()}")
    message_type: DDEXMessageType
    message_version: str = "4.1"
    created_datetime: datetime = Field(default_factory=datetime.utcnow)
    
    # Sender and recipient
    sender_name: str = "Big Mann Entertainment"
    sender_id: str = "BME001"
    recipient_name: Optional[str] = None
    recipient_id: Optional[str] = None
    
    # Message content
    release: Optional[DDEXRelease] = None
    musical_works: List[DDEXMusicalWork] = []
    deals: List[Dict[str, Any]] = []  # Commercial terms
    
    # Technical details
    schema_version_id: str = "41"
    business_profile_type: str = "CommonReleaseTypes"
    
class DDEXSalesReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"RPT_{uuid.uuid4().hex[:8].upper()}")
    report_type: str = "SalesReport"
    reporting_period_start: date
    reporting_period_end: date
    
    # Reporting parties
    message_sender: DDEXParty
    message_recipient: DDEXParty
    sales_reporting_party: DDEXParty
    
    # Sales data
    sales_transactions: List[Dict[str, Any]] = []
    usage_data: List[Dict[str, Any]] = []
    
class DDEXWorkRegistration(BaseModel):
    registration_id: str = Field(default_factory=lambda: f"WRK_{uuid.uuid4().hex[:8].upper()}")
    work: DDEXMusicalWork
    
    # Registration details
    registration_date: date = Field(default_factory=date.today)
    registration_territory: TerritoryCode = TerritoryCode.US
    performing_rights_organization: str  # ASCAP, BMI, SESAC
    
    # Rights splits
    writer_splits: List[Dict[str, Any]] = []  # Writer shares
    publisher_splits: List[Dict[str, Any]] = []  # Publisher shares
    
    # Administrative details
    submitter: DDEXParty
    contact_info: Dict[str, str]