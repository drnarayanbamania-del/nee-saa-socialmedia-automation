#!/bin/bash

# स्टूडियो - AI-Powered Cinematic Video Studio
# App Preview Launcher
# One-click preview of the complete platform
# Usage: ./preview.sh

set -e

echo "🎬 स्टूडियो - Cinematic AI Factory"
echo "===================================="
echo ""
echo "This script will launch the app preview in your browser."
echo ""

# Check if dashboard preview exists
if [ ! -f "frontend/app_preview.html" ]; then
    echo "❌ Error: Dashboard preview not found!"
    echo "Please ensure you're in the project root directory."
    exit 1
fi

# Detect OS and open browser
OPEN_CMD=""\nif [[ "$OSTYPE" == "darwin"* ]]; then
    OPEN_CMD="open"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OPEN_CMD="xdg-open"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OPEN_CMD="start"
else
    echo "⚠️ Unknown OS. Please open manually."
    echo ""
    echo "📂 File location:"
    echo "   $(pwd)/frontend/app_preview.html"
    echo ""
    echo "👉 Please open this file in your browser."
    exit 0
fi

echo "🎨 Launching Dashboard Preview..."
echo ""
echo "✨ Features you'll see:"
echo "   • English UI (buttons, navigation, labels)"
echo "   • Hindi content (scripts, captions, narration)"
echo "   • Real-time metrics and charts"
echo "   • Glass-morphism design"
echo "   • Workflow visualization"
echo ""
echo "🎬 To generate a real sample video:"
echo "   1. Set your API key: export OPENAI_API_KEY='sk-your-key'"
echo "   2. Run: python demo/generate_sample_video.py"
echo ""
echo "🚀 Opening in browser..."
echo ""

# Give user a moment to read
echo "Opening in 3 seconds..."
sleep 1
echo "Opening in 2 seconds..."
sleep 1
echo "Opening in 1 second..."
sleep 1

# Launch browser
$OPEN_CMD "frontend/app_preview.html"

echo ""
echo "✅ Dashboard preview launched!"
echo ""
echo "📖 For detailed preview guide, see: PREVIEW_GUIDE.md"
echo ""
echo "🎯 Next steps:"
echo "   • Explore the dashboard UI"
echo "   • View sample Hindi content"
echo "   • Check the workflow pipeline"
echo "   • Generate a real video (with API key)"
echo ""
echo "Happy previewing! 🎉"
