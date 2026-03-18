# 🚀 Deploy to Vercel - Complete Guide

Deploy your AI-Powered Cinematic Video Studio to Vercel in **10 minutes** with serverless architecture.

## 📋 Prerequisites

- [ ] Vercel account (free tier available)
- [ ] GitHub/GitLab account connected to Vercel
- [ ] API Keys:
  - OpenAI API Key
  - ElevenLabs API Key (optional, for voice)
  - PostgreSQL database (Supabase free tier recommended)
  - Redis (Upstash free tier recommended)

## 🎯 Deployment Options

### **Option 1: One-Click Deploy (Recommended)**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/studio-cinematic-ai-factory&env=OPENAI_API_KEY,ELEVENLABS_API_KEY,DATABASE_URL,REDIS_URL,JWT_SECRET,ADMIN_API_KEY&envDescription=API%20Keys%20for%20AI%20Video%20Studio&envLink=https://github.com/yourusername/studio-cinematic-ai-factory/blob/main/.env.example&project-name=studio-cinematic-ai&repository-name=studio-cinematic-ai-factory)

### **Option 2: Manual Deploy**

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel --prod
```

### **Option 3: Git Integration**

1. Push code to GitHub
2. Import project in Vercel dashboard
3. Add environment variables
4. Deploy

---

## 🔧 Step-by-Step Deployment

### **Step 1: Prepare Environment Variables**

Create `.env.production`:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
ADMIN_API_KEY=your-admin-api-key-for-authentication

# Optional (but recommended)
ELEVENLABS_API_KEY=your-elevenlabs-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://:password@host:6379

# Configuration
ENVIRONMENT=production
MAX_VIDEO_DURATION=90
MAX_CONCURRENT_JOBS=3
```

### **Step 2: Configure Vercel**

The `vercel.json` file is pre-configured:

```json
{
  "builds": [
    {"src": "api/index.py", "use": "@vercel/python"},
    {"src": "frontend/*.html", "use": "@vercel/static"}
  ],
  "routes": [
    {"src": "/api/(.*)", "dest": "/api/index.py"},
    {"src": "/(.*)", "dest": "/frontend/$1"}
  ],
  "functions": {
    "api/index.py": {
      "memory": 3008,
      "maxDuration": 60
    }
  }
}
```

### **Step 3: Deploy**

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

---

## 🎛️ Environment Variables in Vercel

### **Add via Vercel Dashboard:**

1. Go to project settings
2. Click "Environment Variables"
3. Add each variable:

| Variable | Value | Environment |
|----------|-------|-------------|
| `OPENAI_API_KEY` | sk-... | Production |
| `JWT_SECRET` | random-string | Production |
| `ADMIN_API_KEY` | your-admin-key | Production |
| `ELEVENLABS_API_KEY` | your-key | Production (optional) |

### **Add via CLI:**

```bash
vercel env add OPENAI_API_KEY
vercel env add JWT_SECRET
vercel env add ADMIN_API_KEY
```

---

## 🗄️ Database Setup (Supabase)

### **Create Free PostgreSQL:**

