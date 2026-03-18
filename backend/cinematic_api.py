"""
Cinematic AI Factory - Enhanced FastAPI Backend
Professional-grade API for cinematic content generation
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Query, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import json
import logging
import uuid
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.workflow_engine import WorkflowEngine
from scraper.trending_scraper import TrendingScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cinematic AI Factory API",
    description="Professional-grade AI automation platform for viral Hindi video creation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
trending_scraper = TrendingScraper()

# Job tracking
active_jobs: Dict[str, Dict] = {}
job_results: Dict[str, Dict] = {}

# Configuration
SHARE_BASE_URL = os.getenv("SHARE_BASE_URL", "http://localhost:8000")

# Enums
class Platform(str, Enum):
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK = "tiktok"

class Category(str, Enum):
    MOTIVATION = "motivation"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    LIFESTYLE = "lifestyle"

class ColorPreset(str, Enum):
    CINEMATIC_BLUE = "cinematic_blue"
    WARM_GOLD = "warm_gold"
    DRAMATIC = "dramatic"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Pydantic models
class ApiKey(BaseModel):
    key: str
    name: str
    permissions: List[str]
    created_at: datetime
    last_used: Optional[datetime]

class GenerateCinematicRequest(BaseModel):
    topic: str = Field(..., description="Video topic in Hindi", min_length=3, max_length=200)
    category: Category = Field(default=Category.MOTIVATION, description="Content category")
    platform: Platform = Field(default=Platform.YOUTUBE_SHORTS, description="Target platform")
    duration: int = Field(default=60, ge=15, le=90, description="Video duration in seconds")
    color_preset: ColorPreset = Field(default=ColorPreset.CINEMATIC_BLUE, description="Color grading preset")
    music_enabled: bool = Field(default=True, description="Add background music")
    thumbnail_enabled: bool = Field(default=True, description="Generate thumbnail")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for completion notification")

class GenerateCinematicResponse(BaseModel):
    success: bool
    job_id: str
    message: str
    estimated_time: int
    status_url: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    outputs: Optional[Dict[str, Any]]
    error: Optional[str]

class TrendingTopic(BaseModel):
    title: str
    description: str
    category: str
    score: float
    source: str
    url: Optional[str]

class TrendingResponse(BaseModel):
    success: bool
    topics: List[TrendingTopic]
    fetched_at: datetime

class WorkflowCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    trigger: str = Field(..., regex="^(manual|scheduled|webhook)$")
    schedule: Optional[str] = Field(None, description="Cron expression for scheduled workflows")
    steps: List[Dict[str, Any]]
    enabled: bool = Field(default=True)

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    trigger: str
    schedule: Optional[str]
    enabled: bool
    created_at: datetime
    last_run: Optional[datetime]
    run_count: int
    success_count: int
    failure_count: int

class StatsResponse(BaseModel):
    total_videos: int
    today_videos: int
    success_rate: float
    active_jobs: int
    average_duration: float
    trending_categories: Dict[str, int]

# Authentication
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify API key from Authorization header"""
    api_key = credentials.credentials
    
    # In production, validate against database
    # For now, using mock validation
    valid_keys = [
        "sk-admin-key-12345",
        "sk-pro-key-67890",
        os.getenv("ADMIN_API_KEY", "sk-admin-cinematic-2024")
    ]
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return api_key

