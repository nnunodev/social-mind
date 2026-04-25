from enum import Enum


class Platform(str, Enum):
    """Supported social media platforms."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


class ContentType(str, Enum):
    """Types of content."""
    VIDEO = "video"
    IMAGE = "image"
    POST = "post"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"


class Tone(str, Enum):
    """Content tone options."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    DRAMATIC = "dramatic"
    FUNNY = "funny"
    INSPIRATIONAL = "inspirational"


class CalendarStatus(str, Enum):
    """Calendar item statuses."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
