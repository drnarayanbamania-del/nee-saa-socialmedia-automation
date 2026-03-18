"""
Bamania's Cine AI - Facebook Publisher
Handles OAuth authentication and video publishing to Facebook Pages
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

class FacebookPublisher:
    """Publisher for Facebook Pages via Graph API"""
    
    def __init__(self):
        """Initialize Facebook publisher"""
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.redirect_uri = os.getenv('FACEBOOK_REDIRECT_URI')
        
        if not all([self.app_id, self.app_secret]):
            logger.warning("Facebook credentials not configured")
    
    def get_auth_url(self, user_id: str) -> Tuple[str, str]:
        """
        Generate Facebook OAuth URL for Page publishing
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Tuple of (auth_url, state_token)
        """
        try:
            # Facebook permissions needed for video publishing
            scopes = [
                'pages_show_list',        # View connected pages
                'pages_read_engagement',  # Read page insights
                'pages_manage_posts',     # Publish videos
                'pages_manage_metadata'   # Page information
            ]
            
            # Generate state token
            state_token = f"facebook_{user_id}_{int(time.time())}"
            
            # Build auth URL
            auth_url = (
                f"https://www.facebook.com/v18.0/dialog/oauth?"
                f"client_id={self.app_id}"
                f"&redirect_uri={self.redirect_uri}"
                f"&scope={','.join(scopes)}"
                f"&state={state_token}"
                f"&response_type=code"
            )
            
            logger.info(f"Generated Facebook auth URL for user {user_id}")
            return auth_url, state_token
            
        except Exception as e:
            logger.error(f"Failed to generate Facebook auth URL: {e}")
            raise
    
    def handle_oauth_callback(self, code: str, state: str) -> Dict:
        """
        Handle OAuth callback and get Page access
        
        Args:
            code: Authorization code from Facebook
            state: State token from OAuth flow
            
        Returns:
            Dictionary with credentials and account info
        """
        try:
            # Step 1: Exchange code for User access token
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': code
            }
            
            response = requests.get(token_url, params=params)
            response.raise_for_status()
            
            token_data = response.json()
            user_access_token = token_data['access_token']
            
            # Step 2: Get User's Pages
            pages_url = "https://graph.facebook.com/v18.0/me/accounts"
            params = {
                'access_token': user_access_token,
                'fields': 'id,name,access_token,category,link,picture'
            }
            
            response = requests.get(pages_url, params=params)
            response.raise_for_status()
            
            pages_data = response.json()
            
            if not pages_data.get('data'):
                raise Exception("No Facebook pages found. Please create a page first.")
            
            # Return first page (in production, let user select)
            page = pages_data['data'][0]
            page_access_token = page['access_token']
            
            # Step 3: Get extended Page token (never expires)
            extend_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': page_access_token
            }
            
            response = requests.get(extend_url, params=params)
            response.raise_for_status()
            
            extended_token_data = response.json()
            long_lived_token = extended_token_data['access_token']
            
            return {
                'credentials': {
                    'access_token': long_lived_token,
                    'user_access_token': user_access_token,
                    'token_type': extended_token_data.get('token_type', 'bearer')
                },
                'platform_user_id': page['id'],
                'account_name': page['name'],
                'account_username': None,  # Pages don't have usernames
                'page_id': page['id'],
                'profile_picture_url': page.get('picture', {}).get('data', {}).get('url'),
                'follower_count': 0,  # Will be fetched separately
                'token_expires_at': None  # Extended tokens don't expire
            }
            
        except requests.RequestException as e:
            logger.error(f"Facebook OAuth API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Facebook OAuth callback failed: {e}")
            raise
    
    def refresh_credentials(self, credentials_data: Dict) -> str:
        """
        Refresh Facebook Page access token
        
        Args:
            credentials_data: Current credentials
            
        Returns:
            Valid access token
        """
        try:
            access_token = credentials_data['access_token']
            
            # Debug token to check validity
            debug_url = "https://graph.facebook.com/v18.0/debug_token"
            params = {
                'input_token': access_token,
                'access_token': f"{self.app_id}|{self.app_secret}"
            }
            
            response = requests.get(debug_url, params=params)
            response.raise_for_status()
            
            debug_data = response.json()['data']
            
            if debug_data.get('is_valid'):
                logger.info("Facebook token is valid")
                return access_token
            else:
                raise Exception("Facebook token is invalid")
                
        except Exception as e:
            logger.error(f"Failed to validate Facebook token: {e}")
            raise
    
    def upload_video(self, video_file: str, message: str, 
                     credentials_data: Dict, page_id: str,
                     title: Optional[str] = None) -> Dict:
        """
        Upload video to Facebook Page
        
        Args:
            video_file: Path to video file
            message: Post message/caption
            credentials_data: OAuth credentials
            page_id: Facebook Page ID
            title: Optional video title
            
        Returns:
            Dictionary with post ID and status
        """
        try:
            access_token = credentials_data['access_token']
            
            # Step 1: Start video upload session
            logger.info("Starting Facebook video upload session...")
            
            upload_session_url = f"https://graph.video.facebook.com/v18.0/{page_id}/videos"
            
            with open(video_file, 'rb') as video:
                files = {
                    'video': video
                }
                params = {
                    'access_token': access_token,
                    'description': message,
                    'title': title or message[:100],  # Use first 100 chars if no title
                }
                
                response = requests.post(upload_session_url, params=params, files=files)
                response.raise_for_status()
            
            upload_data = response.json()
            
            if 'id' not in upload_data:
                raise Exception(f"Upload failed: {upload_data}")
            
            video_id = upload_data['id']
            logger.info(f"Video uploaded successfully: {video_id}")
            
            return {
                'post_id': video_id,
                'status': 'published',
                'platform': 'facebook',
                'published_at': datetime.now(timezone.utc).isoformat(),
                'url': f"https://facebook.com/{page_id}/videos/{video_id}"
            }
            
        except requests.RequestException as e:
            logger.error(f"Facebook API request failed: {e}")
            return {
                'status': 'failed',
                'error': f"API request failed: {str(e)}",
                'platform': 'facebook'
            }
            
        except Exception as e:
            logger.error(f"Facebook video upload failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'platform': 'facebook'
            }
    
    def get_post_insights(self, post_id: str, credentials_data: Dict) -> Dict:
        """
        Get insights for published post
        
        Args:
            post_id: Facebook post/video ID
            credentials_data: OAuth credentials
            
        Returns:
            Dictionary with engagement metrics
        """
        try:
            access_token = credentials_data['access_token']
            
            insights_url = f"https://graph.facebook.com/v18.0/{post_id}/insights"
            params = {
                'access_token': access_token,
                'metric': 'post_engagements,post_impressions,post_reactions_by_type_total,video_views'
            }
            
            response = requests.get(insights_url, params=params)
            response.raise_for_status()
            
            insights_data = response.json()
            
            # Parse metrics
            metrics = {}
            for item in insights_data.get('data', []):
                metric_name = item['name']
                values = item.get('values', [{}])
                
                if metric_name == 'post_reactions_by_type_total':
                    # Sum all reaction types
                    metrics['likes'] = sum(values[0]['value'].values())
                elif metric_name == 'post_engagements':
                    metrics['engagement'] = values[0]['value']
                elif metric_name == 'post_impressions':
                    metrics['impressions'] = values[0]['value']
                elif metric_name == 'video_views':
                    metrics['views'] = values[0]['value']
            
            return {
                'views': metrics.get('views', 0),
                'likes': metrics.get('likes', 0),
                'comments': 0,  # Requires separate API call
                'shares': 0,  # Not directly available
                'impressions': metrics.get('impressions', 0),
                'engagement': metrics.get('engagement', 0),
            }
            
        except Exception as e:
            logger.error(f"Failed to get Facebook insights: {e}")
            return {'error': str(e)}