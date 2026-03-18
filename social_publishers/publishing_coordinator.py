"""
Bamania's Cine AI - Publishing Coordinator
Manages the complete social media publishing workflow
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import publishers
from .youtube_publisher import YouTubePublisher
from .instagram_publisher import InstagramPublisher
from .facebook_publisher import FacebookPublisher

# Import database helpers
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class PublishingJob:
    """Data class for publishing job"""
    video_id: str
    user_id: str
    video_file: str
    title: str
    caption: str
    hashtags: List[str]
    platforms: List[str]
    scheduled_for: Optional[datetime] = None
    template_id: Optional[str] = None

class PublishingCoordinator:
    """Coordinates publishing across multiple social media platforms"""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize publishing coordinator"""
        self.db = db_manager
        self.youtube = YouTubePublisher()
        self.instagram = InstagramPublisher()
        self.facebook = FacebookPublisher()
        
        # Thread pool for concurrent publishing
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Platform-specific limits
        self.platform_limits = {
            'youtube': {
                'daily_limit': 100,
                'title_max': 100,
                'description_max': 5000,
                'min_duration': 1,
                'max_duration': 60
            },
            'instagram': {
                'daily_limit': 50,
                'caption_max': 2200,
                'min_duration': 3,
                'max_duration': 90
            },
            'facebook': {
                'daily_limit': 200,
                'message_max': 5000,
                'title_max': 255,
                'min_duration': 1,
                'max_duration': 240
            }
        }
    
    async def publish_video(self, job: PublishingJob) -> Dict:
        """
        Publish video to multiple platforms
        
        Args:
            job: PublishingJob with video details
            
        Returns:
            Dictionary with publishing results for each platform
        """
        try:
            logger.info(f"Starting publish job for video {job.video_id} to {job.platforms}")
            
            # Validate job
            validation = self._validate_job(job)
            if not validation['valid']:
                return {
                    'status': 'failed',
                    'error': validation['errors'],
                    'platforms': {}
                }
            
            # Get user accounts
            accounts = self._get_user_accounts(job.user_id, job.platforms)
            if not accounts:
                return {
                    'status': 'failed',
                    'error': 'No social accounts connected for selected platforms',
                    'platforms': {}
                }
            
            # Prepare content for each platform
            platform_content = self._prepare_platform_content(job)
            
            # Create publishing queue entry
            queue_id = self._create_queue_entry(job, accounts)
            
            # Publish to each platform concurrently
            tasks = []
            for platform in job.platforms:
                if platform in accounts:
                    task = asyncio.create_task(
                        self._publish_to_platform(
                            platform,
                            accounts[platform],
                            platform_content[platform],
                            job.video_file
                        )
                    )
                    tasks.append((platform, task))
            
            # Wait for all tasks to complete
            results = {}
            for platform, task in tasks:
                try:
                    result = await task
                    results[platform] = result
                    
                    # Update queue entry
                    self._update_queue_status(queue_id, platform, result)
                    
                    # Update analytics
                    if result['status'] == 'published':
                        self._update_analytics(job.user_id, platform, accounts[platform]['id'])
                    
                except Exception as e:
                    logger.error(f"Publishing to {platform} failed: {e}")
                    results[platform] = {
                        'status': 'failed',
                        'error': str(e),
                        'platform': platform
                    }
            
            # Mark queue entry as complete
            self._mark_queue_complete(queue_id, results)
            
            return {
                'status': 'completed',
                'platforms': results,
                'queue_id': str(queue_id)
            }
            
        except Exception as e:
            logger.error(f"Publishing job failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'platforms': {}
            }
    
    def _validate_job(self, job: PublishingJob) -> Dict:
        """Validate publishing job"""
        errors = []
        
        # Check video file exists
        if not os.path.exists(job.video_file):
            errors.append(f"Video file not found: {job.video_file}")
        
        # Validate platforms
        valid_platforms = ['youtube', 'instagram', 'facebook']
        for platform in job.platforms:
            if platform not in valid_platforms:
                errors.append(f"Invalid platform: {platform}")
            
            # Check platform-specific limits
            limits = self.platform_limits.get(platform, {})
            
            # Title/Message length
            if platform == 'youtube':
                if len(job.title) > limits.get('title_max', 100):
                    errors.append(f"YouTube title too long (max {limits['title_max']} chars)")
            elif platform == 'instagram':
                caption = f"{job.caption} {' '.join(job.hashtags)}"
                if len(caption) > limits.get('caption_max', 2200):
                    errors.append(f"Instagram caption too long (max {limits['caption_max']} chars)")
            elif platform == 'facebook':
                if len(job.caption) > limits.get('message_max', 5000):
                    errors.append(f"Facebook message too long (max {limits['message_max']} chars)")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _get_user_accounts(self, user_id: str, platforms: List[str]) -> Dict:
        """Get user's connected social accounts"""
        query = """
            SELECT id, platform, account_name, access_token, refresh_token, 
                   platform_user_id, page_id, channel_id
            FROM social_accounts
            WHERE user_id = %s 
              AND platform = ANY(%s)
              AND is_active = true
              AND is_valid = true
        """
        
        results = self.db.execute_query(query, (user_id, platforms))
        
        accounts = {}
        for row in results:
            platform = row['platform']
            accounts[platform] = {
                'id': row['id'],
                'account_name': row['account_name'],
                'credentials': {
                    'access_token': row['access_token'],
                    'refresh_token': row.get('refresh_token')
                },
                'platform_user_id': row['platform_user_id'],
                'page_id': row.get('page_id'),
                'channel_id': row.get('channel_id')
            }
        
        return accounts
    
    def _prepare_platform_content(self, job: PublishingJob) -> Dict:
        """Prepare platform-specific content"""
        content = {}
        
        # Hashtag string
        hashtag_str = ' '.join(job.hashtags)
        
        for platform in job.platforms:
            if platform == 'youtube':
                content['youtube'] = {
                    'title': f"{job.title} #Shorts",
                    'description': f"{job.caption}\n\n{hashtag_str}",
                    'category_id': '22',  # People & Blogs
                    'privacy_status': 'public'
                }
            elif platform == 'instagram':
                # Instagram allows max 30 hashtags
                ig_hashtags = job.hashtags[:30]
                ig_hashtag_str = ' '.join(ig_hashtags)
                
                content['instagram'] = {
                    'caption': f"{job.caption}\n\n{ig_hashtag_str}"
                }
            elif platform == 'facebook':
                content['facebook'] = {
                    'message': f"{job.caption}\n\n{hashtag_str}",
                    'title': job.title
                }
        
        return content
    
    def _create_queue_entry(self, job: PublishingJob, accounts: Dict) -> str:
        """Create publishing queue entry"""
        query = """
            INSERT INTO publishing_queue (
                video_id, user_id, youtube_destination, 
                instagram_destination, facebook_destination,
                status, scheduled_for
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        queue_id = self.db.execute_query(query, (
            job.video_id,
            job.user_id,
            accounts.get('youtube', {}).get('id'),
            accounts.get('instagram', {}).get('id'),
            accounts.get('facebook', {}).get('id'),
            'scheduled' if job.scheduled_for else 'publishing',
            job.scheduled_for
        ))[0]['id']
        
        return queue_id
    
    async def _publish_to_platform(self, platform: str, account: Dict, 
                                 content: Dict, video_file: str) -> Dict:
        """Publish to a specific platform"""
        try:
            if platform == 'youtube':
                return await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.youtube.upload_short,
                    video_file,
                    content['title'],
                    content['description'],
                    account['credentials'],
                    content['category_id'],
                    content['privacy_status']
                )
            elif platform == 'instagram':
                return await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.instagram.upload_reel,
                    video_file,
                    content['caption'],
                    account['credentials'],
                    account['platform_user_id']
                )
            elif platform == 'facebook':
                return await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.facebook.upload_video,
                    video_file,
                    content['message'],
                    account['credentials'],
                    account['page_id'],
                    content.get('title')
                )
        except Exception as e:
            logger.error(f"Platform publishing error ({platform}): {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'platform': platform
            }
    
    def _update_queue_status(self, queue_id: str, platform: str, result: Dict):
        """Update publishing queue with platform result"""
        # Update based on platform
        column_map = {
            'youtube': 'youtube_video_id',
            'instagram': 'instagram_media_id',
            'facebook': 'facebook_post_id'
        }
        
        if result['status'] == 'published':
            column = column_map.get(platform)
            if column:
                query = f"""
                    UPDATE publishing_queue 
                    SET {column} = %s, status = %s
                    WHERE id = %s
                """
                self.db.execute_query(query, (
                    result.get('video_id') or result.get('media_id') or result.get('post_id'),
                    'publishing',
                    queue_id
                ))
    
    def _update_analytics(self, user_id: str, platform: str, account_id: str):
        """Update publishing analytics"""
        query = """
            INSERT INTO publishing_analytics (user_id, platform, account_id, date, videos_published)
            VALUES (%s, %s, %s, CURRENT_DATE, 1)
            ON CONFLICT (user_id, platform, account_id, date)
            DO UPDATE SET videos_published = publishing_analytics.videos_published + 1,
                         updated_at = NOW()
        """
        
        self.db.execute_query(query, (user_id, platform, account_id))
    
    def _mark_queue_complete(self, queue_id: str, results: Dict):
        """Mark publishing queue entry as complete"""
        # Check if all platforms completed
        all_published = all(
            r.get('status') == 'published' 
            for r in results.values()
        )
        
        status = 'published' if all_published else 'failed'
        
        query = """
            UPDATE publishing_queue 
            SET status = %s, published_at = NOW()
            WHERE id = %s
        """
        
        self.db.execute_query(query, (status, queue_id))
    
    def schedule_video(self, job: PublishingJob) -> str:
        """
        Schedule video for future publishing
        
        Args:
            job: PublishingJob with scheduled_for datetime
            
        Returns:
            Queue ID
        """
        try:
            # Get accounts
            accounts = self._get_user_accounts(job.user_id, job.platforms)
            
            # Create queue entry with scheduled status
            queue_id = self._create_queue_entry(job, accounts)
            
            logger.info(f"Video scheduled for {job.scheduled_for} (Queue ID: {queue_id})")
            
            return queue_id
            
        except Exception as e:
            logger.error(f"Failed to schedule video: {e}")
            raise
    
    async def publish_scheduled_videos(self):
        """Publish videos that are scheduled for now"""
        try:
            # Get due scheduled videos
            query = """
                SELECT q.*, v.file_path, v.title, v.caption, v.hashtags
                FROM publishing_queue q
                JOIN videos v ON q.video_id = v.id
                WHERE q.status = 'scheduled'
                  AND q.scheduled_for <= NOW()
                  AND q.retry_count < q.max_retries
                ORDER BY q.scheduled_for ASC
                LIMIT 10
            """
            
            scheduled_items = self.db.execute_query(query)
            
            for item in scheduled_items:
                try:
                    # Create PublishingJob
                    job = PublishingJob(
                        video_id=item['video_id'],
                        user_id=item['user_id'],
                        video_file=item['file_path'],
                        title=item['title'],
                        caption=item['caption'],
                        hashtags=item['hashtags'],
                        platforms=[]  # Will be determined from destinations
                    )
                    
                    # Determine platforms from destinations
                    if item['youtube_destination']:
                        job.platforms.append('youtube')
                    if item['instagram_destination']:
                        job.platforms.append('instagram')
                    if item['facebook_destination']:
                        job.platforms.append('facebook')
                    
                    # Publish the video
                    result = await self.publish_video(job)
                    
                    logger.info(f"Published scheduled video {item['id']}: {result}")
                    
                except Exception as e:
                    logger.error(f"Failed to publish scheduled video {item['id']}: {e}")
                    
                    # Increment retry count
                    update_query = """
                        UPDATE publishing_queue 
                        SET retry_count = retry_count + 1,
                            error_message = %s,
                            status = CASE 
                                WHEN retry_count >= max_retries THEN 'failed'
                                ELSE 'scheduled'
                            END
                        WHERE id = %s
                    """
                    
                    self.db.execute_query(update_query, (str(e), item['id']))
        
        except Exception as e:
            logger.error(f"Scheduled publishing task failed: {e}")
    
    def get_publishing_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get publishing statistics for user"""
        try:
            query = """
                SELECT 
                    platform,
                    SUM(videos_published) as total_videos,
                    SUM(total_views) as total_views,
                    SUM(total_likes) as total_likes,
                    SUM(total_comments) as total_comments,
                    AVG(engagement_rate) as avg_engagement_rate
                FROM publishing_analytics
                WHERE user_id = %s
                  AND date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY platform
            """
            
            results = self.db.execute_query(query, (user_id, days))
            
            stats = {}
            for row in results:
                platform = row['platform']
                stats[platform] = {
                    'videos_published': int(row['total_videos'] or 0),
                    'total_views': int(row['total_views'] or 0),
                    'total_likes': int(row['total_likes'] or 0),
                    'total_comments': int(row['total_comments'] or 0),
                    'avg_engagement_rate': float(row['avg_engagement_rate'] or 0)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get publishing stats: {e}")
            return {}