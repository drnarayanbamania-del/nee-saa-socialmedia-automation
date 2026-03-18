#!/bin/bash

# Cinematic AI Factory - Quick Start Script
# One-command setup and launch

set -e

echo "🎬 Cinematic AI Factory - Quick Start"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3.8+ is required but not installed"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    print_success "Docker found"
else
    print_warning "Docker not found. Docker deployment will not be available."
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose found"
else
    print_warning "Docker Compose not found. Container orchestration will not be available."
fi

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p output/{scripts,images,voice,videos,thumbnails,metadata}
mkdir -p logs/{workflows,scrapes,generations}
mkdir -p assets/{music,fonts,temp}
mkdir -p workflows
mkdir -p temp
print_success "Directories created"

# Check for .env file
echo ""
echo "Checking configuration..."
if [ -f ".env" ]; then
    print_success ".env file found"
else
    print_warning ".env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file with your API keys before running the application"
    else
        print_error ".env.example not found. Cannot create configuration file."
        exit 1
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Install additional packages for cinematic features
echo ""
echo "Installing cinematic dependencies..."
pip install moviepy==1.0.3 pillow==10.0.0 numpy==1.24.3
print_success "Cinematic dependencies installed"

# Check for API keys
echo ""
echo "Checking API keys..."
if grep -q "OPENAI_API_KEY=sk-" .env; then
    if grep -q "OPENAI_API_KEY=sk-your-key" .env; then
        print_warning "OpenAI API key is not configured. Please add your API key to .env file"
    else
        print_success "OpenAI API key found"
    fi
else
    print_warning "OpenAI API key not found in .env file"
fi

if grep -q "ELEVENLABS_API_KEY=" .env; then
    if grep -q "ELEVENLABS_API_KEY=sk-your-key" .env; then
        print_warning "ElevenLabs API key is not configured. Please add your API key to .env file"
    else
        print_success "ElevenLabs API key found"
    fi
else
    print_warning "ElevenLabs API key not found in .env file"
fi

# Test imports
echo ""
echo "Testing imports..."
python3 -c "
import sys
try:
    from ai_engine.cinematic_video_composer import CinematicVideoComposer
    from main_cinematic_coordinator import CinematicAIFactory
    print('✅ Core modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Create sample background music directory
echo ""
echo "Setting up assets..."
if [ ! -f "assets/music/cinematic.mp3" ]; then
    print_info "Creating placeholder music directory..."
    echo "⚠️  Please add background music files to assets/music/ directory"
    echo "   Recommended: cinematic.mp3, epic.mp3, inspirational.mp3"
fi

# Display next steps
echo ""
echo "======================================"
echo "🎉 Setup completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Choose your deployment method:"
echo ""
echo "   Option A - Docker (Recommended):"
echo "   docker-compose up --build"
echo ""
echo "   Option B - Native Python:"
echo "   python backend/cinematic_api.py"
echo ""
echo "   Option C - Development with auto-reload:"
echo "   uvicorn backend.cinematic_api:app --reload"
echo ""
echo "3. Access the dashboard:"
echo "   http://localhost:8000"
echo ""
echo "4. Generate your first cinematic video:"
echo "   python main_cinematic_coordinator.py --mode single --topic 'सफलता के रहस्य'"
echo ""
echo "======================================"
echo "📖 Documentation: README_CINEMATIC.md"
echo "🐛 Issues: GitHub Issues"
echo "💬 Discord: https://discord.gg/cinematic-factory"
echo "======================================"
echo ""

# Offer to start services
echo "Would you like to start the services now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting Cinematic AI Factory..."
    
    if command -v docker-compose &> /dev/null; then
        echo "Starting with Docker Compose..."
        docker-compose up --build
    else
        echo "Starting with Python..."
        python backend/cinematic_api.py
    fi
else
    echo ""
    echo "You can start the services later using:"
    echo "  docker-compose up --build"
    echo "  or"
    echo "  python backend/cinematic_api.py"
fi

echo ""
print_success "Setup complete! 🎬"