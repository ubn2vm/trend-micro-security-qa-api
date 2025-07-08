import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# LangChain 相關導入
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrendMicroQASystem:
    """趨勢科技資安報告智能問答系統"""
    
    def __init__(self, knowledge_file: str = None):
        """
        初始化問答系統
        
        Args:
            knowledge_file: 知識庫檔案路徑，如果為 None 則使用環境變數 KNOWLEDGE_FILE
        """
        # 如果沒有指定檔案，使用環境變數
        if knowledge_file is None:
            knowledge_file = os.getenv("KNOWLEDGE_FILE", "summary.txt")
        self.knowledge_file = knowledge_file
        self.vector_store = None
        self.qa_chain = None
        self.embeddings = None
        
        # 載入環境變數 - 先載入 config.env，再載入 .env（API Key）
        load_dotenv('../config/config.env')
        load_dotenv('../.env')
        
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
    
    def _load_knowledge_base(self) -> str:
        """載入知識庫檔案"""
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as file:
                content = file.read()
            logger.info(f"成功載入知識庫檔案: {self.knowledge_file}")
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到知識庫檔案: {self.knowledge_file}")
        except Exception as e:
            raise Exception(f"載入知識庫檔案時發生錯誤: {str(e)}")
    
    def _split_text(self, text: str) -> List[Document]:
        """將文本分割成適合向量化的片段"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )
        
        documents = text_splitter.create_documents([text])
        logger.info(f"文本已分割成 {len(documents)} 個片段")
        return documents
    
    def _create_vector_store(self, documents: List[Document]):
        """建立向量資料庫"""
        try:
            # 使用本地嵌入模型（避免 API 調用成本）
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # 建立 FAISS 向量資料庫
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            logger.info("向量資料庫建立成功")
            
        except Exception as e:
            logger.error(f"建立向量資料庫時發生錯誤: {str(e)}")
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
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True
            )
            logger.info("問答鏈建立成功")
        except Exception as e:
            logger.error(f"建立問答鏈時發生錯誤: {str(e)}")
            raise
    
    def _initialize_system(self):
        """初始化整個系統"""
        logger.info("開始初始化趨勢科技資安問答系統...")
        
        # 載入知識庫
        knowledge_text = self._load_knowledge_base()
        
        # 分割文本
        documents = self._split_text(knowledge_text)
        
        # 建立向量資料庫
        self._create_vector_store(documents)
        
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
            
            # 執行問答
            result = self.qa_chain({"query": question})
            
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

def main():
    """主函數 - 用於測試"""
    try:
        # 建立問答系統
        qa_system = TrendMicroQASystem()
        
        # 測試問題
        test_questions = [
            "什麼是網路風險指數 (CRI)？",
            "2024年的整體平均 CRI 是多少？",
            "哪些行業的 CRI 最高？",
            "什麼是 CREM？",
            "如何降低企業的網路風險？"
        ]
        
        print("=== 趨勢科技資安報告智能問答系統測試 ===\n")
        
        for question in test_questions:
            print(f"問題: {question}")
            result = qa_system.ask_question(question)
            print(f"答案: {result['answer']}")
            if result['sources']:
                print(f"來源: {result['sources'][0]}")
            print("-" * 80)
            
    except Exception as e:
        print(f"系統初始化失敗: {str(e)}")

if __name__ == "__main__":
    main() 