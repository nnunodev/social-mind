"""Pydantic schemas for validation and serialization."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


# ========================================
# Analytics Schemas
# ========================================

class AnalyticsRecordBase(BaseModel):
    date: datetime
    content_type: Optional[str] = None
    title: Optional[str] = None
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    platform_data: Dict[str, Any] = {}


class AnalyticsRecordCreate(AnalyticsRecordBase):
    pass


class AnalyticsRecordResponse(AnalyticsRecordBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uploaded_data_id: int


class UploadedDataBase(BaseModel):
    filename: str
    platform: str
    row_count: int = 0


class UploadedDataCreate(UploadedDataBase):
    file_path: str
    processed_data: Dict[str, Any] = {}


class UploadedDataResponse(UploadedDataBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    upload_date: datetime
    processed_data: Dict[str, Any]


class UploadedDataWithRecords(UploadedDataResponse):
    analytics_records: List[AnalyticsRecordResponse] = []


class AnalyticsSummary(BaseModel):
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    avg_engagement_rate: float
    top_performing_content: List[AnalyticsRecordResponse]
    growth_by_date: List[Dict[str, Any]]


# ========================================
# Hook Generator Schemas
# ========================================

class HookGenerateRequest(BaseModel):
    topic: str
    tone: str = "professional"  # casual, professional, dramatic, funny, inspirational
    platform: str  # youtube, instagram, tiktok, twitter
    count: int = 5
    keywords: List[str] = []


class HookBase(BaseModel):
    topic: str
    tone: str
    platform: str
    hook_text: str
    tags: List[str] = []


class HookCreate(HookBase):
    pass


class HookResponse(HookBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    used: int
    is_favorite: bool


class HookUpdate(BaseModel):
    hook_text: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None


# ========================================
# Calendar Schemas
# ========================================

class CalendarItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    platform: str
    content_type: str
    scheduled_date: datetime
    status: str = "draft"
    caption: Optional[str] = None
    hashtags: List[str] = []
    media_urls: List[str] = []


class CalendarItemCreate(CalendarItemBase):
    hook_id: Optional[int] = None


class CalendarItemResponse(CalendarItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    hook_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]


class CalendarItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None


class CalendarView(BaseModel):
    date: datetime
    items: List[CalendarItemResponse]


# ========================================
# Template Schemas
# ========================================

class TemplateBase(BaseModel):
    name: str
    platform: str
    content_type: str
    template: str
    variables: List[str] = []
    tags: List[str] = []


class TemplateCreate(TemplateBase):
    pass


class TemplateResponse(TemplateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


# ========================================
# Common Schemas
# ========================================

class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class CSVUploadResponse(BaseModel):
    success: bool
    records_processed: int
    uploaded_data_id: int
    message: str
