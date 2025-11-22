# Deployment Guide

## Backend (Render)

### Option 1: Using Render Dashboard
1. Create new Web Service
2. Connect your GitHub repository: `pranavv1210/Multi-Agent-Tourism-Project`
3. Configure Service:
   - **Name**: tourism-orchestrator-backend (or your choice)
   - **Root Directory**: Leave empty (use project root)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `USER_AGENT` = `tourism-planner/1.0 (+your-email@example.com)`
   - `ALLOWED_ORIGINS` = `https://your-frontend-url.vercel.app`
   - `LOG_LEVEL` = `INFO`
5. Deploy and wait for build to complete
6. Test health check: `https://your-backend.onrender.com/health`

**Important**: The `runtime.txt` file must be in the repository root (not backend folder) for Render to detect it.

### Option 2: Using render.yaml (Infrastructure as Code)
Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: tourism-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: USER_AGENT
        value: tourism-planner/1.0 (+your-email@example.com)
      - key: ALLOWED_ORIGINS
        value: https://your-frontend-url.vercel.app
      - key: LOG_LEVEL
        value: INFO
```

### Troubleshooting Render Build Errors
If you encounter `metadata-generation-failed` errors:
1. The `runtime.txt` file specifies Python 3.11.9
2. Ensure all dependencies are compatible with Python 3.11
3. Check build logs for specific package causing issues
4. Try clearing Render's build cache (Settings → Clear build cache)

## Frontend (Vercel)
1. Import project.
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Environment variable:
   - `VITE_BACKEND_URL=https://<your-backend-host>`
6. Deploy. Access site via generated URL.

## Single Service Option
You can serve built frontend from backend using a static files mount (not implemented here to keep clarity). Recommended: deploy separately for scalability.

## .env Examples
```
# backend/.env
USER_AGENT=your-email-or-app-name@example.com
LOG_LEVEL=INFO

# frontend/.env
VITE_BACKEND_URL=https://your-backend-host
```

## Rate Limiting & Observability
- Caching reduces external calls frequency.
- Structured logs suitable for ingestion (JSON lines).
- Consider adding request limiting middleware if exposed publicly.

## Post Deployment Test
```bash
curl https://<backend-host>/health
curl -X POST https://<backend-host>/api/plan -H "Content-Type: application/json" -d '{"message":"weather and places in Bangalore"}'
```

## Troubleshooting
- 429 from Nominatim/Overpass: increase TTL or reduce query frequency.
- Empty place: ensure message contains a recognizable place or extend heuristics.
- Weather missing precipitation probability: possible time mismatch; retry automatically applied.
