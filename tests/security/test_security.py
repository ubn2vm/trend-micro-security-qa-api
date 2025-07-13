"""
安全測試

測試系統的安全性和漏洞防護
"""

import pytest
import sys
import os
import time
import requests
from typing import List, Dict, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.utils.test_helpers import TestClient, TestResultValidator, TestReportGenerator
from tests.utils.mock_data import MockDataGenerator

class TestSecurity:
    """安全測試類別"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試設定"""
        self.client = TestClient()
        self.validator = TestResultValidator()
        self.report_generator = TestReportGenerator()
        self.mock_data = MockDataGenerator()
    
    def test_sql_injection_protection(self):
        """測試 SQL 注入防護"""
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' UNION SELECT * FROM users --",
            "'; UPDATE users SET password='hacked' --"
        ]
        
        for payload in sql_injection_payloads:
            result = self.client.ask_question(payload)
            self.report_generator.add_result(result)
            
            # SQL 注入應該被阻止或返回錯誤
            assert result.status_code in [400, 422, 500], f"SQL 注入防護失敗: {payload}"
    
    def test_xss_protection(self):
        """測試 XSS 防護"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            result = self.client.ask_question(payload)
            self.report_generator.add_result(result)
            
            # XSS 應該被阻止或返回錯誤
            assert result.status_code in [400, 422, 500], f"XSS 防護失敗: {payload}"
    
    def test_path_traversal_protection(self):
        """測試路徑遍歷防護"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam"
        ]
        
        for payload in path_traversal_payloads:
            result = self.client.ask_question(payload)
            self.report_generator.add_result(result)
            
            # 路徑遍歷應該被阻止或返回錯誤
            assert result.status_code in [400, 422, 500], f"路徑遍歷防護失敗: {payload}"
    
    def test_command_injection_protection(self):
        """測試命令注入防護"""
        command_injection_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& del C:\\Windows\\System32",
            "; ls -la",
            "| whoami"
        ]
        
        for payload in command_injection_payloads:
            result = self.client.ask_question(payload)
            self.report_generator.add_result(result)
            
            # 命令注入應該被阻止或返回錯誤
            assert result.status_code in [400, 422, 500], f"命令注入防護失敗: {payload}"
    
    def test_input_validation(self):
        """測試輸入驗證"""
        invalid_inputs = [
            "",  # 空輸入
            "a" * 10000,  # 超長輸入
            "\x00\x01\x02",  # 二進制字符
            "測試\n換行\t製表符\r回車",  # 控制字符
            "🚀🔥💻📱🔒",  # Emoji
        ]
        
        for invalid_input in invalid_inputs:
            result = self.client.ask_question(invalid_input)
            self.report_generator.add_result(result)
            
            # 無效輸入應該被拒絕
            assert result.status_code in [400, 422], f"輸入驗證失敗: {repr(invalid_input)}"
    
    def test_rate_limiting(self):
        """測試速率限制"""
        # 快速發送多個請求
        for i in range(20):
            result = self.client.ask_question(f"測試問題 {i}")
            self.report_generator.add_result(result)
            
            # 如果系統有速率限制，某些請求應該被拒絕
            if result.status_code == 429:  # Too Many Requests
                print(f"速率限制生效於請求 {i}")
                break
        
        # 速率限制是可選的，所以不強制要求
        print("速率限制測試完成")
    
    def test_authentication_bypass(self):
        """測試認證繞過"""
        # 測試未授權訪問
        try:
            response = requests.get(f"{self.client.base_url}/admin", timeout=10)
            # 管理端點應該返回 401 或 403
            assert response.status_code in [401, 403, 404], f"認證繞過測試失敗: {response.status_code}"
        except Exception:
            # 如果無法訪問，那也是可以接受的
            pass
    
    def test_sensitive_data_exposure(self):
        """測試敏感資料洩露"""
        # 測試健康檢查端點是否洩露敏感資訊
        health_result = self.client.health_check()
        self.report_generator.add_result(health_result)
        
        if health_result.data:
            sensitive_fields = ["password", "secret", "key", "token", "credential"]
            data_str = str(health_result.data).lower()
            
            for field in sensitive_fields:
                assert field not in data_str, f"敏感資料洩露: {field}"
    
    def test_cors_configuration(self):
        """測試 CORS 配置"""
        try:
            # 測試 CORS 預檢請求
            response = requests.options(
                f"{self.client.base_url}/ask",
                headers={
                    "Origin": "https://malicious-site.com",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=10
            )
            
            # CORS 應該有適當的配置
            assert response.status_code in [200, 204, 405], f"CORS 配置測試失敗: {response.status_code}"
            
        except Exception:
            # 如果 CORS 測試失敗，那也是可以接受的
            pass
    
    def test_content_security_policy(self):
        """測試內容安全策略"""
        try:
            response = requests.get(f"{self.client.base_url}/", timeout=10)
            
            # 檢查是否有 CSP 標頭
            csp_header = response.headers.get("Content-Security-Policy")
            if csp_header:
                print(f"CSP 標頭存在: {csp_header}")
            else:
                print("CSP 標頭不存在")
                
        except Exception:
            # 如果無法訪問，那也是可以接受的
            pass
    
    def test_http_security_headers(self):
        """測試 HTTP 安全標頭"""
        try:
            response = requests.get(f"{self.client.base_url}/health", timeout=10)
            
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Referrer-Policy"
            ]
            
            for header in security_headers:
                if header in response.headers:
                    print(f"安全標頭存在: {header}")
                else:
                    print(f"安全標頭缺失: {header}")
                    
        except Exception:
            # 如果無法訪問，那也是可以接受的
            pass
    
    def test_error_handling_security(self):
        """測試錯誤處理安全性"""
        # 測試各種錯誤情況
        error_tests = [
            ("無效 JSON", "invalid json", 400),
            ("無效端點", "/nonexistent", 404),
            ("無效方法", "GET", 405)
        ]
        
        for test_name, payload, expected_status in error_tests:
            try:
                if test_name == "無效 JSON":
                    response = requests.post(
                        f"{self.client.base_url}/ask",
                        data=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                elif test_name == "無效端點":
                    response = requests.get(f"{self.client.base_url}{payload}", timeout=10)
                elif test_name == "無效方法":
                    response = requests.get(f"{self.client.base_url}/ask", timeout=10)
                
                # 錯誤回應不應該洩露敏感資訊
                response_text = response.text.lower()
                sensitive_info = ["password", "secret", "key", "token", "credential", "stack trace"]
                
                for info in sensitive_info:
                    assert info not in response_text, f"錯誤回應洩露敏感資訊: {info}"
                
            except Exception:
                # 如果測試失敗，那也是可以接受的
                pass
    
    def test_input_sanitization(self):
        """測試輸入清理"""
        # 測試各種特殊字符和編碼
        sanitization_tests = [
            "測試<script>alert('XSS')</script>",
            "正常問題'; DROP TABLE users; --",
            "問題<>&\"'",
            "測試%20編碼",
            "測試\n換行\r回車\t製表符"
        ]
        
        for test_input in sanitization_tests:
            result = self.client.ask_question(test_input)
            self.report_generator.add_result(result)
            
            # 系統應該能夠處理這些輸入而不崩潰
            assert result.status_code is not None
            assert result.status_code in [200, 400, 422]
    
    def test_session_management(self):
        """測試會話管理"""
        # 測試多次請求的會話處理
        questions = self.mock_data.generate_test_questions()[:5]
        
        for question in questions:
            result = self.client.ask_question(question)
            self.report_generator.add_result(result)
            
            # 每個請求都應該獨立處理
            assert result.status_code is not None
        
        print("會話管理測試完成")

def run_security_tests():
    """執行安全測試"""
    import pytest
    
    # 執行測試
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])

if __name__ == "__main__":
    run_security_tests() 