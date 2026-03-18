from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    PREMIUM = "premium"

class ContentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

class Platform(str, Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"

# Authentication schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

# Topic schemas
class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[List[str]] = []

class TopicResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    source: str
    source_url: Optional[str]
    trend_score: float
    keywords: List[str]
    category: Optional[str]
    is_processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Script schemas
class ScriptRequest(BaseModel):
    topic: str
    duration: int = 60
    tone: str = "engaging"
    platform: Platform = Platform.YOUTUBE
    style: Optional[str] = "storytelling"

class ScriptCreate(BaseModel):
    topic_id: int
    title: str
    content: str
    hook: Optional[str] = None
    scenes: Optional[List[Dict[str, Any]]] = []
    duration_estimate: Optional[int] = None
    tone: str = "engaging"

class ScriptResponse(BaseModel):
    id: int
    title: str
    content: str
    hook: Optional[str]
    scenes: List[Dict[str, Any]]
    duration_estimate: Optional[int]
    tone: str
    status: ContentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Image schemas
class ImageRequest(BaseModel):
    prompt: str
    size: Optional[str] = "1792x1024"
    high_quality: bool = True
    style: Optional[str] = "cinematic"
    scene_number: Optional[int] = None

class ImageResponse(BaseModel):
    id: int
    prompt: str
    image_url: Optional[str]
    scene_number: Optional[int]
    style: str
    status: ContentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Voice schemas
class VoiceRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    voice_settings: Optional[Dict[str, Any]] = None
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.75

class VoiceResponse(BaseModel):
    id: int
    text: str
    voice_url: Optional[str]
    duration: Optional[float]
    voice_id: str
    status: ContentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Video schemas
class VideoCreate(BaseModel):
    script_id: int
    title: str
    description: Optional[str] = None
    resolution: Optional[str] = "1080p"

class VideoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    duration: Optional[float]
    resolution: str
    status: ContentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Automation schemas
class AutomationJobCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_config: Dict[str, Any]
    schedule: Optional[str] = None  # cron expression
    is_active: bool = True

class AutomationJobResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    schedule: Optional[str]
    is_active: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    status: ContentStatus
    run_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Publishing schemas
class PublishingRequest(BaseModel):
    video_id: int
    platform: Platform
    title: str
    description: str
    tags: Optional[List[str]] = []
    scheduled_at: Optional[datetime] = None

class PublishedContentResponse(BaseModel):
    id: int
    platform: Platform
    platform_post_id: Optional[str]
    title: str
    description: str
    tags: List[str]
    publish_url: Optional[str]
    status: ContentStatus
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    views: int
    likes: int
    comments: int
    shares: int
    
    class Config:
        from_attributes = True

# Analytics schemas
class AnalyticsResponse(BaseModel):
    id: int
    platform: Platform
    metric_type: str
    value: float
    recorded_at: datetime
    
    class Config:
        from_attributes = True

# Scraper schemas
class ScrapedTopic(BaseModel):
    title: str
    description: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    trend_score: float
    keywords: List[str]
    category: Optional[str] = None

# Webhook schemas
class WebhookPayload(BaseModel):
    event: str
    data: Dict[str, Any]
    timestamp: datetime
