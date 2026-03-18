--
-- Hindi AI Automation Platform Database Schema
-- PostgreSQL
--

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    role VARCHAR(50) DEFAULT 'user', -- admin, user
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    api_key VARCHAR(255) UNIQUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    permissions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Topics table (trending topics)
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_en TEXT NOT NULL,
    topic_hi TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    category_hi VARCHAR(100),
    trending_score FLOAT DEFAULT 0,
    source VARCHAR(100), -- youtube, google_trends, twitter, news
    metadata JSONB DEFAULT '{}',
    is_used BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trending_score (trending_score DESC),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at DESC)
);

-- Scripts table
CREATE TABLE scripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES topics(id) ON DELETE SET NULL,
    title_en TEXT NOT NULL,
    title_hi TEXT NOT NULL,
    description_en TEXT,
    description_hi TEXT,
    category VARCHAR(100),
    duration_seconds INTEGER DEFAULT 0,
    segments JSONB NOT NULL, -- Array of script segments
    tags JSONB DEFAULT '[]',
    is_generated BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, rejected
    performance_score FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_status (status)
);

-- Images table
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    dimensions VARCHAR(50),
    style VARCHAR(100),
    is_thumbnail BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_script_id (script_id),
    INDEX idx_user_id (user_id)
);

-- Voice files table
CREATE TABLE voice_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    scene_number INTEGER NOT NULL,
    hindi_text TEXT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    duration_seconds FLOAT,
    voice_type VARCHAR(100),
    language VARCHAR(10) DEFAULT 'hi',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_script_id (script_id),
    INDEX idx_user_id (user_id)
);

-- Videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    title_en TEXT NOT NULL,
    title_hi TEXT NOT NULL,
    description_en TEXT,
    description_hi TEXT,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    duration_seconds INTEGER,
    resolution VARCHAR(50),
    platform VARCHAR(50), -- youtube_shorts, instagram_reels, tiktok
    thumbnail_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'draft', -- draft, rendering, ready, published, failed
    render_metadata JSONB DEFAULT '{}',
    performance_score FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_platform (platform)
);

-- Automation jobs table
CREATE TABLE automation_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workflow_type VARCHAR(100) NOT NULL, -- full_automation, video_only, trending_to_script
    parameters JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed, retrying
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    result JSONB,
    error_message TEXT,
    queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC)
);

-- Published content table
CREATE TABLE published_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- youtube, instagram, tiktok, twitter
    platform_content_id VARCHAR(255),
    title_en TEXT,
    title_hi TEXT,
    caption_en TEXT,
    caption_hi TEXT,
    hashtags JSONB DEFAULT '[]',
    thumbnail_url VARCHAR(500),
    content_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, publishing, published, failed
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_platform (platform),
    INDEX idx_status (status),
    INDEX idx_scheduled_at (scheduled_at)
);

-- Analytics table
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID REFERENCES published_content(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    watch_time_seconds INTEGER DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0,
    revenue FLOAT DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_content_id (content_id),
    INDEX idx_platform (platform),
    INDEX idx_recorded_at (recorded_at DESC)
);

-- API usage logs table
CREATE TABLE api_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    request_body JSONB,
    response_body JSONB,
    ip_address INET,
    user_agent TEXT,
    duration_ms INTEGER,
    cost_usd FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_api_key_id (api_key_id),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_endpoint (endpoint)
);

-- Webhook events table
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, delivered, failed
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    last_attempt_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at DESC)
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scripts_updated_at BEFORE UPDATE ON scripts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_published_content_updated_at BEFORE UPDATE ON published_content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for analytics
CREATE VIEW user_analytics_summary AS
SELECT 
    u.id as user_id,
    u.email,
    u.full_name,
    COUNT(DISTINCT v.id) as total_videos,
    COUNT(DISTINCT CASE WHEN v.status = 'published' THEN v.id END) as published_videos,
    SUM(v.duration_seconds) as total_duration_seconds,
    AVG(v.performance_score) as avg_performance_score,
    COUNT(DISTINCT s.id) as total_scripts,
    COUNT(DISTINCT j.id) as total_automation_jobs,
    COUNT(DISTINCT CASE WHEN j.status = 'completed' THEN j.id END) as successful_jobs
FROM users u
LEFT JOIN videos v ON u.id = v.user_id
LEFT JOIN scripts s ON u.id = s.user_id
LEFT JOIN automation_jobs j ON u.id = j.user_id
GROUP BY u.id, u.email, u.full_name;

CREATE VIEW content_performance_summary AS
SELECT 
    p.id,
    p.user_id,
    p.platform,
    p.title_hi,
    p.status,
    COALESCE(SUM(a.views), 0) as total_views,
    COALESCE(SUM(a.likes), 0) as total_likes,
    COALESCE(SUM(a.comments), 0) as total_comments,
    COALESCE(SUM(a.shares), 0) as total_shares,
    COALESCE(AVG(a.engagement_rate), 0) as avg_engagement_rate
FROM published_content p
LEFT JOIN analytics a ON p.id = a.content_id
GROUP BY p.id, p.user_id, p.platform, p.title_hi, p.status;

-- Insert sample user (for testing)
INSERT INTO users (email, password_hash, full_name, role, api_key) VALUES
('admin@aifactory.com', '$2b$12$LQv3c1yqB9q9m5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z5z', 'Admin User', 'admin', 'sk-admin-key-12345')
ON CONFLICT (email) DO NOTHING;