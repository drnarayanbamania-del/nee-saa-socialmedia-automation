#!/bin/bash

# 🚀 Deploy Studio AI to Vercel
# One-command deployment script
# Usage: ./deploy_vercel.sh [preview|production]

set -e

set -e

echo "🎬 ==========================================="
echo "   स्टूडियो AI - Vercel Deployment"
echo "   Cinematic Video Studio"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Check Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLI not found. Installing...${NC}"
    npm i -g vercel
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Check environment variables
echo "🔧 Checking environment variables..."

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your API keys${NC}"
        echo "   Then run this script again"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
fi

# Check required env vars
source .env

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set in .env${NC}"
    exit 1
fi

if [ -z "$JWT_SECRET" ]; then
    echo -e "${YELLOW}⚠️  JWT_SECRET not set. Generating random secret...${NC}"
    echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
fi

if [ -z "$ADMIN_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  ADMIN_API_KEY not set. Generating random key...${NC}"
    echo "ADMIN_API_KEY=st_admin_$(openssl rand -hex 16)" >> .env
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"
echo ""

# Login to Vercel
echo "🔐 Checking Vercel authentication..."

if ! vercel whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Vercel. Opening login...${NC}"
    vercel login
fi

echo -e "${GREEN}✅ Authenticated as $(vercel whoami)${NC}"
echo ""

# Pull environment variables
echo "📥 Pulling Vercel environment variables..."

# Check if project exists on Vercel
PROJECT_NAME="studio-cinematic-ai"
if vercel ls | grep -q "$PROJECT_NAME"; then
    echo -e "${GREEN}✅ Project exists on Vercel${NC}"
    vercel env pull .env.vercel
else
    echo -e "${YELLOW}⚠️  Project not found on Vercel. Will create during deployment${NC}"
fi

echo ""

# Build frontend
echo "🔨 Building frontend..."
npm run build:frontend

echo -e "${GREEN}✅ Frontend built successfully${NC}"
echo ""

# Deploy
echo "🚀 Starting deployment..."
echo -e "${YELLOW}This will take 2-3 minutes...${NC}"
echo ""

# Ask for deployment type
echo "Select deployment type:"
echo "1) Preview (test before production)"
echo "2) Production (go live)"
echo "3) Only build (test build)"
read -p "Choice (1-3): " choice

case $choice in
    1)
        echo -e "${YELLOW}📦 Deploying to preview...${NC}"
        vercel
        ;;
    2)
        echo -e "${GREEN}🎬 Deploying to production...${NC}"
        vercel --prod
        ;;
    3)
        echo -e "${YELLOW}🔨 Building only...${NC}"
        vercel build
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

# Get deployment URL
DEPLOYMENT_URL=$(vercel ls | grep "production" | awk '{print $2}' | head -n1)

if [ -z "$DEPLOYMENT_URL" ]; then
    DEPLOYMENT_URL=$(vercel ls | awk 'NR==3 {print $2}')
fi

echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo ""
echo "📍 Deployment URL: $DEPLOYMENT_URL"
echo ""
echo "🔗 Quick Links:"
echo "   Dashboard: $DEPLOYMENT_URL"
echo "   API Health: $DEPLOYMENT_URL/api/v1/health"
echo "   Progress Tracker: $DEPLOYMENT_URL/progress"
echo ""
echo "🧪 Test your deployment:"
echo "   curl $DEPLOYMENT_URL/api/v1/health"
echo ""
echo "🎬 Happy video generating!"
echo ""