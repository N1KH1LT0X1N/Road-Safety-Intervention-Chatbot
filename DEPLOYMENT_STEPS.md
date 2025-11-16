# Final Deployment Steps 🚀

## Your Backend URL
✅ **Backend URL**: `https://road-safety-intervention-chatbot-production.up.railway.app`

## Step 1: Get Your API Key from Railway

1. In Railway, go to your **backend service** (click on it in Architecture view)
2. Click **"Variables"** tab (or "Settings" → "Variables")
3. Look for `API_KEY` variable
4. **Copy the value** - you'll need this for Streamlit Cloud

**If `API_KEY` doesn't exist:**
1. Click **"New Variable"**
2. Name: `API_KEY`
3. Value: Generate a random string (e.g., use a password generator or `openssl rand -hex 32`)
4. Click **"Add"**
5. **Copy the value** you just created

## Step 2: Deploy Frontend to Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your **GitHub account** (same one you use for this repo)
3. Click **"New app"** button
4. Fill in:
   - **Repository**: `N1KH1LT0X1N/Road-Safety-Intervention-Chatbot`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
   - **App name**: `road-safety-chatbot` (or any name you like)
5. Click **"Deploy!"**

## Step 3: Set Environment Variables in Streamlit Cloud

After deployment (takes 1-2 minutes):

1. In Streamlit Cloud, click on your app
2. Click **"Settings"** (gear icon) in the top right
3. Click **"Secrets"** in the left sidebar
4. Add these secrets:

```toml
API_URL = "https://road-safety-intervention-chatbot-production.up.railway.app"
API_KEY = "your-api-key-from-railway-here"
```

5. Click **"Save"**

## Step 4: Test Your App!

1. Your Streamlit app will be at: `https://road-safety-chatbot.streamlit.app` (or whatever name you chose)
2. Open the app
3. Go to **Settings** → **API Configuration** in the sidebar
4. Click **"Test Connection"** - it should show ✅ Connection successful!
5. Try a search query like "damaged road sign"

## Your Final URLs

- **Backend API**: `https://road-safety-intervention-chatbot-production.up.railway.app`
- **Frontend App**: `https://your-app-name.streamlit.app` (you'll get this after deployment)

## Troubleshooting

### Connection fails?
- Check that `API_URL` in Streamlit Cloud matches exactly (with `https://`)
- Verify `API_KEY` matches between Railway and Streamlit Cloud
- Make sure Railway backend is running (check Railway logs)

### 401 Unauthorized?
- API keys don't match - double-check both places

### Backend not responding?
- Check Railway logs to see if backend is running
- Verify the backend URL is correct

## You're Done! 🎉

Once both are deployed and connected, your Road Safety Intervention AI is live!

