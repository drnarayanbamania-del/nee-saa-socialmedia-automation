-- Bamania's Cine AI - Social Media Publishing Schema
-- Stores social media accounts, publishing queues, and analytics

-- Social media accounts table (stores OAuth tokens)
CREATE TABLE social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('youtube', 'instagram', 'facebook', 'tiktok', 'twitter')),
    account_name VARCHAR(255) NOT NULL,
    account_username VARCHAR(255),
    
    -- OAuth credentials (encrypted)
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Platform-specific IDs
    platform_user_id VARCHAR(255),
    channel_id VARCHAR(255), -- For YouTube
    page_id VARCHAR(255), -- For Facebook
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_valid BOOLEAN DEFAULT true,
    last_validated_at TIMESTAMP WITH TIME ZONE,
    
    -- Rate limiting
    daily_quota INTEGER DEFAULT 50,
    videos_today INTEGER DEFAULT 0,
    quota_resets_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    profile_picture_url TEXT,
    follower_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_social_accounts_user ON social_accounts(user_id);
CREATE INDEX idx_social_accounts_platform ON social_accounts(platform);
CREATE INDEX idx_social_accounts_valid ON social_accounts(is_valid, is_active);

-- Publishing queue table
CREATE TABLE publishing_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Target platforms
    youtube_destination UUID REFERENCES social_accounts(id),
    instagram_destination UUID REFERENCES social_accounts(id),
    facebook_destination UUID REFERENCES social_accounts(id),
    
    -- Publishing details
    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'scheduled', 'publishing', 'published', 'failed')),
    
    scheduled_for TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    
    -- Platform-specific data
    youtube_video_id VARCHAR(255),
    instagram_media_id VARCHAR(255),
    facebook_post_id VARCHAR(255),
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Performance tracking
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_publishing_queue_status ON publishing_queue(status, scheduled_for);
CREATE INDEX idx_publishing_queue_video ON publishing_queue(video_id);
CREATE INDEX idx_publishing_queue_user ON publishing_queue(user_id);

-- Platform templates (pre-configured captions, hashtags, etc.)
CREATE TABLE platform_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('youtube', 'instagram', 'facebook')),
    
    template_name VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT false,
    
    -- Content templates
    caption_template TEXT,
    hashtag_template TEXT,
    
    -- Platform-specific settings
    youtube_category VARCHAR(50),
    youtube_privacy VARCHAR(20) DEFAULT 'public',
    youtube_tags TEXT[],
    
    instagram_music_id VARCHAR(255),
    facebook_allow_sharing BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_platform_templates_user ON platform_templates(user_id, platform);

-- Publishing analytics (daily stats per platform)
CREATE TABLE publishing_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID REFERENCES social_accounts(id),
    platform VARCHAR(20) NOT NULL,
    
    date DATE NOT NULL,
    
    videos_published INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    
    -- Engagement rate
    engagement_rate DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_publishing_analytics_user_date ON publishing_analytics(user_id, date);
CREATE INDEX idx_publishing_analytics_platform ON publishing_analytics(platform);

-- OAuth state table (for login flow)
CREATE TABLE oauth_states (
    state VARCHAR(255) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '10 minutes'
);

CREATE INDEX idx_oauth_states_expires ON oauth_states(expires_at);

-- Webhook events (for platform notifications)
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(20) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_webhook_events_processed ON webhook_events(processed, created_at);

-- Update timestamps function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_social_accounts_updated_at 
    BEFORE UPDATE ON social_accounts FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publishing_queue_updated_at 
    BEFORE UPDATE ON publishing_queue FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_templates_updated_at 
    BEFORE UPDATE ON platform_templates FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publishing_analytics_updated_at 
    BEFORE UPDATE ON publishing_analytics FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
