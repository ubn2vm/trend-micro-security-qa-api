# Quick Start Guide - Trend Micro Security QA API

## Overview

This guide provides step-by-step instructions for deploying the Trend Micro Security QA API using three different methods:
1. **One-Click Windows Deployment** (Recommended for interviews)
2. **Manual Python Virtual Environment Setup**
3. **Docker Container Deployment**

## Quick Start - One-Click Deployment (Windows)

### Prerequisites
- Windows 10/11
- Python 3.8+ installed
- Internet connection for API key and dependencies

### Step 1: Get Google API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key (starts with 'AI')

### Step 2: One-Click Launch
```bash
# Execute the main startup script
start.bat
```

**What happens automatically:**
- Python environment detection
- Virtual environment creation (`aiops/`)
- Dependency installation from `core_app/requirements.txt`
- Environment configuration setup
- API key validation
- Knowledge base initialization
- Port availability check
- API server startup

### Step 3: Verify Deployment
After successful startup, you'll see:
```
===========================================
Starting Trend Micro Security QA API
===========================================

[DOCS] API Documentation: http://localhost:8000/docs
[HEALTH] Health Check: http://localhost:8000/health
[EXAMPLES] Example Questions: http://localhost:8000/examples
[ROOT] Root Path: http://localhost:8000/

Press Ctrl+C to stop the server
```

### Step 4: Test the API
Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Example Questions**: http://localhost:8000/examples

## Manual Setup (Alternative Method)

### Step 1: Environment Setup
```bash
# Run environment setup script
setup_env.bat
```

This script will:
- Create `.env` file from `config/env.example`
- Open Notepad for API key configuration
- Guide you through Google API key setup

### Step 2: Configure API Key
Edit the `.env` file:
```env
# Google API Key - Replace with your actual API Key
# Get from https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_actual_api_key_here

# Other settings are loaded from config.env automatically
# Override here if needed:
# GEMINI_MODEL=gemini-2.0-flash-lite
# GEMINI_TEMPERATURE=0.1
# GEMINI_MAX_TOKENS=200
```

### Step 3: Manual Virtual Environment Setup
```bash
# Create virtual environment
python -m venv aiops

# Activate virtual environment
call aiops\Scripts\activate.bat

# Install dependencies
pip install -r core_app\requirements.txt
```

### Step 4: Start API Server
```bash
# Ensure virtual environment is activated
call aiops\Scripts\activate.bat

# Start the API server
python core_app\app.py
```

## Docker Deployment

### Prerequisites
- Docker Desktop installed
- Docker Compose available

### Step 1: Configure Environment
```bash
# Copy environment template
copy config\env.example .env

# Edit .env file with your API key
notepad .env
```

### Step 2: Docker Compose Deployment
```bash
# Start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 3: Verify Docker Deployment
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Container Status**: `docker-compose ps`

## API Endpoints Reference

| Endpoint | Purpose | URL | Method |
|----------|---------|-----|--------|
| API Documentation | Swagger UI | http://localhost:8000/docs | GET |
| Health Check | System Status | http://localhost:8000/health | GET |
| API Information | Detailed Info | http://localhost:8000/info | GET |
| Example Questions | Test Questions | http://localhost:8000/examples | GET |
| Ask Question | Q&A Service | http://localhost:8000/ask | POST |

## Testing & Validation

### Quick Test Scripts
```bash
# Automated comprehensive testing
testing_tools\quick_test.bat

# Project validation
testing_tools\validate_project.bat

# Security testing
python testing_tools\test_security.py
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Cyber Risk Index (CRI)?"}'
```

### Comprehensive Testing
```bash
# Run all test suites
python tests/test_comprehensive.py
python tests/test_summary.py
python tests/test_gemini_only.py
```

## Troubleshooting

### Connection Refused
**Symptom**: Browser shows "Cannot connect to this website"
**Cause**: API service not started
**Solution**:
1. Check command line for `(aiops)` virtual environment
2. Look for error messages
3. Re-run `python core_app\app.py`

### ModuleNotFoundError
**Symptom**: "No module named 'xxx'" error
**Cause**: Missing dependencies
**Solution**:
```bash
# Reinstall dependencies
pip install -r core_app\requirements.txt
```

### API Key Validation Failed
**Symptom**: API key error during startup
**Cause**: Invalid or missing API key
**Solution**:
1. Check `.env` file exists
2. Verify `GOOGLE_API_KEY` format (starts with 'AI', min 20 chars)
3. Re-run `setup_env.bat` if needed

### Port Already in Use
**Symptom**: Port 8000 already in use
**Cause**: Another service using port 8000
**Solution**:
1. Change port in `config/config.env`: `API_PORT=8001`
2. Or close other applications using port 8000

### Docker Issues
**Symptom**: Docker container fails to start
**Cause**: Configuration or resource issues
**Solution**:
```bash
# Check Docker logs
docker-compose logs

# Rebuild container
docker-compose down
docker-compose up --build -d
```

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8+
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Network**: Internet connection for API calls

### Recommended Requirements
- **OS**: Windows 11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.11+
- **RAM**: 8GB
- **Storage**: 5GB free space
- **Network**: Stable internet connection

## Security Considerations

### API Key Security
- Never commit `.env` file to version control
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage

### Network Security
- Use HTTPS in production
- Implement rate limiting
- Configure CORS properly
- Monitor access logs

---

**Compatibility**: Python 3.8+, Docker 20.10+ 