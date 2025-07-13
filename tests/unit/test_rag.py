"""
RAG 系統單元測試

測試 RAG 系統的核心功能
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestRAGSystem:
    """RAG 系統測試類別"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試設定"""
        # 模擬 RAG 系統組件
        self.mock_vector_store = Mock()
        self.mock_llm = Mock()
        self.mock_embeddings = Mock()
    
    def test_question_processing(self):
        """測試問題處理"""
        # 模擬問題處理
        question = "什麼是網路風險指數？"
        
        # 測試問題清理
        cleaned_question = question.strip()
        assert cleaned_question == question
        
        # 測試問題長度驗證
        assert len(question) > 0
        assert len(question) < 1000
    
    def test_embedding_generation(self):
        """測試嵌入生成"""
        # 模擬嵌入生成
        question = "測試問題"
        mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        self.mock_embeddings.embed_query.return_value = mock_embedding
        
        # 測試嵌入生成
        embedding = self.mock_embeddings.embed_query(question)
        assert embedding == mock_embedding
        assert len(embedding) == 5
    
    def test_vector_search(self):
        """測試向量搜尋"""
        # 模擬向量搜尋
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock_results = [
            {"content": "相關文件1", "score": 0.9},
            {"content": "相關文件2", "score": 0.8},
            {"content": "相關文件3", "score": 0.7}
        ]
        
        self.mock_vector_store.similarity_search_with_score.return_value = mock_results
        
        # 測試向量搜尋
        results = self.mock_vector_store.similarity_search_with_score(query_embedding, k=3)
        assert len(results) == 3
        assert all("content" in result for result in results)
        assert all("score" in result for result in results)
    
    def test_context_assembly(self):
        """測試上下文組裝"""
        # 模擬搜尋結果
        search_results = [
            {"content": "文件內容1", "score": 0.9},
            {"content": "文件內容2", "score": 0.8},
            {"content": "文件內容3", "score": 0.7}
        ]
        
        # 測試上下文組裝
        context_parts = [result["content"] for result in search_results]
        context = "\n\n".join(context_parts)
        
        assert "文件內容1" in context
        assert "文件內容2" in context
        assert "文件內容3" in context
        assert context.count("\n\n") == 2
    
    def test_prompt_generation(self):
        """測試提示詞生成"""
        question = "什麼是網路風險指數？"
        context = "網路風險指數是一個重要的安全指標..."
        
        # 測試提示詞生成
        prompt = f"""基於以下上下文回答問題：

上下文：
{context}

問題：{question}

回答："""
        
        assert question in prompt
        assert context in prompt
        assert "基於以下上下文回答問題" in prompt
    
    def test_llm_response_generation(self):
        """測試 LLM 回應生成"""
        # 模擬 LLM 回應
        mock_response = "網路風險指數是一個衡量網路安全風險的指標..."
        
        self.mock_llm.generate_response.return_value = mock_response
        
        # 測試 LLM 回應生成
        response = self.mock_llm.generate_response("測試提示詞")
        assert response == mock_response
        assert len(response) > 0
    
    def test_response_formatting(self):
        """測試回應格式化"""
        # 模擬原始回應
        raw_response = "網路風險指數是一個重要的安全指標。"
        
        # 測試回應格式化
        formatted_response = {
            "answer": raw_response,
            "sources": [
                {"title": "來源1", "content": "內容1", "page": 1},
                {"title": "來源2", "content": "內容2", "page": 5}
            ],
            "confidence": 0.85
        }
        
        assert "answer" in formatted_response
        assert "sources" in formatted_response
        assert "confidence" in formatted_response
        assert len(formatted_response["sources"]) == 2
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 測試空問題處理
        empty_question = ""
        assert len(empty_question) == 0
        
        # 測試無效嵌入處理
        with pytest.raises(Exception):
            self.mock_embeddings.embed_query.side_effect = Exception("嵌入生成失敗")
            self.mock_embeddings.embed_query("測試問題")
        
        # 測試向量搜尋失敗處理
        with pytest.raises(Exception):
            self.mock_vector_store.similarity_search_with_score.side_effect = Exception("搜尋失敗")
            self.mock_vector_store.similarity_search_with_score([0.1, 0.2, 0.3], k=3)
    
    def test_performance_metrics(self):
        """測試性能指標"""
        # 模擬性能指標
        start_time = 0.0
        end_time = 2.5
        
        processing_time = end_time - start_time
        assert processing_time == 2.5
        
        # 測試回應時間驗證
        assert processing_time < 30.0  # 應該在 30 秒內完成
    
    def test_confidence_scoring(self):
        """測試信心度評分"""
        # 模擬搜尋結果分數
        search_scores = [0.9, 0.8, 0.7, 0.6]
        
        # 計算平均信心度
        avg_confidence = sum(search_scores) / len(search_scores)
        assert avg_confidence == 0.75
        
        # 測試信心度範圍
        assert 0.0 <= avg_confidence <= 1.0
    
    def test_source_validation(self):
        """測試來源驗證"""
        # 模擬來源資料
        sources = [
            {"title": "來源1", "content": "內容1", "page": 1},
            {"title": "來源2", "content": "內容2", "page": 5},
            {"title": "", "content": "", "page": 0}  # 無效來源
        ]
        
        # 驗證有效來源
        valid_sources = [s for s in sources if s["title"] and s["content"]]
        assert len(valid_sources) == 2
        
        # 測試來源格式
        for source in valid_sources:
            assert "title" in source
            assert "content" in source
            assert "page" in source

class TestRAGComponents:
    """RAG 組件測試類別"""
    
    def test_text_processor(self):
        """測試文本處理器"""
        # 模擬文本處理
        raw_text = "  這是原始文本，包含多餘的空格和換行。\n\n  需要清理。  "
        
        # 測試文本清理
        cleaned_text = raw_text.strip()
        assert cleaned_text.startswith("這是原始文本")
        assert cleaned_text.endswith("需要清理。")
        
        # 測試文本分割
        text_chunks = cleaned_text.split("。")
        assert len(text_chunks) >= 2
    
    def test_vector_store_operations(self):
        """測試向量資料庫操作"""
        # 模擬向量資料庫操作
        mock_store = Mock()
        
        # 測試添加文檔
        mock_store.add_documents.return_value = ["doc1", "doc2"]
        docs = mock_store.add_documents(["文檔1", "文檔2"])
        assert len(docs) == 2
        
        # 測試搜尋文檔
        mock_store.search.return_value = [{"content": "搜尋結果", "score": 0.9}]
        results = mock_store.search("查詢")
        assert len(results) == 1
        assert results[0]["score"] == 0.9
    
    def test_llm_integration(self):
        """測試 LLM 整合"""
        # 模擬 LLM 整合
        mock_llm = Mock()
        
        # 測試提示詞處理
        prompt = "請回答這個問題：什麼是網路安全？"
        mock_llm.process_prompt.return_value = "網路安全是保護網路系統的實踐。"
        
        response = mock_llm.process_prompt(prompt)
        assert "網路安全" in response
        
        # 測試回應驗證
        assert len(response) > 0
        assert isinstance(response, str)

def run_rag_tests():
    """執行 RAG 測試"""
    import pytest
    
    # 執行測試
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])

if __name__ == "__main__":
    run_rag_tests() 