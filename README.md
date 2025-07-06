# Trend Micro Security Q&A API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent Q&A system powered by Google Gemini AI, designed to analyze and answer questions about Trend Micro's 2025 Cyber Risk Report. This project demonstrates advanced AI engineering capabilities with RAG (Retrieval-Augmented Generation) technology, containerization, and DevOps best practices.

## Overview

This system provides automated analysis of cybersecurity intelligence through natural language processing, enabling security professionals to quickly access insights from Trend Micro's comprehensive threat reports.

## Key Features

- **AI-Powered Q&A**: Google Gemini API integration for intelligent responses
- **Security Intelligence**: Analysis of Trend Micro's 2025 Cyber Risk Report
- **RAG Technology**: Retrieval-Augmented Generation for accurate knowledge retrieval
- **Docker Ready**: Complete containerization with health checks
- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **Security Best Practices**: Environment variable management and secure configurations
- **Health Monitoring**: Built-in health checks and monitoring endpoints
- **Swagger UI**: Interactive API documentation

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Google        │    │   FAISS Vector  │
│   Backend       │◄──►│   Gemini API    │    │   Database      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docker        │    │   LangChain     │    │   HuggingFace   │
│   Container     │    │   Framework     │    │   Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

- **Backend**: FastAPI with Python 3.11+
- **AI Engine**: Google Gemini API
- **RAG Framework**: LangChain
- **Vector Database**: FAISS
- **Embeddings**: HuggingFace sentence-transformers
- **Containerization**: Docker & Docker Compose
- **Documentation**: Swagger UI / OpenAPI

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- Google Gemini API Key

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/trend-micro-security-qa-api.git
cd trend-micro-security-qa-api
```

### 2. Environment Setup

```bash
# Copy environment variables template
cp env.example .env

# Edit .env file with your Google API Key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Local Development

```bash
# Create virtual environment
python -m venv aiops
source aiops/bin/activate  # On Windows: aiops\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
python app.py
```

### 4. Docker Deployment (Recommended)

```bash
# Build and start with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
```

### 5. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/info
- **Example Questions**: http://localhost:8000/examples

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint - API information |
| `/health` | GET | Health check and system status |
| `/info` | GET | Detailed API information |
| `/examples` | GET | List of example questions |
| `/ask` | POST | AI-powered Q&A endpoint |
| `/docs` | GET | Interactive API documentation |

### Example API Usage

```bash
# Ask a question
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the Cyber Risk Index (CRI)?"}'

# Health check
curl http://localhost:8000/health

# Get example questions
curl http://localhost:8000/examples
```

## Project Structure

```
trend-micro-security-qa-api/
├── app.py                  # FastAPI application
├── main.py                 # Core AI logic
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── PROJECT_STATUS.md     # Project status documentation
├── docker.md             # Docker deployment guide
├── knowledgebase.txt     # Trend Micro security report data
├── summary.txt           # Knowledge base summary
├── start_api.bat         # Windows startup script
├── tests/                # Test files
│   ├── test_gemini_only.py
│   └── test_summary.py
├── examples/             # Example files
│   └── test_log.py
└── python_config/        # Python environment config
    ├── python.bat
    ├── pip.bat
    └── setup_python.bat
```

## Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Gemini Model Settings
GEMINI_MODEL=gemini-2.0-flash-lite
GEMINI_TEMPERATURE=0.1
GEMINI_MAX_TOKENS=200

# API Service Settings
API_HOST=0.0.0.0
API_PORT=8000
API_TITLE=Trend Micro Security Q&A API
API_DESCRIPTION=AI-powered security intelligence system
API_VERSION=1.0.0

# Knowledge Base Settings
KNOWLEDGE_FILE=summary.txt

# Logging
LOG_LEVEL=INFO
```

### Model Configuration Details

The system uses the following AI model configuration:

- **Model**: `gemini-2.0-flash-lite` - Google's latest Gemini Flash model for fast, efficient responses (configurable via `GEMINI_MODEL`)
- **Temperature**: `0.1` - Low temperature for consistent, factual responses (configurable via `GEMINI_TEMPERATURE`)
- **Max Tokens**: `200` - Optimized response length for concise answers (configurable via `GEMINI_MAX_TOKENS`)
- **Embeddings**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` - Multilingual embedding model for Chinese text processing
- **Vector Database**: FAISS with 3 nearest neighbors retrieval
- **Text Chunking**: 1000 characters with 200 character overlap for optimal context

**Note**: All model parameters are now configurable via environment variables for maximum flexibility.

### Docker Configuration

The project includes:
- **Dockerfile**: Multi-stage build with security best practices
- **docker-compose.yml**: Complete service orchestration
- **Health checks**: Automatic service monitoring
- **Volume mounts**: Knowledge base file persistence

## Testing

### Run Tests

```bash
# Basic functionality test
python tests/test_gemini_only.py

# Knowledge base test
python tests/test_summary.py
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test Q&A endpoint
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the main cybersecurity trends in 2025?"}'
```

## Project Status

- ✅ **Core AI Logic**: Google Gemini integration with RAG
- ✅ **API Development**: FastAPI backend with comprehensive endpoints
- ✅ **Containerization**: Docker support with health checks
- ✅ **Documentation**: Complete API documentation and guides
- ✅ **Security**: Environment variable management and best practices
- ✅ **Testing**: Comprehensive test suite
- 🔄 **CI/CD**: GitHub Actions workflow (planned)
- 🔄 **Cloud Deployment**: Azure container deployment (planned)

For detailed progress, see [PROJECT_STATUS.md](PROJECT_STATUS.md)

## Docker Deployment

### Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Features

- **Multi-stage build**: Optimized image size
- **Non-root user**: Security best practices
- **Health checks**: Automatic service monitoring
- **Volume mounts**: Persistent knowledge base
- **Environment variables**: Flexible configuration

For detailed Docker documentation, see [docker.md](docker.md)

## Security Considerations

- **API Key Management**: Environment variables for sensitive data
- **Container Security**: Non-root user execution
- **Input Validation**: Request validation and sanitization
- **Error Handling**: Secure error messages
- **Health Monitoring**: Built-in security checks

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Trend Micro**: For providing the cybersecurity report data
- **Google**: For the Gemini AI API
- **FastAPI**: For the excellent web framework
- **LangChain**: For the RAG framework
- **Docker**: For containerization technology

## Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-username/trend-micro-security-qa-api/issues)
- **Project Status**: [PROJECT_STATUS.md](PROJECT_STATUS.md)

---

**Built for Trend Micro Security Intelligence**

*Last updated: 2025-07-06*
*Version: 1.0.0*