# 🚀 Render + Streamlit Cloud Deployment Guide

**Zero Code Changes Required** - Deploy using existing configuration!

---

## 📋 Prerequisites

Before you start:
- ✅ GitHub account (to push your code)
- ✅ Render account ([render.com](https://render.com) - sign up free)
- ✅ Streamlit Cloud account ([streamlit.io/cloud](https://streamlit.io/cloud) - sign up free)
- ✅ Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
- ✅ Code pushed to GitHub repository

---

## 🎯 Deployment Overview

We'll deploy in 2 steps:
1. **Backend** → Render (using your existing Dockerfile)
2. **Frontend** → Streamlit Cloud (using your existing Streamlit app)

**Total Time**: ~15 minutes

---

## 🔧 Part 1: Deploy Backend on Render

### Step 1: Push Code to GitHub (if not already)

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started" → Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. **Dashboard** → Click "New +" → Select "Web Service"

2. **Connect Repository**:
   - Find and select: `Road-Safety-Intervention-Chatbot`
   - Click "Connect"

3. **Configure Service**:

   **Basic Settings:**
   - **Name**: `road-safety-backend` (or any name you prefer)
   - **Region**: Choose closest to your users (e.g., Oregon, Frankfurt, Singapore)
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: `backend`

   **Build Settings:**
   - **Runtime**: `Docker`
   - Render will automatically detect your `backend/Dockerfile`

   **Instance Type:**
   - Select **Free** tier to start (512MB RAM, 0.1 CPU)
   - Or **Starter** ($7/month) for better performance

4. **Environment Variables**:

   Click "Add Environment Variable" and add these:

   | Key | Value |
   |-----|-------|
   | `GEMINI_API_KEY` | `your_actual_gemini_api_key_here` |
   | `API_KEYS` | `prod-key-abc123,prod-key-xyz789` |
   | `ENVIRONMENT` | `production` |
   | `LOG_LEVEL` | `info` |
   | `PORT` | `8000` |

   **Generate secure API keys**: Use random strings, e.g.:
   ```
   prod-key-a8f3d9e2b1c4f5a6
   prod-key-x7y2z9w3k8m5n1p4
   ```

5. **Advanced Settings** (Optional):

   - **Auto-Deploy**: Keep "Yes" (deploys on git push)
   - **Health Check Path**: `/health`

6. **Create Web Service**:

   Click "Create Web Service" button at the bottom

### Step 4: Wait for Deployment

- Render will:
  1. Clone your repository
  2. Build the Docker image (2-5 minutes)
  3. Deploy your backend
  4. Provide you with a URL

- **Your backend URL** will be something like:
  ```
  https://road-safety-backend.onrender.com
  ```

### Step 5: Test Backend

Once deployed (status shows "Live"):

1. **Health Check**:
   ```
   https://road-safety-backend.onrender.com/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **API Documentation**:
   ```
   https://road-safety-backend.onrender.com/docs
   ```

3. **Test Search** (using curl or browser):
   ```bash
   curl -X POST "https://road-safety-backend.onrender.com/api/v1/search" \
     -H "X-API-Key: prod-key-abc123" \
     -H "Content-Type: application/json" \
     -d '{"query": "faded stop sign", "max_results": 3}'
   ```

**Important Notes:**
- ⚠️ Free tier "spins down" after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds
- Upgrade to Starter ($7/month) for always-on service

---

## 🎨 Part 2: Deploy Frontend on Streamlit Cloud

### Step 1: Create Streamlit Cloud Account

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "Sign up" → Sign in with GitHub
3. Authorize Streamlit Cloud to access your repositories

### Step 2: Deploy New App

1. **Dashboard** → Click "New app"

2. **Repository, branch, and file path**:
   - **Repository**: Select `Road-Safety-Intervention-Chatbot`
   - **Branch**: `main` (or your deployment branch)
   - **Main file path**: `frontend/app.py`

3. **Advanced Settings** → **Secrets**:

   Click "Advanced settings" → Add secrets in TOML format:

   ```toml
   API_URL = "https://road-safety-backend.onrender.com"
   API_KEY = "prod-key-abc123"
   ```

   **Important**:
   - Use your actual Render backend URL (from Part 1, Step 4)
   - Use one of the API keys you set in Render (from Part 1, Step 3)
   - NO trailing slash in API_URL

4. **Python Version**:
   - Leave as "3.11" (auto-detected from your requirements.txt)

5. **Deploy!**:

   Click "Deploy!" button

### Step 3: Wait for Deployment

- Streamlit will:
  1. Clone your repository
  2. Install dependencies from `frontend/requirements.txt` (1-2 minutes)
  3. Launch your Streamlit app
  4. Provide you with a URL

- **Your frontend URL** will be something like:
  ```
  https://road-safety-intervention.streamlit.app
  ```

### Step 4: Test Frontend

Once deployed:

1. **Visit your Streamlit app URL**

2. **Test Connection**:
   - Look for "Test Connection" button in sidebar (if available)
   - Or try a search query immediately

3. **Full Feature Test**:
   - Search: "damaged speed breaker on national highway"
   - Upload an image (test image analysis)
   - Generate a PDF report
   - Try budget optimization

**Troubleshooting:**
- If connection fails, check:
  - ✅ API_URL is correct (no trailing slash)
  - ✅ API_KEY matches one from Render
  - ✅ Backend is "Live" on Render
  - ✅ No typos in secrets

---

## ✅ Verify Complete Deployment

### Backend Checklist
- [ ] Render shows "Live" status
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/docs` shows API documentation
- [ ] Can make API requests with API key

### Frontend Checklist
- [ ] Streamlit app loads without errors
- [ ] Can submit search queries
- [ ] Results appear with IRC references
- [ ] Advanced features work (PDF, images, analytics)

---

## 🔄 Auto-Deployment Setup

Both platforms support auto-deployment:

### Render
- ✅ Already enabled by default
- Deploys on every `git push` to your branch
- Check deploy logs in Render dashboard

### Streamlit Cloud
- ✅ Already enabled by default
- Deploys on every `git push` to your branch
- Check "Manage app" → "Logs" for deployment status

**Workflow:**
```bash
git add .
git commit -m "Update feature X"
git push origin main
# Both backend and frontend will auto-deploy!
```

---

## 💰 Cost Breakdown

### Free Tier (Perfect for Testing)
- **Render**: Free (512MB RAM, spins down after 15min inactivity)
- **Streamlit Cloud**: Free (1GB resources)
- **Gemini API**: Pay-per-use (~$0-5/month for light usage)
- **Total**: $0-5/month

### Production Tier (Recommended)
- **Render Starter**: $7/month (always-on, 512MB RAM)
- **Streamlit Cloud**: Free tier is usually sufficient
- **Gemini API**: ~$10-20/month (moderate usage)
- **Total**: $17-27/month

---

## 🎯 Environment Variables Reference

### Backend (Render)

| Variable | Value | Notes |
|----------|-------|-------|
| `GEMINI_API_KEY` | Your Gemini API key | Get from Google AI Studio |
| `API_KEYS` | Comma-separated keys | Generate random secure strings |
| `ENVIRONMENT` | `production` | Required |
| `LOG_LEVEL` | `info` | Optional: debug, info, warning, error |
| `PORT` | `8000` | Render auto-assigns, but good to set |

### Frontend (Streamlit Cloud)

```toml
API_URL = "https://your-backend.onrender.com"
API_KEY = "one_of_your_backend_api_keys"
```

---

## 🐛 Troubleshooting Guide

### Backend Issues

**Problem**: Build fails on Render
- **Solution**: Check Render logs → "Events" tab
- Common issues:
  - Missing dependencies in `requirements.txt`
  - Dockerfile errors (unlikely - yours is tested)
  - Out of memory (upgrade to Starter plan)

**Problem**: Backend shows "Live" but `/health` fails
- **Solution**:
  - Wait 30-60 seconds after first deploy
  - Check logs for Python errors
  - Verify `PORT` environment variable is set

**Problem**: Database/Vector store not found
- **Solution**:
  - Your Dockerfile already handles this
  - App generates data from CSV at startup
  - Check logs for initialization messages

### Frontend Issues

**Problem**: "Connection Error" or "API not reachable"
- **Solution**:
  1. Verify `API_URL` in secrets (no trailing slash)
  2. Verify `API_KEY` matches Render environment variable
  3. Test backend directly: `https://your-backend.onrender.com/health`
  4. Check Render backend is "Live" (not sleeping)

**Problem**: App loads but search returns no results
- **Solution**:
  - Check backend logs on Render
  - Verify Gemini API key is valid
  - Test backend API directly with curl

**Problem**: Slow first request (30-60 seconds)
- **Solution**:
  - This is normal on Render free tier (cold start)
  - Upgrade to Starter plan for always-on service
  - Or accept 30-60s delay after 15min inactivity

### General Issues

**Problem**: Auto-deployment not working
- **Solution**:
  - Check webhook settings in GitHub
  - Re-authenticate Render/Streamlit with GitHub
  - Manually trigger deploy from dashboard

---

## 🎉 Success! What You've Achieved

✅ **Backend**: Deployed on Render with Docker
✅ **Frontend**: Deployed on Streamlit Cloud
✅ **Auto-Deploy**: Enabled on both platforms
✅ **24/7 Availability**: Works even when your computer is off
✅ **Public URLs**: Accessible from anywhere
✅ **Zero Code Changes**: Used existing configuration

---

## 🚀 Next Steps

### Recommended Enhancements

1. **Custom Domain** (Optional):
   - Render: Add custom domain in dashboard (requires paid plan)
   - Streamlit: Use Streamlit's subdomain or upgrade for custom domain

2. **Monitoring** (Recommended):
   - Render: Built-in metrics in dashboard
   - Streamlit: Check "Manage app" → "Logs"
   - Set up uptime monitoring (e.g., UptimeRobot - free)

3. **Database Backups** (Important):
   - Your data is in Docker container (ephemeral on Render)
   - Consider using Render Disk storage for persistence
   - Or migrate to PostgreSQL on Render

4. **HTTPS** (Built-in):
   - Both Render and Streamlit provide free SSL
   - Your URLs are automatically HTTPS

5. **Rate Limiting** (Optional):
   - Add to your API for production use
   - Protect against abuse

---

## 📞 Support & Resources

### Documentation
- **Render Docs**: https://render.com/docs
- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Your API Docs**: `https://your-backend.onrender.com/docs`

### Community
- Render Community: https://community.render.com
- Streamlit Forum: https://discuss.streamlit.io

### Getting Help
- Check deployment logs first (usually shows the issue)
- Search Render/Streamlit community forums
- GitHub issues on your repository

---

## 🎊 You're All Set!

Your Road Safety Intervention AI is now:
- 🌐 **Deployed globally**
- 🔄 **Auto-updating** on every git push
- 💪 **Production-ready**
- 🆓 **Running on free tier** (or paid for better performance)

**Share your app**:
- Frontend: `https://your-app.streamlit.app`
- Backend API: `https://your-backend.onrender.com/docs`

Happy deploying! 🚀
