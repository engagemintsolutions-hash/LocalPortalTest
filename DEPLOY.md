# Deployment Guide

## Quick Deploy Options

### Option 1: Vercel (Recommended for Frontend)

#### Deploy Frontend to Vercel
```bash
cd frontend
vercel
```

Follow prompts:
- Project name: `property-search-portal`
- Framework: Static HTML
- Build command: (leave empty)
- Output directory: `.`

#### Environment Variables
Add in Vercel dashboard:
- `API_URL` = your backend URL

### Option 2: GitHub Pages (Free, Static Only)

#### Frontend Only
```bash
# In GitHub repo settings
Settings → Pages → Source: main branch → /frontend folder
```

URL will be: `https://engagemintsolutions-hash.github.io/LocalPortalTest/`

**Note**: Backend API needs separate hosting

### Option 3: Railway.app (Full Stack)

#### Deploy Both Frontend + Backend
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

Add environment variables in Railway dashboard.

### Option 4: Render (Free Tier)

#### Backend API
1. Go to render.com
2. New Web Service
3. Connect GitHub repo
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `python smart_api.py`
   - Port: 8000

#### Frontend
1. New Static Site
2. Build: (none)
3. Publish: `frontend`

---

## Production Checklist

### Before Deploying:

- [ ] Update API URLs in frontend JS files
- [ ] Add CORS domains (not wildcard *)
- [ ] Set up environment variables
- [ ] Configure AWS credentials (for S3)
- [ ] Add rate limiting
- [ ] Set up SSL/HTTPS
- [ ] Configure custom domain
- [ ] Add analytics (Google Analytics)
- [ ] Test on mobile devices
- [ ] Add error monitoring (Sentry)

### Environment Variables Needed

```bash
# Backend
DATABASE_URL=postgresql://...  # If using database
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=eu-west-2
STRIPE_SECRET_KEY=sk_live_...  # For real payments

# Frontend
VITE_API_URL=https://your-api.com
```

---

## Current Status

✅ **Ready to deploy**:
- Frontend: Static HTML/CSS/JS (works on any host)
- Backend: Python FastAPI (works on Railway/Render/Vercel)
- Data: JSON file (50 properties)

⏳ **For production**:
- Set up PostgreSQL database
- Load full S3 data
- Real Stripe integration
- Custom domain

---

## Quick Test Deploy (Now)

### Vercel (2 minutes)
```bash
cd "C:\Sales Portal"
vercel --prod
```

Your site will be live at: `https://property-search-xxxx.vercel.app`

---

Want me to deploy now?