# Background task processor
async def process_cinematic_generation(job_id: str, request: GenerateCinematicRequest):
    """Process cinematic video generation in background"""
    try:
        logger.info(f"[Job {job_id}] Starting cinematic generation for: {request.topic}")
        
        # Update job status
        active_jobs[job_id].update({
            "status": JobStatus.RUNNING,
            "started_at": datetime.now(),
            "progress": 10
        })
        
        # Import and initialize cinematic factory
        from main_cinematic_coordinator import CinematicAIFactory
        factory = CinematicAIFactory()
        
        # Step 1: Generate script (Progress: 10-30%)
        active_jobs[job_id]["progress"] = 20
        logger.info(f"[Job {job_id}] Generating script...")
        
        # Step 2: Generate images (Progress: 30-50%)
        active_jobs[job_id]["progress"] = 40
        logger.info(f"[Job {job_id}] Generating images...")
        
        # Step 3: Generate voice (Progress: 50-70%)
        active_jobs[job_id]["progress"] = 60
        logger.info(f"[Job {job_id}] Generating voice...")
        
        # Step 4: Compose video (Progress: 70-90%)
        active_jobs[job_id]["progress"] = 80
        logger.info(f"[Job {job_id}] Composing video...")
        
        # Generate cinematic content
        result = factory.generate_cinematic_content(
            topic=request.topic,
            category=request.category.value,
            platform=request.platform.value,
            duration=request.duration
        )
        
        if result["status"] == "completed":
            # Update job as completed
            active_jobs[job_id].update({
                "status": JobStatus.COMPLETED,
                "completed_at": datetime.now(),
                "progress": 100,
                "outputs": result["outputs"]
            })
            
            # Store result
            job_results[job_id] = result
            
            logger.info(f"[Job {job_id}] Cinematic generation completed successfully!")
            
            # Send webhook notification if configured
            if request.webhook_url:
                await send_webhook_notification(request.webhook_url, job_id, result)
                
        else:
            # Update job as failed
            active_jobs[job_id].update({
                "status": JobStatus.FAILED,
                "completed_at": datetime.now(),
                "progress": 100,
                "error": result.get("error", "Unknown error")
            })
            
            logger.error(f"[Job {job_id}] Cinematic generation failed: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"[Job {job_id}] Fatal error: {str(e)}")
        
        active_jobs[job_id].update({
            "status": JobStatus.FAILED,
            "completed_at": datetime.now(),
            "progress": 100,
            "error": str(e)
        })

async def send_webhook_notification(webhook_url: str, job_id: str, result: Dict):
    """Send webhook notification on job completion"""
    try:
        import aiohttp
        
        payload = {
            "event": "cinematic_generation_completed",
            "job_id": job_id,
            "status": result["status"],
            "outputs": result.get("outputs", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"[Job {job_id}] Webhook notification sent successfully")
                else:
                    logger.warning(f"[Job {job_id}] Webhook notification failed: {response.status}")
    
    except Exception as e:
        logger.error(f"[Job {job_id}] Failed to send webhook: {str(e)}")

# API Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Cinematic AI Factory API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "generate": "/api/v1/generate-cinematic",
            "jobs": "/api/v1/jobs/{job_id}",
            "trending": "/api/v1/trending",
            "stats": "/api/v1/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "workflow_engine": "operational" if workflow_engine else "degraded",
            "trending_scraper": "operational" if trending_scraper else "degraded"
        }
    }

