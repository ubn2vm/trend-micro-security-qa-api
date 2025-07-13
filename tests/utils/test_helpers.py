"""
測試輔助工具

提供測試過程中需要的共用工具和輔助函數
"""

import os
import sys
import time
import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@dataclass
class TestResult:
    """測試結果資料類別"""
    name: str
    status: str  # 'success', 'error', 'warning'
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class TestClient:
    """API 測試客戶端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AIOps-Test-Client/1.0'
        })
    
    def health_check(self) -> TestResult:
        """健康檢查測試"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            end_time = time.time()
            
            return TestResult(
                name="健康檢查",
                status="success" if response.status_code == 200 else "error",
                response_time=end_time - start_time,
                status_code=response.status_code,
                data=response.json() if response.status_code == 200 else None,
                error_message=f"HTTP {response.status_code}" if response.status_code != 200 else None
            )
        except Exception as e:
            return TestResult(
                name="健康檢查",
                status="error",
                error_message=str(e)
            )
    
    def get_examples(self) -> TestResult:
        """獲取範例問題測試"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/examples", timeout=self.timeout)
            end_time = time.time()
            
            return TestResult(
                name="範例問題端點",
                status="success" if response.status_code == 200 else "error",
                response_time=end_time - start_time,
                status_code=response.status_code,
                data=response.json() if response.status_code == 200 else None,
                error_message=f"HTTP {response.status_code}" if response.status_code != 200 else None
            )
        except Exception as e:
            return TestResult(
                name="範例問題端點",
                status="error",
                error_message=str(e)
            )
    
    def ask_question(self, question: str) -> TestResult:
        """問答功能測試"""
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/ask",
                json={"question": question},
                timeout=self.timeout
            )
            end_time = time.time()
            
            return TestResult(
                name=f"問答測試: {question[:30]}...",
                status="success" if response.status_code == 200 else "error",
                response_time=end_time - start_time,
                status_code=response.status_code,
                data=response.json() if response.status_code == 200 else None,
                error_message=f"HTTP {response.status_code}" if response.status_code != 200 else None
            )
        except Exception as e:
            return TestResult(
                name=f"問答測試: {question[:30]}...",
                status="error",
                error_message=str(e)
            )

class TestResultValidator:
    """測試結果驗證器"""
    
    @staticmethod
    def validate_health_check(result: TestResult) -> bool:
        """驗證健康檢查結果"""
        if result.status != "success":
            return False
        
        if not result.data:
            return False
        
        required_fields = ["status", "version"]
        return all(field in result.data for field in required_fields)
    
    @staticmethod
    def validate_qa_response(result: TestResult) -> bool:
        """驗證問答回應結果"""
        if result.status != "success":
            return False
        
        if not result.data:
            return False
        
        required_fields = ["answer"]
        return all(field in result.data for field in required_fields)
    
    @staticmethod
    def validate_performance(result: TestResult, max_response_time: float = 10.0) -> bool:
        """驗證性能結果"""
        if result.status != "success":
            return False
        
        if result.response_time is None:
            return False
        
        return result.response_time <= max_response_time

class TestReportGenerator:
    """測試報告生成器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def add_result(self, result: TestResult):
        """添加測試結果"""
        self.results.append(result)
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成測試摘要"""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.status == "success"])
        failed_tests = len([r for r in self.results if r.status == "error"])
        warning_tests = len([r for r in self.results if r.status == "warning"])
        
        avg_response_time = 0
        response_times = [r.response_time for r in self.results if r.response_time is not None]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "warning_tests": warning_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "average_response_time": round(avg_response_time, 3)
            },
            "results": [self._result_to_dict(r) for r in self.results]
        }
    
    def _result_to_dict(self, result: TestResult) -> Dict[str, Any]:
        """將測試結果轉換為字典"""
        return {
            "name": result.name,
            "status": result.status,
            "response_time": result.response_time,
            "status_code": result.status_code,
            "error_message": result.error_message,
            "timestamp": result.timestamp
        }
    
    def save_report(self, filename: str = "test_report.json"):
        """儲存測試報告"""
        report = self.generate_summary()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return filename
    
    def print_summary(self):
        """列印測試摘要"""
        summary = self.generate_summary()
        
        print("=" * 60)
        print("測試報告摘要")
        print("=" * 60)
        print(f"測試時間: {summary['timestamp']}")
        print(f"總測試數: {summary['summary']['total_tests']}")
        print(f"成功測試: {summary['summary']['successful_tests']}")
        print(f"失敗測試: {summary['summary']['failed_tests']}")
        print(f"警告測試: {summary['summary']['warning_tests']}")
        print(f"成功率: {summary['summary']['success_rate']:.1f}%")
        print(f"平均回應時間: {summary['summary']['average_response_time']}s")
        print("=" * 60)
        
        # 列印詳細結果
        for result in self.results:
            status_icon = "✅" if result.status == "success" else "❌" if result.status == "error" else "⚠️"
            print(f"{status_icon} {result.name}")
            if result.response_time:
                print(f"   回應時間: {result.response_time:.3f}s")
            if result.error_message:
                print(f"   錯誤訊息: {result.error_message}")
        print("=" * 60) 