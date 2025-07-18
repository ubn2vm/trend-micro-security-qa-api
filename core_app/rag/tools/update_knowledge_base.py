"""
知識庫更新執行腳本
支援增量更新和完整重建
"""

import argparse
import logging
import sys
from pathlib import Path

# 解決導入問題：添加RAG根目錄到Python路徑
current_file = Path(__file__).resolve()
rag_root = current_file.parent.parent  # 從tools/回到rag/根目錄
sys.path.insert(0, str(rag_root))

# 現在可以正常導入
from tools.incremental_updater import IncrementalRAGUpdater

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="RAG 知識庫更新工具")
    parser.add_argument("--force-rebuild", action="store_true", 
                       help="強制重建整個向量資料庫")
    parser.add_argument("--data-dir", default="data", 
                       help="資料目錄路徑")
    parser.add_argument("--vector-dir", default="vector_store/crem_faiss_index", 
                       help="向量資料庫目錄路徑")
    parser.add_argument("--show-info", action="store_true", 
                       help="顯示已處理文件資訊")
    
    args = parser.parse_args()
    
    try:
        logger.info(f"RAG工作目錄: {rag_root}")
        logger.info(f"資料目錄: {args.data_dir}")
        logger.info(f"向量目錄: {args.vector_dir}")
        
        # 建立更新器
        updater = IncrementalRAGUpdater(args.data_dir, args.vector_dir)
        
        if args.show_info:
            # 顯示已處理文件資訊
            info = updater.get_processed_files_info()
            logger.info("=== 已處理文件資訊 ===")
            logger.info(f"總文件數: {info['total_files']}")
            for file_info in info['files']:
                logger.info(f"- {file_info['filename']} ({file_info['source_type']})")
                logger.info(f"  處理日期: {file_info['processed_date']}")
                logger.info(f"  分塊數量: {file_info['chunk_count']}")
        else:
            # 執行更新
            logger.info("開始執行知識庫更新...")
            stats = updater.update_knowledge_base(force_rebuild=args.force_rebuild)
            
            logger.info("=== 更新完成 ===")
            logger.info(f"狀態: {stats.get('status', 'unknown')}")
            logger.info(f"新文件數: {stats.get('processed_files', 0)}")
            logger.info(f"新分塊數: {stats.get('new_chunks', 0)}")
            logger.info(f"總文件數: {stats.get('total_files', 0)}")
            logger.info(f"向量數量: {stats.get('vector_count', 0)}")
            
        return 0
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit(main())