import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

# LangChain 相關導入 - 重新加入LLM支援
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# 添加RAG模組路徑
import sys
rag_dir = Path(__file__).parent / "rag"
sys.path.append(str(rag_dir))

# 導入現有的RAG系統
from tools.unified_query_engine import UnifiedQueryEngine

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrendMicroQASystem:
    """趨勢科技資安報告智能問答系統（完整RAG + LLM模式）"""
    
    # 動態 CREM Prompt 模板
    ENHANCED_CREM_PROMPT_TEMPLATE = """
你是一個趨勢科技資安技術專家，專門回答關於 CREM (Cyber Risk Exposure Management) 和網路安全的問題。

系統資訊：您正在使用一個完整的知識庫系統，基於檢索到的相關資料進行分析。

基於以下檢索到的相關資料，準確回答用戶的問題：

=== 檢索結果 ({result_count}個結果) ===
{context}

=== 用戶問題 ===
{question}

=== 回答指導原則 ===
1. **充分利用檢索結果**: 基於提供的{result_count}個檢索結果進行全面分析
2. **數據洞察判斷**: 檢索結果中是否包含明確的數字、統計數據、百分比、排名、圖表數據等具體量化資訊
3. **專業術語準確**: 正確使用 CREM、CRI、Trend Vision One 等專業術語
4. **結構化回答**: 提供清晰的摘要和詳細說明

=== 回答格式要求 ===
**📋 摘要**
[簡潔摘要，突出核心要點]

**🔍 詳細分析**
[基於檢索結果的詳細分析和解釋]

**💡 關鍵發現**
- [要點1]
- [要點2] 
- [要點3]

**📊 數據洞察**
[注意：只有當檢索結果明確包含數字統計、百分比、排名、圖表、數據表格等量化資訊時，才寫出此部分。如果檢索結果主要是概念說明、功能描述、定義解釋等文字內容，請直接跳過此部分，不要寫「📊 數據洞察」標題]

注意：不要在回答中包含資料來源部分，系統會自動添加完整的來源信息。

請開始回答：
"""

    def __init__(self):
        """初始化問答系統（整合現有RAG + LLM）"""
        # 載入環境變數
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        config_path = os.path.join(project_root, 'config', 'config.env')
        env_path = os.path.join(project_root, '.env')
        
        load_dotenv(config_path)
        load_dotenv(env_path)
        
        # 驗證 API Key（可選）
        self.llm_available = self._check_api_key()
        
        # 初始化現有RAG系統
        self._initialize_rag_system()
        
        # 初始化 LLM（如果可用）
        if self.llm_available:
            self._initialize_llm()
    
    def _check_api_key(self) -> bool:
        """檢查 Google API Key（非強制）"""
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key or len(api_key.strip()) < 20:
            logger.warning("⚠️ GOOGLE_API_KEY 未設定或無效，將使用格式化回答模式")
            return False
        
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
        logger.info(f"✅ Google API Key 已設定: {masked_key}")
        return True
    
    def _initialize_rag_system(self):
        """初始化RAG系統"""
        try:
            logger.info("正在初始化RAG系統...")
            
            # 使用現有向量資料庫
            current_dir = Path(__file__).parent
            vector_dir = current_dir / "rag" / "vector_store" / "crem_faiss_index"
            
            if not vector_dir.exists():
                raise FileNotFoundError(f"RAG 向量資料庫不存在: {vector_dir}")
            
            # 初始化統一查詢引擎
            self.rag_engine = UnifiedQueryEngine(str(vector_dir))
            
            if not self.rag_engine.load_vector_db():
                raise Exception("無法載入向量資料庫")
            
            # 動態獲取系統統計
            stats = self.rag_engine.get_query_stats()
            self.vector_count = stats.get('vector_count', 0)
            
            # 動態獲取表格數量
            self.table_count = self._get_table_count()
            self.estimated_text_count = self.vector_count - self.table_count
            
            logger.info("✅ RAG系統初始化成功")
            logger.info(f"📊 向量資料庫統計: 總計{self.vector_count}個向量")
            logger.info(f"📊 估算組成: ~{self.estimated_text_count}個文本向量 + {self.table_count}個表格向量")
            
        except Exception as e:
            logger.error(f"RAG系統初始化失敗: {str(e)}")
            raise
    
    def _get_table_count(self) -> int:
        """動態獲取表格數量"""
        try:
            table_texts_file = Path(__file__).parent / "rag" / "data" / "processed" / "table_texts.json"
            if table_texts_file.exists():
                import json
                with open(table_texts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('total_tables', 0)
        except Exception as e:
            logger.warning(f"無法讀取表格數量: {e}")
        return 0
    
    def _initialize_llm(self):
        """初始化LLM（如果API Key可用）"""
        try:
            # 從環境變數取得模型設定
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
            temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.05"))
            max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "300"))
            
            logger.info(f"🤖 初始化 Gemini 模型: {model_name}")
            logger.info(f"⚙️ 溫度: {temperature}, 最大 Token: {max_tokens}")
            
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # 建立 Prompt 模板
            self.prompt_template = PromptTemplate(
                template=self.ENHANCED_CREM_PROMPT_TEMPLATE,
                input_variables=["context", "question", "result_count"]
            )
            
            logger.info("✅ LLM 初始化成功")
            
        except Exception as e:
            logger.error(f"LLM 初始化失敗: {str(e)}")
            self.llm_available = False
    
    def ask_question(self, question: str, filter_type: str = "all", k: int = 5) -> Dict[str, Any]:
        """
        回答問題（完整RAG + LLM模式）
        
        Args:
            question: 使用者問題
            filter_type: 查詢類型 ("all", "text", "table")  
            k: 返回結果數量
            
        Returns:
            包含答案和來源的字典
        """
        try:
            logger.info(f"收到問題: {question} (類型: {filter_type})")
            
            # 步驟1: 使用現有RAG檢索
            detected_filter = self._detect_query_type(question, filter_type)
            results = self.rag_engine.query(
                question=question,
                k=k,
                filter_type=detected_filter
            )
            
            if not results:
                return {
                    "question": question,
                    "answer": f"抱歉，我無法在知識庫（包含{self.vector_count}個向量）中找到相關資訊來回答您的問題。建議您：\n1. 嘗試使用不同的關鍵詞\n2. 提出更具體的問題\n3. 檢查問題是否與網路安全、風險管理相關",
                    "sources": [],
                    "citations": [],  # ✅ 添加空的citations
                    "status": "no_results",
                    "result_count": 0,
                    "text_results": 0,
                    "table_results": 0,
                    "generation_method": "fallback",
                    "system_type": "TrendMicroQASystem",  # ✅ 新增 system_type
                    "llm_available": self.llm_available,   # ✅ 新增 llm_available
                    "vector_db_size": self.vector_count
                }
            
            # 步驟2: 構建context
            context_parts = []
            text_count = 0
            table_count = 0
            
            for i, result in enumerate(results):
                if result.content_type == "table":
                    table_count += 1
                    context_parts.append(f"[表格資料 {i+1}] 來源: {result.source}\n{result.content}")
                else:
                    text_count += 1
                    context_parts.append(f"[文本資料 {i+1}] 來源: {result.source}\n{result.content}")
            
            context = "\n\n".join(context_parts)
            
            # 步驟3: LLM生成答案（如果可用）
            if self.llm_available and hasattr(self, 'llm'):
                try:
                    prompt = self.prompt_template.format(
                        context=context, 
                        question=question,
                        result_count=len(results)
                    )
                    response = self.llm.invoke(prompt)
                    answer = response.content if hasattr(response, 'content') else str(response)
                    generation_method = "llm_generated"
                    
                    logger.info("✅ LLM 答案生成成功")
                    
                except Exception as llm_error:
                    logger.error(f"LLM 生成失敗，回退到格式化答案: {llm_error}")
                    answer = self._generate_structured_answer(results, question)
                    generation_method = "fallback_structured"
            else:
                # 使用結構化格式化答案
                answer = self._generate_structured_answer(results, question)
                generation_method = "structured_formatted"
            
            # 步驟4: 提取來源資訊和引用內容
            sources = []
            citations = []

            logger.info(f"🔍 Debug: 準備處理 {len(results)} 個檢索結果")

            for i, result in enumerate(results[:3]):
                # 確保confidence_score是Python float類型
                confidence_value = float(result.confidence_score) if hasattr(result.confidence_score, 'item') else float(result.confidence_score)
                
                source_info = f"[{result.content_type.upper()}] {result.source} (信心度: {confidence_value:.2f})"
                sources.append(source_info)
                
                # 添加引用內容 - 所有值都轉換為Python原生類型
                citation = {
                    "rank": int(i + 1),
                    "source": str(result.source),
                    "content_type": str(result.content_type),
                    "content": str(result.content),
                    "confidence": confidence_value  # Python float
                }
                citations.append(citation)
                logger.info(f"🔍 Debug: 添加citation {i+1}: {result.source} - 內容長度: {len(result.content)} - 信心度類型: {type(confidence_value)}")

            logger.info(f"🔍 Debug: 總共創建了 {len(citations)} 個citations")

            response = {
                "question": question,
                "answer": answer,
                "sources": sources,
                "citations": citations,  # ✅ 確保包含citations
                "status": "success",
                "result_count": len(results),
                "text_results": text_count,
                "table_results": table_count,
                "filter_type": detected_filter,
                "generation_method": generation_method,
                "system_type": "TrendMicroQASystem",
                "llm_available": self.llm_available,
                "vector_db_size": self.vector_count
            }
            
            logger.info(f"🔍 Debug: 響應中包含 {len(response.get('citations', []))} 個citations")
            logger.info(f"問題回答完成: 找到{len(results)}個結果 (文本:{text_count}, 表格:{table_count})")
            return response
            
        except Exception as e:
            logger.error(f"回答問題時發生錯誤: {str(e)}")
            return {
                "question": question,
                "answer": f"抱歉，處理您的問題時發生錯誤: {str(e)}",
                "sources": [],
                "citations": [],  # ✅ 添加空的citations
                "status": "error",
                "result_count": 0,
                "text_results": 0,
                "table_results": 0,
                "generation_method": "error",
                "system_type": "TrendMicroQASystem",  # ✅ 新增 system_type
                "llm_available": self.llm_available,   # ✅ 新增 llm_available
                "vector_db_size": getattr(self, 'vector_count', 0)
            }
    
    def _detect_query_type(self, question: str, default_filter: str) -> str:
        """智能檢測查詢類型 - 優化版"""
        if default_filter != "all":
            return default_filter
            
        question_lower = question.lower()
        
        # 表格相關關鍵詞 - 數據導向
        table_keywords = [
            # 排行榜類
            "前10", "top 10", "前十", "前5", "top 5", "排行", "排名", "ranking",
            # 統計數據類
            "統計", "數據", "表格", "statistics", "data", "table", "chart",
            # 比較分析類
            "比較", "對比", "分析", "comparison", "analysis", "versus", "vs",
            # 列表類
            "list", "清單", "列表", "項目",
            # 特定風險事件
            "risky events", "風險事件", "威脅事件", "security incidents",
            # 數量詞
            "多少", "幾個", "how many", "count"
        ]
        
        # 文本相關關鍵詞 - 概念和說明導向
        text_keywords = [
            # 政策指導類
            "政策", "policy", "policies", "規範", "準則", "guidelines",
            # 建議諮詢類  
            "建議", "recommendation", "recommendations", "suggest", "advice",
            # 策略規劃類
            "策略", "戰略", "strategy", "strategies", "approach", "framework",
            # 方法步驟類
            "方法", "步驟", "流程", "method", "methods", "process", "procedure",
            # 詢問解釋類
            "如何", "怎麼", "怎樣", "how to", "how can", "how do", "how does",
            # 定義概念類
            "什麼是", "什麼叫", "定義", "what is", "what are", "define", "definition",
            # 解釋說明類
            "解釋", "說明", "介紹", "explain", "explanation", "describe", "overview",
            # 原因分析類
            "為什麼", "原因", "why", "because", "reason", "cause",
            # 功能作用類
            "功能", "作用", "用途", "function", "purpose", "benefit", "advantage",
            # 實施執行類
            "實施", "執行", "部署", "implement", "deploy", "execute",
            # 最佳實踐類
            "最佳", "最好", "優化", "best", "optimal", "improve", "enhancement"
        ]
        
        # 混合查詢關鍵詞 - 可能需要表格+文本結合
        hybrid_keywords = [
            "趨勢", "現狀", "狀況", "情況", "trend", "current", "situation", "status",
            "評估", "分析報告", "assessment", "evaluation", "report"
        ]
        
        # 檢查表格關鍵詞（優先級最高）
        if any(keyword in question_lower for keyword in table_keywords):
            return "table"
            
        # 檢查文本關鍵詞
        if any(keyword in question_lower for keyword in text_keywords):
            return "text"
            
        # 檢查混合關鍵詞
        if any(keyword in question_lower for keyword in hybrid_keywords):
            return "all"
            
        # 預設混合查詢
        return "all"
    
    def _generate_structured_answer(self, results: List, question: str) -> str:
        """生成結構化答案（當LLM不可用時）"""
        if not results:
            return "抱歉，我無法找到相關資訊。"
        
        best_result = results[0]
        
        # 根據結果類型生成不同格式的答案
        if best_result.content_type == "table":
            if any(keyword in question.lower() for keyword in ["前10", "top 10", "排行", "前十"]):
                answer = f"📊 **根據知識庫的統計資料：**\n\n{best_result.content}"
                
                if len(results) > 1:
                    answer += f"\n\n**相關補充資訊：**\n{results[1].content[:200]}..."
                
                # ✅ 移除資料來源部分
                return answer
        
        # 一般結構化回答格式
        answer = f"**📋 摘要**\n基於知識庫檢索結果：\n\n{best_result.content[:400]}"
        
        if len(best_result.content) > 400:
            answer += "..."
        
        # 添加相關資訊
        if len(results) > 1:
            second_result = results[1]
            answer += f"\n\n**🔍 相關資訊**\n{second_result.content[:200]}"
            if len(second_result.content) > 200:
                answer += "..."
        
        # ✅ 移除資料來源部分，系統會自動添加
        return answer
    
    def get_system_stats(self) -> Dict[str, Any]:
        """獲取系統統計資訊"""
        if hasattr(self, 'rag_engine'):
            stats = self.rag_engine.get_query_stats()
            current_vector_count = stats.get('vector_count', 0)
            
            return {
                "system_type": "TrendMicroQASystem",  # ✅ 修復：使用正確的系統類型
                "system_description": f"完整RAG+LLM系統 ({current_vector_count}向量)",  # 描述移到新欄位
                "vector_count": current_vector_count,
                "estimated_text_vectors": self.estimated_text_count,
                "table_vectors": self.table_count,
                "total_queries": stats.get('total_queries', 0),
                "text_results": stats.get('text_results', 0),
                "table_results": stats.get('table_results', 0),
                "last_query_time": stats.get('last_query_time'),
                "llm_available": self.llm_available,
                "llm_model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite") if self.llm_available else "N/A",
                "capabilities": [
                    f"{current_vector_count}個向量完整檢索 (~{self.estimated_text_count}文本 + {self.table_count}表格)",
                    "Gemini LLM自然語言生成" if self.llm_available else "結構化格式回答",
                    "多語言支援(中文/英文)",
                    "智能查詢類型檢測",
                    "表格和文本混合查詢",
                    "置信度評估",
                    "來源追蹤"
                ]
            }
        else:
            return {
                "system_type": "TrendMicroQASystem",
                "system_description": "系統未初始化",
                "vector_count": 0,
                "estimated_text_vectors": 0,
                "table_vectors": 0,
                "total_queries": 0,
                "text_results": 0,
                "table_results": 0,
                "last_query_time": None,
                "llm_available": False,
                "llm_model": "N/A",
                "capabilities": []
            }
    
    def test_system_integrity(self) -> Dict[str, Any]:
        """測試系統完整性"""
        try:
            # 測試RAG檢索
            test_results = self.rag_engine.query("CREM", k=1)
            rag_status = "success" if test_results else "no_results"
            
            # 測試LLM（如果可用）
            llm_status = "not_available"
            if self.llm_available and hasattr(self, 'llm'):
                try:
                    test_response = self.llm.invoke("什麼是CREM？請簡短回答。")
                    llm_status = "success" if test_response else "failed"
                except:
                    llm_status = "failed"
            
            stats = self.rag_engine.get_query_stats()
            current_vector_count = stats.get('vector_count', 0)
            
            return {
                "overall_status": "healthy",
                "rag_status": rag_status,
                "llm_status": llm_status,
                "vector_count": current_vector_count,
                "table_count": self.table_count,
                "estimated_text_count": self.estimated_text_count,
                "message": f"系統運行正常，包含{current_vector_count}個向量"
            }
        except Exception as e:
            return {
                "overall_status": "error",
                "message": f"系統測試失敗: {str(e)}"
            }

