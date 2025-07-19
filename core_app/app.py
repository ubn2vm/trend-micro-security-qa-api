import os
import logging
import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 載入環境變數 - 使用絕對路徑確保在任何目錄下都能正確載入
from pathlib import Path

# 取得專案根目錄的絕對路徑
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / 'config' / 'config.env'
ENV_PATH = PROJECT_ROOT / '.env'

# 載入環境變數 - 先載入 config.env，再載入 .env（API Key）
load_dotenv(CONFIG_PATH)
load_dotenv(ENV_PATH)

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
    title=os.getenv("API_TITLE", "Trend Micro Advanced RAG API"),
    description=os.getenv("API_DESCRIPTION", "支援表格和文本混合查詢的進階RAG系統 - Trend Micro 2025 Cyber Risk Report"),
    version=os.getenv("API_VERSION", "2.0.0"),
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
    filter_type: str = Field(default="all", description="Query type: all, text, table")
    k: int = Field(default=3, description="Number of results to return", ge=1, le=10)
    
    class Config:
        schema_extra = {
            "example": {
                "question": "前10大風險事件有哪些？",
                "filter_type": "all",
                "k": 3
            }
        }

class QuestionResponse(BaseModel):
    """Question response model"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI generated answer")
    sources: List[str] = Field(default=[], description="Source document fragments")
    citations: List[Dict[str, Any]] = Field(default=[], description="Detailed citation information")
    status: str = Field(..., description="Response status")
    result_count: int = Field(default=0, description="Number of results found")
    text_results: int = Field(default=0, description="Number of text results")
    table_results: int = Field(default=0, description="Number of table results")
    filter_type: str = Field(default="all", description="Query type used")
    # 新增關鍵欄位
    generation_method: str = Field(default="unknown", description="Answer generation method")
    llm_available: bool = Field(default=False, description="Whether LLM is available")
    system_type: str = Field(default="unknown", description="System type identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "前10大風險事件有哪些？",
                "answer": "根據最新資料統計：...",
                "sources": ["[TABLE] Research-Risk-Report-2025.pdf (信心度: 0.95)"],
                "citations": [
                    {
                        "rank": 1,
                        "source": "Research-Risk-Report-2025.pdf",
                        "content_type": "text",
                        "content": "The top risk events include...",
                        "confidence": 0.95
                    }
                ],
                "status": "success",
                "result_count": 3,
                "text_results": 1,
                "table_results": 2,
                "filter_type": "all",
                "generation_method": "llm_generated",
                "llm_available": True,
                "system_type": "TrendMicroQASystem"
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
    # 新增系統統計欄位
    system_type: str = Field(default="unknown", description="System type")
    vector_count: int = Field(default=0, description="Total vector count")
    llm_available: bool = Field(default=False, description="LLM availability")
    llm_model: str = Field(default="unknown", description="LLM model name")

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
    logger.info("趨勢科技進階RAG API 啟動中...")
    try:
        # 預先初始化進階RAG系統
        qa_system = get_qa_system()
        stats = qa_system.get_system_stats()
        logger.info("進階RAG API 啟動成功！")
        logger.info(f"✅ 系統類型: {stats.get('system_type', 'Unknown')}")
        logger.info(f"✅ 向量數量: {stats.get('vector_count', 0)}")
        logger.info(f"✅ 支援功能: {len(stats.get('capabilities', []))}項")
    except Exception as e:
        logger.error(f"進階RAG API 啟動失敗: {str(e)}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint - API Information"""
    return {
        "message": "Trend Micro Advanced RAG API",
        "version": os.getenv("API_VERSION", "2.0.0"),
        "description": "支援表格和文本混合查詢的進階RAG系統",
        "features": "表格查詢 + 文本查詢 + 多語言支援",
        "docs": "/docs",
        "health": "/health",
        "examples": "/examples",
        "stats": "/stats",
        "info": "/info"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    try:
        # 初始化組件狀態
        components = {}
        environment = {}
        
        # 初始化系統統計預設值
        system_type = "unknown"
        vector_count = 0
        llm_available = False
        llm_model = "unknown"
        
        # 檢查環境變數
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
            environment["api_key"] = f"Configured ({masked_key})"
            components["api_key"] = "healthy"
        else:
            environment["api_key"] = "Not configured"
            components["api_key"] = "error"
        
        # 檢查模型設定
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
        temperature = os.getenv("GEMINI_TEMPERATURE", "0.05")
        max_tokens = os.getenv("GEMINI_MAX_TOKENS", "300")
        environment["model"] = model_name
        environment["temperature"] = temperature
        environment["max_tokens"] = max_tokens
        
        # 檢查 RAG 向量資料庫路徑
        current_dir = Path(__file__).parent
        rag_vector_dir = current_dir / "rag" / "vector_store" / "crem_faiss_index"
        
        if rag_vector_dir.exists():
            environment["rag_vector_dir"] = f"{rag_vector_dir} (Exists)"
            components["rag_vector_store"] = "healthy"
        else:
            environment["rag_vector_dir"] = f"{rag_vector_dir} (Not found)"
            components["rag_vector_store"] = "error"
        
        # 檢查進階RAG系統（但不執行查詢）
        try:
            qa_system = get_qa_system()
            components["rag_system"] = "healthy"
            
            # 獲取系統統計（不執行查詢）
            stats = qa_system.get_system_stats()
            system_type = stats.get("system_type", "TrendMicroQASystem")
            vector_count = stats.get("vector_count", 0)
            llm_available = stats.get("llm_available", False)
            llm_model = stats.get("llm_model", "unknown")
            
            if vector_count > 0:
                components["vector_database"] = "healthy"
                environment["vector_count"] = str(vector_count)
                environment["total_queries"] = str(stats.get("total_queries", 0))
            else:
                components["vector_database"] = "warning"
            
            # 簡單檢查RAG引擎是否載入（不執行查詢）
            if hasattr(qa_system, 'rag_engine') and qa_system.rag_engine and qa_system.rag_engine.vector_db:
                components["query_engine"] = "healthy"
            else:
                components["query_engine"] = "warning"
                
        except Exception as e:
            components["rag_system"] = "error"
            components["vector_database"] = "error"
            components["query_engine"] = "error"
            logger.error(f"進階RAG系統檢查失敗: {str(e)}")
        
        # 檢查 API 服務
        components["api_server"] = "healthy"
        
        # 檢查記憶體使用
        try:
            import psutil
            memory = psutil.virtual_memory()
            environment["memory_usage"] = f"{memory.percent}%"
            environment["memory_available"] = f"{memory.available // (1024**3)} GB"
            
            # 檢查磁碟空間
            disk = psutil.disk_usage('.')
            environment["disk_usage"] = f"{disk.percent}%"
            environment["disk_free"] = f"{disk.free // (1024**3)} GB"
        except ImportError:
            environment["memory_usage"] = "N/A (psutil not installed)"
            environment["disk_usage"] = "N/A (psutil not installed)"
        
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
            version=os.getenv("API_VERSION", "2.0.0"),
            timestamp=datetime.datetime.now().isoformat(),
            components=components,
            environment=environment,
            system_type=system_type,
            vector_count=vector_count,
            llm_available=llm_available,
            llm_model=llm_model
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service error: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, qa_system: TrendMicroQASystem = Depends(get_qa_system)):
    """
    Intelligent Q&A endpoint with advanced RAG support
    
    - **question**: User question
    - **filter_type**: Query type (all, text, table)
    - **k**: Number of results to return
    - **returns**: AI generated answer and related sources with detailed stats
    """
    try:
        logger.info(f"收到問題請求: {request.question} (類型: {request.filter_type}, 結果數: {request.k})")
        
        # 執行問答
        result = qa_system.ask_question(
            question=request.question,
            filter_type=request.filter_type,
            k=request.k
        )
        
        # 檢查回應狀態
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("answer", "處理問題時發生錯誤"))
        
        # 獲取系統統計以補充響應
        stats = qa_system.get_system_stats()
        
        # 建構完整響應
        response_data = {
            **result,  # 包含原始回應的所有欄位
            "generation_method": result.get("generation_method", "unknown"),
            "llm_available": stats.get("llm_available", False),
            "system_type": stats.get("system_type", "TrendMicroQASystem")
        }
        
        logger.info(f"問題處理完成: {request.question} - 找到 {result.get('result_count', 0)} 個結果")
        
        return QuestionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理問題時發生未預期錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"內部服務錯誤: {str(e)}")

