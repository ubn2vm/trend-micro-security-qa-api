#!/usr/bin/env python3
"""
專案驗證腳本 - 快速檢查趨勢科技資安問答 API 的所有功能
"""

import os
import sys
import time
import requests
import json
from typing import Dict, Any, List

def test_api_endpoints() -> Dict[str, Any]:
    """測試所有 API 端點"""
    base_url = "http://localhost:8000"
    results = {}
    
    print("🔍 測試 API 端點...")
    
    # 測試健康檢查
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            results["health"] = {
                "status": "success",
                "data": {
                    "status": data.get("status"),
                    "version": data.get("version"),
                    "components": data.get("components", {})
                }
            }
            print("  ✅ 健康檢查通過")
        else:
            results["health"] = {"status": "error", "code": response.status_code}
            print(f"  ❌ 健康檢查失敗: {response.status_code}")
    except Exception as e:
        results["health"] = {"status": "error", "message": str(e)}
        print(f"  ❌ 健康檢查錯誤: {e}")
    
    # 測試範例問題
    try:
        response = requests.get(f"{base_url}/examples", timeout=10)
        if response.status_code == 200:
            data = response.json()
            results["examples"] = {
                "status": "success",
                "count": len(data) if isinstance(data, list) else 0
            }
            print("  ✅ 範例問題端點通過")
        else:
            results["examples"] = {"status": "error", "code": response.status_code}
            print(f"  ❌ 範例問題端點失敗: {response.status_code}")
    except Exception as e:
        results["examples"] = {"status": "error", "message": str(e)}
        print(f"  ❌ 範例問題端點錯誤: {e}")
    
    # 測試問答功能
    try:
        test_questions = [
            "什麼是網路風險指數？",
            "2025年的主要網路威脅有哪些？",
            "如何評估企業的網路安全風險？"
        ]
        
        qa_results = []
        for i, question in enumerate(test_questions):
            start_time = time.time()
            response = requests.post(
                f"{base_url}/ask",
                json={"question": question},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                qa_results.append({
                    "question": question,
                    "status": "success",
                    "response_time": end_time - start_time,
                    "answer_length": len(data.get("answer", "")),
                    "has_sources": bool(data.get("sources"))
                })
                print(f"  ✅ 問答測試 {i+1} 通過 ({end_time - start_time:.2f}s)")
            else:
                qa_results.append({
                    "question": question,
                    "status": "error",
                    "code": response.status_code
                })
                print(f"  ❌ 問答測試 {i+1} 失敗: {response.status_code}")
        
        results["qa"] = {
            "status": "success" if all(r["status"] == "success" for r in qa_results) else "partial",
            "tests": qa_results
        }
        
    except Exception as e:
        results["qa"] = {"status": "error", "message": str(e)}
        print(f"  ❌ 問答功能錯誤: {e}")
    
    return results

def test_file_structure() -> Dict[str, Any]:
    """檢查檔案結構"""
    print("📁 檢查檔案結構...")
    
    required_files = [
        "core_app/app.py",
        "core_app/main.py",
        "core_app/requirements.txt",
        "config/env.example",
        "containerization/Dockerfile",
        "containerization/docker-compose.yml",
        "start.bat",
        "start_api_enhanced.bat",
        "testing_tools/quick_test.bat",
        "docs/README.md",
        "docs/QUICK_START.md"
    ]
    
    required_dirs = [
        "tests",
        "python_config"
    ]
    
    results = {
        "files": {},
        "directories": {},
        "missing": []
    }
    
    # 檢查檔案
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            results["files"][file] = {"exists": True, "size": size}
            print(f"  ✅ {file} ({size} bytes)")
        else:
            results["files"][file] = {"exists": False}
            results["missing"].append(file)
            print(f"  ❌ {file} (缺失)")
    
    # 檢查目錄
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            results["directories"][dir_name] = {"exists": True}
            print(f"  ✅ {dir_name}/")
        else:
            results["directories"][dir_name] = {"exists": False}
            results["missing"].append(dir_name)
            print(f"  ❌ {dir_name}/ (缺失)")
    
    return results

def test_environment() -> Dict[str, Any]:
    """檢查環境配置"""
    print("🔧 檢查環境配置...")
    
    results = {}
    
    # 檢查虛擬環境
    if os.path.exists("aiops/Scripts/activate.bat"):
        results["virtual_env"] = {"status": "success", "message": "虛擬環境存在"}
        print("  ✅ 虛擬環境存在")
    else:
        results["virtual_env"] = {"status": "warning", "message": "虛擬環境不存在"}
        print("  ⚠️  虛擬環境不存在")
    
    # 檢查 .env 檔案
    if os.path.exists(".env"):
        results["env_file"] = {"status": "success", "message": ".env 檔案存在"}
        print("  ✅ .env 檔案存在")
    else:
        results["env_file"] = {"status": "warning", "message": ".env 檔案不存在"}
        print("  ⚠️  .env 檔案不存在")
    
    # 檢查知識庫檔案
    knowledge_files = ["core_app/summary.txt", "core_app/knowledgebase.txt"]
    for file in knowledge_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            results[f"knowledge_{file}"] = {"status": "success", "size": size}
            print(f"  ✅ {file} ({size} bytes)")
        else:
            results[f"knowledge_{file}"] = {"status": "warning", "message": f"{file} 不存在"}
            print(f"  ⚠️  {file} 不存在")
    
    return results

def generate_summary(api_results: Dict, file_results: Dict, env_results: Dict) -> Dict[str, Any]:
    """生成驗證摘要"""
    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api_tests": {
            "health": api_results.get("health", {}).get("status"),
            "examples": api_results.get("examples", {}).get("status"),
            "qa": api_results.get("qa", {}).get("status")
        },
        "file_structure": {
            "total_files": len(file_results.get("files", {})),
            "existing_files": sum(1 for f in file_results.get("files", {}).values() if f.get("exists")),
            "missing_files": len(file_results.get("missing", []))
        },
        "environment": {
            "virtual_env": env_results.get("virtual_env", {}).get("status"),
            "env_file": env_results.get("env_file", {}).get("status"),
            "knowledge_files": sum(1 for k, v in env_results.get("knowledge_files", {}).items() if v.get("status") == "success")
        }
    }
    
    # 計算整體成功率
    api_success = sum(1 for status in summary["api_tests"].values() if status == "success")
    api_total = len(summary["api_tests"])
    file_success = summary["file_structure"]["existing_files"]
    file_total = summary["file_structure"]["total_files"]
    
    overall_score = (api_success / api_total * 0.6 + file_success / file_total * 0.4) * 100
    summary["overall_score"] = round(overall_score, 1)
    
    return summary

