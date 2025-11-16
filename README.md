# 🚦 Road Safety Intervention AI

An AI-powered system for recommending road safety interventions based on IRC standards, using Google Gemini API and hybrid RAG search.

## 🌟 Features

### Core Features
- **Multi-Interface Support**: Web App (Streamlit), REST API (FastAPI), and CLI Tool
- **Hybrid Search**: Combines RAG (vector similarity) and structured queries
- **AI-Powered**: Google Gemini for embeddings, entity extraction, and synthesis
- **Comprehensive Database**: 105+ road safety interventions from IRC standards
- **Smart Recommendations**: Confidence scoring, detailed specifications, and IRC citations

### 🎉 WOW Features (Advanced Capabilities)

**🎨 Visual Generation**
- Auto-generate road sign images from IRC specifications
- Create road marking diagrams (arrows, zebra crossings, chevrons, etc.)
- Instant visual previews with accurate colors and dimensions

**📄 PDF Report Generation**
- Professional, multi-page PDF reports with branding
- Executive summaries and detailed specifications
- Download-ready reports for stakeholders

**📸 Image Analysis with AI**
- Upload photos of road signs/markings for instant analysis
- Automatic identification and condition assessment
- Auto-generate search queries from images
- Gemini Vision-powered recognition

**📊 Multi-Intervention Planning**
- Create comprehensive implementation plans
- Timeline generation with start/end dates
- Cost aggregation and budget tracking
- Priority-based optimization

**⚖️ Budget Optimization**
- Maximize safety impact within budget constraints
- Value/cost ratio analysis
- Smart intervention selection algorithm

**📈 Interactive Comparison**
- Compare interventions side-by-side
- Multi-factor winner analysis
- Trade-off identification

**📊 Analytics Dashboard**
- Comprehensive statistics and insights
- Category and problem distributions
- Search history analytics
- Actionable recommendations

👉 **See [WOW_FEATURES.md](docs/WOW_FEATURES.md) for detailed documentation!**

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  User Interfaces                         │
│  - Streamlit Web App (Streamlit Cloud)  │
│  - REST API (Railway)                    │
│  - CLI Tool                              │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Backend Core (FastAPI + Python)        │
│  - Query Orchestrator                    │
│  - Multi-Strategy Search                │
│    • RAG (Vector Similarity)            │
│    • Structured Queries                  │
│    • Hybrid Fusion (RRF)                │
│  - Gemini Service                        │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Data Layer                              │
│  - ChromaDB (Vector Store)              │
│  - SQLite/JSON (Structured Data)        │
│  - Cache (In-Memory TTL)                │
└─────────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Road-Safety-Intervention-Chatbot
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_gemini_api_key_here
# API_KEYS=key1,key2,key3  # Generate random keys for API access
```

### 4. Process Data and Create Databases

```bash
python backend/scripts/setup_database.py
```

This will:
- Clean and enrich the CSV data
- Generate embeddings using Gemini
- Create vector store (ChromaDB)
- Save processed data as JSON

### 5. Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 6. Start the Frontend (Optional)

```bash
cd frontend
pip install -r requirements.txt

# Copy frontend env
cp .env.example .env
# Edit and add API_URL and API_KEY

streamlit run app.py
```

Frontend will be available at: http://localhost:8501

### 7. Install CLI Tool (Optional)

```bash
cd cli
pip install -e .

# Configure CLI
road-safety config set api_url http://localhost:8000
road-safety config set api_key your_api_key_here

# Test CLI
road-safety search query "faded stop sign on highway"
```

## 📖 Usage

### Web App

1. Open http://localhost:8501
2. Enter your road safety query in natural language
3. Apply filters (optional)
4. View ranked recommendations with AI analysis

### REST API

**Local Development:**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "faded stop sign on highway",
    "max_results": 5
  }'
```

**Production (Deployed Backend):**
```bash
curl -X POST "https://road-safety-intervention-chatbot-production.up.railway.app/api/v1/search" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "faded stop sign on highway",
    "max_results": 5
  }'
```

### CLI

```bash
# Direct search
road-safety search query "damaged speed breaker"

# Interactive mode
road-safety interactive start

# With filters
road-safety search query "faded marking" \
  --category "Road Marking" \
  --speed-min 50 \
  --speed-max 100
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `API_KEYS` | Comma-separated API keys | Required |
| `ENVIRONMENT` | Environment (development/production) | development |
| `LOG_LEVEL` | Logging level | info |
| `DEFAULT_SEARCH_STRATEGY` | Default search strategy | hybrid |
| `MAX_RESULTS` | Default max results | 5 |

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Set environment variables in .env file
cp .env.example .env

# Build and run
docker-compose up --build

# Access services:
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

### Individual Containers

**Backend:**
```bash
cd backend
docker build -t road-safety-backend .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e API_KEYS=key1,key2 \
  -e ENVIRONMENT=production \
  road-safety-backend
