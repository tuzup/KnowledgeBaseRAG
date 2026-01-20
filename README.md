# FastAPI + React + Material-UI Document Processing System

A full-stack application for processing PDF documents using Docling, with semantic search capabilities powered by ChromaDB and OpenAI embeddings.

## Features

### Backend (FastAPI + Celery + RabbitMQ)
- 🚀 **Async PDF Processing** with Celery background tasks
- 📄 **Docling Integration** for advanced PDF parsing
- 🔍 **Semantic Search** with ChromaDB vector database
- 📊 **Real-time Progress** tracking
- 🐰 **RabbitMQ** for both message broker and result backend (no Redis needed!)

### Frontend (React + Material-UI)
- 📤 **File Upload** interface with drag-and-drop
- 📈 **Progress Tracking** with real-time status updates
- 📋 **Chunk Viewer** to browse processed document chunks
- 🔎 **Semantic Search** with filters and pagination
- 🎨 **Modern UI** with Material-UI components
- 📱 **Responsive Design** works on all devices

## Architecture

```
┌─────────────┐      HTTP       ┌──────────────┐
│   React     │ ─────────────> │   FastAPI    │
│  Frontend   │                 │   Backend    │
└─────────────┘                 └──────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │   RabbitMQ   │
                                │ (Broker+RPC) │
                                └──────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │    Celery    │
                                │    Worker    │
                                └──────────────┘
                                       │
                          ┌────────────┴────────────┐
                          ▼                         ▼
                   ┌──────────┐            ┌──────────────┐
                   │ ChromaDB │            │    OpenAI    │
                   │  Vector  │            │   Embedding  │
                   └──────────┘            └──────────────┘
```

## Quick Start with Docker

### 1. Clone and Setup

```bash
unzip fastapi_react_docling.zip
cd fastapi_react_docling

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Flower (Celery Monitor)**: http://localhost:5555

## Local Setup (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- RabbitMQ

### Backend Setup

```bash
# Install RabbitMQ
brew install rabbitmq  # macOS
brew services start rabbitmq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads outputs data/chroma

# Configure environment
cp .env.example .env
# Edit .env with your settings (use localhost for RabbitMQ)

# Run FastAPI (Terminal 1)
uvicorn app.main:app --reload --port 8000

# Run Celery Worker (Terminal 2)
celery -A app.core.celery_app:celery_app worker --loglevel=info

# Run Flower (Terminal 3 - Optional)
celery -A app.core.celery_app:celery_app flower --port=5555
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start
```

Frontend will run on http://localhost:3000

## Usage Guide

### 1. Upload a Document

1. Go to the **Upload** page
2. Click "Choose PDF File" and select a PDF
3. Enter a **Category** (required)
4. Optionally add a **Subcategory**
5. Click "Upload and Process"
6. Watch the progress in real-time!

### 2. View Chunks

1. Navigate to the **Chunks** page
2. Use the dropdown to filter by document
3. Browse through all processed chunks
4. See metadata like page numbers, images, and tables

### 3. Search Documents

1. Go to the **Search** page
2. Enter your search query
3. Adjust number of results with the slider
4. Use filters (Images Only, Tables Only)
5. Click Search to find relevant chunks

## API Endpoints

### Upload
```http
POST /api/v1/upload/file
Content-Type: multipart/form-data

file: <PDF file>
```

### Process Document
```http
POST /api/v1/documents/process
Content-Type: application/json

{
  "pdf_path_or_url": "./uploads/document.pdf",
  "category": "Research",
  "subcategory": "ML"
}
```

### Check Task Status
```http
GET /api/v1/documents/task/{task_id}
```

### Search Documents
```http
POST /api/v1/documents/search
Content-Type: application/json

{
  "query_text": "transformer architecture",
  "n_results": 10,
  "images_only": false,
  "tables_only": false
}
```

### List Chunks
```http
GET /api/v1/documents/chunks?limit=100&offset=0&document_id=abc123
```

## Configuration

### Environment Variables

```env
# OpenAI (Required)
OPENAI_API_KEY=your_key_here

# Celery (RabbitMQ RPC Backend)
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=rpc://

# CORS (Frontend URL)
CORS_ORIGINS=http://localhost:3000

# File Upload
MAX_UPLOAD_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
```

## Why RabbitMQ RPC Backend?

This project uses **RabbitMQ for both message broker and result backend** instead of Redis:

**Benefits:**
- ✅ **Simpler Setup**: Only need RabbitMQ (no Redis)
- ✅ **One Less Service**: Reduces infrastructure complexity
- ✅ **Good Performance**: Fast enough for most use cases
- ✅ **Easy to Deploy**: Fewer moving parts

**Trade-offs:**
- ⚠️ Slightly slower than Redis for result lookups
- ⚠️ Results not persisted (cleared on RabbitMQ restart)

For production with high load, consider using Redis as the result backend.

## Project Structure

```
fastapi_react_docling/
├── app/                      # Backend (FastAPI)
│   ├── api/v1/endpoints/    # API routes
│   ├── core/                # Configuration & Celery
│   ├── services/            # Business logic
│   ├── tasks/               # Celery tasks
│   ├── schemas/             # Pydantic models
│   └── utils/               # Helper functions
├── frontend/                 # Frontend (React)
│   ├── public/              # Static files
│   └── src/
│       ├── components/      # React components
│       ├── pages/           # Page components
│       └── services/        # API client
├── uploads/                  # Uploaded PDFs
├── outputs/                  # Processed outputs
├── data/chroma/             # Vector database
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Development

### Backend Development

```bash
# Run tests
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Run tests
npm test

# Build for production
npm run build

# Lint
npm run lint
```

## Deployment

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Scaling Workers

```bash
docker-compose up -d --scale celery_worker=3
```

### Production Considerations

1. **Set strong passwords** for RabbitMQ
2. **Use HTTPS** with reverse proxy (Nginx)
3. **Add authentication** to API endpoints
4. **Set up monitoring** (Prometheus + Grafana)
5. **Configure logging** (ELK stack)
6. **Use managed services** for RabbitMQ (CloudAMQP)

## Troubleshooting

### RabbitMQ Connection Failed

```bash
# Check if RabbitMQ is running
docker-compose ps

# View logs
docker-compose logs rabbitmq

# Restart
docker-compose restart rabbitmq
```

### Frontend Can't Connect to Backend

1. Check CORS_ORIGINS in .env
2. Verify backend is running on port 8000
3. Check network connectivity in docker-compose

### Celery Tasks Not Processing

```bash
# Check worker logs
docker-compose logs celery_worker

# Check Flower dashboard
http://localhost:5555
```

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.

---

Built with ❤️ using FastAPI, React, Material-UI, Celery, RabbitMQ, and Docling
