"""
Bamania's Cine AI - YouTube Shorts Publisher
Handles OAuth authentication and video publishing to YouTube Shorts
"""

import os
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import requests

logger = logging.getLogger(__name__)

class YouTubePublisher:
    """Publisher for YouTube Shorts with OAuth 2.0 support"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube.readonly'
    ]
    
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'
    
    def __init__(self, client_secrets_file: str = None):
        """Initialize YouTube publisher"""
        self.client_secrets_file = client_secrets_file or os.getenv(
            'YOUTUBE_CLIENT_SECRETS_FILE', 
            'config/youtube_client_secrets.json'
        )
        self.credentials = None
        self.service = None
        
    def get_auth_url(self, user_id: str, redirect_uri: str) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL for user
        
        Args:
            user_id: Unique identifier for the user
            redirect_uri: URL to redirect after authorization
            
        Returns:
            Tuple of (auth_url, state_token)
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            # Generate state token
            state_token = f"youtube_{user_id}_{int(time.time())}"
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state_token,
                prompt='consent'
            )
            
            logger.info(f"Generated YouTube auth URL for user {user_id}")
            return auth_url, state_token
            
        except Exception as e:
            logger.error(f"Failed to generate YouTube auth URL: {e}")
            raise
    
    def handle_oauth_callback(self, state: str, code: str, 
                            redirect_uri: str) -> Dict:
        """
        Handle OAuth callback and exchange code for tokens
        
        Args:
            state: State token from OAuth flow
            code: Authorization code from Google
            redirect_uri: Redirect URI used in auth
            
        Returns:
            Dictionary with credentials and account info
        """
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secrets_file,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            
            # Get credentials
            credentials = flow.credentials
            
            # Build YouTube service to get channel info
            service = build(
                self.API_SERVICE_NAME, 
                self.API_VERSION, 
                credentials=credentials
            )
            
            # Get channel details
            channels_response = service.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                raise Exception("No YouTube channel found")
            
            channel = channels_response['items'][0]
            
            # Prepare credentials data
            creds_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            return {
                'credentials': creds_data,
                'platform_user_id': channel['id'],
                'account_name': channel['snippet']['title'],
                'account_username': None,  # YouTube uses channel name
                'channel_id': channel['id'],
                'profile_picture_url': channel['snippet']['thumbnails']['high']['url'],
                'follower_count': int(channel['statistics']['subscriberCount']),
                'token_expires_at': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
        except Exception as e:
            logger.error(f"YouTube OAuth callback failed: {e}")
            raise
    
    def refresh_credentials(self, credentials_data: Dict) -> Credentials:
        """Refresh expired credentials"""
        try:
            credentials = Credentials(**credentials_data)
            
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                logger.info("Refreshed YouTube credentials")
            
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to refresh YouTube credentials: {e}")
            raise
    
    def upload_short(self, video_file: str, title: str, description: str,
                    credentials_data: Dict, category_id: str = "22",
                    privacy_status: str = "public") -> Dict:
        """
        Upload a video as YouTube Short
        
        Args:
            video_file: Path to video file
            title: Video title
            description: Video description
            credentials_data: OAuth credentials
            category_id: YouTube category ID
            privacy_status: 'public', 'private', or 'unlisted'
            
        Returns:
            Dictionary with video ID and status
        """
        try:
            # Refresh credentials if needed
            credentials = self.refresh_credentials(credentials_data)
            
            # Build YouTube service
            service = build(
                self.API_SERVICE_NAME, 
                self.API_VERSION, 
                credentials=credentials
            )
            
            # Prepare video metadata for Shorts
            # YouTube Shorts requirements:
            # - Vertical video (9:16)
            # - Duration: 60 seconds or less
            # - Title with #Shorts hashtag
            
            if '#shorts' not in title.lower() and '#short' not in title.lower():
                title += " #Shorts"
            
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # Description limit
                    'categoryId': category_id,
                    'tags': ['Shorts', 'vertical', 'mobile']
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                },
                'contentDetails': {
                    'uploadType': 'shorts'
                }
            }
            
            # Upload video
            media = MediaFileUpload(
                video_file,
                mimetype='video/mp4',
                chunksize=1024*1024,  # 1MB chunks
                resumable=True
            )
            
            # Insert video
            request = service.videos().insert(
                part='snippet,status,contentDetails',
                body=body,
                media_body=media
            )
            
            # Execute upload with progress tracking
            response = None
            attempts = 0
            max_attempts = 3
            
            while response is None and attempts < max_attempts:
                try:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        attempts += 1
                        logger.warning(f"Upload retry {attempts}/{max_attempts}")
                        time.sleep(2  ** attempts)  # Exponential backoff
                    else:
                        raise
            
            if response is None:
                raise Exception("Video upload failed after all retries")
            
            video_id = response['id']
            logger.info(f"Successfully uploaded YouTube Short: {video_id}")
            
            return {
                'video_id': video_id,
                'status': 'published',
                'platform': 'youtube',
                'published_at': datetime.now(timezone.utc).isoformat(),
                'url': f"https://youtube.com/shorts/{video_id}"
            }
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_message = error_content.get('error', {}).get('message', str(e))
            logger.error(f"YouTube API error: {error_message}")
            
            return {
                'status': 'failed',
                'error': error_message,
                'platform': 'youtube'
            }
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            
            return {
                'status': 'failed',
                'error': str(e),
                'platform': 'youtube'
            }
    
    def get_video_analytics(self, video_id: str, credentials_data: Dict) -> Dict:
        """Get analytics for a published video"""
        try:
            credentials = self.refresh_credentials(credentials_data)
            service = build(
                self.API_SERVICE_NAME, 
                self.API_VERSION, 
                credentials=credentials
            )
            
            # Get video statistics
            response = service.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                return {'error': 'Video not found'}
            
            video = response['items'][0]
            stats = video['statistics']
            
            return {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'shares': 0,  # YouTube doesn't provide share count
                'published_at': video['snippet']['publishedAt'],
                'thumbnail_url': video['snippet']['thumbnails']['high']['url']
            }
            
        except Exception as e:
            logger.error(f"Failed to get YouTube analytics: {e}")
            return {'error': str(e)}