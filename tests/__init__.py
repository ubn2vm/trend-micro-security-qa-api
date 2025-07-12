"""
趨勢科技資安問答 API 測試套件

這個測試套件包含完整的測試框架，確保系統的品質和可靠性：

- unit/: 單元測試 - 測試個別模組和函數
- integration/: 整合測試 - 測試 API 端點和服務整合
- performance/: 性能測試 - 測試系統效能和負載能力
- security/: 安全測試 - 測試安全性和漏洞防護
- utils/: 測試工具 - 共用的測試輔助函數和模擬資料
- scripts/: 測試腳本 - 自動化測試執行腳本

使用方式：
    python -m pytest tests/                    # 執行所有測試
    python -m pytest tests/unit/              # 執行單元測試
    python -m pytest tests/integration/       # 執行整合測試
    python -m pytest tests/performance/       # 執行性能測試
    python -m pytest tests/security/          # 執行安全測試
"""

__version__ = "1.0.0"
__author__ = "AIOps Team"
__description__ = "趨勢科技資安問答 API 完整測試框架" 