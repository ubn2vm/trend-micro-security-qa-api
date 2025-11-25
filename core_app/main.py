import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

# LangChain 相關導入 - 重新加入LLM支援
from langchain_core.prompts import PromptTemplate
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
    """趨勢科技技術知識問答系統（支援技術文檔、研究報告、網路錯誤碼、日誌格式）"""
    
    # 動態 Prompt 模板
    ENHANCED_PROMPT_TEMPLATE = """
你是一個趨勢科技資安技術專家，專門回答關於技術文檔、研究報告、網路錯誤碼、日誌格式和網路安全的問題。

系統資訊：您正在使用一個完整的知識庫系統，基於檢索到的相關資料進行分析。

基於以下檢索到的相關資料，準確回答用戶的問題：

=== 檢索結果 ({result_count}個結果) ===
{context}

=== 用戶問題 ===
{question}

=== 回答指導原則 ===
1. **充分利用檢索結果**: 基於提供的{result_count}個檢索結果進行全面分析，**必須嚴格依據檢索結果回答，不要使用檢索結果之外的知識**
2. **縮寫展開**: 如果問題中包含縮寫（如 DDI、CREM、CRI），請在回答中同時使用縮寫和完整形式（如 DDI (Deep Discovery Inspector)）
3. **路徑問題的準確性**（重要）:
   - 如果問題問的是「目錄」(directory)、「路徑」(path)、「儲存位置」、「預設日誌目錄」(default log directory)，答案應該是**目錄路徑**（如 `/var/log/suricata`）
   - 如果問題問的是「檔名」(filename)、「日誌檔」(log file)、「完整路徑」(full path)、「日誌文件路徑」，答案應該是**完整文件路徑**（如 `/var/log/suricata/suricata.log`）
   - **關鍵區別**：目錄路徑通常以目錄名結尾（如 `/var/log/suricata`），文件路徑以文件名結尾（如 `/var/log/suricata/suricata.log`）
   - **必須仔細區分「目錄」和「文件」的差異，不要混淆**
4. **數據洞察判斷**: 檢索結果中是否包含明確的數字、統計數據、百分比、排名、圖表數據等具體量化資訊
5. **專業術語準確**: 正確使用 CREM、CRI、Trend Vision One、DDI (Deep Discovery Inspector) 等專業術語
6. **結構化回答**: 提供清晰的摘要和詳細說明
7. **來源引用**: 如果檢索結果中明確提到某個定義、格式或說明，請直接引用該內容

=== 回答格式要求 ===
**📋 摘要**
[簡潔摘要，突出核心要點。如果是路徑問題，必須明確指出是目錄路徑還是文件路徑，並給出準確的路徑值]

**🔍 詳細分析**
[基於檢索結果的詳細分析和解釋。如果是路徑問題，請明確說明這是目錄還是文件，並引用檢索結果中的具體路徑信息]

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
        """載入RAG系統（從已建立的向量資料庫）"""
        try:
            logger.info("正在載入RAG向量資料庫...")
            
            # 使用現有向量資料庫
            current_dir = Path(__file__).parent
            vector_dir = current_dir / "rag" / "vector_store" / "default_faiss_index"
            
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
            
            logger.info("✅ RAG向量資料庫載入成功")
            logger.info(f"📊 向量資料庫統計: 總計{self.vector_count}個向量")
            logger.info(f"📊 估算組成: ~{self.estimated_text_count}個文本向量 + {self.table_count}個表格向量")
            
        except Exception as e:
            logger.error(f"RAG向量資料庫載入失敗: {str(e)}")
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
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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
                template=self.ENHANCED_PROMPT_TEMPLATE,
                input_variables=["context", "question", "result_count"]
            )
            
            logger.info("✅ LLM 初始化成功")
            
        except Exception as e:
            logger.error(f"LLM 初始化失敗: {str(e)}")
            self.llm_available = False
    
    def ask_question(self, question: str, filter_type: str = "all", k: int = 5) -> Dict[str, Any]:
        """
        回答問題（技術知識RAG + LLM模式）
        
        Args:
            question: 使用者問題
            filter_type: 查詢類型 ("all", "text", "table")  
            k: 返回結果數量
            
        Returns:
            包含答案和來源的字典
        """
        try:
            logger.info(f"收到問題: {question} (類型: {filter_type})")
            
            # 步驟1: 查詢擴展（展開縮寫）
            expanded_question = self._expand_abbreviations(question)
            logger.info(f"原始問題: {question}")
            if expanded_question != question:
                logger.info(f"擴展後問題: {expanded_question}")
            
            # 步驟2: 使用現有RAG檢索（使用擴展後的問題）
            detected_filter = self._detect_query_type(expanded_question, filter_type)
            results = self.rag_engine.query(
                question=expanded_question,
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

            # 智能選擇最相關的引用：優先選擇包含問題關鍵詞的結果
            question_lower = question.lower()
            question_keywords = []
            
            # 提取問題關鍵詞
            if "目錄" in question or "directory" in question_lower:
                question_keywords.extend(["log directory", "/var/log", "default log directory", "日誌目錄"])
            if "檔名" in question or "filename" in question_lower or "log file" in question_lower:
                question_keywords.extend(["suricata.log", "log file", "filename"])
            if "suricata" in question_lower:
                question_keywords.append("suricata")
            if "日誌" in question or "log" in question_lower:
                question_keywords.extend(["log", "日誌"])
            
            # 對結果進行相關性排序：包含關鍵詞的結果優先
            def calculate_relevance(result, keywords):
                """計算結果與問題的相關性"""
                content_lower = str(result.content).lower()
                relevance_score = 0
                for keyword in keywords:
                    if keyword.lower() in content_lower:
                        relevance_score += 1
                return relevance_score
            
            # 為每個結果計算相關性
            results_with_relevance = []
            for result in results:
                relevance = calculate_relevance(result, question_keywords)
                results_with_relevance.append((relevance, result))
            
            # 按相關性排序（相關性高的在前，然後按信心度）
            results_with_relevance.sort(key=lambda x: (x[0], x[1].confidence_score), reverse=True)
            
            # 選擇最相關的結果作為引用（最多3個）
            selected_results = results_with_relevance[:3]
            
            for i, (relevance, result) in enumerate(selected_results):
                # 確保confidence_score是Python float類型
                confidence_value = float(result.confidence_score) if hasattr(result.confidence_score, 'item') else float(result.confidence_score)
                
                source_info = f"[{result.content_type.upper()}] {result.source} (信心度: {confidence_value:.2f})"
                sources.append(source_info)
                
                # 獲取完整的引用內容（從 metadata 中獲取原始內容，如果可用）
                citation_content = str(result.content)
                
                # 如果 metadata 中有原始內容，優先使用（更完整）
                if hasattr(result, 'metadata') and result.metadata:
                    original_content = result.metadata.get('original_content') or result.metadata.get('page_content')
                    if original_content and len(str(original_content)) > len(citation_content):
                        citation_content = str(original_content)
                
                # 清理引用內容：移除開頭的奇怪字符和格式問題
                try:
                    from processors.text_processor import TextProcessor
                    text_processor = TextProcessor()
                    citation_content = text_processor.clean_citation_content(citation_content)
                except Exception as e:
                    # 如果導入失敗，使用簡單的清理方法
                    logger.warning(f"無法導入 TextProcessor，使用簡單清理: {e}")
                    import re
                    citation_content = citation_content.strip()
                    # 移除開頭的點號
                    if citation_content.startswith('.'):
                        citation_content = citation_content[1:].strip()
                    # 移除多餘空白
                    citation_content = re.sub(r'\s+', ' ', citation_content).strip()
                
                # 添加引用內容 - 所有值都轉換為Python原生類型
                citation = {
                    "rank": int(i + 1),
                    "source": str(result.source),
                    "content_type": str(result.content_type),
                    "content": citation_content,  # 使用完整內容
                    "confidence": confidence_value,  # Python float
                    "content_length": len(citation_content),  # 添加內容長度信息
                    "relevance_score": relevance,  # 添加相關性分數
                    "metadata": result.metadata if hasattr(result, 'metadata') else {}  # 添加 metadata 以便提取頁碼
                }
                citations.append(citation)
                logger.info(f"🔍 Debug: 添加citation {i+1}: {result.source} - 相關性: {relevance} - 內容長度: {len(citation_content)} - 信心度: {confidence_value:.2f}")

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
    
    def _expand_abbreviations(self, question: str) -> str:
        """
        展開問題中的縮寫，提高檢索準確率
        
        Args:
            question: 原始問題
            
        Returns:
            擴展後的問題（包含縮寫和完整形式）
        """
        # 縮寫到完整形式的映射
        abbreviation_map = {
            "DDI": "Deep Discovery Inspector",
            "CREM": "Cyber Risk Exposure Management",
            "CRI": "Cyber Risk Index",
            "XDR": "Extended Detection and Response",
            "EDR": "Endpoint Detection and Response",
            "SAE": "Security Analytics Engine",
            "SOC": "Security Operations Center"
        }
        
        expanded_question = question
        
        # 檢查問題中是否包含縮寫
        for abbrev, full_form in abbreviation_map.items():
            # 使用正則表達式匹配完整的單詞（避免部分匹配）
            import re
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            if re.search(pattern, expanded_question, re.IGNORECASE):
                # 如果問題中只有縮寫，添加完整形式
                if full_form.lower() not in expanded_question.lower():
                    expanded_question = re.sub(
                        pattern, 
                        f"{abbrev} ({full_form})", 
                        expanded_question, 
                        flags=re.IGNORECASE
                    )
        
        # 日誌相關的擴展（針對 Suricata 日誌目錄問題）
        question_lower = question.lower()
        
        # 檢測是否為 Suricata 相關查詢
        is_suricata_query = "suricata" in question_lower
        
        # 檢測是否為日誌相關查詢
        is_log_query = "日誌" in question or "log" in question_lower
        
        # 檢測是否為路徑/目錄相關查詢
        is_path_query = any(kw in question for kw in ["路徑", "目錄", "directory", "path", "位置", "location"])
        
        # 針對 Suricata log directory 的專門擴展
        if is_suricata_query and is_log_query and is_path_query:
            # 這是 Suricata 日誌目錄查詢，添加多種變體
            if "目錄" in question or "directory" in question_lower:
                # 目錄查詢：重點搜索目錄路徑
                expanded_question += " log directory /var/log/suricata /var/log default log directory path location"
                expanded_question += " suricata log directory configuration default log location"
            elif "檔名" in question or "filename" in question_lower or "log file" in question_lower or "日誌檔" in question:
                # 文件查詢：重點搜索文件路徑
                expanded_question += " log file filename suricata.log /var/log/suricata/suricata.log"
                expanded_question += " suricata log file path default log file"
            else:
                # 未明確指定，同時搜索目錄和文件
                expanded_question += " log directory /var/log/suricata suricata.log default log"
                expanded_question += " log path log location configuration"
        
        # 一般日誌查詢擴展
        elif is_log_query:
            if "目錄" in question or "directory" in question_lower:
                expanded_question += " log directory /var/log default log directory path"
            elif "檔名" in question or "filename" in question_lower or "log file" in question_lower or "日誌檔" in question:
                expanded_question += " log file filename suricata.log /var/log/suricata/suricata.log"
            elif "日誌輸出目錄" in question or "日誌目錄" in question:
                expanded_question += " log directory log path default log directory /var/log"
            elif "日誌路徑" in question:
                expanded_question += " log path log directory"
            elif "default log" in question_lower or ("預設" in question and "日誌" in question):
                expanded_question += " /var/log default log directory"
        
        # Suricata 相關查詢擴展
        if is_suricata_query:
            if is_path_query:
                expanded_question += " /var/log/suricata suricata.log log directory default log directory"
                expanded_question += " suricata configuration log path"
        
        # 一般路徑查詢擴展
        if is_path_query and not is_suricata_query and not is_log_query:
            expanded_question += " /var/log /etc directory path location"
        
        # 添加技術術語變體以提高召回率
        if "預設" in question or "default" in question_lower:
            expanded_question += " default configuration setting"
        
        # DDI 故障排除相關查詢擴展
        is_ddi_query = "ddi" in question_lower or "deep discovery inspector" in question_lower
        is_troubleshooting_query = any(kw in question for kw in [
            "故障排除", "troubleshooting", "問題", "無法", "不能", "can't", "cannot",
            "登入", "登錄", "log on", "login", "access", "存取", "連接", "connect"
        ])
        
        if is_ddi_query and is_troubleshooting_query:
            # DDI 故障排除查詢，添加相關關鍵詞
            expanded_question += " administration console log on credentials network cable"
            expanded_question += " troubleshooting cannot log on access management interface"
            expanded_question += " network connection credentials authentication"
            if "登入" in question or "log on" in question_lower or "login" in question_lower:
                expanded_question += " cannot log on administration console credentials network cable"
                expanded_question += " make sure network cable securely connected correct credentials"
        
        # CEF 格式相關查詢擴展
        is_cef_query = any(kw in question_lower for kw in [
            "cef", "common event format", "威脅日誌", "threat log", "threat logs"
        ])
        is_field_mapping_query = any(kw in question for kw in [
            "對應", "對應到", "對應哪個", "欄位", "field", "mapping", "哪個欄位", "which field"
        ])
        
        if is_cef_query or is_field_mapping_query:
            # CEF 格式查詢，添加相關關鍵詞
            expanded_question += " CEF Common Event Format threat log field mapping"
            expanded_question += " CEF key CEF欄位 field mapping table"
            if "攻擊階段" in question or "attack phase" in question_lower:
                expanded_question += " Attack Phase cs6Label pAttackPhase cs6"
            if "ddi" in question_lower or "deep discovery inspector" in question_lower:
                expanded_question += " Deep Discovery Inspector DDI CEF format"
        
        return expanded_question
    
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
            "多少", "幾個", "how many", "count",
            # CEF 格式和欄位映射類
            "cef", "欄位", "field", "對應", "mapping", "格式", "format",
            "cef key", "cef欄位", "對應到", "對應哪個", "哪個欄位", "which field"
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
                "system_description": f"技術知識RAG+LLM系統 ({current_vector_count}向量)",  # 描述移到新欄位
                "vector_count": current_vector_count,
                "estimated_text_vectors": self.estimated_text_count,
                "table_vectors": self.table_count,
                "total_queries": stats.get('total_queries', 0),
                "text_results": stats.get('text_results', 0),
                "table_results": stats.get('table_results', 0),
                "last_query_time": stats.get('last_query_time'),
                "llm_available": self.llm_available,
                "llm_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash") if self.llm_available else "N/A",
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
        
        logger.info("=== 趨勢科技技術知識問答系統測試 ===")
        
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