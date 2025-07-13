import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# LangChain 相關導入
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrendMicroQASystem:
    """趨勢科技資安報告智能問答系統（RAG 模式）"""
    
    # CREM 專業 Prompt 模板
    CREM_PROMPT_TEMPLATE = """
你是一個趨勢科技資安技術專家，專門回答關於 CREM (Cyber Risk Exposure Management) 的問題。

基於以下技術文檔內容，準確回答用戶的問題：

{context}

用戶問題: {question}

**重要提醒**：
- CREM (Cyber Risk Exposure Management) 是趨勢科技的網路風險暴露管理解決方案
- 請只基於提供的文檔內容回答，不要添加未提及的資訊

回答要求：
1. **直接回答**：不要有任何開場白、自我說明或資料來源聲明，直接進入重點
2. **概念準確性**：確保 CREM 的概念描述準確無誤
3. **專業術語**：正確使用技術術語
4. **誠實回答**：如果文檔中沒有相關資訊，請明確說明
5. **結構化回答**：提供清晰的摘要和詳細說明

回答格式：
**📋 摘要**
[2-3 句話的簡潔摘要，突出核心要點]

**🔍 詳細說明**
[詳細的技術說明和解釋]

**💡 關鍵要點**
- [要點1]
- [要點2]
- [要點3]

如果問題超出文檔範圍或文檔中沒有相關資訊，請誠實回答："根據提供的文檔內容，我無法找到關於 [具體問題] 的相關資訊。"

回答：
"""

    def __init__(self):
        """初始化問答系統（RAG 模式）"""
        # 載入環境變數 - 修正路徑問題
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        config_path = os.path.join(project_root, 'config', 'config.env')
        env_path = os.path.join(project_root, '.env')
        
        load_dotenv(config_path)
        load_dotenv(env_path)
        
        # 驗證 API Key
        self._validate_api_key()
        
        # 初始化系統
        self._initialize_system()
    
    def _validate_api_key(self):
        """驗證 Google API Key 和模型設定，並加強安全性提示"""
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # 基本存在性檢查
        if not api_key:
            logger.error("[安全警告] 未設定 GOOGLE_API_KEY，系統將無法連線 Gemini API！")
            raise ValueError("請設定 GOOGLE_API_KEY 環境變數，否則無法啟動問答服務。")
        
        # 移除空白字符
        api_key = api_key.strip()
        if not api_key:
            logger.error("[安全警告] GOOGLE_API_KEY 為空字串！")
            raise ValueError("GOOGLE_API_KEY 不能為空字串。")
        
        # 格式驗證
        if len(api_key) < 20:
            logger.error(f"[安全警告] GOOGLE_API_KEY 長度不足: {len(api_key)} 字符")
            raise ValueError("GOOGLE_API_KEY 長度不足，請檢查金鑰是否完整。")
        
        if not api_key.startswith("AI"):
            logger.error(f"[安全警告] GOOGLE_API_KEY 格式異常，應以 'AI' 開頭")
            raise ValueError("GOOGLE_API_KEY 格式不正確，Gemini API Key 應以 'AI' 開頭。")
        
        # 安全檢查
        if "demo" in api_key.lower():
            logger.warning("[安全警告] 偵測到 demo 測試金鑰，請勿在生產環境使用！")
        
        if "test" in api_key.lower():
            logger.warning("[安全警告] 偵測到測試金鑰，請確認是否為正式環境金鑰。")
        
        # 遮罩顯示（只顯示前4位和後4位）
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
        logger.info(f"Google API Key 驗證成功: {masked_key}")
        
        # 驗證模型設定
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
        temperature = os.getenv("GEMINI_TEMPERATURE", "0.1")
        max_tokens = os.getenv("GEMINI_MAX_TOKENS", "200")
        
        logger.info(f"Gemini 模型設定: {model_name}, 溫度: {temperature}, 最大 Token: {max_tokens}")
        
        # 驗證模型參數
        try:
            temp_val = float(temperature)
            if temp_val < 0 or temp_val > 2:
                logger.warning(f"[配置警告] 溫度值 {temp_val} 超出建議範圍 (0-2)")
        except ValueError:
            logger.error(f"[配置錯誤] 溫度值 '{temperature}' 不是有效數字")
            raise ValueError("GEMINI_TEMPERATURE 必須是有效數字")
        
        try:
            tokens_val = int(max_tokens)
            if tokens_val < 1 or tokens_val > 8192:
                logger.warning(f"[配置警告] 最大 Token 數 {tokens_val} 超出建議範圍 (1-8192)")
        except ValueError:
            logger.error(f"[配置錯誤] 最大 Token 數 '{max_tokens}' 不是有效整數")
            raise ValueError("GEMINI_MAX_TOKENS 必須是有效整數")
    
    def _create_vector_store(self):
        """載入 RAG 向量資料庫"""
        try:
            # 修正路徑處理邏輯
            current_dir = os.path.dirname(os.path.abspath(__file__))
            rag_vector_dir = os.getenv("RAG_VECTOR_DIR")
            
            if rag_vector_dir:
                # 如果環境變數設定了路徑，則相對於 core_app 目錄
                rag_vector_dir = os.path.join(current_dir, rag_vector_dir)
            else:
                # 預設路徑
                rag_vector_dir = os.path.join(current_dir, "rag", "vector_store", "crem_faiss_index")
            
            if not os.path.exists(rag_vector_dir):
                raise FileNotFoundError(f"RAG 向量資料庫不存在: {rag_vector_dir}")
            
            logger.info("載入 RAG 向量資料庫...")
            embedding_model = os.getenv("RAG_EMBEDDING_MODEL", 
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'}
            )
            self.vector_store = FAISS.load_local(rag_vector_dir, self.embeddings, allow_dangerous_deserialization=True)
            logger.info("成功載入 CREM RAG 向量資料庫")
            
        except Exception as e:
            logger.error(f"載入向量資料庫時發生錯誤: {str(e)}")
            raise
    
    def _create_qa_chain(self):
        """建立問答鏈"""
        try:
            # 從環境變數取得模型設定
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
            temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
            max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "200"))
            
            logger.info(f"使用 Gemini 模型: {model_name}, 溫度: {temperature}, 最大 Token: {max_tokens}")
            
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # 建立專業的 CREM Prompt 模板
            prompt = PromptTemplate(
                template=self.CREM_PROMPT_TEMPLATE,
                input_variables=["context", "question"]
            )
            
            # 建立問答鏈，使用自定義 Prompt
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={
                        "k": 5,  # 增加檢索數量
                        "score_threshold": 0.7  # 增加相關性閾值
                    }
                ),
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
            logger.info("CREM 專業問答鏈建立成功")
        except Exception as e:
            logger.error(f"建立問答鏈時發生錯誤: {str(e)}")
            raise
    
    def _initialize_system(self):
        """初始化整個系統"""
        logger.info("開始初始化趨勢科技資安問答系統（RAG 模式）...")
        
        # 載入向量資料庫
        self._create_vector_store()
        
        # 建立問答鏈
        self._create_qa_chain()
        
        logger.info("系統初始化完成！")
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        回答問題
        
        Args:
            question: 使用者問題
            
        Returns:
            包含答案和來源的字典
        """
        try:
            logger.info(f"收到問題: {question}")
            
            # 問題分類和預處理
            question_type = self._classify_question(question)
            processed_question = self._preprocess_question(question, question_type)
            
            # 執行問答
            result = self.qa_chain.invoke({"query": processed_question})
            
            # 提取答案和來源
            answer = result.get("result", "無法找到答案")
            source_documents = result.get("source_documents", [])
            
            # 格式化來源資訊
            sources = []
            for doc in source_documents:
                if hasattr(doc, 'page_content'):
                    # 取前100個字符作為來源摘要
                    content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                    sources.append(content_preview)
            
            response = {
                "question": question,
                "answer": answer,
                "sources": sources,
                "status": "success"
            }
            
            logger.info("問題回答完成")
            return response
            
        except Exception as e:
            logger.error(f"回答問題時發生錯誤: {str(e)}")
            return {
                "question": question,
                "answer": f"抱歉，處理您的問題時發生錯誤: {str(e)}",
                "sources": [],
                "status": "error"
            }

    def _classify_question(self, question: str) -> str:
        """分類問題類型"""
        question_lower = question.lower()
        if "cri" in question_lower and "crem" not in question_lower:
            return "CRI_ONLY"
        elif "crem" in question_lower and "cri" not in question_lower:
            return "CREM_ONLY"
        elif "cri" in question_lower and "crem" in question_lower:
            return "BOTH"
        else:
            return "GENERAL"

    def _preprocess_question(self, question: str, question_type: str) -> str:
        """預處理問題"""
        if question_type == "CRI_ONLY":
            return f"關於 CRI (Cyber Risk Index) 的問題：{question}"
        elif question_type == "CREM_ONLY":
            return f"關於 CREM (Cyber Risk Exposure Management) 的問題：{question}"
        else:
            return question

def main():
    """主函數 - 用於測試"""
    try:
        # 建立問答系統
        qa_system = TrendMicroQASystem()
        
        # 測試問題
        test_questions = [
            "什麼是 CREM？它主要解決什麼問題？",
            "CREM 相比傳統安全方案有什麼主要優勢",
            "CREM 的完整生命週期包含哪些步驟？",
            "CREM 如何整合不同的安全領域？"
        ]
        
        logger.info("=== 趨勢科技智能問答系統測試 ===")
        
        for question in test_questions:
            logger.info(f"問題: {question}")
            result = qa_system.ask_question(question)
            logger.info(f"答案: {result['answer']}")
            if result['sources']:
                logger.info(f"來源: {result['sources'][0]}")
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"系統初始化失敗: {str(e)}")

if __name__ == "__main__":
    main() 