#!/usr/bin/env python3
"""
完整重建向量資料庫腳本
強制重新處理所有文檔並重建向量資料庫
"""

import sys
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("完整重建向量資料庫")
print("=" * 60)

try:
    from core_app.rag.tools.incremental_updater import IncrementalRAGUpdater
    
    rag_root = project_root / "core_app" / "rag"
    data_dir = rag_root / "data"
    vector_dir = rag_root / "vector_store" / "default_faiss_index"
    
    print(f"\n📁 資料目錄: {data_dir}")
    print(f"💾 向量資料庫: {vector_dir}")
    print("\n🔄 開始重建向量資料庫...")
    print("   這可能需要幾分鐘時間，請耐心等待...\n")
    
    updater = IncrementalRAGUpdater(
        data_dir=str(data_dir),
        vector_dir=str(vector_dir)
    )
    
    stats = updater.update_knowledge_base(force_rebuild=True)
    
    print("\n" + "=" * 60)
    print("✅ 重建完成！")
    print("=" * 60)
    print(f"📊 處理統計：")
    print(f"   - 狀態: {stats.get('status', 'unknown')}")
    print(f"   - 總文件數: {stats.get('total_files', 0)}")
    print(f"   - 向量數量: {stats.get('vector_count', 0)}")
    print(f"   - 處理的文件: {stats.get('processed_files', 0)}")
    print(f"   - 新分塊數: {stats.get('new_chunks', 0)}")
    print(f"\n💾 向量資料庫位置: {vector_dir}")
    print("\n✅ 重建成功！")
    
except Exception as e:
    print(f"\n❌ 重建失敗: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

