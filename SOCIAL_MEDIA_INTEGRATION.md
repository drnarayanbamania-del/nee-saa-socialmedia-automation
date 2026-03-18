# Bamania's Cine AI - Social Media Publishing Integration Guide

## 🎬 Complete Social Media Automation System

Automatically publish your AI-generated cinematic videos to YouTube Shorts, Instagram Reels, and Facebook with a single click.

## 📋 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Platform Configuration](#platform-configuration)
5. [API Reference](#api-reference)
6. [Frontend Integration](#frontend-integration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## ✨ Features

### 🚀 Automated Publishing
- **One-Click Publishing**: Publish to multiple platforms simultaneously
- **Scheduled Publishing**: Schedule videos for optimal posting times
- **Bulk Publishing**: Publish multiple videos at once
- **Auto-Publish**: Automatically publish after video generation

### 🔗 Platform Support
- **YouTube Shorts**: Full OAuth 2.0 integration with analytics
- **Instagram Reels**: Facebook Graph API integration for business accounts
- **Facebook**: Page publishing with engagement tracking

### 📊 Analytics & Insights
- **Real-time Metrics**: Views, likes, comments, shares
- **Engagement Rate**: Platform-specific engagement calculations
- **Performance Tracking**: Historical performance data
- **Quota Management**: Daily publishing limits per platform

### 🔐 Security & Management
- **OAuth 2.0**: Secure authentication for all platforms
- **Token Management**: Automatic token refresh
- **Account Management**: Connect/disconnect accounts easily
- **Rate Limiting**: Respect platform API limits

---

## 🏗️ Architecture

### System Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Frontend UI   │────▶│  Backend API     │────▶│  Publishers      │
│                 │     │                  │     │                  │
│ • Dashboard     │     │ • Auth Endpoints │────▶│ • YouTube        │
│ • Queue Manager │     │ • Publish API    │────▶│ • Instagram      │
│ • Analytics     │     │ • WebSockets     │────▶│ • Facebook       │
└─────────────────┘     └──────────────────┘     └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   Database       │
                        │                  │
                        │ • social_accounts│
                        │ • publishing_queue│
                        │ • analytics      │
                        └──────────────────┘
```

### Key Components

1. **Publishing Coordinator** (`social_publishers/publishing_coordinator.py`)
   - Orchestrates publishing across all platforms
   - Manages queue and scheduling
   - Handles errors and retries

2. **Platform Publishers**
   - `youtube_publisher.py`: YouTube Data API v3
   - `instagram_publisher.py`: Facebook Graph API v18.0
   - `facebook_publisher.py`: Facebook Graph API v18.0

3. **Backend API** (`api/social/publish.py`)
   - RESTful endpoints for all operations
   - OAuth callback handlers
   - WebSocket support for real-time updates

4. **Database Schema** (`database/publishing_schema.sql`)
   - Stores accounts, queue, templates, analytics
   - Handles state management

---

## 🔧 Setup Instructions

### Step 1: Database Setup

```bash
# Run the publishing schema
psql -U your_user -d your_database -f database/publishing_schema.sql

# Verify tables created
psql -U your_user -d your_database -c "\dt social_*"
psql -U your_user -d your_database -c "\dt publishing_*"
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install platform-specific packages
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install requests
```

### Step 3: Configure Environment Variables

Create or update your `.env` file:

```bash
# YouTube API
YOUTUBE_CLIENT_SECRETS_FILE=config/youtube_client_secrets.json

# Instagram API (via Facebook)
INSTAGRAM_APP_ID=your_instagram_app_id
INSTAGRAM_APP_SECRET=your_instagram_app_secret
INSTAGRAM_REDIRECT_URI=https://your-domain.com/api/v1/social/callback/instagram

# Facebook API
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=https://your-domain.com/api/v1/social/callback/facebook

# JWT & Security
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
ADMIN_API_KEY=your-admin-api-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/bamanias_cine_ai

# Redis (for queue management)
REDIS_URL=redis://localhost:6379/0

# Supabase (for video storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
```

---

## 🔌 Platform Configuration

### YouTube Setup

1. **Create Google Cloud Project**
   ```bash
   # Go to: https://console.cloud.google.com/
   # Create new project or select existing
   ```

2. **Enable YouTube Data API v3**
   ```
   APIs & Services > Library > Search "YouTube Data API v3" > Enable
   ```

3. **Create OAuth 2.0 Credentials**
   ```
   APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID
   
   Application type: Web application
   Authorized redirect URIs: https://your-domain.com/api/v1/social/callback/youtube
   ```

4. **Download Client Secrets**
   ```bash
   # Download JSON file
   # Save to: config/youtube_client_secrets.json
   # Add to .gitignore!
   ```

5. **Configure Consent Screen**
   ```
   OAuth consent screen > Add scopes:
   - ../auth/youtube.upload
   - ../auth/youtube.readonly
   ```

### Instagram Setup

1. **Create Facebook App**
   ```
   https://developers.facebook.com/ > My Apps > Create App
   
   App Type: Business
   ```

2. **Configure Instagram Product**
   ```
   Add Product: Instagram Graph API
   ```

3. **Get App Credentials**
   ```
   Settings > Basic
   
   Copy: App ID, App Secret
   Add to .env as INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET
   ```

4. **Configure OAuth**
   ```
   Facebook Login > Settings:
   - Valid OAuth Redirect URIs: https://your-domain.com/api/v1/social/callback/instagram
   ```

5. **Business Account Requirements**
   ```
   Your Instagram account must be:
   - Business or Creator account
   - Connected to a Facebook Page
   - Have 2FA enabled (recommended)
   ```

### Facebook Setup

1. **Use Same App as Instagram**
   - Facebook shares the same app credentials
   - Just needs different redirect URI

2. **Configure Page Permissions**
   ```
   Graph API Explorer > Get Token > pages_manage_posts,pages_read_engagement
   ```

3. **Test Page Access**
   ```bash
   curl "https://graph.facebook.com/v18.0/me/accounts?access_token=TOKEN"
   ```

---

## 📡 API Reference

### Authentication

All endpoints require JWT authentication:

```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN',
  'Content-Type': 'application/json'
}
```

### Connect Account

**Start OAuth Flow:**
```http
POST /api/v1/social/connect/{platform}

Response:
{
  "status": "auth_required",
  "auth_url": "https://..."
}
```

**OAuth Callback:**
```http
GET /api/v1/social/callback/{platform}?code=...&state=...

Redirects to: dashboard.html?connected={platform}
```

### Publish Video

**Immediate Publishing:**
```http
POST /api/v1/social/publish
{
  "video_id": "video_uuid",
  "platforms": ["youtube", "instagram", "facebook"],
  "caption": "Your caption here",
  "hashtags": ["#shorts", "#viral"],
  "auto_publish": true
}

Response:
{
  "status": "processing",
  "message": "Video publishing started",
  "platforms": {
    "youtube": {"status": "processing"},
    "instagram": {"status": "processing"}
  }
}
```

**Scheduled Publishing:**
```http
POST /api/v1/social/publish
{
  "video_id": "video_uuid",
  "platforms": ["youtube"],
  "caption": "Scheduled post",
  "scheduled_for": "2024-12-01T15:00:00Z"
}

Response:
{
  "status": "scheduled",
  "message": "Video scheduled for 2024-12-01T15:00:00Z",
  "job_id": "queue_uuid"
}
```

### Get Connected Accounts

```http
GET /api/v1/social/accounts

Response:
{
  "status": "success",
  "accounts": [
    {
      "id": "account_uuid",
      "platform": "youtube",
      "account_name": "My Channel",
      "account_username": "@mychannel",
      "profile_picture_url": "https://...",
      "follower_count": 1250,
      "is_active": true,
      "created_at": "2024-11-06T10:00:00Z"
    }
  ]
}
```

### Disconnect Account

```http
DELETE /api/v1/social/accounts/{account_id}

Response:
{
  "status": "success",
  "message": "Account disconnected successfully"
}
```

### Get Publishing Stats

```http
GET /api/v1/social/stats?days=30

Response:
{
  "status": "success",
  "days": 30,
  "stats": {
    "youtube": {
      "videos_published": 15,
      "total_views": 12500,
      "total_likes": 850,
      "avg_engagement_rate": 6.8
    },
    "instagram": {
      "videos_published": 12,
      "total_views": 8900,
      "total_likes": 1200,
      "avg_engagement_rate": 13.5
    }
  }
}
```

---

## 🎨 Frontend Integration

### Load Social Dashboard

```html
<!-- Add to navigation -->
<a href="social_dashboard.html" class="nav-link">
  <i class="fas fa-share-alt"></i> Social Media
</a>
```

### Auto-Publish After Generation

```javascript
// In video generation callback
async function onVideoGenerated(videoId) {
  // Check if auto-publish is enabled
  const autoPublish = localStorage.getItem('autoPublish') === 'true';
  
  if (autoPublish) {
    const platforms = JSON.parse(localStorage.getItem('autoPublishPlatforms') || '[]');
    
    await fetch(`${API_BASE}/social/publish`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        video_id: videoId,
        platforms: platforms,
        auto_publish: true
      })
    });
  }
}
```

### WebSocket Real-Time Updates

```javascript
// Connect to publishing progress
const ws = new WebSocket(
  `wss://your-domain.com/api/v1/social/ws/publishing/${queue_id}`
);

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  // Update progress bars
  update.platformProgress(update.platform, update.status, update.progress);
  
  // Show notification when complete
  if (update.status === 'completed') {
    showNotification('Video published to all platforms!', 'success');
  }
};
```

---

## 🧪 Testing

### 1. Test OAuth Flow

```bash
# Start backend
python backend/main.py

