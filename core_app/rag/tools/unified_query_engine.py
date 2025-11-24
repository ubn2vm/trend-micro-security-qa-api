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
            # 檢測查詢類型以決定檢索策略
            is_technical_query = any(keyword in question.lower() for keyword in [
                "路徑", "path", "目錄", "directory", "配置", "config", 
                "預設", "default", "設定", "setting", "日誌", "log",
                "suricata", "location", "位置"
            ])
            
            # 檢測是否為 CEF 或表格映射查詢
            is_cef_query = any(keyword in question.lower() for keyword in [
                "cef", "common event format", "威脅日誌", "threat log", "threat logs",
                "欄位", "field", "對應", "mapping", "對應到", "對應哪個", "哪個欄位"
            ])
            
            # 對於技術查詢或 CEF 查詢，增加檢索數量以提高召回率
            if is_technical_query or is_cef_query:
                search_k = k * 5  # CEF 表格查詢需要更多結果
            else:
                search_k = k * 3
            
            # 執行相似性搜尋（增加檢索數量以提高召回率）
            docs = self.vector_db.similarity_search_with_score(question, k=search_k)
            
            if not docs:
                logger.warning(f"查詢 '{question}' 沒有找到任何結果")
                return []
            
            results = []
            text_count = 0
            table_count = 0
            
            # FAISS 返回的是 L2 距離（歐幾里得距離），距離越小越相似
            # 計算相對相似度：使用最小距離作為基準
            distances = [score for _, score in docs]
            min_distance = min(distances)
            max_distance = max(distances)
            distance_range = max_distance - min_distance if max_distance > min_distance else 1.0
            
            # 使用相對距離轉換為相似度（0-1 範圍）
            # 相似度 = 1 - (距離 - 最小距離) / 距離範圍
            # 這樣最相似的結果相似度接近 1，最不相似的接近 0
            
            # 對於技術查詢，使用關鍵詞匹配來提高相關結果的優先級
            question_keywords = set()
            if is_technical_query:
                # 提取關鍵詞
                for keyword in ["/var/log/suricata", "var/log/suricata", "log directory", 
                               "default log", "suricata.log", "suricata", "log path"]:
                    if keyword.lower() in question.lower():
                        question_keywords.add(keyword.lower())
            
            # 檢測是否為 CEF 或表格映射查詢
            is_cef_query = any(keyword in question.lower() for keyword in [
                "cef", "common event format", "威脅日誌", "threat log", "threat logs",
                "欄位", "field", "對應", "mapping", "對應到", "對應哪個", "哪個欄位"
            ])
            
            # 對於 CEF 查詢，添加 CEF 相關關鍵詞
            if is_cef_query:
                for keyword in ["cef", "common event format", "threat log", "威脅日誌",
                               "attack phase", "攻擊階段", "cs6label", "cs6", "pattackphase",
                               "field", "欄位", "mapping", "對應", "cef key"]:
                    if keyword.lower() in question.lower():
                        question_keywords.add(keyword.lower())
                # 強制添加 CEF 相關關鍵詞以提高匹配率
                question_keywords.update(["cef", "field", "mapping"])
            
            for i, (doc, score) in enumerate(docs):
                # 計算相對相似度（0-1 範圍）
                if distance_range > 0:
                    # 正規化：距離越小，相似度越高
                    normalized_distance = (score - min_distance) / distance_range
                    similarity = 1.0 - normalized_distance
                else:
                    # 如果所有距離相同，給相同的相似度
                    similarity = 0.5
                
                # 對於技術查詢或 CEF 查詢，如果內容包含關鍵詞，提高相似度
                if (is_technical_query or is_cef_query) and question_keywords:
                    content_lower = doc.page_content.lower()
                    keyword_matches = sum(1 for kw in question_keywords if kw in content_lower)
                    if keyword_matches > 0:
                        # 根據關鍵詞匹配數量提高相似度
                        # CEF 查詢需要更大的 boost，因為表格內容可能與問題的語義相似度較低
                        boost_multiplier = 0.15 if is_cef_query else 0.1
                        similarity_boost = min(0.3 if is_cef_query else 0.2, keyword_matches * boost_multiplier)
                        similarity = min(1.0, similarity + similarity_boost)
                        
                        # 對於 CEF 查詢，如果包含特定的 CEF 欄位名稱，進一步提高相似度
                        if is_cef_query:
                            cef_specific_keywords = ["cs6label", "pattackphase", "attack phase", "攻擊階段"]
                            cef_matches = sum(1 for kw in cef_specific_keywords if kw in content_lower)
                            if cef_matches > 0:
                                similarity = min(1.0, similarity + 0.15)  # 額外提高 0.15
                
                # 過濾極低相似度結果
                # 對於技術問題（路徑、配置等）或 CEF 查詢，使用更寬鬆的閾值
                if is_technical_query or is_cef_query:
                    # 技術問題或 CEF 查詢：更寬鬆的過濾（保留更多結果）
                    # 如果包含關鍵詞，進一步放寬閾值
                    # CEF 表格查詢需要更寬鬆的閾值，因為表格內容的語義相似度可能較低
                    if is_cef_query:
                        threshold = 0.02 if question_keywords and any(kw in doc.page_content.lower() for kw in question_keywords) else 0.04
                        max_distance_threshold = 250 if question_keywords and any(kw in doc.page_content.lower() for kw in question_keywords) else 200
                    else:
                        threshold = 0.03 if question_keywords and any(kw in doc.page_content.lower() for kw in question_keywords) else 0.05
                        max_distance_threshold = 200 if question_keywords and any(kw in doc.page_content.lower() for kw in question_keywords) else 150
                    
                    if similarity < threshold or score > max_distance_threshold:
                        logger.debug(f"過濾{'CEF' if is_cef_query else '技術'}查詢結果: 距離={score:.2f}, 相似度={similarity:.3f}")
                        continue
                else:
                    # 一般問題：正常過濾
                    if similarity < 0.1 or score > 100:
                        logger.debug(f"過濾結果: 距離={score:.2f}, 相似度={similarity:.3f}")
                        continue
                
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
                    # 文本內容：保留完整內容用於引用（不截取）
                    # 這樣用戶可以在原文中找到完整的引用內容
                    # 注意：這裡不截取，讓引用內容保持完整
                    text_count += 1
                
                # 建立查詢結果
                # 使用計算出的相對相似度（已在上面計算）
                # 在 metadata 中保存原始完整內容，以便引用時使用
                enhanced_metadata = doc.metadata.copy()
                enhanced_metadata['original_content'] = doc.page_content  # 保存完整原始內容
                
                result = QueryResult(
                    rank=len(results) + 1,
                    content_type=content_type,
                    content=content,  # 保持完整內容（已在上面處理，不截取）
                    source=doc.metadata.get("source", "unknown"),
                    confidence_score=similarity,  # 使用相對相似度（0-1 範圍）
                    metadata=enhanced_metadata
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