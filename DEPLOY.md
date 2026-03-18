# 🚀 Deploy Bamania's Cine AI to Vercel

## One-Click Deploy via GitHub

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Bamania's Cine AI v2.0 — Production Ready"
git remote add origin https://github.com/drnarayanbamania-del/Bamania-scine-ai.git
git push -u origin main
```

### Step 2 — Import to Vercel
1. Go to https://vercel.com/new
2. Import your GitHub repo: `drnarayanbamania-del/Bamania-scine-ai`
3. Framework: **Vite** (auto-detected)
4. Build Command: `npm run build`
5. Output Directory: `dist`
6. Click **Deploy**

### Step 3 — Add Environment Variables in Vercel
In Vercel Dashboard → Settings → Environment Variables:

```
ADMIN_API_KEY        = bca-demo-key-2025
ENVIRONMENT          = production
OPENAI_API_KEY       = sk-your-key
ELEVENLABS_API_KEY   = your-key
```

### Step 4 — Done! 🎉
Your app is live at: `https://bamania-scine-ai.vercel.app`

## API Endpoints (Auto-available after deploy)
- `GET  /api/health`             — Health check
- `POST /api/auth/login`         — Login
- `POST /api/auth/register`      — Register
- `GET  /api/projects`           — List projects
- `DELETE /api/projects/{id}`    — Delete project
- `POST /api/generate/video`     — Generate video
- `GET  /api/viral-content`      — Trending topics
- `POST /api/schedule`           — Schedule post
- `DELETE /api/schedule/{id}`    — Remove schedule
- `POST /api/publish`            — Publish to social
- `GET  /api/analytics`          — Analytics data

## Demo Credentials
```
Email:    demo@bamaniacineai.com
Password: demo123
```

## Local Development
```bash
# Frontend
npm install
npm run dev

# Backend (separate terminal)
pip install fastapi uvicorn pydantic
uvicorn api.index:app --reload --port 8000
```
