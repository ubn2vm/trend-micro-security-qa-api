# Trend Micro Internal Knowledge Q&A Robot 
Transform hours of document hunting into seconds of intelligent answers with our RAG-powered knowledge assistant. First product knowledge is based on Cyber Risk Exposure Management (CREM).

## Problem & Solution

**Daily Struggle**: Every time I need to answer questions about a new Trend Vision One App, I spend hours digging through hundreds of PDFs and wiki pages. With 100+ apps and growing, it's exhausting to learn each new app while trying to find accurate, up-to-date information. Even as a senior analyst, I often end up with outdated answers or missing critical details. This bottleneck prevents me from quickly providing stakeholders with the data insights they need, ultimately dragging down company productivity.

**My Solution**: Built this RAG-powered knowledge assistant that instantly finds relevant information and provides accurate answers with source references. This eliminates manual document hunting and enables immediate access to current information, significantly boosting both individual and organizational productivity.

## Demo & Screenshots

### Quick Start Demo
![Quick Start Demo](presentation/assets/screenshots/gif/start_simple_bat.gif)

### Gradio Interface Demo
![Gradio Interface Demo](presentation/assets/screenshots/gif/start_gradio_bat.gif)

### Chatbot Interface (Gradio)
![Chatbot Interface](presentation/assets/screenshots/gif/gradio.png)

### Auto-generated API Docs (FastAPI/Swagger)
![API Documentation](presentation/assets/screenshots/gif/ap1.png)

## Technology Stack

- **Runtime Environment**: Python 3.11+
- **Web Framework**: FastAPI with Uvicorn ASGI server
- **AI/ML Libraries**: LangChain, FAISS, Sentence Transformers
- **Cloud AI Service**: Gemini 2.0 Flash-Lite (gemini-2.0-flash-lite)
- **Frontend Framework**: Gradio
- **Containerization**: Docker with Docker Compose
- **System Monitoring**: psutil for resource utilization tracking
- **Data Extracting**: pdfplumber for PDF 

## System Architecture & Design

### High-Level Architecture
```mermaid
flowchart TB
    subgraph Frontend
        A[Gradio UI]
    end
    subgraph API
        B[FastAPI Backend]
    end
    subgraph Processing
        C[RAG Engine]
        D[Gemini 2.0 API]
    end
    subgraph Data
        E[FAISS Vector DB]
        F[CREM Knowledge Base]
    end
    subgraph Monitoring
        G[Health Monitor]
        H[System Diagnostics]
        I[Audit Logging]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    E --> F
    B -.-> G
    G --> H
    H --> I
```

### Data Flow & Processing Pipeline
**Quick Overview**: User queries flow through the Gradio UI → FastAPI backend → RAG processing engine → FAISS vector search → Gemini 2.0 API → structured response back to user interface.

For detailed data flow diagrams and technical specifications, please refer to our [Technical Documentation](docs/README.md).

### API Endpoints & Integration
| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/health` | GET | System health status | None |
| `/docs` | GET | Interactive API documentation | None |
| `/info` | GET | System information and configuration | None |
| `/examples` | GET | Sample query examples | None |
| `/ask` | POST | Query processing endpoint | **No Auth (Demo)** |

**Security Notice**:
- `/ask` endpoint currently has **no authentication**
- This is a demo/development version, not production-ready
- Authentication must be implemented before production deployment

### Engineering Practices & Optimization

#### RAG Pipeline Optimization
- **Text Chunking**: 512-character chunks with 50-character overlap for optimal context retention
- **Prompt Engineering**: Custom CREM_PROMPT_TEMPLATE with temperature 0.05 to minimize hallucinations
- **Vector Search**: FAISS index with top-5 similarity matching and 0.7 score threshold
- **Data Processing**: 19 chunks averaging 410 characters with 49 technical terms identified

## Deployment Options

### Quick Start (Windows Only, Recommended)
```bash
# Execute automated deployment script
presentation/scripts/start_simple.bat
```

**Note**: Currently, one-click deployment scripts are only available for Windows. macOS and Linux versions are planned for future releases.

### Manual Deployment
```bash
# Environment setup
python -m venv aiops

# Activate virtual environment
# Windows:
aiops\Scripts\activate.bat
# macOS/Linux:
source aiops/bin/activate

pip install -r core_app/requirements.txt

# API server startup
python core_app/app.py

# Frontend interface
python core_app/gradio_app.py
```

### Containerized Deployment
```bash
# Docker Compose deployment
cd containerization
docker-compose up -d
```

## Development Status

### TODOs
- **Testing Framework**: pytest security tests execution and validation
    - Unit Tests: Individual component functionality
    - Integration Tests: End-to-end system validation
    - Performance Tests: Load testing and response time analysis
    - Security Tests: Vulnerability assessment and penetration testing
- **Security Implementation**: Security testing and vulnerability assessment
    - API Key Management
    - Input Validation
    - Data Protection
    - Container Security

## Future Enhancements

### RAG System Evaluation Metrics
- **Response Accuracy**: Implement automated testing with predefined Q&A pairs to measure answer correctness
- **Relevance Scoring**: Use cosine similarity between query and retrieved context to ensure relevance
- **Hallucination Detection**: Compare generated responses against source documents using semantic similarity

### Testing Framework Enhancement
- **Automated RAG Testing**: Create test suite with 50+ predefined Q&A pairs covering different CREM topics

### CI/CD Pipeline Implementation
- **Automated Testing**: GitHub Actions workflow that runs tests on every commit

## Support and Contact

For technical support or questions regarding this implementation, please refer to the project documentation or contact the development team.

---

**Note**: This system is designed for demonstration and educational purposes. For production deployment, additional security hardening and compliance measures should be implemented. 