# Open social dashboard
open frontend/social_dashboard.html

# Click "Connect" for each platform
# Verify redirect and account connection
```

### 2. Test Publishing

```bash
# Generate a test video
python demo/test_full_pipeline.py

# Get video ID from output
VIDEO_ID="video_..."

# Test API publishing
curl -X POST http://localhost:8000/api/v1/social/publish \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d "{
    \"video_id\": \"$VIDEO_ID\",
    \"platforms\": [\"youtube\"],
    \"caption\": \"Test video from Bamania's Cine AI\",
    \"hashtags\": [\"#AI\", \"#VideoGeneration\"]
  }"
```

### 3. Test Scheduling

```bash
# Schedule for 1 hour from now
SCHEDULE_TIME=$(date -d "+1 hour" --iso-8601=seconds)

curl -X POST http://localhost:8000/api/v1/social/publish \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d "{
    \"video_id\": \"$VIDEO_ID\",
    \"platforms\": [\"instagram\", \"facebook\"],
    \"scheduled_for\": \"$SCHEDULE_TIME\"
  }"
```

### 4. Verify Database

```bash
# Check connected accounts
psql -c "SELECT platform, account_name, is_valid FROM social_accounts;"

# Check publishing queue
psql -c "SELECT status, platform, created_at FROM publishing_queue;"

