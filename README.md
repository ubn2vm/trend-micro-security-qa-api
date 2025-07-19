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

### High-Level Architecture
```mermaid
graph TB

    %% Node Definitions - Define all nodes first
    A["1.Gradio UI<br>Port 7860"]
    B["2.User Query Input"]
    C["3.FastAPI Backend<br>Port 8000"]
    D["4.Request Validation"]
    E["5.Authentication & Rate Limiting"]
    F["6.RAG Processing Engine"]
    G["7.Query Vectorization"]
    H["8.Semantic Search"]
    I["9.FAISS Vector Database"]
    J["0.Knowledge Base<br>CREM Documents"]
    K["11.Google Gemini 1.5 Pro API"]
    O["12.Response Generation"]
    Q["13.Structured Response"]
    R["14.Response Validation"]
    S["15.User Interface"]

    %% Monitoring Layer Nodes
    L1["Health Monitor"]
    L2["System Diagnostics"]
    L3["Audit Logging"]

    %% Main Flow Connections
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I -- "10.Retrieve Relevant Chunks" --> F
    F --> K
    K --> O
    O --> Q
    Q --> R
    R --> S

    %% Knowledge Base Initialization Connection
    J -- "Initialization/Vectorization" --> I

    %% Monitoring Layer Connections
    C -.-> L1
    L1 --> L2
    L2 --> L3

    %% Color Styles - High Contrast for Light/Dark Mode
    %% Frontend Layer (Blue with White Text)
    style A fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#fff
    style B fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#fff
    style S fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#fff

    %% API Layer (Purple with White Text)
    style C fill:#7b1fa2,stroke:#4a148c,stroke-width:2px,color:#fff
    style D fill:#7b1fa2,stroke:#4a148c,stroke-width:2px,color:#fff
    style E fill:#7b1fa2,stroke:#4a148c,stroke-width:2px,color:#fff

    %% Processing/LLM Layer (Green with White Text)
    style F fill:#388e3c,stroke:#1b5e20,stroke-width:2px,color:#fff
    style G fill:#388e3c,stroke:#1b5e20,stroke-width:2px,color:#fff
    style H fill:#388e3c,stroke:#1b5e20,stroke-width:2px,color:#fff
    style K fill:#388e3c,stroke:#1b5e20,stroke-width:2px,color:#fff
    style O fill:#388e3c,stroke:#1b5e20,stroke-width:2px,color:#fff
    style Q fill:#388e3c,stroke:#1b5e20,stroke-width:2px,color:#fff
    style R fill:#388e3c,stroke:#1b5e20,stroke-width:2px,color:#fff

    %% Database Layer (Orange with Black Text)
    style I fill:#ffa726,stroke:#f57c00,stroke-width:2px,color:#000
    style J fill:#ffa726,stroke:#f57c00,stroke-width:2px,color:#000

    %% Monitoring Layer (Teal with Black Text)
    style L1 fill:#0097a7,stroke:#006064,stroke-width:2px,color:#fff
    style L2 fill:#0097a7,stroke:#006064,stroke-width:2px,color:#fff
    style L3 fill:#0097a7,stroke:#006064,stroke-width:2px,color:#fff
```

### Data Flow & Processing Pipeline
**Quick Overview**: User queries flow through the Gradio UI → FastAPI backend → RAG processing engine → FAISS vector search → Gemini 2.0 API → structured response back to user interface.

For detailed data flow diagrams and technical specifications, please refer to our [Data Flow](docs/data_flow.md).

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
# Environment setup
python -m venv aiops

# Activate virtual environment
# Windows:
aiops\Scripts\activate.bat
# macOS/Linux:
source aiops/bin/activate

pip install -r core_app/requirements.txt

# API server startup
python -m core_app.app

# Frontend interface
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