# 🔒 Trend Micro Security Intelligence API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Secure-blue.svg)](https://www.docker.com/)
[![Security](https://img.shields.io/badge/Security-Hardened-red.svg)](https://owasp.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Enterprise-grade AI-powered cybersecurity intelligence platform**  
> Leveraging Google Gemini AI and RAG technology to provide real-time analysis of Trend Micro's 2025 Cyber Risk Report for security professionals and threat intelligence teams.

## 🎯 Mission Statement

This platform transforms raw cybersecurity intelligence into actionable insights through advanced natural language processing, enabling security teams to rapidly assess threats, understand attack vectors, and make informed security decisions based on comprehensive threat intelligence data.

## 🛡️ Security-First Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Google        │    │   FAISS Vector  │
│   Security      │◄──►│   Gemini API    │    │   Database      │
│   Gateway       │    │   (Encrypted)   │    │   (Encrypted)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docker        │    │   LangChain     │    │   HuggingFace   │
│   Container     │    │   Framework     │    │   Embeddings    │
│   (Hardened)    │    │   (Secure)      │    │   (Local)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔥 Core Capabilities

### **Threat Intelligence Analysis**
- **Real-time Threat Assessment**: AI-powered analysis of emerging cyber threats
- **Risk Scoring**: Automated calculation of Cyber Risk Index (CRI) metrics
- **Attack Vector Mapping**: Identification and classification of attack patterns
- **Vulnerability Correlation**: Cross-reference threats with known vulnerabilities

### **Security Intelligence Features**
- **RAG-Powered Q&A**: Retrieval-Augmented Generation for accurate threat intelligence
- **Multi-language Support**: Native Chinese and English threat analysis
- **Contextual Understanding**: Deep comprehension of security terminology and concepts
- **Evidence-based Responses**: Citations and references to source intelligence

### **Enterprise Security**
- **Containerized Deployment**: Secure, isolated execution environment
- **Health Monitoring**: Comprehensive system health and security checks
- **API Security**: Input validation, rate limiting, and secure error handling
- **Audit Logging**: Complete request/response logging for compliance

## 🏗️ Technology Stack

| Component | Technology | Security Features |
|-----------|------------|-------------------|
| **Backend Framework** | FastAPI 0.104+ | Input validation, CORS, rate limiting |
| **AI Engine** | Google Gemini 2.0 Flash | Encrypted API communication |
| **RAG Framework** | LangChain | Secure knowledge retrieval |
| **Vector Database** | FAISS | Local, encrypted storage |
| **Embeddings** | HuggingFace sentence-transformers | Local processing, no external calls |
| **Containerization** | Docker & Docker Compose | Non-root execution, security scanning |
| **Documentation** | Swagger UI / OpenAPI | Interactive API exploration |

## 🚀 Secure Deployment

### **Prerequisites**

- Python 3.11+ (LTS version recommended)
- Docker Engine 20.10+ (for containerized deployment)
- Google Gemini API Key (with appropriate security permissions)
- Minimum 4GB RAM, 2 CPU cores

### **1. Secure Repository Setup**

```bash
# Clone with security verification
git clone https://github.com/ubn2vm/trend-micro-security-qa-api.git
cd trend-micro-security-qa-api

# Verify repository integrity
git log --oneline -5
```

### **2. Environment Security Configuration**

**Option A: Automatic Setup (Recommended)**
```bash
# Run the setup script
setup_env.bat

# Or run start.bat directly (it will auto-create .env)
start.bat
```

**Option B: Manual Setup**
```bash
# Create secure environment file from template
copy env.example .env

# Configure with your secure API credentials
# IMPORTANT: Never commit .env files to version control
notepad .env
```

**Required Environment Variables:**
```env
# Google API Configuration (Secure)
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_secure_api_key_here

# Other settings are loaded from config.env automatically
# You can override them in .env if needed:
# GEMINI_MODEL=gemini-2.0-flash-lite
# GEMINI_TEMPERATURE=0.1
# GEMINI_MAX_TOKENS=200
```

**Security Notes:**
- `.env` file contains sensitive API keys and is not tracked by git
- Each developer must create their own `.env` file
- Never share or commit your `.env` file
- Use `env.example` as a template for creating `.env`

### **3. Local Development (Secure)**

```bash
# Create isolated virtual environment
python -m venv aiops
source aiops/bin/activate  # On Windows: aiops\Scripts\activate

# Install dependencies with security verification
pip install -r requirements.txt

# Verify installation security
pip list --outdated

# Start secure API server
python app.py
```

#### **Windows Secure Startup**
```bash
# Use provided secure startup script
start.bat

# Manual secure startup
call aiops\Scripts\activate.bat
python app.py
```

#### **Troubleshooting Security Issues**

| Issue | Root Cause | Security Resolution |
|-------|------------|-------------------|
| **Connection Refused** | Service not started | Verify virtual environment `(aiops)` and restart |
| **ModuleNotFoundError** | Missing dependencies | `pip install psutil` or use `python_config\pip.bat install psutil` |
| **API Key Validation Failed** | Invalid credentials | Verify `.env` file format and API key validity |
| **Port Conflict** | Port already in use | Change `API_PORT` in `.env` or terminate conflicting services |

### **4. Docker Secure Deployment (Recommended)**

```bash
# Build and deploy with security scanning
docker-compose up -d

# Verify container security
docker-compose ps
docker-compose logs --tail=50

# Security health check
curl http://localhost:8000/health
```

### **5. Access Secure API**

| Endpoint | Purpose | Security Level |
|----------|---------|----------------|
| **API Documentation** | http://localhost:8000/docs | Interactive security testing |
| **Health Check** | http://localhost:8000/health | System security status |
| **API Information** | http://localhost:8000/info | Configuration verification |
| **Example Queries** | http://localhost:8000/examples | Threat intelligence samples |

## 🔍 API Security Endpoints

| Endpoint | Method | Security Features | Description |
|----------|--------|-------------------|-------------|
| `/` | GET | Rate limiting, CORS | Root endpoint with security info |
| `/health` | GET | Health monitoring | Comprehensive system security status |
| `/info` | GET | Configuration validation | Detailed API security configuration |
| `/examples` | GET | Input sanitization | Secure example threat queries |
| `/ask` | POST | Input validation, rate limiting | AI-powered threat intelligence Q&A |
| `/docs` | GET | Interactive security testing | Swagger UI for API exploration |

### **Secure API Usage Examples**

```bash
# Threat intelligence query with security headers
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -H "User-Agent: Security-Client/1.0" \
     -d '{"question": "What is the current Cyber Risk Index (CRI) and its implications?"}'

# Security health check
curl -H "Accept: application/json" http://localhost:8000/health

# Threat intelligence examples
curl -H "Accept: application/json" http://localhost:8000/examples
```

## 📁 Secure Project Structure

```
trend-micro-security-qa-api/
├── app.py                  # FastAPI security application
├── main.py                 # Core AI security logic
├── requirements.txt        # Secure Python dependencies
├── Dockerfile             # Hardened Docker configuration
├── docker-compose.yml     # Secure service orchestration
├── .env.example           # Secure environment template
├── .gitignore            # Security-focused ignore rules
├── README.md             # Security documentation
├── PROJECT_STATUS.md     # Security project status
├── docker.md             # Secure deployment guide
├── knowledgebase.txt     # Threat intelligence data
├── summary.txt           # Secure knowledge base
├── start.bat             # Secure Windows startup
├── tests/                # Security test suite
│   ├── test_gemini_only.py
│   └── test_summary.py
├── examples/             # Security examples
│   └── test_log.py
└── python_config/        # Secure Python environment
    ├── python.bat
    ├── pip.bat
    └── setup_python.bat
```

## 🔧 Security Configuration

### **AI Model Security Settings**

The platform employs enterprise-grade AI model configuration:

- **Model**: `gemini-2.0-flash-lite` - Google's latest secure Gemini Flash model
- **Temperature**: `0.1` - Low temperature for consistent, factual threat analysis
- **Max Tokens**: `200` - Optimized response length for concise security insights
- **Embeddings**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` - Local multilingual processing
- **Vector Database**: FAISS with 3 nearest neighbors for secure retrieval
- **Text Chunking**: 1000 characters with 200 character overlap for optimal context

**Security Note**: All model parameters are configurable via environment variables for maximum security flexibility.

### **Docker Security Configuration**

- **Multi-stage build**: Optimized image size and attack surface reduction
- **Non-root execution**: Security best practices for container isolation
- **Health checks**: Automatic security monitoring and alerting
- **Volume mounts**: Secure knowledge base persistence
- **Security scanning**: Built-in vulnerability assessment

## 🧪 Security Testing

### **Run Security Tests**

```bash
# Core security functionality test
python tests/test_gemini_only.py

# Threat intelligence knowledge base test
python tests/test_summary.py
```

### **API Security Testing**

```bash
# Security health endpoint test
curl -H "Accept: application/json" http://localhost:8000/health

# Threat intelligence Q&A security test
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -H "User-Agent: Security-Test/1.0" \
     -d '{"question": "What are the emerging cybersecurity threats in 2025?"}'
```

## 📊 Security Project Status

- ✅ **Core AI Security**: Google Gemini integration with secure RAG
- ✅ **API Security**: FastAPI backend with comprehensive security endpoints
- ✅ **Container Security**: Hardened Docker deployment with security scanning
- ✅ **Security Documentation**: Complete API security documentation
- ✅ **Threat Intelligence**: Environment variable security management
- ✅ **Security Testing**: Comprehensive security test suite
- 🔄 **Security CI/CD**: GitHub Actions security workflow (planned)
- 🔄 **Cloud Security**: Azure secure container deployment (planned)

For detailed security progress, see [PROJECT_STATUS.md](PROJECT_STATUS.md)

## 🐳 Secure Docker Deployment

### **Quick Secure Start with Docker**

```bash
# Deploy with security scanning
docker-compose up -d

# Monitor security logs
docker-compose logs -f

# Secure service shutdown
docker-compose down
```

### **Docker Security Features**

- **Multi-stage build**: Reduced attack surface and optimized security
- **Non-root user**: Security best practices for container isolation
- **Health checks**: Automatic security monitoring and alerting
- **Volume mounts**: Secure knowledge base persistence
- **Environment variables**: Flexible security configuration

For detailed Docker security documentation, see [docker.md](docker.md)

## 🛡️ Security Considerations

### **API Security**
- **API Key Management**: Secure environment variable handling for sensitive credentials
- **Input Validation**: Comprehensive request validation and sanitization
- **Rate Limiting**: Protection against abuse and DDoS attacks
- **CORS Configuration**: Secure cross-origin resource sharing
- **Error Handling**: Secure error messages without information disclosure

### **Container Security**
- **Non-root Execution**: Container runs with minimal privileges
- **Security Scanning**: Built-in vulnerability assessment
- **Image Hardening**: Optimized base images with security patches
- **Network Isolation**: Secure container networking

### **Data Security**
- **Local Processing**: Embeddings processed locally without external calls
- **Encrypted Storage**: Vector database with encryption at rest
- **Secure Logging**: Audit trails for compliance and security monitoring
- **Access Control**: Environment-based access management

## 🤝 Contributing to Security

1. **Security Review**: Fork the repository and conduct security assessment
2. **Feature Branch**: Create a security-focused feature branch (`git checkout -b security/security-feature`)
3. **Security Commit**: Commit with security-focused message (`git commit -m 'Add security enhancement'`)
4. **Security Push**: Push to security branch (`git push origin security/security-feature`)
5. **Security PR**: Open a Pull Request with security documentation

## 📄 Security License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for security terms and conditions.

## 🙏 Security Acknowledgments

- **Trend Micro**: For providing comprehensive cybersecurity threat intelligence
- **Google**: For secure Gemini AI API and enterprise-grade AI capabilities
- **FastAPI**: For secure, high-performance web framework
- **LangChain**: For secure RAG framework implementation
- **Docker**: For secure containerization technology
- **OWASP**: For security best practices and guidelines

## 🆘 Security Support

- **Security Documentation**: [API Security Docs](http://localhost:8000/docs)
- **Security Issues**: [GitHub Security Issues](https://github.com/ubn2vm/trend-micro-security-qa-api/issues)
- **Security Status**: [PROJECT_STATUS.md](PROJECT_STATUS.md)
- **Security Guide**: [QUICK_START.md](QUICK_START.md)

---

**🔒 Built for Enterprise Cybersecurity Intelligence**  
**🛡️ Security-First Design**  
**🎯 Threat Intelligence Excellence**

*Last updated: 2025-01-XX*  
*Security Version: 1.0.0*  
*Security Level: Enterprise*