"""
向量資料庫建構模組
- 從已分塊的 JSON 檔案建立 FAISS 向量資料庫
- 支援 CREM、DDI、Suricata 等多種技術文檔
- 使用 HuggingFace Embeddings 進行向量化
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDatabaseBuilder:
    """
    向量資料庫建構器
    從已分塊的 JSON 檔案建立 FAISS 向量資料庫
    
    支援多種技術文檔類型：CREM、DDI、Suricata、網路錯誤碼等
    """
    def __init__(self, chunk_path: str, vector_dir: str):
        self.chunk_path = Path(chunk_path)
        self.vector_dir = Path(vector_dir)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.documents: List[Document] = []
        self.vector_db = None

    def load_chunks(self) -> List[Document]:
        """載入已分塊的 JSON 檔案"""
        logger.info(f"讀取分塊檔案: {self.chunk_path}")
        with open(self.chunk_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        self.documents = [
            Document(page_content=chunk['content'], metadata=chunk['metadata'])
            for chunk in chunks
        ]
        logger.info(f"共載入 {len(self.documents)} 個分塊")
        return self.documents

    def build_vector_db(self) -> Any:
        """建立 FAISS 向量資料庫"""
        if not self.documents:
            self.load_chunks()
        logger.info("開始向量化...")
        self.vector_db = FAISS.from_documents(self.documents, self.embeddings)
        logger.info("向量化完成")
        return self.vector_db

    def save_vector_db(self) -> None:
        """儲存向量資料庫到指定目錄"""
        if self.vector_db is None:
            raise ValueError("尚未建立向量資料庫")
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db.save_local(str(self.vector_dir))
        logger.info(f"向量資料庫已儲存到: {self.vector_dir}")

    def validate_vector_db(self) -> Dict[str, Any]:
        """驗證向量資料庫並返回統計資訊"""
        if self.vector_db is None:
            raise ValueError("尚未建立向量資料庫")
        # 驗證向量維度與數量
        stats = {
            "vector_count": self.vector_db.index.ntotal,
            "vector_dim": self.vector_db.index.d,
            "doc_count": len(self.documents)
        }
        logger.info(f"向量庫統計: {stats}")
        return stats

def build_and_save_knowledge_base():
    """從已分塊資料建立並儲存向量資料庫的便捷函數"""
    chunk_path = "data/text_chunks.json"
    vector_dir = "vector_store/crem_faiss_index"
    builder = VectorDatabaseBuilder(chunk_path, vector_dir)
    builder.load_chunks()
    builder.build_vector_db()
    builder.save_vector_db()
    stats = builder.validate_vector_db()
    logger.info("=== 向量化與知識庫建立完成 ===")
    logger.info(f"向量數量: {stats['vector_count']}")
    logger.info(f"向量維度: {stats['vector_dim']}")
    logger.info(f"分塊數量: {stats['doc_count']}")

if __name__ == "__main__":
    build_and_save_knowledge_base() 

