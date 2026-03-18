# 🚀 Bamania's Cine AI — Deploy to Vercel via GitHub

## Backend (Render.com)
URL: https://nee-saa-socialmedia-automation-1.onrender.com

## Frontend (Vercel)
Connected to Render backend via VITE_API_URL env variable.

---

## 1️⃣ Push to GitHub
```bash
git add .
git commit -m "feat: connect Render backend + Vercel deploy ready"
git push origin main
```

## 2️⃣ Import in Vercel
1. Go to https://vercel.com/new
2. Import: drnarayanbamania-del/Bamania-scine-ai
3. Framework: Vite (auto-detected)
4. Build Command: npm run build
5. Output Directory: dist

## 3️⃣ Add Environment Variable in Vercel
Key:   VITE_API_URL
Value: https://nee-saa-socialmedia-automation-1.onrender.com

## 4️⃣ Deploy → Done!

---

## Demo Login
Email:    demo@bamaniacineai.com
Password: demo123

## Backend Connection
- Auto-wakes Render backend on load
- Falls back to local mode if offline
- Status banner shows connection state
