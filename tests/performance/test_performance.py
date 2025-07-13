"""
性能測試

測試系統的效能和負載能力
"""

import pytest
import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.utils.test_helpers import TestClient, TestResultValidator, TestReportGenerator
from tests.utils.mock_data import MockDataGenerator

class TestPerformance:
    """性能測試類別"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試設定"""
        self.client = TestClient()
        self.validator = TestResultValidator()
        self.report_generator = TestReportGenerator()
        self.mock_data = MockDataGenerator()
    
    def test_single_request_performance(self):
        """測試單次請求性能"""
        question = "什麼是網路風險指數？"
        
        start_time = time.time()
        result = self.client.ask_question(question)
        end_time = time.time()
        
        self.report_generator.add_result(result)
        
        # 基本性能要求
        assert result.status == "success"
        assert result.response_time is not None
        assert result.response_time < 30.0  # 單次請求應該在 30 秒內完成
        
        # 記錄詳細性能資料
        print(f"單次請求性能: {result.response_time:.3f}秒")
    
    def test_multiple_requests_performance(self):
        """測試多次請求性能"""
        questions = self.mock_data.generate_test_questions()[:5]
        results = []
        
        start_time = time.time()
        for question in questions:
            result = self.client.ask_question(question)
            results.append(result)
            self.report_generator.add_result(result)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / len(questions)
        
        # 性能要求
        assert total_time < 150.0  # 5 個請求應該在 150 秒內完成
        assert avg_time < 30.0  # 平均每個請求應該在 30 秒內完成
        
        # 成功率要求
        success_count = len([r for r in results if r.status == "success"])
        success_rate = (success_count / len(results)) * 100
        assert success_rate >= 80.0, f"成功率過低: {success_rate:.1f}%"
        
        print(f"多次請求性能: 總時間 {total_time:.3f}秒, 平均 {avg_time:.3f}秒, 成功率 {success_rate:.1f}%")
    
    def test_concurrent_requests_performance(self):
        """測試並發請求性能"""
        questions = self.mock_data.generate_test_questions()[:10]
        max_workers = 5
        
        def make_request(question: str) -> Dict[str, Any]:
            start_time = time.time()
            result = self.client.ask_question(question)
            end_time = time.time()
            
            return {
                "question": question,
                "result": result,
                "response_time": end_time - start_time
            }
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request, q) for q in questions]
            
            for future in as_completed(futures):
                result_data = future.result()
                results.append(result_data)
                self.report_generator.add_result(result_data["result"])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能要求
        assert total_time < 300.0  # 10 個並發請求應該在 300 秒內完成
        
        # 成功率要求
        success_count = len([r for r in results if r["result"].status == "success"])
        success_rate = (success_count / len(results)) * 100
        assert success_rate >= 70.0, f"並發成功率過低: {success_rate:.1f}%"
        
        # 平均回應時間
        response_times = [r["response_time"] for r in results if r["result"].status == "success"]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 60.0  # 平均回應時間應該在 60 秒內
        
        print(f"並發請求性能: 總時間 {total_time:.3f}秒, 成功率 {success_rate:.1f}%")
    
    def test_load_testing(self):
        """負載測試"""
        # 模擬較大的負載
        questions = self.mock_data.generate_performance_questions()
        results = []
        
        start_time = time.time()
        for i, question in enumerate(questions):
            result = self.client.ask_question(question)
            results.append(result)
            self.report_generator.add_result(result)
            
            # 短暫延遲，避免過度負載
            time.sleep(1)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # 負載測試要求
        assert total_time < 600.0  # 負載測試應該在 10 分鐘內完成
        
        # 成功率要求
        success_count = len([r for r in results if r.status == "success"])
        success_rate = (success_count / len(results)) * 100
        assert success_rate >= 60.0, f"負載測試成功率過低: {success_rate:.1f}%"
        
        print(f"負載測試: 總時間 {total_time:.3f}秒, 成功率 {success_rate:.1f}%")
    
    def test_memory_usage(self):
        """測試記憶體使用情況"""
        import psutil
        import os
        
        # 獲取當前進程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 執行一系列請求
        questions = self.mock_data.generate_test_questions()[:10]
        for question in questions:
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
        
        # 檢查記憶體使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 記憶體增長應該在合理範圍內
        assert memory_increase < 500.0, f"記憶體增長過大: {memory_increase:.1f}MB"
        
        print(f"記憶體使用: 初始 {initial_memory:.1f}MB, 最終 {final_memory:.1f}MB, 增長 {memory_increase:.1f}MB")
    
    def test_response_time_consistency(self):
        """測試回應時間一致性"""
        question = "什麼是網路風險指數？"
        response_times = []
        
        # 多次請求同一個問題
        for _ in range(5):
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            if result.response_time is not None:
                response_times.append(result.response_time)
            
            time.sleep(1)  # 短暫延遲
        
        if len(response_times) >= 3:
            # 計算變異係數
            mean_time = sum(response_times) / len(response_times)
            variance = sum((t - mean_time) ** 2 for t in response_times) / len(response_times)
            std_dev = variance ** 0.5
            coefficient_of_variation = (std_dev / mean_time) * 100 if mean_time > 0 else 0
            
            # 變異係數應該小於 50%
            assert coefficient_of_variation < 50.0, f"回應時間變異過大: {coefficient_of_variation:.1f}%"
            
            print(f"回應時間一致性: 平均 {mean_time:.3f}秒, 變異係數 {coefficient_of_variation:.1f}%")
    
    def test_error_recovery_performance(self):
        """測試錯誤恢復性能"""
        # 先發送一個正常請求
        normal_result = self.client.ask_question("什麼是網路風險指數？")
        self.report_generator.add_result(normal_result)
        
        # 再發送一個可能導致錯誤的請求
        error_result = self.client.ask_question("")
        self.report_generator.add_result(error_result)
        
        # 再發送一個正常請求，測試系統是否恢復
        recovery_result = self.client.ask_question("如何評估企業的網路安全風險？")
        self.report_generator.add_result(recovery_result)
        
        # 系統應該能夠從錯誤中恢復
        assert recovery_result.status == "success"
        assert recovery_result.response_time is not None
        assert recovery_result.response_time < 30.0
        
        print("錯誤恢復性能測試通過")
    
    def test_api_throughput(self):
        """測試 API 吞吐量"""
        questions = self.mock_data.generate_test_questions()[:20]
        start_time = time.time()
        
        success_count = 0
        for question in questions:
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            if result.status == "success":
                success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 計算吞吐量 (請求/分鐘)
        throughput = (success_count / total_time) * 60
        
        # 吞吐量應該至少達到 0.5 請求/分鐘
        assert throughput >= 0.5, f"吞吐量過低: {throughput:.2f} 請求/分鐘"
        
        print(f"API 吞吐量: {throughput:.2f} 請求/分鐘")

def run_performance_tests():
    """執行性能測試"""
    import pytest
    
    # 執行測試
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])

if __name__ == "__main__":
    run_performance_tests() 