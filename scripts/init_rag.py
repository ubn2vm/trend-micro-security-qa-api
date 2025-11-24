#!/usr/bin/env python3
"""
RAG 系統智能初始化腳本
- 自動檢查文檔
- 下載缺失的大文件（從 GitHub Releases，可選）
- 建立向量資料庫
"""

import sys
import os
import zipfile
import urllib.request
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# GitHub Releases URL（需要替換為實際 URL）
# 如果沒有設置 GitHub Releases，可以設為 None
LARGE_DOCUMENTS_URL = os.getenv(
    "LARGE_DOCUMENTS_URL",
    "https://github.com/your-username/aiops/releases/latest/download/large-documents.zip"
)

def check_documents(source_dir: Path) -> tuple:
    """檢查文檔，返回已有和缺失的文件列表"""
    required_docs = [
        "ddi_6.8.sp1_ag.pdf",
        "ddi_6.8.sp1_syslog.pdf", 
        "docs-suricata-io-en-latest.pdf",
        "Research-Risk-Report-2025.pdf",
        "sb-crem.pdf"
    ]
    
    existing = []
    missing = []
    
    for doc in required_docs:
        doc_path = source_dir / doc
        if doc_path.exists():
            size_mb = doc_path.stat().st_size / (1024 * 1024)
            existing.append((doc, size_mb))
        else:
            missing.append(doc)
    
    return existing, missing

def download_large_documents(url: str, dest_dir: Path) -> bool:
    """下載大文件"""
    try:
        print(f"\n📥 正在下載大文件...")
        zip_path = dest_dir.parent / "large-documents.zip"
        
        urllib.request.urlretrieve(url, zip_path)
        print("✅ 下載完成")
        
        print("📦 正在解壓縮...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
        
        zip_path.unlink()  # 清理
        print("✅ 解壓縮完成")
        return True
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        print("\n💡 請手動下載：")
        print(f"   1. 前往: {url}")
        print(f"   2. 下載 large-documents.zip")
        print(f"   3. 解壓到: {dest_dir}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("🚀 RAG 系統智能初始化")
    print("=" * 60)
    
    # 設定路徑
    rag_root = project_root / "core_app" / "rag"
    source_dir = rag_root / "data" / "source"
    vector_dir = rag_root / "vector_store" / "crem_faiss_index"
    
    # 確保目錄存在
    source_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 文檔目錄: {source_dir}")
    print(f"💾 向量資料庫: {vector_dir}")
    
    # 檢查文檔
    existing, missing = check_documents(source_dir)
    
    if existing:
        print(f"\n✅ 找到 {len(existing)} 個文檔：")
        for doc, size in existing:
            print(f"   - {doc} ({size:.2f} MB)")
    
    if missing:
        print(f"\n⚠️  缺少 {len(missing)} 個文檔：")
        for doc in missing:
            print(f"   - {doc}")
        
        # 嘗試下載大文件（如果 URL 不是預設值）
        if LARGE_DOCUMENTS_URL and "your-username" not in LARGE_DOCUMENTS_URL:
            response = input("\n是否要從 GitHub Releases 下載缺失的文件？(Y/n): ").strip().lower()
            if response != 'n':
                if not download_large_documents(LARGE_DOCUMENTS_URL, source_dir):
                    print("\n⚠️  下載失敗，將繼續使用現有文檔")
        else:
            print("\n💡 提示：")
            print("   1. 將 PDF 文件放入 core_app/rag/data/source/ 目錄")
            print("   2. 或設置 LARGE_DOCUMENTS_URL 環境變數以自動下載")
    
    # 檢查是否有 PDF 文件
    pdf_files = list(source_dir.glob("*.pdf"))
    if not pdf_files:
        print("\n❌ 錯誤：找不到任何 PDF 文件")
        print("\n💡 請執行以下步驟：")
        print("   1. 將 PDF 文件放入 core_app/rag/data/source/ 目錄")
        print("   2. 重新執行此腳本")
        return 1
    
    print(f"\n📄 總共找到 {len(pdf_files)} 個 PDF 文件")
    
    # 檢查向量資料庫
    if (vector_dir / "index.faiss").exists():
        print(f"\n⚠️  向量資料庫已存在")
        response = input("是否要重建？(y/N): ").strip().lower()
        if response != 'y':
            print("✅ 使用現有向量資料庫")
            return 0
        force_rebuild = True
    else:
        force_rebuild = False
        print(f"\n📦 將建立新的向量資料庫...")
    
    # 執行初始化
    try:
        print("\n🔄 開始處理文檔並建立向量資料庫...")
        print("   這可能需要幾分鐘時間，請耐心等待...")
        
        from core_app.rag.tools.incremental_updater import IncrementalRAGUpdater
        
        updater = IncrementalRAGUpdater(
            data_dir=str(rag_root / "data"),
            vector_dir=str(vector_dir)
        )
        
        stats = updater.update_knowledge_base(force_rebuild=force_rebuild)
        
        print("\n" + "=" * 60)
        print("✅ 初始化完成！")
        print("=" * 60)
        print(f"📊 處理統計：")
        print(f"   - 總文件數: {stats.get('total_files', 0)}")
        print(f"   - 向量數量: {stats.get('vector_count', 0)}")
        print(f"   - 狀態: {stats.get('status', 'unknown')}")
        print(f"\n💾 向量資料庫位置: {vector_dir}")
        print("\n🚀 現在可以啟動服務了！")
        print("\n啟動方式：")
        print("   - Docker: cd containerization && docker-compose up -d")
        print("   - 本地: python -m core_app.app")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

