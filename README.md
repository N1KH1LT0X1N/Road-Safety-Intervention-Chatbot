# 🚦 Road Safety Intervention AI

An AI-powered system for recommending road safety interventions based on IRC standards, using Google Gemini API and hybrid RAG search.

## 🌟 Features

- **Multi-Interface Support**: Web App (Streamlit), REST API (FastAPI), and CLI Tool
- **Hybrid Search**: Combines RAG (vector similarity) and structured queries
- **AI-Powered**: Google Gemini for embeddings, entity extraction, and synthesis
- **Comprehensive Database**: 105+ road safety interventions from IRC standards
- **Smart Recommendations**: Confidence scoring, detailed specifications, and IRC citations

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  User Interfaces                         │
│  - Streamlit Web App (Vercel)           │
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

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
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

```bash
# Backend
cd backend
docker build -t road-safety-backend .
docker run -p 8000:8000 --env-file ../.env road-safety-backend

# Frontend
cd frontend
docker build -t road-safety-frontend .
docker run -p 8501:8501 --env-file .env road-safety-frontend
```

## 🚀 Deployment

### Backend on Railway

1. Push code to GitHub
2. Create new project on [Railway](https://railway.app)
3. Connect GitHub repository
4. Set environment variables:
   - `GEMINI_API_KEY`
   - `API_KEYS`
   - `ENVIRONMENT=production`
5. Deploy from `backend` directory
6. Railway will auto-deploy on push

### Frontend on Vercel

1. Push code to GitHub
2. Import project on [Vercel](https://vercel.com)
3. Set root directory to `frontend`
4. Add environment variables:
   - `API_URL=https://your-railway-app.railway.app`
   - `API_KEY=your_api_key`
5. Deploy

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/stats` | GET | Database statistics |
| `/api/v1/search` | POST | Search interventions |
| `/api/v1/interventions` | GET | List interventions |
| `/api/v1/interventions/{id}` | GET | Get specific intervention |
| `/api/v1/interventions/categories/list` | GET | List categories |
| `/api/v1/interventions/problems/list` | GET | List problem types |

See full API documentation at `/docs` endpoint.

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
│   └── scripts/          # Setup scripts
├── frontend/             # Streamlit web app
│   ├── components/       # UI components
│   ├── utils/            # Utilities
│   └── app.py            # Main app
├── cli/                  # CLI tool
│   └── road_safety_cli/  # CLI package
├── docs/                 # Documentation
├── docker/               # Docker configs
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
