from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    PREMIUM = "premium"

class ContentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

class Platform(str, enum.Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    api_key = Column(String, unique=True, index=True)
    credits = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topics = relationship("Topic", back_populates="user")
    scripts = relationship("Script", back_populates="user")
    videos = relationship("Video", back_populates="user")
    automations = relationship("AutomationJob", back_populates="user")
    published_content = relationship("PublishedContent", back_populates="user")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    source = Column(String)  # youtube, news, twitter, etc.
    source_url = Column(String)
    trend_score = Column(Float, default=0.0)
    keywords = Column(JSON)  # Array of keywords
    category = Column(String)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="topics")
    scripts = relationship("Script", back_populates="topic")

class Script(Base):
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    hook = Column(Text)  # Opening hook
    scenes = Column(JSON)  # Array of scene objects
    duration_estimate = Column(Integer)  # in seconds
    tone = Column(String)  # professional, casual, funny, etc.
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scripts")
    topic = relationship("Topic", back_populates="scripts")
    video = relationship("Video", back_populates="script", uselist=False)

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    script_id = Column(Integer, ForeignKey("scripts.id"))
    prompt = Column(Text, nullable=False)
    image_url = Column(String)
    storage_path = Column(String)
    scene_number = Column(Integer)
    style = Column(String)  # cinematic, cartoon, realistic, etc.
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    video = relationship("Video", back_populates="image")

class VoiceFile(Base):
    __tablename__ = "voice_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    script_id = Column(Integer, ForeignKey("scripts.id"))
    text = Column(Text, nullable=False)
    voice_url = Column(String)
    storage_path = Column(String)
    voice_id = Column(String)  # ElevenLabs voice ID
    settings = Column(JSON)  # Voice settings
    duration = Column(Float)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    video = relationship("Video", back_populates="voice")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    script_id = Column(Integer, ForeignKey("scripts.id"))
    image_id = Column(Integer, ForeignKey("images.id"))
    voice_id = Column(Integer, ForeignKey("voice_files.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    video_url = Column(String)
    storage_path = Column(String)
    thumbnail_url = Column(String)
    duration = Column(Float)
    resolution = Column(String)  # 1080p, 720p, etc.
    file_size = Column(Integer)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="videos")
    script = relationship("Script", back_populates="video")
    image = relationship("Image", back_populates="video")
    voice = relationship("VoiceFile", back_populates="video")
    published_content = relationship("PublishedContent", back_populates="video")

class AutomationJob(Base):
    __tablename__ = "automation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    workflow_config = Column(JSON)  # Complete workflow configuration
    schedule = Column(String)  # cron expression
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="automations")
    executions = relationship("JobExecution", back_populates="job")

class JobExecution(Base):
    __tablename__ = "job_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("automation_jobs.id"))
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    result = Column(JSON)
    
    # Relationships
    job = relationship("AutomationJob", back_populates="executions")

class PublishedContent(Base):
    __tablename__ = "published_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    platform = Column(SQLEnum(Platform), nullable=False)
    platform_post_id = Column(String)  # ID from the platform
    title = Column(String)
    description = Column(Text)
    tags = Column(JSON)  # Array of hashtags
    publish_url = Column(String)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.SCHEDULED)
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="published_content")
    video = relationship("Video", back_populates="published_content")

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("published_content.id"))
    platform = Column(SQLEnum(Platform))
    metric_type = Column(String)  # views, likes, engagement, etc.
    value = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    content = relationship("PublishedContent")
