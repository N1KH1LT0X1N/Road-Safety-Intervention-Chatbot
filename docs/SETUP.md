# Setup Guide

Complete setup guide for the Road Safety Intervention AI system.

## Prerequisites

Before you begin, ensure you have:

- Python 3.11 or higher
- Git
- Google Gemini API Key
- (Optional) Docker and Docker Compose

## Step-by-Step Setup

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key (you'll need it later)

### 2. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd Road-Safety-Intervention-Chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Open .env in your favorite editor
nano .env  # or vim, code, etc.
```

Edit the `.env` file and set:

```bash
# Required
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Generate random API keys for authentication
# You can use: python -c "import secrets; print(','.join([secrets.token_urlsafe(32) for _ in range(3)]))"
API_KEYS=random_key_1,random_key_2,random_key_3

# Optional (defaults are usually fine)
ENVIRONMENT=development
LOG_LEVEL=info
```

### 4. Process the CSV Data

This is the most important step - it processes the CSV file and creates the vector database:

```bash
# Make sure you're in the project root
python backend/scripts/setup_database.py
```

This script will:
1. Load and clean the CSV file
2. Extract features (speed ranges, dimensions, colors, etc.)
3. Generate embeddings using Gemini API (this may take 2-3 minutes)
4. Create ChromaDB vector store
5. Save processed JSON data

Expected output:
```
[1/4] Processing CSV data...
Processed 105 interventions

[2/4] Saving processed data...
Saved json: backend/data/processed/interventions.json
Saved csv: backend/data/processed/interventions_cleaned.csv
Saved report: backend/data/processed/data_quality_report.txt

[3/4] Generating embeddings with Gemini...
Generated 105 embeddings

[4/4] Creating vector store...
Vector store created with 105 documents

✅ DATABASE SETUP COMPLETE!
```

### 5. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Starting Road Safety Intervention API...
INFO:     Initializing Gemini service...
INFO:     Initializing vector store...
INFO:     Initializing database...
INFO:     API initialized successfully!
```

Test the API:
```bash
# In a new terminal
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": true,
  "vector_store": true
}
```

### 6. Test the API with a Search

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "X-API-Key: your_api_key_from_env" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "faded stop sign on highway",
    "max_results": 3
  }'
```

Or use the test script:
```bash
python backend/scripts/test_queries.py
```

### 7. Start the Frontend (Optional)

In a new terminal:

```bash
cd frontend
pip install -r requirements.txt

# Copy frontend env
cp .env.example .env

# Edit frontend/.env
# Set API_URL=http://localhost:8000
# Set API_KEY=one_of_your_api_keys
```

Start Streamlit:
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### 8. Install CLI Tool (Optional)

```bash
cd cli
pip install -e .

# Configure
road-safety config set api_url http://localhost:8000
road-safety config set api_key your_api_key_here

# Test
road-safety search query "damaged speed breaker"

# Interactive mode
road-safety interactive start
```

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# 1. Set up .env file (same as above)
cp .env.example .env
# Edit and add GEMINI_API_KEY and API_KEYS

# 2. Run setup script FIRST (outside Docker)
python backend/scripts/setup_database.py

# 3. Build and run with Docker Compose
docker-compose up --build

# Access:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:8501
```

## Troubleshooting

### Issue: "CSV file not found"

**Solution:** Make sure `GPT_Input_DB(Sheet1).csv` is in the project root directory.

### Issue: "Invalid API key" errors

**Solution:**
1. Check your `.env` file has the correct `GEMINI_API_KEY`
2. Make sure you've activated your virtual environment
3. Verify the API key is valid at Google AI Studio

### Issue: "ChromaDB collection not found"

**Solution:** Run the setup script again:
```bash
python backend/scripts/setup_database.py
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

### Issue: Slow embedding generation

**Solution:** This is normal. Generating 105 embeddings takes 2-3 minutes due to API rate limits. Be patient.

### Issue: Frontend can't connect to backend

**Solution:**
1. Make sure backend is running on port 8000
2. Check `frontend/.env` has correct `API_URL`
3. Verify `API_KEY` matches one from backend's `API_KEYS`

## Verification Checklist

After setup, verify everything works:

- [ ] Backend starts without errors
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/stats` endpoint returns database statistics
- [ ] Search API returns results for test query
- [ ] Frontend loads and can connect to backend
- [ ] CLI tool can perform searches

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **Try the Web App**: Use the Streamlit interface for a user-friendly experience
3. **Test Different Queries**: Try various road safety scenarios
4. **Review the Data**: Check `backend/data/processed/data_quality_report.txt`

## Production Deployment

See the main README.md for deployment instructions:
- Backend: Railway
- Frontend: Vercel
- Both: Full Docker Compose setup

## Support

If you encounter issues:
1. Check the logs for error messages
2. Review this troubleshooting section
3. Check GitHub issues
4. Create a new issue with error details
