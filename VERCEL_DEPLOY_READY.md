# Bamania's Cine AI — Vercel Deploy Ready Setup

## What is ready
- Vite React frontend builds to `dist`
- FastAPI serverless API is available at `api/index.py`
- `vercel.json` is configured for:
  - Vite frontend output
  - Python serverless function routing
  - clean rewrites for `/api/*`

## Required environment variables in Vercel
Add these in **Vercel Project → Settings → Environment Variables**:

### Required
- `ENVIRONMENT=production`

### Optional
- `ADMIN_API_KEY=your-secure-admin-key`

If `ADMIN_API_KEY` is not set, demo API routes still work publicly.

## Deploy steps
1. Push this project to GitHub.
2. Import the repository into Vercel.
3. Framework preset: **Vite**
4. Build command: `npm run build`
5. Output directory: `dist`
6. Root directory: `./`
7. Add environment variables.
8. Deploy.

## Local pre-check
```bash
npm install
npm run build
```

## Important notes
- The frontend calls `/api/v1/viral-content` without exposing secrets in the browser.
- The API is lightweight and safe for Vercel serverless deployment.
- Heavy cinematic rendering should be moved to an external worker later if you want full production rendering on Vercel.

## Working routes after deploy
- `/` → main Bamania's Cine AI app
- `/api/v1/health` → health endpoint
- `/api/v1/trending` → trending topics
- `/api/v1/content/library` → content library demo data
- `/api/v1/viral-content` → viral YouTube + Instagram demo/live-ready content
- `/api/v1/video/generate` → queued mock-safe generation endpoint
- `/api/v1/video/generate-sync` → direct mock-safe generation endpoint

## Recommended production next step
For real video generation, use:
- Vercel for frontend + lightweight API
- external worker/container for rendering, voice, and uploads
- storage like S3/Supabase for generated files
