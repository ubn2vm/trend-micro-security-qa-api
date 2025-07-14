# Detailed Data Flow Diagram

## Complete System Data Flow

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

## Color Legend

- <span style="background-color:#e3f2fd; border:1px solid #1976d2; padding:2px 8px;">Frontend</span>
- <span style="background-color:#f3e5f5; border:1px solid #7b1fa2; padding:2px 8px;">API Layer</span>
- <span style="background-color:#e8f5e9; border:1px solid #388e3c; padding:2px 8px;">Processing/LLM Layer</span>
- <span style="background-color:#fff3e0; border:1px solid #f57c00; padding:2px 8px;">Data Layer</span>
- <span style="background-color:#f1f8e9; border:1px solid #33691e; padding:2px 8px;">Monitoring Layer</span>

## Detailed Flow Description

### 1. User Interface Layer
- **Gradio UI (Port 7860)**: Web-based chat interface
- **User Query Input**: Natural language questions about Trend Micro products

### 2. API Layer
- **FastAPI Backend (Port 8000)**: RESTful API server
- **Request Validation**: Input sanitization and format checking
- **Authentication & Rate Limiting**: API key validation and usage limits

### 3. Processing Layer
- **RAG Processing Engine**: Core retrieval-augmented generation logic
- **Query Vectorization**: Convert text queries to vector embeddings
- **Semantic Search**: Find relevant document chunks using similarity
- **Google Gemini 2.0 API**: Large language model for response generation

### 4. Data Layer
- **FAISS Vector Database**: High-performance similarity search index
- **Knowledge Base**: CREM documents and technical specifications

### 5. Monitoring Layer
- **Health Monitor**: System status and performance metrics
- **System Diagnostics**: Resource utilization and error tracking
- **Audit Logging**: Request/response logging for compliance

## Technical Specifications

### Vector Search Parameters
- **Chunk Size**: 512 characters with 50-character overlap
- **Similarity Threshold**: 0.7 minimum score
- **Top Results**: 5 most relevant chunks

### Response Generation
- **Temperature**: 0.05 (low randomness for consistent answers)
- **Max Tokens**: 2048
- **Prompt Template**: Custom CREM_PROMPT_TEMPLATE

### Performance Metrics
- **Average Response Time**: < 3 seconds
- **Vector Search Speed**: < 100ms
- **System Uptime**: 99.9% 