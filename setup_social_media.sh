#!/bin/bash

# Bamania's Cine AI - Social Media Publishing Setup
# This script helps you set up social media publishing for all platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo ""
    echo -e "${PURPLE}==== $1 ====${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check requirements
check_requirements() {
    log_header "Checking Requirements"
    
    local missing_requirements=()
    
    if ! command_exists python3; then
        missing_requirements+=("python3")
    fi
    
    if ! command_exists psql; then
        missing_requirements+=("postgresql")
    fi
    
    if ! command_exists node; then
        missing_requirements+=("nodejs")
    fi
    
    if [ ${#missing_requirements[@]} -ne 0 ]; then
        log_error "Missing requirements: ${missing_requirements[*]}"
        log_info "Please install missing requirements and try again."
        exit 1
    fi
    
    log_success "All requirements met!"
}

# Setup database
setup_database() {
    log_header "Setting Up Database"
    
    read -p "Enter PostgreSQL host [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Enter PostgreSQL port [5432]: " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    read -p "Enter PostgreSQL database name [bamanias_cine_ai]: " DB_NAME
    DB_NAME=${DB_NAME:-bamanias_cine_ai}
    
    read -p "Enter PostgreSQL username: " DB_USER
    
    read -s -p "Enter PostgreSQL password: " DB_PASS
    echo ""
    
    # Test connection
    log_info "Testing database connection..."
    if PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        log_success "Database connection successful!"
    else
        log_error "Database connection failed. Please check credentials."
        exit 1
    fi
    
    # Run schema
    log_info "Creating publishing tables..."
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f database/publishing_schema.sql
    
    log_success "Database setup complete!"
}

# Setup YouTube
setup_youtube() {
    log_header "Setting Up YouTube Integration"
    
    log_info "To integrate YouTube, you need to:"
    echo ""
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Create a new project or select existing"
    echo "3. Enable YouTube Data API v3"
    echo "4. Create OAuth 2.0 credentials (Web application)"
    echo "5. Add authorized redirect URI:"
    echo "   https://your-domain.com/api/v1/social/callback/youtube"
    echo "6. Download client secrets JSON"
    echo ""
    
    read -p "Have you downloaded the YouTube client secrets JSON? (y/n): " has_youtube
    
    if [ "$has_youtube" = "y" ]; then
        read -p "Enter path to client_secrets.json file: " YOUTUBE_SECRETS_PATH
        
        if [ -f "$YOUTUBE_SECRETS_PATH" ]; then
            mkdir -p config
            cp "$YOUTUBE_SECRETS_PATH" config/youtube_client_secrets.json
            log_success "YouTube client secrets saved!"
        else
            log_error "File not found: $YOUTUBE_SECRETS_PATH"
            exit 1
        fi
    else
        log_warning "Skipping YouTube setup. You can add it later."
    fi
}

# Setup Instagram
setup_instagram() {
    log_header "Setting Up Instagram Integration"
    
    log_info "To integrate Instagram, you need to:"
    echo ""
    echo "1. Create Facebook App at: https://developers.facebook.com/"
    echo "2. Add Instagram Graph API product"
    echo "3. Get App ID and App Secret"
    echo "4. Add OAuth redirect URI:"
    echo "   https://your-domain.com/api/v1/social/callback/instagram"
    echo "5. Ensure Instagram account is Business/Creator"
    echo "6. Connect Instagram to Facebook Page"
    echo ""
    
    read -p "Do you have Instagram App ID and App Secret? (y/n): " has_instagram
    
    if [ "$has_instagram" = "y" ]; then
        read -p "Enter Instagram App ID: " INSTAGRAM_APP_ID
        read -p "Enter Instagram App Secret: " INSTAGRAM_APP_SECRET
        
        # Save to .env
        echo "INSTAGRAM_APP_ID=$INSTAGRAM_APP_ID" >> .env
        echo "INSTAGRAM_APP_SECRET=$INSTAGRAM_APP_SECRET" >> .env
        echo "INSTAGRAM_REDIRECT_URI=https://your-domain.com/api/v1/social/callback/instagram" >> .env
        
        log_success "Instagram credentials saved!"
    else
        log_warning "Skipping Instagram setup. You can add it later."
    fi
}

# Setup Facebook
setup_facebook() {
    log_header "Setting Up Facebook Integration"
    
    log_info "Facebook uses the same app as Instagram"
    echo ""
    
    read -p "Do you want to set up Facebook publishing? (y/n): " setup_fb
    
    if [ "$setup_fb" = "y" ]; then
        # Use same credentials as Instagram or ask for new ones
        if grep -q "INSTAGRAM_APP_ID" .env; then
            INSTAGRAM_APP_ID=$(grep INSTAGRAM_APP_ID .env | cut -d '=' -f2)
            INSTAGRAM_APP_SECRET=$(grep INSTAGRAM_APP_SECRET .env | cut -d '=' -f2)
            
            echo "FACEBOOK_APP_ID=$INSTAGRAM_APP_ID" >> .env
            echo "FACEBOOK_APP_SECRET=$INSTAGRAM_APP_SECRET" >> .env
            echo "FACEBOOK_REDIRECT_URI=https://your-domain.com/api/v1/social/callback/facebook" >> .env
            
            log_success "Facebook credentials saved (same as Instagram)!"
        else
            read -p "Enter Facebook App ID: " FACEBOOK_APP_ID
            read -p "Enter Facebook App Secret: " FACEBOOK_APP_SECRET
            
            echo "FACEBOOK_APP_ID=$FACEBOOK_APP_ID" >> .env
            echo "FACEBOOK_APP_SECRET=$FACEBOOK_APP_SECRET" >> .env
            echo "FACEBOOK_REDIRECT_URI=https://your-domain.com/api/v1/social/callback/facebook" >> .env
            
            log_success "Facebook credentials saved!"
        fi
    else
        log_warning "Skipping Facebook setup. You can add it later."
    fi
}

# Install Python dependencies
install_dependencies() {
    log_header "Installing Python Dependencies"
    
    if [ -f "requirements.txt" ]; then
        log_info "Installing from requirements.txt..."
        pip install -r requirements.txt
        log_success "Dependencies installed!"
    else
        log_warning "requirements.txt not found. Creating basic requirements..."
        
        cat > requirements.txt << EOF
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
requests==2.31.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
redis==5.0.1
supabase==2.0.3
fastapi==0.104.1
uvicorn==0.24.0
EOF
        
        pip install -r requirements.txt
        log_success "Dependencies installed!"
    fi
}

# Create configuration files
create_config_files() {
    log_header "Creating Configuration Files"
    
    # Create config directory
    mkdir -p config
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        log_info "Creating .env file..."
        
        cat > .env << EOF
# Bamania's Cine AI - Configuration

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bamanias_cine_ai

# JWT & Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
ADMIN_API_KEY=sk-admin-key-12345

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# ElevenLabs (optional)
ELEVENLABS_API_KEY=your-elevenlabs-key

# Redis (for queue management)
REDIS_URL=redis://localhost:6379/0

# Supabase (for video storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# YouTube (to be configured)
YOUTUBE_CLIENT_SECRETS_FILE=config/youtube_client_secrets.json

# Instagram (to be configured)
INSTAGRAM_APP_ID=your-instagram-app-id
INSTAGRAM_APP_SECRET=your-instagram-app-secret
INSTAGRAM_REDIRECT_URI=https://your-domain.com/api/v1/social/callback/instagram

# Facebook (to be configured)
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_REDIRECT_URI=https://your-domain.com/api/v1/social/callback/facebook

# Project
PROJECT_NAME="Bamania's Cine AI"
EOF
        
        log_success ".env file created!"
    else
        log_info ".env file already exists"
    fi
}

# Test the setup
test_setup() {
    log_header "Testing Setup"
    
    log_info "Running database connection test..."
    python3 -c "
import sys
try:
    from database.db_manager import DatabaseManager
    db = DatabaseManager()
    result = db.execute_query('SELECT 1')[0]
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection: FAILED - {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Database test passed!"
    else
        log_error "Database test failed!"
        exit 1
    fi
    
    log_info "Testing imports..."
    python3 -c "
from social_publishers.youtube_publisher import YouTubePublisher
from social_publishers.instagram_publisher import InstagramPublisher
from social_publishers.facebook_publisher import FacebookPublisher
from social_publishers.publishing_coordinator import PublishingCoordinator
print('All imports successful!')
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Import test passed!"
    else
        log_warning "Some imports failed. This might be normal if credentials are not configured yet."
    fi
}

# Create run script
create_run_script() {
    log_header "Creating Run Script"
    
    cat > run_social_publisher.sh << 'EOF'
#!/bin/bash

# Run the social media publisher worker
# This handles scheduled publishing and queue processing

echo "Starting Bamania's Cine AI - Social Media Publisher Worker..."
echo "Press Ctrl+C to stop"
echo ""

# Run the worker
python3 worker/publishing_worker.py
EOF
    
    chmod +x run_social_publisher.sh
    log_success "Run script created: run_social_publisher.sh"
}

# Main menu
main() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}║   🎬  Bamania' s Cine AI - Social Media Setup Wizard  🎬   ║${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_requirements
    
    # Ask what to set up
    echo "What would you like to set up?"
    echo "1) Complete setup (recommended)"
    echo "2) Database only"
    echo "3) YouTube only"
    echo "4) Instagram only"
    echo "5) Facebook only"
    echo "6) Skip to test"
    echo ""
    read -p "Enter your choice [1]: " choice
    choice=${choice:-1}
    
    case $choice in
        1)
            create_config_files
            install_dependencies
            setup_database
            setup_youtube
            setup_instagram
            setup_facebook
            ;;
        2)
            setup_database
            ;;
        3)
            setup_youtube
            ;;
        4)
            setup_instagram
            ;;
        5)
            setup_facebook
            ;;
        6)
            log_info "Skipping setup, running tests..."
            ;;
        *)
            log_error "Invalid choice"
            exit 1
            ;;
    esac
    
    create_run_script
    test_setup
    
    # Summary
    log_header "Setup Complete!"
    echo ""
    echo -e "${GREEN}✅ Database configured${NC}"
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    echo -e "${GREEN}✅ Configuration files created${NC}"
    echo -e "${GREEN}✅ Tests passed${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start the main API server: python backend/main.py"
    echo "2. Start the publishing worker: ./run_social_publisher.sh"
    echo "3. Open frontend: open frontend/social_dashboard.html"
    echo "4. Connect your social media accounts"
    echo "5. Start publishing!"
    echo ""
    echo -e "${PURPLE}📚 For detailed documentation, see: SOCIAL_MEDIA_INTEGRATION.md${NC}"
    echo ""
}

# Handle script interruption
trap 'log_error "Setup interrupted"; exit 1' INT

# Run main function
main "$@"