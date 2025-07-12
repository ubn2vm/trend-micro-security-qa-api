"""
模擬資料生成器

提供測試過程中需要的模擬資料和假資料
"""

import random
import string
from typing import List, Dict, Any

class MockDataGenerator:
    """模擬資料生成器"""
    
    @staticmethod
    def generate_test_questions() -> List[str]:
        """生成測試問題"""
        return [
            "什麼是網路風險指數？",
            "2025年的主要網路威脅有哪些？",
            "如何評估企業的網路安全風險？",
            "什麼是 CREM 模型？",
            "網路攻擊的趨勢是什麼？",
            "如何防護勒索軟體攻擊？",
            "什麼是零信任安全架構？",
            "雲端安全的最佳實踐有哪些？",
            "如何檢測進階持續性威脅？",
            "資安事件回應流程是什麼？"
        ]
    
    @staticmethod
    def generate_boundary_questions() -> List[str]:
        """生成邊界測試問題"""
        return [
            "",  # 空問題
            "?",  # 單字符
            "測試" * 200,  # 超長問題
            "!@#$%^&*()_+{}|:<>?[]\\;'\",./",  # 特殊字符
            "What is 網路風險指數 CRI?",  # 中英文混合
            "123456789",  # 數字問題
            "a" * 1000,  # 重複字符
            "測試\n換行\t製表符\r回車",  # 控制字符
            "🚀🔥💻📱🔒",  # Emoji
            "测试简体中文繁體中文English日本語한국어"  # 多語言
        ]
    
    @staticmethod
    def generate_performance_questions() -> List[str]:
        """生成性能測試問題"""
        return [
            "請詳細說明網路安全架構的設計原則和實施方法",
            "分析當前網路威脅環境的變化趨勢和應對策略",
            "比較不同安全框架的優缺點和適用場景",
            "探討人工智慧在網路安全中的應用和挑戰",
            "評估企業資安成熟度模型的實施效果"
        ]
    
    @staticmethod
    def generate_security_test_data() -> Dict[str, Any]:
        """生成安全測試資料"""
        return {
            "sql_injection": [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "'; INSERT INTO users VALUES ('hacker', 'password'); --"
            ],
            "xss_attacks": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')"
            ],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "....//....//....//etc/passwd"
            ],
            "command_injection": [
                "; rm -rf /",
                "| cat /etc/passwd",
                "&& del C:\\Windows\\System32"
            ]
        }
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """生成隨機字串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_question() -> str:
        """生成隨機問題"""
        prefixes = ["什麼是", "如何", "為什麼", "什麼時候", "在哪裡"]
        subjects = ["網路安全", "資安威脅", "風險評估", "安全防護", "事件回應"]
        suffixes = ["？", "?", "呢？", "嗎？"]
        
        prefix = random.choice(prefixes)
        subject = random.choice(subjects)
        suffix = random.choice(suffixes)
        
        return f"{prefix}{subject}{suffix}"
    
    @staticmethod
    def generate_mock_api_response() -> Dict[str, Any]:
        """生成模擬 API 回應"""
        return {
            "answer": "這是一個模擬的回答，用於測試目的。",
            "sources": [
                {
                    "title": "模擬來源文件 1",
                    "content": "這是模擬來源內容的一部分...",
                    "page": 1
                },
                {
                    "title": "模擬來源文件 2", 
                    "content": "另一個模擬來源內容...",
                    "page": 5
                }
            ],
            "confidence": 0.85,
            "processing_time": 2.3
        }
    
    @staticmethod
    def generate_mock_health_response() -> Dict[str, Any]:
        """生成模擬健康檢查回應"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "components": {
                "api": "healthy",
                "database": "healthy",
                "vector_store": "healthy",
                "llm_service": "healthy"
            },
            "uptime": 3600,
            "memory_usage": "45.2%",
            "cpu_usage": "12.8%"
        }
    
    @staticmethod
    def generate_mock_examples() -> List[str]:
        """生成模擬範例問題"""
        return [
            "什麼是網路風險指數？",
            "如何評估企業的網路安全風險？",
            "2025年的主要網路威脅有哪些？",
            "什麼是 CREM 模型？",
            "如何防護勒索軟體攻擊？"
        ]
    
    @staticmethod
    def generate_test_scenarios() -> List[Dict[str, Any]]:
        """生成測試場景"""
        return [
            {
                "name": "基本功能測試",
                "description": "測試 API 的基本問答功能",
                "questions": MockDataGenerator.generate_test_questions()[:3],
                "expected_status": 200
            },
            {
                "name": "邊界情況測試",
                "description": "測試各種邊界情況和異常輸入",
                "questions": MockDataGenerator.generate_boundary_questions(),
                "expected_status": [200, 422]
            },
            {
                "name": "性能測試",
                "description": "測試系統性能和回應時間",
                "questions": MockDataGenerator.generate_performance_questions(),
                "expected_status": 200
            },
            {
                "name": "安全測試",
                "description": "測試系統安全性和漏洞防護",
                "questions": [
                    "正常問題測試",
                    "SQL 注入測試",
                    "XSS 攻擊測試"
                ],
                "expected_status": [200, 400, 422]
            }
        ] 