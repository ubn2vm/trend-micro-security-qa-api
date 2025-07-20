# Trend Micro Internal Knowledge Q&A Robot 
Transform hours of document hunting into seconds of intelligent answers with our RAG-powered knowledge assistant. First product knowledge is based on Cyber Risk Exposure Management (CREM).

## Problem & Solution

**Daily Struggle**: Every time I need to answer questions about a new Trend Vision One App, I spend hours digging through hundreds of PDFs and wiki pages. With 100+ apps and growing, it's exhausting to learn each new app while trying to find accurate, up-to-date information. Even as a senior analyst, I often end up with outdated answers or missing critical details. This bottleneck prevents me from quickly providing stakeholders with the data insights they need, ultimately dragging down company productivity.

**My Solution**: Built this RAG-powered knowledge assistant that instantly finds relevant information and provides accurate answers with source references. This eliminates manual document hunting and enables immediate access to current information, significantly boosting both individual and organizational productivity.

## Demo & Screenshots

### Quick Start Demo
![Quick Start Demo](presentation/assets/screenshots/gif/start_simple_bat.gif)

### Quick Start Gradio Interface Demo
![Gradio Interface Demo](presentation/assets/screenshots/gif/start_gradio_bat.gif)

### Chatbot Interface
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
- **Document & Table Processing**: pdfplumber, camelot-py, PyMuPDF, tabula-py for comprehensive PDF text and table extraction with multi-strategy approach

## System Architecture & Design

### High-Level Architecture Overview
```mermaid
graph LR
    subgraph "User Interface Layer"
        A[Gradio Web UI]
    end
    
    subgraph "API Gateway Layer"
        B[FastAPI Backend]
    end
    
    subgraph "AI Processing Layer"
        C[RAG Engine]
        D[Vector Search]
        E[LLM Integration]
    end
    
    subgraph "Data Layer"
        F[Knowledge Base]
        G[Vector Store]
    end
    
    subgraph "Monitoring Layer"
        H[Health Monitor]
        I[Audit Logging]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> C
    F --> G
    G --> D
    B --> H
    H --> I
    
    %% GitHub-friendly color scheme - works on both light and dark themes
    style A fill:#0366d6,stroke:#0366d6,stroke-width:2px,color:#ffffff
    style B fill:#6f42c1,stroke:#6f42c1,stroke-width:2px,color:#ffffff
    style C fill:#28a745,stroke:#28a745,stroke-width:2px,color:#ffffff
    style D fill:#28a745,stroke:#28a745,stroke-width:2px,color:#ffffff
    style E fill:#28a745,stroke:#28a745,stroke-width:2px,color:#ffffff
    style F fill:#f66a0a,stroke:#f66a0a,stroke-width:2px,color:#ffffff
    style G fill:#f66a0a,stroke:#f66a0a,stroke-width:2px,color:#ffffff
    style H fill:#17a2b8,stroke:#17a2b8,stroke-width:2px,color:#ffffff
    style I fill:#17a2b8,stroke:#17a2b8,stroke-width:2px,color:#ffffff
```

### Core Design Principles

#### 1. **Modular Architecture**
- **Separation of Concerns**: Each layer has distinct responsibilities
- **Scalability**: Independent scaling of UI, API, and processing components
- **Maintainability**: Clear interfaces between components

#### 2. **RAG-Powered Intelligence**
- **Retrieval-Augmented Generation**: Combines document search with AI generation
- **Real-time Knowledge Access**: Instant access to up-to-date information
- **Source Attribution**: Every answer includes reference to source documents

#### 3. **Enterprise-Grade Features**
- **Multi-format Document Support**: PDF, tables, and structured data
- **Vector-based Search**: Semantic similarity for context-aware retrieval
- **Performance Optimization**: Sub-second response times for user queries

### Business Value & Impact

#### **Productivity Enhancement**
- **Time Savings**: Reduce document hunting from hours to seconds
- **Accuracy Improvement**: Eliminate outdated information risks
- **Knowledge Democratization**: Make expert knowledge accessible to all team members

#### **Operational Efficiency**
- **Reduced Training Time**: New team members can quickly access product knowledge
- **Consistent Responses**: Standardized answers across the organization
- **Scalable Support**: Handle multiple concurrent users without degradation

For detailed technical implementation and data flow specifications, please refer to our [Data Flow Documentation](docs/data_flow.md).

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
- **Data Processing**: 174 text chunks + 88 table extracts = 262 total vectors with 99,826 characters of structured table content and comprehensive enterprise document coverage

## Deployment Options

### Quick Start (Windows Only, Recommended)
```bash
# Execute automated deployment script
presentation/scripts/start_simple.bat
```

**Note**: Currently, one-click deployment scripts are only available for Windows. macOS and Linux versions are planned for future releases.

### Manual Deployment
```bash
# Step 1: Get Google API Key
# Visit https://makersuite.google.com/app/apikey to get your API key

# Step 2: Configure Environment
# Copy environment template
cp config/env.example .env
# Windows: copy config\env.example .env

# Edit .env file to add your API key:
# GOOGLE_API_KEY=your_actual_api_key_here

# Step 3: Environment setup
python -m venv aiops

# Activate virtual environment
# Windows:
aiops\Scripts\activate.bat
# macOS/Linux:
source aiops/bin/activate

pip install -r core_app/requirements.txt

# Step 4: Start services
# API server startup
python -m core_app.app

# Frontend interface (run in separate terminal)
python -m core_app.gradio_app
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