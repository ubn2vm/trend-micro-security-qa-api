"""
表格向量整合器
將表格文本資料整合到RAG向量資料庫中
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableVectorIntegrator:
    """表格向量整合器"""
    
    def __init__(self, vector_dir: str):
        self.vector_dir = Path(vector_dir)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.integration_stats = {
            "total_tables": 0,
            "integrated_tables": 0,
            "vector_count_before": 0,
            "vector_count_after": 0,
            "integration_date": None
        }
    
    def load_existing_vector_db(self) -> Optional[FAISS]:
        """載入現有的向量資料庫"""
        faiss_file = self.vector_dir / "index.faiss"
        pkl_file = self.vector_dir / "index.pkl"
        
        if faiss_file.exists() and pkl_file.exists():
            try:
                vector_db = FAISS.load_local(
                    str(self.vector_dir), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"✅ 成功載入現有向量資料庫 (向量數: {vector_db.index.ntotal})")
                self.integration_stats["vector_count_before"] = vector_db.index.ntotal
                return vector_db
            except Exception as e:
                logger.warning(f"載入向量資料庫失敗: {e}")
                return None
        else:
            logger.info("沒有找到現有向量資料庫")
            return None
    
    def convert_table_texts_to_documents(self, table_texts_path: str) -> List[Document]:
        """
        將表格文本轉換為 Langchain Document 格式
        
        Args:
            table_texts_path: 表格文本JSON檔案路徑
            
        Returns:
            Document 列表
            
        >>> integrator = TableVectorIntegrator("test_vector")
        >>> # 模擬測試會在實際測試中進行
        """
        logger.info(f"載入表格文本: {table_texts_path}")
        
        with open(table_texts_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        table_texts = data.get("table_texts", [])
        self.integration_stats["total_tables"] = len(table_texts)
        
        documents = []
        
        for table_text in table_texts:
            try:
                # 建立 Document
                doc = Document(
                    page_content=table_text["content"],
                    metadata={
                        "source": table_text["metadata"]["source_file"],
                        "source_type": "table",
                        "table_id": table_text["table_id"],
                        "table_type": table_text["metadata"]["table_type"],
                        "source_page": table_text["metadata"]["source_page"],
                        "confidence": table_text["metadata"]["confidence"],
                        "extractor_method": table_text["metadata"]["extractor_method"],
                        "processed_date": table_text["metadata"]["conversion_date"],
                        "content_type": "structured_table"
                    }
                )
                documents.append(doc)
                self.integration_stats["integrated_tables"] += 1
                
            except Exception as e:
                logger.warning(f"轉換表格文本失敗: {e}")
                continue
        
        logger.info(f"成功轉換 {len(documents)} 個表格為向量文檔")
        return documents
    
    def integrate_tables_to_vector_db(self, table_texts_path: str, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        將表格資料整合到向量資料庫
        
        Args:
            table_texts_path: 表格文本JSON檔案路徑
            force_rebuild: 是否強制重建向量資料庫
            
        Returns:
            整合統計資訊
        """
        logger.info("開始表格向量整合...")
        self.integration_stats["integration_date"] = datetime.now().isoformat()
        
        # 載入現有向量資料庫
        vector_db = self.load_existing_vector_db()
        
        if force_rebuild:
            logger.info("強制重建模式：忽略現有向量資料庫")
            vector_db = None
        
        # 轉換表格文本為向量文檔
        table_documents = self.convert_table_texts_to_documents(table_texts_path)
        
        if not table_documents:
            logger.warning("沒有表格文檔可以整合")
            return self.integration_stats
        
        # 整合到向量資料庫
        if vector_db is None:
            logger.info("建立新的向量資料庫（包含表格資料）...")
            vector_db = FAISS.from_documents(table_documents, self.embeddings)
        else:
            logger.info(f"將 {len(table_documents)} 個表格文檔加入現有向量資料庫...")
            vector_db.add_documents(table_documents)
        
        # 儲存更新後的向量資料庫
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        vector_db.save_local(str(self.vector_dir))
        
        # 更新統計資訊
        self.integration_stats["vector_count_after"] = vector_db.index.ntotal
        
        logger.info("表格向量整合完成")
        logger.info(f"整合表格數: {self.integration_stats['integrated_tables']}")
        logger.info(f"向量數 (前): {self.integration_stats['vector_count_before']}")
        logger.info(f"向量數 (後): {self.integration_stats['vector_count_after']}")
        
        return self.integration_stats
    
    def test_table_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        測試表格搜尋功能
        
        Args:
            query: 搜尋查詢
            k: 返回結果數量
            
        Returns:
            搜尋結果列表
        """
        vector_db = self.load_existing_vector_db()
        
        if vector_db is None:
            logger.error("無法載入向量資料庫進行測試")
            return []
        
        try:
            # 執行相似性搜尋
            docs = vector_db.similarity_search(query, k=k)
            
            results = []
            for i, doc in enumerate(docs):
                result = {
                    "rank": i + 1,
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata,
                    "content_type": doc.metadata.get("content_type", "unknown")
                }
                results.append(result)
            
            logger.info(f"搜尋查詢: '{query}' - 找到 {len(results)} 個結果")
            return results
            
        except Exception as e:
            logger.error(f"搜尋測試失敗: {e}")
            return []
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """獲取整合統計資訊"""
        return self.integration_stats.copy()


def integrate_tables_demo():
    """Demo函數：整合表格到向量資料庫"""
    integrator = TableVectorIntegrator("vector_store/crem_faiss_index")
    
    # 表格文本檔案路徑
    table_texts_path = "data/processed/table_texts.json"
    
    try:
        # 執行整合
        stats = integrator.integrate_tables_to_vector_db(table_texts_path)
        
        logger.info("=== 整合統計 ===")
        logger.info(f"整合時間: {stats['integration_date']}")
        logger.info(f"總表格數: {stats['total_tables']}")
        logger.info(f"成功整合: {stats['integrated_tables']}")
        logger.info(f"向量數變化: {stats['vector_count_before']} → {stats['vector_count_after']}")
        
        # 測試搜尋功能
        logger.info("\n=== 搜尋測試 ===")
        test_queries = [
            "風險事件",
            "risky events", 
            "表格資料",
            "統計數據"
        ]
        
        for query in test_queries:
            logger.info(f"\n搜尋: '{query}'")
            results = integrator.test_table_search(query, k=2)
            for result in results:
                logger.info(f"  {result['rank']}. {result['metadata'].get('table_id', 'unknown')} "
                           f"(類型: {result['content_type']})")
                logger.info(f"     {result['content'][:100]}...")
        
        return stats
        
    except Exception as e:
        logger.error(f"整合Demo失敗: {e}")
        return {}


if __name__ == "__main__":
    integrate_tables_demo() 