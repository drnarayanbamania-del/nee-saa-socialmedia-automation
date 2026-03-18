"""
Hindi AI Automation Platform - Backend API
FastAPI backend for managing AI content factory
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.workflow_engine import WorkflowEngine, JobStatus
from scraper.trending_scraper import HindiTrendingScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hindi AI Automation Platform API",
    description="AI-powered content factory for generating viral Hindi videos",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances
workflow_engine = WorkflowEngine()
trending_scraper = HindiTrendingScraper()

# Mock user database (in production, use real database)
MOCK_USERS = {
    "sk-admin-key-12345": {
        "id": "admin-user-id",
        "email": "admin@aifactory.com",
        "role": "admin"
    }
}

# Pydantic models
class User(BaseModel):
    id: str
    email: str
    role: str

class GenerateScriptRequest(BaseModel):
    topic: str
    category: str = "general"
    tone: str = "entertaining"
    target_duration: int = 75

class GenerateScriptResponse(BaseModel):
    success: bool
    script: Optional[Dict[str, Any]]
    error: Optional[str]

class TrendingTopicsResponse(BaseModel):
    success: bool
    topics: List[Dict[str, Any]]
    count: int

class ViralContentResponse(BaseModel):
    success: bool
    youtube_videos: List[Dict[str, Any]]
    instagram_reels: List[Dict[str, Any]]
    count: int

class AutomationJobRequest(BaseModel):
    workflow_type: str
    parameters: Dict[str, Any]
    max_retries: int = 3

class AutomationJobResponse(BaseModel):
    success: bool
    job_id: Optional[str]
    status: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

class VideoCompositionRequest(BaseModel):
    script: Dict[str, Any]
    platform: str = "youtube_shorts"
    image_style: str = "cinematic"
    voice_type: str = "female_neutral"

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Authenticate user from API key"""
    try:
        api_key = credentials.credentials
        
        # In production, validate against database
        user_data = MOCK_USERS.get(api_key)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        return User(**user_data)
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# API routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hindi AI Automation Platform API",
        "version": "1.0.0",
        "endpoints": {
            "trending": "/api/v1/trending",
            "generate_script": "/api/v1/generate-script",
            "create_job": "/api/v1/jobs",
            "job_status": "/api/v1/jobs/{job_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "ok",
            "workflow_engine": "ok",
            "redis": "ok"
        }
    }

