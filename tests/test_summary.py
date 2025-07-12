#!/usr/bin/env python3
"""
測試腳本 - 使用 summary.txt 測試 Google Gemini API
"""

import os
import sys
from dotenv import load_dotenv
import pytest
from core_app.main import TrendMicroQASystem

def test_imports():
    """測試必要的套件導入"""
    print("=== 測試套件導入 ===")
    
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
        assert False, "不應該有 langchain_openai 套件"
    except ImportError:
        print("✅ 確認沒有 langchain_openai 套件")

def test_environment():
    """測試環境變數"""
    print("\n=== 測試環境變數 ===")
    
    load_dotenv()
    
    # 檢查 Google API Key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    assert google_api_key and google_api_key != "your_google_api_key_here", "GOOGLE_API_KEY 未設定或使用預設值"
    print("✅ GOOGLE_API_KEY 已設定")
    
    # 確認沒有 OpenAI API Key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    assert not openai_api_key, "不應該有 OPENAI_API_KEY 環境變數"
    print("✅ 確認沒有 OPENAI_API_KEY 環境變數")

def test_rag_system_initialization():
    """測試 RAG 問答系統初始化"""
    qa_system = TrendMicroQASystem()
    assert qa_system.vector_store is not None
    assert qa_system.qa_chain is not None

def test_rag_system_answer():
    """測試 RAG 問答系統回答"""
    qa_system = TrendMicroQASystem()
    question = "什麼是 CREM？"
    result = qa_system.ask_question(question)
    assert result["status"] == "success"
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0

def main():
    """主測試函數"""
    print("趨勢科技資安問答系統 - Google Gemini 專用測試")
    print("使用 summary.txt 作為知識庫")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_environment,
        test_rag_system_initialization,
        test_rag_system_answer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
        print()
    
    print("=" * 60)
    print(f"測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("✅ 所有測試通過！系統已成功移除 OpenAI 相關程式碼")
        print("✅ 系統使用 Google Gemini API 正常運作")
        return 0
    else:
        print("❌ 部分測試失敗，請檢查上述問題")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 