"""
SQLAlchemy Models for Creator Profile System
Includes: User profiles, Assets, Royalties, DAO Governance
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pg_database import Base
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

# Enums
class ProposalStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    APPROVED = "approved"
    REJECTED = "rejected"

class VoteChoice(str, enum.Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

class AssetType(str, enum.Enum):
    MUSIC = "music"
    VIDEO = "video"
    MERCH = "merch"
    IMAGE = "image"

# User Profile Model
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    mongo_user_id = Column(String, unique=True, index=True, nullable=False)  # Link to MongoDB user
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String)
    avatar_url = Column(String)
    tagline = Column(Text)
    bio = Column(Text)
    
    # GS1 Metadata
    gs1_link = Column(String)
    gln = Column(String)  # Global Location Number
    gtin_prefix = Column(String)  # Company prefix for GTINs
    location = Column(String)
    
    # Social Links (JSON array)
    social_links = Column(JSON, default=list)  # [{name, url, icon, connected, access_token}]
    
    # Profile Settings
    profile_public = Column(Boolean, default=True)
    show_earnings = Column(Boolean, default=False)
    show_dao_activity = Column(Boolean, default=True)
    
    # Campaign
    campaign_title = Column(String)
    campaign_description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assets = relationship("Asset", back_populates="user")
    royalties = relationship("Royalty", back_populates="user")
    sponsors = relationship("Sponsor", back_populates="user")
    trace_events = relationship("TraceEvent", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    proposals = relationship("Proposal", back_populates="user")
    votes = relationship("Vote", back_populates="voter")
    # Social media relationships are defined in social_media_models.py

# Asset Model (Music, Video, Merch, etc.)
class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    mongo_media_id = Column(String, index=True)  # Link to MongoDB media collection
    
    title = Column(String, nullable=False)
    description = Column(Text)
    asset_type = Column(String, nullable=False)  # music, video, merch, image
    thumbnail_url = Column(String)
    content_url = Column(String)
    
    # GS1 Identifiers
    gtin = Column(String, unique=True, index=True)  # Global Trade Item Number
    isrc = Column(String)  # International Standard Recording Code (music)
    isan = Column(String)  # International Standard Audiovisual Number (video)
    gdti = Column(String)  # Global Document Type Identifier (images)
    
    # Licensing & Rights
    license = Column(String)
    copyright_notice = Column(String)
    rights_holder = Column(String)
    
    # Engagement Metrics
    engagement_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Smart Contract Status
    contract_status = Column(String)
    contract_address = Column(String)
    blockchain_hash = Column(String)
    
    # Additional data storage
    asset_metadata = Column(JSON, default=dict)  # Flexible metadata storage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserProfile", back_populates="assets")
    royalties = relationship("Royalty", back_populates="asset")

# Royalty Model
class Royalty(Base):
    __tablename__ = "royalties"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"))
    
    contributor_name = Column(String, nullable=False)
    contributor_id = Column(String)  # Link to another user if internal
    amount = Column(Float, nullable=False)
    percentage = Column(Float)  # Percentage of total royalties
    
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    payment_status = Column(String, default="pending")  # pending, processed, paid
    payment_date = Column(DateTime(timezone=True))
    transaction_id = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("UserProfile", back_populates="royalties")
    asset = relationship("Asset", back_populates="royalties")

# Sponsor Model
class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    name = Column(String, nullable=False)
    logo_url = Column(String)
    website_url = Column(String)
    description = Column(Text)
    
    sponsorship_amount = Column(Float)
    sponsorship_start = Column(DateTime(timezone=True))
    sponsorship_end = Column(DateTime(timezone=True))
    
    active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UserProfile", back_populates="sponsors")

# Traceability Event Model (EPCIS-style)
class TraceEvent(Base):
    __tablename__ = "trace_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"))
    
    event_type = Column(String, nullable=False)  # upload, distribution, sale, license, stream
    description = Column(Text, nullable=False)
    platform = Column(String)  # Where the event occurred
    location = Column(String)  # Geographic location
    
    # EPCIS Fields
    epc = Column(String)  # Electronic Product Code
    gln_source = Column(String)  # Source GLN
    gln_destination = Column(String)  # Destination GLN
    
    event_metadata = Column(JSON, default=dict)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UserProfile", back_populates="trace_events")

# Fan Comment Model
class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    commenter_id = Column(String)  # ID of person leaving comment
    commenter_name = Column(String)
    
    text = Column(Text, nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"))
    
    likes = Column(Integer, default=0)
    flagged = Column(Boolean, default=False)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UserProfile", back_populates="comments")

# DAO Proposal Model
class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    proposal_type = Column(String)  # royalty_adjustment, content_approval, policy_change
    
    # Proposal Target
    target_asset_id = Column(String, ForeignKey("assets.id"))
    target_data = Column(JSON, default=dict)  # Flexible data for different proposal types
    
    # Voting Configuration
    voting_power_required = Column(Integer, default=51)  # Percentage required to pass
    quorum_required = Column(Integer, default=10)  # Minimum votes required
    
    status = Column(String, nullable=False, default="open")
    
    # Results
    total_yes = Column(Integer, default=0)
    total_no = Column(Integer, default=0)
    total_abstain = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Smart Contract Integration
    smart_contract_triggered = Column(Boolean, default=False)
    execution_tx_hash = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    voting_ends_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))

    user = relationship("UserProfile", back_populates="proposals")
    votes = relationship("Vote", back_populates="proposal")

# DAO Vote Model
class Vote(Base):
    __tablename__ = "votes"

    id = Column(String, primary_key=True, default=generate_uuid)
    proposal_id = Column(String, ForeignKey("proposals.id"), nullable=False)
    voter_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    choice = Column(String, nullable=False)  # yes, no, abstain
    weight = Column(Integer, default=1)  # Voting power (based on tokens/stake)
    
    comment = Column(Text)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    proposal = relationship("Proposal", back_populates="votes")
    voter = relationship("UserProfile", back_populates="votes")

# Note: SocialConnection model moved to social_media_models.py to avoid conflicts

# DAO Proposal Comment/Discussion Model
class ProposalComment(Base):
    __tablename__ = "proposal_comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    proposal_id = Column(String, ForeignKey("proposals.id"), nullable=False)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False)
    
    comment_text = Column(Text, nullable=False)
    parent_comment_id = Column(String, ForeignKey("proposal_comments.id"))  # For threaded discussions
    
    likes = Column(Integer, default=0)
    flagged = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
