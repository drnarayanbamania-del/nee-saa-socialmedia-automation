# 🚀 Hindi AI Automation Platform - Getting Started Guide

## Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key (get from [platform.openai.com](https://platform.openai.com/api-keys))
- 4GB+ free disk space

### Step 1: Setup

```bash
# Clone or download this repository
git clone <repository-url>
cd hindi-ai-automation-platform

# Make quickstart script executable
chmod +x quickstart.sh

# Create environment file
cp .env.example .env
```

### Step 2: Configure

Edit `.env` file and add your OpenAI API key:

```bash
# Open .env in your editor
nano .env

# Change this line:
OPENAI_API_KEY=sk-your-openai-api-key-here

# To your actual API key:
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Run

```bash
# Start the platform
./quickstart.sh

# Or manually:
docker-compose up --build
```

### Step 4: Access

- **Dashboard**: http://localhost
- **API Documentation**: http://localhost:8000/docs
- **API Key**: `sk-admin-key-12345`

That's it! 🎉

---

## 📚 Usage Examples

### Example 1: Generate a Hindi Script

```bash
# Open the dashboard and go to "Script Generator"
# Enter topic: "सफलता के रहस्य"
# Select category: "Motivation"
# Click "Generate Script"
```

Or via API:

```bash
curl -X POST http://localhost:8000/api/v1/generate-script \
  -H "Authorization: Bearer sk-admin-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"topic": "सफलता के रहस्य", "category": "motivation"}'
```

### Example 2: Full Automation

```bash
# Run complete pipeline
python main_coordinator.py --mode full --platform youtube_shorts
```

Or via dashboard:
1. Go to "Automation" tab
2. Select "Full Automation"
3. Click "Start Automation"

### Example 3: Check Job Status

```bash
curl http://localhost:8000/api/v1/jobs/{job_id} \
  -H "Authorization: Bearer sk-admin-key-12345"
```

---

## 🎯 What's Included

### AI Engines
- **Script Generator**: Creates viral Hindi scripts with hooks, storytelling, CTAs
- **Image Generator**: Cinematic visuals for each scene
- **Voice Generator**: Realistic Hindi TTS (female/male voices)
- **Video Composer**: Professional video editing with subtitles
- **Caption Generator**: Viral Hindi captions & trending hashtags

### Scrapers
- YouTube trending (simulated, use API in production)
- Google Trends for India
- Twitter/X trending topics
- News headline aggregator

### Automation
- Workflow engine with Redis queue
- Distributed workers
- Job monitoring & retry logic
- Real-time status updates

### Dashboard
- Modern React interface (no build required)
- Real-time job tracking
- Content library
- Analytics

---

## 📁 Output Files

After running automation, check these directories:

- `outputs/`: Generated scripts and results (JSON files)
- `generated_images/`: Scene images (PNG files)
- `temp_audio/`: Voiceover audio segments (MP3 files)
- `final_videos/`: Completed videos (MP4 files)
- `thumbnails/`: Video thumbnails (PNG files)

---

## 🔧 Configuration Options

### Change AI Parameters

Edit the automation request:

```json
{
  "workflow_type": "full_automation",
  "parameters": {
    "topic": "सुबह की रूटीन",
    "platform": "youtube_shorts",  // or "instagram_reels", "tiktok"
    "image_style": "cinematic",    // or "animated", "realistic", "bollywood"
    "voice_type": "female_neutral" // or "male_neutral"
  }
}
```

### Environment Variables

Key settings in `.env`:

```bash
# Required
OPENAI_API_KEY=sk-your-key

# Optional
DEFAULT_PLATFORM=youtube_shorts
DEFAULT_IMAGE_STYLE=cinematic
DEFAULT_VOICE_TYPE=female_neutral
MAX_VIDEO_DURATION=90
```

---

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f worker

# Stop services
docker-compose down

# Restart
docker-compose restart

# Scale workers
docker-compose up -d --scale worker=3

# Check status
docker-compose ps
```

---

## 🛠️ Troubleshooting

### Problem: "OpenAI API key not found"
**Solution**: Make sure you added your API key to `.env` file

### Problem: "Redis connection failed"
**Solution**: Check if Redis container is running: `docker-compose ps`

### Problem: "Video generation failed"
**Solution**: Ensure FFmpeg is installed in the container (it should be)

### Problem: "No trending topics found"
**Solution**: The scraper uses simulated data. Connect real APIs in production:
- YouTube Data API
- Google Trends API
- Twitter API

---

## 📖 API Documentation

Once running, visit: http://localhost:8000/docs

Interactive Swagger UI with all endpoints:
- Generate scripts
- Create automation jobs
- Check job status
- Get trending topics
- Compose videos

---

## 🎯 Next Steps

1. **Explore the dashboard** - Try all features
2. **Generate your first script** - Use a trending topic
3. **Run full automation** - See the complete pipeline
4. **Check outputs** - Review generated content
5. **Customize settings** - Adjust for your needs

---

## 📞 Support

- **Documentation**: See README.md for full documentation
- **API Reference**: http://localhost:8000/docs
- **Issues**: Report problems on GitHub
- **Examples**: Check `examples/` directory

---

## 💡 Tips for Success

1. **Use trending topics** for maximum viral potential
2. **Experiment with different categories** (motivation, business, education)
3. **Customize voice type** based on your audience preference
4. **Try different image styles** (cinematic, bollywood, animated)
5. **Review and refine** generated content before publishing
6. **Monitor analytics** to see what works best

---

## 🎉 You're Ready!

Your Hindi AI Automation Platform is now running. Start creating viral Hindi content automatically!

**Happy content creation!** 🚀

---

<div align="center">

### Made with ❤️ for Indian Content Creators

</div>