@app.get("/api/v1/trending", response_model=TrendingTopicsResponse)
async def get_trending_topics(
    limit: int = Query(10, ge=1, le=50),
    categories: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Get trending topics for Hindi content creation
    
    Args:
        limit: Number of topics to return
        categories: Comma-separated list of categories to filter
        
    Returns:
        List of trending topics
    """
    try:
        logger.info(f"Fetching trending topics for user: {current_user.email}")
        
        # Parse categories filter
        category_list = None
        if categories:
            category_list = [cat.strip() for cat in categories.split(",")]
        
        # Get trending topics
        topics = trending_scraper.get_top_topics(
            limit=limit,
            categories=category_list
        )
        
        # Convert to response format
        response_topics = []
        for topic in topics:
            response_topics.append({
                "id": str(topic.topic),
                "topic_en": topic.topic,
                "topic_hi": topic.metadata.get("hindi_topic", topic.topic),
                "category_en": topic.category,
                "category_hi": topic.hindi_category,
                "trending_score": topic.trending_score,
                "source": topic.source,
                "metadata": topic.metadata
            })
        
        return {
            "success": True,
            "topics": response_topics,
            "count": len(response_topics)
        }
        
    except Exception as e:
        logger.error(f"Error fetching trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/viral-content", response_model=ViralContentResponse)
async def get_viral_content(
    current_user: User = Depends(get_current_user)
):
    """Get auto-scraped viral YouTube videos and trending Instagram reels."""
    try:
        logger.info(f"Fetching viral content for user: {current_user.email}")

        youtube_items = trending_scraper.scrape_youtube_viral_videos()
        instagram_items = trending_scraper.scrape_instagram_trending_reels()

        def serialize(items: List[Any]) -> List[Dict[str, Any]]:
            serialized: List[Dict[str, Any]] = []
            for item in items:
                serialized.append({
                    "title_en": item.topic,
                    "title_hi": item.metadata.get("hindi_topic", item.topic),
                    "source": item.source,
                    "category": item.category,
                    "category_hi": item.hindi_category,
                    "trending_score": item.trending_score,
                    "creator": item.metadata.get("creator", "Unknown"),
                    "views": item.metadata.get("views", "N/A"),
                    "duration": item.metadata.get("duration", "Short"),
                    "published": item.metadata.get("published", "recently"),
                    "url": item.metadata.get("url"),
                    "thumbnail": item.metadata.get("thumbnail"),
                    "platform": item.metadata.get("platform"),
                    "content_type": item.metadata.get("content_type"),
                })
            return serialized

        youtube_serialized = serialize(youtube_items)
        instagram_serialized = serialize(instagram_items)

        return {
            "success": True,
            "youtube_videos": youtube_serialized,
            "instagram_reels": instagram_serialized,
            "count": len(youtube_serialized) + len(instagram_serialized),
        }
    except Exception as e:
        logger.error(f"Error fetching viral content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate-script", response_model=GenerateScriptResponse)
async def generate_script(
    request: GenerateScriptRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate Hindi script from topic
    
    Args:
        request: Script generation parameters
        
    Returns:
        Generated script
    """
    try:
        logger.info(f"Generating script for topic: {request.topic}")
        
        # Get OpenAI API key from environment or user settings
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Import and use script generator
        import asyncio
        from ai_engine.script_generator import HindiScriptGenerator
        
        generator = HindiScriptGenerator(api_key=openai_api_key)
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        script = loop.run_until_complete(
            generator.generate_script(
                topic=request.topic,
                category=request.category,
                tone=request.tone,
                target_duration=request.target_duration
            )
        )
        loop.close()
        
        if not script:
            raise HTTPException(status_code=500, detail="Failed to generate script")
        
        return {
            "success": True,
            "script": script.dict(),
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/jobs", response_model=AutomationJobResponse)
async def create_automation_job(
    request: AutomationJobRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new automation job
    
    Args:
        request: Job creation parameters
        
    Returns:
        Created job details
    """
    try:
        logger.info(f"Creating automation job for user: {current_user.email}")
        
        # Ensure OpenAI API key is in parameters
        if "openai_api_key" not in request.parameters:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                request.parameters["openai_api_key"] = openai_api_key
            else:
                raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Create job
        job_id = workflow_engine.create_job(
            workflow_type=request.workflow_type,
            parameters=request.parameters,
            max_retries=request.max_retries
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "pending",
            "result": None,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error creating automation job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}", response_model=AutomationJobResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get automation job status
    
    Args:
        job_id: Job ID
        
    Returns:
        Job status and result
    """
    try:
        logger.info(f"Fetching job status: {job_id}")
        
        status = workflow_engine.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "job_id": status["job_id"],
            "status": status["status"],
            "result": status.get("result"),
            "error": status.get("error_message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/compose-video", response_model=Dict[str, Any])
async def compose_video(
    request: VideoCompositionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Compose video from script and media files
    
    Args:
        request: Video composition parameters
        
    Returns:
        Video path and status
    """
    try:
        logger.info(f"Composing video for user: {current_user.email}")
        
        # Create scenes from script
        scenes = []
        for segment in request.script.get("segments", []):
            scene_number = segment["scene_number"]
            scenes.append({
                "image_path": f"generated_images/scene_{scene_number:02d}.png",
                "audio_path": f"temp_audio/scene_{scene_number:02d}.mp3",
                "hindi_text": segment["hindi_text"],
                "duration": segment["duration_seconds"]
            })
        
        # Compose video
        from ai_engine.video_composer import HindiVideoComposer
        
        composer = HindiVideoComposer()
        video_path = composer.compose_video(
            scenes=scenes,
            output_path=f"final_video_{current_user.id}.mp4",
            platform=request.platform
        )
        
        if not video_path:
            raise HTTPException(status_code=500, detail="Failed to compose video")
        
        return {
            "success": True,
            "video_path": video_path,
            "message": "Video composed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error composing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an automation job
    
    Args:
        job_id: Job ID to cancel
        
    Returns:
        Cancellation status
    """
    try:
        logger.info(f"Cancelling job: {job_id}")
        
        success = workflow_engine.cancel_job(job_id)
        if not success:
            raise HTTPException(status_code=400, detail="Job cannot be cancelled")
        
        return {
            "success": True,
            "message": "Job cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "success": False,
        "error": exc.detail
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )