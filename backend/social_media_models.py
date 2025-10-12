"""
SQLAlchemy Models for Social Media Integration
Includes: OAuth Tokens, Social Connections, Posts, Metrics
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, Boolean, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pg_database import Base
import uuid
from datetime import datetime, timezone

def generate_uuid():
    return str(uuid.uuid4())

# OAuth Token Storage (Encrypted)
class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)  # twitter, facebook, etc.
    
    # Encrypted token fields
    access_token = Column(Text, nullable=False)  # Will be encrypted
    refresh_token = Column(Text)  # Will be encrypted
    token_type = Column(String, default="Bearer")
    expires_at = Column(DateTime(timezone=True))
    scope = Column(String)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("UserProfile", back_populates="oauth_tokens", lazy="joined")

# Social Media Connection
class SocialConnection(Base):
    __tablename__ = "social_connections"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)
    
    # Platform-specific data
    platform_user_id = Column(String, nullable=False)
    username = Column(String)
    display_name = Column(String)
    profile_image_url = Column(String)
    profile_data = Column(JSON, default=dict)  # Store additional profile info
    
    # Connection status
    is_active = Column(Boolean, default=True)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    last_sync = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("UserProfile", back_populates="social_connections", lazy="joined")
    connection_posts = relationship("SocialPost", back_populates="connection", lazy="dynamic")

# Social Media Post
class SocialPost(Base):
    __tablename__ = "social_posts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("user_profiles.id"), nullable=False, index=True)
    connection_id = Column(String, ForeignKey("social_connections.id"))
    
    # Content
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=list)  # List of media URLs
    platforms = Column(JSON, default=list)  # List of platforms ['twitter', 'facebook']
    
    # Platform-specific post IDs
    platform_post_ids = Column(JSON, default=dict)  # {'twitter': 'tweet_id', 'facebook': 'post_id'}
    
    # Scheduling
    scheduled_for = Column(DateTime(timezone=True))
    posted_at = Column(DateTime(timezone=True))
    
    # Status: draft, scheduled, posted, failed
    status = Column(String, default="draft", index=True)
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("UserProfile", back_populates="social_posts", lazy="joined")
    connection = relationship("SocialConnection", back_populates="connection_posts", lazy="joined")
    metrics = relationship("SocialMetric", back_populates="post", lazy="dynamic")

# Social Media Metrics
class SocialMetric(Base):
    __tablename__ = "social_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("social_posts.id"), nullable=False, index=True)
    provider = Column(String, nullable=False, index=True)
    
    # Engagement metrics
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)
    retweets = Column(Integer, default=0)  # Twitter-specific
    quote_tweets = Column(Integer, default=0)  # Twitter-specific
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Additional metrics data (platform-specific)
    metrics_data = Column(JSON, default=dict)
    
    # Timestamps
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("SocialPost", back_populates="metrics")

# Webhook Event Log
class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=generate_uuid)
    provider = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    
    # Payload
    payload = Column(JSON, nullable=False)
    signature = Column(String)
    
    # Processing
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    # Metadata
    received_at = Column(DateTime(timezone=True), server_default=func.now())