# Check analytics
psql -c "SELECT platform, videos_published, total_views FROM publishing_analytics;"
```

---

## 🔧 Troubleshooting

### YouTube OAuth Error: "redirect_uri_mismatch"

**Solution:**
```
1. Go to Google Cloud Console > Credentials
2. Edit OAuth 2.0 Client ID
3. Add exact redirect URI from error message
4. Include: https://your-domain.com/api/v1/social/callback/youtube
5. Save and retry
```

### Instagram Error: "No Instagram Business Account found"

**Solution:**
```
1. Convert Instagram to Business/Creator account
   - Profile > Settings > Account > Switch to Professional Account
2. Connect to Facebook Page
   - Profile > Edit Profile > Page > Connect Facebook Page
3. Ensure page is published (not unpublished)
4. Retry OAuth flow
```

### Facebook Error: "(#200) Requires pages_manage_posts permission"

**Solution:**
```
1. Go to Facebook Developer Console
2. App Review > Permissions and Features
3. Request advanced access for:
   - pages_manage_posts
   - pages_read_engagement
4. Submit for review with screencast
5. Wait for approval (3-7 days)
```

### Publishing Error: "Token expired"

**Solution:**
```python
# Coordinator automatically refreshes tokens
# If manual refresh needed:

from social_publishers.youtube_publisher import YouTubePublisher

