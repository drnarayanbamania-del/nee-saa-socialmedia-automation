# ⚡ Quick Start - Deploy to Vercel

**Deploy your AI Cinematic Video Studio in 5 minutes!**

---

## 🎯 **Ultra-Fast Deploy**

```bash
# 1. Setup
git clone <your-repo>
cd studio-cinematic-ai-factory

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Deploy
chmod +x deploy_vercel.sh
./deploy_vercel.sh
```

---

## 📋 **Prerequisites Checklist**

- [ ] Node.js 18+ installed
- [ ] Python 3.9+ installed
- [ ] Vercel account (free)
- [ ] OpenAI API key
- [ ] Git repository

---

## 🔑 **Required API Keys**

Get these before deploying:

### **1. OpenAI API Key** (Required)
```
Platform: platform.openai.com/api-keys
Cost: ~$0.45/video
```

### **2. ElevenLabs API Key** (Optional)
```
Platform: elevenlabs.io/api
Cost: ~$0.10/video
If not provided, uses Google TTS (free)
```

### **3. Vercel Account** (Free)
```
Platform: vercel.com/signup
Cost: FREE for hobby tier
```

---

## 🚀 **Deploy Commands**

### **Interactive Deployment**
```bash
./deploy_vercel.sh
# → Prompts for all options
# → Checks everything
# → Deploys with guidance
```

### **Direct Deploy**
```bash
# Preview (test first)
vercel

# Production (go live)
vercel --prod
```

### **One-Click**
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

---

## 📊 **Environment Variables**

Add to Vercel dashboard or `.env`:

```bash
# Required
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
JWT_SECRET=your-super-secret-32-char-min
ADMIN_API_KEY=your-admin-key-here

# Optional
ELEVENLABS_API_KEY=your-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

**Quick Generate:**
```bash
# Generate JWT_SECRET
openssl rand -base64 32

# Generate ADMIN_API_KEY
echo "st_admin_$(openssl rand -hex 16)"
```

---

## 🧪 **Test After Deploy**

```bash
# Replace with your deployment URL
URL="https://your-project.vercel.app"

# Test health
curl $URL/api/v1/health

# Test trending
curl $URL/api/v1/trending

# Test video generation
curl -X POST $URL/api/v1/video/generate-sync \
  -H "Authorization: Bearer sk-admin-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"topic": "morning routine"}'
```

**Browser Test:**
```
Open: https://your-project.vercel.app
Click: "Generate Video"
Watch: Progress tracker
Result: Download video
```

---

## 📱 **Access Your Studio**

After deployment:

```
Dashboard:        https://your-project.vercel.app
API Base:         https://your-project.vercel.app/api/v1
Progress Tracker: https://your-project.vercel.app/progress_tracker.html
Health Check:     https://your-project.vercel.app/api/v1/health
```

---

## 💰 **Cost Estimate**

### **Free Tier (Hobby)**
```
Videos per day: 10-50
Cost: $0/month
Best for: Testing, personal use
```

### **Pro Plan**
```
Videos per day: 100-500
Cost: $20-50/month
Best for: Content creators
```

**Per Video:** ~$0.57
- OpenAI (GPT-4 + DALL-E): $0.45
- ElevenLabs: $0.10
- Vercel: $0.02

---

## 🎛️ **Common Issues**

### **Build Fails**
```bash
# Check logs
vercel logs

# Common fix: Add missing env vars
vercel env add OPENAI_API_KEY
```

### **API Timeout**
- Video > 60s? Use async endpoint
- Check memory: 3008 MB limit
- Optimize images

### **CORS Errors**
- Already configured in api/index.py
- Check API_URL detection

---

## 🔥 **Pro Tips**

### **Before Production:**
1. Change default `ADMIN_API_KEY`
2. Add real API keys to Vercel
3. Test with preview deployment first
4. Set up custom domain

### **For High Volume:**
1. Use Upstash Redis for queue
2. Implement webhooks
3. Add rate limiting
4. Monitor costs daily

### **For Teams:**
1. Add members in Vercel
2. Use GitHub integration
3. Set up preview deployments
4. Add branch protection

---

## 📞 **Quick Support**

**Deployment Guide**: `DEPLOY_VERCEL.md`
**API Docs**: In `api/index.py` comments
**Vercel Docs**: vercel.com/docs
**Logs**: `vercel logs`

---

## 🎊 **Success Checklist**

After deploying, verify:

- [ ] Dashboard loads
- [ ] API health returns 200
- [ ] Trending topics load
- [ ] Video generation works
- [ ] Progress updates
- [ ] Mobile looks good
- [ ] No errors in logs
- [ ] Cost within budget

---

## 🎯 **Next Steps**

1. **Deploy**: `./deploy_vercel.sh`
2. **Test**: Generate first video
3. **Monitor**: Vercel dashboard
4. **Customize**: Your branding
5. **Launch**: Share with users!

---

## 🚀 **Deploy Now!**

```bash
cd studio-cinematic-ai-factory
./deploy_vercel.sh
```

**Your AI video studio will be live in 3-5 minutes!** 🎬✨

---

**Questions?** See `DEPLOY_VERCEL.md` for detailed guide.

**Happy video generating!** 🎉