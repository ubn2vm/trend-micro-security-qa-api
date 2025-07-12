import os
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 載入環境變數 - 先載入 config.env，再載入 .env（API Key）
load_dotenv('../config/config.env')
load_dotenv('../.env')

# 導入我們的問答系統
## 使用絕對導入，確保在各種執行環境下都能正常工作
from core_app.main import TrendMicroQASystem

# 設定日誌
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用程式
app = FastAPI(
    title=os.getenv("API_TITLE", "Trend Micro Security Intelligence API"),
    description=os.getenv("API_DESCRIPTION", "AI-powered cybersecurity intelligence platform based on Trend Micro 2025 Cyber Risk Report"),
    version=os.getenv("API_VERSION", "1.0.0"),
    docs_url="/docs",
    redoc_url="/redoc"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該設定具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 模型定義
class QuestionRequest(BaseModel):
    """Question request model"""
    question: str = Field(..., description="User question", min_length=1, max_length=500)
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is Cyber Risk Index (CRI)?"
            }
        }

class QuestionResponse(BaseModel):
    """Question response model"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI generated answer")
    sources: List[str] = Field(default=[], description="Source document fragments")
    status: str = Field(..., description="Response status")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is Cyber Risk Index (CRI)?",
                "answer": "Cyber Risk Index (CRI) is a metric that quantifies an organization's overall security risk...",
                "sources": ["CREM calculates the Cyber Risk Index (CRI), which quantifies an organization's overall security risk based on integrated asset and risk factor scores..."],
                "status": "success"
            }
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Check timestamp")
    components: Dict[str, str] = Field(..., description="Component statuses")
    environment: Dict[str, str] = Field(..., description="Environment information")

# 全域變數
qa_system = None

def get_qa_system() -> TrendMicroQASystem:
    """取得問答系統實例"""
    global qa_system
    if qa_system is None:
        try:
            qa_system = TrendMicroQASystem()
            logger.info("問答系統初始化成功")
        except Exception as e:
            logger.error(f"問答系統初始化失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=f"系統初始化失敗: {str(e)}")
    return qa_system

@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件"""
    logger.info("趨勢科技資安問答 API 啟動中...")
    try:
        # 預先初始化問答系統
        get_qa_system()
        logger.info("API 啟動成功！")
    except Exception as e:
        logger.error(f"API 啟動失敗: {str(e)}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API Information"""
    return {
        "message": "Trend Micro Security Intelligence API",
        "version": os.getenv("API_VERSION", "1.0.0"),
        "docs": "/docs",
        "health": "/health",
        "examples": "/examples",
        "info": "/info"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    import datetime
    
    try:
        # 初始化組件狀態
        components = {}
        environment = {}
        
        # 檢查環境變數
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
            environment["api_key"] = f"Configured ({masked_key})"
        else:
            environment["api_key"] = "Not configured"
            components["api_key"] = "error"
        
        # 檢查模型設定
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
        temperature = os.getenv("GEMINI_TEMPERATURE", "0.1")
        max_tokens = os.getenv("GEMINI_MAX_TOKENS", "200")
        environment["model"] = model_name
        environment["temperature"] = temperature
        environment["max_tokens"] = max_tokens
        
        # 檢查 RAG 向量資料庫
        rag_vector_dir = os.getenv("RAG_VECTOR_DIR", "core_app/rag/vector_store/crem_faiss_index")
        if os.path.exists(rag_vector_dir):
            environment["rag_vector_dir"] = f"{rag_vector_dir} (Exists)"
            components["rag_vector_store"] = "healthy"
        else:
            environment["rag_vector_dir"] = f"{rag_vector_dir} (Not found)"
            components["rag_vector_store"] = "error"
        
        # 檢查問答系統
        try:
            qa_system = get_qa_system()
            components["qa_system"] = "healthy"
            
            # 執行簡單測試
            test_result = qa_system.ask_question("測試")
            if test_result.get("status") == "success":
                components["ai_model"] = "healthy"
            else:
                components["ai_model"] = "warning"
        except Exception as e:
            components["qa_system"] = "error"
            components["ai_model"] = "error"
            logger.error(f"問答系統檢查失敗: {str(e)}")
        
        # 檢查 API 服務
        components["api_server"] = "healthy"
        
        # 檢查記憶體使用
        import psutil
        memory = psutil.virtual_memory()
        environment["memory_usage"] = f"{memory.percent}%"
        environment["memory_available"] = f"{memory.available // (1024**3)} GB"
        
        # 檢查磁碟空間
        disk = psutil.disk_usage('.')
        environment["disk_usage"] = f"{disk.percent}%"
        environment["disk_free"] = f"{disk.free // (1024**3)} GB"
        
        # 判斷整體狀態
        if "error" in components.values():
            status = "unhealthy"
            message = "Some components are unhealthy"
        elif "warning" in components.values():
            status = "degraded"
            message = "Service running with some component warnings"
        else:
            status = "healthy"
            message = "All components are running normally"
        
        return HealthResponse(
            status=status,
            message=message,
            version=os.getenv("API_VERSION", "1.0.0"),
            timestamp=datetime.datetime.now().isoformat(),
            components=components,
            environment=environment
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service error: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, qa_system: TrendMicroQASystem = Depends(get_qa_system)):
    """
    Intelligent Q&A endpoint
    
    - **question**: User question
    - **returns**: AI generated answer and related sources
    """
    try:
        logger.info(f"收到問題請求: {request.question}")
        
        # 執行問答
        result = qa_system.ask_question(request.question)
        
        # 檢查回應狀態
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("answer", "處理問題時發生錯誤"))
        
        logger.info(f"問題處理完成: {request.question}")
        
        return QuestionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理問題時發生未預期錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"內部服務錯誤: {str(e)}")

@app.get("/examples", response_model=List[str])
async def get_example_questions():
    """Get example questions list"""
    examples = [
        "What is Cyber Risk Index (CRI)?",
        "What is the overall average CRI for 2024?",
        "Which industries have the highest CRI?",
        "What is CREM?",
        "How to reduce enterprise cyber risk?",
        "What is Trend Vision One?",
        "What are the main cyber threats facing enterprises?",
        "How to improve cybersecurity posture?"
    ]
    return examples

@app.get("/info", response_model=Dict[str, Any])
async def get_api_info():
    """Get API detailed information"""
    return {
        "title": "Trend Micro Security Intelligence API",
        "description": "AI-powered cybersecurity intelligence platform based on Trend Micro 2025 Cyber Risk Report",
        "version": app.version,
        "knowledge_base": os.getenv("KNOWLEDGE_FILE", "summary.txt"),
        "endpoints": {
            "root": "/",
            "health": "/health",
            "ask": "/ask",
            "examples": "/examples",
            "info": "/info",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"啟動 API 服務於 {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info") 