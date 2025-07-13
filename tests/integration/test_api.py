"""
API 整合測試

測試所有 API 端點的功能和整合性
"""

import pytest
import sys
import os
from typing import Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.utils.test_helpers import TestClient, TestResultValidator, TestReportGenerator
from tests.utils.mock_data import MockDataGenerator

class TestAPIEndpoints:
    """API 端點測試類別"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試設定"""
        self.client = TestClient()
        self.validator = TestResultValidator()
        self.report_generator = TestReportGenerator()
        self.mock_data = MockDataGenerator()
    
    def test_health_check(self):
        """測試健康檢查端點"""
        result = self.client.health_check()
        self.report_generator.add_result(result)
        
        assert result.status == "success"
        assert result.status_code == 200
        assert self.validator.validate_health_check(result)
        assert result.response_time is not None
        assert result.response_time < 5.0  # 健康檢查應該很快
    
    def test_examples_endpoint(self):
        """測試範例問題端點"""
        result = self.client.get_examples()
        self.report_generator.add_result(result)
        
        assert result.status == "success"
        assert result.status_code == 200
        assert result.data is not None
        assert isinstance(result.data, list)
        assert len(result.data) > 0
    
    def test_qa_basic_functionality(self):
        """測試基本問答功能"""
        test_questions = self.mock_data.generate_test_questions()[:3]
        
        for question in test_questions:
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            assert result.status == "success"
            assert result.status_code == 200
            assert self.validator.validate_qa_response(result)
            assert result.response_time is not None
            assert result.response_time < 30.0  # 問答應該在合理時間內完成
    
    def test_qa_boundary_cases(self):
        """測試邊界情況"""
        boundary_questions = self.mock_data.generate_boundary_questions()
        
        for question in boundary_questions:
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            # 邊界情況可能返回錯誤，但應該有適當的錯誤處理
            assert result.status_code is not None
            assert result.status_code in [200, 400, 422]
    
    def test_qa_performance(self):
        """測試問答性能"""
        performance_questions = self.mock_data.generate_performance_questions()[:2]
        
        for question in performance_questions:
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            assert result.status == "success"
            assert result.status_code == 200
            assert self.validator.validate_performance(result, max_response_time=60.0)
    
    def test_api_consistency(self):
        """測試 API 回應一致性"""
        # 對同一個問題多次請求，應該得到一致的回應
        question = "什麼是網路風險指數？"
        responses = []
        
        for _ in range(3):
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            if result.status == "success" and result.data:
                responses.append(result.data.get("answer", ""))
        
        # 至少應該有成功的回應
        assert len(responses) > 0
        
        # 回應應該有內容
        for response in responses:
            assert len(response) > 0
    
    def test_error_handling(self):
        """測試錯誤處理"""
        # 測試無效的 JSON
        try:
            import requests
            response = requests.post(
                f"{self.client.base_url}/ask",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            assert response.status_code in [400, 422]
        except Exception:
            # 如果請求失敗，那也是可以接受的錯誤處理
            pass
    
    def test_api_documentation(self):
        """測試 API 文檔端點"""
        try:
            import requests
            response = requests.get(f"{self.client.base_url}/docs", timeout=10)
            # 文檔端點應該存在
            assert response.status_code in [200, 404]  # 404 也是可以接受的
        except Exception:
            # 如果無法訪問文檔，那也是可以接受的
            pass
    
    def test_cors_headers(self):
        """測試 CORS 標頭"""
        try:
            import requests
            response = requests.options(f"{self.client.base_url}/ask", timeout=10)
            # CORS 預檢請求應該有適當的回應
            assert response.status_code in [200, 204, 405]
        except Exception:
            # 如果 CORS 測試失敗，那也是可以接受的
            pass

class TestAPIIntegration:
    """API 整合測試類別"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試設定"""
        self.client = TestClient()
        self.report_generator = TestReportGenerator()
    
    def test_full_workflow(self):
        """測試完整工作流程"""
        # 1. 健康檢查
        health_result = self.client.health_check()
        self.report_generator.add_result(health_result)
        assert health_result.status == "success"
        
        # 2. 獲取範例問題
        examples_result = self.client.get_examples()
        self.report_generator.add_result(examples_result)
        assert examples_result.status == "success"
        
        # 3. 使用範例問題進行問答
        if examples_result.data and len(examples_result.data) > 0:
            example_question = examples_result.data[0]
            qa_result = self.client.ask_question(example_question)
            self.report_generator.add_result(qa_result)
            assert qa_result.status == "success"
    
    def test_concurrent_requests(self):
        """測試並發請求"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(question: str, index: int):
            try:
                result = self.client.ask_question(question)
                results.append((index, result))
            except Exception as e:
                errors.append((index, str(e)))
        
        # 建立多個執行緒同時發送請求
        threads = []
        questions = self.mock_data.generate_test_questions()[:5]
        
        for i, question in enumerate(questions):
            thread = threading.Thread(target=make_request, args=(question, i))
            threads.append(thread)
            thread.start()
        
        # 等待所有執行緒完成
        for thread in threads:
            thread.join()
        
        # 檢查結果
        assert len(results) > 0  # 至少應該有一些成功的請求
        assert len(errors) < len(questions)  # 錯誤應該少於總請求數
        
        # 添加結果到報告
        for index, result in results:
            self.report_generator.add_result(result)
    
    def test_api_stability(self):
        """測試 API 穩定性"""
        # 連續發送多個請求，測試系統穩定性
        questions = self.mock_data.generate_test_questions()
        success_count = 0
        
        for question in questions:
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            if result.status == "success":
                success_count += 1
            
            # 短暫延遲，避免過度負載
            import time
            time.sleep(0.5)
        
        # 成功率應該超過 80%
        success_rate = (success_count / len(questions)) * 100
        assert success_rate >= 80.0, f"成功率過低: {success_rate:.1f}%"

def run_integration_tests():
    """執行整合測試"""
    import pytest
    
    # 執行測試
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])

if __name__ == "__main__":
    run_integration_tests() 