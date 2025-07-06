import os
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入我們的問答系統
from main import TrendMicroQASystem

# 設定日誌
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用程式
app = FastAPI(
    title=os.getenv("API_TITLE", "趨勢科技資安報告智能問答 API"),
    description=os.getenv("API_DESCRIPTION", "基於趨勢科技2025年網路風險報告的智能問答系統"),
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
    """問題請求模型"""
    question: str = Field(..., description="使用者問題", min_length=1, max_length=500)
    
    class Config:
        schema_extra = {
            "example": {
                "question": "什麼是網路風險指數 (CRI)？"
            }
        }

class QuestionResponse(BaseModel):
    """問題回應模型"""
    question: str = Field(..., description="原始問題")
    answer: str = Field(..., description="AI 生成的答案")
    sources: List[str] = Field(default=[], description="來源文檔片段")
    status: str = Field(..., description="回應狀態")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "什麼是網路風險指數 (CRI)？",
                "answer": "網路風險指數 (CRI) 是一個量化組織整體安全風險的指標...",
                "sources": ["CREM 計算企業的網路風險指數 (CRI)，該指標基於整合各項資產和風險因子評分來量化組織的整體安全風險..."],
                "status": "success"
            }
        }

class HealthResponse(BaseModel):
    """健康檢查回應模型"""
    status: str = Field(..., description="服務狀態")
    message: str = Field(..., description="狀態訊息")
    version: str = Field(..., description="API 版本")

# 全域變數
qa_system = None

def get_qa_system() -> TrendMicroQASystem:
    """取得問答系統實例"""
    global qa_system
    if qa_system is None:
        try:
            knowledge_file = os.getenv("KNOWLEDGE_FILE", "knowledgebase.txt")
            qa_system = TrendMicroQASystem(knowledge_file=knowledge_file)
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
    """根路徑 - API 資訊"""
    return {
        "message": "趨勢科技資安報告智能問答 API",
        "version": os.getenv("API_VERSION", "1.0.0"),
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康檢查端點"""
    try:
        # 檢查問答系統是否正常
        qa_system = get_qa_system()
        
        # 執行簡單測試
        test_result = qa_system.ask_question("測試")
        
        return HealthResponse(
            status="healthy",
            message="服務正常運行",
            version=os.getenv("API_VERSION", "1.0.0")
        )
    except Exception as e:
        logger.error(f"健康檢查失敗: {str(e)}")
        raise HTTPException(status_code=503, detail=f"服務異常: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, qa_system: TrendMicroQASystem = Depends(get_qa_system)):
    """
    智能問答端點
    
    - **question**: 使用者問題
    - **returns**: AI 生成的答案和相關來源
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
    """取得範例問題列表"""
    examples = [
        "什麼是網路風險指數 (CRI)？",
        "2024年的整體平均 CRI 是多少？",
        "哪些行業的 CRI 最高？",
        "什麼是 CREM？",
        "如何降低企業的網路風險？",
        "什麼是 Trend Vision One？",
        "企業面臨的主要網路威脅有哪些？",
        "如何改善網路安全態勢？"
    ]
    return examples

@app.get("/info", response_model=Dict[str, Any])
async def get_api_info():
    """取得 API 詳細資訊"""
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "knowledge_base": os.getenv("KNOWLEDGE_FILE", "knowledgebase.txt"),
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