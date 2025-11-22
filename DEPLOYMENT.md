# Deployment Guide

## Backend (Render)
1. Create new Web Service.
2. Connect repository.
3. Set Environment:
   - Python version: 3.11
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `USER_AGENT=your-email-or-app-name@example.com`
   - `LOG_LEVEL=INFO`
5. Deploy. Health check at `/health`.

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
