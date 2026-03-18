from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4
import os
import json

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Bamania's Cine AI API",
    version="2.0.0",
    description="Production API for Bamania's Cine AI — AI-Powered Cinematic Video Studio"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Config ─────────────────────────────────────────────────────────────────────
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "bca-demo-key-2025")
ENVIRONMENT   = os.getenv("ENVIRONMENT", "production")
OPENAI_KEY    = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_KEY= os.getenv("ELEVENLABS_API_KEY", "")

# ── In-memory store (replace with DB in production) ───────────────────────────
DB: Dict[str, Any] = {
    "users": {
        "demo@bamaniacineai.com": {
            "id": "user_001",
            "name": "Dr. Narayan Bamania",
            "email": "demo@bamaniacineai.com",
            "password": "demo123",
            "plan": "Pro",
            "credits": 153,
            "total_credits": 1000,
            "avatar": "N",
        }
    },
    "projects": [
        {
            "id": "p1", "title": "The Rise of AI Revolution 2025",
            "topic": "AI Technology", "status": "Ready",
            "duration": "2:45", "resolution": "4K", "ratio": "9:16",
            "platform": "YouTube Shorts", "views": "847K", "likes": "52K",
            "comments": "3.4K", "videoLength": "short", "category": "Technology",
            "createdAt": "Jan 15, 2025 • 10:30 AM",
            "thumbnail": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=400&h=700&fit=crop",
            "videoUrl": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
        },
        {
            "id": "p2", "title": "Quantum Computing Breakthrough",
            "topic": "Science & Tech", "status": "Ready",
            "duration": "3:12", "resolution": "4K", "ratio": "9:16",
            "platform": "YouTube Shorts", "views": "623K", "likes": "41K",
            "comments": "2.8K", "videoLength": "short", "category": "Science",
            "createdAt": "Jan 15, 2025 • 07:15 AM",
            "thumbnail": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=700&fit=crop",
            "videoUrl": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
        },
        {
            "id": "p3", "title": "Future of Space Exploration",
            "topic": "Space & Cosmos", "status": "Scheduled",
            "duration": "2:58", "resolution": "4K", "ratio": "9:16",
            "platform": "YouTube Shorts", "views": "0", "likes": "0",
            "comments": "0", "videoLength": "short", "category": "Science",
            "createdAt": "Jan 15, 2025 • 02:20 PM",
            "scheduledFor": "Mar 20, 2025 • 06:00 PM",
            "thumbnail": "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=400&h=700&fit=crop",
            "videoUrl": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
        },
        {
            "id": "p4", "title": "Ancient Civilizations Mysteries",
            "topic": "History & Culture", "status": "Ready",
            "duration": "4:22", "resolution": "2K", "ratio": "16:9",
            "platform": "YouTube", "views": "412K", "likes": "28K",
            "comments": "1.9K", "videoLength": "long", "category": "History",
            "createdAt": "Jan 14, 2025 • 11:45 AM",
            "thumbnail": "https://images.unsplash.com/photo-1568322445389-f64ac2515020?w=400&h=700&fit=crop",
            "videoUrl": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
        },
        {
            "id": "p5", "title": "Morning Routine Secrets",
            "topic": "Motivation", "status": "Ready",
            "duration": "1:58", "resolution": "4K", "ratio": "9:16",
            "platform": "Instagram Reels", "views": "1.2M", "likes": "89K",
            "comments": "5.6K", "videoLength": "short", "category": "Motivation",
            "createdAt": "Jan 13, 2025 • 09:00 AM",
            "thumbnail": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=700&fit=crop",
            "videoUrl": "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
        },
    ],
    "schedules": [],
    "tokens": {}
}

# ── Models ─────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class VideoGenerateRequest(BaseModel):
    topic: str
    platform: str = "youtube_shorts"
    duration_type: str = "short"
    resolution: str = "4k"
    aspect_ratio: str = "9:16"
    voice_gender: str = "male"
    style: str = "cinematic"

class ScheduleRequest(BaseModel):
    project_id: str
    scheduled_for: str
    platforms: List[str] = ["youtube"]

class DeleteProjectRequest(BaseModel):
    project_id: str

class ThumbnailRequest(BaseModel):
    title: str
    topic: str
    style: str = "cinematic"
    color_scheme: str = "purple"

class PublishRequest(BaseModel):
    project_id: str
    platforms: List[str]
    caption: str = ""
    hashtags: List[str] = []

