"""Database models for Social Mind."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class UploadedData(Base):
    """Model for uploaded CSV analytics data."""
    __tablename__ = "uploaded_data"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False)  # "youtube", "instagram", "tiktok"
    upload_date = Column(DateTime, default=datetime.utcnow)
    row_count = Column(Integer, default=0)
    processed_data = Column(JSON, default=dict)
    
    # Relationships
    analytics_records = relationship("AnalyticsRecord", back_populates="uploaded_data", cascade="all, delete-orphan")


class AnalyticsRecord(Base):
    """Individual analytics records from uploaded data."""
    __tablename__ = "analytics_records"
    
    id = Column(Integer, primary_key=True, index=True)
    uploaded_data_id = Column(Integer, ForeignKey("uploaded_data.id"), nullable=False)
    
    # Common metrics
    date = Column(DateTime, nullable=False)
    content_type = Column(String(50), nullable=True)  # "video", "image", "story", "post"
    title = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Platform-specific fields (stored as JSON)
    platform_data = Column(JSON, default=dict)
    
    # Relationship
    uploaded_data = relationship("UploadedData", back_populates="analytics_records")


class GeneratedHook(Base):
    """Generated content hooks."""
    __tablename__ = "generated_hooks"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(Text, nullable=False)
    tone = Column(String(50), default="professional")  # "casual", "professional", "dramatic", "funny"
    platform = Column(String(50), nullable=False)
    hook_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used = Column(Integer, default=0)  # Times used
    is_favorite = Column(Integer, default=0)
    tags = Column(JSON, default=list)


class ContentCalendarItem(Base):
    """Scheduled content for the calendar."""
    __tablename__ = "content_calendar_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    platform = Column(String(50), nullable=False)
    content_type = Column(String(50), nullable=False)  # "video", "image", "post", "story"
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="draft")  # "draft", "scheduled", "published", "cancelled"
    
    # Content details
    hook_id = Column(Integer, ForeignKey("generated_hooks.id"), nullable=True)
    media_urls = Column(JSON, default=list)
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    hook = relationship("GeneratedHook")


class ContentTemplate(Base):
    """Reusable content templates."""
    __tablename__ = "content_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    content_type = Column(String(50), nullable=False)
    template = Column(Text, nullable=False)
    variables = Column(JSON, default=list)  # Variable names for the template
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlatformConfig(Base):
    """Platform-specific configuration."""
    __tablename__ = "platform_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False, unique=True)
    api_key = Column(String(500), nullable=True)
    api_secret = Column(String(500), nullable=True)
    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)
    config_data = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