def main():
    """主函數"""
    print("趨勢科技資安問答 API 專案驗證")
    print("=" * 50)
    print()
    
    # 檢查 API 是否運行
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API 服務未運行，請先啟動服務")
            print("執行: start.bat 或 start_api_enhanced.bat")
            return
    except:
        print("❌ 無法連接到 API 服務")
        print("請先啟動 API 服務")
        return
    
    print("✅ API 服務正在運行")
    print()
    
    # 執行各項測試
    api_results = test_api_endpoints()
    print()
    
    file_results = test_file_structure()
    print()
    
    env_results = test_environment()
    print()
    
    # 生成摘要
    summary = generate_summary(api_results, file_results, env_results)
    
    # 顯示結果
    print("=" * 50)
    print("📊 驗證結果摘要")
    print("=" * 50)
    print(f"驗證時間: {summary['timestamp']}")
    print(f"整體完成度: {summary['overall_score']}%")
    print()
    
    print("API 功能測試:")
    for test, status in summary["api_tests"].items():
        icon = "✅" if status == "success" else "❌"
        print(f"  {icon} {test}: {status}")
    
    print()
    print("檔案結構檢查:")
    print(f"  檔案完整性: {summary['file_structure']['existing_files']}/{summary['file_structure']['total_files']}")
    print(f"  缺失檔案: {summary['file_structure']['missing_files']}")
    
    print()
    print("環境配置檢查:")
    print(f"  虛擬環境: {summary['environment']['virtual_env']}")
    print(f"  環境變數: {summary['environment']['env_file']}")
    print(f"  知識庫檔案: {summary['environment']['knowledge_files']}")
    
    print()
    if summary["overall_score"] >= 90:
        print("🎉 專案驗證通過！準備就緒")
    elif summary["overall_score"] >= 80:
        print("✅ 專案基本完成，有少量問題需要改進")
    elif summary["overall_score"] >= 70:
        print("⚠️  專案需要進一步完善")
    else:
        print("❌ 專案需要重點改進")
    
    # 保存詳細結果
    full_results = {
        "summary": summary,
        "api_results": api_results,
        "file_results": file_results,
        "env_results": env_results
    }
    
    with open("validation_results.json", "w", encoding="utf-8") as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 詳細結果已保存到 validation_results.json")

if __name__ == "__main__":
    main() 