@app.post("/api/v1/generate-cinematic", response_model=GenerateCinematicResponse)
async def generate_cinematic(
    request: GenerateCinematicRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate cinematic video from topic
    
    - **topic**: Video topic in Hindi (e.g., "सफलता के रहस्य")
    - **category**: Content category
    - **platform**: Target platform
    - **duration**: Video duration (15-90 seconds)
    - **color_preset**: Cinematic color grading style
    - **music_enabled**: Add background music
    - **thumbnail_enabled**: Generate thumbnail
    """
    try:
        # Generate job ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Create job tracking entry
        active_jobs[job_id] = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "progress": 0,
            "outputs": None,
            "error": None,
            "request": request.dict()
        }
        
        # Add background task
        background_tasks.add_task(process_cinematic_generation, job_id, request)
        
        # Return response
        return GenerateCinematicResponse(
            success=True,
            job_id=job_id,
            message="Cinematic generation started successfully",
            estimated_time=300,  # 5 minutes estimated
            status_url=f"/api/v1/jobs/{job_id}"
        )
    
    except Exception as e:
        logger.error(f"Error starting cinematic generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, api_key: str = Depends(verify_api_key)):
    """Get status of a cinematic generation job"""
    try:
        if job_id not in active_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = active_jobs[job_id]
        
        return JobStatusResponse(
            job_id=job["job_id"],
            status=job["status"],
            progress=job["progress"],
            created_at=job["created_at"],
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            outputs=job.get("outputs"),
            error=job.get("error")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trending", response_model=TrendingResponse)
async def get_trending_topics(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Number of topics to return"),
    sources: Optional[str] = Query("youtube,google_trends,twitter", description="Comma-separated source list"),
    api_key: str = Depends(verify_api_key)
):
    """Get trending topics from multiple sources"""
    try:
        source_list = sources.split(",") if sources else ["youtube"]
        
        result = trending_scraper.scrape_trending_topics(
            sources=source_list,
            category=category,
            max_results=limit
        )
        
        if result["success"]:
            # Convert to Pydantic models
            topics = [
                TrendingTopic(
                    title=topic["title"],
                    description=topic.get("description", ""),
                    category=topic.get("category", "unknown"),
                    score=topic.get("score", 0.0),
                    source=topic.get("source", "unknown"),
                    url=topic.get("url")
                )
                for topic in result["topics"]
            ]
            
            return TrendingResponse(
                success=True,
                topics=topics,
                fetched_at=datetime.now()
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to fetch trending topics"))
    
    except Exception as e:
        logger.error(f"Error fetching trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowCreateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new automation workflow"""
    try:
        # Create workflow using engine
        workflow_id = workflow_engine.create_workflow(
            name=request.name,
            description=request.description,
            trigger=request.trigger,
            schedule=request.schedule,
            steps=request.steps
        )
        
        # Get created workflow
        workflow = workflow_engine.workflows[workflow_id]
        
        return WorkflowResponse(
            id=workflow["id"],
            name=workflow["name"],
            description=workflow["description"],
            trigger=workflow["trigger"],
            schedule=workflow.get("schedule"),
            enabled=workflow["enabled"],
            created_at=datetime.fromisoformat(workflow["created_at"]),
            last_run=datetime.fromisoformat(workflow["last_run"]) if workflow["last_run"] else None,
            run_count=workflow["run_count"],
            success_count=workflow["success_count"],
            failure_count=workflow["failure_count"]
        )
    
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, api_key: str = Depends(verify_api_key)):
    """Get workflow details"""
    try:
        if workflow_id not in workflow_engine.workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow = workflow_engine.workflows[workflow_id]
        
        return WorkflowResponse(
            id=workflow["id"],
            name=workflow["name"],
            description=workflow["description"],
            trigger=workflow["trigger"],
            schedule=workflow.get("schedule"),
            enabled=workflow["enabled"],
            created_at=datetime.fromisoformat(workflow["created_at"]),
            last_run=datetime.fromisoformat(workflow["last_run"]) if workflow["last_run"] else None,
            run_count=workflow["run_count"],
            success_count=workflow["success_count"],
            failure_count=workflow["failure_count"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Execute a workflow"""
    try:
        # Execute workflow in background
        background_tasks.add_task(workflow_engine.execute_workflow, workflow_id)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow execution started"
        }
    
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get platform statistics"""
    try:
        # Calculate stats from job history
        total_jobs = len(job_results)
        successful_jobs = sum(1 for job in job_results.values() if job["status"] == "completed")
        
        # Count today's jobs
        today = datetime.now().date()
        today_jobs = sum(
            1 for job in job_results.values()
            if datetime.fromisoformat(job["timestamp"]).date() == today
        )
        
        # Calculate success rate
        success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Count active jobs
        active_count = sum(
            1 for job in active_jobs.values()
            if job["status"] in [JobStatus.PENDING, JobStatus.RUNNING]
        )
        
        return StatsResponse(
            total_videos=successful_jobs,
            today_videos=today_jobs,
            success_rate=round(success_rate, 1),
            active_jobs=active_count,
            average_duration=300,  # 5 minutes average
            trending_categories={
                "motivation": 45,
                "education": 30,
                "entertainment": 25
            }
        )
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    api_key: str = Depends(verify_api_key)
):
    """Get recent activity feed"""
    try:
        # Mock recent activity (in production, query database)
        activities = [
            {
                "title": "Video Generated",
                "description": "सफलता के रहस्य - cinematic video completed",
                "icon": "video",
                "time": "2 minutes ago"
            },
            {
                "title": "Workflow Executed",
                "description": "Daily trending batch completed: 5 videos",
                "icon": "cogs",
                "time": "1 hour ago"
            },
            {
                "title": "Trending Topics Updated",
                "description": "Fetched 25 new trending topics",
                "icon": "fire",
                "time": "3 hours ago"
            }
        ]
        
        return {"activities": activities[:limit]}
    
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Content Library Endpoints
@app.get("/videos", response_model=List[Dict[str, Any]])
async def get_videos(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get all generated videos with metadata
    """
    try:
        verify_token(credentials.credentials)
        
        # Mock data - replace with database query
        videos = [
            {
                "id": "vid_001",
                "title": "सफलता के लिए सुबह की 5 आदतें",
                "description": "जाने सफल लोगों की सुबह की रूटीन के बारे में",
                "duration": 67,
                "status": "completed",
                "thumbnail_url": "/thumbnails/vid_001.jpg",
                "created_at": "2025-11-06T10:30:00",
                "category": "motivation"
            },
            {
                "id": "vid_002", 
                "title": "पैसे बचाने के 10 आसान तरीके",
                "description": "हर महीने पैसे बचाने के स्मार्ट तरीके",
                "duration": 78,
                "status": "completed",
                "thumbnail_url": "/thumbnails/vid_002.jpg",
                "created_at": "2025-11-06T11:45:00",
                "category": "finance"
            },
            {
                "id": "vid_003",
                "title": "हेल्दी डाइट टिप्स",
                "description": "रोजाना की डाइट में शामिल करें ये चीजें",
                "duration": 0,
                "status": "processing",
                "thumbnail_url": null,
                "created_at": "2025-11-06T12:00:00",
                "category": "health"
            }
        ]
        
        return videos
    except Exception as e:
        logger.error(f"Error fetching videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos/{video_id}/download")
async def download_video(
    video_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Download a generated video file
    """
    try:
        verify_token(credentials.credentials)
        
        # Mock video file path - replace with actual file storage
        video_path = f"output/{video_id}.mp4"
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video not found")
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"cinematic_video_{video_id}.mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/videos/{video_id}")
async def delete_video(
    video_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete a video and its associated files
    """
    try:
        verify_token(credentials.credentials)
        
        # Mock deletion - replace with actual file/database deletion
        video_path = f"output/{video_id}.mp4"
        thumbnail_path = f"thumbnails/{video_id}.jpg"
        
        # Delete video file if exists
        if os.path.exists(video_path):
            os.remove(video_path)
        
        # Delete thumbnail if exists
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        
        return {
            "success": True,
            "message": f"Video {video_id} deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/videos/{video_id}/share")
async def share_video(
    video_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate shareable link for a video
    """
    try:
        verify_token(credentials.credentials)
        
        # Generate shareable URL
        share_url = f"{SHARE_BASE_URL}/video/{video_id}"
        
        return {
            "success": True,
            "share_url": share_url,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating share URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent-activity")
async def get_recent_activity(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get recent activity feed
    """
    try:
        verify_token(credentials.credentials)
        
        activities = [
            {
                "title": "Video #128 completed",
                "description": "सुबह की रूटीन",
                "time": "2 minutes ago",
                "icon": "check-circle",
                "type": "success"
            },
            {
                "title": "Trending scraper",
                "description": "Collecting YouTube topics...",
                "time": "5 minutes ago",
                "icon": "sync",
                "type": "info"
            },
            {
                "title": "Video #129 rendering",
                "description": "पैसे बचाने के तरीके • 78%",
                "time": "12 minutes ago",
                "icon": "spinner",
                "type": "warning"
            },
            {
                "title": "Script queued",
                "description": "हेल्दी डाइट टिप्स • Position: 5",
                "time": "18 minutes ago",
                "icon": "queue",
                "type": "info"
            }
        ]
        
        return activities
    except Exception as e:
        logger.error(f"Error fetching recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("🚀 Starting Cinematic AI Factory API...")
        
        # Start workflow engine
        workflow_engine.start()
        
        # Create output directories
        directories = ["output", "logs", "temp", "workflows"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        logger.info("✅ API startup completed")
    
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        logger.info("⏹️ Shutting down Cinematic AI Factory API...")
        
        # Stop workflow engine
        workflow_engine.stop()
        
        logger.info("✅ API shutdown completed")
    
    except Exception as e:
        logger.error(f"❌ Shutdown error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "cinematic_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )