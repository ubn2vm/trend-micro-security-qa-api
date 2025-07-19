#!/usr/bin/env python3
"""
完整整合測試 - 驗證 main.py 和 app.py 都使用新的RAG+LLM系統
確保API端點真的調用了新系統，而不是舊的實現
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
from pathlib import Path
from dotenv import load_dotenv

# 添加路徑
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from main import TrendMicroQASystem

class IntegrationTestSuite:
    """完整整合測試套件"""
    
    def __init__(self):
        self.api_process = None
        self.api_base_url = "http://localhost:8000"
        self.direct_system = None
        
    def setup_environment(self):
        """設定測試環境"""
        print("🔧 設定測試環境...")
        print("=" * 80)
        
        # 載入環境變數
        project_root = current_dir.parent
        config_path = project_root / 'config' / 'config.env'
        env_path = project_root / '.env'
        
        load_dotenv(config_path)
        load_dotenv(env_path)
        
        # 檢查API Key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or len(api_key.strip()) < 20:
            print("❌ GOOGLE_API_KEY 未正確設定")
            return False
        
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        print(f"✅ GOOGLE_API_KEY: {masked_key}")
        return True
    
    def start_api_server(self):
        """啟動API服務器"""
        print("🚀 啟動API服務器...")
        
        try:
            # 檢查端口是否已被占用
            response = requests.get(f"{self.api_base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ API服務器已在運行")
                return True
        except:
            pass
        
        # 啟動新的API服務器
        api_script = current_dir / "app.py"
        cmd = [sys.executable, "-m", "uvicorn", "core_app.app:app", "--host", "0.0.0.0", "--port", "8000"]
        
        try:
            self.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=current_dir.parent
            )
            
            # 等待服務器啟動
            for i in range(30):  # 等待30秒
                try:
                    response = requests.get(f"{self.api_base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ API服務器啟動成功")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ API服務器啟動超時")
            return False
            
        except Exception as e:
            print(f"❌ 啟動API服務器失敗: {e}")
            return False
    
    def test_direct_system(self):
        """測試直接調用系統"""
        print("\n📚 測試直接系統調用...")
        print("=" * 80)
        
        try:
            self.direct_system = TrendMicroQASystem()
            
            # 獲取系統特徵
            stats = self.direct_system.get_system_stats()
            print(f"✅ 直接系統初始化成功")
            print(f"   📊 系統類型: {stats['system_type']}")
            print(f"   📊 向量數: {stats['vector_count']}")
            print(f"   🤖 LLM可用: {stats['llm_available']}")
            print(f"   🤖 LLM模型: {stats['llm_model']}")
            
            # 測試問答
            test_question = "前5大風險事件有哪些？"
            result = self.direct_system.ask_question(test_question, filter_type="all", k=3)
            
            print(f"   ✅ 測試問答成功")
            print(f"   🤖 生成方式: {result['generation_method']}")
            print(f"   📊 結果數: {result['result_count']}")
            print(f"   💬 答案預覽: {result['answer'][:100]}...")
            
            return result
            
        except Exception as e:
            print(f"❌ 直接系統測試失敗: {e}")
            return None
    
    def test_api_system(self):
        """測試API系統調用"""
        print("\n🌐 測試API系統調用...")
        print("=" * 80)
        
        try:
            # 測試健康檢查
            health_response = requests.get(f"{self.api_base_url}/health")
            health_data = health_response.json()
            
            print(f"✅ API健康檢查成功")
            print(f"   📊 系統類型: {health_data.get('system_type', 'unknown')}")
            print(f"   📊 向量數: {health_data.get('vector_count', 'unknown')}")
            print(f"   🤖 LLM可用: {health_data.get('llm_available', False)}")
            print(f"   🤖 LLM模型: {health_data.get('llm_model', 'unknown')}")
            
            # 測試問答API
            test_question = "前5大風險事件有哪些？"
            api_request = {
                "question": test_question,
                "filter_type": "all",
                "k": 3
            }
            
            response = requests.post(f"{self.api_base_url}/ask", json=api_request, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ API請求失敗: {response.status_code}")
                print(f"   錯誤內容: {response.text}")
                return None
            
            result = response.json()
            
            print(f"   ✅ API問答成功")
            print(f"   🤖 生成方式: {result.get('generation_method', 'unknown')}")
            print(f"   📊 結果數: {result.get('result_count', 0)}")
            print(f"   💬 答案預覽: {result.get('answer', '')[:100]}...")
            
            return result
            
        except Exception as e:
            print(f"❌ API系統測試失敗: {e}")
            return None
    
    def compare_systems(self, direct_result, api_result):
        """比較直接調用和API調用的結果"""
        print("\n🔍 比較系統調用結果...")
        print("=" * 80)
        
        if not direct_result or not api_result:
            print("❌ 無法比較：某個系統測試失敗")
            return False
        
        # 檢查關鍵特徵
        checks = [
            ("狀態", direct_result.get('status'), api_result.get('status')),
            ("生成方式", direct_result.get('generation_method'), api_result.get('generation_method')),
            ("結果數量", direct_result.get('result_count'), api_result.get('result_count')),
            ("LLM可用", direct_result.get('llm_available'), api_result.get('llm_available')),
        ]
        
        all_match = True
        
        for feature, direct_val, api_val in checks:
            if direct_val == api_val:
                print(f"✅ {feature}: 一致 ({direct_val})")
            else:
                print(f"⚠️ {feature}: 不一致 (直接:{direct_val} vs API:{api_val})")
                all_match = False
        
        # 檢查答案相似性（簡單比較）
        direct_answer = direct_result.get('answer', '')
        api_answer = api_result.get('answer', '')
        
        if len(direct_answer) > 50 and len(api_answer) > 50:
            # 簡單的相似性檢查
            common_words = set(direct_answer.split()) & set(api_answer.split())
            similarity = len(common_words) / max(len(direct_answer.split()), len(api_answer.split()))
            
            if similarity > 0.3:  # 30%的詞彙重疊
                print(f"✅ 答案相似性: 良好 ({similarity:.2%})")
            else:
                print(f"⚠️ 答案相似性: 較低 ({similarity:.2%})")
        
        return all_match
    
    def verify_new_system_features(self, direct_result, api_result):
        """驗證新系統特徵"""
        print("\n🎯 驗證新系統特徵...")
        print("=" * 80)
        
        required_features = {
            "generation_method": ["llm_generated", "structured_formatted"],  # 新系統支援的生成方式
            "llm_available": [True],  # LLM應該可用
            "system_type": ["TrendMicroQASystem"],  # 系統類型
            "result_count": lambda x: x > 0,  # 應該有結果
            "text_results": lambda x: isinstance(x, int),  # 文本結果計數
            "table_results": lambda x: isinstance(x, int),  # 表格結果計數
        }
        
        results = {"direct": direct_result, "api": api_result}
        all_passed = True
        
        for system_name, result in results.items():
            if not result:
                continue
                
            print(f"\n檢查 {system_name.upper()} 系統:")
            
            for feature, expected in required_features.items():
                actual = result.get(feature)
                
                if callable(expected):
                    # 函數檢查
                    if expected(actual):
                        print(f"   ✅ {feature}: {actual}")
                    else:
                        print(f"   ❌ {feature}: {actual} (不符合條件)")
                        all_passed = False
                elif isinstance(expected, list):
                    # 列表檢查
                    if actual in expected:
                        print(f"   ✅ {feature}: {actual}")
                    else:
                        print(f"   ❌ {feature}: {actual} (應為{expected}之一)")
                        all_passed = False
        
        return all_passed
    
    def test_vector_count_consistency(self):
        """測試向量數量一致性"""
        print("\n📊 測試向量數量一致性...")
        print("=" * 80)
        
        try:
            # 從直接系統獲取
            if self.direct_system:
                direct_stats = self.direct_system.get_system_stats()
                direct_count = direct_stats.get('vector_count', 0)
                print(f"直接系統向量數: {direct_count}")
            
            # 從API獲取
            health_response = requests.get(f"{self.api_base_url}/health")
            api_stats = health_response.json()
            api_count = api_stats.get('vector_count', 0)
            print(f"API系統向量數: {api_count}")
            
            # 檢查是否一致且超過200
            if direct_count == api_count and direct_count > 200:
                print(f"✅ 向量數量一致且符合要求: {direct_count} > 200")
                return True
            else:
                print(f"❌ 向量數量問題: 直接({direct_count}) vs API({api_count})")
                return False
        
        except Exception as e:
            print(f"❌ 向量數量檢查失敗: {e}")
            return False
    
    def cleanup(self):
        """清理測試環境"""
        print("\n🧹 清理測試環境...")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("✅ API服務器已停止")
            except:
                self.api_process.kill()
                print("✅ API服務器已強制停止")
    
    def run_complete_test(self):
        """運行完整測試"""
        print("🚀 完整整合測試 - 驗證 main.py 和 app.py 使用新RAG+LLM系統")
        print("=" * 80)
        
        success = True
        
        try:
            # 1. 環境設定
            if not self.setup_environment():
                return False
            
            # 2. 啟動API服務器
            if not self.start_api_server():
                return False
            
            time.sleep(2)  # 給服務器一點時間穩定
            
            # 3. 測試直接系統
            direct_result = self.test_direct_system()
            if not direct_result:
                success = False
            
            # 4. 測試API系統
            api_result = self.test_api_system()
            if not api_result:
                success = False
            
            # 5. 比較系統結果
            if not self.compare_systems(direct_result, api_result):
                success = False
            
            # 6. 驗證新系統特徵
            if not self.verify_new_system_features(direct_result, api_result):
                success = False
            
            # 7. 測試向量數量一致性
            if not self.test_vector_count_consistency():
                success = False
            
            # 最終結果
            print("\n" + "=" * 80)
            if success:
                print("🎉 所有測試通過！")
                print("✅ 確認 main.py 和 app.py 都使用新的RAG+LLM系統")
                print("✅ 確認系統具備超過200個向量的RAG能力")
                print("✅ 確認LLM (Gemini) 正常整合和運作")
                print("✅ 確認API端點和直接調用結果一致")
            else:
                print("❌ 測試失敗！存在系統整合問題")
            
            return success
            
        except KeyboardInterrupt:
            print("\n⚠️ 測試被用戶中斷")
            return False
        except Exception as e:
            print(f"\n❌ 測試過程中發生錯誤: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """主函數"""
    test_suite = IntegrationTestSuite()
    success = test_suite.run_complete_test()
    
    if success:
        print("\n🎯 結論: 系統整合測試成功！")
        print("   📚 main.py: TrendMicroQASystem 使用新RAG+LLM")
        print("   🌐 app.py: API端點正確調用新系統")
        print("   🔗 整合完整: 兩種調用方式結果一致")
    else:
        print("\n⚠️ 結論: 系統整合測試失敗，需要檢查實現")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 