def main():
    """主函數 - 測試完整系統"""
    try:
        # 建立問答系統
        qa_system = TrendMicroQASystem()
        
        # 測試系統完整性
        integrity_test = qa_system.test_system_integrity()
        logger.info(f"系統完整性測試: {integrity_test['overall_status']}")
        logger.info(f"向量統計: 總計{integrity_test.get('vector_count', 'unknown')}個")
        logger.info(f"組成: ~{integrity_test.get('estimated_text_count', 'unknown')}文本 + {integrity_test.get('table_count', 'unknown')}表格")
        
        # 測試問題
        test_questions = [
            ("前10大風險事件有哪些？請詳細分析", "all"),
            ("什麼是CREM？它如何幫助企業管理網路風險？", "text"),
            ("統計資料顯示的主要威脅有哪些？", "table"),
            ("risky cloud app access相關的表格數據", "table"),
            ("企業安全政策的最佳實踐建議", "text")
        ]
        
        logger.info("=== 趨勢科技完整RAG+LLM系統測試 ===")
        
        for question, filter_type in test_questions:
            logger.info(f"問題: {question} (類型: {filter_type})")
            result = qa_system.ask_question(question, filter_type=filter_type)
            logger.info(f"狀態: {result['status']}")
            logger.info(f"生成方式: {result.get('generation_method', 'unknown')}")
            logger.info(f"LLM可用: {result.get('llm_available', False)}")
            logger.info(f"答案預覽: {result['answer'][:150]}...")
            if result['sources']:
                logger.info(f"來源: {result['sources'][0]}")
            logger.info(f"結果統計: {result.get('result_count', 0)}個結果 "
                       f"(文本:{result.get('text_results', 0)}, 表格:{result.get('table_results', 0)})")
            logger.info("-" * 80)
            
        # 顯示系統統計
        stats = qa_system.get_system_stats()
        logger.info("=== 系統統計 ===")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
            
    except Exception as e:
        logger.error(f"系統初始化或測試失敗: {str(e)}")
        logger.error("建議檢查：")
        logger.error("1. 向量資料庫檔案是否存在且完整")
        logger.error("2. GOOGLE_API_KEY 設定（可選，不影響基本功能）")
        logger.error("3. 網路連接（僅LLM功能需要）")

if __name__ == "__main__":
    main() 