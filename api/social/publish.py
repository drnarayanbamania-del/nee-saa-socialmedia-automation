"""
Bamania's Cine AI - Social Media Publish API
FastAPI endpoint for publishing videos to social media platforms
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio

# Import publishing coordinator
from social_publishers.publishing_coordinator import PublishingCoordinator, PublishingJob

# Import authentication
from auth.jwt_handler import get_current_user

# Import database
from database.db_manager import DatabaseManager

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/social", tags=["Social Publishing"])

# Pydantic models
class PublishRequest(BaseModel):
    """Request model for publishing video"""
    video_id: str
    platforms: List[str]  # youtube, instagram, facebook
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    scheduled_for: Optional[datetime] = None
    template_id: Optional[str] = None
    auto_publish: bool = False  # Publish immediately after generation

class PublishResponse(BaseModel):
    """Response model for publishing"""
    status: str
    message: str
    job_id: Optional[str] = None
    platforms: Dict[str, Dict] = {}

class ConnectAccountRequest(BaseModel):
    """Request model for connecting social account"""
    platform: str  # youtube, instagram, facebook
    code: str  # OAuth authorization code
    state: str  # OAuth state token

class AccountResponse(BaseModel):
    """Response model for account operations"""
    status: str
    account: Optional[Dict] = None
    accounts: Optional[List[Dict]] = None
    auth_url: Optional[str] = None

# Initialize coordinator (singleton)
coordinator = None
db_manager = None

def get_coordinator():
    """Get or create publishing coordinator"""
    global coordinator, db_manager
    
    if coordinator is None:
        db_manager = DatabaseManager()
        coordinator = PublishingCoordinator(db_manager)
    
    return coordinator

@router.post("/publish", response_model=PublishResponse)
async def publish_video(
    request: PublishRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Publish a video to social media platforms
    
    - **video_id**: ID of the video to publish
    - **platforms**: List of platforms (youtube, instagram, facebook)
    - **caption**: Custom caption (optional)
    - **hashtags**: List of hashtags (optional)
    - **scheduled_for**: Schedule for future publishing (optional)
    - **template_id**: Use a saved template (optional)
    - **auto_publish**: Publish immediately after generation (optional)
    """
    try:
        coordinator = get_coordinator()
        user_id = current_user['user_id']
        
        logger.info(f"Publishing request from user {user_id}: {request}")
        
        # Get video details
        video_query = """
            SELECT id, title, caption, hashtags, file_path, metadata
            FROM videos
            WHERE id = %s AND user_id = %s
        """
        
        video_results = db_manager.execute_query(video_query, (request.video_id, user_id))
        
        if not video_results:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video = video_results[0]
        
        # Prepare hashtags
        hashtags = request.hashtags or video['hashtags'] or []
        if isinstance(hashtags, str):
            hashtags = hashtags.split(',')
        
        # Prepare caption
        caption = request.caption or video['caption'] or video['title']
        
        # Create publishing job
        job = PublishingJob(
            video_id=video['id'],
            user_id=user_id,
            video_file=video['file_path'],
            title=video['title'],
            caption=caption,
            hashtags=hashtags,
            platforms=request.platforms,
            scheduled_for=request.scheduled_for,
            template_id=request.template_id
        )
        
        # If scheduled, just schedule it
        if request.scheduled_for:
            queue_id = coordinator.schedule_video(job)
            
            return PublishResponse(
                status="scheduled",
                message=f"Video scheduled for {request.scheduled_for}",
                job_id=queue_id,
                platforms={platform: {"status": "scheduled"} for platform in request.platforms}
            )
        
        # Otherwise, publish now in background
        background_tasks.add_task(coordinator.publish_video, job)
        
        return PublishResponse(
            status="processing",
            message="Video publishing started in background",
            platforms={platform: {"status": "processing"} for platform in request.platforms}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Publish endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/connect/{platform}", response_model=AccountResponse)
async def connect_account(
    platform: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Start OAuth flow to connect a social media account
    
    - **platform**: Platform to connect (youtube, instagram, facebook)
    """
    try:
        if platform not in ['youtube', 'instagram', 'facebook']:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        coordinator = get_coordinator()
        user_id = current_user['user_id']
        
        # Get current base URL
        base_url = str(request.base_url).rstrip('/')
        redirect_uri = f"{base_url}/api/v1/social/callback/{platform}"
        
        # Generate auth URL
        if platform == 'youtube':
            auth_url, state = coordinator.youtube.get_auth_url(user_id, redirect_uri)
        elif platform == 'instagram':
            auth_url, state = coordinator.instagram.get_auth_url(user_id)
        elif platform == 'facebook':
            auth_url, state = coordinator.facebook.get_auth_url(user_id)
        
        # Store state in database for security
        store_state_query = """
            INSERT INTO oauth_states (state, user_id, platform, expires_at)
            VALUES (%s, %s, %s, NOW() + INTERVAL '10 minutes')
        """
        db_manager.execute_query(store_state_query, (state, user_id, platform))
        
        return AccountResponse(
            status="auth_required",
            auth_url=auth_url
        )
        
    except Exception as e:
        logger.error(f"Connect account error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback/{platform}")
async def oauth_callback(
    platform: str,
    code: str,
    state: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Handle OAuth callback from social media platforms
    """
    try:
        if platform not in ['youtube', 'instagram', 'facebook']:
            raise HTTPException(status_code=400, detail="Invalid platform")
        
        coordinator = get_coordinator()
        user_id = current_user['user_id']
        
        # Verify state token
        verify_state_query = """
            SELECT * FROM oauth_states
            WHERE state = %s AND user_id = %s AND platform = %s
              AND expires_at > NOW()
        """
        
        state_results = db_manager.execute_query(verify_state_query, (state, user_id, platform))
        
        if not state_results:
            raise HTTPException(status_code=400, detail="Invalid or expired state token")
        
        # Get base URL for redirect
        base_url = str(request.base_url).rstrip('/').replace('/api/v1/social/callback/' + platform, '')
        redirect_uri = f"{base_url}/api/v1/social/callback/{platform}"
        
        # Handle OAuth callback
        if platform == 'youtube':
            account_data = coordinator.youtube.handle_oauth_callback(
                state, code, redirect_uri
            )
        elif platform == 'instagram':
            account_data = coordinator.instagram.handle_oauth_callback(code, state)
        elif platform == 'facebook':
            account_data = coordinator.facebook.handle_oauth_callback(code, state)
        
        # Store account in database
        insert_account_query = """
            INSERT INTO social_accounts (
                user_id, platform, account_name, account_username,
                access_token, refresh_token, token_expires_at,
                platform_user_id, page_id, channel_id,
                profile_picture_url, follower_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, platform, platform_user_id)
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                token_expires_at = EXCLUDED.token_expires_at,
                is_valid = true,
                last_validated_at = NOW(),
                updated_at = NOW()
            RETURNING id
        """
        
        creds = account_data['credentials']
        
        account_id = db_manager.execute_query(insert_account_query, (
            user_id,
            platform,
            account_data['account_name'],
            account_data['account_username'],
            creds['access_token'],
            creds.get('refresh_token'),
            account_data['token_expires_at'],
            account_data['platform_user_id'],
            account_data.get('page_id'),
            account_data.get('channel_id'),
            account_data.get('profile_picture_url'),
            account_data.get('follower_count', 0)
        ))[0]['id']
        
        # Clean up state token
        delete_state_query = "DELETE FROM oauth_states WHERE state = %s"
        db_manager.execute_query(delete_state_query, (state,))
        
        # Redirect to dashboard with success
        dashboard_url = f"{base_url}/dashboard.html?connected={platform}"
        return JSONResponse(
            status_code=302,
            headers={"Location": dashboard_url},
            content={"message": f"Successfully connected {platform} account"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        # Redirect to dashboard with error
        base_url = str(request.base_url).rstrip('/').replace('/api/v1/social/callback/' + platform, '')
        dashboard_url = f"{base_url}/dashboard.html?error={platform}"
        return JSONResponse(
            status_code=302,
            headers={"Location": dashboard_url},
            content={"message": f"Failed to connect {platform} account"}
        )

@router.get("/accounts", response_model=AccountResponse)
async def get_connected_accounts(current_user: dict = Depends(get_current_user)):
    """Get all connected social media accounts for user"""
    try:
        user_id = current_user['user_id']
        
        query = """
            SELECT id, platform, account_name, account_username,
                   profile_picture_url, follower_count, is_active,
                   created_at
            FROM social_accounts
            WHERE user_id = %s AND is_valid = true
            ORDER BY platform, created_at DESC
        """
        
        results = db_manager.execute_query(query, (user_id,))
        
        accounts = []
        for row in results:
            accounts.append({
                'id': str(row['id']),
                'platform': row['platform'],
                'account_name': row['account_name'],
                'account_username': row['account_username'],
                'profile_picture_url': row['profile_picture_url'],
                'follower_count': row['follower_count'],
                'is_active': row['is_active'],
                'created_at': row['created_at'].isoformat()
            })
        
        return AccountResponse(
            status="success",
            accounts=accounts
        )
        
    except Exception as e:
        logger.error(f"Get accounts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/accounts/{account_id}", response_model=AccountResponse)
async def disconnect_account(
    account_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Disconnect a social media account"""
    try:
        user_id = current_user['user_id']
        
        # Verify account belongs to user
        verify_query = """
            SELECT id FROM social_accounts 
            WHERE id = %s AND user_id = %s
        """
        
        results = db_manager.execute_query(verify_query, (account_id, user_id))
        
        if not results:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Deactivate account
        update_query = """
            UPDATE social_accounts 
            SET is_active = false, is_valid = false
            WHERE id = %s
        """
        
        db_manager.execute_query(update_query, (account_id,))
        
        return AccountResponse(
            status="success",
            message="Account disconnected successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disconnect account error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_publishing_stats(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get publishing statistics for user"""
    try:
        coordinator = get_coordinator()
        user_id = current_user['user_id']
        
        stats = coordinator.get_publishing_stats(user_id, days)
        
        return {
            "status": "success",
            "stats": stats,
            "days": days
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))