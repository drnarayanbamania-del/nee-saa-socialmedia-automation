#!/bin/bash

# Hindi AI Automation Platform - Quick Start Script
# This script helps you get started quickly with the platform

set -e

echo "🚀 Hindi AI Automation Platform - Quick Start"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=sk-your-api-key-here"
    echo ""
    read -p "Press Enter after you've added your API key to .env file..."
fi

# Check if OpenAI API key is set
if grep -q "OPENAI_API_KEY=sk-your" .env; then
    echo ""
    echo "❌ Please update OPENAI_API_KEY in .env file with your actual API key"
    echo "   Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi

echo ""
echo "📋 Checking configuration..."
echo "✅ Docker is installed"
echo "✅ Docker Compose is installed"
echo "✅ .env file exists"
echo "✅ OpenAI API key is configured"

# Create necessary directories
echo ""
echo "📁 Creating output directories..."
mkdir -p outputs generated_images temp_audio final_videos thumbnails

# Set permissions
chmod 777 outputs generated_images temp_audio final_videos thumbnails

echo "✅ Directories created"

# Build and start services
echo ""
echo "🐳 Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""

docker-compose up --build -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo ""
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "=============================================="
echo "🎉 Hindi AI Automation Platform is Ready!"
echo "=============================================="
echo ""
echo "📊 Access Points:"
echo "   • Dashboard: http://localhost"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • API Key: sk-admin-key-12345"
echo ""
echo "🚀 Quick Start Commands:"
echo ""
echo "1. View trending topics:"
echo "   curl -H \"Authorization: Bearer sk-admin-key-12345\" \\"
echo "     http://localhost:8000/api/v1/trending"
echo ""
echo "2. Run full automation:"
echo "   python main_coordinator.py --mode full"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "4. Stop services:"
echo "   docker-compose down"
echo ""
echo "📖 Full Documentation: https://github.com/your-repo/hindi-ai-automation"
echo ""
echo "❓ Need help? Open an issue on GitHub"
echo ""
echo "Happy content creation! 🎬"