# ── Auth helpers ───────────────────────────────────────────────────────────────
def get_token_user(authorization: Optional[str]) -> Optional[Dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "").strip()
    return DB["tokens"].get(token)

def require_auth(authorization: Optional[str]) -> Dict:
    user = get_token_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required. Please login.")
    return user

def make_token(user: Dict) -> str:
    token = f"bca_{uuid4().hex}"
    DB["tokens"][token] = user
    return token

# ── Auth routes ────────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = DB["users"].get(req.email)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = make_token(user)
    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "plan": user["plan"],
            "credits": user["credits"],
            "total_credits": user["total_credits"],
            "avatar": user["avatar"],
        }
    }

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    if req.email in DB["users"]:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = {
        "id": f"user_{uuid4().hex[:8]}",
        "name": req.name,
        "email": req.email,
        "password": req.password,
        "plan": "Starter",
        "credits": 50,
        "total_credits": 50,
        "avatar": req.name[0].upper(),
    }
    DB["users"][req.email] = user
    token = make_token(user)
    return {
        "status": "success",
        "token": token,
        "user": {k: v for k, v in user.items() if k != "password"}
    }

@app.get("/api/auth/me")
def me(authorization: Optional[str] = Header(default=None)):
    user = require_auth(authorization)
    return {
        "status": "success",
        "user": {k: v for k, v in user.items() if k != "password"}
    }

@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        DB["tokens"].pop(token, None)
    return {"status": "success", "message": "Logged out successfully"}

# ── Projects ───────────────────────────────────────────────────────────────────
@app.get("/api/projects")
def get_projects(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    return {
        "status": "success",
        "projects": DB["projects"],
        "total": len(DB["projects"])
    }

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    before = len(DB["projects"])
    DB["projects"] = [p for p in DB["projects"] if p["id"] != project_id]
    if len(DB["projects"]) == before:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "success", "message": "Project deleted successfully"}

