"""
統一查詢引擎
支援文本和表格的混合查詢，提供結構化的搜尋結果
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dataclasses import dataclass

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """查詢結果資料結構"""
    rank: int
    content_type: str  # 'text' or 'table'
    content: str
    source: str
    confidence_score: float
    metadata: Dict[str, Any]

class UnifiedQueryEngine:
    """統一查詢引擎"""
    
    def __init__(self, vector_dir: str):
        self.vector_dir = Path(vector_dir)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.vector_db = None
        self.query_stats = {
            "total_queries": 0,
            "text_results": 0,
            "table_results": 0,
            "last_query_time": None
        }
    
    def load_vector_db(self) -> bool:
        """載入向量資料庫"""
        faiss_file = self.vector_dir / "index.faiss"
        pkl_file = self.vector_dir / "index.pkl"
        
        if faiss_file.exists() and pkl_file.exists():
            try:
                self.vector_db = FAISS.load_local(
                    str(self.vector_dir), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"✅ 載入向量資料庫成功 (向量數: {self.vector_db.index.ntotal})")
                return True
            except Exception as e:
                logger.error(f"載入向量資料庫失敗: {e}")
                return False
        else:
            logger.error("向量資料庫檔案不存在")
            return False
    
    def query(self, question: str, k: int = 5, filter_type: str = "all") -> List[QueryResult]:
        """
        執行統一查詢
        
        Args:
            question: 查詢問題
            k: 返回結果數量
            filter_type: 篩選類型 ("all", "text", "table")
            
        Returns:
            查詢結果列表
            
        >>> engine = UnifiedQueryEngine("vector_store/crem_faiss_index")
        >>> engine.load_vector_db()
        True
        >>> results = engine.query("風險事件", k=3)
        >>> len(results) <= 3
        True
        """
        if self.vector_db is None:
            if not self.load_vector_db():
                return []
        
        self.query_stats["total_queries"] += 1
        self.query_stats["last_query_time"] = datetime.now().isoformat()
        
        try:
            # 執行相似性搜尋
            docs = self.vector_db.similarity_search_with_score(question, k=k*2)  # 多取一些以便篩選
            
            results = []
            text_count = 0
            table_count = 0
            
            for i, (doc, score) in enumerate(docs):
                # 判斷內容類型
                content_type = doc.metadata.get("content_type", "text")
                if content_type == "structured_table":
                    content_type = "table"
                else:
                    content_type = "text"
                
                # 篩選類型
                if filter_type != "all" and content_type != filter_type:
                    continue
                
                # 如果已經有足夠的結果，停止
                if len(results) >= k:
                    break
                
                # 處理內容顯示
                content = doc.page_content
                if content_type == "table":
                    # 表格內容格式化
                    content = self._format_table_content(content, doc.metadata)
                    table_count += 1
                else:
                    # 文本內容截取
                    if len(content) > 300:
                        content = content[:300] + "..."
                    text_count += 1
                
                # 建立查詢結果
                result = QueryResult(
                    rank=len(results) + 1,
                    content_type=content_type,
                    content=content,
                    source=doc.metadata.get("source", "unknown"),
                    confidence_score=1.0 - score,  # FAISS返回的是距離，轉換為相似度
                    metadata=doc.metadata
                )
                
                results.append(result)
            
            # 更新統計
            self.query_stats["text_results"] += text_count
            self.query_stats["table_results"] += table_count
            
            logger.info(f"查詢完成: '{question}' - 找到 {len(results)} 個結果 "
                       f"(文本: {text_count}, 表格: {table_count})")
            
            return results
            
        except Exception as e:
            logger.error(f"查詢執行失敗: {e}")
            return []
    
    def _format_table_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """格式化表格內容顯示"""
        table_id = metadata.get("table_id", "unknown")
        table_type = metadata.get("table_type", "general")
        source_page = metadata.get("source_page", "unknown")
        confidence = metadata.get("confidence", 0)
        
        # 提取表格的關鍵資訊
        lines = content.split('\n')
        title = lines[0] if lines else "未知表格"
        
        # 建立簡潔的表格摘要
        summary_parts = [
            f"📊 {title}",
            f"   類型: {table_type} | 頁面: {source_page} | 信心度: {confidence:.1f}%"
        ]
        
        # 添加部分內容
        content_lines = [line.strip() for line in lines[1:8] if line.strip()]  # 取前7行
        if content_lines:
            summary_parts.append("   內容預覽:")
            for line in content_lines[:5]:  # 只顯示前5行
                if len(line) > 0:
                    summary_parts.append(f"     {line}")
            if len(content_lines) > 5:
                summary_parts.append("     ...")
        
        return '\n'.join(summary_parts)
    
    def search_tables_only(self, question: str, k: int = 5) -> List[QueryResult]:
        """僅搜尋表格資料"""
        return self.query(question, k=k, filter_type="table")
    
    def search_text_only(self, question: str, k: int = 5) -> List[QueryResult]:
        """僅搜尋文本資料"""
        return self.query(question, k=k, filter_type="text")
    
    def display_results(self, results: List[QueryResult]) -> None:
        """美觀地顯示查詢結果"""
        if not results:
            print("❌ 沒有找到相關結果")
            return
        
        print(f"\n🔍 找到 {len(results)} 個結果:\n")
        
        for result in results:
            # 結果標題
            type_icon = "📊" if result.content_type == "table" else "📄"
            print(f"{type_icon} [{result.rank}] {result.content_type.upper()} "
                  f"(相似度: {result.confidence_score:.3f})")
            
            # 來源資訊
            print(f"   來源: {result.source}")
            if result.content_type == "table":
                table_id = result.metadata.get("table_id", "unknown")
                print(f"   表格ID: {table_id}")
            
            # 內容
            print(f"   內容:")
            content_lines = result.content.split('\n')
            for line in content_lines:
                if line.strip():
                    print(f"     {line}")
            
            print("-" * 80)
    
    def get_query_stats(self) -> Dict[str, Any]:
        """獲取查詢統計資訊"""
        stats = self.query_stats.copy()
        stats["vector_count"] = self.vector_db.index.ntotal if self.vector_db else 0
        return stats


def demo_unified_query():
    """Demo函數：統一查詢測試"""
    engine = UnifiedQueryEngine("vector_store/crem_faiss_index")
    
    if not engine.load_vector_db():
        logger.error("無法載入向量資料庫")
        return
    
    # 測試查詢
    test_queries = [
        ("風險事件有哪些？", "all"),
        ("risky events", "all"), 
        ("表格中的統計資料", "table"),
        ("安全政策", "text")
    ]
    
    print("=" * 80)
    print("🚀 統一查詢引擎 Demo")
    print("=" * 80)
    
    for question, filter_type in test_queries:
        print(f"\n🔎 查詢: '{question}' (類型: {filter_type})")
        print("-" * 60)
        
        results = engine.query(question, k=3, filter_type=filter_type)
        engine.display_results(results)
    
    # 顯示統計
    stats = engine.get_query_stats()
    print("\n📊 查詢統計:")
    print(f"   總查詢次數: {stats['total_queries']}")
    print(f"   文本結果數: {stats['text_results']}")
    print(f"   表格結果數: {stats['table_results']}")
    print(f"   向量資料庫大小: {stats['vector_count']} 個向量")
    print(f"   最後查詢時間: {stats['last_query_time']}")


if __name__ == "__main__":
    demo_unified_query() 