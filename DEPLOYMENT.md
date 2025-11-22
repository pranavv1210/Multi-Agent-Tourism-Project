# Deployment Guide

## Backend (Render)

### Option 1: Using Render Dashboard
1. Create new Web Service
2. Connect your GitHub repository: `pranavv1210/Multi-Agent-Tourism-Project`
3. Configure Service:
   - **Name**: tourism-orchestrator-backend (or your choice)
   - **Root Directory**: **LEAVE BLANK** (Render must read runtime.txt from project root)
   - **Environment**: Python 3
   - **Region**: Choose closest to your users
   - **Branch**: main
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Auto-Deploy**: Yes (optional, deploys on every push)
4. Add Environment Variables:
   - `USER_AGENT` = `tourism-planner/1.0 (+your-email@example.com)`
   - `ALLOWED_ORIGINS` = `https://your-frontend-url.vercel.app`
   - `LOG_LEVEL` = `INFO`
5. Deploy and wait for build to complete
6. Test health check: `https://your-backend.onrender.com/health`

**CRITICAL**: 
- The `runtime.txt` file MUST be in the project root (not backend folder)
- Root Directory MUST be blank for Render to detect runtime.txt
- If you previously set Root Directory to "backend", delete it and save
- Render will look for runtime.txt in the repository root to determine Python version

### Alternative Configuration (Root Directory = `backend`)
If you prefer to set Render's Root Directory to `backend` instead of leaving it blank:
1. Set **Root Directory** to `backend`.
2. Place a copy of `runtime.txt` inside `backend/` (already added).
3. Build Command can then be simplified to `pip install -r requirements.txt` if you keep the new root-level `requirements.txt` delegator, OR `pip install -r requirements.txt` (which in that context refers to `backend/requirements.txt`).
4. Start Command (with Root Directory = backend): `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Ensure both `runtime.txt` files (root and backend) specify the same version.

This gives you two working deployment patterns:
| Pattern | Root Directory | runtime.txt location | Build Command | Start Command |
|---------|----------------|----------------------|---------------|---------------|
| Recommended | (blank) | `/runtime.txt` | `pip install -r backend/requirements.txt` | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Alternative | `backend` | `backend/runtime.txt` | `pip install -r requirements.txt` (delegated) | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

After switching approaches, always Clear Build Cache in Render before redeploying to force Python version re-selection.

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

#### Python Version Issues
**CRITICAL FIX**: Render's auto-detection of `runtime.txt` fails when using custom build commands. You MUST manually configure the Python version in Render Dashboard:

1. **Dashboard Manual Override** (Recommended - Immediate Fix):
   - Go to Render Dashboard → Your Service → Settings
   - Scroll to "Environment" section
   - Look for "Python Version" dropdown or field
   - If not visible, check if there's a "Native Environment" or similar toggle - enable it
   - Set Python version to **3.11** (Render may show 3.11.x where x is latest patch)
   - Save changes
   - Clear build cache and redeploy

2. **Verify File Detection** (If dashboard override not available):
   - The repository now contains THREE version specification files:
     - `runtime.txt` (root): `python-3.11.9`
     - `.python-version` (root): `3.11.9`
     - `backend/runtime.txt`: `python-3.11.9`
   - Render should detect at least one of these
   - If still using 3.13.4, Root Directory setting is interfering

3. **Root Directory Configuration**:
   - **MUST BE BLANK** for Render to read root-level version files
   - If set to `backend`, Render ignores root `runtime.txt` and `.python-version`
   - With blank Root Directory:
     - Build Command: `pip install -r backend/requirements.txt`
     - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Force Version Selection**:
   ```bash
   # In Render Shell (if available), verify Python version:
   python --version  # Should show 3.11.9, not 3.13.4
   ```

If Render is using Python 3.13.4 despite all version files:
- This is a Render platform issue with custom build commands overriding version detection
- Temporary workaround: Use `render.yaml` (Blueprint) instead of dashboard configuration
- The repository now includes `render.yaml` - delete your manual service and deploy via Blueprint

#### Metadata Generation Failed (pydantic-core)
If you see "Cargo, the Rust package manager, is not installed":
- This happens when Render uses Python 3.13 instead of 3.11
- pydantic-core 2.18.2 requires pre-built wheels for Python 3.11
- Follow "Python Version Issues" steps above to fix

#### Other Common Issues
1. **429 from Nominatim/Overpass**: Increase TTL or reduce query frequency
2. **Empty place**: Ensure message contains a recognizable place or extend heuristics
3. **Weather missing precipitation**: Possible time mismatch; retry automatically applied
4. **Build timeout**: Large dependencies may need longer build time (check Render plan limits)

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
