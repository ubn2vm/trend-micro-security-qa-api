# Trend Micro Internal Knowledge Q&A Bot - Quick Start Guide

> **Important Note**: This guide provides detailed deployment steps and troubleshooting. For project overview, please read the [README.md](../README.md) in the root directory first.

## Overview

This guide provides three different deployment methods:
1. **Windows One-Click Deployment**
2. **Manual Python Virtual Environment Setup**
3. **Docker Container Deployment**

## Quick Start - Windows One-Click Deployment

### Prerequisites
- Windows 10/11
- Python 3.8+ installed
- Internet connection (for API keys and dependencies)

### Step 1: Get Google API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key (starts with 'AI')

### Step 2: One-Click Launch
```bash
# Execute the main startup script
presentation/scripts/start_simple.bat
```

**Automatically executed operations:**
- Python environment detection
- Virtual environment creation (`aiops/`)
- Dependency installation from `core_app/requirements.txt`
- Environment configuration setup
- API key validation
- Knowledge base initialization
- Port availability check
- API server startup

### Step 3: Verify Deployment
After successful startup, you will see:
```
===========================================
Starting Trend Micro Internal Knowledge Q&A Bot
===========================================

[DOCS] API Documentation: http://localhost:8000/docs
[HEALTH] Health Check: http://localhost:8000/health
[EXAMPLES] Sample Questions: http://localhost:8000/examples
[ROOT] Root Path: http://localhost:8000/

Press Ctrl+C to stop the server
```

### Step 4: Test API
Visit in your browser:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Sample Questions**: http://localhost:8000/examples

## Manual Setup (Alternative Method)

### Step 1: Environment Setup
```bash
# Run environment setup script
Dev/dev_scripts/setup_env.bat
```

This script will:
- Create `.env` file from `config/env.example`
- Open Notepad for API key configuration
- Guide you through Google API key setup

### Step 2: Configure API Key
Edit the `.env` file:
```env
# Google API Key - Replace with your actual API key
# Get from https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_actual_api_key_here

# Other settings are automatically loaded from config.env
# To override, set them here:
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

# Start API server
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

# Edit .env file to add your API key
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

## API Endpoint Reference

| Endpoint | Purpose | URL | Method |
|----------|---------|-----|--------|
| API Documentation | Swagger UI | http://localhost:8000/docs | GET |
| Health Check | System Status | http://localhost:8000/health | GET |
| API Information | Detailed Info | http://localhost:8000/info | GET |
| Sample Questions | Test Questions | http://localhost:8000/examples | GET |
| Ask Question | Q&A Service | http://localhost:8000/ask | POST |

## Testing and Validation

### Quick Test Scripts
```bash
# Automated comprehensive testing
tests\scripts\quick_test.bat

# Project validation
tests\scripts\validate_project.bat

# Security testing
python tests\security\test_security.py
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Ask question
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Cyber Risk Index (CRI)?"}'
```


## Troubleshooting

### Connection Refused
**Symptoms**: Browser shows "Unable to connect to this site"
**Cause**: API service not started
**Solution**:
1. Check if command line shows `(aiops)` virtual environment
2. Look for error messages
3. Re-run `python core_app\app.py`

### Module Not Found Error
**Symptoms**: "No module named 'xxx'" error
**Cause**: Missing dependencies
**Solution**:
```bash
# Reinstall dependencies
pip install -r core_app\requirements.txt
```

### API Key Validation Failed
**Symptoms**: API key error during startup
**Cause**: Invalid or missing API key
**Solution**:
1. Check if `.env` file exists
2. Verify `GOOGLE_API_KEY` format (starts with 'AI', minimum 20 characters)
3. If needed, re-run `Dev/dev_scripts/setup_env.bat`

### Port Already in Use
**Symptoms**: Port 8000 is already in use
**Cause**: Other service using port 8000
**Solution**:
1. Change port in `config/config.env`: `API_PORT=8001`
2. Or close other applications using port 8000

### Docker Issues
**Symptoms**: Docker container startup failed
**Cause**: Configuration or resource issues
**Solution**:
```bash
# Check Docker logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.8+
- **Memory**: 4GB
- **Storage**: 2GB available space
- **Network**: Internet connection for API calls

### Recommended Requirements
- **Operating System**: Windows 11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.11+
- **Memory**: 8GB
- **Storage**: 5GB available space
- **Network**: Stable internet connection

## Updates Aligned with Root README.md

### Deployment Script Paths
- Updated to `presentation/scripts/start_simple.bat` (consistent with root directory)
- Retained reference to `Dev/dev_scripts/setup_env.bat` (for manual setup)

### Technical Specifications
- Maintained consistency with technology stack descriptions in root README.md
- Updated Python version requirement to 3.11+
- Kept same API endpoint descriptions

### Security Notes
- Emphasized that `/ask` endpoint currently has no authentication (demo version)
- Reminded that this is a demo/development version, not suitable for production deployment
- Maintained consistency with security warnings in root README.md 