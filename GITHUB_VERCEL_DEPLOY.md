# Bamania's Cine AI — GitHub → Vercel Deployment

This project is configured to deploy to **Vercel** after you push to **GitHub**.

## 1) Push the repository to GitHub

Use the included helper:

```bash
chmod +x push_to_github.sh
./push_to_github.sh
```

Or push manually:

```bash
git init
git add .
git commit -m "feat: prepare app for vercel deployment"
git branch -M main
git remote add origin https://github.com/drnarayanbamania-del/Bamania-scine-ai.git
git push -u origin main
```

## 2) Import the repo in Vercel

- Go to: https://vercel.com/new
- Import: `drnarayanbamania-del/Bamania-scine-ai`
- Framework should detect as: **Vite**
- Root directory: `./`
- Build command: `npm run build`
- Output directory: `dist`

## 3) Add environment variables in Vercel

Use values from `.env.vercel.example`.

Recommended minimum:

- `ENVIRONMENT=production`
- `ADMIN_API_KEY=your-secure-admin-key`

Optional:

- `OPENAI_API_KEY=...`
- `YOUTUBE_API_KEY=...`
- `YOUTUBE_REGION=IN`
- `SARVAM_API_KEY=...`

## 4) Optional: Auto deploy from GitHub Actions

This repo includes:

- `.github/workflows/vercel-deploy.yml`

Add these GitHub repository secrets:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

Then every push to `main` can deploy automatically to Vercel.

## 5) Verify deployment

After deploy:

- App: `https://your-vercel-domain.vercel.app`
- API health: `https://your-vercel-domain.vercel.app/api/v1/health`
- Viral content: `https://your-vercel-domain.vercel.app/api/v1/viral-content`

## Notes

- The UI is Vite/React and builds into `dist`.
- The lightweight API is served by `api/index.py`.
- Heavy cinematic rendering should be handled by external workers/services for production scale.
