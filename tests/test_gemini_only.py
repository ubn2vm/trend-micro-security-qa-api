#!/usr/bin/env python3
"""
測試腳本 - 確認系統只使用 Google Gemini API
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """測試必要的套件導入"""
    print("=== 測試套件導入 ===")
    
    try:
        # 測試 Google Gemini 相關套件
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai 導入成功")
        
        from langchain.chains import RetrievalQA
        print("✅ langchain.chains 導入成功")
        
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("✅ langchain_community.embeddings 導入成功")
        
        from langchain_community.vectorstores import FAISS
        print("✅ langchain_community.vectorstores 導入成功")
        
        # 測試不會導入 OpenAI 相關套件
        try:
            import langchain_openai
            print("❌ 警告: 發現 langchain_openai 套件")
            return False
        except ImportError:
            print("✅ 確認沒有 langchain_openai 套件")
        
        return True
        
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        return False

def test_environment():
    """測試環境變數"""
    print("\n=== 測試環境變數 ===")
    
    load_dotenv()
    
    # 檢查 Google API Key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key and google_api_key != "your_google_api_key_here":
        print("✅ GOOGLE_API_KEY 已設定")
    else:
        print("⚠️ GOOGLE_API_KEY 未設定或使用預設值")
    
    # 確認沒有 OpenAI API Key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        print("❌ 警告: 發現 OPENAI_API_KEY 環境變數")
        return False
    else:
        print("✅ 確認沒有 OPENAI_API_KEY 環境變數")
    
    return True

def test_main_system():
    """測試主系統"""
    print("\n=== 測試主系統 ===")
    
    try:
        from main import TrendMicroQASystem
        print("✅ TrendMicroQASystem 類別導入成功")
        
        # 檢查知識庫檔案
        if os.path.exists("knowledgebase.txt"):
            print("✅ knowledgebase.txt 檔案存在")
        else:
            print("❌ knowledgebase.txt 檔案不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 主系統測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("趨勢科技資安問答系統 - Google Gemini 專用測試")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_main_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("✅ 所有測試通過！系統已成功移除 OpenAI 相關程式碼")
        return 0
    else:
        print("❌ 部分測試失敗，請檢查上述問題")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 