@app.get("/api/projects/{project_id}/download")
def download_project(project_id: str, authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    project = next((p for p in DB["projects"] if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "status": "success",
        "download_url": project.get("videoUrl", "https://samplelib.com/lib/preview/mp4/sample-5s.mp4"),
        "filename": f"{project['title'].replace(' ', '_')}.mp4",
        "size": "12.4 MB"
    }

@app.post("/api/projects/{project_id}/share")
def share_project(project_id: str, authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    project = next((p for p in DB["projects"] if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    share_url = f"https://bamanias-cine-ai.vercel.app/watch/{project_id}"
    return {
        "status": "success",
        "share_url": share_url,
        "title": project["title"]
    }

# ── Video Generation ───────────────────────────────────────────────────────────
@app.post("/api/generate/video")
def generate_video(
    req: VideoGenerateRequest,
    authorization: Optional[str] = Header(default=None)
):
    user = require_auth(authorization)
    if user.get("credits", 0) < 1:
        raise HTTPException(status_code=402, detail="Insufficient credits. Please upgrade your plan.")

    job_id = f"job_{uuid4().hex[:12]}"
    now    = datetime.utcnow()

    titles = {
        "motivation": "Success Secrets That Changed Everything",
        "technology": "The Future of Technology Is Here",
        "health":     "Health Transformation Journey",
        "finance":    "Money Mindset That Creates Wealth",
        "science":    "Science Discoveries That Shocked The World",
    }
    topic_lower = req.topic.lower()
    category = next((k for k in titles if k in topic_lower), "technology")
    title    = titles.get(category, req.topic)

    thumbnails = {
        "motivation": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=700&fit=crop",
        "technology": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=400&h=700&fit=crop",
        "health":     "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=700&fit=crop",
        "finance":    "https://images.unsplash.com/photo-1559526324-593bc073d938?w=400&h=700&fit=crop",
        "science":    "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=700&fit=crop",
    }
    thumbnail = thumbnails.get(category, thumbnails["technology"])

    new_project = {
        "id":          f"p{uuid4().hex[:8]}",
        "title":       title,
        "topic":       req.topic,
        "status":      "Ready",
        "duration":    "1:45" if req.duration_type == "short" else "8:30",
        "resolution":  req.resolution.upper(),
        "ratio":       req.aspect_ratio,
        "platform":    "YouTube Shorts" if req.aspect_ratio == "9:16" else "YouTube",
        "views":       "0",
        "likes":       "0",
        "comments":    "0",
        "videoLength": req.duration_type,
        "category":    category.capitalize(),
        "createdAt":   now.strftime("%b %d, %Y • %I:%M %p"),
        "thumbnail":   thumbnail,
        "videoUrl":    "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
        "job_id":      job_id,
    }

    DB["projects"].insert(0, new_project)

    return {
        "status":  "success",
        "job_id":  job_id,
        "project": new_project,
        "stages": [
            {"name": "Analyzing Topic",   "duration": 2},
            {"name": "Writing Script",    "duration": 5},
            {"name": "Generating Scenes", "duration": 4},
            {"name": "Creating Visuals",  "duration": 8},
            {"name": "Voice Synthesis",   "duration": 6},
            {"name": "Video Composition", "duration": 5},
        ],
        "message": f"Cinematic video '{title}' generated successfully!"
    }

@app.get("/api/generate/progress/{job_id}")
def generation_progress(job_id: str, authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    return {
        "status":     "success",
        "job_id":     job_id,
        "progress":   100,
        "stage":      "completed",
        "percentage": 100,
        "video_url":  "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
    }

# ── Thumbnail ──────────────────────────────────────────────────────────────────
@app.post("/api/generate/thumbnail")
def generate_thumbnail(
    req: ThumbnailRequest,
    authorization: Optional[str] = Header(default=None)
):
    require_auth(authorization)
    images = {
        "cinematic": "https://images.unsplash.com/photo-1518818419601-72c8673f5852?w=1280&h=720&fit=crop",
        "viral":     "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=1280&h=720&fit=crop",
        "minimal":   "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1280&h=720&fit=crop",
        "face":      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1280&h=720&fit=crop",
    }
    return {
        "status":        "success",
        "thumbnail_url": images.get(req.style, images["cinematic"]),
        "title":         req.title,
        "style":         req.style,
        "color_scheme":  req.color_scheme,
        "resolution":    "1280x720",
        "created_at":    datetime.utcnow().isoformat() + "Z",
    }

# ── Viral Content ──────────────────────────────────────────────────────────────
@app.get("/api/viral-content")
def viral_content():
    return {
        "status": "success",
        "youtube_videos": [
            {"id":"y1","title":"Morning Routine Secrets of High Performers","subtitle":"High-retention YouTube Short with strong hook","creator":"Growth Lab","metric":"12M views","duration":"0:58","timeAgo":"2 days ago","score":97,"platform":"youtube"},
            {"id":"y2","title":"AI Tools That Will Replace Old Workflows","subtitle":"Tech trend short performing well across productivity niches","creator":"Tech Insider","metric":"8.5M views","duration":"1:24","timeAgo":"1 day ago","score":93,"platform":"youtube"},
            {"id":"y3","title":"5 Habits That Changed My Life Forever","subtitle":"Personal development with emotional storytelling hook","creator":"Life Mastery","metric":"6.2M views","duration":"2:15","timeAgo":"3 days ago","score":91,"platform":"youtube"},
        ],
        "instagram_reels": [
            {"id":"i1","title":"3 Reel Hooks That Instantly Boost Watch Time","subtitle":"Short-form Instagram structure built around fast hooks","creator":"@growthreels","metric":"3.1M plays","duration":"0:32","timeAgo":"5 hours ago","score":95,"platform":"instagram"},
            {"id":"i2","title":"Luxury Cinematic B-Roll Ideas for Viral Reels","subtitle":"Premium aesthetic transitions and smooth camera movements","creator":"@cinematicpro","metric":"2.8M plays","duration":"0:45","timeAgo":"8 hours ago","score":91,"platform":"instagram"},
            {"id":"i3","title":"Behind The Scenes of Viral Content Creation","subtitle":"Authentic BTS content showing the creative process","creator":"@creatorlife","metric":"1.9M plays","duration":"1:12","timeAgo":"12 hours ago","score":89,"platform":"instagram"},
        ],
        "total": 6,
        "last_updated": datetime.utcnow().isoformat() + "Z",
    }

# ── Schedule ───────────────────────────────────────────────────────────────────
@app.get("/api/schedule")
def get_schedules(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    return {
        "status":    "success",
        "schedules": DB["schedules"],
        "total":     len(DB["schedules"])
    }

@app.post("/api/schedule")
def create_schedule(
    req: ScheduleRequest,
    authorization: Optional[str] = Header(default=None)
):
    require_auth(authorization)
    project = next((p for p in DB["projects"] if p["id"] == req.project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    schedule = {
        "id":           f"sch_{uuid4().hex[:8]}",
        "project_id":   req.project_id,
        "project_title":project["title"],
        "scheduled_for":req.scheduled_for,
        "platforms":    req.platforms,
        "status":       "scheduled",
        "created_at":   datetime.utcnow().isoformat() + "Z",
    }
    DB["schedules"].append(schedule)
    project["status"]       = "Scheduled"
    project["scheduledFor"] = req.scheduled_for

    return {"status": "success", "schedule": schedule, "message": "Post scheduled successfully!"}

@app.delete("/api/schedule/{schedule_id}")
def delete_schedule(schedule_id: str, authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    sch = next((s for s in DB["schedules"] if s["id"] == schedule_id), None)
    if not sch:
        raise HTTPException(status_code=404, detail="Schedule not found")
    DB["schedules"] = [s for s in DB["schedules"] if s["id"] != schedule_id]
    project = next((p for p in DB["projects"] if p["id"] == sch["project_id"]), None)
    if project:
        project["status"] = "Ready"
        project.pop("scheduledFor", None)
    return {"status": "success", "message": "Schedule removed successfully"}

# ── Publish ────────────────────────────────────────────────────────────────────
@app.post("/api/publish")
def publish(
    req: PublishRequest,
    authorization: Optional[str] = Header(default=None)
):
    require_auth(authorization)
    project = next((p for p in DB["projects"] if p["id"] == req.project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    results = {}
    for platform in req.platforms:
        results[platform] = {
            "status":     "published",
            "url":        f"https://{platform}.com/watch/{uuid4().hex[:8]}",
            "published_at": datetime.utcnow().isoformat() + "Z",
        }

    return {
        "status":  "success",
        "results": results,
        "message": f"Published to {', '.join(req.platforms)} successfully!"
    }

# ── Analytics ──────────────────────────────────────────────────────────────────
@app.get("/api/analytics")
def analytics(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    return {
        "status": "success",
        "stats": {
            "total_videos":   len(DB["projects"]),
            "total_views":    "3.1M",
            "total_likes":    "210K",
            "total_comments": "13.7K",
            "scheduled_posts":len([p for p in DB["projects"] if p["status"] == "Scheduled"]),
            "credits_used":   847,
            "credits_total":  1000,
            "success_rate":   94,
        },
        "platform_stats": {
            "youtube":   {"videos": 3, "views": "1.9M", "growth": "+12%"},
            "instagram": {"videos": 2, "views": "1.2M", "growth": "+8%"},
            "facebook":  {"videos": 1, "views": "89K",  "growth": "+3%"},
        },
        "weekly_data": [
            {"day":"Mon","videos":2,"views":45000},
            {"day":"Tue","videos":3,"views":67000},
            {"day":"Wed","videos":1,"views":23000},
            {"day":"Thu","videos":4,"views":89000},
            {"day":"Fri","videos":3,"views":72000},
            {"day":"Sat","videos":5,"views":98000},
            {"day":"Sun","videos":2,"views":41000},
        ]
    }

# ── Voice Test ─────────────────────────────────────────────────────────────────
@app.post("/api/voice/test")
def test_voice(authorization: Optional[str] = Header(default=None)):
    require_auth(authorization)
    return {
        "status":    "success",
        "audio_url": "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3",
        "message":   "Voice test successful! Hindi voice is ready.",
        "provider":  "Edge TTS (Madhur)",
        "language":  "Hindi (hi-IN)"
    }

# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {
        "status":      "healthy",
        "app":         "Bamania's Cine AI",
        "version":     "2.0.0",
        "environment": ENVIRONMENT,
        "openai":      "configured" if OPENAI_KEY else "not configured (using demo)",
        "elevenlabs":  "configured" if ELEVENLABS_KEY else "not configured (using demo)",
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "endpoints": {
            "auth":     ["/api/auth/login", "/api/auth/register", "/api/auth/me"],
            "projects": ["/api/projects", "/api/projects/{id}", "/api/projects/{id}/download"],
            "generate": ["/api/generate/video", "/api/generate/thumbnail"],
            "social":   ["/api/schedule", "/api/publish"],
            "viral":    ["/api/viral-content"],
            "analytics":["/api/analytics"],
        }
    }

@app.get("/")
def root():
    return {"message": "Bamania's Cine AI API v2.0 — Live!", "docs": "/docs"}
