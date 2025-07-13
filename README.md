# Trend Micro Internal Knowledge Q&A Robot
- aka Trend Micro RAG Walking Dictionary
- aka 趨勢RAG活字典 


## Demo & Screenshots

### Quick Start Demo
![Quick Start Demo](presentation/assets/screenshots/gif/start_simple_bat.gif)

### Gradio Interface Demo
![Gradio Interface Demo](presentation/assets/screenshots/gif/start_gradio_bat.gif)

### Chatbot Interface
![Chatbot Interface](presentation/assets/screenshots/gif/gradio.png)

### API Documentation
![API Documentation](presentation/assets/screenshots/gif/ap1.png)

## Problem & Solution

**Daily Struggle**: Every time I need to answer questions about a new Trend Vision One App, I spend hours digging through hundreds of PDFs and wiki pages. With 100+ apps and growing, it's exhausting to learn each new app while trying to find accurate, up-to-date information. Even as a senior analyst, I often end up with outdated answers or missing critical details. This bottleneck prevents me from quickly providing stakeholders with the data insights they need, ultimately dragging down company productivity.

**My Solution**: Built this RAG-powered knowledge assistant that instantly finds relevant information and provides accurate answers with source references. This eliminates manual document hunting and enables immediate access to current information, significantly boosting both individual and organizational productivity.


## Deployment Options

### One-Click Deployment (Recommended)
```bash
# Execute automated deployment script
presentation/scripts/start_simple.bat
```

### Manual Deployment
```bash
# Environment setup
python -m venv aiops
aiops\Scripts\activate.bat
pip install -r core_app\requirements.txt

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

## API Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/health` | GET | System health status | None |
| `/docs` | GET | Interactive API documentation | None |
| `/info` | GET | System information and configuration | None |
| `/examples` | GET | Sample query examples | None |
| `/ask` | POST | Query processing endpoint | API Key |


### Technology Stack

- **Runtime Environment**: Python 3.13.5
- **Web Framework**: FastAPI with Uvicorn ASGI server
- **AI/ML Libraries**: LangChain, FAISS, Sentence Transformers
- **Cloud AI Service**: Google Gemini 2.0 API
- **Frontend Framework**: Gradio
- **Containerization**: Docker with Docker Compose
- **System Monitoring**: psutil for resource utilization tracking
- **Data Extracting**: pdfplumber for PDF 

## System Architecture

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

## Data Flow

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
    K["11.Google Gemini 2.0 API"]
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

    %% Color Styles for Different Layers
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style B fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style S fill:#e3f2fd,stroke:#1976d2,stroke-width:2px

    style C fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style D fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    style F fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style G fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style H fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style K fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style O fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style Q fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style R fill:#e8f5e9,stroke:#388e3c,stroke-width:2px

    style I fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style J fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    style L1 fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    style L2 fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    style L3 fill:#f1f8e9,stroke:#33691e,stroke-width:2px
```

**Color Legend:**
- <span style="background-color:#e3f2fd; border:1px solid #1976d2; padding:2px 8px;">Frontend</span>
- <span style="background-color:#f3e5f5; border:1px solid #7b1fa2; padding:2px 8px;">API Layer</span>
- <span style="background-color:#e8f5e9; border:1px solid #388e3c; padding:2px 8px;">Processing/LLM Layer</span>
- <span style="background-color:#fff3e0; border:1px solid #f57c00; padding:2px 8px;">Data Layer</span>
- <span style="background-color:#f1f8e9; border:1px solid #33691e; padding:2px 8px;">Monitoring Layer</span>

## Engineering Practices

### RAG Pipeline Optimization
- **Text Chunking**: 512-character chunks with 50-character overlap for optimal context retention
- **Prompt Engineering**: Custom CREM_PROMPT_TEMPLATE with temperature 0.05 to minimize hallucinations
- **Vector Search**: FAISS index with top-5 similarity matching and 0.7 score threshold
- **Quality Validation**: 100% quality score with 19 chunks averaging 410 characters

## Development Status

### In Development
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