@app.get("/examples", response_model=List[str])
async def get_example_questions():
    """Get example questions list for advanced RAG system"""
    examples = [
        "前10大風險事件有哪些？",
        "最常見的安全威脅是什麼？",
        "雲端應用程式的風險",
        "risky cloud app access",
        "統計資料和數據分析",
        "安全政策建議",
        "企業面臨的主要挑戰",
        "如何防範網路攻擊？",
        "Microsoft Entra ID 安全問題",
        "spam protection policy"
    ]
    return examples

@app.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(qa_system: TrendMicroQASystem = Depends(get_qa_system)):
    """Get advanced RAG system statistics"""
    try:
        stats = qa_system.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"獲取系統統計失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"統計錯誤: {str(e)}")

def get_dynamic_table_count():
    """動態獲取表格數量"""
    try:
        from pathlib import Path
        import json
        
        table_texts_file = Path(__file__).parent / "rag" / "data" / "processed" / "table_texts.json"
        if table_texts_file.exists():
            with open(table_texts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('total_tables', 0)
    except Exception:
        pass
    return 0

@app.get("/info", response_model=Dict[str, Any])
async def get_system_info():
    """Get comprehensive system information"""
    
    # ✅ 動態獲取表格數量
    table_count = get_dynamic_table_count()
    
    return {
        "title": "Trend Micro Advanced RAG API",
        "description": "支援表格和文本混合查詢的進階RAG系統 - Trend Micro 2025 Cyber Risk Report",
        "version": app.version,
        "rag_type": "表格+文本混合RAG",
        "capabilities": [
            f"{table_count}個表格數據查詢",  # ✅ 動態顯示
            "混合文本+表格搜尋",
            "多語言支援(中文/英文)",
            "語義搜尋",
            "智能查詢類型檢測"
        ],
        "endpoints": {
            "root": "/",
            "health": "/health",
            "ask": "/ask",
            "examples": "/examples",
            "stats": "/stats",
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