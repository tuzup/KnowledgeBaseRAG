# FastAPI + React + Celery + RabbitMQ - Local Setup Guide (Without Docker)

Complete step-by-step guide to run your PDF processing application locally without Docker.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Architecture Overview](#architecture-overview)
3. [Install Prerequisites](#install-prerequisites)
4. [Backend Setup (FastAPI + Celery)](#backend-setup)
5. [Frontend Setup (React)](#frontend-setup)
6. [Running the Application](#running-the-application)
7. [Testing the System](#testing-the-system)
8. [Troubleshooting](#troubleshooting)
9. [Stopping Services](#stopping-services)

---

## System Requirements

- **Operating System**: macOS, Linux (Ubuntu/Debian), or Windows 10/11
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 5GB free

---

## Architecture Overview

```
┌─────────────┐      HTTP      ┌──────────────┐
│   React     │ ─────────────> │   FastAPI    │
│  (Port 3000)│                 │  (Port 8000) │
└─────────────┘                 └──────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │   RabbitMQ   │
                                │  (Port 5672) │
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

**Components:**
1. **React Frontend** - User interface for uploading PDFs and searching
2. **FastAPI Backend** - REST API server handling requests
3. **RabbitMQ** - Message broker for task queuing (also serves as result backend via RPC)
4. **Celery Worker** - Background worker processing PDF documents
5. **ChromaDB** - Vector database for semantic search
6. **OpenAI API** - Generates embeddings for semantic search

---

## Install Prerequisites

### 1. Install Python 3.11+

#### macOS:
```bash
# Using Homebrew
brew install python@3.11
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

#### Windows:
1. Download Python 3.11 from https://www.python.org/downloads/
2. Run installer and check "Add Python to PATH"

**Verify installation:**
```bash
python3 --version
# Should show: Python 3.11.x
```

---

### 2. Install Node.js 18+

#### macOS:
```bash
brew install node@18
```

#### Ubuntu/Debian:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Windows:
1. Download from https://nodejs.org/
2. Run the installer

**Verify installation:**
```bash
node --version
# Should show: v18.x.x

npm --version
# Should show: 9.x.x or higher
```

---

### 3. Install RabbitMQ

#### macOS:
```bash
# Install RabbitMQ
brew install rabbitmq

# Start RabbitMQ service
brew services start rabbitmq

# Verify it's running
brew services list | grep rabbitmq
```

#### Ubuntu/Debian:
```bash
# Install RabbitMQ
sudo apt-get update
sudo apt-get install -y rabbitmq-server

# Start RabbitMQ
sudo systemctl start rabbitmq-server

# Enable auto-start on boot
sudo systemctl enable rabbitmq-server

# Check status
sudo systemctl status rabbitmq-server
```

#### Windows:
1. Install **Erlang** first (required dependency):
   - Download from: https://www.erlang.org/downloads
   - Install with default settings

2. Install **RabbitMQ**:
   - Download from: https://www.rabbitmq.com/download.html
   - Run installer
   - Start from Windows Services or run: `rabbitmq-server start`

**Verify RabbitMQ is running:**
```bash
# Test connection (should show login page HTML)
curl http://localhost:15672

# Or open in browser:
# http://localhost:15672
# Default credentials: guest / guest
```

---

## Backend Setup

### Step 1: Extract Project Files

```bash
# Unzip the project
unzip fastapi_react_docling.zip

# Navigate to project directory
cd fastapi_react_docling
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**If you encounter dependency conflicts, use this updated `requirements.txt`:**

```text
# FastAPI and related
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
pydantic-settings>=2.3.0,<3.0.0
python-multipart==0.0.6
aiofiles==23.2.1

# Celery and message broker
celery==5.3.6
flower==2.0.1

# Docling and document processing
numpy==1.26.4
docling==1.16.2
docling-core==1.8.1
tiktoken==0.5.2

# Vector database
chromadb==0.4.22

# OpenAI
openai==1.10.0

# Other utilities
python-dotenv==1.0.0
httpx==0.26.0
Pillow==10.2.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Update `.env` with these settings for local deployment:**

```env
# OpenAI Configuration (REQUIRED - get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Celery Configuration - LOCAL (RabbitMQ RPC backend)
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://

# RabbitMQ Configuration - LOCAL
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# ChromaDB Configuration
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=document_collection

# FastAPI Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=FastAPI Docling Service
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS - Allow frontend access
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Document Processing Configuration
MAX_TOKENS=8191
CHUNKING_MAX_TOKENS=8191
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
IMAGES_SCALE=2.0
PICTURE_DESCRIPTION_TIMEOUT=60
MAX_UPLOAD_SIZE=52428800

# Celery Worker Configuration
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3000
```

### Step 5: Create Required Directories

```bash
# Create directories for uploads, outputs, and database
mkdir -p uploads
mkdir -p outputs
mkdir -p data/chroma
```

### Step 6: Verify Backend Setup

```bash
# Test imports
python -c "from app.main import app; print('✓ Backend imports successful')"

# If you see the success message, you're ready to proceed
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Node.js Dependencies

```bash
# Install all npm packages
npm install

# This will take a few minutes
```

### Step 3: Configure Frontend Environment

```bash
# Create local environment file
cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
```

**On Windows, create `.env.local` manually with this content:**
```
REACT_APP_API_URL=http://localhost:8000
```

### Step 4: Verify Frontend Setup

```bash
# Build test (optional, to verify everything compiles)
npm run build

# Should complete without errors
```

---

## Running the Application

You need to run **4 separate processes** in different terminal windows/tabs.

### Terminal 1: FastAPI Backend

```bash
# Navigate to project root
cd /path/to/fastapi_react_docling

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Starting FastAPI Docling Service
INFO:     Application startup complete.
```

**Keep this terminal running.**

---

### Terminal 2: Celery Worker

**Important:** Make sure to include `-Q pdf_processing` flag!

```bash
# Open new terminal
cd /path/to/fastapi_react_docling

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Start Celery worker (MUST include -Q pdf_processing)
celery -A app.core.celery_app:celery_app worker --loglevel=info --concurrency=4 -Q pdf_processing --pool=solo
```

**Expected output:**
```
-------------- celery@yourhostname v5.3.6 (emerald-rush)
--- ***** ----- 
-- ******* ---- Linux-x.x.x 2025-10-25 10:00:00
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         document_processor:0x...
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     rpc://
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF
--- ***** ----- 
 -------------- [queues]
                .> pdf_processing   exchange=pdf_processing(direct) key=pdf_processing
                

[tasks]
  . app.tasks.document_tasks.process_pdf_task

[2025-10-25 10:00:00,000: INFO/MainProcess] Connected to amqp://guest:**@localhost:5672//
[2025-10-25 10:00:00,000: INFO/MainProcess] celery@yourhostname ready.
```

**Keep this terminal running.**

---

### Terminal 3: Flower (Optional - for monitoring)

```bash
# Open new terminal
cd /path/to/fastapi_react_docling

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Start Flower dashboard
celery -A app.core.celery_app:celery_app flower --port=5555
```

**Expected output:**
```
[I 2025-10-25 10:00:00,000 command: Starting Flower on port 5555
[I 2025-10-25 10:00:00,000 command: Broker: amqp://guest:**@localhost:5672//
[I 2025-10-25 10:00:00,000 command: Registered tasks: ...
[I 2025-10-25 10:00:00,000 command: Flower dashboard running at: http://localhost:5555
```

**Keep this terminal running.**

---

### Terminal 4: React Frontend

```bash
# Open new terminal
cd /path/to/fastapi_react_docling/frontend

# Start React development server
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view docling-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

**Keep this terminal running.**

The browser should automatically open to http://localhost:3000

---

## Service URLs

Once everything is running, you can access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **React Frontend** | http://localhost:3000 | - |
| **FastAPI Backend** | http://localhost:8000 | - |
| **API Documentation** | http://localhost:8000/docs | - |
| **RabbitMQ Management** | http://localhost:15672 | guest / guest |
| **Flower Dashboard** | http://localhost:5555 | - |

---

## Testing the System

### 1. Access the Frontend

Open http://localhost:3000 in your browser.

### 2. Upload a PDF

1. Click "CHOOSE PDF FILE"
2. Select a PDF document
3. Enter a **Category** (required) - e.g., "Research Papers"
4. Enter a **Subcategory** (optional) - e.g., "Machine Learning"
5. Click "UPLOAD AND PROCESS"

### 3. Monitor Progress

- Watch the **Processing Status** panel on the right
- Status will change: PENDING → STARTED → SUCCESS
- You'll see progress stages: initializing → processing_pdf → storing_embeddings → completed
- Once complete, you'll see the number of chunks processed and document ID

### 4. View Chunks

1. Click **"Chunks"** in the navigation menu
2. Use the dropdown to filter by document
3. Browse through processed chunks
4. View metadata (page numbers, images, tables)

### 5. Search Documents

1. Click **"Search"** in the navigation menu
2. Enter a search query (e.g., "transformer architecture")
3. Adjust number of results with the slider
4. Apply filters if needed (Images Only, Tables Only)
5. Click **"Search"**
6. View semantically similar results

---

## Troubleshooting

### Problem: RabbitMQ Not Running

**Symptoms:**
- Celery worker fails to connect
- Error: `[Errno 61] Connection refused`

**Solution:**

```bash
# Check if RabbitMQ is running
# macOS:
brew services list | grep rabbitmq

# Linux:
sudo systemctl status rabbitmq-server

# Restart if needed
# macOS:
brew services restart rabbitmq

# Linux:
sudo systemctl restart rabbitmq-server

# Windows:
# Go to Services → RabbitMQ → Restart
```

---

### Problem: Tasks Stuck at PENDING

**Symptoms:**
- Upload succeeds but status never changes from PENDING
- Celery worker is online but not processing

**Solution:**

1. **Check worker is listening to correct queue:**
   ```bash
   # Your celery command MUST include -Q pdf_processing
   celery -A app.core.celery_app:celery_app worker --loglevel=info -Q pdf_processing
   ```

2. **Verify task registration:**
   ```bash
   celery -A app.core.celery_app:celery_app inspect registered
   # Should show: app.tasks.document_tasks.process_pdf_task
   ```

3. **Check RabbitMQ queues:**
   - Open http://localhost:15672
   - Go to "Queues" tab
   - You should see `pdf_processing` queue with messages being consumed

4. **Restart Celery worker** with correct queue flag

---

### Problem: Import Errors in Python

**Symptoms:**
- `ModuleNotFoundError: No module named 'app'`
- `ImportError: cannot import name ...`

**Solution:**

```bash
# Make sure you're in the project root directory
pwd
# Should show: /path/to/fastapi_react_docling

# Make sure virtual environment is activated
which python
# Should show: /path/to/fastapi_react_docling/venv/bin/python

# If not activated:
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Problem: Port Already in Use

**Symptoms:**
- `Error: Address already in use`
- Can't start FastAPI or React

**Solution:**

```bash
# Find process using port 8000 (FastAPI)
# macOS/Linux:
lsof -ti:8000
# Kill it:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID <PID> /F

# Same for port 3000 (React)
lsof -ti:3000 | xargs kill -9  # macOS/Linux
```

---

### Problem: Numpy/ChromaDB Compatibility Error

**Symptoms:**
- `AttributeError: np.float_ was removed in NumPy 2.0`
- Celery worker crashes on startup

**Solution:**

```bash
# Ensure numpy 1.26.4 is installed
pip install numpy==1.26.4 --force-reinstall

# Verify version
python -c "import numpy; print(numpy.__version__)"
# Should show: 1.26.4
```

---

### Problem: Frontend Can't Connect to Backend

**Symptoms:**
- CORS errors in browser console
- Network errors when uploading

**Solution:**

1. **Check `.env` CORS settings:**
   ```env
   CORS_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

2. **Verify FastAPI is running on port 8000:**
   ```bash
   curl http://localhost:8000/api/v1/health
   # Should return: {"status":"healthy",...}
   ```

3. **Check React `.env.local`:**
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. **Restart both frontend and backend**

---

### Problem: OpenAI API Errors

**Symptoms:**
- Task fails during embedding generation
- Error about API key or rate limits

**Solution:**

1. **Verify API key in `.env`:**
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Test API key:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **Check OpenAI account:**
   - Go to https://platform.openai.com/account/billing
   - Ensure you have credits
   - Check usage limits

---

### Problem: ChromaDB Permission Errors

**Symptoms:**
- Error creating/accessing `./data/chroma`
- Permission denied errors

**Solution:**

```bash
# Ensure directories exist with proper permissions
mkdir -p data/chroma uploads outputs
chmod -R 755 data uploads outputs

# On Windows, make sure you have write permissions to the project folder
```

---

## Stopping Services

### Option 1: Stop Each Service Individually

In each terminal window, press:
```
Ctrl + C
```

### Option 2: Stop All Services Script

Create `stop.sh`:

```bash
#!/bin/bash

echo "Stopping all services..."

# Stop FastAPI
pkill -f "uvicorn app.main:app"

# Stop Celery worker
pkill -f "celery.*worker"

# Stop Flower
pkill -f "celery.*flower"

# Stop React dev server
pkill -f "react-scripts"

# Optionally stop RabbitMQ
# brew services stop rabbitmq  # macOS
# sudo systemctl stop rabbitmq-server  # Linux

echo "All services stopped."
```

Make it executable and run:
```bash
chmod +x stop.sh
./stop.sh
```

### Option 3: Keep RabbitMQ Running

RabbitMQ can stay running in the background. Only stop it if you need to:

```bash
# macOS:
brew services stop rabbitmq

# Linux:
sudo systemctl stop rabbitmq-server

# Windows:
# Services → RabbitMQ → Stop
```

---

## Development Workflow

### Making Code Changes

#### Backend Changes:
- Edit files in `app/` directory
- FastAPI auto-reloads (if running with `--reload`)
- **Celery worker does NOT auto-reload** - you must restart it manually:
  ```bash
  # In Celery terminal: Ctrl+C, then restart
  celery -A app.core.celery_app:celery_app worker --loglevel=info -Q pdf_processing
  ```

#### Frontend Changes:
- Edit files in `frontend/src/`
- React dev server auto-reloads
- Changes appear immediately in browser

---

## Production Deployment Tips

When moving to production, consider:

1. **Use a process manager:**
   - For Python: Supervisor or systemd
   - For React: Build and serve with Nginx

2. **Secure RabbitMQ:**
   - Change default credentials
   - Enable SSL/TLS
   - Restrict network access

3. **Use environment-specific configs:**
   - Separate `.env.production` file
   - Disable DEBUG mode
   - Use proper CORS origins

4. **Set up monitoring:**
   - Use Flower or Prometheus
   - Set up log aggregation
   - Configure alerts

5. **Scale workers:**
   ```bash
   # Run multiple workers
   celery -A app.core.celery_app:celery_app worker -Q pdf_processing &
   celery -A app.core.celery_app:celery_app worker -Q pdf_processing &
   ```

---

## Quick Reference Commands

### Start All Services (copy-paste friendly)

```bash
# Terminal 1 - Backend
cd /path/to/fastapi_react_docling && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Celery Worker
cd /path/to/fastapi_react_docling && source venv/bin/activate && celery -A app.core.celery_app:celery_app worker --loglevel=info -Q pdf_processing

# Terminal 3 - Flower (optional)
cd /path/to/fastapi_react_docling && source venv/bin/activate && celery -A app.core.celery_app:celery_app flower --port=5555

# Terminal 4 - Frontend
cd /path/to/fastapi_react_docling/frontend && npm start
```

### Check Service Status

```bash
# Check if ports are in use
lsof -i :8000  # FastAPI
lsof -i :3000  # React
lsof -i :5672  # RabbitMQ
lsof -i :5555  # Flower

# Check if processes are running
ps aux | grep uvicorn
ps aux | grep celery
ps aux | grep react-scripts
```

---

## Support

If you encounter issues not covered in this guide:

1. **Check logs** - All terminals show detailed error messages
2. **Verify all services are running** - Use the status checks above
3. **Test individually** - Isolate which component is failing
4. **Check system resources** - Ensure you have enough RAM/CPU
5. **Review environment variables** - Double-check `.env` file

---

## Summary Checklist

Before running the application, ensure:

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] RabbitMQ installed and running
- [ ] Virtual environment created and activated
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with OpenAI API key
- [ ] Required directories created (`uploads`, `outputs`, `data/chroma`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend `.env.local` configured

To run:

- [ ] Terminal 1: FastAPI backend running
- [ ] Terminal 2: Celery worker running with `-Q pdf_processing`
- [ ] Terminal 3: Flower running (optional)
- [ ] Terminal 4: React frontend running

Access at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Flower: http://localhost:5555

---

**You're all set! Start uploading and processing PDFs!**
