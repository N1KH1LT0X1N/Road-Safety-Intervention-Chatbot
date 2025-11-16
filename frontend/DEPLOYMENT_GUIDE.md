# Frontend Deployment Guide - Streamlit Cloud

## ⚠️ Important Note
**Streamlit apps cannot run on Vercel** because Streamlit requires persistent WebSocket connections, which serverless functions don't support. Use **Streamlit Cloud** instead (it's free and designed for Streamlit apps).

## Step-by-Step Deployment

### 1. Get Your Backend URL from Railway
1. Go to your Railway dashboard
2. Click on your backend service
3. Copy the **public URL** (e.g., `https://your-app-name.up.railway.app`)
4. Also get your **API key** from Railway environment variables

### 2. Deploy to Streamlit Cloud

#### Option A: Quick Deploy (Recommended)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `N1KH1LT0X1N/Road-Safety-Intervention-Chatbot`
5. Set **Main file path**: `frontend/app.py`
6. Click **"Deploy!"**

#### Option B: Manual Setup
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `N1KH1LT0X1N/Road-Safety-Intervention-Chatbot`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
   - **Python version**: `3.11` (or latest)

### 3. Configure Environment Variables

After deployment, go to **"Settings"** → **"Secrets"** and add:

```toml
API_URL = "https://your-railway-backend-url.up.railway.app"
API_KEY = "your-api-key-from-railway"
```

**How to get your Railway API key:**
1. Go to Railway dashboard
2. Click on your backend service
3. Go to **"Variables"** tab
4. Find `API_KEY` variable
5. Copy the value (or create one if it doesn't exist)

### 4. Update Backend CORS Settings

Your backend needs to allow requests from Streamlit Cloud. Check your Railway backend:

1. Go to Railway → Your backend service
2. Check that CORS is enabled (it should be - we set `allow_origins=["*"]`)

If you need to restrict it, update `backend/app/main.py`:
```python
allow_origins=["https://your-app-name.streamlit.app", "*"]
```

### 5. Test the Connection

1. Once deployed, your Streamlit app will be at: `https://your-app-name.streamlit.app`
2. Open the app
3. Go to **Settings** → **API Configuration** in the sidebar
4. The app should automatically use the environment variables
5. Click **"Test Connection"** to verify it works

## Troubleshooting

### Frontend can't connect to backend
- Check that `API_URL` in Streamlit Cloud matches your Railway URL
- Verify the Railway backend is running (check Railway logs)
- Make sure CORS is enabled in backend
- Check that `API_KEY` matches between frontend and backend

### Backend returns 401 Unauthorized
- Verify `API_KEY` in Streamlit Cloud matches Railway's `API_KEY`
- Check that the backend is using the same API key

### Backend returns 404
- Make sure the Railway URL is correct (should end with `.railway.app`)
- Verify the backend service is deployed and running

## Alternative: Deploy Frontend on Railway Too

If you prefer everything on Railway:

1. Create a new Railway service
2. Connect it to the same GitHub repo
3. Set root directory to `frontend/`
4. Use the Dockerfile in `frontend/` directory
5. Set environment variables:
   - `API_URL`: Your backend Railway URL
   - `API_KEY`: Your API key
6. Deploy!

## Your Deployment URLs

After deployment, you'll have:
- **Backend**: `https://your-backend-name.up.railway.app`
- **Frontend**: `https://your-app-name.streamlit.app`

Share the frontend URL with users! 🚀