youtube = YouTubePublisher()
new_creds = youtube.refresh_credentials(old_credentials_data)

# Update in database
db.execute_query(
    "UPDATE social_accounts SET access_token = %s WHERE id = %s",
    (new_creds.token, account_id)
)
```

### Rate Limiting Error: "quotaExceeded"

**Solution:**
```python
# Check current quota
current_quota = db.execute_query(
    "SELECT videos_today, daily_quota FROM social_accounts WHERE id = %s",
    (account_id,)
)

# Wait until quota resets (midnight PST for YouTube)
# Or request quota increase from platform
```

### Video Upload Error: "Video too long"

**Solution:**
```python
# Check video duration before publishing
duration = get_video_duration(video_file)

platform_limits = {
    'youtube': 60,      # 60 seconds for Shorts
    'instagram': 90,    # 90 seconds for Reels
    'facebook': 240     # 240 seconds for Facebook
}

if duration > platform_limits[platform]:
    # Trim video or reject
    raise Exception(f"Video too long for {platform}")
```

---

## 📊 Monitoring & Analytics

### Enable Detailed Logging

```python
# In your Python script
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Platform-specific logs
logger = logging.getLogger('YouTubePublisher')
logger.setLevel(logging.DEBUG)
```

### Track Publishing Metrics

```python
# Get daily stats
coordinator = PublishingCoordinator(db_manager)
stats = coordinator.get_publishing_stats(user_id='user_123', days=7)

print(f"YouTube: {stats['youtube']['videos_published']} videos, {stats['youtube']['total_views']} views")
print(f"Instagram: {stats['instagram']['avg_engagement_rate']}% engagement")
```

### Set Up Alerts

```python
# Failed publishing alert
if result['status'] == 'failed':
    send_discord_alert(f"Publishing failed: {result['error']}")
    send_email_alert(user_email, "Publishing failed", result['error'])
```

---

## 🚀 Production Deployment

### Vercel Deployment

```bash
# Add environment variables in Vercel Dashboard
vercel env add YOUTUBE_CLIENT_SECRETS_FILE
vercel env add INSTAGRAM_APP_ID
vercel env add INSTAGRAM_APP_SECRET
vercel env add FACEBOOK_APP_ID
vercel env add FACEBOOK_APP_SECRET

# Deploy
vercel --prod
```

### Docker Deployment

```bash
# Build with all credentials
docker build \
  --build-arg YOUTUBE_CLIENT_SECRETS_FILE=config/youtube_client_secrets.json \
  --build-arg INSTAGRAM_APP_ID=${INSTAGRAM_APP_ID} \
  --build-arg INSTAGRAM_APP_SECRET=${INSTAGRAM_APP_SECRET} \
  -t bamanias-cine-ai:latest .

# Run
docker run -p 8000:8000 bamanias-cine-ai:latest
```

### Scaling Recommendations

```python
# Use Redis for queue management in production
# Use Supabase for video storage
# Use separate worker processes for publishing

# docker-compose.yml
services:
  web:
    build: .
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
  worker:
    build: .
    command: python worker/publishing_worker.py
  redis:
    image: redis:7-alpine
```

---

## 📚 Additional Resources

### Platform Documentation
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api/)

### OAuth Tools
- [Google OAuth Playground](https://developers.google.com/oauthplayground/)
- [Facebook Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)

### Video Specifications
- [YouTube Shorts Requirements](https://support.google.com/youtube/answer/10059070)
- [Instagram Reels Guidelines](https://business.instagram.com/getting-started/reels-ads/)

---

## 🎉 Success Metrics

Once fully integrated, you should be able to:

✅ **Connect all three platforms** via OAuth
✅ **Publish to multiple platforms** with one click
✅ **Schedule videos** for future publishing
✅ **Track publishing progress** in real-time
✅ **View analytics** per platform
✅ **Auto-publish** after video generation
✅ **Manage multiple accounts** per platform
✅ **Handle errors gracefully** with retry logic

---

**Your social media publishing system is now ready!** 🚀

Start publishing your AI-generated cinematic videos to YouTube Shorts, Instagram Reels, and Facebook automatically with Bamania's Cine AI.