```

**Frontend:**
```bash
cd frontend
docker build -t road-safety-frontend .
docker run -p 8501:8501 \
  -e API_URL=http://localhost:8000 \
  -e API_KEY=your_api_key \
  road-safety-frontend
```

**Note**: The backend Dockerfile uses a multi-stage build and automatically generates `interventions.json` from CSV on first startup if missing.

## 🚀 Deployment

### ✅ Backend on Railway (Deployed)

The backend is deployed and running on Railway:

**🌐 Backend URL**: `https://road-safety-intervention-chatbot-production.up.railway.app`

**Deployment Steps:**
1. Push code to GitHub
2. Create new project on [Railway](https://railway.app)
3. Connect GitHub repository
4. Set build context to root (`.`)
5. Set Dockerfile path to `backend/Dockerfile`
6. Set environment variables in Railway:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `API_KEYS` - Comma-separated API keys for authentication
   - `ENVIRONMENT=production`
7. Railway will auto-deploy on push

**Configuration Files:**
- `railway.json` - Railway deployment configuration
- `backend/Dockerfile` - Multi-stage Docker build
- `.dockerignore` - Excludes unnecessary files from build

**Key Features:**
- Auto-generates `interventions.json` from CSV on first startup
- Handles empty vector store gracefully (falls back to structured search)
- CORS enabled for frontend connections

### ✅ Frontend on Streamlit Cloud (Recommended)

**⚠️ Note**: Streamlit apps cannot run on Vercel (requires WebSocket connections). Use Streamlit Cloud instead.

**Deployment Steps:**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Configure:
   - **Repository**: `N1KH1LT0X1N/Road-Safety-Intervention-Chatbot`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
5. Click **"Deploy!"**
6. After deployment, go to **Settings** → **Secrets** and add:
   ```toml
   API_URL = "https://road-safety-intervention-chatbot-production.up.railway.app"
   API_KEY = "your-api-key-from-railway"
   ```

**Alternative: Deploy Frontend on Railway**
- Create a new Railway service
- Set root directory to `frontend/`
- Use the `frontend/Dockerfile`
- Set environment variables: `API_URL` and `API_KEY`

**See [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) for detailed deployment instructions.**

## 📊 API Endpoints

**Base URL**: `https://road-safety-intervention-chatbot-production.up.railway.app`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/stats` | GET | Database statistics |
| `/api/v1/search` | POST | Search interventions |
| `/api/v1/interventions` | GET | List interventions |
| `/api/v1/interventions/{id}` | GET | Get specific intervention |
| `/api/v1/interventions/categories/list` | GET | List categories |
| `/api/v1/interventions/problems/list` | GET | List problem types |

**API Documentation**: Visit `https://road-safety-intervention-chatbot-production.up.railway.app/docs` for interactive API docs.

**Authentication**: All API endpoints require an `X-API-Key` header with a valid API key.

## 🧪 Testing

```bash
# Run test queries
python backend/scripts/test_queries.py

# Run unit tests (if implemented)
cd backend
pytest
```

## 📁 Project Structure

```
Road-Safety-Intervention-Chatbot/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Business logic
│   │   ├── models/       # Data models
│   │   ├── services/     # Services
│   │   └── utils/        # Utilities
│   ├── data/             # Data files
│   │   ├── raw/         # Raw CSV data
│   │   ├── processed/   # Processed JSON data
│   │   └── chroma_db/   # Vector store
│   ├── scripts/          # Setup scripts
│   ├── Dockerfile        # Docker configuration
│   └── requirements.txt  # Python dependencies
├── frontend/             # Streamlit web app
│   ├── utils/            # Utilities (API client)
│   ├── app.py            # Main app
│   ├── Dockerfile        # Docker configuration
│   ├── requirements.txt  # Python dependencies
│   └── vercel.json       # Vercel config (not used - use Streamlit Cloud)
├── cli/                  # CLI tool
│   └── road_safety_cli/  # CLI package
├── docs/                 # Documentation
├── railway.json          # Railway deployment config
├── .dockerignore         # Docker ignore rules
├── DEPLOYMENT_STEPS.md   # Deployment guide
└── README.md             # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- IRC Standards for road safety data
- FastAPI, Streamlit, and Typer frameworks

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for Road Safety**