1. Go to [supabase.com](https://supabase.com)
2. Create new project (free tier)
3. Copy database URL
4. Add to Vercel environment variables:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### **Run Migrations:**

```bash
# Connect to Supabase
psql $DATABASE_URL

# Run schema
\i database/schema.sql
```

---

## 🔄 Queue Setup (Upstash Redis)

### **Create Free Redis:**

1. Go to [upstash.com](https://upstash.com)
2. Create Redis database (free tier)
3. Copy REST URL
4. Add to Vercel:

```bash
REDIS_URL=https://your-redis.upstash.io
REDIS_TOKEN=your-token
```

---

## 📊 Vercel Configuration Details

### **Serverless Functions**

- **Location**: `api/index.py`
- **Runtime**: Python 3.9
- **Memory**: 3008 MB (max)
- **Timeout**: 60 seconds (max)
- **Region**: Automatically optimized

### **Frontend**

- **Location**: `frontend/*.html`
- **Type**: Static files
- **CDN**: Automatic global CDN
- **Cache**: 1 year for assets

### **API Routes**

```
/api/v1/health              → Health check
/api/v1/trending            → Get trending topics
/api/v1/video/generate      → Generate video (async)
/api/v1/video/generate-sync → Generate video (sync)
/api/v1/video/status/{id}   → Check status
/api/v1/content/library     → Get generated videos
```

---

## 🚀 Post-Deployment

### **Test Your Deployment:**

```bash
# Get deployment URL
DEPLOYMENT_URL=$(vercel ls | grep production | awk '{print $2}')

# Test health endpoint
curl $DEPLOYMENT_URL/api/v1/health

# Test trending topics
curl $DEPLOYMENT_URL/api/v1/trending

# Test video generation (with API key)
curl -X POST $DEPLOYMENT_URL/api/v1/video/generate \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"topic": "morning routine"}'
```

### **Verify in Browser:**

Open your deployment URL:
- Dashboard: `https://your-project.vercel.app`
- Progress Tracker: `https://your-project.vercel.app/progress`

---

## 🎛️ Performance Optimization

### **Enable in Vercel Dashboard:**

1. **CDN**: Already enabled for static assets
2. **Compression**: Automatic gzip/brotli
3. **Image Optimization**: Use `/_next/image`
4. **Edge Functions**: For global API routes

### **Cache Configuration:**

```json
{
  "headers": [
    {
      "source": "/frontend/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

---

## 💰 Cost Estimation

### **Free Tier Limits:**

| Resource | Limit | Cost |
|----------|-------|------|
| Serverless Functions | 100 GB-hours | Free |
| Edge Functions | 500k executions | Free |
| Bandwidth | 100 GB | Free |
| Build Time | 6,000 minutes | Free |

### **Typical Usage:**

- **10 videos/day**: Within free tier
- **100 videos/day**: ~$20/month
- **1000 videos/day**: ~$150/month

---

## 🔍 Monitoring & Logs

### **View Logs:**

```bash
# CLI
vercel logs

# Dashboard
# Go to project > Deployments > [deployment] > Logs
```

### **Set Up Alerts:**

1. Go to Vercel dashboard
2. Project settings > Notifications
3. Add email/Slack for errors

---

## 🐛 Troubleshooting

### **Build Fails:**

```bash
# Check build logs
vercel logs [deployment-url]

# Common issues:
# 1. Missing environment variables
# 2. Python package conflicts
# 3. Memory limits exceeded
```

### **API Timeout:**

- Reduce video generation time
- Use async endpoints
- Implement webhook callbacks
- Consider Upstash QStash for background jobs

### **Memory Errors:**

- Optimize image sizes
- Process in smaller batches
- Use streaming responses
- Upgrade to Pro plan (more memory)

---

## 🔄 Continuous Deployment

### **Git Integration:**

1. Connect GitHub repo in Vercel
2. Enable "Deploy on push"
3. Add branch protection
4. Auto-deploy on merge to main

### **Preview Deployments:**

Every pull request gets a preview URL:
```
https://your-project-git-feature-branch.vercel.app
```

---

## 🛡️ Security

### **Best Practices:**

✅ **Never commit `.env` files** - Use Vercel env vars
✅ **Rotate API keys** - Regularly update in dashboard
✅ **Use JWT_SECRET** - Minimum 32 characters
✅ **Enable 2FA** - On Vercel and GitHub
✅ **Set up CSP headers** - Prevent XSS

### **Environment Variable Protection:**

```bash
# Sensitive vars should be encrypted
vercel env add OPENAI_API_KEY --sensitive
```

---

## 🌍 Custom Domain

### **Add Your Domain:**

1. Go to project settings > Domains
2. Add domain: `studio.yourdomain.com`
3. Update DNS records
4. Wait for SSL certificate (automatic)

### **Configuration:**

```bash
# Using CLI
vercel domains add studio.yourdomain.com
```

---

## 📱 Vercel Mobile App

Monitor deployments on the go:
- iOS: [App Store](https://apps.apple.com/app/vercel/id1526710674)
- Android: [Play Store](https://play.google.com/store/apps/details?id=com.vercel.app)

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Dashboard loads: `https://your-project.vercel.app`
- [ ] API health: `/api/v1/health` returns 200
- [ ] Trending topics: `/api/v1/trending` returns data
- [ ] Video generation works: `/api/v1/video/generate`
- [ ] Progress tracking shows updates
- [ ] Content library displays videos
- [ ] Mobile responsive works
- [ ] Logs show no errors
- [ ] Costs within budget
- [ ] Custom domain working (optional)

---

## 📞 Support

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Community**: [vercel.com/community](https://vercel.com/community)
- **Status**: [vercel-status.com](https://vercel-status.com)

---

## 🎬 Next Steps

After successful deployment:

1. **Test thoroughly** with different topics
2. **Monitor costs** in Vercel dashboard
3. **Set up analytics** with Vercel Analytics
4. **Optimize performance** based on logs
5. **Scale up** as needed

---

**🚀 Your AI Cinematic Video Studio is ready for Vercel!**

Deploy now and start creating viral Hindi videos automatically! 🎬✨