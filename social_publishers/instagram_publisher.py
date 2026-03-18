"""
Bamania's Cine AI - Instagram Reels Publisher
Handles OAuth authentication and video publishing to Instagram Reels via Facebook Graph API
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

class InstagramPublisher:
    """Publisher for Instagram Reels via Facebook Graph API"""
    
    def __init__(self):
        """Initialize Instagram publisher"""
        self.app_id = os.getenv('INSTAGRAM_APP_ID')
        self.app_secret = os.getenv('INSTAGRAM_APP_SECRET')
        self.redirect_uri = os.getenv('INSTAGRAM_REDIRECT_URI')
        
        if not all([self.app_id, self.app_secret]):
            logger.warning("Instagram credentials not configured")
    
    def get_auth_url(self, user_id: str) -> Tuple[str, str]:
        """
        Generate Facebook OAuth URL for Instagram publishing
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Tuple of (auth_url, state_token)
        """
        try:
            # Instagram requires these permissions via Facebook
            scopes = [
                'instagram_content_publish',  # For posting
                'instagram_basic',            # For reading account info
                'pages_show_list',            # For page access
                'pages_read_engagement'       # For insights
            ]
            
            # Generate state token
            state_token = f"instagram_{user_id}_{int(time.time())}"
            
            # Build auth URL
            auth_url = (
                f"https://www.facebook.com/v18.0/dialog/oauth?"
                f"client_id={self.app_id}"
                f"&redirect_uri={self.redirect_uri}"
                f"&scope={','.join(scopes)}"
                f"&state={state_token}"
                f"&response_type=code"
            )
            
            logger.info(f"Generated Instagram auth URL for user {user_id}")
            return auth_url, state_token
            
        except Exception as e:
            logger.error(f"Failed to generate Instagram auth URL: {e}")
            raise
    
    def handle_oauth_callback(self, code: str, state: str) -> Dict:
        """
        Handle OAuth callback and get Instagram Business Account access
        
        Args:
            code: Authorization code from Facebook
            state: State token from OAuth flow
            
        Returns:
            Dictionary with credentials and account info
        """
        try:
            # Step 1: Exchange code for access token
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
            access_token = token_data['access_token']
            
            # Step 2: Get User's Pages (Instagram accounts are connected to pages)
            pages_url = "https://graph.facebook.com/v18.0/me/accounts"
            params = {
                'access_token': access_token,
                'fields': 'id,name,instagram_business_account'
            }
            
            response = requests.get(pages_url, params=params)
            response.raise_for_status()
            
            pages_data = response.json()
            
            if not pages_data.get('data'):
                raise Exception("No Facebook pages found. Please create a page and connect Instagram.")
            
            # Step 3: Find Instagram Business Account
            instagram_account = None
            page_info = None
            
            for page in pages_data['data']:
                if 'instagram_business_account' in page:
                    instagram_account = page['instagram_business_account']
                    page_info = page
                    break
            
            if not instagram_account:
                raise Exception(
                    "No Instagram Business Account found. "
                    "Please convert your Instagram to a Business account and connect it to a Facebook page."
                )
            
            # Step 4: Get Instagram account details
            ig_account_id = instagram_account['id']
            ig_info_url = f"https://graph.facebook.com/v18.0/{ig_account_id}"
            params = {
                'access_token': access_token,
                'fields': 'username,name,profile_picture_url,followers_count'
            }
            
            response = requests.get(ig_info_url, params=params)
            response.raise_for_status()
            
            ig_data = response.json()
            
            return {
                'credentials': {
                    'access_token': access_token,
                    'token_type': token_data.get('token_type', 'bearer'),
                    'expires_in': token_data.get('expires_in', 5184000)  # 60 days default
                },
                'platform_user_id': ig_account_id,
                'account_name': ig_data.get('name', ig_data.get('username')),
                'account_username': ig_data['username'],
                'page_id': page_info['id'],
                'profile_picture_url': ig_data.get('profile_picture_url'),
                'follower_count': ig_data.get('followers_count', 0),
                'token_expires_at': None  # Facebook tokens are long-lived
            }
            
        except requests.RequestException as e:
            logger.error(f"Instagram OAuth API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Instagram OAuth callback failed: {e}")
            raise
    
    def refresh_credentials(self, credentials_data: Dict) -> str:
        """
        Refresh Instagram access token (Facebook Graph API)
        
        Args:
            credentials_data: Current credentials
            
        Returns:
            New access token
        """
        try:
            access_token = credentials_data['access_token']
            
            # Exchange for long-lived token (valid 60 days)
            refresh_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'fb_exchange_token': access_token
            }
            
            response = requests.get(refresh_url, params=params)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Refreshed Instagram access token")
            
            return token_data['access_token']
            
        except Exception as e:
            logger.error(f"Failed to refresh Instagram token: {e}")
            raise
    
    def upload_reel(self, video_file: str, caption: str, 
                   credentials_data: Dict, account_id: str) -> Dict:
        """
        Upload video as Instagram Reel
        
        Args:
            video_file: Path to video file
            caption: Video caption with hashtags
            credentials_data: OAuth credentials
            account_id: Instagram Business Account ID
            
        Returns:
            Dictionary with media ID and status
        """
        try:
            access_token = credentials_data['access_token']
            
            # Step 1: Upload video to Facebook Graph API
            logger.info("Uploading video to Instagram...")
            
            upload_url = f"https://graph.facebook.com/v18.0/{account_id}/media"
            
            # Prepare multipart upload
            with open(video_file, 'rb') as video:
                files = {
                    'video': video
                }
                params = {
                    'access_token': access_token,
                    'media_type': 'REELS',
                    'caption': caption[:2200],  # Instagram caption limit
                    'share_to_feed': 'true'
                }
                
                response = requests.post(upload_url, params=params, files=files)
                response.raise_for_status()
            
            upload_data = response.json()
            
            if 'id' not in upload_data:
                raise Exception(f"Upload failed: {upload_data}")
            
            container_id = upload_data['id']
            logger.info(f"Video uploaded, container ID: {container_id}")
            
            # Step 2: Check upload status
            status_url = f"https://graph.facebook.com/v18.0/{container_id}"
            params = {
                'access_token': access_token,
                'fields': 'status_code,status'
            }
            
            # Wait for video to be ready (max 60 seconds)
            max_wait = 60
            waited = 0
            
            while waited < max_wait:
                response = requests.get(status_url, params=params)
                response.raise_for_status()
                
                status_data = response.json()
                status_code = status_data.get('status_code')
                
                if status_code == 'FINISHED':
                    break
                elif status_code in ['ERROR', 'deleted']:
                    raise Exception(f"Video processing failed: {status_data.get('status')}")
                
                time.sleep(5)
                waited += 5
                logger.info(f"Video processing... {waited}s elapsed")
            
            if waited >= max_wait:
                raise Exception("Video processing timeout")
            
            # Step 3: Publish the Reel
            logger.info("Publishing Reel...")
            
            publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
            params = {
                'access_token': access_token,
                'creation_id': container_id
            }
            
            response = requests.post(publish_url, params=params)
            response.raise_for_status()
            
            publish_data = response.json()
            
            if 'id' not in publish_data:
                raise Exception(f"Publish failed: {publish_data}")
            
            media_id = publish_data['id']
            logger.info(f"Reel published successfully: {media_id}")
            
            return {
                'media_id': media_id,
                'status': 'published',
                'platform': 'instagram',
                'published_at': datetime.now(timezone.utc).isoformat(),
                'url': f"https://instagram.com/reel/{media_id}"
            }
            
        except requests.RequestException as e:
            logger.error(f"Instagram API request failed: {e}")
            return {
                'status': 'failed',
                'error': f"API request failed: {str(e)}",
                'platform': 'instagram'
            }
            
        except Exception as e:
            logger.error(f"Instagram Reel upload failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'platform': 'instagram'
            }
    
    def get_media_insights(self, media_id: str, credentials_data: Dict) -> Dict:
        """
        Get insights for published media
        
        Args:
            media_id: Instagram media ID
            credentials_data: OAuth credentials
            
        Returns:
            Dictionary with engagement metrics
        """
        try:
            access_token = credentials_data['access_token']
            
            insights_url = f"https://graph.facebook.com/v18.0/{media_id}/insights"
            params = {
                'access_token': access_token,
                'metric': 'engagement,impressions,reach,saved,video_views'
            }
            
            response = requests.get(insights_url, params=params)
            response.raise_for_status()
            
            insights_data = response.json()
            
            # Parse insights
            metrics = {}
            for item in insights_data.get('data', []):
                metrics[item['name']] = item.get('values', [{}])[0].get('value', 0)
            
            return {
                'views': metrics.get('video_views', 0),
                'likes': 0,  # Instagram API doesn't provide likes directly
                'comments': 0,  # Requires separate API call
                'shares': metrics.get('shares', 0),
                'saves': metrics.get('saved', 0),
                'reach': metrics.get('reach', 0),
                'impressions': metrics.get('impressions', 0),
                'engagement': metrics.get('engagement', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Instagram insights: {e}")
            return {'error': str(e)}